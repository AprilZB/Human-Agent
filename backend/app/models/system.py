from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from app.core.database import Base

class SysConfig(Base):
    __tablename__ = "sys_config"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(String(500), nullable=False)
    description = Column(String(255))
