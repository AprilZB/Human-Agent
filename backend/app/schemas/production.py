from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductionOrderCreate(BaseModel):
    order_code: str
    material_code: str
    target_quantity: int
    routing_code: Optional[str] = None
    plan_start_time: Optional[datetime] = None
    plan_end_time: Optional[datetime] = None

class ProductionOrderResponse(ProductionOrderCreate):
    status: str
    class Config:
        from_attributes = True
