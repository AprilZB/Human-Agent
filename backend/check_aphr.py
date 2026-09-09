from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    # Try looking inside accupath db
    try:
        res = conn.execute(text("SHOW TABLES IN accupath LIKE '%schedule%'")).fetchall()
        print("accupath schedule tables:", [r[0] for r in res])
        res = conn.execute(text("SHOW TABLES IN accupath LIKE '%shift%'")).fetchall()
        print("accupath shift tables:", [r[0] for r in res])
        res = conn.execute(text("SHOW TABLES IN accupath LIKE '%holiday%'")).fetchall()
        print("accupath holiday tables:", [r[0] for r in res])
    except Exception as e:
        print("Error accessing accupath:", e)
