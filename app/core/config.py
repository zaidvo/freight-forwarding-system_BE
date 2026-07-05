from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Backend API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    debug: bool = True
    jwt_secret_key: str = "change-this-secret"
    access_token_expire_minutes: int = 60
    root_admin_full_name: str = "Root Admin"
    root_admin_email: str = "admin@example.com"
    root_admin_password: str = "admin"
    backend_cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://82.112.254.202:3020"
    ]

    database_url: str
    trading_import_data_dir: str = "data/trading"
    trading_import_max_upload_mb: int = 25

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return value


settings = Settings()