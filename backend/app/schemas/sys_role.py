from datetime import datetime
from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    role_name: str = Field(..., min_length=1, max_length=64)
    role_code: str = Field(..., min_length=1, max_length=64)
    description: str = ""


class RoleUpdate(BaseModel):
    role_name: str | None = None
    role_code: str | None = None
    description: str | None = None


class RoleOut(BaseModel):
    id: int
    role_name: str
    role_code: str
    description: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class RoleMenusUpdate(BaseModel):
    menu_ids: list[int] = []