from sqlalchemy import text
from app.core.database import engine

with engine.begin() as conn:
    conn.execute(text("ALTER TABLE base_bom DROP COLUMN operation_code;"))
    conn.execute(text("ALTER TABLE base_process ADD COLUMN bound_bom_code VARCHAR(50);"))
