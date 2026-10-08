from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierOut
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/suppliers", tags=["供应商管理"])


@router.get("", response_model=list[SupplierOut])
def list_suppliers(
    keyword: str = "",
    type_filter: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Supplier)
    if keyword:
        q = q.filter(Supplier.name.contains(keyword))
    if type_filter:
        q = q.filter(Supplier.type == type_filter)
    return q.order_by(Supplier.id).all()


@router.post("", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(
    body: SupplierCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if db.query(Supplier).filter(Supplier.name == body.name).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "供应商名称已存在")
    s = Supplier(**body.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.put("/{sid}", response_model=SupplierOut)
def update_supplier(
    sid: int,
    body: SupplierUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = db.get(Supplier, sid)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "供应商不存在")
    data = body.model_dump(exclude_none=True)
    if "name" in data:
        exists = db.query(Supplier).filter(
            Supplier.name == data["name"], Supplier.id != sid
        ).first()
        if exists:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "供应商名称已存在")
    for k, v in data.items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{sid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(
    sid: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = db.get(Supplier, sid)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "供应商不存在")
    db.delete(s)
    db.commit()