from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class User(Base):
    __tablename__ = "t_user"

    id         = Column(BigIntPK, primary_key=True, autoincrement=True)
    username   = Column(String(50), unique=True, nullable=False, index=True)
    password   = Column(String(120), nullable=False)
    real_name  = Column(String(50))
    dept       = Column(String(50))
    role       = Column(String(20), default="viewer")
    data_scope = Column(String(30), default="all")
    status     = Column(String(10), default="enabled")
    created_at = Column(DateTime, server_default=func.now())