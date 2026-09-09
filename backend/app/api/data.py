from flask import Blueprint, jsonify, request
from app.core.database import SessionLocal
import app.models.master_data as md
import app.models.production as prod
from sqlalchemy import or_

data_bp = Blueprint('data', __name__)

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
        # Handle nan -> None
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')
        
        db = SessionLocal()
        try:
            for rec in records:
                # Merge does an upsert if primary key matches
                obj = model(**rec)
                db.merge(obj)
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
