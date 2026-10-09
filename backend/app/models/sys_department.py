from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class SysDepartment(Base):
    __tablename__ = "sys_department"

    id         = Column(BigIntPK, primary_key=True, autoincrement=True)
    name       = Column(String(64), comment="部门名称")
    parent_id  = Column(BigInteger, default=0, comment="父级ID")
    code       = Column(String(64), comment="部门编码")
    sort_order = Column(Integer, default=0)
    level      = Column(Integer, default=1)
    path       = Column(String(256))
    status     = Column(Integer, default=1)
    is_deleted = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())