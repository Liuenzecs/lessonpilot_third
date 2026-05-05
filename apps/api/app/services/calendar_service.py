"""教学日历服务 — 学期管理、排课、查询。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import LessonScheduleEntry, Semester, Task, WeekSchedule
from app.schemas.calendar import (
    LessonScheduleEntryCreate,
    LessonScheduleEntryRead,
    LessonScheduleEntryUpdate,
    SemesterCreate,
    SemesterDetailRead,
    SemesterRead,
    SemesterUpdate,
    WeekScheduleRead,
    WeekScheduleUpdate,
)

_DAY_LABELS = ["", "周一", "周二", "周三", "周四", "周五"]


def _generate_weeks(start: date, end: date) -> list[dict]:
    """根据起止日期计算每周槽位。"""
    weeks = []
    current = start
    week_num = 1
    while current <= end:
        week_end = current + timedelta(days=4)  # Mon-Fri only
        if week_end > end:
            week_end = end
        weeks.append({
            "week_number": week_num,
            "label": f"第{week_num}周（{current.strftime('%m/%d')}-{week_end.strftime('%m/%d')}）",
            "start_date": current,
            "end_date": week_end,
        })
        current = current + timedelta(days=7)
        week_num += 1
    return weeks


def create_semester(session: Session, user_id: str, payload: SemesterCreate) -> SemesterRead:
    if payload.end_date <= payload.start_date:
        raise HTTPException(status_code=400, detail="结束日期必须晚于开始日期")

    weeks_data = _generate_weeks(payload.start_date, payload.end_date)

    semester = Semester(
        user_id=user_id,
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        grade=payload.grade,
        subject=payload.subject,
        week_count=len(weeks_data),
    )
    session.add(semester)
    session.flush()

    for w in weeks_data:
        week = WeekSchedule(
            semester_id=semester.id,
            week_number=w["week_number"],
            label=w["label"],
            start_date=w["start_date"],
            end_date=w["end_date"],
        )
        session.add(week)

    session.commit()
    session.refresh(semester)
    return _serialize_semester(semester)


def list_semesters(session: Session, user_id: str, grade: str | None = None, subject: str | None = None) -> list[SemesterRead]:
    query = select(Semester).where(Semester.user_id == user_id)
    if grade:
        query = query.where(Semester.grade == grade)
    if subject:
        query = query.where(Semester.subject == subject)
    semesters = session.exec(query.order_by(Semester.created_at.desc())).all()
    return [_serialize_semester(s) for s in semesters]


def get_semester_detail(session: Session, semester_id: str, user_id: str) -> SemesterDetailRead:
    semester = _get_owned_semester(session, semester_id, user_id)
    weeks = session.exec(
        select(WeekSchedule)
        .where(WeekSchedule.semester_id == semester_id)
        .order_by(WeekSchedule.week_number)
    ).all()

    # Batch-load all entries for all weeks in one query
    week_ids = [w.id for w in weeks]
    all_entries = session.exec(
        select(LessonScheduleEntry).where(LessonScheduleEntry.week_schedule_id.in_(week_ids))
    ).all()
    entries_by_week: dict[str, list[LessonScheduleEntry]] = {}
    for e in all_entries:
        entries_by_week.setdefault(e.week_schedule_id, []).append(e)

    # Batch-load all referenced tasks in one query
    task_ids = list({e.task_id for e in all_entries})
    tasks_by_id: dict[str, Task] = {}
    if task_ids:
        tasks = session.exec(select(Task).where(Task.id.in_(task_ids))).all()
        tasks_by_id = {t.id: t for t in tasks}

    week_reads = []
    for week in weeks:
        entries = entries_by_week.get(week.id, [])
        entry_reads = [
            LessonScheduleEntryRead(
                id=e.id,
                week_schedule_id=e.week_schedule_id,
                task_id=e.task_id,
                day_of_week=e.day_of_week,
                class_period=e.class_period,
                notes=e.notes,
                task_title=tasks_by_id[e.task_id].title if e.task_id in tasks_by_id else "",
                task_subject=tasks_by_id[e.task_id].subject if e.task_id in tasks_by_id else "",
                task_grade=tasks_by_id[e.task_id].grade if e.task_id in tasks_by_id else "",
                created_at=e.created_at,
            )
            for e in entries
        ]
        week_reads.append(WeekScheduleRead(
            id=week.id,
            semester_id=week.semester_id,
            week_number=week.week_number,
            label=week.label,
            start_date=week.start_date,
            end_date=week.end_date,
            notes=week.notes,
            entries=entry_reads,
        ))

    return SemesterDetailRead(
        id=semester.id,
        name=semester.name,
        start_date=semester.start_date,
        end_date=semester.end_date,
        grade=semester.grade,
        subject=semester.subject,
        week_count=semester.week_count,
        created_at=semester.created_at,
        updated_at=semester.updated_at,
        weeks=week_reads,
    )


def update_semester(session: Session, semester_id: str, user_id: str, payload: SemesterUpdate) -> SemesterRead:
    semester = _get_owned_semester(session, semester_id, user_id)

    if payload.name is not None:
        semester.name = payload.name
    if payload.start_date is not None or payload.end_date is not None:
        start = payload.start_date or semester.start_date
        end = payload.end_date or semester.end_date
        if end <= start:
            raise HTTPException(status_code=400, detail="结束日期必须晚于开始日期")
        # Remove existing weeks and regenerate
        old_weeks = session.exec(
            select(WeekSchedule).where(WeekSchedule.semester_id == semester_id)
        ).all()
        for w in old_weeks:
            session.exec(
                select(LessonScheduleEntry).where(LessonScheduleEntry.week_schedule_id == w.id)
            )
            entries = session.exec(
                select(LessonScheduleEntry).where(LessonScheduleEntry.week_schedule_id == w.id)
            ).all()
            for e in entries:
                session.delete(e)
            session.delete(w)
        semester.start_date = start
        semester.end_date = end
        weeks_data = _generate_weeks(start, end)
        semester.week_count = len(weeks_data)
        for w in weeks_data:
            session.add(WeekSchedule(
                semester_id=semester.id,
                week_number=w["week_number"],
                label=w["label"],
                start_date=w["start_date"],
                end_date=w["end_date"],
            ))

    semester.updated_at = datetime.now(timezone.utc)
    session.add(semester)
    session.commit()
    session.refresh(semester)
    return _serialize_semester(semester)


def delete_semester(session: Session, semester_id: str, user_id: str) -> None:
    semester = _get_owned_semester(session, semester_id, user_id)
    weeks = session.exec(
        select(WeekSchedule).where(WeekSchedule.semester_id == semester_id)
    ).all()
    for w in weeks:
        entries = session.exec(
            select(LessonScheduleEntry).where(LessonScheduleEntry.week_schedule_id == w.id)
        ).all()
        for e in entries:
            session.delete(e)
        session.delete(w)
    session.delete(semester)
    session.commit()


def add_entry(
    session: Session, week_id: str, user_id: str, payload: LessonScheduleEntryCreate,
) -> LessonScheduleEntryRead:
    week = _get_owned_week(session, week_id, user_id)
    task = session.get(Task, payload.task_id)
    if task is None or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    entry = LessonScheduleEntry(
        week_schedule_id=week.id,
        task_id=payload.task_id,
        day_of_week=payload.day_of_week,
        class_period=payload.class_period,
        notes=payload.notes,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return LessonScheduleEntryRead(
        id=entry.id,
        week_schedule_id=entry.week_schedule_id,
        task_id=entry.task_id,
        day_of_week=entry.day_of_week,
        class_period=entry.class_period,
        notes=entry.notes,
        task_title=task.title,
        task_subject=task.subject,
        task_grade=task.grade,
        created_at=entry.created_at,
    )


def update_entry(
    session: Session, entry_id: str, user_id: str, payload: LessonScheduleEntryUpdate,
) -> LessonScheduleEntryRead:
    entry = session.get(LessonScheduleEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    # Verify ownership via week → semester → user
    week = session.get(WeekSchedule, entry.week_schedule_id)
    if week is None:
        raise HTTPException(status_code=404, detail="Week not found")
    _get_owned_semester(session, week.semester_id, user_id)

    if payload.day_of_week is not None:
        entry.day_of_week = payload.day_of_week
    if payload.class_period is not None:
        entry.class_period = payload.class_period
    if payload.notes is not None:
        entry.notes = payload.notes

    task = session.get(Task, entry.task_id)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return LessonScheduleEntryRead(
        id=entry.id,
        week_schedule_id=entry.week_schedule_id,
        task_id=entry.task_id,
        day_of_week=entry.day_of_week,
        class_period=entry.class_period,
        notes=entry.notes,
        task_title=task.title if task else "",
        task_subject=task.subject if task else "",
        task_grade=task.grade if task else "",
        created_at=entry.created_at,
    )


def delete_entry(session: Session, entry_id: str, user_id: str) -> None:
    entry = session.get(LessonScheduleEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    week = session.get(WeekSchedule, entry.week_schedule_id)
    if week is not None:
        _get_owned_semester(session, week.semester_id, user_id)
    session.delete(entry)
    session.commit()


def update_week(session: Session, week_id: str, user_id: str, payload: WeekScheduleUpdate) -> WeekScheduleRead:
    week = _get_owned_week(session, week_id, user_id)
    if payload.label is not None:
        week.label = payload.label
    if payload.notes is not None:
        week.notes = payload.notes
    week.updated_at = datetime.now(timezone.utc)
    session.add(week)
    session.commit()
    session.refresh(week)
    return WeekScheduleRead(
        id=week.id,
        semester_id=week.semester_id,
        week_number=week.week_number,
        label=week.label,
        start_date=week.start_date,
        end_date=week.end_date,
        notes=week.notes,
    )


def _get_owned_semester(session: Session, semester_id: str, user_id: str) -> Semester:
    semester = session.get(Semester, semester_id)
    if semester is None or semester.user_id != user_id:
        raise HTTPException(status_code=404, detail="Semester not found")
    return semester


def _get_owned_week(session: Session, week_id: str, user_id: str) -> WeekSchedule:
    week = session.get(WeekSchedule, week_id)
    if week is None:
        raise HTTPException(status_code=404, detail="Week not found")
    _get_owned_semester(session, week.semester_id, user_id)
    return week


def _serialize_semester(s: Semester) -> SemesterRead:
    return SemesterRead(
        id=s.id,
        name=s.name,
        start_date=s.start_date,
        end_date=s.end_date,
        grade=s.grade,
        subject=s.subject,
        week_count=s.week_count,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )
