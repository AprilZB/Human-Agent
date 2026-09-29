with open('backend/app/models/master_data.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_bom = '''class BaseBom(Base):
    __tablename__ = 'base_bom'
    bom_code = Column(String(50), primary_key=True)
    product_code = Column(String(50), ForeignKey('base_material.material_code'))
    component_code = Column(String(50), ForeignKey('base_material.material_code'))
    quantity = Column(Numeric(10, 2), nullable=False)
    alt_group = Column(String(50)) # 替代物料同行?替代?    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))'''

# Fallback regex if exact match fails
import re
new_bom = '''class BaseBom(Base):
    __tablename__ = 'base_bom'
    bom_code = Column(String(50), primary_key=True)
    product_code = Column(String(50), ForeignKey('base_material.material_code'), primary_key=True)
    component_code = Column(String(50), ForeignKey('base_material.material_code'), primary_key=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    alt_group = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))'''

code = re.sub(r'class BaseBom\(Base\):.*?created_at = Column\(TIMESTAMP, server_default=text\("CURRENT_TIMESTAMP"\)\)', new_bom, code, flags=re.DOTALL)

with open('backend/app/models/master_data.py', 'w', encoding='utf-8') as f:
    f.write(code)
