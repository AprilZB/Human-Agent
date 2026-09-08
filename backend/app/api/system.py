from flask import Blueprint, jsonify
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
