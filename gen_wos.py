import sys
sys.path.append('.')
from app.core.database import SessionLocal
import app.models.production as prod

db = SessionLocal()
orders = db.query(prod.BizProductionOrder).all()
first_process = db.query(prod.BaseProcess).first()

if first_process:
    count = 0
    for order in orders:
        existing = db.query(prod.BizWorkOrder).filter_by(order_code=order.order_code).first()
        if not existing:
            wo = prod.BizWorkOrder(
                work_order_code=f"WO-{order.order_code}-01",
                order_code=order.order_code,
                process_code=first_process.process_code,
                required_count=3,
                status='PENDING'
            )
            db.add(wo)
            count += 1
    db.commit()
    print(f"Retroactively generated {count} work orders.")
else:
    print("No processes found.")
