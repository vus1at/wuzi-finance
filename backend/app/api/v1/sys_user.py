from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sys_user import SysUser
from app.models.sys_role import SysRole
from app.models.sys_user_role import SysUserRole
from app.schemas.sys_user import UserCreate, UserUpdate, PasswordReset, SysUserOut, RoleOut
from app.core.security import hash_password
from app.api.deps import get_current_user

router = APIRouter(prefix="/sys-users", tags=["用户管理"])


def _build_out(db: Session, u: SysUser) -> SysUserOut:
    rows = (
        db.query(SysRole.id, SysRole.role_name)
        .join(SysUserRole, SysRole.id == SysUserRole.role_id)
        .filter(SysUserRole.user_id == u.id, SysUserRole.is_deleted == 0)
        .all()
    )
    return SysUserOut(
        id=u.id, username=u.username, real_name=u.real_name,
        phone=u.phone, status=u.status,
        role_ids=[r[0] for r in rows],
        role_names=[r[1] for r in rows],
        created_at=u.created_at,
    )


def _set_roles(db: Session, user_id: int, role_ids: list[int]):
    db.query(SysUserRole).filter(SysUserRole.user_id == user_id).delete()
    for rid in role_ids:
        db.add(SysUserRole(user_id=user_id, role_id=rid))
    db.flush()


# ---------- 角色列表下拉 ----------
@router.get("/roles", response_model=list[RoleOut])
def list_roles(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    return db.query(SysRole).filter(SysRole.is_deleted == 0).order_by(SysRole.id).all()


# ---------- 用户列表 ----------
@router.get("", response_model=list[SysUserOut])
def list_users(
    keyword: str = "",
    status_filter: int | None = None,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    q = db.query(SysUser).filter(SysUser.is_deleted == 0)
    if keyword:
        q = q.filter(
            (SysUser.username.contains(keyword)) | (SysUser.real_name.contains(keyword))
        )
    if status_filter is not None:
        q = q.filter(SysUser.status == status_filter)
    return [_build_out(db, u) for u in q.order_by(SysUser.id).all()]


# ---------- 新增 ----------
@router.post("", response_model=SysUserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    if db.query(SysUser).filter(SysUser.username == body.username).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "用户名已存在")
    u = SysUser(
        username=body.username,
        password=hash_password(body.password),
        real_name=body.real_name,
        phone=body.phone,
        status=body.status,
    )
    db.add(u)
    db.flush()
    _set_roles(db, u.id, body.role_ids)
    db.commit()
    db.refresh(u)
    return _build_out(db, u)


# ---------- 编辑 ----------
@router.put("/{uid}", response_model=SysUserOut)
def update_user(
    uid: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    u = db.get(SysUser, uid)
    if not u or u.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
     #不能禁用自己
    if uid == user.id and body.status == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "不能禁用当前登录账号")
    if body.real_name is not None:
        u.real_name = body.real_name
    if body.phone is not None:
        u.phone = body.phone
    if body.status is not None:
        u.status = body.status
    if body.role_ids is not None:
        _set_roles(db, uid, body.role_ids)
    db.commit()
    db.refresh(u)
    return _build_out(db, u)


# ---------- 删除（软删） ----------
@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    uid: int,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    u = db.get(SysUser, uid)
    if not u:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    if u.id == user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "不能删除自己")
    u.is_deleted = 1
    db.commit()


# ---------- 重置密码 ----------
@router.post("/{uid}/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    uid: int,
    body: PasswordReset,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    u = db.get(SysUser, uid)
    if not u:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    u.password = hash_password(body.new_password)
    db.commit()
    return {"ok": True, "message": "密码已重置"}