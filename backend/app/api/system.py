from flask import Blueprint, jsonify, request
from app.core.database import SessionLocal
from app.models.system import SysConfig

system_bp = Blueprint('system', __name__)

@system_bp.route("/configs", methods=["GET"])
def get_configs():
    db = SessionLocal()
    try:
        configs = db.query(SysConfig).all()
        return jsonify([{"id": c.id, "config_key": c.config_key, "config_value": c.config_value, "description": c.description} for c in configs])
    finally:
        db.close()

@system_bp.route("/configs/<config_key>", methods=["PUT"])
def update_config(config_key):
    db = SessionLocal()
    try:
        data = request.json
        config = db.query(SysConfig).filter(SysConfig.config_key == config_key).first()
        if not config:
            return jsonify({"detail": "Config not found"}), 404
        if "config_value" in data:
            config.config_value = str(data["config_value"])
        db.commit()
        return jsonify({"message": "Success", "config_key": config.config_key, "config_value": config.config_value})
    finally:
        db.close()


from app.models.system import SysAttendanceRule
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

@system_bp.route("/attendance-rules", methods=["GET"])
def get_attendance_rules():
    db = SessionLocal()
    try:
        rules = db.query(SysAttendanceRule).all()
        # manual clean dict
        data = []
        for r in rules:
            d = r.__dict__.copy()
            d.pop('_sa_instance_state', None)
            if d.get('start_time'):
                d['start_time'] = str(d['start_time'])
            if d.get('end_time'):
                d['end_time'] = str(d['end_time'])
            if d.get('created_at'):
                d['created_at'] = str(d['created_at'])
            data.append(d)
        return jsonify(data)
    finally:
        db.close()

@system_bp.route("/attendance-rules", methods=["POST"])
def create_attendance_rule():
    db = SessionLocal()
    try:
        data = request.json
        rule = SysAttendanceRule(**data)
        db.merge(rule)
        db.commit()
        return jsonify({"message": "success"})
    finally:
        db.close()

@system_bp.route("/attendance-rules/<shift_code>", methods=["DELETE"])
def delete_attendance_rule(shift_code):
    db = SessionLocal()
    try:
        rule = db.query(SysAttendanceRule).filter_by(shift_code=shift_code).first()
        if rule:
            db.delete(rule)
            db.commit()
        return jsonify({"message": "success"})
    finally:
        db.close()
