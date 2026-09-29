import sys
sys.path.append('backend')
from app.api.data import HEADER_MAPPING
import pandas as pd
import json

file_path = 'd:/DEV/Human-Agent/导入文件/AI智能体员工档案中包间.xlsx'
df = pd.read_excel(file_path)
df.rename(columns=HEADER_MAPPING, inplace=True)
df.columns = [str(c).strip().lower() for c in df.columns]

from app.models.master_data import BaseEmployee
model_cols = [c.name for c in BaseEmployee.__table__.columns]
valid_cols = [c for c in df.columns if c in model_cols]

df = df[valid_cols]
df = df.where(pd.notnull(df), None)
records = df.to_dict(orient='records')

for rec in records:
    for k, v in rec.items():
        if isinstance(v, str) and (v.strip().startswith('{') or v.strip().startswith('[')):
            try:
                rec[k] = json.loads(v)
            except:
                pass
print("Records parsed successfully:")
print(records[:1])
