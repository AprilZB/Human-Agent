from app.core.database import engine
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
    conn.execute(text("DROP TABLE IF EXISTS biz_work_order;"))
    conn.execute(text("DROP TABLE IF EXISTS biz_production_order;"))
    conn.execute(text("DROP TABLE IF EXISTS base_bom;"))
    conn.execute(text("DROP TABLE IF EXISTS base_routing_detail;"))
    conn.execute(text("DROP TABLE IF EXISTS base_routing;"))
    conn.execute(text("DROP TABLE IF EXISTS base_material;"))
    conn.execute(text("DROP TABLE IF EXISTS base_material_group;"))
    conn.execute(text("DROP TABLE IF EXISTS base_employee;"))
    conn.execute(text("DROP TABLE IF EXISTS base_team;"))
    conn.execute(text("DROP TABLE IF EXISTS base_workshop;"))
    conn.execute(text("DROP TABLE IF EXISTS base_defect_reason;"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
