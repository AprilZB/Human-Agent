from sqlalchemy import Column, Integer, String, TIMESTAMP, text, DATETIME, JSON, ForeignKey, DECIMAL, Enum, Boolean

with open('backend/app/models/system.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_model = '''
from sqlalchemy import DECIMAL, Boolean, Time

class SysAttendanceRule(Base):
    __tablename__ = 'sys_attendance_rule'
    shift_code = Column(String(50), primary_key=True)
    shift_name = Column(String(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_cross_day = Column(Boolean, default=False)
    meal_break_hours = Column(DECIMAL(10, 2), default=1.25)
    standard_work_hours = Column(DECIMAL(10, 2), default=8.0)
    is_overtime_counted = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
'''

if 'SysAttendanceRule' not in code:
    code = code + "\n" + new_model
    with open('backend/app/models/system.py', 'w', encoding='utf-8') as f:
        f.write(code)
