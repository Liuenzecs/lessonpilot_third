# Phase 12：Google Docs 手感的教师备课桌 UI 重构

## Summary

Phase 12 只改 UI 和前端交互呈现，不改业务接口、数据库或生成链路。目标是把 LessonPilot 从功能面板式产品，重构为老师打开就能工作的“在线备课文档桌”：文档是中心，质量检查、引用、学校模板、个人资料和导出作为周边辅助。

## Design Direction

- **Google Docs 手感**：顶部文档工具栏、左侧大纲、中间纸张画布、右侧检查栏。
- **LessonPilot 内核**：结构化 JSON、section 生成、pending/confirmed、section 引用、质量体检和 Word 导出全部保留。
- **老师迁移价值**：突出“旧资料进来、格式能套、导出前能检查、明天能上课”。
- **UI only**：不新增后端 API，不变更数据模型。

## Key Changes

- `DESIGN.md` 从 Notion 风格改为“教师文档桌”设计系统。
- `CLAUDE.md` 的 UI 方向同步为文档优先界面。
- 公域页首屏展示真实产品文档工作区。
- 备课台改为备课队列和工具区。
- 创建页改为课题优先的启动台，并突出模板、个人资料、知识增强提示。
- 编辑器改为三栏文档体验，右侧集中质量、引用、导出、资料和上课包。
- 旧教案导入、学校模板、个人资料库同步为资料柜 / 格式库视觉。

## Test Plan

- `pnpm --dir apps/web type-check`
- `pnpm --dir apps/web test --run`
- `pnpm --dir apps/web build`
- 固定使用 `5173` 启动前端；如被占用，释放占用进程后仍用 `5173`。
- 手动验收公域页、备课台、创建页、编辑器、导入页、学校模板、个人资料库。

## Acceptance Criteria

- 公域页第一屏能说明“备课文档 + 质量检查 + Word 导出”。
- 备课台可判断每份备课的下一步动作。
- 创建页主流程围绕课题和资料匹配展开。
- 编辑器中心是纸张画布，左侧为目录，右侧为检查和辅助信息。
- 所有 Phase 5-11 主链路继续可用。
- 阶段结束时更新 `docs/PROGRESS.md` 和 `docs/NEXT.md`，停在验收口。
