from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sys_menu import SysMenu
from app.schemas.sys_menu import MenuCreate, MenuUpdate, MenuOut
from app.api.deps import get_current_user
from app.models.sys_user import SysUser
from app.models.sys_role import SysRole
from app.models.sys_role_menu import SysRoleMenu
from app.models.sys_user_role import SysUserRole

router = APIRouter(prefix="/menus", tags=["菜单管理"])


def _build_tree(rows: list[SysMenu], parent_id: int = 0) -> list[MenuOut]:
    """递归构建菜单树"""
    result = []
    for r in rows:
        if r.parent_id != parent_id:
            continue
        node = MenuOut(
            id=r.id,
            parent_id=r.parent_id,
            menu_name=r.menu_name,
            menu_code=r.menu_code,
            path=r.path,
            component=r.component,
            icon=r.icon,
            menu_type=r.menu_type,
            sort_order=r.sort_order,
            status=r.status,
        )
        node.children = _build_tree(rows, r.id)
        result.append(node)
    return result


@router.get("/tree", response_model=list[MenuOut])
def get_menu_tree(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    """菜单树（用于侧边栏 + 菜单管理页）"""
    rows = (
        db.query(SysMenu)
        .filter(SysMenu.is_deleted == 0)
        .order_by(SysMenu.sort_order, SysMenu.id)
        .all()
    )
    return _build_tree(rows, 0)

@router.get("/me", response_model=list[MenuOut])
def get_my_menu_tree(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    """当前登录用户的菜单树（按角色权限过滤）"""
    # 1. 拿用户所有角色
    role_ids = [
        r[0] for r in
        db.query(SysUserRole.role_id).filter(
            SysUserRole.user_id == user.id,
            SysUserRole.is_deleted == 0,
        ).all()
    ]

    # 2. 判断是否有 ADMIN 角色
    is_admin = False
    if role_ids:
        is_admin = (
            db.query(SysRole).filter(
                SysRole.id.in_(role_ids),
                SysRole.role_code == "ADMIN",
                SysRole.is_deleted == 0,
            ).first()
            is not None
        )

    if is_admin:
        # 管理员：全部启用菜单
        rows = (
            db.query(SysMenu)
            .filter(SysMenu.is_deleted == 0, SysMenu.status == 1)
            .order_by(SysMenu.sort_order, SysMenu.id)
            .all()
        )
    else:
        # 普通用户：按角色-菜单关联
        if not role_ids:
            return []
        menu_ids = [
            x[0] for x in
            db.query(SysRoleMenu.menu_id).filter(
                SysRoleMenu.role_id.in_(role_ids),
                SysRoleMenu.is_deleted == 0,
            ).distinct().all()
        ]
        if not menu_ids:
            return []
        rows = (
            db.query(SysMenu)
            .filter(
                SysMenu.id.in_(menu_ids),
                SysMenu.is_deleted == 0,
                SysMenu.status == 1,
            )
            .order_by(SysMenu.sort_order, SysMenu.id)
            .all()
        )

    return _build_tree(rows, 0)

@router.get("", response_model=list[MenuOut])
def list_menus(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    """扁平列表"""
    rows = (
        db.query(SysMenu)
        .filter(SysMenu.is_deleted == 0)
        .order_by(SysMenu.sort_order, SysMenu.id)
        .all()
    )
    return [MenuOut.model_validate(r) for r in rows]


@router.post("", response_model=MenuOut, status_code=status.HTTP_201_CREATED)
def create_menu(
    body: MenuCreate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    m = SysMenu(**body.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return MenuOut.model_validate(m)


@router.put("/{mid}", response_model=MenuOut)
def update_menu(
    mid: int,
    body: MenuUpdate,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    m = db.get(SysMenu, mid)
    if not m or m.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "菜单不存在")

    data = body.model_dump(exclude_none=True)
    #不能把自己设为自己的父级
    if data.get("parent_id") == mid:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "父菜单不能是自己")
    for k, v in data.items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return MenuOut.model_validate(m)


@router.delete("/{mid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(
    mid: int,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    m = db.get(SysMenu, mid)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "菜单不存在")
    #有子菜单不让删
    has_child = db.query(SysMenu).filter(
        SysMenu.parent_id == mid, SysMenu.is_deleted == 0
    ).first()
    if has_child:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请先删除子菜单")
    m.is_deleted = 1
    db.commit()