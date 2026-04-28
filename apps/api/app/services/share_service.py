"""分享链接服务 — 创建、解析、评论管理。"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import Document, ShareComment, ShareLink, Task, User
from app.schemas.share import (
    ShareCommentCreate,
    ShareCommentRead,
    ShareLinkCreate,
    ShareLinkRead,
    ShareLinkUpdate,
    SharedDocumentView,
)
from app.services.document_service import load_content


def _generate_token() -> str:
    return secrets.token_urlsafe(24)


def _build_share_url(token: str) -> str:
    from app.core.config import get_settings
    settings = get_settings()
    base = getattr(settings, "app_base_url", "http://localhost:5173")
    return f"{base.rstrip('/')}/share/{token}"


def create_share_link(
    session: Session,
    document_id: str,
    user_id: str,
    payload: ShareLinkCreate,
) -> ShareLinkRead:
    document = session.exec(
        select(Document).where(Document.id == document_id, Document.user_id == user_id)
    ).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    expires_at = None
    if payload.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=payload.expires_in_days)

    token = _generate_token()
    link = ShareLink(
        document_id=document_id,
        owner_id=user_id,
        token=token,
        permission=payload.permission,
        expires_at=expires_at,
    )
    session.add(link)
    session.commit()
    session.refresh(link)

    return ShareLinkRead(
        id=link.id,
        document_id=link.document_id,
        token=link.token,
        permission=link.permission,
        expires_at=link.expires_at,
        is_active=link.is_active,
        url=_build_share_url(link.token),
        created_at=link.created_at,
    )


def list_share_links(session: Session, document_id: str, user_id: str) -> list[ShareLinkRead]:
    document = session.exec(
        select(Document).where(Document.id == document_id, Document.user_id == user_id)
    ).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    links = session.exec(
        select(ShareLink)
        .where(ShareLink.document_id == document_id, ShareLink.owner_id == user_id)
        .order_by(ShareLink.created_at.desc())
    ).all()

    return [
        ShareLinkRead(
            id=link.id,
            document_id=link.document_id,
            token=link.token,
            permission=link.permission,
            expires_at=link.expires_at,
            is_active=link.is_active,
            url=_build_share_url(link.token),
            created_at=link.created_at,
        )
        for link in links
    ]


def update_share_link(
    session: Session,
    share_id: str,
    user_id: str,
    payload: ShareLinkUpdate,
) -> ShareLinkRead:
    link = session.exec(
        select(ShareLink).where(ShareLink.id == share_id, ShareLink.owner_id == user_id)
    ).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Share link not found")

    if payload.is_active is not None:
        link.is_active = payload.is_active
    if payload.permission is not None:
        link.permission = payload.permission
    if payload.expires_in_days is not None:
        link.expires_at = datetime.now(timezone.utc) + timedelta(days=payload.expires_in_days)
    link.updated_at = datetime.now(timezone.utc)

    session.add(link)
    session.commit()
    session.refresh(link)

    return ShareLinkRead(
        id=link.id,
        document_id=link.document_id,
        token=link.token,
        permission=link.permission,
        expires_at=link.expires_at,
        is_active=link.is_active,
        url=_build_share_url(link.token),
        created_at=link.created_at,
    )


def deactivate_share_link(session: Session, share_id: str, user_id: str) -> None:
    link = session.exec(
        select(ShareLink).where(ShareLink.id == share_id, ShareLink.owner_id == user_id)
    ).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Share link not found")
    link.is_active = False
    link.updated_at = datetime.now(timezone.utc)
    session.add(link)
    session.commit()


def resolve_share_token(session: Session, token: str) -> SharedDocumentView:
    link = session.exec(
        select(ShareLink).where(ShareLink.token == token)
    ).first()
    if link is None or not link.is_active:
        raise HTTPException(status_code=404, detail="分享链接不存在或已失效")
    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="分享链接已过期")

    document = session.exec(select(Document).where(Document.id == link.document_id)).first()
    if document is None:
        raise HTTPException(status_code=404, detail="文档已被删除")

    task = session.exec(select(Task).where(Task.id == document.task_id)).first()
    content = load_content(document)

    comments = session.exec(
        select(ShareComment)
        .where(ShareComment.share_link_id == link.id)
        .order_by(ShareComment.created_at.asc())
    ).all()

    return SharedDocumentView(
        title=task.title if task else document.title,
        subject=task.subject if task else "",
        grade=task.grade if task else "",
        topic=task.topic if task else "",
        doc_type=document.doc_type,
        content=content.model_dump(by_alias=True) if hasattr(content, "model_dump") else content,
        permission=link.permission,
        comments=[_serialize_comment(c) for c in comments],
    )


def add_comment(
    session: Session,
    token: str,
    payload: ShareCommentCreate,
    user: User | None = None,
) -> ShareCommentRead:
    link = session.exec(
        select(ShareLink).where(ShareLink.token == token)
    ).first()
    if link is None or not link.is_active:
        raise HTTPException(status_code=404, detail="分享链接不存在或已失效")
    if link.permission != "comment":
        raise HTTPException(status_code=403, detail="此分享链接不支持评论")

    comment = ShareComment(
        share_link_id=link.id,
        user_id=user.id if user else None,
        author_name=user.name if user else payload.author_name,
        section_name=payload.section_name,
        body=payload.body,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _serialize_comment(comment)


def list_comments(session: Session, token: str) -> list[ShareCommentRead]:
    link = session.exec(
        select(ShareLink).where(ShareLink.token == token)
    ).first()
    if link is None or not link.is_active:
        raise HTTPException(status_code=404, detail="分享链接不存在或已失效")

    comments = session.exec(
        select(ShareComment)
        .where(ShareComment.share_link_id == link.id)
        .order_by(ShareComment.created_at.asc())
    ).all()
    return [_serialize_comment(c) for c in comments]


def _serialize_comment(c: ShareComment) -> ShareCommentRead:
    return ShareCommentRead(
        id=c.id,
        section_name=c.section_name,
        body=c.body,
        author_name=c.author_name,
        resolved=c.resolved,
        created_at=c.created_at,
    )
