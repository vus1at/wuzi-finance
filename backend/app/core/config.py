import os
from pydantic_settings import BaseSettings

# 从环境变量 ENV 决定读哪个文件；默认 dev
ENV = os.getenv("ENV", "dev")


class Settings(BaseSettings):
    APP_NAME: str = "物资财务系统"
    API_PREFIX: str = "/api/v1"

    # 兜底值（假数据），真实值从 .env.{ENV} 读
    DATABASE_URL: str = "sqlite:///./wuzi.db"
    JWT_SECRET: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 720

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = f".env.{ENV}"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()