from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.production import BizProductionOrder
from app.schemas.production import ProductionOrderCreate, ProductionOrderResponse
from app.services.dispatch_service import decompose_production_order
from app.services.match_service import run_intelligent_matching
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

@router.post("/orders/{order_code}/decompose")
def decompose_order(order_code: str, db: Session = Depends(get_db)):
    try:
        work_orders = decompose_production_order(db, order_code)
        return {"message": "Decomposed successfully", "count": len(work_orders)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/work-orders/{wo_code}/match")
async def intelligent_match(wo_code: str, db: Session = Depends(get_db)):
    try:
        assignments = await run_intelligent_matching(db, wo_code)
        return {"message": "Intelligent matching completed", "matched_count": len(assignments)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
