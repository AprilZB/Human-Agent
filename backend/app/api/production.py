from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.production import BizProductionOrder
from app.schemas.production import ProductionOrderCreate, ProductionOrderResponse
from typing import List

router = APIRouter()

@router.post("/orders", response_model=ProductionOrderResponse)
def create_order(order: ProductionOrderCreate, db: Session = Depends(get_db)):
    db_order = BizProductionOrder(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/orders", response_model=List[ProductionOrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(BizProductionOrder).all()
