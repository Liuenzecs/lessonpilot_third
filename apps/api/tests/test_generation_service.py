from __future__ import annotations

from app.services.generation_service import _get_section_specs, _validate_section_value


def _get_spec(doc_type: str, section_name: str):
    return next(item for item in _get_section_specs(doc_type) if item["name"] == section_name)


def test_validate_section_value_normalizes_objectives_variants():
    spec = _get_spec("lesson_plan", "objectives")

    value = {
        "知识与技能": "理解文本主要内容",
        "能力": "能够概括人物形象",
        "情感态度与价值观": "感受作品情感",
    }

    objectives = _validate_section_value(value, spec)

    assert [item.dimension for item in objectives] == ["knowledge", "ability", "emotion"]
    assert objectives[0].content == "理解文本主要内容"


def test_validate_section_value_normalizes_assessment_variants():
    spec = _get_spec("study_guide", "collaboration")

    value = {
        "questions": [
            {
                "type": "简答题",
                "question": "结合文本，说说人物的性格特点。",
                "reference_answer": "可从语言、动作、神态等角度作答。",
                "explanation": "围绕文本细节组织答案即可。",
            }
        ]
    }

    items = _validate_section_value(value, spec)

    assert len(items) == 1
    assert items[0].level == "B"
    assert items[0].item_type == "short_answer"
    assert items[0].prompt == "结合文本，说说人物的性格特点。"
    assert items[0].answer == "可从语言、动作、神态等角度作答。"
