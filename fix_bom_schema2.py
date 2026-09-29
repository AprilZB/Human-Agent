import sys
sys.path.append('backend')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.execute(text("DROP TABLE IF EXISTS base_bom"))
db.execute(text('''
CREATE TABLE base_bom (
  bom_code varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  product_code varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  component_code varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  quantity decimal(10,2) NOT NULL,
  alt_group varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (bom_code, product_code, component_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
'''))
db.commit()
print("Success")
