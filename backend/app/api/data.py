from flask import Blueprint, jsonify, request
from app.core.database import SessionLocal
import app.models.master_data as md
import app.models.production as prod
from sqlalchemy import or_

data_bp = Blueprint('data', __name__)

HEADER_MAPPING = {
    "生产订单号": "order_code",
    "订单编号": "order_code",
    "物料编码": "material_code",
    "目标数量": "target_quantity",
    "计划开始时间": "plan_start_time",
    "计划开始": "plan_start_time",
    "计划结束时间": "plan_end_time",
    "计划结束": "plan_end_time",
    "状态": "status",
    "工艺路线": "routing_code",
    
    # 员工出勤
    "考勤日期": "attendance_date",
    "工作日期": "attendance_date",
    "工号": "employee_id",
    "排班": "shift_code",
    "班次": "shift_code",
    "签到时间": "actual_punch_in",
    "签退时间": "actual_punch_out",
    "实际工时": "actual_work_hours",
    "出勤类型": "attendance_type",
    
    # 物料
    "物料描述": "material_desc",
    "基本单位": "base_uom",
    "物料组": "material_group_code",
    
    # 确认单
    "确认单号": "confirmation_no",
    "批次号": "batch_no",
    "工厂": "plant",
    "合格数量": "yield_quantity",
    "报废数量": "scrap_quantity",
    "执行日期": "exec_datetime",
    
    # 员工基本信息
    "姓名": "name",
    "车间": "workshop_code",
    "健康证状态": "health_cert_status",
    "上岗证状态": "work_cert_status",
    "健康证状态/有效期": "health_cert_status",
    "上岗证状态/有效期": "work_cert_status",
    "技能矩阵": "skills"
}


def paginate(query):
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return {"total": total, "page": page, "size": size, "records": [item.__dict__ for item in items]}

import datetime
from decimal import Decimal

def clean_dict(d):
    res = {}
    for k, v in d.items():
        if not k.startswith('_'):
            if isinstance(v, (datetime.datetime, datetime.date)):
                res[k] = v.isoformat()
            elif isinstance(v, Decimal):
                res[k] = float(v)
            else:
                res[k] = v
    return res

@data_bp.route("/materials", methods=["GET"])
def get_materials():
    db = SessionLocal()
    try:
        q = db.query(md.BaseMaterial)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(md.BaseMaterial.material_code.like(f"%{keyword}%"), md.BaseMaterial.material_desc.like(f"%{keyword}%")))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/employees", methods=["GET"])
def get_employees():
    db = SessionLocal()
    try:
        q = db.query(md.BaseEmployee)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(md.BaseEmployee.employee_id.like(f"%{keyword}%"), md.BaseEmployee.name.like(f"%{keyword}%")))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/production-orders", methods=["GET"])
def get_production_orders():
    db = SessionLocal()
    try:
        q = db.query(prod.BizProductionOrder)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(prod.BizProductionOrder.order_code.like(f"%{keyword}%"), prod.BizProductionOrder.material_code.like(f"%{keyword}%")))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/workshops", methods=["GET"])
def get_workshops():
    db = SessionLocal()
    try:
        q = db.query(md.BaseWorkshop)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/defect-reasons", methods=["GET"])
def get_defect_reasons():
    db = SessionLocal()
    try:
        q = db.query(md.BaseDefectReason)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/material-groups", methods=["GET"])
def get_material_groups():
    db = SessionLocal()
    try:
        q = db.query(md.BaseMaterialGroup)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/routings", methods=["GET"])
def get_routings():
    db = SessionLocal()
    try:
        q = db.query(md.BaseRouting)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/processes", methods=["GET"])
def get_processes():
    db = SessionLocal()
    try:
        q = db.query(prod.BaseProcess)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/boms", methods=["GET"])
def get_boms():
    db = SessionLocal()
    try:
        q = db.query(md.BaseBom)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

from flask import send_file
import pandas as pd
import io

# Generic Import/Export Map
TAB_MODEL_MAP = {
    "materials": md.BaseMaterial,
    "production-orders": prod.BizProductionOrder,
    "employees": md.BaseEmployee,
    "workshops": md.BaseWorkshop,
    "defect-reasons": md.BaseDefectReason,
    "material-groups": md.BaseMaterialGroup,
    "routings": md.BaseRouting,
    "processes": prod.BaseProcess,
    "boms": md.BaseBom,
    "confirmations": prod.BizProductionConfirmation,
    "attendances": prod.BizEmployeeAttendance
}

@data_bp.route("/confirmations", methods=["GET"])
def get_confirmations():
    db = SessionLocal()
    try:
        q = db.query(prod.BizProductionConfirmation)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(prod.BizProductionConfirmation.order_code.like(f"%{keyword}%"), prod.BizProductionConfirmation.material_code.like(f"%{keyword}%")))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/<tab_name>/export", methods=["GET"])
def export_data(tab_name):
    if tab_name not in TAB_MODEL_MAP:
        return jsonify({"error": "Invalid tab"}), 400
        
    model = TAB_MODEL_MAP[tab_name]
    is_template = request.args.get('template') == '1'
    
    db = SessionLocal()
    try:
        if is_template:
            data = []
        else:
            items = db.query(model).all()
            data = [clean_dict(item.__dict__) for item in items]
        
        if not data:
            cols = [c.name for c in model.__table__.columns if c.name not in ['id', 'created_at']]
            df = pd.DataFrame(columns=cols)
        else:
            # Reorder columns to ensure id and created_at are at the end or removed if not wanted.
            # But here we just use pandas defaults for data
            df = pd.DataFrame(data)
            
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            
        out.seek(0)
        filename = f"{tab_name}_template.xlsx" if is_template else f"{tab_name}.xlsx"
        return send_file(out, download_name=filename, as_attachment=True)
    finally:
        db.close()

@data_bp.route("/<tab_name>/import", methods=["POST"])
def import_data(tab_name):
    if tab_name not in TAB_MODEL_MAP:
        return jsonify({"error": "Invalid tab"}), 400
        
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    model = TAB_MODEL_MAP[tab_name]
    
    try:
        df = pd.read_excel(file)
        # Rename columns based on mapping if they match
        df.rename(columns=HEADER_MAPPING, inplace=True)
        # Also, lowercase the headers just in case they are english but capitalized
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Keep only columns that exist in the model
        model_cols = [c.name for c in model.__table__.columns]
        valid_cols = [c for c in df.columns if c in model_cols]
        if not valid_cols:
            return jsonify({"error": "No valid columns found in the uploaded file"}), 400
            
        df = df[valid_cols]
        
        # Handle nan -> None
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')
        
        # Parse JSON fields if necessary
        import json
        import pandas as pd
        for rec in records:
            for k, v in rec.items():
                if isinstance(v, pd.Timestamp):
                    rec[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(v, str) and (v.strip().startswith('{') or v.strip().startswith('[')):
                    try:
                        rec[k] = json.loads(v)
                    except:
                        pass
        
        # Special aggregation for employees: they might have multiple rows for different skills
        if tab_name == 'employees':
            emp_dict = {}
            for rec in records:
                eid = rec.get('employee_id')
                if eid not in emp_dict:
                    emp_dict[eid] = rec.copy()
                    # Ensure skills is a list
                    skill = emp_dict[eid].get('skills')
                    if skill and isinstance(skill, str):
                        emp_dict[eid]['skills'] = [skill]
                    elif not skill:
                        emp_dict[eid]['skills'] = []
                else:
                    # Append skill
                    skill = rec.get('skills')
                    if skill and isinstance(skill, str):
                        if isinstance(emp_dict[eid].get('skills'), list):
                            emp_dict[eid]['skills'].append(skill)
            records = list(emp_dict.values())

        db = SessionLocal()
        try:
            for rec in records:
                # To prevent Identity Map duplicate insert issues when merging new items,
                # we query the DB first to see if it exists.
                pk_name = model.__table__.primary_key.columns.keys()[0]
                pk_val = rec.get(pk_name)
                
                existing = None
                if pk_val is not None:
                    existing = db.query(model).filter(getattr(model, pk_name) == pk_val).first()
                
                if existing:
                    for k, v in rec.items():
                        setattr(existing, k, v)
                else:
                    obj = model(**rec)
                    db.add(obj)
            db.commit()
            
            # Auto-generate Work Orders for Production Orders to make them show up in dispatch
            if tab_name == 'production-orders':
                import app.models.production as prod
                # Get the first process as default
                first_process = db.query(prod.BaseProcess).first()
                if first_process:
                    for rec in records:
                        order_code = rec.get('order_code')
                        # Check if a work order already exists
                        existing = db.query(prod.BizWorkOrder).filter_by(order_code=order_code).first()
                        if not existing:
                            wo = prod.BizWorkOrder(
                                work_order_code=f"WO-{order_code}-01",
                                order_code=order_code,
                                process_code=first_process.process_code,
                                required_count=3,  # default 3 people needed
                                status='PENDING'
                            )
                            db.add(wo)
                    db.commit()
            return jsonify({"message": "Import successful", "count": len(records)})
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@data_bp.route("/attendances", methods=["GET"])
def get_attendances():
    db = SessionLocal()
    try:
        q = db.query(prod.BizEmployeeAttendance)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(prod.BizEmployeeAttendance.employee_id.like(f"%{keyword}%"))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()
