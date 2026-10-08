from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class DictItem(Base):
    """字典选项值,12 个字典共用一张表,用dict_key 区分"""
    __tablename__ = "t_dict_item"

    id         = Column(BigIntPK, primary_key=True, autoincrement=True)
    dict_key   = Column(String(30), nullable=False, index=True, comment="字典标识")
    dict_value = Column(String(100), nullable=False, comment="选项值")
    sort_order = Column(Integer, default=0, comment="排序号")
    created_at = Column(DateTime, server_default=func.now())