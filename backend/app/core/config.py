from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "物资财务系统"
    API_PREFIX: str = "/api/v1"

    # ⚠️ 兜底值（假数据），真实值从 .env 文件读
    DATABASE_URL: str = "sqlite:///./wuzi.db"

    JWT_SECRET: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 720

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()