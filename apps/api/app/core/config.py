from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

API_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[4]


def _resolve_env_files() -> tuple[str, ...]:
    files: list[str] = []
    project_env = PROJECT_ROOT / ".env"
    api_env = API_ROOT / ".env"

    if project_env.exists():
        files.append(str(project_env))
    if api_env.exists():
        files.append(str(api_env))

    return tuple(files) or (".env",)


class Settings(BaseSettings):
    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://lessonpilot:lessonpilot@localhost:5432/lessonpilot"
    jwt_secret: str = "replace-with-a-long-random-secret"
    jwt_expire_minutes: int = 1440
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    cors_origins: str = "http://localhost:5173"
    app_base_url: str = "http://localhost:5173"
    mail_delivery_mode: Literal["console", "smtp"] = "console"
    mail_from_email: str = "hello@lessonpilot.com"
    mail_from_name: str = "LessonPilot"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    feedback_notify_email: str = "feedback@lessonpilot.com"
    verify_email_token_expire_hours: int = 48
    reset_password_token_expire_minutes: int = 30
    rate_limit_enabled: bool = True
    rate_limit_login_per_minute: int = 10
    rate_limit_generation_per_hour: int = 20
    rate_limit_general_per_minute: int = 60
    llm_provider: Literal["fake", "deepseek", "minimax"] = "fake"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    minimax_api_key: str = ""
    minimax_model: str = "MiniMax-Text-01"
    minimax_base_url: str = "https://api.minimax.chat/v1"
    minimax_embedding_model: str = "embo-01"
    embedding_provider: Literal["local_bge", "minimax"] = "local_bge"
    embedding_model: str = "BAAI/bge-m3"
    embedding_device: str = "cpu"
    rag_enabled: bool = True
    rag_trigger_mode: Literal["topic_route", "always", "disabled"] = "topic_route"
    rag_max_knowledge_tokens: int = 3000
    rag_top_k: int = 8

    model_config = SettingsConfigDict(
        env_file=_resolve_env_files(),
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_runtime_settings(self) -> "Settings":
        if self.app_env == "production":
            normalized_secret = self.jwt_secret.strip()
            insecure_defaults = {
                "",
                "development-secret",
                "replace-with-a-long-random-secret",
            }
            if normalized_secret in insecure_defaults or len(normalized_secret) < 32:
                raise ValueError("JWT_SECRET must be replaced with a strong secret before production startup")
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
