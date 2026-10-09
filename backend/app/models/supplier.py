from sqlalchemy import Column, BigInteger, Integer, String, Text, Numeric, Date, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class Supplier(Base):
    __tablename__ = "supplier"

    id               = Column(BigIntPK, primary_key=True, autoincrement=True)
    name             = Column(String(128), comment="名称")
    type             = Column(Integer, default=1, comment="0非厂商 1厂商")
    contact_name     = Column(String(20), comment="联系人")
    contact_mobile   = Column(String(20), comment="联系方式")
    company_address  = Column(String(256), comment="企业地址")
    business_scope   = Column(Text, comment="经营范围")
    amount           = Column(Numeric(18, 8), comment="注册资本")
    established_date = Column(Date, comment="成立时间")
    status           = Column(String(64), comment="状态")
    is_deleted       = Column(Integer, default=0)
    created_at       = Column(DateTime, server_default=func.now())
    updated_at       = Column(DateTime, server_default=func.now(), onupdate=func.now())