from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class Project(Base):
    __tablename__ = "project"

    id            = Column(BigIntPK, primary_key=True, autoincrement=True)
    name          = Column(String(64), comment="名称")
    short_name    = Column(String(64), comment="简称")
    category      = Column(String(64), comment="类别")
    subsidiary_id = Column(BigInteger, comment="子分公司ID（关联 sys_department）")
    address       = Column(String(256), comment="地址")
    status        = Column(Integer, default=1, comment="1启用 0停用")
    is_deleted    = Column(Integer, default=0)
    created_at    = Column(DateTime, server_default=func.now())
    updated_at    = Column(DateTime, server_default=func.now(), onupdate=func.now())