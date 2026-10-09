from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sys_user import SysUser
from app.models.sys_role import SysRole
from app.models.sys_user_role import SysUserRole
from app.schemas.user import LoginIn, LoginOut, UserOut
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


def _get_user_roles(db: Session, user_id: int) -> list[str]:
    """查用户的所有角色编码"""
    rows = (
        db.query(SysRole.role_code)
        .join(SysUserRole, SysRole.id == SysUserRole.role_id)
        .filter(SysUserRole.user_id == user_id, SysUserRole.is_deleted == 0)
        .all()
    )
    return [r[0] for r in rows]


def _build_user_out(db: Session, user: SysUser) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        phone=user.phone,
        status=user.status,
        roles=_get_user_roles(db, user.id),
    )


@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = (
        db.query(SysUser)
        .filter(SysUser.username == body.username, SysUser.is_deleted == 0)
        .first()
    )
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号已被停用，请联系管理员")

    token = create_access_token(user.id)
    return LoginOut(token=token, user=_build_user_out(db, user))


@router.get("/me", response_model=UserOut)
def me(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
):
    return _build_user_out(db, user)