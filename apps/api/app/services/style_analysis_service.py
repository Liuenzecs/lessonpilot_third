"""风格分析服务 — 样本采集 + 自动分析 + few-shot 提示。"""

from __future__ import annotations

from sqlmodel import Session, select

from app.models.style_sample import StyleSample
from app.models.teacher_style_profile import TeacherStyleProfile


def collect_style_sample(
    session: Session,
    user_id: str,
    document_id: str,
    subject: str,
    grade: str,
    section_key: str,
    original_content: str | None,
    confirmed_content: str | None,
) -> StyleSample | None:
    """当教师确认 section 时，采集风格样本。"""
    if not original_content or not confirmed_content:
        return None

    # Compute simple diff summary
    diff_summary = _compute_diff_summary(original_content, confirmed_content)
    if not diff_summary:
        return None

    sample = StyleSample(
        user_id=user_id,
        document_id=document_id,
        subject=subject,
        grade=grade,
        section_key=section_key,
        original_content=original_content[:3000],
        confirmed_content=confirmed_content[:3000],
        diff_summary=diff_summary[:500],
    )
    session.add(sample)

    # Update sample_count on style profile
    profile_stmt = select(TeacherStyleProfile).where(
        TeacherStyleProfile.user_id == user_id
    )
    profile = session.exec(profile_stmt).first()
    if profile:
        profile.sample_count = (profile.sample_count or 0) + 1
        session.add(profile)

    session.commit()
    return sample


def get_few_shot_examples(
    session: Session, user_id: str, subject: str, limit: int = 3
) -> str:
    """获取教师最近确认的风格样本作为 few-shot 示例。"""
    stmt = (
        select(StyleSample)
        .where(
            StyleSample.user_id == user_id,
            StyleSample.subject == subject,
            StyleSample.extracted_patterns.isnot(None),
        )
        .order_by(StyleSample.created_at.desc())
        .limit(limit)
    )
    rows = session.exec(stmt).all()
    if not rows or len(rows) < 3:
        return ""

    examples: list[str] = []
    for sample in rows:
        patterns = sample.extracted_patterns or {}
        example_parts = [f"section: {sample.section_key}"]
        if patterns.get("preferred_phrasing"):
            example_parts.append(f"偏好措辞: {patterns['preferred_phrasing']}")
        if patterns.get("activity_style"):
            example_parts.append(f"活动风格: {patterns['activity_style']}")
        if sample.diff_summary:
            example_parts.append(f"修改摘要: {sample.diff_summary}")
        examples.append("\n".join(example_parts))

    if not examples:
        return ""

    return (
        "【Few-shot 风格示例】（以下是你之前的备课风格，请保持一致）\n\n"
        + "\n\n---\n\n".join(examples)
    )


def suggest_style_updates(session: Session, user_id: str) -> dict | None:
    """分析样本，生成风格建议。当样本数 >= 5 时触发。"""
    stmt = (
        select(StyleSample)
        .where(StyleSample.user_id == user_id)
        .order_by(StyleSample.created_at.desc())
        .limit(20)
    )
    rows = session.exec(stmt).all()
    if len(rows) < 5:
        return None

    # Extract common patterns from diff summaries
    all_diffs = [r.diff_summary for r in rows if r.diff_summary]
    activity_keywords = [
        "活动", "讨论", "小组", "朗读", "练习", "探究", "展示", "讲解", "提问", "板书"
    ]
    preference_hints: list[str] = []

    for kw in activity_keywords:
        count = sum(1 for diff in all_diffs if diff and kw in diff)
        if count >= 3:
            preference_hints.append(f"倾向于调整{kw}相关内容的细节")

    return {
        "sample_count": len(rows),
        "suggestions": (
            "基于你最近的 " + str(len(rows)) + " 次备课修改，AI 观察到以下风格倾向：\n"
            + "\n".join(f"- {h}" for h in preference_hints)
        ) if preference_hints else "暂未收集到足够的风格信号，继续使用会逐步学习你的偏好。",
    }


def _compute_diff_summary(original: str, confirmed: str) -> str:
    """简单的 diff 摘要：长度变化 + 关键词检测。"""
    orig_len = len(original)
    conf_len = len(confirmed)

    parts: list[str] = []
    if conf_len > orig_len * 1.15:
        parts.append("显著扩充内容")
    elif conf_len < orig_len * 0.85:
        parts.append("精简了内容")

    # Check for common editing patterns
    if "讨论" not in original and "讨论" in confirmed:
        parts.append("增加了讨论活动")
    if "朗读" not in original and "朗读" in confirmed:
        parts.append("增加了朗读环节")
    if "小组" not in original and "小组" in confirmed:
        parts.append("增加了小组合作")
    if "板书" not in original and "板书" in confirmed:
        parts.append("补充了板书相关")
    if "练习" not in original and "练习" in confirmed:
        parts.append("增加了练习内容")

    return "; ".join(parts) if parts else ""
