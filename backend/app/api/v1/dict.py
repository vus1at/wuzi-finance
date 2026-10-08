from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dict_item import DictItem
from app.core.dicts import DICT_META, get_meta
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dicts", tags=["字典管理"])


class DictItemsUpdate(BaseModel):
    items: list[str]


@router.get("")
def list_dicts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """返回所有字典（元信息 + 数据库中的选项列表）"""
    result = []
    for meta in DICT_META:
        rows = (
            db.query(DictItem)
            .filter(DictItem.dict_key == meta["key"])
            .order_by(DictItem.sort_order, DictItem.id)
            .all()
        )
        result.append({
            "key": meta["key"],
            "label": meta["label"],
            "group": meta["group"],
            "desc": meta["desc"],
            "items": [r.dict_value for r in rows],
        })
    return result


@router.get("/{key}")
def get_dict(
    key: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """返回单个字典"""
    meta = get_meta(key)
    if not meta:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "字典不存在")
    rows = (
        db.query(DictItem)
        .filter(DictItem.dict_key == key)
        .order_by(DictItem.sort_order, DictItem.id)
        .all()
    )
    return {
        "key": meta["key"],
        "label": meta["label"],
        "group": meta["group"],
        "desc": meta["desc"],
        "items": [r.dict_value for r in rows],
    }


@router.put("/{key}")
def update_dict(
    key: str,
    body: DictItemsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新整个字典的选项列表（先删后插）"""
    meta = get_meta(key)
    if not meta:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "字典不存在")
    if not body.items:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "字典至少保留 1 项")

    # 去重 + 去空
    seen = set()
    cleaned = []
    for v in body.items:
        v = (v or "").strip()
        if v and v not in seen:
            seen.add(v)
            cleaned.append(v)
    if not cleaned:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "字典至少保留 1 项有效值")

    # 先删后插
    db.query(DictItem).filter(DictItem.dict_key == key).delete()
    for i, v in enumerate(cleaned):
        db.add(DictItem(dict_key=key, dict_value=v, sort_order=i))
    db.commit()

    return {
        "key": key,
        "label": meta["label"],
        "items": cleaned,
    }