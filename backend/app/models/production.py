from sqlalchemy import Column, Integer, String, TIMESTAMP, text, DATETIME, JSON, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class BaseProcess(Base):
    __tablename__ = 'base_process'
    process_code = Column(String(50), primary_key=True)
    process_name = Column(String(100), nullable=False)
    required_skills = Column(JSON, nullable=False)
    standard_time_sec = Column(Integer)
    bound_bom_code = Column(String(50)) # 绑定的BOM编码
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BizProductionOrder(Base):
    __tablename__ = 'biz_production_order'
    order_code = Column(String(50), primary_key=True)
    material_code = Column(String(50), nullable=False)
    routing_code = Column(String(50))
    target_quantity = Column(Integer, nullable=False)
    plan_start_time = Column(DATETIME)
    plan_end_time = Column(DATETIME)
    status = Column(String(20), default='RELEASED')
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BizWorkOrder(Base):
    __tablename__ = 'biz_work_order'
    work_order_code = Column(String(50), primary_key=True)
    order_code = Column(String(50), ForeignKey('biz_production_order.order_code'))
    process_code = Column(String(50), ForeignKey('base_process.process_code'))
    team_code = Column(String(50))
    required_count = Column(Integer, default=1)
    status = Column(String(20), default='PENDING')
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    process = relationship("BaseProcess")

class TaskPersonnelAssignment(Base):
    __tablename__ = 'task_personnel_assignment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_order_code = Column(String(50), ForeignKey('biz_work_order.work_order_code'))
    employee_id = Column(String(50), nullable=False)
    recommend_reason = Column(String(1000))
    status = Column(String(20), default='AI_RECOMMENDED')
    confirmed_by = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BizProductionConfirmation(Base):
    __tablename__ = 'biz_production_confirmation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_code = Column(String(50), nullable=False)
    material_code = Column(String(50), nullable=False)
    work_center_code = Column(String(50))
    batch_no = Column(String(50))
    yield_quantity = Column(DECIMAL(10, 2), default=0)
    scrap_quantity = Column(DECIMAL(10, 2), default=0)
    confirmation_no = Column(String(50))
    plant = Column(String(50))
    exec_datetime = Column(DATETIME)
    cancel_flag = Column(Enum('Y', 'N'), default='N')
    reversed_flag = Column(Enum('Y', 'N'), default='N')
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))



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


class BizEmployeeDailyGrade(Base):
    __tablename__ = 'biz_employee_daily_grade'
    id = Column(Integer, primary_key=True, autoincrement=True)
    grade_date = Column(DATE, nullable=False)
    employee_id = Column(String(50), nullable=False)
    score = Column(Integer, default=0) # -4, -2, 0, 2, 4
    remark = Column(String(255))
    graded_by = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
