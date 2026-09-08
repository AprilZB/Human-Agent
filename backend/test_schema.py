import sqlalchemy
from app.core.database import engine
with engine.connect() as conn:
    conn.execute(sqlalchemy.text("UPDATE biz_work_order SET status='ASSIGNED' WHERE status=''"))
    conn.commit()
    print("Database status fixed!")
