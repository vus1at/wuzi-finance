from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw: str) -> str:
    """把明文密码转成bcrypt hash"""
    return pwd_ctx.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    """校验明文密码和hash是否匹配"""
    try:
        return pwd_ctx.verify(raw, hashed)
    except Exception:
        return False


def create_access_token(sub: str, extra: dict | None = None) -> str:
    """生成JWT token"""
    payload = {
        "sub": str(sub),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        "iat": datetime.now(timezone.utc),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """解码JWT token，失败返回None"""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None