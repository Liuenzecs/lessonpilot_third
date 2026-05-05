"""语文重点篇目分层题库服务。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlmodel import Session, func, select

from app.models.question import Question


def get_chapters(session: Session, subject: str = "语文") -> list[str]:
    """返回所有已有题目的篇目列表。"""
    rows = session.exec(
        select(Question.chapter).where(Question.subject == subject).distinct().order_by(Question.chapter)
    ).all()
    return list(rows)


def get_questions(
    session: Session,
    *,
    chapter: str | None = None,
    grade: str | None = None,
    difficulty: str | None = None,
    question_type: str | None = None,
    subject: str = "语文",
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Question], int]:
    """搜索/筛选题目。返回（题目列表, 总数）。"""
    stmt = select(Question).where(Question.subject == subject)

    if chapter:
        stmt = stmt.where(Question.chapter == chapter)
    if grade:
        stmt = stmt.where(Question.grade == grade)
    if difficulty:
        stmt = stmt.where(Question.difficulty == difficulty)
    if question_type:
        stmt = stmt.where(Question.question_type == question_type)

    # 计数使用相同的过滤条件
    count_stmt = select(Question).where(Question.subject == subject)
    if chapter:
        count_stmt = count_stmt.where(Question.chapter == chapter)
    if grade:
        count_stmt = count_stmt.where(Question.grade == grade)
    if difficulty:
        count_stmt = count_stmt.where(Question.difficulty == difficulty)
    if question_type:
        count_stmt = count_stmt.where(Question.question_type == question_type)
    total = session.exec(select(func.count()).select_from(count_stmt.subquery())).one()

    questions = session.exec(stmt.order_by(Question.chapter, Question.difficulty).offset(offset).limit(limit)).all()
    return list(questions), total


def get_question_by_id(session: Session, question_id: str) -> Question | None:
    return session.exec(select(Question).where(Question.id == question_id)).first()


def select_questions_for_study_guide(
    session: Session,
    chapter: str,
    *,
    count_a: int = 2,
    count_b: int = 2,
    count_c: int = 1,
    count_d: int = 1,
) -> dict[str, list[Question]]:
    """为学案生成按难度分层选题。返回 {"A": [...], "B": [...], "C": [...], "D": [...]}。"""
    result: dict[str, list[Question]] = {}
    for level, count in [("A", count_a), ("B", count_b), ("C", count_c), ("D", count_d)]:
        if count <= 0:
            result[level] = []
            continue
        questions = session.exec(
            select(Question)
            .where(Question.chapter == chapter, Question.difficulty == level)
            .limit(count)
        ).all()
        result[level] = list(questions)
    return result


def seed_questions(session: Session, questions_data: list[dict]) -> int:
    """加载种子题目数据。返回插入的题目数量。"""
    count = 0
    for data in questions_data:
        existing = session.exec(
            select(Question).where(
                Question.chapter == data["chapter"],
                Question.difficulty == data["difficulty"],
                Question.question_type == data["question_type"],
                Question.prompt == data["prompt"],
            )
        ).first()
        if existing:
            continue
        question = Question(
            id=str(uuid.uuid4()),
            chapter=data["chapter"],
            grade=data.get("grade", ""),
            question_type=data["question_type"],
            difficulty=data["difficulty"],
            prompt=data["prompt"],
            options=data.get("options"),
            answer=data.get("answer", ""),
            analysis=data.get("analysis", ""),
            source=data.get("source", "原创"),
            tags=data.get("tags"),
            subject=data.get("subject", "语文"),
            created_at=datetime.now(timezone.utc),
        )
        session.add(question)
        count += 1
    if count > 0:
        session.commit()
    return count
