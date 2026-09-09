import sqlalchemy
from app.core.database import engine
with engine.connect() as conn:
    res = conn.execute(sqlalchemy.text("SHOW TABLES")).fetchall()
    print([r[0] for r in res])
