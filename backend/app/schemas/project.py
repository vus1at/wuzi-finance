from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    category: str = "铁路"
    sub_company: str = "一处"
    addr: str = ""
    status: str = "启用"


class ProjectUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    sub_company: str | None = None
    addr: str | None = None


class ProjectStatusUpdate(BaseModel):
    status: str = Field(..., description="启用/停用")


class ProjectOut(BaseModel):
    id: int
    name: str
    category: str | None = None
    sub_company: str | None = None
    addr: str | None = None
    status: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True