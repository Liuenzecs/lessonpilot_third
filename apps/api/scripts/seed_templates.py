import asyncio
import json
import logging
from sqlalchemy import select
from app.core.db import async_session_factory
from app.models.template import Template, TemplateSection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed():
    async with async_session_factory() as session:
        # Check if templates already exist
        stmt = select(Template).where(Template.name == "标准语文教案（新手版）")
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            logger.info("Templates already seeded. Exiting.")
            return

        logger.info("Seeding templates...")

        # 1. 语文教案模板
        lesson_plan = Template(
            name="标准语文教案（新手版）",
            subject="语文",
            grade="通用",
            description="基于新课标的标准化语文教案模板，适合公立校新手教师使用。",
            template_type="lesson_plan",
            is_public=True,
            content={
                "base_info": {
                    "title": "标准语文教案",
                    "subject": "语文",
                    "lesson_type": "新授课",
                    "duration": "1课时"
                }
            }
        )
        session.add(lesson_plan)
        await session.commit()
        await session.refresh(lesson_plan)

        lp_sections = [
            TemplateSection(
                template_id=lesson_plan.id,
                section_name="教学目标",
                order=1,
                description="核心素养或三维目标"
            ),
            TemplateSection(
                template_id=lesson_plan.id,
                section_name="教学重难点",
                order=2,
                description="本节课的重点和难点分析"
            ),
            TemplateSection(
                template_id=lesson_plan.id,
                section_name="教学过程",
                order=3,
                description="含教师活动、学生活动和设计意图"
            ),
            TemplateSection(
                template_id=lesson_plan.id,
                section_name="板书设计",
                order=4,
                description="黑板排版和核心梳理"
            ),
        ]
        session.add_all(lp_sections)

        # 2. 语文学案模板
        study_guide = Template(
            name="标准语文学案（全流程版）",
            subject="语文",
            grade="通用",
            description="完整的导学案，包含预习、探究、测评等环节。",
            template_type="study_guide",
            is_public=True,
            content={
                "base_info": {
                    "title": "标准语文学案",
                    "subject": "语文"
                }
            }
        )
        session.add(study_guide)
        await session.commit()
        await session.refresh(study_guide)

        sg_sections = [
            TemplateSection(
                template_id=study_guide.id,
                section_name="学习目标",
                order=1,
                description="从学生视角的我能...目标"
            ),
            TemplateSection(
                template_id=study_guide.id,
                section_name="知识链接",
                order=2,
                description="前置知识或背景资料"
            ),
            TemplateSection(
                template_id=study_guide.id,
                section_name="自主学习",
                order=3,
                description="A/B级基础任务"
            ),
            TemplateSection(
                template_id=study_guide.id,
                section_name="合作探究",
                order=4,
                description="核心重难点突破"
            ),
            TemplateSection(
                template_id=study_guide.id,
                section_name="达标测评",
                order=5,
                description="巩固练习"
            ),
        ]
        session.add_all(sg_sections)

        await session.commit()
        logger.info("Templates seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
