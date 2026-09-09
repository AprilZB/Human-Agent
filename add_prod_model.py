with open('backend/app/models/production.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_model = '''
from sqlalchemy import DATE, Boolean

class BizEmployeeAttendance(Base):
    __tablename__ = 'biz_employee_attendance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    attendance_date = Column(DATE, nullable=False)
    employee_id = Column(String(50), nullable=False)
    shift_code = Column(String(50))
    is_holiday = Column(Boolean, default=False)
    actual_punch_in = Column(DATETIME)
    actual_punch_out = Column(DATETIME)
    attendance_status = Column(String(50))
    calculated_overtime = Column(DECIMAL(10, 2), default=0)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
'''

if 'BizEmployeeAttendance' not in code:
    code = code + "\n" + new_model
    with open('backend/app/models/production.py', 'w', encoding='utf-8') as f:
        f.write(code)
