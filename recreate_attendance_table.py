import sys
sys.path.append('.')
from app.core.database import engine, Base
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS biz_employee_attendance"))
    conn.commit()

from app.models.production import *
Base.metadata.create_all(bind=engine)
print("Table dropped and recreated successfully with new schema.")
