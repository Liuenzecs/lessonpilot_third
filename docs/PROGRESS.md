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

## [Phase 1] — 复核意见完善
- 完成日期：2026-04-11
- 完成内容：
  - 同步 `GOAL.md` 阶段勾选状态，使其与 `PROGRESS.md` 中的 Phase 0 / Phase 1 完成记录一致
  - 在当前本机环境重新验证前端生产构建，确认 `pnpm --dir apps/web build` 已通过，不再保留该项为待办
  - 收敛 `NEXT.md` 为仅剩用户手动验收与后续指示，避免状态描述混乱
  - 补充本地缓存目录忽略规则，降低 Git 状态噪音
- 关键文件：
  - `docs/GOAL.md`
  - `docs/PROGRESS.md`
  - `docs/NEXT.md`
  - `.gitignore`
- 验证结果：
  - `pnpm --dir apps/web build`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：5 passed
- Status: DONE

## [Phase 1] — DeepSeek 生成链路修复
- 完成日期：2026-04-11
- 完成内容：
  - 修复 DeepSeek prompt 模板中的 JSON 花括号未转义问题，避免在 `.format()` 阶段提前报错
  - 为模型返回的 block 增加服务端兼容层，自动补齐缺失的 `id / status / source`
  - 支持解析 `{"blocks":[...]}`、裸数组以及 `data.blocks` 形式的模型响应，降低结构抖动带来的失败率
  - 确认当前工作区中的真实 DeepSeek 调用已能返回可落库的 block 数据
- 关键文件：
  - `apps/api/app/prompts/lesson_section_generation_prompt.md`
  - `apps/api/app/services/llm_service.py`
  - `apps/api/tests/test_llm_service.py`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：7 passed
  - 直接调用 `DeepSeekProvider.generate_section(...)`：passed，已返回带自动补齐 `id` 的 block
- Status: DONE

## [Phase 1] — 用户验收通过
- 完成日期：2026-04-11
- 完成内容：
  - 用户完成 Phase 1 主链路手动验收，确认注册、创建任务、AI 生成、pending 接受/拒绝、编辑自动保存与导出流程可用
  - 将 `NEXT.md` 收口为“等待用户指示”，不自动进入 Phase 2
  - 准备提交当前工作区中与 DeepSeek 生成链路和阶段状态同步相关的改动
- 关键文件：
  - `docs/NEXT.md`
  - `docs/PROGRESS.md`
- 验证结果：
  - 用户手动验收：passed
- Status: DONE

## [Phase 2] — 编辑器深化与历史版本（首轮实现，后续被判定未达标）
- 完成日期：2026-04-11
- 完成内容：
  - 该实现后续被用户判定为未完全满足 `docs/design/editor-ui.md` 的“全面落地”要求，本记录仅保留为返工基础，不再作为 Phase 2 最终完成依据
  - 扩展 `ContentDocument` 契约到 8 类 block，新增 `exercise_group / choice_question / fill_blank_question / short_answer_question`，并补充 `pending suggestion` 元数据
  - 后端新增 `document_snapshots` 持久化与最近 10 条历史裁剪，完成历史查询、快照预览、恢复为新版本
  - 后端完成局部 AI 重写能力：`POST /api/v1/documents/{id}/rewrite` 与 `GET /api/v1/documents/{id}/rewrite/stream`，支持 block 级与 paragraph 选中文本级 rewrite/polish/expand
  - 后端扩展 section 生成能力到题组与题型块，并新增 PDF 导出；Word/PDF 仅导出 `confirmed` 内容
  - 前端将编辑器升级为 block editor：支持题组/题型编辑、同父级拖拽排序、上下移动、删除、类型转换、AI 重写、段落选中文本 AI 润色/扩写、历史抽屉、导出下拉与快捷键
  - 补齐 Phase 2 后端测试：内容契约校验、rewrite 流、history trim/restore、题组生成、PDF 导出
- 关键文件：
  - `packages/shared-types/src/content.ts`
  - `apps/api/app/schemas/content.py`
  - `apps/api/app/models/document_snapshot.py`
  - `apps/api/app/services/document_service.py`
  - `apps/api/app/services/rewrite_service.py`
  - `apps/api/app/services/export_service.py`
  - `apps/api/app/api/v1/endpoints/documents.py`
  - `apps/web/src/features/editor/views/EditorView.vue`
  - `apps/web/src/features/editor/components/DocumentBlockItem.vue`
  - `apps/web/src/features/editor/components/HistoryDrawer.vue`
  - `apps/web/src/shared/utils/content.ts`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（保留现有 Vue 模板格式 warnings，无 error）
  - `pnpm --dir apps/web build`：passed
- Status: SUPERSEDED

## [Phase 2] — 编辑器返工补齐与设计落地
- 完成日期：2026-04-11
- 完成内容：
  - 修复 AI prompt 模板渲染链路，放弃对 prompt 文件使用 `.format()`，改为安全占位替换，避免 JSON 花括号再次触发 `KeyError`
  - 后端新增 `POST /api/v1/documents/{id}/append` 与 `GET /api/v1/documents/{id}/append/stream`，实现“AI 补充内容”能力，按 section 末尾追加 `pending + append` 建议，并把快照来源扩展为 `append_ai`
  - 前端将编辑器按 `docs/design/editor-ui.md` 返工为“安静工作台”风格，补齐生成骨架屏、逐段替换、顶部状态条、底部快捷操作栏、导出预览模态、可折叠大纲导航与 hover 显示 block 操作
  - 将编辑器视图继续拆分为 `useEditorView`、编辑器头部、section 卡片、底部快捷栏、导出预览等组件与样式文件，恢复单文件长度约束
  - 为 AI 重写、AI 补充、导出下载等动作增加“先确保本地改动已保存”的保护，避免老师在未落库状态下对旧版本文档继续操作
  - 更新 `AGENTS.md`，把“设计文档全面落地”提升为强制验收规则，补上阶段 `DONE` 前必须逐项对照设计文档和 phase 清单的流程要求
- 关键文件：
  - `apps/api/app/services/llm_service.py`
  - `apps/api/app/services/append_service.py`
  - `apps/api/app/api/v1/endpoints/documents.py`
  - `apps/api/app/schemas/document.py`
  - `apps/api/tests/api/test_documents_phase2.py`
  - `apps/web/src/features/editor/composables/useEditorView.ts`
  - `apps/web/src/features/editor/views/EditorView.vue`
  - `apps/web/src/features/editor/components/EditorShellHeader.vue`
  - `apps/web/src/features/editor/components/EditorQuickActionsBar.vue`
  - `apps/web/src/features/editor/components/ExportPreviewModal.vue`
  - `apps/web/src/features/editor/styles/editor.css`
  - `AGENTS.md`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：16 passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（存在既有 Vue 模板格式 warning，但无 error）
  - `pnpm --dir apps/web build`：passed
- Status: DONE

## [Phase 2] — 用户验收通过
- 完成日期：2026-04-11
- 完成内容：
  - 用户确认 Phase 2 返工补齐结果可通过验收，认可编辑器深度完善、AI 补充内容、历史版本、导出预览与相关设计落地结果
  - 同步更新 `GOAL.md`，将 Phase 2 标记为已完成
  - 将 `NEXT.md` 收口为“等待用户指示”，不自动进入 Phase 3
- 关键文件：
  - `docs/GOAL.md`
  - `docs/PROGRESS.md`
  - `docs/NEXT.md`
- 验证结果：
  - 用户手动验收：passed
- Status: DONE
