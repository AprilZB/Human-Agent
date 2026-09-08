import sqlalchemy
from app.core.database import engine
with engine.connect() as conn:
    res = conn.execute(sqlalchemy.text("SELECT * FROM sys_config")).fetchall()
    print(res)
