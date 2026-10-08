from sqlalchemy import Column, BigInteger, Integer, String, Numeric, DateTime, func

from app.db.session import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class Ledger(Base):
    """台账表，看板用的核心15列"""
    __tablename__ = "t_ledger"

    id                  = Column(BigIntPK, primary_key=True, autoincrement=True)
    project_name        = Column(String(80), nullable=False, index=True, comment="项目名称")
    supplier_name       = Column(String(120), nullable=False, index=True, comment="供应商名称")
    material_type       = Column(String(30), default="", comment="物资种类")
    month_purchase_amt  = Column(Numeric(18, 4), default=0, comment="本月采购金额(万)")
    month_supply_amt    = Column(Numeric(18, 4), default=0, comment="本月供应金额(万)")
    month_profit        = Column(Numeric(18, 4), default=0, comment="利润/管理费(万)")
    month_pay           = Column(Numeric(18, 4), default=0, comment="本月实际支付(万)")
    month_receive       = Column(Numeric(18, 4), default=0, comment="本月实际回款(万)")
    total_debt          = Column(Numeric(18, 4), default=0, comment="总债务余额(万)")
    overdue_debt        = Column(Numeric(18, 4), default=0, comment="逾期债务(万)")
    max_overdue_days    = Column(Integer, default=0, comment="最长逾期天数")
    receivable          = Column(Numeric(18, 4), default=0, comment="应收债权(万)")
    overdue_receivable  = Column(Numeric(18, 4), default=0, comment="逾期债权(万)")
    debt_level          = Column(String(20), default="低风险", comment="债务分级")
    created_at          = Column(DateTime, server_default=func.now())