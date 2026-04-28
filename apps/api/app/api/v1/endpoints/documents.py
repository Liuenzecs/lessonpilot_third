from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import Response, StreamingResponse
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import Task, User
from app.schemas.document import (
    DocumentHistoryResponse,
    DocumentListResponse,
    DocumentRead,
    DocumentRewritePayload,
    DocumentRewriteStartResponse,
    DocumentSnapshotRead,
    DocumentUpdatePayload,
)
from app.schemas.quality import QualityCheckResponse, QualityFixPayload
from app.schemas.reimport import ReimportMergePayload, ReimportPreview
from app.schemas.teaching_package import TeachingPackageRead
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
from app.services.export_service import build_docx
from app.services.courseware_service import build_pptx
from app.services.reimport_service import apply_reimport_merge, preview_reimport
from app.services.quality_fix_service import apply_quality_fix
from app.services.quality_service import check_export_quality
from app.services.rewrite_service import get_document_task, stream_rewrite
from app.services.teaching_package_service import generate_teaching_package, list_teaching_packages

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=DocumentListResponse)
def get_documents(
    task_id: str = Query(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentListResponse:
    documents = list_documents_for_task(session, task_id, current_user.id)
    return DocumentListResponse(items=[serialize_document(doc) for doc in documents])


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
    request: Request,
    document_id: str,
    payload: DocumentRewritePayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentRewriteStartResponse:
    _ = request
    document = get_owned_document(session, document_id, current_user.id)
    if payload.document_version != document.version:
        raise HTTPException(status_code=409, detail="Document version conflict")

    from urllib.parse import urlencode
    query = urlencode(
        {
            "document_version": payload.document_version,
            "section_name": payload.section_name,
            "action": payload.action,
            "instruction": payload.instruction or "",
        }
    )
    return DocumentRewriteStartResponse(
        stream_url=f"/api/v1/documents/{document_id}/rewrite/stream?{query}"
    )


@router.get("/{document_id}/rewrite/stream")
async def stream_document_rewrite(
    request: Request,
    document_id: str,
    document_version: int,
    section_name: str,
    action: str = "rewrite",
    instruction: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    document = get_owned_document(session, document_id, current_user.id)
    if document.version != document_version:
        raise HTTPException(status_code=409, detail="Document version conflict")

    task = get_document_task(session, document)
    payload = DocumentRewritePayload(
        document_version=document_version,
        section_name=section_name,
        action=action,
        instruction=instruction,
    )
    return StreamingResponse(
        stream_rewrite(
            session=session,
            document=document,
            task=task,
            payload=payload,
            request=request,
        ),
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
    document = get_owned_document(session, document_id, current_user.id)
    snapshots = list_document_history(session, document, limit=limit)
    return DocumentHistoryResponse(items=[serialize_snapshot(s) for s in snapshots])


@router.get("/{document_id}/history/{snapshot_id}", response_model=DocumentSnapshotRead)
def get_document_history_snapshot(
    document_id: str,
    snapshot_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentSnapshotRead:
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
    document = get_owned_document(session, document_id, current_user.id)
    snapshot = get_document_snapshot(session, document, snapshot_id)
    updated_document = restore_document_snapshot(session, document, snapshot)
    return serialize_document(updated_document)


@router.get("/{document_id}/export")
def export_document(
    document_id: str,
    format: str = Query("docx"),
    template_id: str | None = Query(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    document = get_owned_document(session, document_id, current_user.id)
    task = session.exec(
        select(Task).where(Task.id == document.task_id, Task.user_id == current_user.id)
    ).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if format == "docx":
        content = load_content(document)
        doc_type_label = "学案" if document.doc_type == "study_guide" else "教案"
        filename = quote(f"{task.title}_{doc_type_label}.docx")
        template_spec = _load_template_spec(session, template_id, current_user.id)
        docx_bytes = build_docx(task, content, template_spec=template_spec)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
        )

    if format == "pptx":
        if document.doc_type != "lesson_plan":
            raise HTTPException(
                status_code=400,
                detail="PPTX 课件导出仅支持教案类型，当前文档为学案，请切换到教案文档后重试。",
            )
        content = load_content(document)
        filename = quote(f"{task.title}_课件.pptx")
        pptx_bytes = build_pptx(task, content)
        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
        )

    raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")


@router.post("/{document_id}/reimport/preview", response_model=ReimportPreview)
async def preview_reimport_endpoint(
    document_id: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ReimportPreview:
    document = get_owned_document(session, document_id, current_user.id)
    if document.doc_type != "lesson_plan":
        raise HTTPException(status_code=400, detail="回导仅支持教案类型")
    file_bytes = await file.read()
    return preview_reimport(file_bytes, file.filename or "modified.docx", document)


@router.post("/{document_id}/reimport/merge", response_model=DocumentRead)
async def merge_reimport_endpoint(
    document_id: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    document = get_owned_document(session, document_id, current_user.id)
    if document.doc_type != "lesson_plan":
        raise HTTPException(status_code=400, detail="回导仅支持教案类型")

    # Parse multipart: file + form fields
    form = await request.form()
    file = form.get("file")
    if not file or not hasattr(file, "filename"):
        raise HTTPException(status_code=400, detail="请上传修改后的 .docx 文件")
    file_bytes = await file.read()

    import json

    sections_to_accept = json.loads(form.get("sections_to_accept", "[]"))
    sections_to_reject = json.loads(form.get("sections_to_reject", "[]"))
    document_version = int(form.get("document_version", "0"))

    from app.services.import_service import (
        _build_lesson_plan_content,
        _bucket_document_items,
        _clean_text,
        _extract_metadata,
    )
    from docx import Document as DocxDocument
    from io import BytesIO

    docx = DocxDocument(BytesIO(file_bytes))
    paragraphs = [_clean_text(p.text) for p in docx.paragraphs if _clean_text(p.text)]
    metadata = _extract_metadata(paragraphs, file.filename or "modified.docx")
    buckets, _unmapped, _warnings = _bucket_document_items(docx, paragraphs)
    imported = _build_lesson_plan_content(metadata, buckets, _warnings)

    payload = ReimportMergePayload(
        sections_to_accept=sections_to_accept,
        sections_to_reject=sections_to_reject,
        document_version=document_version,
    )
    return apply_reimport_merge(session, document, payload, imported)


@router.get("/{document_id}/teaching-packages", response_model=list[TeachingPackageRead])
def get_teaching_packages(
    document_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[TeachingPackageRead]:
    get_owned_document(session, document_id, current_user.id)
    return list_teaching_packages(session, document_id, current_user.id)


@router.post("/{document_id}/teaching-package", response_model=TeachingPackageRead, status_code=201)
def create_teaching_package(
    document_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TeachingPackageRead:
    return generate_teaching_package(session, document_id, current_user.id)


@router.post("/{document_id}/quality-check", response_model=QualityCheckResponse)
def quality_check_document(
    document_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> QualityCheckResponse:
    document = get_owned_document(session, document_id, current_user.id)
    task = session.exec(
        select(Task).where(Task.id == document.task_id, Task.user_id == current_user.id)
    ).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return check_export_quality(task, load_content(document))


@router.post("/{document_id}/quality-fix", response_model=DocumentRead)
def quality_fix_document(
    document_id: str,
    payload: QualityFixPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    document = get_owned_document(session, document_id, current_user.id)
    task = session.exec(
        select(Task).where(Task.id == document.task_id, Task.user_id == current_user.id)
    ).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    updated_document = apply_quality_fix(session, document, task, payload)
    return serialize_document(updated_document)


def _load_template_spec(session: Session, template_id: str | None, user_id: str) -> dict | None:
    if not template_id:
        return None
    from app.services.template_service import get_accessible_template

    template = get_accessible_template(session, template_id, user_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.template_type != "school_lesson_export":
        return None
    return template.content
