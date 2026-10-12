from datetime import datetime
from pydantic import BaseModel


class InitialBalanceUpdate(BaseModel):
    ytd_purchase_amount: float = 0
    ytd_supply_amount:   float = 0
    ytd_payment_amount:  float = 0
    ytd_receipt_amount:  float = 0
    ytd_profit_amount:   float = 0
    ytd_supply_quantity: float = 0

    cum_purchase_amount: float = 0
    cum_supply_amount:   float = 0
    cum_payment_amount:  float = 0
    cum_receipt_amount:  float = 0
    cum_payment_ratio:   float = 0
    cum_receipt_ratio:   float = 0


class InitialBalanceOut(InitialBalanceUpdate):
    id: int
    updated_at: datetime | None = None

    class Config:
        from_attributes = True