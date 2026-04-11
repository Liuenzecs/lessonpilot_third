from __future__ import annotations

import logging
from urllib.parse import quote

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _public_url(path: str) -> str:
    base_url = get_settings().app_base_url.rstrip("/")
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url}{normalized_path}"


def _log_email(subject: str, recipient: str, body: str) -> None:
    logger.info("Console email\nTo: %s\nSubject: %s\n\n%s", recipient, subject, body)


def send_verification_email(to_email: str, name: str, token: str) -> None:
    verify_url = _public_url(f"/verify-email?token={quote(token)}")
    body = (
        f"{name}，你好：\n\n"
        "欢迎使用 LessonPilot。\n"
        f"请点击下面的链接验证邮箱：\n{verify_url}\n\n"
        "这个链接将在 48 小时后失效。"
    )
    _log_email("LessonPilot 邮箱验证", to_email, body)


def send_password_reset_email(to_email: str, name: str, token: str) -> None:
    reset_url = _public_url(f"/reset-password?token={quote(token)}")
    body = (
        f"{name}，你好：\n\n"
        "我们收到了你的密码重置请求。\n"
        f"请点击下面的链接设置新密码：\n{reset_url}\n\n"
        "如果这不是你的操作，可以忽略这封邮件。"
    )
    _log_email("LessonPilot 密码重置", to_email, body)


def send_feedback_notification(
    *,
    user_name: str,
    user_email: str,
    mood: str,
    message: str,
    page_path: str | None,
) -> None:
    recipient = get_settings().feedback_notify_email
    body = (
        "收到新的产品反馈：\n\n"
        f"用户：{user_name} <{user_email}>\n"
        f"心情：{mood}\n"
        f"页面：{page_path or '未知页面'}\n\n"
        f"内容：\n{message}"
    )
    _log_email("LessonPilot 用户反馈", recipient, body)
