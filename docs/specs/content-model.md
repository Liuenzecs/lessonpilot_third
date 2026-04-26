# 内容模型规格

## 核心原则

教案/学案结构化 JSON 是 LessonPilot 的中枢。

同一份内容被以下模块共同使用：

- 前端编辑器渲染。
- 后端 AI 生成。
- 后端 section 改写。
- 自动保存。
- Word 导出。
- RAG 引用展示。

## 类型源

前后端必须保持同步：

- `packages/shared-types/src/content.ts`
- `apps/api/app/schemas/content.py`

## Section Status

每个可生成 section 都有状态：

- `pending`：系统生成或改写后，等待老师确认。
- `confirmed`：老师确认后，可进入正式导出。

## LessonPlanContent

主要字段：

- `header`
- `objectives`
- `key_points`
- `preparation`
- `teaching_process`
- `board_design`
- `reflection`
- `section_references`

导出重点：

- `reflection` 默认可留空。
- `teaching_process` 是主体，占真实课堂价值最大。

## StudyGuideContent

主要字段：

- `header`
- `learning_objectives`
- `key_difficulties`
- `prior_knowledge`
- `learning_process`
- `assessment`
- `extension`
- `self_reflection`
- `section_references`

重要约束：

- `self_study`
- `collaboration`
- `presentation`

这三段在前端 section 里展示，但数据必须统一存入 `learning_process`。

## CitationReference

用于保存 RAG 引用元数据：

- `chunk_id`
- `source`
- `title`
- `knowledge_type`
- `chapter`
- `content_snippet`

正文中不保存 `[cite:...]` 脏标记，引用通过 `section_references` 展示。
