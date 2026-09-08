from sqlalchemy.orm import Session
from app.models.production import BizProductionOrder, BizWorkOrder
from app.models.master_data import BaseRoutingDetail
import uuid

def decompose_production_order(db: Session, order_code: str):
    """
    将生产订单依据工艺路线拆解为具体的工单任务 (Work Orders)
    """
    order = db.query(BizProductionOrder).filter(BizProductionOrder.order_code == order_code).first()
    if not order:
        raise ValueError(f"Order {order_code} not found")
        
    if not order.routing_code:
        raise ValueError(f"Order {order_code} has no routing code assigned")
        
    # 查询该工艺路线下的所有工序明细
    routing_details = db.query(BaseRoutingDetail).filter(
        BaseRoutingDetail.routing_code == order.routing_code
    ).order_by(BaseRoutingDetail.step_seq).all()
    
    if not routing_details:
        raise ValueError(f"No routing details found for {order.routing_code}")
        
    work_orders = []
    for detail in routing_details:
        # 为每道工序生成一个派工单
        wo_code = f"WO-{order_code}-{detail.step_seq}"
        wo = BizWorkOrder(
            work_order_code=wo_code,
            order_code=order_code,
            process_code=detail.process_code,
            required_count=1, # 默认1人，实际业务可结合产能模型调整
            status='PENDING'
        )
        db.add(wo)
        work_orders.append(wo)
        
    db.commit()
    return work_orders
