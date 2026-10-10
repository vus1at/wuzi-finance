from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class SysMenu(Base):
    __tablename__ = "sys_menu"

    id         = Column(BigIntPK, primary_key=True, autoincrement=True)
    parent_id  = Column(BigInteger, default=0, comment="父菜单ID，0为顶级")
    menu_name  = Column(String(64), comment="菜单名称")
    menu_code  = Column(String(128), comment="菜单编码（权限标识）")
    path       = Column(String(256), comment="前端路由路径")
    component  = Column(String(256), comment="前端组件路径")
    icon       = Column(String(64), comment="菜单图标")
    menu_type  = Column(Integer, default=1, comment="1一级可点击 2一级目录 3二级页面 4按钮")
    sort_order = Column(Integer, default=0)
    status     = Column(Integer, default=1, comment="1启用 0禁用")
    is_deleted = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())