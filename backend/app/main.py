from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import Base, engine
from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.supplier import Supplier  # noqa: F401
from app.models.dict_item import DictItem  # noqa: F401

from app.api.v1.auth import router as auth_router
from app.api.v1.project import router as project_router
from app.api.v1.supplier import router as supplier_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.dict import router as dict_router

app = FastAPI(title=settings.APP_NAME)

# 开发期自动建表（生产环境应改为 Alembic 迁移）
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(project_router, prefix=settings.API_PREFIX)
app.include_router(supplier_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(dict_router, prefix=settings.API_PREFIX)


@app.get("/health")
def health():
    return {"ok": True}