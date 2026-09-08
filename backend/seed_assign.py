from app.core.database import SessionLocal
from app.models.production import BizWorkOrder, TaskPersonnelAssignment
import datetime

db = SessionLocal()
try:
    pending_wos = db.query(BizWorkOrder).filter(BizWorkOrder.status.in_(['PENDING', 'UNASSIGNED'])).all()
    
    for wo in pending_wos:
        existing = db.query(TaskPersonnelAssignment).filter_by(work_order_code=wo.work_order_code).first()
        if not existing:
            # Add AI recommendations
            for i in range(wo.required_count):
                emp_id = f"EMP00{i+1}"
                assignment = TaskPersonnelAssignment(
                    work_order_code=wo.work_order_code,
                    employee_id=emp_id,
                    status='AI_RECOMMENDED',
                    recommend_reason="AI 自动匹配推荐 (技能与工时符合最优解)",
                    created_at=datetime.datetime.now()
                )
                db.add(assignment)
                
    db.commit()
    print("AI Recommendations seeded successfully!")
finally:
    db.close()
