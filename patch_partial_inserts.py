with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_logic = '''        db = SessionLocal()
        try:
            for rec in records:
                # To prevent Identity Map duplicate insert issues when merging new items,
                # we query the DB first to see if it exists.
                pk_name = model.__table__.primary_key.columns.keys()[0]
                pk_val = rec.get(pk_name)
                
                existing = None
                if pk_val is not None:
                    existing = db.query(model).filter(getattr(model, pk_name) == pk_val).first()
                
                if existing:
                    for k, v in rec.items():
                        setattr(existing, k, v)
                else:
                    obj = model(**rec)
                    db.add(obj)
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
                        existing_wo = db.query(prod.BizWorkOrder).filter_by(order_code=order_code).first()
                        if not existing_wo:
                            wo = prod.BizWorkOrder(
                                work_order_code=f"WO-{order_code}-01",
                                order_code=order_code,
                                process_code=first_process.process_code,
                                required_count=3,  # default 3 people needed
                                status='PENDING'
                            )
                            db.add(wo)
                    db.commit()
            
            return jsonify({"message": "Import successful", "count": len(records)})
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()'''

new_import_logic = '''        db = SessionLocal()
        success = 0
        fail = 0
        errors = []
        try:
            for i, rec in enumerate(records):
                try:
                    with db.begin_nested():
                        # To prevent Identity Map duplicate insert issues when merging new items,
                        # we query the DB first to see if it exists.
                        pk_name = model.__table__.primary_key.columns.keys()[0]
                        pk_val = rec.get(pk_name)
                        
                        existing = None
                        if pk_val is not None:
                            existing = db.query(model).filter(getattr(model, pk_name) == pk_val).first()
                        
                        if existing:
                            for k, v in rec.items():
                                setattr(existing, k, v)
                        else:
                            obj = model(**rec)
                            db.add(obj)
                        db.flush()
                    success += 1
                except Exception as e:
                    fail += 1
                    errors.append(f"Row {i+1} failed: {str(e)}")
            
            db.commit()
            
            # Auto-generate Work Orders for Production Orders to make them show up in dispatch
            if tab_name == 'production-orders':
                import app.models.production as prod
                # Get the first process as default
                first_process = db.query(prod.BaseProcess).first()
                if first_process:
                    for rec in records:
                        try:
                            with db.begin_nested():
                                order_code = rec.get('order_code')
                                # Check if a work order already exists
                                existing_wo = db.query(prod.BizWorkOrder).filter_by(order_code=order_code).first()
                                if not existing_wo:
                                    wo = prod.BizWorkOrder(
                                        work_order_code=f"WO-{order_code}-01",
                                        order_code=order_code,
                                        process_code=first_process.process_code,
                                        required_count=3,  # default 3 people needed
                                        status='PENDING'
                                    )
                                    db.add(wo)
                                db.flush()
                        except:
                            pass
                    db.commit()
            
            return jsonify({
                "message": "Import finished", 
                "total_read": len(records),
                "success": success,
                "fail": fail,
                "errors": errors[:10] # limit returned errors
            })
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()'''

code = code.replace(import_logic, new_import_logic)
with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
