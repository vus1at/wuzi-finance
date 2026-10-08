from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class Project(Base):
    __tablename__ = "t_project"

    id          = Column(BigIntPK, primary_key=True, autoincrement=True)
    name        = Column(String(80), nullable=False, index=True, comment="项目名称")
    category    = Column(String(20), default="铁路", comment="项目类别")
    sub_company = Column(String(30), default="一处", comment="所属子分公司")
    addr        = Column(String(50), default="", comment="项目地址")
    status      = Column(String(10), default="启用", comment="启用/停用")
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())