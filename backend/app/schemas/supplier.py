from datetime import datetime
from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    type: str = "厂商"
    contact: str = ""
    phone: str = ""
    addr: str = ""
    scope: str = ""
    capital: str = ""
    founded: str = ""


class SupplierUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    contact: str | None = None
    phone: str | None = None
    addr: str | None = None
    scope: str | None = None
    capital: str | None = None
    founded: str | None = None


class SupplierOut(BaseModel):
    id: int
    name: str
    type: str | None = None
    contact: str | None = None
    phone: str | None = None
    addr: str | None = None
    scope: str | None = None
    capital: str | None = None
    founded: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True