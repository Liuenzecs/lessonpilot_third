"""分享链接 API 端点。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user, get_optional_user
from app.models import User
from app.schemas.share import (
    ShareCommentCreate,
    ShareCommentRead,
    ShareLinkCreate,
    ShareLinkRead,
    ShareLinkUpdate,
    SharedDocumentView,
)
from app.services.share_service import (
    add_comment,
    create_share_link,
    deactivate_share_link,
    list_comments,
    list_share_links,
    resolve_share_token,
    update_share_link,
)

router = APIRouter(tags=["sharing"])


# ---------------------------------------------------------------------------
# Owner endpoints (auth required)
# ---------------------------------------------------------------------------


@router.post("/documents/{document_id}/share", response_model=ShareLinkRead)
def create_document_share(
    document_id: str,
    payload: ShareLinkCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ShareLinkRead:
    return create_share_link(session, document_id, current_user.id, payload)


@router.get("/documents/{document_id}/shares", response_model=list[ShareLinkRead])
def get_document_shares(
    document_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[ShareLinkRead]:
    return list_share_links(session, document_id, current_user.id)


@router.patch("/shares/{share_id}", response_model=ShareLinkRead)
def patch_share_link(
    share_id: str,
    payload: ShareLinkUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ShareLinkRead:
    return update_share_link(session, share_id, current_user.id, payload)


@router.delete("/shares/{share_id}", status_code=204)
def delete_share_link(
    share_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    deactivate_share_link(session, share_id, current_user.id)


# ---------------------------------------------------------------------------
# Public endpoints (no auth required)
# ---------------------------------------------------------------------------


@router.get("/share/{token}", response_model=SharedDocumentView)
def get_shared_document(
    token: str,
    session: Session = Depends(get_session),
) -> SharedDocumentView:
    return resolve_share_token(session, token)


@router.post("/share/{token}/comments", response_model=ShareCommentRead)
def post_share_comment(
    token: str,
    payload: ShareCommentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_optional_user),
) -> ShareCommentRead:
    return add_comment(session, token, payload, current_user)


@router.get("/share/{token}/comments", response_model=list[ShareCommentRead])
def get_share_comments(
    token: str,
    session: Session = Depends(get_session),
) -> list[ShareCommentRead]:
    return list_comments(session, token)
