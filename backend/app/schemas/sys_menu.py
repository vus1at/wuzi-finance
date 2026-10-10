from datetime import datetime
from pydantic import BaseModel, Field


class MenuCreate(BaseModel):
    parent_id: int = 0
    menu_name: str = Field(..., min_length=1, max_length=64)
    menu_code: str = ""
    path: str = ""
    component: str = ""
    icon: str = ""
    menu_type: int = 1
    sort_order: int = 0
    status: int = 1


class MenuUpdate(BaseModel):
    parent_id: int | None = None
    menu_name: str | None = None
    menu_code: str | None = None
    path: str | None = None
    component: str | None = None
    icon: str | None = None
    menu_type: int | None = None
    sort_order: int | None = None
    status: int | None = None


class MenuOut(BaseModel):
    id: int
    parent_id: int
    menu_name: str
    menu_code: str | None = None
    path: str | None = None
    component: str | None = None
    icon: str | None = None
    menu_type: int
    sort_order: int
    status: int
    children: list["MenuOut"] = []

    class Config:
        from_attributes = True


MenuOut.model_rebuild()      # 处理自引用