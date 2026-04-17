"""Template service + AI quality validation tests."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient


class TestTemplateEndpoints:
    def test_list_templates_empty(self, client: TestClient) -> None:
        resp = client.get("/api/v1/templates/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_and_read_template(self, client: TestClient, auth_headers: dict) -> None:
        payload = {
            "name": "测试教案模板",
            "subject": "语文",
            "grade": "通用",
            "template_type": "lesson_plan",
            "description": "测试模板描述",
            "sections": [
                {
                    "section_name": "教学目标",
                    "order": 1,
                    "prompt_hints": "写出 2-3 条教学目标",
                },
            ],
        }
        resp = client.post("/api/v1/templates/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "测试教案模板"
        assert data["id"]
        template_id = data["id"]

        resp = client.get(f"/api/v1/templates/{template_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "测试教案模板"

    def test_list_templates_filter_by_subject(self, client: TestClient, auth_headers: dict) -> None:
        for name in ["模板A", "模板B"]:
            client.post(
                "/api/v1/templates/",
                json={
                    "name": name,
                    "subject": "语文",
                    "grade": "通用",
                    "template_type": "lesson_plan",
                },
                headers=auth_headers,
            )

        resp = client.get("/api/v1/templates/?subject=语文")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        resp = client.get("/api/v1/templates/?subject=数学")
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_get_template_sections(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.post(
            "/api/v1/templates/",
            json={
                "name": "有分节的模板",
                "subject": "语文",
                "grade": "通用",
                "template_type": "lesson_plan",
                "sections": [
                    {"section_name": "教学目标", "order": 1, "prompt_hints": "目标提示"},
                    {"section_name": "教学过程", "order": 2, "prompt_hints": "过程提示"},
                ],
            },
            headers=auth_headers,
        )
        template_id = resp.json()["id"]

        resp = client.get(f"/api/v1/templates/{template_id}/sections")
        assert resp.status_code == 200
        sections = resp.json()
        assert len(sections) == 2
        assert sections[0]["section_name"] == "教学目标"
        assert sections[0]["prompt_hints"] == "目标提示"

    def test_update_template(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.post(
            "/api/v1/templates/",
            json={
                "name": "原名称",
                "subject": "语文",
                "grade": "通用",
                "template_type": "lesson_plan",
            },
            headers=auth_headers,
        )
        template_id = resp.json()["id"]

        resp = client.patch(
            f"/api/v1/templates/{template_id}",
            json={"name": "新名称"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "新名称"

    def test_template_not_found(self, client: TestClient) -> None:
        resp = client.get("/api/v1/templates/nonexistent-id")
        assert resp.status_code == 404


class TestTaskWithTemplate:
    def test_create_task_with_template_id(self, client: TestClient, auth_headers: dict) -> None:
        tpl_resp = client.post(
            "/api/v1/templates/",
            json={
                "name": "测试模板",
                "subject": "语文",
                "grade": "通用",
                "template_type": "lesson_plan",
                "sections": [
                    {"section_name": "教学目标", "order": 1, "prompt_hints": "写出教学目标"},
                ],
            },
            headers=auth_headers,
        )
        template_id = tpl_resp.json()["id"]

        resp = client.post(
            "/api/v1/tasks/",
            json={
                "subject": "语文",
                "grade": "七年级",
                "topic": "测试课题",
                "template_id": template_id,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["template_id"] == template_id

    def test_create_task_without_template_id(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.post(
            "/api/v1/tasks/",
            json={
                "subject": "语文",
                "grade": "七年级",
                "topic": "无模板课题",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["template_id"] is None

    def test_duplicate_task_copies_template_id(self, client: TestClient, auth_headers: dict) -> None:
        tpl_resp = client.post(
            "/api/v1/templates/",
            json={
                "name": "复制测试模板",
                "subject": "语文",
                "grade": "通用",
                "template_type": "lesson_plan",
            },
            headers=auth_headers,
        )
        template_id = tpl_resp.json()["id"]

        task_resp = client.post(
            "/api/v1/tasks/",
            json={
                "subject": "语文",
                "grade": "七年级",
                "topic": "原始课题",
                "template_id": template_id,
            },
            headers=auth_headers,
        )
        task_id = task_resp.json()["id"]

        dup_resp = client.post(
            f"/api/v1/tasks/{task_id}/duplicate",
            headers=auth_headers,
        )
        assert dup_resp.status_code == 201
        assert dup_resp.json()["template_id"] == template_id


class TestAIQualityValidation:
    """Test the _validate_generated_content function."""

    def test_validate_good_lesson_plan(self) -> None:
        from app.services.generation_service import _validate_generated_content
        from app.schemas.content import LessonPlanContent

        content = LessonPlanContent.model_validate({
            "doc_type": "lesson_plan",
            "header": {"title": "测试", "subject": "语文", "grade": "七年级"},
            "objectives": [{"dimension": "knowledge", "content": "掌握基础"}],
            "key_points": {"key_points": ["重点1"], "difficulties": ["难点1"]},
            "teaching_process": [
                {"phase": "导入", "duration": 5, "teacher_activity": "提问", "student_activity": "思考", "design_intent": "激发兴趣"},
                {"phase": "新授", "duration": 20, "teacher_activity": "讲解", "student_activity": "听讲", "design_intent": "传授知识"},
                {"phase": "练习", "duration": 10, "teacher_activity": "引导", "student_activity": "练习", "design_intent": "巩固"},
            ],
            "board_design": "板书",
            "reflection": "",
        })
        warnings = _validate_generated_content(content)
        assert len(warnings) == 0

    def test_validate_lesson_plan_few_phases(self) -> None:
        from app.services.generation_service import _validate_generated_content
        from app.schemas.content import LessonPlanContent

        content = LessonPlanContent.model_validate({
            "doc_type": "lesson_plan",
            "header": {"title": "测试", "subject": "语文", "grade": "七年级"},
            "objectives": [{"dimension": "knowledge", "content": "掌握基础"}],
            "key_points": {"keyPoints": ["重点1"], "difficulties": []},
            "teaching_process": [
                {"phase": "导入", "duration": 5, "teacher_activity": "提问", "student_activity": "思考", "design_intent": "激发兴趣"},
            ],
            "board_design": "板书",
            "reflection": "",
        })
        warnings = _validate_generated_content(content)
        assert any("1 个环节" in w for w in warnings)

    def test_validate_study_guide_empty_self_study(self) -> None:
        from app.services.generation_service import _validate_generated_content
        from app.schemas.content import StudyGuideContent

        content = StudyGuideContent.model_validate({
            "doc_type": "study_guide",
            "header": {"title": "测试", "subject": "语文", "grade": "七年级"},
            "learning_objectives": ["我能理解课文"],
            "key_difficulties": ["难点1"],
            "prior_knowledge": ["知识1"],
            "learning_process": {"selfStudy": [], "collaboration": [], "presentation": []},
            "assessment": [{"level": "A", "itemType": "choice", "prompt": "题目", "options": ["A", "B"], "answer": "A", "analysis": "解析"}],
            "extension": [],
            "self_reflection": "",
        })
        warnings = _validate_generated_content(content)
        assert any("自主学习" in w for w in warnings)


class TestPromptHintsInjection:
    """Test that prompt_hints are correctly loaded and formatted."""

    def test_load_prompt_hints_no_template(self) -> None:
        from sqlmodel import Session, create_engine, SQLModel
        from app.services.generation_service import _load_prompt_hints

        engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            result = _load_prompt_hints(session, None, "lesson_plan")
            assert result == ""

    def test_load_prompt_hints_with_template(self) -> None:
        from sqlmodel import Session, create_engine, SQLModel
        from app.services.generation_service import _load_prompt_hints
        from app.models.template import Template, TemplateSection

        engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            tpl = Template(
                name="测试",
                subject="语文",
                grade="通用",
                template_type="lesson_plan",
                is_public=True,
                content={},
            )
            session.add(tpl)
            session.flush()

            section = TemplateSection(
                template_id=tpl.id,
                section_name="教学目标",
                order=1,
                prompt_hints="写出 2-3 条目标",
            )
            session.add(section)
            session.commit()

            result = _load_prompt_hints(session, tpl.id, "lesson_plan")
            assert "教学目标" in result
            assert "写出 2-3 条目标" in result
