from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    short_name: str = ""
    category: str = "铁路"
    subsidiary_id: int | None = None
    address: str = ""
    status: int = 1


class ProjectUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    category: str | None = None
    subsidiary_id: int | None = None
    address: str | None = None
    status: int | None = None


class ProjectOut(BaseModel):
    id: int
    name: str
    short_name: str | None = None
    category: str | None = None
    subsidiary_id: int | None = None
    subsidiary_name: str | None = None   
    address: str | None = None
    status: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True