from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.task import (
    GenerationStartPayload,
    GenerationStartResponse,
    PaginatedTasks,
    TaskCreatePayload,
    TaskRead,
    TaskUpdatePayload,
)
from app.services.generation_service import get_task_document, stream_generation
from app.services.task_service import (
    create_task,
    delete_task,
    duplicate_task,
    get_owned_task,
    list_tasks,
    update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _to_task_read(task) -> TaskRead:
    return TaskRead(
        id=task.id,
        title=task.title,
        subject=task.subject,
        grade=task.grade,
        topic=task.topic,
        requirements=task.requirements,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/", response_model=PaginatedTasks)
def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedTasks:
    tasks, total = list_tasks(session, current_user.id, page, page_size)
    return PaginatedTasks(
        items=[_to_task_read(task) for task in tasks],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def post_task(
    payload: TaskCreatePayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    task = create_task(session, current_user.id, payload)
    return _to_task_read(task)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    return _to_task_read(get_owned_task(session, task_id, current_user.id))


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(
    task_id: str,
    payload: TaskUpdatePayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    task = get_owned_task(session, task_id, current_user.id)
    return _to_task_read(update_task(session, task, payload))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task(
    task_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    task = get_owned_task(session, task_id, current_user.id)
    delete_task(session, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/duplicate", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def duplicate_owned_task(
    task_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    source_task, source_document = get_task_document(session, task_id, current_user.id)
    duplicated_task = duplicate_task(session, source_task, source_document)
    return _to_task_read(duplicated_task)


@router.post("/{task_id}/generate", response_model=GenerationStartResponse)
def start_generation(
    task_id: str,
    payload: GenerationStartPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> GenerationStartResponse:
    get_owned_task(session, task_id, current_user.id)
    section_query = f"?section_id={payload.section_id}" if payload.section_id else ""
    return GenerationStartResponse(stream_url=f"/api/v1/tasks/{task_id}/generate/stream{section_query}")


@router.get("/{task_id}/generate/stream")
async def stream_task_generation(
    request: Request,
    task_id: str,
    section_id: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    task, document = get_task_document(session, task_id, current_user.id)
    return StreamingResponse(
        stream_generation(session, task, document, request=request, section_id=section_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
