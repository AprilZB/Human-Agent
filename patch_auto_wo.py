with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_logic_old = '''            for rec in records:
                # Merge does an upsert if primary key matches
                obj = model(**rec)
                db.merge(obj)
            db.commit()'''

import_logic_new = '''            for rec in records:
                # Merge does an upsert if primary key matches
                obj = model(**rec)
                db.merge(obj)
            db.commit()
            
            # Auto-generate Work Orders for Production Orders to make them show up in dispatch
            if tab_name == 'production-orders':
                import app.models.production as prod
                # Get the first process as default
                first_process = db.query(prod.BaseProcess).first()
                if first_process:
                    for rec in records:
                        order_code = rec.get('order_code')
                        # Check if a work order already exists
                        existing = db.query(prod.BizWorkOrder).filter_by(order_code=order_code).first()
                        if not existing:
                            wo = prod.BizWorkOrder(
                                work_order_code=f"WO-{order_code}-01",
                                order_code=order_code,
                                process_code=first_process.process_code,
                                required_count=3,  # default 3 people needed
                                status='PENDING'
                            )
                            db.add(wo)
                    db.commit()'''

code = code.replace(import_logic_old, import_logic_new)
with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
