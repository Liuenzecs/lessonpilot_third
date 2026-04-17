"""导入语文教案/学案标准模板的种子数据脚本。

用法：cd apps/api && python -m scripts.seed_templates
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# 确保 app 包可导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from app.core.db import get_engine
from app.models.template import Template, TemplateSection

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 模板数据定义
# ---------------------------------------------------------------------------

LESSON_PLAN_TEMPLATES: list[dict] = [
    {
        "name": "标准语文教案（公立校版）",
        "subject": "语文",
        "grade": "通用",
        "description": "基于新课标的标准化语文教案模板，适合公立校新手教师。包含完整的教学目标、重难点、教学过程和板书设计。",
        "template_type": "lesson_plan",
        "sections": [
            {"section_name": "教学目标", "order": 1, "description": "核心素养或三维目标", "prompt_hints": "写出 2-3 条教学目标，涵盖知识与能力、过程与方法、情感态度价值观三个维度。每条目标应具体、可检测。"},
            {"section_name": "教学重难点", "order": 2, "description": "本节课的重点和难点", "prompt_hints": "列出 2-3 个教学重点和 1-2 个教学难点。重点应与教学目标直接对应，难点应说明为什么学生容易困惑。"},
            {"section_name": "教学准备", "order": 3, "description": "教学资源和工具", "prompt_hints": "列出 3-5 项教学准备，包括课件、教材、音频视频等资源。"},
            {"section_name": "教学过程", "order": 4, "description": "完整教学流程", "prompt_hints": "设计至少 4 个教学环节：导入新课（5分钟，联系学生已有经验）、新授知识（15-20分钟）、巩固练习（10分钟）、课堂小结（5分钟）。每个环节包含教师活动、学生活动和设计意图。"},
            {"section_name": "板书设计", "order": 5, "description": "板书排版", "prompt_hints": "设计清晰的板书结构，突出课题、重点概念和关键词。"},
        ],
    },
    {
        "name": "简化语文教案（家教版）",
        "subject": "语文",
        "grade": "通用",
        "description": "精简版教案，适合大学生家教快速备课。重点突出教学步骤和练习设计。",
        "template_type": "lesson_plan",
        "sections": [
            {"section_name": "教学目标", "order": 1, "description": "核心教学目标", "prompt_hints": "写出 1-2 条简洁的核心目标，聚焦知识掌握和基本技能。"},
            {"section_name": "教学重难点", "order": 2, "description": "重点和难点", "prompt_hints": "简洁列出 1-2 个重点即可。"},
            {"section_name": "教学过程", "order": 3, "description": "教学流程", "prompt_hints": "设计 2-3 个环节即可：知识讲解（15分钟）、练习巩固（15分钟）、总结布置作业（5分钟）。侧重讲练结合。"},
            {"section_name": "板书设计", "order": 4, "description": "板书要点", "prompt_hints": "简要列出核心知识点即可。"},
        ],
    },
    {
        "name": "通用语文教案（培训机构版）",
        "subject": "语文",
        "grade": "通用",
        "description": "机构通用的中等规范教案模板，兼顾教学效果和备课效率。",
        "template_type": "lesson_plan",
        "sections": [
            {"section_name": "教学目标", "order": 1, "description": "教学目标", "prompt_hints": "写出 2-3 条教学目标，注重能力培养和实际应用。"},
            {"section_name": "教学重难点", "order": 2, "description": "重难点分析", "prompt_hints": "列出 2 个重点和 1-2 个难点，说明突破策略。"},
            {"section_name": "教学准备", "order": 3, "description": "教学资源", "prompt_hints": "列出 2-3 项必要准备。"},
            {"section_name": "教学过程", "order": 4, "description": "教学流程", "prompt_hints": "设计 3-4 个环节：情境导入（3分钟）、新知探究（15分钟）、巩固提升（10分钟）、课堂总结（2分钟）。注重互动和趣味性。"},
            {"section_name": "板书设计", "order": 5, "description": "板书", "prompt_hints": "设计结构化板书，突出知识框架。"},
        ],
    },
]

STUDY_GUIDE_TEMPLATES: list[dict] = [
    {
        "name": "标准语文学案（导学案版）",
        "subject": "语文",
        "grade": "通用",
        "description": "完整的公立校导学案模板，包含预习、探究、展示、测评等环节。",
        "template_type": "study_guide",
        "sections": [
            {"section_name": "学习目标", "order": 1, "description": "学生视角的我能...目标", "prompt_hints": "用'我能...'的口吻写出 2-3 条学习目标，聚焦具体可检测的能力。"},
            {"section_name": "重点难点预测", "order": 2, "description": "预计遇到的困难", "prompt_hints": "列出 1-2 个可能的难点，给出初步思考方向。"},
            {"section_name": "知识链接", "order": 3, "description": "前置知识回顾", "prompt_hints": "回顾与本课相关的 1-2 个已学知识点，帮助学生建立联系。"},
            {"section_name": "自主学习", "order": 4, "description": "A/B 级基础任务", "prompt_hints": "设计 2-3 道基础题（A级填空/选择 + B级简答），帮助学生预习课文核心内容。"},
            {"section_name": "合作探究", "order": 5, "description": "B/C 级深度任务", "prompt_hints": "设计 1-2 道需要小组讨论的探究题（B/C级），引导学生深入理解课文。"},
            {"section_name": "达标测评", "order": 6, "description": "巩固练习", "prompt_hints": "设计 3-4 道测评题（A/B/C级混合），当堂检测学习效果。"},
        ],
    },
    {
        "name": "简化语文学案（家教讲义版）",
        "subject": "语文",
        "grade": "通用",
        "description": "家教用讲义式学案，侧重知识梳理和练习。",
        "template_type": "study_guide",
        "sections": [
            {"section_name": "学习目标", "order": 1, "description": "学习要点", "prompt_hints": "简洁列出 1-2 个本课核心学习目标。"},
            {"section_name": "知识链接", "order": 2, "description": "知识梳理", "prompt_hints": "简要梳理本课涉及的 1-2 个关键知识点。"},
            {"section_name": "自主学习", "order": 3, "description": "基础练习", "prompt_hints": "设计 2-3 道基础练习题，帮助学生掌握核心概念。"},
            {"section_name": "达标测评", "order": 4, "description": "巩固检测", "prompt_hints": "设计 2-3 道检测题，包含一道综合题。"},
        ],
    },
]


def seed() -> None:
    engine = get_engine()

    with Session(engine) as session:
        existing = session.exec(select(Template)).first()
        if existing is not None:
            logger.info("Templates already exist. Skipping seed.")
            return

        logger.info("Seeding templates...")

        all_templates = [
            *LESSON_PLAN_TEMPLATES,
            *STUDY_GUIDE_TEMPLATES,
        ]

        for tpl_data in all_templates:
            template = Template(
                name=tpl_data["name"],
                subject=tpl_data["subject"],
                grade=tpl_data["grade"],
                description=tpl_data["description"],
                template_type=tpl_data["template_type"],
                is_public=True,
                content={},
            )
            session.add(template)
            session.flush()

            for sec_data in tpl_data["sections"]:
                section = TemplateSection(
                    template_id=template.id,
                    section_name=sec_data["section_name"],
                    order=sec_data["order"],
                    description=sec_data.get("description"),
                    prompt_hints=sec_data.get("prompt_hints"),
                )
                session.add(section)

        session.commit()
        logger.info("Seeded %d templates successfully.", len(all_templates))


if __name__ == "__main__":
    seed()
