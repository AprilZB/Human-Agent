from sqlalchemy import Column, Integer, String, TIMESTAMP, text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class BaseWorkshop(Base):
    __tablename__ = 'base_workshop'
    workshop_code = Column(String(50), primary_key=True)
    workshop_name = Column(String(100), nullable=False)
    manager_id = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BaseTeam(Base):
    __tablename__ = 'base_team'
    team_code = Column(String(50), primary_key=True)
    team_name = Column(String(100), nullable=False)
    workshop_code = Column(String(50), ForeignKey('base_workshop.workshop_code'))
    leader_id = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BaseMaterial(Base):
    __tablename__ = 'base_material'
    material_code = Column(String(50), primary_key=True)
    material_name = Column(String(150), nullable=False)
    material_type = Column(String(20), nullable=False)
    unit = Column(String(20), default='PCS')
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BaseRouting(Base):
    __tablename__ = 'base_routing'
    routing_code = Column(String(50), primary_key=True)
    material_code = Column(String(50), ForeignKey('base_material.material_code'))
    version = Column(String(20), default='V1.0')
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    
    details = relationship("BaseRoutingDetail", backref="routing")

class BaseRoutingDetail(Base):
    __tablename__ = 'base_routing_detail'
    id = Column(Integer, primary_key=True, autoincrement=True)
    routing_code = Column(String(50), ForeignKey('base_routing.routing_code'))
    step_seq = Column(Integer, nullable=False)
    process_code = Column(String(50), ForeignKey('base_process.process_code'))
