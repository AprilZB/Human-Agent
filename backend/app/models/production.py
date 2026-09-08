from sqlalchemy import Column, Integer, String, TIMESTAMP, text, DATETIME, JSON, ForeignKey, DECIMAL, Enum
from app.core.database import Base

class BaseProcess(Base):
    __tablename__ = 'base_process'
    process_code = Column(String(50), primary_key=True)
    process_name = Column(String(100), nullable=False)
    required_skills = Column(JSON, nullable=False)
    standard_time_sec = Column(Integer)
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
