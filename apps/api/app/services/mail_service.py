from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from urllib.parse import quote

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MailPayload:
    template_key: str
    recipient_email: str
    subject: str
    body: str
    user_id: str | None = None


def _public_url(path: str) -> str:
    base_url = get_settings().app_base_url.rstrip("/")
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url}{normalized_path}"


def _build_message(payload: MailPayload) -> EmailMessage:
    settings = get_settings()
    message = EmailMessage()
    message["From"] = f"{settings.mail_from_name} <{settings.mail_from_email}>"
    message["To"] = payload.recipient_email
    message["Subject"] = payload.subject
    message.set_content(payload.body)
    return message


def _send_console(payload: MailPayload) -> None:
    logger.info("Console email\nTo: %s\nSubject: %s\n\n%s", payload.recipient_email, payload.subject, payload.body)


def _send_smtp(payload: MailPayload) -> None:
    settings = get_settings()
    if not settings.smtp_host:
        raise RuntimeError("SMTP host is not configured")

    message = _build_message(payload)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)


def _deliver(payload: MailPayload) -> None:
    if get_settings().mail_delivery_mode == "smtp":
        _send_smtp(payload)
        return
    _send_console(payload)


def send_welcome_verification_email(to_email: str, name: str, token: str, *, user_id: str | None = None) -> None:
    verify_url = _public_url(f"/verify-email?token={quote(token)}")
    body = (
        f"{name}，你好：\n\n"
        "欢迎来到 LessonPilot。\n"
        "你的备课台已经准备好了，现在只差最后一步邮箱验证。\n\n"
        f"点击这里完成验证：\n{verify_url}\n\n"
        "验证链接 48 小时内有效。"
    )
    _deliver(
        MailPayload(
            template_key="welcome_verify_email",
            recipient_email=to_email,
            subject="欢迎来到 LessonPilot，请验证你的邮箱",
            body=body,
            user_id=user_id,
        )
    )


def send_verification_email(to_email: str, name: str, token: str, *, user_id: str | None = None) -> None:
    verify_url = _public_url(f"/verify-email?token={quote(token)}")
    body = (
        f"{name}，你好：\n\n"
        "请点击下面的链接验证你的 LessonPilot 邮箱：\n"
        f"{verify_url}\n\n"
        "如果这不是你的操作，可以忽略这封邮件。"
    )
    _deliver(
        MailPayload(
            template_key="verify_email",
            recipient_email=to_email,
            subject="LessonPilot 邮箱验证",
            body=body,
            user_id=user_id,
        )
    )


def send_password_reset_email(to_email: str, name: str, token: str, *, user_id: str | None = None) -> None:
    reset_url = _public_url(f"/reset-password?token={quote(token)}")
    body = (
        f"{name}，你好：\n\n"
        "我们收到了你的密码重置请求。\n"
        f"请点击下面的链接设置新密码：\n{reset_url}\n\n"
        "如果这不是你的操作，可以忽略这封邮件。"
    )
    _deliver(
        MailPayload(
            template_key="password_reset",
            recipient_email=to_email,
            subject="LessonPilot 密码重置",
            body=body,
            user_id=user_id,
        )
    )


def send_feedback_notification(
    *,
    user_id: str | None,
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
    _deliver(
        MailPayload(
            template_key="feedback_notification",
            recipient_email=recipient,
            subject="LessonPilot 用户反馈",
            body=body,
            user_id=user_id,
        )
    )
