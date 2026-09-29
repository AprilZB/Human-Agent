import sys
sys.path.append('backend')
import pandas as pd
from app.api.data import HEADER_MAPPING
from app.models.master_data import BaseBom
from app.core.database import SessionLocal
import json
import math

df = pd.read_excel('d:/DEV/Human-Agent/导入文件/boms_template.xlsx')
df.rename(columns=HEADER_MAPPING, inplace=True)
df.columns = [str(c).strip().lower() for c in df.columns]

model_cols = [c.name for c in BaseBom.__table__.columns]
valid_cols = [c for c in df.columns if c in model_cols]
df = df[valid_cols]
df = df.where(pd.notnull(df), None)
records = df.to_dict(orient='records')

for rec in records:
    for k, v in rec.items():
        if isinstance(v, float) and math.isnan(v):
            rec[k] = None
        elif isinstance(v, pd.Timestamp):
            rec[k] = v.strftime('%Y-%m-%d %H:%M:%S')

db = SessionLocal()
model = BaseBom
try:
    for i, rec in enumerate(records):
        try:
            with db.begin_nested():
                pk_names = model.__table__.primary_key.columns.keys()
                existing = None
                if all(rec.get(pk) is not None for pk in pk_names):
                    filters = [getattr(model, pk) == rec.get(pk) for pk in pk_names]
                    existing = db.query(model).filter(*filters).first()
                    
                if existing:
                    for k, v in rec.items():
                        setattr(existing, k, v)
                else:
                    obj = model(**rec)
                    db.add(obj)
                db.flush()
            print(f"Row {i} success")
        except Exception as e:
            print(f"Row {i} error: {e}")
except Exception as e:
    print("Outer error:", e)
finally:
    db.close()
