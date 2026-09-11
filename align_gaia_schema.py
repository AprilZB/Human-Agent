with open('backend/app/models/production.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re

old_model = '''class BizEmployeeAttendance(Base):
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
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))'''

new_model = '''class BizEmployeeAttendance(Base):
    __tablename__ = 'biz_employee_attendance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    attendance_date = Column(DATE, nullable=False) # 工作日期
    employee_id = Column(String(50), nullable=False) # 工号
    shift_code = Column(String(50)) # 排班
    is_holiday = Column(Boolean, default=False)
    actual_punch_in = Column(DATETIME) # 签到时间
    actual_punch_out = Column(DATETIME) # 签退时间
    actual_work_hours = Column(DECIMAL(10, 2), default=0) # 实际工时 (盖雅)
    calculated_overtime = Column(DECIMAL(10, 2), default=0) # 核算加班工时
    attendance_type = Column(String(50)) # 出勤类型 (如：正常/请假/外出/出差)
    attendance_status = Column(String(50)) # 状态
    sync_time = Column(DATETIME) # 同步时间
    external_source = Column(String(50), default='GaiaWorks') # 数据来源
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))'''

code = code.replace(old_model, new_model)

with open('backend/app/models/production.py', 'w', encoding='utf-8') as f:
    f.write(code)
