from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database - MySQL
    database_url: str = "mysql+aiomysql://root:password@localhost:3306/vitalis"

    # JWT
    secret_key: str = "changeme-in-production-use-strong-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@vitalis.com.br"

    # WebRTC
    stun_server: str = "stun:stun.l.google.com:19302"
    turn_server: str = ""
    turn_user: str = ""
    turn_password: str = ""

    # Storage
    storage_type: str = "local"
    storage_path: str = "./uploads"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = ""
    aws_region: str = "us-east-1"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
