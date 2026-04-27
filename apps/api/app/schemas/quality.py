from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Readiness = Literal["ready", "needs_fixes", "blocked"]
QualitySeverity = Literal["blocker", "warning", "suggestion"]


class QualityIssue(BaseModel):
    severity: QualitySeverity
    section: str | None = None
    message: str
    suggestion: str = ""


class AlignmentMapItem(BaseModel):
    objective: str
    process_matches: list[str] = []
    assessment_matches: list[str] = []
    status: Literal["covered", "partial", "missing"] = "missing"


class QualityCheckResponse(BaseModel):
    readiness: Readiness
    summary: str
    issues: list[QualityIssue]
    warnings: list[QualityIssue]
    suggestions: list[QualityIssue]
    alignment_map: list[AlignmentMapItem] = []
