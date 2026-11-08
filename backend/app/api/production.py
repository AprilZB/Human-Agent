from flask import Blueprint, jsonify, request
from app.core.database import SessionLocal
from app.models.production import BizProductionOrder, BizWorkOrder, TaskPersonnelAssignment, BaseProcess
from app.services.dispatch_service import decompose_production_order
from app.services.match_service import run_intelligent_matching
from app.services.dingtalk_service import batch_send_by_employee_ids
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
                query = query.join(BizProductionOrder).filter(
                    BizProductionOrder.plan_start_time >= datetime.combine(target_date, datetime.min.time()),
                    BizProductionOrder.plan_start_time <= datetime.combine(target_date, datetime.max.time())
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
            po = db.query(BizProductionOrder).filter(BizProductionOrder.order_code == wo.order_code).first()
            proc = db.query(BaseProcess).filter(BaseProcess.process_code == wo.process_code).first()
            
            assignments = db.query(TaskPersonnelAssignment).filter(TaskPersonnelAssignment.work_order_code == wo.work_order_code).all()
            if not assignments and wo.status in ['PENDING', 'UNASSIGNED']:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    assignments = loop.run_until_complete(run_intelligent_matching(db, wo.work_order_code))
                except Exception as ex:
                    print(f"Auto-match fallback error: {ex}")
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
    data = request.json or {}
    employee_ids = data.get("employee_ids") or []
    if isinstance(employee_ids, str):
        employee_ids = [e.strip() for e in employee_ids.split(",") if e.strip()]
    if not employee_ids and data.get("employee_id"):
        employee_ids = [str(data.get("employee_id")).strip()]
        
    wo_code = data.get("work_order_code", "")
    message = data.get("message")
    
    # 若有工单编码但未选人员，从该工单已派工表中获取
    if not employee_ids and wo_code:
        db = SessionLocal()
        try:
            assignments = db.query(TaskPersonnelAssignment).filter_by(work_order_code=wo_code).all()
            employee_ids = [a.employee_id for a in assignments if a.employee_id]
        finally:
            db.close()
            
    # 默认兜底：若未指定则推送测试工号 (张勃 404256402, 李丽丽 404191243)
    if not employee_ids:
        employee_ids = ["404256402", "404191243"]
        
    if not message:
        message = f"【派工提醒】您已被分配至生产任务工单：{wo_code or 'WO-13551286-01'}，工序：中包装，请按规范准时出勤开工。"
        
    report = batch_send_by_employee_ids(employee_ids, message, title="【生产现场派工提醒】")
    
    return jsonify({
        "success": report["success_count"] > 0,
        "message": f"成功向 {report['success_count']} 名员工发送钉钉工作通知",
        "report": report
    })
