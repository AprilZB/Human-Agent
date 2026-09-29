import sys
sys.path.append('backend')
from app.core.database import SessionLocal
from app.models.master_data import BaseEmployee
import pandas as pd

db = SessionLocal()
ts = pd.Timestamp('2027-09-20 00:00:00')
emp = BaseEmployee(employee_id='TEST_123', name='Test', health_cert_status=ts)
try:
    db.merge(emp)
    db.commit()
    print("Success")
except Exception as e:
    print("Failed:", e)
finally:
    db.close()
