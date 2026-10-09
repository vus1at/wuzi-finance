from datetime import datetime
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=64)
    real_name: str = ""
    phone: str = ""
    status: int = 1
    role_ids: list[int] = []


class UserUpdate(BaseModel):
    real_name: str | None = None
    phone: str | None = None
    status: int | None = None
    role_ids: list[int] | None = None


class PasswordReset(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=64)


class SysUserOut(BaseModel):
    id: int
    username: str
    real_name: str | None = None
    phone: str | None = None
    status: int
    role_ids: list[int] = []
    role_names: list[str] = []
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class RoleOut(BaseModel):
    id: int
    role_name: str
    role_code: str
    description: str | None = None

    class Config:
        from_attributes = True