from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models import Task, TeachingPackage
from app.schemas.content import AssessmentItem, LearningProcess, LessonPlanContent, StudyGuideContent, StudyGuideHeader
from app.schemas.teaching_package import PptSlideDraft, TalkScriptDraft, TeachingPackageContent, TeachingPackageRead
from app.services.document_service import get_owned_document, load_content


def generate_teaching_package(session: Session, document_id: str, user_id: str) -> TeachingPackageRead:
    document = get_owned_document(session, document_id, user_id)
    task = session.exec(select(Task).where(Task.id == document.task_id, Task.user_id == user_id)).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    content = load_content(document)
    if not isinstance(content, LessonPlanContent):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上课包需要从教案生成")
    _ensure_ready_for_package(content)

    package_content = TeachingPackageContent(
        study_guide=_build_study_guide(task, content),
        ppt_outline=_build_ppt_outline(task, content),
        talk_script=_build_talk_script(task, content),
    )
    package = TeachingPackage(
        user_id=user_id,
        task_id=task.id,
        document_id=document.id,
        title=f"{task.title}上课包",
        status="pending",
        content=package_content.model_dump(by_alias=True),
    )
    session.add(package)
    session.commit()
    session.refresh(package)
    return _serialize_package(package)


def list_teaching_packages(session: Session, document_id: str, user_id: str) -> list[TeachingPackageRead]:
    statement = (
        select(TeachingPackage)
        .where(TeachingPackage.document_id == document_id, TeachingPackage.user_id == user_id)
        .order_by(TeachingPackage.created_at.desc())
    )
    return [_serialize_package(package) for package in session.exec(statement).all()]


def _ensure_ready_for_package(content: LessonPlanContent) -> None:
    missing: list[str] = []
    if content.objectives_status != "confirmed" or not content.objectives:
        missing.append("教学目标")
    has_key_points = bool(content.key_points.key_points or content.key_points.difficulties)
    if content.key_points_status != "confirmed" or not has_key_points:
        missing.append("教学重难点")
    if content.teaching_process_status != "confirmed" or len(content.teaching_process) < 2:
        missing.append("教学过程")
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"请先确认{ '、'.join(missing) }后再生成上课包。",
        )


def _build_study_guide(task: Task, content: LessonPlanContent) -> StudyGuideContent:
    objectives = [f"我能{_student_objective(item.content)}" for item in content.objectives[:3]]
    key_difficulties = content.key_points.difficulties or content.key_points.key_points[:2]
    self_study = [
        AssessmentItem(level="A", item_type="short_answer", prompt=f"用一句话概括“{step.phase}”要解决的问题。")
        for step in content.teaching_process[:2]
    ]
    collaboration = [
        AssessmentItem(
            level="B",
            item_type="short_answer",
            prompt=f"围绕“{content.key_points.key_points[0]}”找出文本依据并说明理由。"
            if content.key_points.key_points
            else "结合课文内容，说明本课最值得讨论的一个问题。",
        )
    ]
    assessment = [
        AssessmentItem(
            level="A",
            item_type="short_answer",
            prompt=f"本课学习后，你能怎样说明“{objective.content}”？",
            answer="结合课堂学习内容作答。",
            analysis="答案应能对应学习目标，并引用文本或课堂活动中的证据。",
        )
        for objective in content.objectives[:2]
    ]
    return StudyGuideContent(
        header=StudyGuideHeader(title=f"{task.topic}学案", subject=task.subject, grade=task.grade),
        learning_objectives=objectives,
        learning_objectives_status="pending",
        key_difficulties=key_difficulties,
        key_difficulties_status="pending",
        prior_knowledge=content.preparation[:3],
        prior_knowledge_status="pending",
        learning_process=LearningProcess(self_study=self_study, collaboration=collaboration, presentation=[]),
        self_study_status="pending",
        collaboration_status="pending",
        presentation_status="pending",
        assessment=assessment,
        assessment_status="pending",
    )


def _build_ppt_outline(task: Task, content: LessonPlanContent) -> list[PptSlideDraft]:
    slides = [
        PptSlideDraft(
            title=task.topic,
            bullets=[f"{task.grade} · {task.subject}", f"第 {task.class_hour} 课时"],
            speaker_note="开场点明课题和本节学习任务。",
        ),
        PptSlideDraft(
            title="学习目标",
            bullets=[item.content for item in content.objectives[:3]],
            speaker_note="用学生听得懂的话说明本节课要完成什么。",
        ),
    ]
    for step in content.teaching_process:
        slides.append(
            PptSlideDraft(
                title=step.phase,
                bullets=[step.teacher_activity, step.student_activity],
                activity=step.student_activity,
                speaker_note=step.design_intent,
            )
        )
    if content.board_design:
        slides.append(PptSlideDraft(title="板书与小结", bullets=[content.board_design], speaker_note="收束课堂结构。"))
    return slides


def _build_talk_script(task: Task, content: LessonPlanContent) -> TalkScriptDraft:
    questions = [
        f"在“{step.phase}”中，你认为最关键的文本依据是什么？"
        for step in content.teaching_process[:4]
    ]
    transitions = [
        f"完成“{step.phase}”后，我们继续看下一个问题。"
        for step in content.teaching_process[1:4]
    ]
    return TalkScriptDraft(
        opening=f"同学们，今天我们学习{task.topic}。请先带着本节目标进入文本。",
        questions=questions,
        transitions=transitions,
        closing="请用一两句话回顾本节课的收获，并把仍不确定的问题标出来。",
    )


def _student_objective(value: str) -> str:
    value = value.strip()
    value = value.removeprefix("能够").removeprefix("能").removeprefix("掌握")
    return value or "说出本节课的核心内容"


def _serialize_package(package: TeachingPackage) -> TeachingPackageRead:
    return TeachingPackageRead(
        id=package.id,
        task_id=package.task_id,
        document_id=package.document_id,
        title=package.title,
        status=package.status,
        content=TeachingPackageContent.model_validate(package.content),
        created_at=package.created_at,
        updated_at=package.updated_at,
    )
