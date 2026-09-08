from flask import Blueprint, jsonify, request
from app.core.database import SessionLocal
from app.models.production import BizProductionOrder, BizWorkOrder, TaskPersonnelAssignment, BaseProcess
from app.services.dispatch_service import decompose_production_order
from app.services.match_service import run_intelligent_matching
import asyncio
from datetime import datetime

production_bp = Blueprint('production', __name__)

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

@production_bp.route("/work-orders", methods=["GET"])
def get_work_orders():
    db = SessionLocal()
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        query = db.query(BizWorkOrder)
        
        if start_date_str:
            try:
                target_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(BizWorkOrder.created_at >= datetime.combine(target_start, datetime.min.time()))
            except ValueError:
                pass
                
        if end_date_str:
            try:
                target_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(BizWorkOrder.created_at <= datetime.combine(target_end, datetime.max.time()))
            except ValueError:
                pass
        
        date_str = request.args.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                query = query.filter(
                    BizWorkOrder.created_at >= datetime.combine(target_date, datetime.min.time()),
                    BizWorkOrder.created_at <= datetime.combine(target_date, datetime.max.time())
                )
            except ValueError:
                pass

        status_filter = request.args.get('status')
        if status_filter:
            statuses = status_filter.split(',')
            query = query.filter(BizWorkOrder.status.in_(statuses))
        else:
            query = query.filter(BizWorkOrder.status.in_(['PENDING', 'UNASSIGNED']))

        query = query.order_by(BizWorkOrder.created_at.desc())
        wos = query.all()
        
        result = []
        for wo in wos:
            # fetch related production order and process for details
            po = db.query(BizProductionOrder).filter(BizProductionOrder.order_code == wo.order_code).first()
            proc = db.query(BaseProcess).filter(BaseProcess.process_code == wo.process_code).first()
            
            assignments = db.query(TaskPersonnelAssignment).filter(TaskPersonnelAssignment.work_order_code == wo.work_order_code).all()
            emps = [{"employee_id": a.employee_id, "reason": a.recommend_reason} for a in assignments]
            
            result.append({
                "work_order_code": wo.work_order_code,
                "order_code": wo.order_code,
                "material_code": po.material_code if po else '未知产品',
                "target_quantity": po.target_quantity if po else 0,
                "process_code": wo.process_code,
                "process_name": proc.process_name if proc else '未知工序',
                "required_count": wo.required_count,
                "status": wo.status,
                "created_at": wo.created_at.strftime('%Y-%m-%d %H:%M:%S') if wo.created_at else None,
                "assignments": emps
            })
        return jsonify(result)
    finally:
        db.close()

@production_bp.route("/work-orders/<wo_code>/match", methods=["POST"])
def intelligent_match(wo_code):
    db = SessionLocal()
    try:
        db.query(TaskPersonnelAssignment).filter(TaskPersonnelAssignment.work_order_code == wo_code).delete()
        db.commit()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        assignments = loop.run_until_complete(run_intelligent_matching(db, wo_code))
        
        result = [{"employee_id": a.employee_id, "reason": a.recommend_reason} for a in assignments]
        return jsonify({"message": "Intelligent matching completed", "matched_count": len(result), "assignments": result})
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400
    finally:
        db.close()

@production_bp.route("/work-orders/<wo_code>/confirm-dispatch", methods=["POST"])
def confirm_dispatch(wo_code):
    db = SessionLocal()
    try:
        data = request.json
        final_employees = data.get('employees', [])
        
        wo = db.query(BizWorkOrder).filter(BizWorkOrder.work_order_code == wo_code).first()
        if not wo:
            return jsonify({"detail": "Work order not found"}), 404
            
        wo.status = 'ASSIGNED'
        
        db.query(TaskPersonnelAssignment).filter(TaskPersonnelAssignment.work_order_code == wo_code).delete()
        
        for emp_id in final_employees:
            assignment = TaskPersonnelAssignment(
                work_order_code=wo_code,
                employee_id=emp_id,
                status='CONFIRMED',
                recommend_reason='Manual adjustment / Confirmed'
            )
            db.add(assignment)
            
        db.commit()
        return jsonify({"message": "Dispatch confirmed successfully"})
    finally:
        db.close()

@production_bp.route("/dingtalk-push", methods=["POST"])
def dingtalk_push():
    data = request.json
    phone = data.get("phone", "15957270693")
    message = data.get("message", "Task assigned")
    
    print(f"========== DINGTALK PUSH ==========")
    print(f"Target Phone: {phone}")
    print(f"Message: {message}")
    print(f"===================================")
    
    return jsonify({"message": f"Successfully sent DingTalk message to {phone}", "success": True})
