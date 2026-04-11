from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Document, DocumentSnapshot
from app.models.base import utcnow
from app.schemas.content import ContentDocument
from app.schemas.document import (
    DocumentRead,
    DocumentSnapshotRead,
    DocumentUpdatePayload,
)

SNAPSHOT_LIMIT = 10


def get_owned_document(session: Session, document_id: str, user_id: str) -> Document:
    document = session.exec(
        select(Document).where(Document.id == document_id, Document.user_id == user_id)
    ).first()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


def list_documents_for_task(session: Session, task_id: str, user_id: str) -> list[Document]:
    return session.exec(
        select(Document).where(Document.task_id == task_id, Document.user_id == user_id)
    ).all()


def load_content(document: Document) -> ContentDocument:
    content = ContentDocument.model_validate(document.content)
    content.version = document.version
    return content


def serialize_document(document: Document) -> DocumentRead:
    return DocumentRead(
        id=document.id,
        task_id=document.task_id,
        user_id=document.user_id,
        doc_type=document.doc_type,
        title=document.title,
        content=load_content(document),
        version=document.version,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def serialize_snapshot(snapshot: DocumentSnapshot) -> DocumentSnapshotRead:
    return DocumentSnapshotRead(
        id=snapshot.id,
        document_id=snapshot.document_id,
        version=snapshot.version,
        content=ContentDocument.model_validate(snapshot.content),
        source=snapshot.source,
        created_at=snapshot.created_at,
    )


def _trim_snapshots(session: Session, document_id: str) -> None:
    snapshots = session.exec(
        select(DocumentSnapshot)
        .where(DocumentSnapshot.document_id == document_id)
        .order_by(DocumentSnapshot.version.desc(), DocumentSnapshot.created_at.desc())
    ).all()
    for snapshot in snapshots[SNAPSHOT_LIMIT:]:
        session.delete(snapshot)


def _create_snapshot(
    session: Session,
    document: Document,
    content: ContentDocument,
    source: str,
) -> DocumentSnapshot:
    snapshot = DocumentSnapshot(
        document_id=document.id,
        version=document.version,
        content=content.model_dump(mode="json", by_alias=True),
        source=source,
    )
    session.add(snapshot)
    session.flush()
    _trim_snapshots(session, document.id)
    return snapshot


def save_document(
    session: Session,
    document: Document,
    content: ContentDocument,
    *,
    snapshot_source: str | None = None,
) -> Document:
    next_version = document.version + 1
    content.version = next_version
    document.content = content.model_dump(mode="json", by_alias=True)
    document.version = next_version
    document.updated_at = utcnow()
    session.add(document)
    session.flush()
    if snapshot_source is not None:
        _create_snapshot(session, document, content, snapshot_source)
    session.commit()
    session.refresh(document)
    return document


def record_current_snapshot(session: Session, document: Document, source: str) -> DocumentSnapshot:
    content = load_content(document)
    snapshot = _create_snapshot(session, document, content, source)
    session.commit()
    session.refresh(snapshot)
    return snapshot


def list_document_history(
    session: Session,
    document: Document,
    limit: int = SNAPSHOT_LIMIT,
) -> list[DocumentSnapshot]:
    return session.exec(
        select(DocumentSnapshot)
        .where(DocumentSnapshot.document_id == document.id)
        .order_by(DocumentSnapshot.version.desc(), DocumentSnapshot.created_at.desc())
        .limit(limit)
    ).all()


def get_document_snapshot(
    session: Session,
    document: Document,
    snapshot_id: str,
) -> DocumentSnapshot:
    snapshot = session.exec(
        select(DocumentSnapshot).where(
            DocumentSnapshot.id == snapshot_id,
            DocumentSnapshot.document_id == document.id,
        )
    ).first()
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found")
    return snapshot


def restore_document_snapshot(
    session: Session,
    document: Document,
    snapshot: DocumentSnapshot,
) -> Document:
    content = ContentDocument.model_validate(snapshot.content)
    return save_document(session, document, content, snapshot_source="restore")


def update_document(
    session: Session,
    document: Document,
    payload: DocumentUpdatePayload,
) -> Document:
    if payload.version != document.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document version conflict",
        )
    content = ContentDocument.model_validate(payload.content)
    return save_document(session, document, content, snapshot_source="save")
