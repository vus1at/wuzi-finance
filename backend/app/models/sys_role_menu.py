from sqlalchemy import Column, BigInteger, Integer, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class SysRoleMenu(Base):
    __tablename__ = "sys_role_menu"

    id         = Column(BigIntPK, primary_key=True, autoincrement=True)
    role_id    = Column(BigInteger, comment="角色ID")
    menu_id    = Column(BigInteger, comment="菜单ID")
    is_deleted = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())