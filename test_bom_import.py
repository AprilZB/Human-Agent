import sys
sys.path.append('backend')
import pandas as pd
from app.api.data import HEADER_MAPPING
from app.models.master_data import BaseBom
from app.core.database import SessionLocal
import json

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
        if isinstance(v, pd.Timestamp):
            rec[k] = v.strftime('%Y-%m-%d %H:%M:%S')

# No generic aggregation in this test to see the DB error
db = SessionLocal()
try:
    for i, rec in enumerate(records):
        try:
            with db.begin_nested():
                pk_val = str(rec.get('bom_code'))
                existing = db.query(BaseBom).filter_by(bom_code=pk_val).first()
                if existing:
                    for k, v in rec.items():
                        setattr(existing, k, v)
                else:
                    obj = BaseBom(**rec)
                    db.add(obj)
                db.flush()
            print(f"Row {i} success")
        except Exception as e:
            print(f"Row {i} error: {e}")
except Exception as e:
    print("Outer error:", e)
finally:
    db.close()
