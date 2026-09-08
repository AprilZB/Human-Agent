from sqlalchemy.orm import Session
from app.models.production import BizWorkOrder, TaskPersonnelAssignment
from app.models.system import SysConfig
from app.utils.llm_client import llm_client
import json

async def run_intelligent_matching(db: Session, work_order_code: str):
    # 1. 获取工单及其工序基础信息
    wo = db.query(BizWorkOrder).filter(BizWorkOrder.work_order_code == work_order_code).first()
    if not wo:
        raise ValueError("Work order not found")
        
    process = wo.process
    if not process:
        raise ValueError("Process master data not found for work order")
        
    required_skills = process.required_skills if process.required_skills else []
    
    # 获取系统合规配置
    max_ot_config = db.query(SysConfig).filter(SysConfig.config_key == 'MAX_OVERTIME_HOURS_PER_MONTH').first()
    max_ot = float(max_ot_config.config_value) if max_ot_config else 36.0
    
    # 2. 调用 APHR 接口获取候选人数据 (此处为 Mock 逻辑)
    # 实际开发中，应向 APHR 发起 HTTP 请求，拉取人员技能与考勤数据
    mock_candidates = [
        {"emp_id": "EMP001", "name": "王师傅", "skills": ["激光切割", "焊接"], "overtime_hours": 20.5, "shift_status": "空闲", "leave": False},
        {"emp_id": "EMP002", "name": "李师傅", "skills": ["打磨"], "overtime_hours": 10.0, "shift_status": "空闲", "leave": False},
        {"emp_id": "EMP003", "name": "张师傅", "skills": ["激光切割"], "overtime_hours": 38.0, "shift_status": "空闲", "leave": False}, # 超过36小时，会被过滤
        {"emp_id": "EMP004", "name": "赵师傅", "skills": ["激光切割"], "overtime_hours": 5.0, "shift_status": "作业中", "leave": True}    # 请假，会被过滤
    ]
    
    # 3. 规则引擎：硬过滤 (Hard Constraints)
    qualified_candidates = []
    for c in mock_candidates:
        # A. 请假过滤
        if c['leave']: continue
        # B. 技能匹配
        if required_skills and not any(s in c['skills'] for s in required_skills):
            continue
        # C. 疲劳度(合规)过滤
        if c['overtime_hours'] > max_ot:
            continue
            
        qualified_candidates.append(c)
        
    if not qualified_candidates:
        raise ValueError("No qualified candidates found based on current rules.")
        
    # 排序：按加班时长从小到大（优先指派不怎么加班的）
    qualified_candidates.sort(key=lambda x: x['overtime_hours'])
    
    # 取所需人数 (默认1人)
    selected = qualified_candidates[:wo.required_count]
    
    # 4. 模型辅助：生成人性化推荐文案并入库
    assignments = []
    for candidate in selected:
        # 异步调用本地 vLLM
        reason = await llm_client.generate_recommendation_reason(work_order_code, process.process_name, candidate)
        
        assignment = TaskPersonnelAssignment(
            work_order_code=work_order_code,
            employee_id=candidate['emp_id'],
            recommend_reason=reason,
            status='AI_RECOMMENDED'
        )
        db.add(assignment)
        assignments.append(assignment)
        
    wo.status = 'ASSIGNED'
    db.commit()
    
    return assignments
