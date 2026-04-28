"""题库服务测试 — 通过 API 端点。"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.models.question import Question  # noqa: F401 确保模型注册到 SQLModel.metadata


class TestQuestionChapters:
    def test_returns_empty_when_no_questions(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.get("/api/v1/questions/chapters", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_chapters_after_seed(self, client: TestClient, auth_headers: dict) -> None:
        seed_resp = client.post("/api/v1/questions/seed", headers=auth_headers)
        assert seed_resp.status_code == 200

        resp = client.get("/api/v1/questions/chapters", headers=auth_headers)
        assert resp.status_code == 200
        chapters = resp.json()
        assert len(chapters) > 0
        chapter_names = [c["chapter"] for c in chapters]
        assert "春" in chapter_names


class TestSearchQuestions:
    def test_filters_by_chapter(self, client: TestClient, auth_headers: dict) -> None:
        client.post("/api/v1/questions/seed", headers=auth_headers)
        resp = client.get("/api/v1/questions/?chapter=春", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        for item in data["items"]:
            assert item["chapter"] == "春"

    def test_filters_by_difficulty(self, client: TestClient, auth_headers: dict) -> None:
        client.post("/api/v1/questions/seed", headers=auth_headers)
        resp = client.get("/api/v1/questions/?chapter=春&difficulty=B", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        for item in data["items"]:
            assert item["difficulty"] == "B"

    def test_filters_by_type(self, client: TestClient, auth_headers: dict) -> None:
        client.post("/api/v1/questions/seed", headers=auth_headers)
        resp = client.get("/api/v1/questions/?question_type=choice", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] > 0
        for item in data["items"]:
            assert item["question_type"] == "choice"

    def test_search_without_auth_fails(self, client: TestClient) -> None:
        resp = client.get("/api/v1/questions/")
        assert resp.status_code == 401


class TestSeedQuestions:
    def test_seed_inserts_data(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.post("/api/v1/questions/seed", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["inserted"] > 0

    def test_seed_is_idempotent(self, client: TestClient, auth_headers: dict) -> None:
        resp1 = client.post("/api/v1/questions/seed", headers=auth_headers)
        count1 = resp1.json()["inserted"]
        resp2 = client.post("/api/v1/questions/seed", headers=auth_headers)
        count2 = resp2.json()["inserted"]
        assert count2 == 0  # 第二次不应重复插入


class TestGetQuestion:
    def test_get_question_by_id(self, client: TestClient, auth_headers: dict) -> None:
        client.post("/api/v1/questions/seed", headers=auth_headers)
        list_resp = client.get("/api/v1/questions/?limit=1", headers=auth_headers)
        question_id = list_resp.json()["items"][0]["id"]

        resp = client.get(f"/api/v1/questions/{question_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == question_id

    def test_returns_404_for_missing(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.get("/api/v1/questions/nonexistent-id", headers=auth_headers)
        assert resp.status_code == 404
