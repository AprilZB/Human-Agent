import sys
sys.path.append('.')
from app.core.database import SessionLocal
import app.models.master_data as md
import app.models.production as prod

TAB_MODEL_MAP = {
    "materials": md.BaseMaterial,
    "production-orders": prod.BizProductionOrder,
    "employees": md.BaseEmployee,
    "workshops": md.BaseWorkshop,
    "defect-reasons": md.BaseDefectReason,
    "material-groups": md.BaseMaterialGroup,
    "routings": md.BaseRouting,
    "processes": prod.BaseProcess,
    "boms": md.BaseBom,
    "confirmations": prod.BizProductionConfirmation,
    "attendances": prod.BizEmployeeAttendance
}

all_cols = set()
for model in TAB_MODEL_MAP.values():
    for c in model.__table__.columns:
        all_cols.add(c.name)

for c in sorted(list(all_cols)):
    print(c)
