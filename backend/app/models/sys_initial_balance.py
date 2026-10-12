from sqlalchemy import Column, BigInteger, Integer, Numeric, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class SysInitialBalance(Base):
    """期初数据（整表只存一行，id=1）"""
    __tablename__ = "sys_initial_balance"

    id = Column(BigIntPK, primary_key=True, autoincrement=True)

    # ---------- 年累（截至上月底） ----------
    ytd_purchase_amount = Column(Numeric(18, 4), default=0, comment="年累采购金额(万)")
    ytd_supply_amount   = Column(Numeric(18, 4), default=0, comment="年累供应金额(万)")
    ytd_payment_amount  = Column(Numeric(18, 4), default=0, comment="年累支付金额(万)")
    ytd_receipt_amount  = Column(Numeric(18, 4), default=0, comment="年累回款金额(万)")
    ytd_profit_amount   = Column(Numeric(18, 4), default=0, comment="年累利润(万)")
    ytd_supply_quantity = Column(Numeric(18, 2), default=0, comment="年累供应数量")

    # ---------- 开累（全部历史） ----------
    cum_purchase_amount = Column(Numeric(18, 4), default=0, comment="开累采购金额(万)")
    cum_supply_amount   = Column(Numeric(18, 4), default=0, comment="开累供应金额(万)")
    cum_payment_amount  = Column(Numeric(18, 4), default=0, comment="开累付款金额(万)")
    cum_receipt_amount  = Column(Numeric(18, 4), default=0, comment="开累回款金额(万)")
    cum_payment_ratio   = Column(Numeric(10, 4), default=0, comment="开累付款比例(%)")
    cum_receipt_ratio   = Column(Numeric(10, 4), default=0, comment="开累回款比例(%)")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())