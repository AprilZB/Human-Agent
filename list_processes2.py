import sys
sys.path.append('.')
from app.core.database import SessionLocal
import app.models.production as prod

db = SessionLocal()
processes = db.query(prod.BaseProcess).all()
for p in processes:
    print(p.process_code, p.process_name)
