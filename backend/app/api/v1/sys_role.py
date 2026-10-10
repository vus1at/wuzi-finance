from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sys_role import SysRole
from app.models.sys_role_menu import SysRoleMenu
from app.models.sys_user_role import SysUserRole
from app.schemas.sys_role import RoleCreate, RoleUpdate, RoleOut, RoleMenusUpdate
from app.api.deps import get_current_user
from app.models.sys_user import SysUser

router = APIRouter(prefix="/sys-roles", tags=["角色管理"])

# ⭐ 内置角色白名单：不允许改 role_code，不允许删除
BUILTIN_ROLE_CODES = {"ADMIN", "EDITOR", "VIEWER"}


@router.get("", response_model=list[RoleOut])
def list_roles(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    return (
        db.query(SysRole)
        .filter(SysRole.is_deleted == 0)
        .order_by(SysRole.id)
        .all()
    )


@router.post("", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    body: RoleCreate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    if db.query(SysRole).filter(SysRole.role_code == body.role_code, SysRole.is_deleted == 0).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "角色编码已存在")
    r = SysRole(**body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/{rid}", response_model=RoleOut)
def update_role(
    rid: int,
    body: RoleUpdate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    r = db.get(SysRole, rid)
    if not r or r.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "角色不存在")

    # ⭐ 内置角色不允许改 role_code
    if r.role_code in BUILTIN_ROLE_CODES:
        if body.role_code and body.role_code != r.role_code:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"内置角色（{r.role_code}）的角色编码不允许修改",
            )

    data = body.model_dump(exclude_none=True)
    if "role_code" in data:
        exists = (
            db.query(SysRole)
            .filter(
                SysRole.role_code == data["role_code"],
                SysRole.id != rid,
                SysRole.is_deleted == 0,
            )
            .first()
        )
        if exists:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "角色编码已存在")

    for k, v in data.items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    rid: int,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    r = db.get(SysRole, rid)
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "角色不存在")

    # ⭐ 内置角色不允许删除
    if r.role_code in BUILTIN_ROLE_CODES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"内置角色（{r.role_code}）不允许删除",
        )

    # 有用户绑定也不让删
    binding = (
        db.query(SysUserRole)
        .filter(SysUserRole.role_id == rid, SysUserRole.is_deleted == 0)
        .first()
    )
    if binding:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "该角色已分配给用户，无法删除")

    r.is_deleted = 1
    db.commit()


# ---------- 角色-菜单关联 ----------

@router.get("/{rid}/menus")
def get_role_menus(
    rid: int,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    """查询角色已分配的菜单 ID 列表"""
    r = db.get(SysRole, rid)
    if not r or r.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "角色不存在")
    rows = (
        db.query(SysRoleMenu.menu_id)
        .filter(SysRoleMenu.role_id == rid, SysRoleMenu.is_deleted == 0)
        .all()
    )
    return {"menu_ids": [x[0] for x in rows]}


@router.put("/{rid}/menus")
def set_role_menus(
    rid: int,
    body: RoleMenusUpdate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    """保存角色的菜单权限（先删后插）"""
    r = db.get(SysRole, rid)
    if not r or r.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "角色不存在")

    menu_ids = list(set(body.menu_ids))

    db.query(SysRoleMenu).filter(SysRoleMenu.role_id == rid).delete()
    for mid in menu_ids:
        db.add(SysRoleMenu(role_id=rid, menu_id=mid))
    db.commit()
    return {"ok": True, "count": len(menu_ids)}