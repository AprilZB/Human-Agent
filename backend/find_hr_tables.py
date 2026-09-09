from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    dbs = conn.execute(text("SHOW DATABASES")).fetchall()
    for db in dbs:
        db_name = db[0]
        try:
            res = conn.execute(text(f"SHOW TABLES IN {db_name}")).fetchall()
            for r in res:
                table_name = r[0].lower()
                if any(x in table_name for x in ['shift', 'schedule', 'holiday', 'attend', 'class', 'banci', 'paiban', 'kaoqin', 'kao_qin', 'pai_ban']):
                    print(f"Found in {db_name}: {r[0]}")
        except Exception:
            pass
