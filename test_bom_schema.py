import sys
sys.path.append('backend')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
res = db.execute(text("SHOW CREATE TABLE base_bom")).fetchone()
print(res[1])
