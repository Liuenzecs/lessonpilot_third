from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import Task, User
from app.schemas.document import DocumentListResponse, DocumentRead, DocumentUpdatePayload
from app.services.document_service import (
    get_owned_document,
    list_documents_for_task,
    load_content,
    serialize_document,
    update_document,
)
from app.services.export_service import build_docx

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=DocumentListResponse)
def get_documents(
    task_id: str = Query(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentListResponse:
    documents = list_documents_for_task(session, task_id, current_user.id)
    return DocumentListResponse(items=[serialize_document(document) for document in documents])


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    document = get_owned_document(session, document_id, current_user.id)
    return serialize_document(document)


@router.patch("/{document_id}", response_model=DocumentRead)
def patch_document(
    document_id: str,
    payload: DocumentUpdatePayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    document = get_owned_document(session, document_id, current_user.id)
    updated_document = update_document(session, document, payload)
    return serialize_document(updated_document)


@router.get("/{document_id}/export")
def export_document(
    document_id: str,
    format: str = Query("docx"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    if format != "docx":
        raise HTTPException(status_code=400, detail="Only docx export is supported")

    document = get_owned_document(session, document_id, current_user.id)
    task = session.exec(select(Task).where(Task.id == document.task_id, Task.user_id == current_user.id)).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    payload = build_docx(task, load_content(document))
    filename = quote(f"{task.title}.docx")
    return Response(
        content=payload,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )
