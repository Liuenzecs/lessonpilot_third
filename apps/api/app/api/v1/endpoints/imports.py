from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.lesson_import import (
    BatchImportConfirmPayload,
    BatchImportConfirmResponse,
    BatchImportPreview,
    LessonPlanImportConfirmPayload,
    LessonPlanImportConfirmResponse,
    LessonPlanImportPreview,
)
from app.services.import_service import (
    batch_create_imported_lesson_plans,
    create_imported_lesson_plan,
    preview_lesson_plan_import,
)

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/lesson-plan/preview", response_model=LessonPlanImportPreview)
async def preview_lesson_plan(
    file: UploadFile = File(...),
    _current_user: User = Depends(get_current_user),
) -> LessonPlanImportPreview:
    file_bytes = await file.read()
    return preview_lesson_plan_import(file_bytes, file.filename or "lesson-plan.docx")


@router.post("/lesson-plan/confirm", response_model=LessonPlanImportConfirmResponse)
def confirm_lesson_plan_import(
    payload: LessonPlanImportConfirmPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> LessonPlanImportConfirmResponse:
    task, document = create_imported_lesson_plan(session, current_user.id, payload)
    return LessonPlanImportConfirmResponse(task=task, document=document)


@router.post("/lesson-plan/batch-preview", response_model=BatchImportPreview)
async def preview_batch_lesson_plan(
    files: list[UploadFile] = File(...),
    _current_user: User = Depends(get_current_user),
) -> BatchImportPreview:
    items: list[LessonPlanImportPreview] = []
    for f in files[:10]:
        file_bytes = await f.read()
        preview = preview_lesson_plan_import(file_bytes, f.filename or "lesson-plan.docx")
        items.append(preview)
    return BatchImportPreview(items=items)


@router.post("/lesson-plan/batch-confirm", response_model=BatchImportConfirmResponse)
def confirm_batch_lesson_plan_import(
    payload: BatchImportConfirmPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BatchImportConfirmResponse:
    return batch_create_imported_lesson_plans(session, current_user.id, payload)
