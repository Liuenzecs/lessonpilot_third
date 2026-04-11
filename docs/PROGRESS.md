# 项目进度记录

## [Phase 0] - 骨架搭建

## [Phase 0] — 从零建立工程骨架
- 完成日期：2026-04-11
- 完成内容：
  - 创建 `apps/web`、`apps/api`、`packages/shared-types`、`scripts`、`.github/workflows`
  - 初始化 Vue 3 + TypeScript + Vite + Pinia + Vue Router + TanStack Query 前端骨架
  - 初始化 FastAPI + SQLModel + Alembic + PostgreSQL 配置骨架
  - 定义 `ContentDocument v1` 与最小块模型：`section / paragraph / list / teaching_step`
  - 增加环境变量模板、pnpm workspace、Docker Compose、CI 基线
- 关键文件：
  - `packages/shared-types/src/content.ts`
  - `apps/api/app/schemas/content.py`
  - `apps/web/package.json`
  - `apps/api/pyproject.toml`
  - `docker-compose.yml`
- 验证结果：
  - `pnpm --dir apps/web type-check`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
- Status: DONE

## [Phase 1] — 核心主链路打通
- 完成日期：2026-04-11
- 完成内容：
  - 后端完成 Auth：注册、登录、登出、当前用户、JWT 鉴权
  - 后端完成 Task / Document CRUD、创建任务自动生成主文档骨架、文档版本递增与冲突保护
  - 后端完成 AI 生成主链路：fake provider + DeepSeek 适配、按 section 逐段生成、SSE 推送 `status / progress / document / done / error`
  - 后端完成 `pending` 内容流：AI 生成内容默认待确认，前端通过正常文档保存完成接受/拒绝
  - 后端完成 `.docx` 导出，仅导出 `confirmed` 内容
  - 前端完成登录/注册、备课台列表、三步创建向导、编辑器、自动保存、Word 导出
  - 前端完成左侧大纲导航、内联 pending 卡片、局部章节重新生成与保存状态提示
  - 增加 Windows 受限环境下的 Vite 包装脚本，降低本机构建/运行阻力
- 关键文件：
  - `apps/api/app/api/v1/endpoints/auth.py`
  - `apps/api/app/api/v1/endpoints/tasks.py`
  - `apps/api/app/api/v1/endpoints/documents.py`
  - `apps/api/app/services/generation_service.py`
  - `apps/api/app/services/export_service.py`
  - `apps/web/src/features/task/views/TaskCreateView.vue`
  - `apps/web/src/features/task/views/TaskListView.vue`
  - `apps/web/src/features/editor/views/EditorView.vue`
  - `apps/web/src/features/editor/components/BlockRenderer.vue`
  - `apps/web/src/features/generation/composables/useGeneration.ts`
  - `apps/web/scripts/vite-wrapper.mjs`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：5 passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（存在 Vue 模板格式 warning，但无 error）
  - `pnpm --dir apps/web build`：当前 Codex Windows 沙箱仍被 `esbuild spawn EPERM` 限制拦截；已增加 `apps/web/scripts/vite-wrapper.mjs` 与 `--configLoader native` 兼容层，需在非受限本机环境复验
- Status: DONE

## [Phase 1] — 验收问题修复
- 完成日期：2026-04-11
- 完成内容：
  - 修复编辑器对 Vue 响应式数据执行 `structuredClone` 导致页面卡在“正在加载编辑器...”的问题
  - 将后端和 Alembic 的数据库默认值统一为 PostgreSQL，并统一 DeepSeek 默认 `base_url`
  - 创建本地 `.env` 与 `apps/api/.env` 模板，默认使用 `fake` provider，真实 DeepSeek 配置改为手动填写
  - 重建本机 `lessonpilot` PostgreSQL 数据库并清理旧 SQLite 文件，补充验收说明
- 关键文件：
  - `apps/web/src/shared/utils/content.ts`
  - `apps/web/src/features/editor/views/EditorView.vue`
  - `apps/api/app/core/config.py`
  - `apps/api/alembic.ini`
  - `.env.example`
  - `apps/api/.env.example`
  - `docs/NEXT.md`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest tests`：5 passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（保留现有 Vue 模板格式 warnings，无 error）
  - PostgreSQL smoke flow：注册 → 创建任务 → SSE 生成 → 接受 pending → 导出 `.docx` 已跑通
- Status: DONE
