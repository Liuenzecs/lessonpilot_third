from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Document
from app.models.base import utcnow
from app.schemas.content import ContentDocument
from app.schemas.document import DocumentRead, DocumentUpdatePayload


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


def save_document_snapshot(session: Session, document: Document, content: ContentDocument) -> Document:
    next_version = document.version + 1
    content.version = next_version
    document.content = content.model_dump(mode="json", by_alias=True)
    document.version = next_version
    document.updated_at = utcnow()
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


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
    return save_document_snapshot(session, document, content)

