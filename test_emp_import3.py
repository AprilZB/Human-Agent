import sys
sys.path.append('backend')
from app.api.data import import_data
from app.core.database import SessionLocal
import pandas as pd
import json

file_path = 'd:/DEV/Human-Agent/导入文件/AI智能体员工档案中包间.xlsx'
df = pd.read_excel(file_path)

from app.api.data import HEADER_MAPPING
df.rename(columns=HEADER_MAPPING, inplace=True)
df.columns = [str(c).strip().lower() for c in df.columns]

from app.models.master_data import BaseEmployee
model = BaseEmployee
model_cols = [c.name for c in model.__table__.columns]
valid_cols = [c for c in df.columns if c in model_cols]

df = df[valid_cols]
df = df.where(pd.notnull(df), None)
records = df.to_dict(orient='records')

for rec in records:
    for k, v in rec.items():
        if isinstance(v, pd.Timestamp):
            rec[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(v, str) and (v.strip().startswith('{') or v.strip().startswith('[')):
            try:
                rec[k] = json.loads(v)
            except:
                pass

emp_dict = {}
for rec in records:
    eid = rec.get('employee_id')
    if eid not in emp_dict:
        emp_dict[eid] = rec.copy()
        skill = emp_dict[eid].get('skills')
        if skill and isinstance(skill, str):
            emp_dict[eid]['skills'] = [skill]
        elif not skill:
            emp_dict[eid]['skills'] = []
    else:
        skill = rec.get('skills')
        if skill and isinstance(skill, str):
            if isinstance(emp_dict[eid].get('skills'), list):
                emp_dict[eid]['skills'].append(skill)
records = list(emp_dict.values())

db = SessionLocal()
try:
    for rec in records:
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
    print("SUCCESS")
except Exception as e:
    print("ERROR:", str(e))
finally:
    db.close()
