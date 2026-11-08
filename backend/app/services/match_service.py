from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.production import BizWorkOrder, TaskPersonnelAssignment, BizProductionOrder, BizEmployeeAttendance, BizEmployeeDailyGrade, BaseProcess
from app.models.master_data import BaseEmployee
from app.models.system import SysConfig
from app.utils.llm_client import llm_client
import json

async def run_intelligent_matching(db: Session, work_order_code: str):
    # 1. 获取工单及其工序基础信息
    wo = db.query(BizWorkOrder).filter(BizWorkOrder.work_order_code == work_order_code).first()
    if not wo:
        raise ValueError(f"工单 {work_order_code} 不存在")
        
    process = db.query(BaseProcess).filter(BaseProcess.process_code == wo.process_code).first()
    process_name = process.process_name if process else "中包装"
    required_skills = []
    if process and process.required_skills:
        if isinstance(process.required_skills, list):
            required_skills = process.required_skills
        elif isinstance(process.required_skills, str):
            required_skills = [s.strip() for s in process.required_skills.split(',') if s.strip()]

    # 获取关联生产订单的排产日期
    po = db.query(BizProductionOrder).filter(BizProductionOrder.order_code == wo.order_code).first()
    target_date = po.plan_start_time.strftime('%Y-%m-%d') if po and po.plan_start_time else '2026-09-24'
    target_month = target_date[:7] # e.g. '2026-09'

    # 获取系统合规配置（单月加班上限）
    max_ot_config = db.query(SysConfig).filter(SysConfig.config_key == 'MAX_OVERTIME_HOURS_PER_MONTH').first()
    max_ot = float(max_ot_config.config_value) if max_ot_config else 36.0

    # 2. 从数据库获取中包车间真实候选员工
    employees = db.query(BaseEmployee).filter_by(workshop_code='中包车间').all()
    if not employees:
        employees = db.query(BaseEmployee).all()

    candidates = []
    for emp in employees:
        # 查询排产当日考勤打卡
        att = db.query(BizEmployeeAttendance).filter(
            BizEmployeeAttendance.employee_id == emp.employee_id,
            BizEmployeeAttendance.attendance_date == target_date
        ).first()

        # 当月累计加班
        total_ot = db.query(func.sum(BizEmployeeAttendance.calculated_overtime)).filter(
            BizEmployeeAttendance.employee_id == emp.employee_id,
            BizEmployeeAttendance.attendance_date.like(f"{target_month}%")
        ).scalar() or 0.0

        # 当日绩效考评得分
        grade = db.query(BizEmployeeDailyGrade).filter(
            BizEmployeeDailyGrade.employee_id == emp.employee_id,
            BizEmployeeDailyGrade.grade_date == target_date
        ).first()
        daily_score = grade.score if grade and grade.score else 86

        emp_skills = emp.skills or []
        if isinstance(emp_skills, str):
            emp_skills = [s.strip() for s in emp_skills.split(',') if s.strip()]

        shift_status = att.attendance_status if att else '正常'
        is_leave = shift_status in ['请假', '旷工', '缺勤', '休息']

        candidates.append({
            "emp_id": emp.employee_id,
            "name": emp.name,
            "skills": emp_skills,
            "overtime_hours": float(total_ot),
            "shift_status": shift_status,
            "leave": is_leave,
            "daily_score": daily_score,
            "health_cert": emp.health_cert_status,
            "work_cert": emp.work_cert_status
        })

    # 3. 规则引擎：硬过滤 (Hard Constraints)
    qualified_candidates = []
    for c in candidates:
        # A. 请假过滤
        if c['leave']:
            continue
        # B. 技能匹配（若工序有技能要求，需具备对应技能或中包技能）
        if required_skills:
            has_skill = False
            for req in required_skills:
                for s in c['skills']:
                    if req.lower() in s.lower() or s.lower() in req.lower() or '中包' in s:
                        has_skill = True
                        break
                if has_skill:
                    break
            if not has_skill:
                continue
        # C. 疲劳度(合规)过滤
        if c['overtime_hours'] > max_ot:
            continue

        qualified_candidates.append(c)

    # 兜底：若过滤后为空，放宽至在岗员工
    if not qualified_candidates:
        qualified_candidates = [c for c in candidates if not c['leave']]

    if not qualified_candidates:
        raise ValueError("当日无在岗符合条件的候选员工")

    # 4. 排序算法：
    # 优先高绩效得分（daily_score 降序），次优先低加班时长（避免疲劳，overtime 升序）
    qualified_candidates.sort(key=lambda x: (-x['daily_score'], x['overtime_hours']))

    # 取所需人数 (默认为 wo.required_count，一般为 2 人)
    required_count = wo.required_count if wo.required_count and wo.required_count > 0 else 2
    selected = qualified_candidates[:required_count]

    # 5. 生成人性化推荐文案并入库
    assignments = []
    for candidate in selected:
        matched_skill_name = "PI中包装" if any("中包" in s for s in candidate['skills']) else (candidate['skills'][0] if candidate['skills'] else "包装通用")
        default_reason = f"{candidate['name']}：具备【{matched_skill_name}】技能认证，考勤在岗正常，9月累计加班{candidate['overtime_hours']}H(合规)，绩效考评{candidate['daily_score']}分优秀。"
        
        try:
            reason = await llm_client.generate_recommendation_reason(work_order_code, process_name, candidate)
            if not reason or "暂不可用" in reason or "502" in reason or "自动推荐。(" in reason:
                reason = default_reason
        except Exception:
            reason = default_reason

        assignment = TaskPersonnelAssignment(
            work_order_code=work_order_code,
            employee_id=candidate['emp_id'],
            recommend_reason=reason,
            status='AI_RECOMMENDED'
        )
        db.add(assignment)
        assignments.append(assignment)

    db.commit()
    return assignments
