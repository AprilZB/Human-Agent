with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_logic = '''                        # To prevent Identity Map duplicate insert issues when merging new items,
                        # we query the DB first to see if it exists.
                        pk_name = model.__table__.primary_key.columns.keys()[0]
                        pk_val = rec.get(pk_name)
                        
                        existing = None
                        if pk_val is not None:
                            existing = db.query(model).filter(getattr(model, pk_name) == pk_val).first()'''

new_import_logic = '''                        # To prevent Identity Map duplicate insert issues when merging new items,
                        # we query the DB first to see if it exists.
                        pk_names = model.__table__.primary_key.columns.keys()
                        
                        existing = None
                        # Ensure all primary key parts are present
                        if all(rec.get(pk) is not None for pk in pk_names):
                            filters = [getattr(model, pk) == rec.get(pk) for pk in pk_names]
                            existing = db.query(model).filter(*filters).first()'''

code = code.replace(import_logic, new_import_logic)
with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
