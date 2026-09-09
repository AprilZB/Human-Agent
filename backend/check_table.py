from app.core.database import engine
from sqlalchemy import text
with engine.begin() as conn:
    res = conn.execute(text("SHOW TABLES LIKE 'base_material_group'")).fetchall()
    print("base_material_group exists:", len(res) > 0)
    if len(res) > 0:
        res2 = conn.execute(text("SHOW CREATE TABLE base_material_group")).fetchall()
        print(res2[0][1])
