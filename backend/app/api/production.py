from flask import Blueprint, jsonify, request
from app.core.database import SessionLocal
from app.models.production import BizProductionOrder
from app.services.dispatch_service import decompose_production_order
from app.services.match_service import run_intelligent_matching
import asyncio

production_bp = Blueprint('production', __name__)

@production_bp.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    db = SessionLocal()
    try:
        db_order = BizProductionOrder(**data)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return jsonify({
            "order_code": db_order.order_code,
            "material_code": db_order.material_code,
            "target_quantity": db_order.target_quantity,
            "status": db_order.status
        })
    finally:
        db.close()

@production_bp.route("/orders", methods=["GET"])
def get_orders():
    db = SessionLocal()
    try:
        orders = db.query(BizProductionOrder).all()
        return jsonify([{
            "order_code": o.order_code,
            "material_code": o.material_code,
            "target_quantity": o.target_quantity,
            "status": o.status
        } for o in orders])
    finally:
        db.close()

@production_bp.route("/orders/<order_code>/decompose", methods=["POST"])
def decompose_order(order_code):
    db = SessionLocal()
    try:
        work_orders = decompose_production_order(db, order_code)
        return jsonify({"message": "Decomposed successfully", "count": len(work_orders)})
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400
    finally:
        db.close()

@production_bp.route("/work-orders/<wo_code>/match", methods=["POST"])
def intelligent_match(wo_code):
    db = SessionLocal()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        assignments = loop.run_until_complete(run_intelligent_matching(db, wo_code))
        return jsonify({"message": "Intelligent matching completed", "matched_count": len(assignments)})
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400
    finally:
        db.close()
