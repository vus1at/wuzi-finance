from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=64)


class UserOut(BaseModel):
    id: int
    username: str
    real_name: str | None = None
    dept: str | None = None
    role: str
    data_scope: str

    class Config:
        from_attributes = True


class LoginOut(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UserOut