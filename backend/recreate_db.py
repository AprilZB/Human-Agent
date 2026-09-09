from app.core.database import engine, Base
from sqlalchemy import text
import app.models.master_data
import app.models.production
import app.models.system

with engine.begin() as conn:
    # Backup sys_config
    sys_configs = conn.execute(text("SELECT config_key, config_value, description FROM sys_config")).fetchall()
    
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
    tables = conn.execute(text("SHOW TABLES")).fetchall()
    for t in tables:
        conn.execute(text(f"DROP TABLE IF EXISTS {t[0]};"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

Base.metadata.create_all(bind=engine)

with engine.begin() as conn:
    # Restore sys_config
    for cfg in sys_configs:
        conn.execute(text("INSERT INTO sys_config (config_key, config_value, description) VALUES (:k, :v, :d)"), 
                     {"k": cfg[0], "v": cfg[1], "d": cfg[2]})
        
print("Database totally wiped and recreated successfully!")
