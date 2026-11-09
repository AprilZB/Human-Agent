from flask import Blueprint, jsonify, request, send_file
from sqlalchemy import func, or_
from datetime import datetime, timedelta
import calendar
from app.core.database import SessionLocal
from app.models.production import BizProductionOrder, BizProductionConfirmation, BizEmployeeAttendance, BizEmployeeDailyGrade
from app.models.master_data import BaseEmployee

report_bp = Blueprint('report', __name__)

def clean_dict(d):
    ret = d.__dict__.copy()
    ret.pop('_sa_instance_state', None)
    for k, v in ret.items():
        if hasattr(v, 'isoformat'):
            ret[k] = v.isoformat()
        elif hasattr(v, '__float__'):
            ret[k] = float(v)
    return ret

@report_bp.route("/production", methods=["GET"])
def get_production_report():
    db = SessionLocal()
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        product_code = request.args.get('product_code')

        q = db.query(BizProductionOrder)
        if start_date:
            q = q.filter(BizProductionOrder.plan_start_time >= start_date)
        if end_date:
            q = q.filter(BizProductionOrder.plan_start_time <= (end_date + " 23:59:59"))
        if product_code:
            q = q.filter(BizProductionOrder.material_code.like(f"%{product_code}%"))
        
        orders = q.all()
        result = []
        for o in orders:
            # sum confirmations
            confs = db.query(BizProductionConfirmation).filter_by(order_code=o.order_code).all()
            completed = sum(c.yield_quantity or 0 for c in confs)
            scrap = sum(c.scrap_quantity or 0 for c in confs)
            
            d = clean_dict(o)
            d['workshop_code'] = '中包车间'
            d['scheduled_start_date'] = o.plan_start_time.strftime('%Y-%m-%d') if o.plan_start_time else ''
            d['total_completed'] = completed
            d['total_scrap'] = scrap
            result.append(d)
        
        return jsonify(result)
    finally:
        db.close()

@report_bp.route("/production/<order_code>/confirmations", methods=["GET"])
def get_order_confirmations(order_code):
    db = SessionLocal()
    try:
        confs = db.query(BizProductionConfirmation).filter_by(order_code=order_code).all()
        res = []
        for c in confs:
            d = clean_dict(c)
            d['confirmation_code'] = c.confirmation_no
            d['actual_date'] = c.exec_datetime.strftime('%Y-%m-%d') if c.exec_datetime else ''
            d['employee_id'] = c.employee_name or c.employee_id
            res.append(d)
        return jsonify(res)
    finally:
        db.close()

@report_bp.route("/overtime", methods=["GET"])
def get_overtime_report():
    db = SessionLocal()
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        q = db.query(
            BizEmployeeAttendance.employee_id,
            BaseEmployee.name,
            func.sum(BizEmployeeAttendance.calculated_overtime).label('total_overtime')
        ).outerjoin(
            BaseEmployee, BizEmployeeAttendance.employee_id == BaseEmployee.employee_id
        )

        if start_date:
            q = q.filter(BizEmployeeAttendance.attendance_date >= start_date)
        if end_date:
            q = q.filter(BizEmployeeAttendance.attendance_date <= end_date)
        
        q = q.group_by(BizEmployeeAttendance.employee_id, BaseEmployee.name)
        
        res = []
        for row in q.all():
            res.append({
                "employee_id": row[0],
                "employee_name": row[1] or 'Unknown',
                "total_overtime": float(row[2]) if row[2] else 0.0
            })
        return jsonify(res)
    finally:
        db.close()

@report_bp.route("/overtime/<employee_id>", methods=["GET"])
def get_employee_overtime_detail(employee_id):
    db = SessionLocal()
    try:
        confs = db.query(BizEmployeeAttendance).filter(
            BizEmployeeAttendance.employee_id == employee_id
        ).order_by(BizEmployeeAttendance.attendance_date.desc()).all()

        return jsonify([clean_dict(c) for c in confs])
    finally:
        db.close()


def get_target_team_member_ids(db, start_date=None, end_date=None, team_leader_id=None):
    """
    获取中包车间班组成员（优先王军班组及下属组员，杜绝全厂数千人员导致前端卡死）
    """
    # 核心中包车间班组成员
    core_ids = ['404201195', '404245800', '404245815', '404266762', '411265010', '404267095', '411265016', '411265017']
    
    # 动态支持当前班组长的直接下属
    leader_subordinate_ids = []
    if team_leader_id:
        leader_emps = db.query(BaseEmployee.employee_id).filter(
            or_(BaseEmployee.direct_manager_id == str(team_leader_id), BaseEmployee.direct_manager_name == '王军')
        ).all()
        leader_subordinate_ids = [e[0] for e in leader_emps]
    else:
        leader_emps = db.query(BaseEmployee.employee_id).filter(
            or_(BaseEmployee.direct_manager_id == '404201195', BaseEmployee.direct_manager_name == '王军')
        ).all()
        leader_subordinate_ids = [e[0] for e in leader_emps]

    # 当月中包车间打卡考勤与考评人员
    att_q = db.query(BizEmployeeAttendance.employee_id)
    if start_date and end_date:
        att_q = att_q.filter(
            BizEmployeeAttendance.attendance_date >= start_date,
            BizEmployeeAttendance.attendance_date <= end_date
        )
    att_eids = [r[0] for r in att_q.distinct().all()]

    grade_q = db.query(BizEmployeeDailyGrade.employee_id)
    if start_date and end_date:
        grade_q = grade_q.filter(
            BizEmployeeDailyGrade.grade_date >= start_date,
            BizEmployeeDailyGrade.grade_date <= end_date
        )
    grade_eids = [r[0] for r in grade_q.distinct().all()]

    res = []
    seen = set()
    for eid in core_ids + leader_subordinate_ids + att_eids + grade_eids:
        if eid and eid not in seen:
            seen.add(eid)
            res.append(eid)
    return res

@report_bp.route("/grading", methods=["GET"])
def get_grading_report():
    db = SessionLocal()
    try:
        month_str = request.args.get('month') # e.g. '2026-09'
        if not month_str:
            month_str = '2026-09'
        
        year, month = map(int, month_str.split('-'))
        start_date = datetime(year, month, 1).date()
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime(year, month, last_day).date()

        team_leader_id = request.args.get('team_leader_id')
        # 仅筛选中包车间班组成员，避免渲染数千员工导致界面卡死
        member_ids = get_target_team_member_ids(db, start_date, end_date, team_leader_id)
        
        employees = db.query(BaseEmployee).filter(BaseEmployee.employee_id.in_(member_ids)).all()
        emp_dict = {e.employee_id: e for e in employees}
        sorted_employees = [emp_dict[eid] for eid in member_ids if eid in emp_dict]

        # Get grades for the month
        grades = db.query(BizEmployeeDailyGrade).filter(
            BizEmployeeDailyGrade.employee_id.in_(member_ids),
            BizEmployeeDailyGrade.grade_date >= start_date,
            BizEmployeeDailyGrade.grade_date <= end_date
        ).all()

        grade_map = {}
        for g in grades:
            d_str = str(g.grade_date)
            if g.employee_id not in grade_map:
                grade_map[g.employee_id] = {}
            score = g.score
            if score is not None and score >= 50:
                score = score - 86
            grade_map[g.employee_id][d_str] = score

        res = []
        for e in sorted_employees:
            e_grades = grade_map.get(e.employee_id, {})
            month_delta = sum(v for v in e_grades.values() if isinstance(v, (int, float)))
            res.append({
                "employee_id": e.employee_id,
                "employee_name": e.name,
                "grades": e_grades,
                "total_delta": month_delta,
                "monthly_score": 80 + month_delta
            })
        return jsonify(res)
    finally:
        db.close()

@report_bp.route("/grading", methods=["POST"])
def save_daily_grade():
    db = SessionLocal()
    try:
        data = request.json
        employee_id = data.get('employee_id')
        grade_date = data.get('grade_date')
        score = data.get('score')
        remark = data.get('remark', '')
        
        # update or insert
        grade = db.query(BizEmployeeDailyGrade).filter_by(employee_id=employee_id, grade_date=grade_date).first()
        if grade:
            grade.score = score
            grade.remark = remark
        else:
            grade = BizEmployeeDailyGrade(employee_id=employee_id, grade_date=grade_date, score=score, remark=remark)
            db.add(grade)
        
        db.commit()
        return jsonify({"message": "success"})
    finally:
        db.close()

@report_bp.route("/grading", methods=["DELETE"])
def delete_daily_grade():
    db = SessionLocal()
    try:
        emp_id = request.args.get('employee_id')
        g_date = request.args.get('grade_date')
        if emp_id and g_date:
            db.query(BizEmployeeDailyGrade).filter_by(employee_id=emp_id, grade_date=g_date).delete()
            db.commit()
        return jsonify({"message": "success"})
    finally:
        db.close()

@report_bp.route("/grading/template", methods=["GET"])
def download_grading_template():
    import io
    import openpyxl
    month_str = request.args.get('month', '2026-09')
    try:
        year, month = map(int, month_str.split('-'))
    except Exception:
        year, month = 2026, 9

    _, days_count = calendar.monthrange(year, month)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{month}月考评矩阵"

    headers = ["工号", "姓名"] + [f"{d}" for d in range(1, days_count + 1)] + ["月度分数"]
    ws.append(headers)

    db = SessionLocal()
    try:
        member_ids = get_target_team_member_ids(db)
        emps = db.query(BaseEmployee).filter(BaseEmployee.employee_id.in_(member_ids)).all()
        emp_dict = {e.employee_id: e for e in emps}
        sorted_emps = [emp_dict[eid] for eid in member_ids if eid in emp_dict]

        for e in sorted_emps:
            sample_scores = [0] * days_count
            for d in range(1, days_count + 1):
                try:
                    wd = datetime(year, month, d).weekday()
                    if wd in (5, 6):
                        sample_scores[d - 1] = "休"
                except:
                    pass
            formula = f"=80+SUM(C{ws.max_row+1}:{openpyxl.utils.get_column_letter(days_count+2)}{ws.max_row+1})"
            ws.append([e.employee_id, e.name] + sample_scores + [formula])
    finally:
        db.close()

    # Sheet 2: 清单明细格式
    ws2 = wb.create_sheet(title="清单格式(可选)")
    ws2.append(["工号", "姓名", "考评日期", "加减分(-4到4)", "备注"])
    ws2.append(["404201195", "王军", f"{year}-{month:02d}-24", 0, "表现平稳"])
    ws2.append(["404245800", "刘端阳", f"{year}-{month:02d}-24", 2, "表现优异加分"])

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return send_file(out, download_name=f"中包车间员工考评导入模板_{month_str}.xlsx", as_attachment=True)


@report_bp.route("/grading/export", methods=["GET"])
def export_grading_data():
    import io
    import openpyxl
    month_str = request.args.get('month', '2026-09')
    try:
        year, month = map(int, month_str.split('-'))
    except Exception:
        year, month = 2026, 9

    start_date = datetime(year, month, 1).date()
    _, days_count = calendar.monthrange(year, month)
    end_date = datetime(year, month, days_count).date()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{month}月考评表"

    headers = ["工号", "姓名"] + [f"{d}" for d in range(1, days_count + 1)] + ["月度分数"]
    ws.append(headers)

    db = SessionLocal()
    try:
        member_ids = get_target_team_member_ids(db, start_date, end_date)
        employees = db.query(BaseEmployee).filter(BaseEmployee.employee_id.in_(member_ids)).all()
        emp_dict = {e.employee_id: e for e in employees}
        sorted_emps = [emp_dict[eid] for eid in member_ids if eid in emp_dict]

        grades = db.query(BizEmployeeDailyGrade).filter(
            BizEmployeeDailyGrade.employee_id.in_(member_ids),
            BizEmployeeDailyGrade.grade_date >= start_date,
            BizEmployeeDailyGrade.grade_date <= end_date
        ).all()

        grade_map = {}
        for g in grades:
            d_str = str(g.grade_date)
            if g.employee_id not in grade_map:
                grade_map[g.employee_id] = {}
            score = g.score
            if score is not None and score >= 50:
                score = score - 86
            grade_map[g.employee_id][d_str] = score

        for e in sorted_emps:
            row_data = [e.employee_id, e.name]
            e_grades = grade_map.get(e.employee_id, {})
            total_delta = 0
            for d in range(1, days_count + 1):
                d_str = f"{year}-{month:02d}-{d:02d}"
                val = e_grades.get(d_str, "")
                if val != "" and val is not None:
                    row_data.append(val)
                    if isinstance(val, (int, float)):
                        total_delta += val
                else:
                    row_data.append("休")
            row_data.append(80 + total_delta)
            ws.append(row_data)
    finally:
        db.close()

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return send_file(out, download_name=f"中包车间员工考评数据_{month_str}.xlsx", as_attachment=True)


@report_bp.route("/grading/import", methods=["POST"])
def import_grading_data():
    if 'file' not in request.files:
        return jsonify({"error": "请选择要上传的 Excel 文件"}), 400

    file = request.files['file']
    month_str = request.args.get('month', '2026-09')
    try:
        year, month = map(int, month_str.split('-'))
    except Exception:
        year, month = 2026, 9

    import openpyxl
    from datetime import date
    try:
        wb = openpyxl.load_workbook(file, data_only=True)
    except Exception as e:
        return jsonify({"error": f"无法读取 Excel 文件: {str(e)}"}), 400

    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return jsonify({"error": "工作表为空，无法导入"}), 400

    db = SessionLocal()
    success = 0
    fail = 0
    errors = []
    records = []

    try:
        # Case A: AI每日评价.xlsx (Cell A1 is an employee name, Row 2 has dates)
        first_cell = str(rows[0][0]).strip() if rows[0][0] is not None else ""
        row2_vals = rows[1] if len(rows) > 1 else []
        is_date_row = any(isinstance(v, (datetime, date)) or (isinstance(v, str) and '-' in v) for v in row2_vals[:5] if v)

        if is_date_row and (len(first_cell) > 0 and not first_cell.isdigit() and first_cell not in ['工号', 'employee_id', '姓名']):
            emp = db.query(BaseEmployee).filter((BaseEmployee.name == first_cell) | (BaseEmployee.employee_id == first_cell)).first()
            emp_id = emp.employee_id if emp else '404201195'

            dates = []
            for col_idx, cell in enumerate(row2_vals):
                if cell:
                    if isinstance(cell, (datetime, date)):
                        dates.append((col_idx, cell.strftime('%Y-%m-%d')))
                    elif isinstance(cell, str) and '-' in cell:
                        dates.append((col_idx, cell.split(' ')[0]))

            score_row_idx = None
            for r_idx in range(len(rows) - 1, 1, -1):
                numeric_count = sum(1 for v in rows[r_idx] if isinstance(v, (int, float)))
                if numeric_count > 5:
                    score_row_idx = r_idx
                    break

            if score_row_idx is not None:
                score_row = rows[score_row_idx]
                for col_idx, d_str in dates:
                    if col_idx < len(score_row):
                        val = score_row[col_idx]
                        try:
                            score = int(float(val)) if val is not None else 0
                            records.append({
                                "employee_id": emp_id,
                                "grade_date": d_str,
                                "score": score,
                                "remark": "Excel指标汇总导入"
                            })
                        except:
                            pass
        else:
            headers = [str(c).strip() if c is not None else "" for c in rows[0]]
            date_col_idx = None
            score_col_idx = None
            emp_id_col_idx = None
            emp_name_col_idx = None
            remark_col_idx = None

            for idx, h in enumerate(headers):
                if h in ['考评日期', '日期', 'grade_date']:
                    date_col_idx = idx
                elif h in ['得分', '分数', '考评分数', 'score']:
                    score_col_idx = idx
                elif h in ['工号', '员工工号', 'employee_id']:
                    emp_id_col_idx = idx
                elif h in ['姓名', '员工姓名', 'name']:
                    emp_name_col_idx = idx
                elif h in ['备注', 'remark']:
                    remark_col_idx = idx

            if date_col_idx is not None and score_col_idx is not None:
                # Case C: 清单明细列表
                for r in rows[1:]:
                    if not any(r): continue
                    eid = str(r[emp_id_col_idx]).strip() if emp_id_col_idx is not None and r[emp_id_col_idx] else ""
                    name = str(r[emp_name_col_idx]).strip() if emp_name_col_idx is not None and r[emp_name_col_idx] else ""
                    if not eid and name:
                        emp = db.query(BaseEmployee).filter_by(name=name).first()
                        if emp: eid = emp.employee_id
                    if not eid: continue

                    raw_d = r[date_col_idx]
                    if isinstance(raw_d, (datetime, date)):
                        d_str = raw_d.strftime('%Y-%m-%d')
                    else:
                        d_str = str(raw_d).strip()

                    try:
                        score = int(float(r[score_col_idx]))
                    except:
                        score = 0
                    rem = str(r[remark_col_idx]).strip() if remark_col_idx is not None and r[remark_col_idx] else "清单明细导入"
                    records.append({
                        "employee_id": eid,
                        "grade_date": d_str,
                        "score": score,
                        "remark": rem
                    })
            else:
                # Case B: 矩阵打分表格式
                for r in rows[1:]:
                    if not any(r): continue
                    eid = str(r[emp_id_col_idx]).strip() if emp_id_col_idx is not None and r[emp_id_col_idx] else ""
                    name = str(r[emp_name_col_idx]).strip() if emp_name_col_idx is not None and r[emp_name_col_idx] else ""
                    if not eid and name:
                        emp = db.query(BaseEmployee).filter_by(name=name).first()
                        if emp: eid = emp.employee_id
                    if not eid:
                        if r[0] and str(r[0]).strip().isdigit():
                            eid = str(r[0]).strip()
                        elif r[0]:
                            emp = db.query(BaseEmployee).filter_by(name=str(r[0]).strip()).first()
                            if emp: eid = emp.employee_id
                    if not eid: continue

                    for idx, h in enumerate(headers):
                        day_str = h.replace('日', '').strip()
                        if day_str.isdigit():
                            day_int = int(day_str)
                            if 1 <= day_int <= 31:
                                val = r[idx] if idx < len(r) else None
                                d_str = f"{year:04d}-{month:02d}-{day_int:02d}"
                                if val in ['休', 'OFF', '-', '/', None, '']:
                                    score = 0
                                else:
                                    try:
                                        score = int(float(val))
                                    except:
                                        score = 0
                                records.append({
                                    "employee_id": eid,
                                    "grade_date": d_str,
                                    "score": score,
                                    "remark": "月度矩阵导入"
                                })

        for rec in records:
            try:
                with db.begin_nested():
                    existing = db.query(BizEmployeeDailyGrade).filter_by(
                        employee_id=rec['employee_id'],
                        grade_date=rec['grade_date']
                    ).first()
                    if existing:
                        existing.score = rec['score']
                        existing.remark = rec['remark']
                    else:
                        g = BizEmployeeDailyGrade(
                            employee_id=rec['employee_id'],
                            grade_date=rec['grade_date'],
                            score=rec['score'],
                            remark=rec['remark'],
                            graded_by='班组长'
                        )
                        db.add(g)
                    db.flush()
                success += 1
            except Exception as e:
                fail += 1
                errors.append(str(e))

        db.commit()
        return jsonify({
            "message": "Import finished",
            "total_read": len(records),
            "success": success,
            "fail": fail,
            "errors": errors[:5]
        })
    finally:
        db.close()
