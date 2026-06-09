from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./tesschain.db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"
    app_name: str = "TessChain API"
    app_version: str = "1.0.0"

    class Config:
        env_file = ".env"


settings = Settings()
