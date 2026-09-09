from app.core.database import engine
from sqlalchemy import text
with engine.begin() as conn:
    res = conn.execute(text("SHOW DATABASES")).fetchall()
    print([r[0] for r in res])
