from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from urllib.parse import quote

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.db import get_engine
from app.models import EmailDeliveryLog, User

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MailPayload:
    template_key: str
    recipient_email: str
    subject: str
    body: str
    user_id: str | None = None
    dedupe_key: str | None = None


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


def _already_sent(session: Session, dedupe_key: str | None) -> bool:
    if not dedupe_key:
        return False
    existing = session.exec(
        select(EmailDeliveryLog).where(
            EmailDeliveryLog.dedupe_key == dedupe_key,
            EmailDeliveryLog.status == "sent",
        )
    ).first()
    return existing is not None


def _persist_log(
    session: Session,
    *,
    payload: MailPayload,
    status: str,
    error_message: str | None = None,
) -> None:
    session.add(
        EmailDeliveryLog(
            user_id=payload.user_id,
            template_key=payload.template_key,
            recipient_email=payload.recipient_email,
            subject=payload.subject,
            delivery_mode=get_settings().mail_delivery_mode,
            status=status,
            dedupe_key=payload.dedupe_key,
            error_message=error_message,
        )
    )
    session.commit()


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


def _send_with_logging(payload: MailPayload) -> bool:
    with Session(get_engine()) as session:
        if _already_sent(session, payload.dedupe_key):
            return False

        try:
            _deliver(payload)
        except Exception as exc:
            _persist_log(session, payload=payload, status="failed", error_message=str(exc))
            logger.exception("Failed to send email template %s to %s", payload.template_key, payload.recipient_email)
            raise

        _persist_log(session, payload=payload, status="sent")
        return True


def send_welcome_verification_email(to_email: str, name: str, token: str, *, user_id: str | None = None) -> bool:
    verify_url = _public_url(f"/verify-email?token={quote(token)}")
    body = (
        f"{name}，你好：\n\n"
        "欢迎来到 LessonPilot。\n"
        "你的备课台已经准备好了，现在只差最后一步邮箱验证。\n\n"
        f"点击这里完成验证：\n{verify_url}\n\n"
        "验证链接 48 小时内有效。"
    )
    return _send_with_logging(
        MailPayload(
            template_key="welcome_verify_email",
            recipient_email=to_email,
            subject="欢迎来到 LessonPilot，请验证你的邮箱",
            body=body,
            user_id=user_id,
        )
    )


def send_verification_email(to_email: str, name: str, token: str, *, user_id: str | None = None) -> bool:
    verify_url = _public_url(f"/verify-email?token={quote(token)}")
    body = (
        f"{name}，你好：\n\n"
        "请点击下面的链接验证你的 LessonPilot 邮箱：\n"
        f"{verify_url}\n\n"
        "如果这不是你的操作，可以忽略这封邮件。"
    )
    return _send_with_logging(
        MailPayload(
            template_key="verify_email",
            recipient_email=to_email,
            subject="LessonPilot 邮箱验证",
            body=body,
            user_id=user_id,
        )
    )


def send_password_reset_email(to_email: str, name: str, token: str, *, user_id: str | None = None) -> bool:
    reset_url = _public_url(f"/reset-password?token={quote(token)}")
    body = (
        f"{name}，你好：\n\n"
        "我们收到了你的密码重置请求。\n"
        f"请点击下面的链接设置新密码：\n{reset_url}\n\n"
        "如果这不是你的操作，可以忽略这封邮件。"
    )
    return _send_with_logging(
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
) -> bool:
    recipient = get_settings().feedback_notify_email
    body = (
        "收到新的产品反馈：\n\n"
        f"用户：{user_name} <{user_email}>\n"
        f"心情：{mood}\n"
        f"页面：{page_path or '未知页面'}\n\n"
        f"内容：\n{message}"
    )
    return _send_with_logging(
        MailPayload(
            template_key="feedback_notification",
            recipient_email=recipient,
            subject="LessonPilot 用户反馈",
            body=body,
            user_id=user_id,
        )
    )


def send_invoice_request_notification(
    *,
    user_id: str | None,
    user_name: str,
    user_email: str,
    order_id: str,
    title: str,
    tax_number: str,
    invoice_email: str,
    remark: str | None,
) -> bool:
    recipient = get_settings().billing_invoice_notify_email
    body = (
        "收到新的发票申请：\n\n"
        f"用户：{user_name} <{user_email}>\n"
        f"订单：{order_id}\n"
        f"抬头：{title}\n"
        f"税号：{tax_number}\n"
        f"接收邮箱：{invoice_email}\n"
        f"备注：{remark or '无'}"
    )
    return _send_with_logging(
        MailPayload(
            template_key="invoice_request_notification",
            recipient_email=recipient,
            subject="LessonPilot 发票申请",
            body=body,
            user_id=user_id,
        )
    )


def send_quota_warning_email(*, user_id: str, remaining: int, month_key: str) -> bool:
    with Session(get_engine()) as session:
        user = session.get(User, user_id)
        if user is None:
            return False

    if remaining not in {0, 1}:
        return False

    template_key = "quota_warning_limit_reached" if remaining == 0 else "quota_warning_almost_reached"
    dedupe_key = f"{template_key}:{user_id}:{month_key}"
    if remaining == 0:
        subject = "LessonPilot 免费额度已用完"
        body = (
            f"{user.name}，你好：\n\n"
            "你本月免费版可新建的 5 份教案额度已经用完。\n"
            "升级到专业版后，可继续新建教案并解锁 PDF、版本历史和局部 AI 能力。"
        )
    else:
        subject = "LessonPilot 免费额度即将用完"
        body = (
            f"{user.name}，你好：\n\n"
            "你本月免费版可新建的教案额度只剩最后 1 份。\n"
            "如果你需要继续高频备课，建议提前升级到专业版，避免中途被额度拦住。"
        )

    return _send_with_logging(
        MailPayload(
            template_key=template_key,
            recipient_email=user.email,
            subject=subject,
            body=body,
            user_id=user.id,
            dedupe_key=dedupe_key,
        )
    )
