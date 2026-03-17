from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    app_name: str = "Innexia AI Strategy Engine API"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "innexia"
    mysql_user: str = "root"
    mysql_password: str = "changeme"

    n8n_webhook_url: str = "http://localhost:5678/webhook/innexia-strategy-engine"
    n8n_timeout_seconds: int = 180

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


settings = Settings()
