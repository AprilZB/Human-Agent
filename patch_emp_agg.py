with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_logic = '''        db = SessionLocal()
        try:
            for rec in records:
                # Merge does an upsert if primary key matches
                obj = model(**rec)
                db.merge(obj)
            db.commit()'''

new_import_logic = '''        # Special aggregation for employees: they might have multiple rows for different skills
        if tab_name == 'employees':
            emp_dict = {}
            for rec in records:
                eid = rec.get('employee_id')
                if eid not in emp_dict:
                    emp_dict[eid] = rec.copy()
                    # Ensure skills is a list
                    skill = emp_dict[eid].get('skills')
                    if skill and isinstance(skill, str):
                        emp_dict[eid]['skills'] = [skill]
                    elif not skill:
                        emp_dict[eid]['skills'] = []
                else:
                    # Append skill
                    skill = rec.get('skills')
                    if skill and isinstance(skill, str):
                        if isinstance(emp_dict[eid].get('skills'), list):
                            emp_dict[eid]['skills'].append(skill)
            records = list(emp_dict.values())

        db = SessionLocal()
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
            db.commit()'''

code = code.replace(import_logic, new_import_logic)
with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
