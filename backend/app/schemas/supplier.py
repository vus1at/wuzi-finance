from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    type: int = 1
    contact_name: str = ""
    contact_mobile: str = ""
    company_address: str = ""
    business_scope: str = ""
    amount: float | None = None
    established_date: date | None = None


class SupplierUpdate(BaseModel):
    name: str | None = None
    type: int | None = None
    contact_name: str | None = None
    contact_mobile: str | None = None
    company_address: str | None = None
    business_scope: str | None = None
    amount: float | None = None
    established_date: date | None = None


class SupplierOut(BaseModel):
    id: int
    name: str
    type: int | None = None
    contact_name: str | None = None
    contact_mobile: str | None = None
    company_address: str | None = None
    business_scope: str | None = None
    amount: float | None = None
    established_date: date | None = None
    status: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True