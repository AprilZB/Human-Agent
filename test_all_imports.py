import os
import sys
sys.path.append('backend')
from app.core.database import SessionLocal
from app.api.data import TAB_MODEL_MAP, HEADER_MAPPING
import pandas as pd
import json

folder = 'd:/DEV/Human-Agent/导入文件/'
files = [f for f in os.listdir(folder) if f.endswith('.xlsx')]

# A helper to map file names to tab_names (based on guessing)
FILE_TAB_MAP = {
    'AI BOM档案.xlsx': 'boms',
    'AI报工.xlsx': 'confirmations',
    'AI不良原因档案.xlsx': 'defect-reasons',
    'AI车间档案.xlsx': 'workshops',
    'AI打卡记录.xlsx': 'attendances',
    'AI工序档案.xlsx': 'processes',
    'AI每日评价.xlsx': 'grading', # not in generic tab map
    'AI物料.xlsx': 'materials',
    'AI物料组.xlsx': 'material-groups',
    'AI员工档案.xlsx': 'employees',
    'AI工艺路线档案.xlsx': 'routings',
    'AI智能体员工档案中包间.xlsx': 'employees',
    'AI智能体中包含生产订单信息表格.xlsx': 'production-orders'
}

for file in files:
    if '评价' in file:
        continue
    
    print(f"\n--- Testing {file} ---")
    tab_name = None
    for k, v in FILE_TAB_MAP.items():
        if k in file:
            tab_name = v
            break
            
    if not tab_name:
        print("Unknown tab mapping")
        continue
        
    model = TAB_MODEL_MAP.get(tab_name)
    if not model:
        print(f"No model for tab {tab_name}")
        continue
        
    try:
        df = pd.read_excel(os.path.join(folder, file))
        # Rename columns based on mapping
        df.rename(columns=HEADER_MAPPING, inplace=True)
        # Convert to lower string
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        model_cols = [c.name for c in model.__table__.columns]
        valid_cols = [c for c in df.columns if c in model_cols]
        
        if not valid_cols:
            print(f"ERROR: No valid columns found. File columns: {df.columns.tolist()}, Model columns: {model_cols}")
            continue
            
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
        
        # Test merging logic
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
            db.flush() # test flush constraints
            db.rollback()
            print("SUCCESS (Dry run passed)")
        except Exception as e:
            db.rollback()
            print("DB ERROR:", str(e))
        finally:
            db.close()
            
    except Exception as e:
        print("READ ERROR:", str(e))

