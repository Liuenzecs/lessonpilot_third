# Phase 6：迁移与提交闭环

## Summary

本阶段目标是让老师把旧 Word 教案带进 LessonPilot，并在导出前知道“这份能不能交”。Phase 6 聚焦三件事：`.docx` 旧教案导入、结构化预览确认、导出前体检。

## Key Changes

- 后端新增旧教案导入能力：`POST /api/v1/import/lesson-plan/preview` 接收 `.docx`，用 `python-docx` 提取段落和表格，按常见标题映射到 `LessonPlanContent`。
- 后端新增确认导入能力：`POST /api/v1/import/lesson-plan/confirm` 将预览结果创建为普通 `Task + Document`。
- 导入采用预览优先：已识别内容进入结构化字段，无法确定的内容进入 `unmapped_sections / warnings`，不静默丢弃。
- 导入内容全部保持 `pending`，保留老师原文，不调用大模型自动改写。
- 新增导出前体检：`POST /api/v1/documents/{document_id}/quality-check` 返回 `ready / needs_fixes / blocked`、问题、提醒和修复建议。
- 前端在备课台和创建页提供“导入旧教案”入口，上传 `.docx` 后展示结构化预览和未识别内容，确认后进入编辑器。
- 编辑器导出区域展示导出前体检结果，帮助老师在提交前发现缺项。

## Non-goals

- 不支持 `.doc`、PDF、PPT、讲义或学案导入。
- 不做完整学校 Word 模板复刻。
- 不新增并行内容模型，结构化 JSON 仍是内容中枢。
- 不自动提交 / 推送，不自动进入下一阶段。

## Acceptance Criteria

- 上传典型旧 `.docx` 教案后能预览映射结果，并确认生成普通备课任务。
- 至少稳定映射教学目标、教学重难点、教学过程、板书设计、教学反思中的 4 类。
- 未识别内容可见，不丢弃。
- 导入后的 section 默认 `pending`。
- 导出前体检能指出必填项、确认状态、教学过程完整度、总时长、板书和准备等风险。
- 现有创建、生成、编辑、RAG 引用、Word 导出链路不退化。

## Validation

- `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests -q`
- `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`
- `pnpm --dir apps/web type-check`
- `pnpm --dir apps/web test --run`
- `pnpm --dir apps/web build`
