from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class SysRole(Base):
    __tablename__ = "sys_role"

    id          = Column(BigIntPK, primary_key=True, autoincrement=True)
    role_name   = Column(String(64), comment="角色名称")
    role_code   = Column(String(64), unique=True, comment="角色编码：ADMIN/EDITOR/VIEWER")
    description = Column(String(256), comment="角色描述")
    is_deleted  = Column(Integer, default=0)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())