from sqlalchemy import Column, Integer, String, TIMESTAMP, text, JSON, Boolean, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

# ================= APHR 主数据 =================
class BaseEmployee(Base):
    __tablename__ = 'base_employee'
    employee_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    workshop_code = Column(String(50))
    health_cert_status = Column(String(100)) # 记录状态和有效期
    work_cert_status = Column(String(100))   # 记录状态和有效期
    skills = Column(JSON)                    # 技能矩阵
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BaseWorkshop(Base):
    __tablename__ = 'base_workshop'
    workshop_code = Column(String(50), primary_key=True)
    workshop_name = Column(String(100), nullable=False)
    sap_work_center_code = Column(String(200)) # 允许一个车间对应多个工作中心，可逗号分隔
    manager_id = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BaseTeam(Base):
    __tablename__ = 'base_team'
    team_code = Column(String(50), primary_key=True)
    team_name = Column(String(100), nullable=False)
    workshop_code = Column(String(50), ForeignKey('base_workshop.workshop_code'))
    leader_id = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


# ================= SAP 主数据 =================

class BaseMaterialGroup(Base):
    __tablename__ = 'base_material_group'
    group_code = Column(String(50), primary_key=True)
    sap_group_code = Column(String(50))
    group_name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BaseMaterial(Base):
    __tablename__ = 'base_material'
    material_code = Column(String(50), primary_key=True) # 物料编码
    material_desc = Column(String(255), nullable=False)  # 物料描述
    material_group_code = Column(String(50), ForeignKey('base_material_group.group_code')) # 物料组
    
    plant_status = Column(String(50))                    # 特定工厂状态
    base_uom = Column(String(20), default='PCS')         # 基本计量单位
    valid_from = Column(Date)                            # 有效起始期
    max_storage_period = Column(Integer)                 # 最大存储期间
    time_unit = Column(String(20))                       # 时间单位
    min_shelf_life = Column(Integer)                     # 最小剩余货架寿命
    total_shelf_life = Column(Integer)                   # 总货架寿命
    inspection_required = Column(Boolean, default=False) # 是否需要检验
    safety_stock = Column(Numeric(10, 2))                # 安全库存
    default_storage_loc = Column(String(50))             # 库存默认地点

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BaseDefectReason(Base):
    __tablename__ = 'base_defect_reason'
    defect_code = Column(String(50), primary_key=True)
    sap_defect_code = Column(String(50))
    defect_name = Column(String(100), nullable=False)
    description = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class BaseRouting(Base):
    __tablename__ = 'base_routing'
    routing_code = Column(String(50), primary_key=True)
    sap_routing_code = Column(String(50))
    routing_name = Column(String(150))
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
    sap_operation_code = Column(String(50))

class BaseBom(Base):
    __tablename__ = 'base_bom'
    bom_code = Column(String(50), primary_key=True)
    product_code = Column(String(50), ForeignKey('base_material.material_code'))
    component_code = Column(String(50), ForeignKey('base_material.material_code'))
    quantity = Column(Numeric(10, 2), nullable=False)
    alt_group = Column(String(50)) # 替代物料同行号/替代组
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

