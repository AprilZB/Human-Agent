from flask import Blueprint, jsonify, request
from app.core.database import SessionLocal
from app.models.system import SysConfig, SysAttendanceRule
from sqlalchemy.orm import Session
from sqlalchemy import or_

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


@system_bp.route("/attendance-rules", methods=["GET"])
def get_attendance_rules():
    db = SessionLocal()
    try:
        rules = db.query(SysAttendanceRule).all()
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


# ================= APHR 人事系统对接与同步接口 =================
from app.services.aphr_service import (
    get_config_dict,
    set_config_dict,
    test_aphr_connection,
    sync_employees_from_aphr,
    update_scheduler_settings,
    aphr_scheduler,
    init_aphr_scheduler
)
from app.models.master_data import BaseEmployee

try:
    init_aphr_scheduler()
except:
    pass

@system_bp.route("/aphr/config", methods=["GET"])
def get_aphr_config():
    db = SessionLocal()
    try:
        cfg = get_config_dict(db)
        job = aphr_scheduler.get_job("aphr_sync_job") if aphr_scheduler.running else None
        next_run = None
        if job and job.next_run_time:
            next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
        is_running = aphr_scheduler.running and job is not None and job.next_run_time is not None
        
        return jsonify({
            "config": cfg,
            "scheduler_running": is_running,
            "next_run_time": next_run
        })
    finally:
        db.close()

@system_bp.route("/aphr/config", methods=["POST"])
def save_aphr_config():
    db = SessionLocal()
    try:
        data = request.json or {}
        set_config_dict(db, data)
        
        enabled = str(data.get("APHR_SYNC_ENABLED", "true")).lower() == "true"
        interval = int(data.get("APHR_SYNC_INTERVAL_MIN", "60"))
        try:
            update_scheduler_settings(enabled, interval)
        except Exception:
            pass
            
        return jsonify({"message": "配置保存成功", "config": get_config_dict(db)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@system_bp.route("/aphr/test", methods=["POST"])
def test_aphr_conn():
    db = SessionLocal()
    try:
        data = request.json or {}
        cfg = get_config_dict(db)
        base_url = data.get("base_url") or cfg.get("APHR_BASE_URL")
        username = data.get("username") or cfg.get("APHR_USERNAME")
        password = data.get("password") or cfg.get("APHR_PASSWORD")
        
        result = test_aphr_connection(base_url, username, password)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    finally:
        db.close()

@system_bp.route("/aphr/sync", methods=["POST"])
def trigger_aphr_sync():
    try:
        custom_cfg = request.json or None
        report = sync_employees_from_aphr(custom_cfg)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e), "status": "FAILED"}), 500

@system_bp.route("/aphr/employees", methods=["GET"])
def get_aphr_synced_employees():
    db = SessionLocal()
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 10))
        keyword = request.args.get("keyword", "").strip()
        
        q = db.query(BaseEmployee)
        if keyword:
            q = q.filter(or_(
                BaseEmployee.employee_id.like(f"%{keyword}%"),
                BaseEmployee.name.like(f"%{keyword}%"),
                BaseEmployee.workshop_code.like(f"%{keyword}%")
            ))
            
        total = q.count()
        items = q.order_by(BaseEmployee.employee_id.asc()).offset((page - 1) * size).limit(size).all()
        
        records = []
        for emp in items:
            records.append({
                "employee_id": emp.employee_id,
                "name": emp.name,
                "workshop_code": emp.workshop_code,
                "health_cert_status": emp.health_cert_status,
                "work_cert_status": emp.work_cert_status,
                "skills": emp.skills or [],
                "created_at": emp.created_at.strftime("%Y-%m-%d %H:%M:%S") if emp.created_at else None
            })
            
        return jsonify({
            "total": total,
            "page": page,
            "size": size,
            "records": records
        })
    finally:
        db.close()
