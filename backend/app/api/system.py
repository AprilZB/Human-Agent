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
