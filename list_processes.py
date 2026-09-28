import sys
sys.path.append('.')
from app.core.database import SessionLocal
import app.models.master_data as md

db = SessionLocal()
processes = db.query(md.BaseProcess).all()
for p in processes:
    print(p.process_code, p.process_name)
