from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

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
    database_url: str = "postgresql+psycopg://lessonpilot:lessonpilot@localhost:5432/lessonpilot"
    jwt_secret: str = "development-secret"
    jwt_expire_minutes: int = 1440
    cors_origins: str = "http://localhost:5173"
    app_base_url: str = "http://localhost:5173"
    mail_delivery_mode: Literal["console"] = "console"
    mail_from_email: str = "hello@lessonpilot.com"
    mail_from_name: str = "LessonPilot"
    feedback_notify_email: str = "hello@lessonpilot.com"
    verify_email_token_expire_hours: int = 48
    reset_password_token_expire_minutes: int = 30
    llm_provider: Literal["fake", "deepseek"] = "fake"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com/v1"

    model_config = SettingsConfigDict(
        env_file=_resolve_env_files(),
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
