from flask import Blueprint, jsonify, request
from sqlalchemy import func
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
            q = q.filter(BizProductionOrder.scheduled_start_date >= start_date)
        if end_date:
            q = q.filter(BizProductionOrder.scheduled_start_date <= end_date)
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
        return jsonify([clean_dict(c) for c in confs])
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
            BaseEmployee.employee_name,
            func.sum(BizEmployeeAttendance.calculated_overtime).label('total_overtime')
        ).outerjoin(
            BaseEmployee, BizEmployeeAttendance.employee_id == BaseEmployee.employee_code
        )

        if start_date:
            q = q.filter(BizEmployeeAttendance.attendance_date >= start_date)
        if end_date:
            q = q.filter(BizEmployeeAttendance.attendance_date <= end_date)
        
        q = q.group_by(BizEmployeeAttendance.employee_id, BaseEmployee.employee_name)
        
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
        # this month and last month
        today = datetime.today()
        this_month_start = today.replace(day=1)
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        confs = db.query(BizEmployeeAttendance).filter(
            BizEmployeeAttendance.employee_id == employee_id,
            BizEmployeeAttendance.attendance_date >= last_month_start.date()
        ).order_by(BizEmployeeAttendance.attendance_date.desc()).all()

        return jsonify([clean_dict(c) for c in confs])
    finally:
        db.close()

@report_bp.route("/grading", methods=["GET"])
def get_grading_report():
    db = SessionLocal()
    try:
        month_str = request.args.get('month') # e.g. '2026-08'
        if not month_str:
            month_str = datetime.today().strftime('%Y-%m')
        
        year, month = map(int, month_str.split('-'))
        start_date = datetime(year, month, 1).date()
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime(year, month, last_day).date()

        # Get all employees
        employees = db.query(BaseEmployee).all()
        # Get grades for the month
        grades = db.query(BizEmployeeDailyGrade).filter(
            BizEmployeeDailyGrade.grade_date >= start_date,
            BizEmployeeDailyGrade.grade_date <= end_date
        ).all()

        grade_map = {}
        for g in grades:
            d_str = str(g.grade_date)
            if g.employee_id not in grade_map:
                grade_map[g.employee_id] = {}
            grade_map[g.employee_id][d_str] = g.score

        res = []
        for e in employees:
            res.append({
                "employee_id": e.employee_code,
                "employee_name": e.employee_name,
                "grades": grade_map.get(e.employee_code, {})
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
