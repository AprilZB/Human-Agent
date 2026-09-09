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
