from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import delete as sa_delete
from sqlmodel import Session, select

from app.core.security import hash_password, verify_password
from app.models import (
    AuthToken,
    Document,
    DocumentSnapshot,
    Feedback,
    Task,
    TeacherStyleProfile,
    User,
)
from app.schemas.account import (
    AccountChangePasswordPayload,
    AccountDeletePayload,
    AccountRead,
    AccountUpdatePayload,
    FeedbackCreatePayload,
    FeedbackRead,
)
from app.services.auth_service import issue_verification_token, validate_password_strength


def serialize_account(user: User) -> AccountRead:
    return AccountRead(
        id=user.id,
        email=user.email,
        name=user.name,
        role=getattr(user, "role", "teacher"),
        email_verified=user.email_verified,
        email_verified_at=user.email_verified_at,
        created_at=user.created_at,
    )


def update_account_profile(session: Session, user: User, payload: AccountUpdatePayload) -> tuple[User, str | None]:
    next_name = payload.name.strip() if payload.name is not None else user.name
    next_email = payload.email.strip().lower() if payload.email is not None else user.email
    email_changed = next_email != user.email

    if email_changed:
        existing_user = session.exec(select(User).where(User.email == next_email, User.id != user.id)).first()
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user.name = next_name
    user.email = next_email
    if email_changed:
        user.email_verified = False
        user.email_verified_at = None

    session.add(user)
    session.commit()
    session.refresh(user)

    verification_token = issue_verification_token(session, user) if email_changed else None
    return user, verification_token


def change_account_password(session: Session, user: User, payload: AccountChangePasswordPayload) -> None:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
    validate_password_strength(payload.new_password)
    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    user.password_hash = hash_password(payload.new_password)
    session.add(user)
    session.commit()


def create_feedback(session: Session, user: User, payload: FeedbackCreatePayload) -> Feedback:
    feedback = Feedback(
        user_id=user.id,
        mood=payload.mood,
        message=payload.message.strip(),
        page_path=payload.page_path.strip() if payload.page_path else None,
    )
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


def serialize_feedback(feedback: Feedback) -> FeedbackRead:
    return FeedbackRead(
        id=feedback.id,
        user_id=feedback.user_id,
        mood=feedback.mood,
        message=feedback.message,
        page_path=feedback.page_path,
        created_at=feedback.created_at,
    )


def export_account_data(session: Session, user: User) -> bytes:
    tasks = session.exec(select(Task).where(Task.user_id == user.id).order_by(Task.updated_at.desc())).all()
    documents = session.exec(
        select(Document).where(Document.user_id == user.id).order_by(Document.updated_at.desc())
    ).all()
    document_ids = [document.id for document in documents]
    if document_ids:
        snapshots = session.exec(
            select(DocumentSnapshot)
            .where(DocumentSnapshot.document_id.in_(document_ids))
            .order_by(DocumentSnapshot.created_at.desc())
        ).all()
    else:
        snapshots = []
    feedback_entries = session.exec(
        select(Feedback).where(Feedback.user_id == user.id).order_by(Feedback.created_at.desc())
    ).all()
    style_profile = session.exec(select(TeacherStyleProfile).where(TeacherStyleProfile.user_id == user.id)).first()

    payload = {
        "exported_at": datetime.now(UTC).isoformat(),
        "user": serialize_account(user).model_dump(mode="json"),
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "subject": task.subject,
                "grade": task.grade,
                "topic": task.topic,
                "requirements": task.requirements,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in tasks
        ],
        "documents": [
            {
                "id": document.id,
                "task_id": document.task_id,
                "title": document.title,
                "doc_type": document.doc_type,
                "version": document.version,
                "content": document.content,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
            }
            for document in documents
        ],
        "snapshots": [
            {
                "id": snapshot.id,
                "document_id": snapshot.document_id,
                "version": snapshot.version,
                "source": snapshot.source,
                "content": snapshot.content,
                "created_at": snapshot.created_at.isoformat(),
            }
            for snapshot in snapshots
        ],
        "style_profile": {
            "enabled": style_profile.enabled,
            "objective_style": style_profile.objective_style,
            "process_style": style_profile.process_style,
            "school_wording": style_profile.school_wording,
            "activity_preferences": style_profile.activity_preferences,
            "avoid_phrases": style_profile.avoid_phrases,
            "sample_count": style_profile.sample_count,
            "updated_at": style_profile.updated_at.isoformat(),
        } if style_profile else None,
        "feedback": [serialize_feedback(entry).model_dump(mode="json") for entry in feedback_entries],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def delete_account(session: Session, user: User, payload: AccountDeletePayload) -> None:
    if payload.confirm_text.strip().upper() != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Please confirm with "DELETE"',
        )

    # Bulk-delete all user data using batch DELETE statements (avoids loading records into memory)
    uid = user.id
    task_ids = session.exec(select(Task.id).where(Task.user_id == uid)).all()
    if task_ids:
        doc_ids = session.exec(select(Document.id).where(Document.task_id.in_(task_ids))).all()
        if doc_ids:
            session.exec(sa_delete(DocumentSnapshot).where(DocumentSnapshot.document_id.in_(doc_ids)))
            session.exec(sa_delete(Document).where(Document.id.in_(doc_ids)))
        session.exec(sa_delete(Task).where(Task.id.in_(task_ids)))

    session.exec(sa_delete(Feedback).where(Feedback.user_id == uid))
    session.exec(sa_delete(AuthToken).where(AuthToken.user_id == uid))
    session.exec(sa_delete(TeacherStyleProfile).where(TeacherStyleProfile.user_id == uid))

    session.delete(user)
    session.commit()
