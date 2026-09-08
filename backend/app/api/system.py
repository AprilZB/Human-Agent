from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.system import SysConfig
from app.schemas.system import SysConfigResponse
from typing import List

router = APIRouter()

@router.get("/configs", response_model=List[SysConfigResponse])
def get_configs(db: Session = Depends(get_db)):
    return db.query(SysConfig).all()
