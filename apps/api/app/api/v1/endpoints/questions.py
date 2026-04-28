"""题目相关 API 端点。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.question import (
    QuestionChapterResponse,
    QuestionListResponse,
    QuestionRead,
    QuestionSeedResponse,
)
from app.services.question_bank_service import (
    get_chapters,
    get_question_by_id,
    get_questions,
    seed_questions,
)

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/chapters", response_model=list[QuestionChapterResponse])
def list_chapters(
    subject: str = Query("语文"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[QuestionChapterResponse]:
    chapters = get_chapters(session, subject=subject)
    return [QuestionChapterResponse(chapter=c) for c in chapters]


@router.get("/", response_model=QuestionListResponse)
def search_questions(
    chapter: str | None = Query(None),
    grade: str | None = Query(None),
    difficulty: str | None = Query(None),
    question_type: str | None = Query(None),
    subject: str = Query("语文"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> QuestionListResponse:
    questions, total = get_questions(
        session,
        chapter=chapter,
        grade=grade,
        difficulty=difficulty,
        question_type=question_type,
        subject=subject,
        limit=limit,
        offset=offset,
    )
    return QuestionListResponse(
        items=[_serialize_question(q) for q in questions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{question_id}", response_model=QuestionRead)
def get_question(
    question_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> QuestionRead:
    question = get_question_by_id(session, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return _serialize_question(question)


@router.post("/seed", response_model=QuestionSeedResponse)
def seed_question_bank(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> QuestionSeedResponse:
    """加载语文重点篇目题库种子数据。"""
    from pathlib import Path

    data_path = Path(__file__).parent.parent.parent.parent / "data" / "question_bank.json"
    if not data_path.exists():
        raise HTTPException(status_code=404, detail="Seed data file not found")

    import json

    questions_data = json.loads(data_path.read_text(encoding="utf-8"))
    count = seed_questions(session, questions_data)
    return QuestionSeedResponse(inserted=count)


def _serialize_question(q) -> QuestionRead:
    return QuestionRead(
        id=q.id,
        chapter=q.chapter,
        grade=q.grade,
        question_type=q.question_type,
        difficulty=q.difficulty,
        prompt=q.prompt,
        options=q.options,
        answer=q.answer,
        analysis=q.analysis,
        source=q.source,
        tags=q.tags,
        subject=q.subject,
    )
