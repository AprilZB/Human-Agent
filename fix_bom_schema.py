import sys
sys.path.append('backend')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
with open('fix_bom.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

for statement in sql.split(';'):
    if statement.strip():
        db.execute(text(statement))
db.commit()
print("Success")
