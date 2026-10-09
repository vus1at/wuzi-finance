from sqlalchemy import Column, BigInteger, Integer, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class SysUserRole(Base):
    __tablename__ = "sys_user_role"

    id         = Column(BigIntPK, primary_key=True, autoincrement=True)
    user_id    = Column(BigInteger, comment="用户ID")
    role_id    = Column(BigInteger, comment="角色ID")
    is_deleted = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())