from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class Supplier(Base):
    __tablename__ = "t_supplier"

    id         = Column(BigIntPK, primary_key=True, autoincrement=True)
    name       = Column(String(120), nullable=False, index=True, comment="供应商名称")
    type       = Column(String(10), default="厂商", comment="厂商/非厂商")
    contact    = Column(String(50), default="", comment="联系人")
    phone      = Column(String(30), default="", comment="联系方式")
    addr       = Column(String(200), default="", comment="企业地址")
    scope      = Column(String(200), default="", comment="经营范围")
    capital    = Column(String(30), default="", comment="注册资本")
    founded    = Column(String(20), default="", comment="成立时间")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())