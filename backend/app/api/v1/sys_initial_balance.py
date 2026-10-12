from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sys_initial_balance import SysInitialBalance
from app.schemas.sys_initial_balance import InitialBalanceUpdate, InitialBalanceOut
from app.api.deps import get_current_user
from app.models.sys_user import SysUser

router = APIRouter(prefix="/initial-balance", tags=["期初初始化"])


def _get_or_create(db: Session) -> SysInitialBalance:
    """获取唯一的一行；没有就创建空行"""
    row = db.query(SysInitialBalance).first()
    if not row:
        row = SysInitialBalance()
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@router.get("", response_model=InitialBalanceOut)
def get_initial_balance(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    return _get_or_create(db)


@router.put("", response_model=InitialBalanceOut)
def update_initial_balance(
    body: InitialBalanceUpdate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    row = _get_or_create(db)
    for k, v in body.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row