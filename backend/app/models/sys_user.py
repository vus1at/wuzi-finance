from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class SysUser(Base):
    __tablename__ = "sys_user"

    id         = Column(BigIntPK, primary_key=True, autoincrement=True)
    dep_id     = Column(BigInteger, nullable=True, comment="部门ID")
    username   = Column(String(64), nullable=False, unique=True, index=True, comment="用户名")
    password   = Column(String(128), nullable=False, comment="BCrypt 密码")
    real_name  = Column(String(64), comment="真实姓名")
    phone      = Column(String(20), comment="手机号")
    status     = Column(Integer, default=1, comment="1启用 0禁用")
    is_deleted = Column(Integer, default=0, comment="0正常 1删除")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())