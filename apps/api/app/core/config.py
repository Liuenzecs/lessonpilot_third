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
    admin_allowlist_emails: str = ""
    billing_mode: Literal["mock", "gateway"] = "mock"
    billing_professional_monthly_price_cents: int = 2900
    billing_professional_yearly_price_cents: int = 22800
    billing_trial_days: int = 7
    billing_gateway_secret: str = ""
    billing_webhook_secret: str = ""
    billing_return_url: str = "http://localhost:5173/settings"
    billing_invoice_notify_email: str = "billing@lessonpilot.com"
    mail_delivery_mode: Literal["console", "smtp"] = "console"
    mail_from_email: str = "hello@lessonpilot.com"
    mail_from_name: str = "LessonPilot"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    feedback_notify_email: str = "hello@lessonpilot.com"
    sentry_dsn_api: str = ""
    sentry_dsn_web: str = ""
    sentry_environment: str = "development"
    sentry_traces_sample_rate_api: float = 0.0
    sentry_traces_sample_rate_web: float = 0.0
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

    @property
    def admin_allowlist(self) -> list[str]:
        return [email.strip().lower() for email in self.admin_allowlist_emails.split(",") if email.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
