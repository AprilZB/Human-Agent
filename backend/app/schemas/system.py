from pydantic import BaseModel
from typing import Optional

class SysConfigBase(BaseModel):
    config_key: str
    config_value: str
    description: Optional[str] = None

class SysConfigResponse(SysConfigBase):
    id: int

    class Config:
        from_attributes = True
