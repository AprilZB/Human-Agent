with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_logic = '''        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')
        
        db = SessionLocal()'''

new_import_logic = '''        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')
        
        # Parse JSON fields if necessary
        import json
        for rec in records:
            for k, v in rec.items():
                if isinstance(v, str) and (v.strip().startswith('{') or v.strip().startswith('[')):
                    try:
                        rec[k] = json.loads(v)
                    except:
                        pass
        
        db = SessionLocal()'''

code = code.replace(import_logic, new_import_logic)
with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
