from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_token
from app.models.sys_user import SysUser

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> SysUser:
    if cred is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "未登录")

    payload = decode_token(cred.credentials)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token 无效或已过期")

    user = db.get(SysUser, int(payload["sub"]))
    if not user or user.status != 1 or user.is_deleted != 0:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号不存在或已停用")
    return user