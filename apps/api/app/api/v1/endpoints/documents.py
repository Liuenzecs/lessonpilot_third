from __future__ import annotations

from urllib.parse import quote, urlencode

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import Task, User
from app.schemas.document import (
    DocumentAppendPayload,
    DocumentAppendStartResponse,
    DocumentHistoryResponse,
    DocumentListResponse,
    DocumentRead,
    DocumentRewritePayload,
    DocumentRewriteStartResponse,
    DocumentSnapshotRead,
    DocumentUpdatePayload,
)
from app.services.analytics_service import record_server_event
from app.services.append_service import get_document_task as get_append_document_task
from app.services.append_service import stream_append
from app.services.billing_service import require_professional_feature
from app.services.document_service import (
    get_document_snapshot,
    get_owned_document,
    list_document_history,
    list_documents_for_task,
    load_content,
    restore_document_snapshot,
    serialize_document,
    serialize_snapshot,
    update_document,
)
from app.services.export_service import build_docx, build_pdf
from app.services.rewrite_service import get_document_task, stream_rewrite

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


@router.post("/{document_id}/rewrite", response_model=DocumentRewriteStartResponse)
def start_document_rewrite(
    document_id: str,
    payload: DocumentRewritePayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentRewriteStartResponse:
    require_professional_feature(session, current_user, "局部 AI 重写")
    document = get_owned_document(session, document_id, current_user.id)
    if payload.document_version != document.version:
        raise HTTPException(status_code=409, detail="Document version conflict")

    query = urlencode(
        {
            "document_version": payload.document_version,
            "mode": payload.mode,
            "target_block_id": payload.target_block_id,
            "action": payload.action,
            "selection_text": payload.selection_text or "",
        }
    )
    return DocumentRewriteStartResponse(
        stream_url=f"/api/v1/documents/{document_id}/rewrite/stream?{query}"
    )


@router.post("/{document_id}/append", response_model=DocumentAppendStartResponse)
def start_document_append(
    document_id: str,
    payload: DocumentAppendPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentAppendStartResponse:
    require_professional_feature(session, current_user, "AI 补充内容")
    document = get_owned_document(session, document_id, current_user.id)
    if payload.document_version != document.version:
        raise HTTPException(status_code=409, detail="Document version conflict")

    query = urlencode(
        {
            "document_version": payload.document_version,
            "section_id": payload.section_id,
            "instruction": payload.instruction,
        }
    )
    return DocumentAppendStartResponse(
        stream_url=f"/api/v1/documents/{document_id}/append/stream?{query}"
    )


@router.get("/{document_id}/append/stream")
async def stream_document_append(
    document_id: str,
    document_version: int,
    section_id: str,
    instruction: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    require_professional_feature(session, current_user, "AI 补充内容")
    document = get_owned_document(session, document_id, current_user.id)
    if document.version != document_version:
        raise HTTPException(status_code=409, detail="Document version conflict")

    task = get_append_document_task(session, document)
    payload = DocumentAppendPayload(
        document_version=document_version,
        section_id=section_id,
        instruction=instruction,
    )
    return StreamingResponse(
        stream_append(session, document, task, payload),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/{document_id}/rewrite/stream")
async def stream_document_rewrite(
    document_id: str,
    document_version: int,
    mode: str,
    target_block_id: str,
    action: str,
    selection_text: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    require_professional_feature(session, current_user, "局部 AI 重写")
    document = get_owned_document(session, document_id, current_user.id)
    if document.version != document_version:
        raise HTTPException(status_code=409, detail="Document version conflict")

    task = get_document_task(session, document)
    payload = DocumentRewritePayload(
        document_version=document_version,
        mode=mode,
        target_block_id=target_block_id,
        action=action,
        selection_text=selection_text,
    )
    return StreamingResponse(
        stream_rewrite(session, document, task, payload),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/{document_id}/history", response_model=DocumentHistoryResponse)
def get_document_history(
    document_id: str,
    limit: int = Query(10, ge=1, le=10),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentHistoryResponse:
    require_professional_feature(session, current_user, "版本历史")
    document = get_owned_document(session, document_id, current_user.id)
    snapshots = list_document_history(session, document, limit=limit)
    return DocumentHistoryResponse(items=[serialize_snapshot(snapshot) for snapshot in snapshots])


@router.get("/{document_id}/history/{snapshot_id}", response_model=DocumentSnapshotRead)
def get_document_history_snapshot(
    document_id: str,
    snapshot_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentSnapshotRead:
    require_professional_feature(session, current_user, "版本历史")
    document = get_owned_document(session, document_id, current_user.id)
    snapshot = get_document_snapshot(session, document, snapshot_id)
    return serialize_snapshot(snapshot)


@router.post("/{document_id}/history/{snapshot_id}/restore", response_model=DocumentRead)
def restore_history_snapshot(
    document_id: str,
    snapshot_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    require_professional_feature(session, current_user, "版本历史")
    document = get_owned_document(session, document_id, current_user.id)
    snapshot = get_document_snapshot(session, document, snapshot_id)
    updated_document = restore_document_snapshot(session, document, snapshot)
    return serialize_document(updated_document)


@router.get("/{document_id}/export")
def export_document(
    document_id: str,
    format: str = Query("docx"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    document = get_owned_document(session, document_id, current_user.id)
    task = session.exec(select(Task).where(Task.id == document.task_id, Task.user_id == current_user.id)).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if format == "docx":
        payload = build_docx(task, load_content(document))
        record_server_event(
            session,
            event_name="docx_export_succeeded",
            user=current_user,
            page_path=f"/tasks/{task.id}/editor",
            properties={"task_id": task.id},
        )
        filename = quote(f"{task.title}.docx")
        return Response(
            content=payload,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
        )
    if format == "pdf":
        require_professional_feature(session, current_user, "PDF 导出")
        payload = build_pdf(task, load_content(document))
        record_server_event(
            session,
            event_name="pdf_export_succeeded",
            user=current_user,
            page_path=f"/tasks/{task.id}/editor",
            properties={"task_id": task.id},
        )
        filename = quote(f"{task.title}.pdf")
        return Response(
            content=payload,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
        )

    raise HTTPException(status_code=400, detail="Only docx and pdf export are supported")
