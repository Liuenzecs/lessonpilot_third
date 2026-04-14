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

## [Phase 2] — 严格返工已重开
- 完成日期：2026-04-11
- 完成内容：
  - 用户明确要求以 `docs/design/editor-ui.md` 为最高优先级重新返工，上一条 Phase 2 完成/验收记录不再代表当前状态
  - 将 `GOAL.md` 中的 Phase 2 改回未完成状态，并将 `NEXT.md` 改写为新的严格验收清单
  - 当前返工范围锁定为工作台、创建向导、编辑器三块体验，验收通过前不进入 Phase 3
- 关键文件：
  - `docs/GOAL.md`
  - `docs/PROGRESS.md`
  - `docs/NEXT.md`
- 验证结果：
  - 文档状态已纠正，等待本轮 Phase 2 严格返工完成后的手动验收
- Status: REOPENED

## [Phase 2] — 严格返工验收通过
- 完成日期：2026-04-11
- 完成内容：
  - 工作台按设计稿重做为大 CTA、最近备课卡片、搜索和头像入口的结构，不再保留 dashboard 式布局
  - 创建向导收口为 3 步一屏流程：学科、年级、课题主题，提交后直接进入编辑器
  - 编辑器继续按 `docs/design/editor-ui.md` 收口：骨架逐段替换、可折叠大纲、hover 才出现的 block 操作、AI 待确认卡片、底部快捷栏、导出预览、历史抽屉、冲突恢复动作
  - 补齐 paragraph/list 缩进持久化、selection rewrite 上下文保留以及相关导出与测试回归
  - 用户已手动验收通过，本轮 Phase 2 可重新视为完成
- 关键文件：
  - `apps/web/src/features/task/views/TaskListView.vue`
  - `apps/web/src/features/task/views/TaskCreateView.vue`
  - `apps/web/src/features/editor/views/EditorView.vue`
  - `apps/web/src/features/editor/composables/useEditorView.ts`
  - `apps/web/src/features/editor/styles/editor.css`
  - `apps/web/src/shared/styles/main.css`
  - `apps/api/tests/api/test_documents_phase2.py`
  - `docs/GOAL.md`
  - `docs/PROGRESS.md`
  - `docs/NEXT.md`
- 验证结果：
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（存在既有 Vue 样式 warning，无 error）
  - `pnpm --dir apps/web build`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：17 passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - 用户手动验收：passed
- Status: DONE

## [Phase 3] — 公域页面与 Auth 完善开始实施
- 完成日期：2026-04-11
- 完成内容：
  - 按 `docs/design/public-pages-ui.md` 重开 `Phase 3`，将其作为本轮最高优先级验收规范
  - 将工作范围锁定为公域页面、Auth 完善、备课台补齐、账户设置、全局反馈入口与任务卡片更多操作
  - 当前实现基线已覆盖三套布局壳、主要公域页面、忘记密码/重置密码/邮箱验证链路、账户与反馈接口、任务复制接口及对应前端页面
  - 同步将 `NEXT.md` 改写为 `Phase 3` 严格验收清单，验收通过前不进入 `Phase 4`
- 关键文件：
  - `docs/NEXT.md`
  - `docs/design/public-pages-ui.md`
  - `apps/web/src/app/router/index.ts`
  - `apps/web/src/app/layouts/`
  - `apps/web/src/features/public/`
  - `apps/web/src/features/auth/views/`
  - `apps/web/src/features/settings/`
  - `apps/api/app/api/v1/endpoints/auth.py`
  - `apps/api/app/api/v1/endpoints/account.py`
  - `apps/api/app/api/v1/endpoints/tasks.py`
- 验证结果：
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（当前仍保留大量 Vue 模板格式 warnings，但已无 error）
  - `pnpm --dir apps/web build`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：22 passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
- Status: IN PROGRESS

## [Phase 3] — 公域页面、账户体系与验收问题修复完成
- 完成日期：2026-04-11
- 完成内容：
  - 严格按 `docs/design/public-pages-ui.md` 完成公域页面、三套布局壳、备课台、账户设置、反馈入口、认证链路与任务卡片更多操作的 Phase 3 落地
  - 修复验收阶段暴露的问题：认证页缺失统一顶部导航、已登录用户仍出现“登录”入口、Footer 文案对比度不足、短页面 Footer 未贴底、旧会话恢复异常、登录/注册失败提示不准确
  - 为后端补齐幂等化 Alembic 迁移与启动迁移执行，修复历史数据库处于半升级状态时导致的登录/注册失败问题，并确认邮箱验证相关字段与认证令牌表已正确落库
  - 用户已明确确认本轮 Phase 3 验收满意，通过验收；同步将 `GOAL.md` 中的 Phase 3 标记为完成，并将 `NEXT.md` 收口为等待下一步指示
- 关键文件：
  - `apps/web/src/app/layouts/AuthLayout.vue`
  - `apps/web/src/app/layouts/PublicLayout.vue`
  - `apps/web/src/app/layouts/PrivateLayout.vue`
  - `apps/web/src/features/public/components/PublicNav.vue`
  - `apps/web/src/features/public/components/PublicFooter.vue`
  - `apps/web/src/features/public/styles/public.css`
  - `apps/web/src/features/auth/views/LoginView.vue`
  - `apps/web/src/features/auth/views/RegisterView.vue`
  - `apps/web/src/features/auth/views/ForgotPasswordView.vue`
  - `apps/web/src/features/auth/views/ResetPasswordView.vue`
  - `apps/web/src/features/auth/views/VerifyEmailView.vue`
  - `apps/web/src/features/auth/utils/error.ts`
  - `apps/web/src/features/task/views/TaskListView.vue`
  - `apps/web/src/features/settings/views/SettingsView.vue`
  - `apps/web/src/features/feedback/`
  - `apps/api/app/core/db.py`
  - `apps/api/alembic/versions/20260411_0003_phase3_auth_account.py`
  - `apps/api/app/api/v1/endpoints/account.py`
  - `apps/api/app/services/account_service.py`
  - `apps/api/tests/api/test_auth.py`
  - `apps/api/tests/api/test_phase3_account.py`
  - `docs/GOAL.md`
  - `docs/PROGRESS.md`
  - `docs/NEXT.md`
- 验证结果：
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（仍有现存 Vue 模板格式 warnings，无 error）
  - `pnpm --dir apps/web build`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：22 passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/alembic/versions apps/api/tests`：passed
  - 手动验收：passed
- Status: DONE

## [Phase 4] — 账户设置与真实计费开始实施
- 完成日期：2026-04-12
- 完成内容：
  - 按 Phase 4 方案将设置页“订阅方案”从展示层升级为真实计费中心，补齐 7 天试用、微信/支付宝双渠道、手动续费、支付记录、发票申请与全局升级弹层
  - 后端新增 `user_subscriptions / billing_orders / billing_webhook_events / invoice_requests` 计费模型、真实订阅摘要、mock/gateway 双模式配置、订单创建/支付回调/发票申请链路
  - 在 `POST /api/v1/tasks/` 与 `POST /api/v1/tasks/{id}/duplicate` 落实免费版每月 5 份教案额度限制，并把额度超限统一收口为结构化 `402 quota_exceeded`
  - 为局部 AI 重写、AI 补充内容、章节重新生成、PDF 导出、版本历史与恢复补齐专业版后端闸门，并统一返回 `402 plan_required`
  - 修复编辑器内升级提示、创建向导额度拦截、备课台订阅信息刷新、账户删除 `DELETE` 二次确认，以及试用/支付在 SQLite 测试环境下的 UTC 时间兼容问题
  - 为 Phase 4 补齐并更新后端测试，覆盖试用状态流转、trial 期间支付生效时间、手动续费顺延、额度限制、专业版闸门、发票申请与 gateway webhook 幂等
- 关键文件：
  - `apps/api/app/services/billing_service.py`
  - `apps/api/app/api/v1/endpoints/account.py`
  - `apps/api/app/api/v1/endpoints/billing.py`
  - `apps/api/app/api/v1/endpoints/tasks.py`
  - `apps/api/app/api/v1/endpoints/documents.py`
  - `apps/api/app/models/user_subscription.py`
  - `apps/api/app/models/billing_order.py`
  - `apps/api/app/models/billing_webhook_event.py`
  - `apps/api/app/models/invoice_request.py`
  - `apps/api/app/schemas/billing.py`
  - `apps/api/tests/api/test_documents_phase2.py`
  - `apps/api/tests/api/test_phase4_billing.py`
  - `apps/web/src/features/settings/views/SettingsView.vue`
  - `apps/web/src/features/public/views/PricingView.vue`
  - `apps/web/src/features/task/views/TaskCreateView.vue`
  - `apps/web/src/features/task/views/TaskListView.vue`
  - `apps/web/src/features/editor/composables/useEditorView.ts`
  - `apps/web/src/features/billing/components/UpgradeModal.vue`
  - `apps/web/src/app/stores/billing.ts`
  - `apps/web/src/features/settings/composables/useAccount.ts`
  - `apps/web/src/features/task/composables/useTasks.ts`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：28 passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/alembic/versions apps/api/tests`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（保留现有 Vue 模板格式 warnings，无 error）
  - `pnpm --dir apps/web build`：passed
- Status: IN PROGRESS

## [Phase 4] — 用户验收通过
- 完成日期：2026-04-12
- 完成内容：
  - 用户已手动验收通过 Phase 4，确认真实计费、免费额度限制、试用/手动续费、升级弹层、发票申请和专业版能力闸门符合本轮要求
  - 同步更新 `GOAL.md`，将 Phase 4 标记为完成
  - 将 `NEXT.md` 收口为“等待用户指示”，在没有新指令前不自动进入 Phase 5
- 关键文件：
  - `docs/GOAL.md`
  - `docs/PROGRESS.md`
  - `docs/NEXT.md`
- 验证结果：
  - 用户手动验收：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：28 passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/alembic/versions apps/api/tests`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（保留现有 Vue 模板格式 warnings，无 error）
  - `pnpm --dir apps/web build`：passed
- Status: DONE

## [Phase 5] — UX 打磨开始实施
- 完成日期：2026-04-12
- 完成内容：
  - 按 `docs/GOAL.md` Phase 5 清单与 accepted advice 重新开启 UX 打磨，实现统一 Toast、错误归一模型、共享状态面板、轻量路由/组件动效与 `prefers-reduced-motion` 支持
  - 为备课台、创建向导、编辑器接入一次性热点导览，并补齐首登空状态、搜索无结果、设置页空记录、帮助中心无结果、导出预览空状态与页面骨架屏
  - 新增独立的 `404 / 500 / 网络错误` 页面，收口私域页面的整页错误态、页面内重试路径、反馈悬浮按钮行为以及编辑器手机端友好提示
  - 将 Word 导出升级为模板化纸面排版，并同步提升 PDF/导出预览的样式层级与 confirmed-only 导出质量
  - 为忘记密码、重置密码、邮箱验证补齐全局 Toast 操作反馈，使认证链路与新的 UX 基础设施保持一致
  - 当前实现已完成，等待用户手动验收；在验收通过前不将 Phase 5 标记为 `DONE`
- 关键文件：
  - `apps/web/src/shared/api/errors.ts`
  - `apps/web/src/shared/composables/useToast.ts`
  - `apps/web/src/shared/components/ToastViewport.vue`
  - `apps/web/src/shared/components/StatePanel.vue`
  - `apps/web/src/features/onboarding/composables/useOnboarding.ts`
  - `apps/web/src/features/onboarding/components/OnboardingCallout.vue`
  - `apps/web/src/features/task/views/TaskListView.vue`
  - `apps/web/src/features/task/views/TaskCreateView.vue`
  - `apps/web/src/features/settings/views/SettingsView.vue`
  - `apps/web/src/features/editor/views/EditorView.vue`
  - `apps/web/src/features/editor/composables/useEditorView.ts`
  - `apps/web/src/features/public/views/ServerErrorView.vue`
  - `apps/web/src/features/public/views/NetworkErrorView.vue`
  - `apps/web/src/features/feedback/components/FeedbackWidget.vue`
  - `apps/api/app/services/export_service.py`
  - `apps/api/tests/api/test_tasks.py`
  - `docs/NEXT.md`
  - `docs/PROGRESS.md`
- 验证结果：
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（保留现有 Vue 模板格式 warnings，无 error）
  - `pnpm --dir apps/web build`：passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：29 passed
- Status: IN PROGRESS

## [Phase 5] — 用户验收通过
- 完成日期：2026-04-12
- 完成内容：
  - 用户已手动验收通过 Phase 5，确认全局 Toast、错误页、热点导览、空状态、响应式收口、反馈入口以及 Word 导出成品排版符合本轮文档要求
  - 修复验收过程中发现的两个回归问题：选中文本 `AI 扩写` 后接受无效，以及导出预览模态无法向下滚动显示完整内容
  - 同步更新 `GOAL.md`，将 Phase 5 标记为完成
  - 将 `NEXT.md` 收口为“等待用户指示”，在没有新指令前不自动进入 Phase 6
- 关键文件：
  - `apps/web/src/shared/utils/content.ts`
  - `apps/api/app/services/llm_service.py`
  - `apps/api/tests/api/test_documents_phase2.py`
  - `apps/web/src/features/editor/styles/editor.css`
  - `docs/GOAL.md`
  - `docs/PROGRESS.md`
  - `docs/NEXT.md`
- 验证结果：
  - 用户手动验收：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（保留现有 Vue 模板格式 warnings，无 error）
  - `pnpm --dir apps/web build`：passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：29 passed
- Status: DONE

## [Phase 6] — 运营基础设施严格落地
- 完成日期：2026-04-12
- 完成内容：
  - 按 `docs/GOAL.md` Phase 6 清单与 accepted advice 完成运营基础设施落地：统一 `console | smtp` 事务邮件抽象、欢迎验证/重置密码/免费额度预警邮件、反馈与发票通知收口、邮件发送日志与去重键
  - 后端新增第一方分析事件管道、`analytics_events / quota_adjustments / email_delivery_logs` 模型与迁移，接入注册、登录、试用、支付、创建/复制任务、导出、反馈等权威运营事件
  - 新增 `/admin` 管理后台接口与前端后台页面，按管理员邮箱白名单控制访问，提供概览、用户列表、用户详情与手动月度配额调整，并把人工调整并入用户侧有效额度计算
  - 前后端统一接入 Sentry，覆盖浏览器、SSR Node 进程与 FastAPI 后端，并对 JWT、Authorization、密码、token、教案内容和 prompt 做敏感信息清洗
  - 前端升级为“公域 SSR + 私域 SPA”运行形态，补齐公域 SEO 元信息、`robots.txt`、`sitemap.xml`、默认 OG 图、Node SSR 服务器、`apps/web` Dockerfile 与更新后的 `docker-compose.yml`
  - 收口路由级懒加载、SSR 缓存策略和静态资源缓存，保持公域首屏、后台聚合与既有编辑器主链路在 Phase 6 下继续稳定
- 关键文件：
  - `apps/api/app/services/mail_service.py`
  - `apps/api/app/services/analytics_service.py`
  - `apps/api/app/services/admin_service.py`
  - `apps/api/app/core/sentry.py`
  - `apps/api/app/api/v1/endpoints/admin.py`
  - `apps/api/app/api/v1/endpoints/analytics.py`
  - `apps/api/alembic/versions/20260412_0005_phase6_ops.py`
  - `apps/api/tests/api/test_phase6_ops.py`
  - `apps/web/src/app/createApp.ts`
  - `apps/web/src/entry-client.ts`
  - `apps/web/src/entry-server.ts`
  - `apps/web/src/app/seo.ts`
  - `apps/web/server.mjs`
  - `apps/web/src/features/admin/views/AdminOverviewView.vue`
  - `apps/web/src/features/admin/views/AdminUsersView.vue`
  - `apps/web/src/features/admin/views/AdminUserDetailView.vue`
  - `apps/web/src/features/analytics/client.ts`
  - `apps/web/Dockerfile`
  - `docker-compose.yml`
  - `docs/NEXT.md`
- 验证结果：
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（保留既有大量 Vue 模板格式 warnings，无 error）
  - `pnpm --dir apps/web build`：passed（已同时产出 client + SSR server）
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/alembic/versions apps/api/tests`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：35 passed
  - SSR smoke：passed（`/`、`/pricing`、`/robots.txt`、`/sitemap.xml` 可访问，源码中可见公域正文与 SEO 信息）
- Status: IN PROGRESS

## [Phase 6] — 用户验收通过
- 完成日期：2026-04-13
- 完成内容：
  - 用户已手动验收通过 Phase 6，确认事务邮件、公域 SSR/SEO、第一方分析管道、Sentry、管理员白名单后台与配额调整链路符合本轮文档要求
  - 同步更新 `GOAL.md`，将 Phase 6 标记为完成
  - 将 `NEXT.md` 收口为“等待用户指示”，在没有新指令前不自动进入 Phase 7
- 关键文件：
  - `docs/GOAL.md`
  - `docs/PROGRESS.md`
  - `docs/NEXT.md`
- 验证结果：
  - 用户手动验收：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（保留既有 Vue 模板格式 warnings，无 error）
  - `pnpm --dir apps/web build`：passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/alembic/versions apps/api/tests`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests`：35 passed
- Status: DONE

## [Milestone 1] — 里程碑重组与 Phase 7 审查加固启动
- 完成日期：2026-04-13
- 完成内容：
  - 按最新项目约束将路线图从单层 `Phase 0-7` 重组为 `Milestone 1 / Milestone 2`
  - 将 Phase 1-6 归档为 Milestone 1 已完成基础，并新增 `Milestone 1 / Phase 7 — 审查与加固`
  - 在 `docs/milestones/milestone-1/` 建立里程碑归档文档，整理核实后的审查报告与正式实现清单
  - 更新 `AGENTS.md`，明确当前活跃阶段、里程碑目录说明、旧 Phase 7 advice 的历史参考属性，以及未经用户确认不得进入 Milestone 2
- 关键文件：
  - `docs/GOAL.md`
  - `docs/NEXT.md`
  - `docs/PROGRESS.md`
  - `docs/milestones/milestone-1/README.md`
  - `docs/milestones/milestone-1/phase-7-audit-hardening.md`
  - `docs/milestones/milestone-1/review-report.md`
  - `AGENTS.md`
- 验证结果：
  - Milestone 文档口径已切换完成
  - 当前阶段保持 `Milestone 1 / Phase 7` 进行中，等待实现与后续手动验收
- Status: IN PROGRESS

## [Milestone 1 / Phase 7] — 审查加固实现中
- 完成日期：2026-04-13
- 完成内容：
  - 完成 Milestone 1 / Phase 7 的核心实现：密钥治理文档收口、`dompurify` 净化层、`slowapi` 关键入口限流、Webhook HMAC 验签、`APP_ENV` + 生产环境 JWT secret 启动校验
  - 完成鲁棒性加固：根级错误边界、`app.config.errorHandler`、编辑器自动保存“未同步 / 正在重试 / 已恢复”反馈、数据库连接池配置、SSE 断连处理、`pytest-cov` 与 Phase 7 测试
  - 完成 UI 收口：Landing 内部文案替换、公域 emoji 改 SVG icon、UpgradeModal 并回主站视觉系统、`focus-visible`、认证页品牌面板、亮暗主题切换与本地偏好持久化
  - 同步补齐 `AGENTS.md` 密钥约束与 `.env.example / apps/api/.env.example` 的 Phase 7 配置模板，新增 `pnpm-workspace.yaml` 的 `allowBuilds` 以方便本机正常安装 `esbuild` 与 `vue-demi`
- 关键文件：
  - `apps/api/app/core/config.py`
  - `apps/api/app/core/db.py`
  - `apps/api/app/core/rate_limit.py`
  - `apps/api/app/core/streaming.py`
  - `apps/api/app/api/v1/endpoints/auth.py`
  - `apps/api/app/api/v1/endpoints/analytics.py`
  - `apps/api/app/api/v1/endpoints/billing.py`
  - `apps/api/app/api/v1/endpoints/tasks.py`
  - `apps/api/app/api/v1/endpoints/documents.py`
  - `apps/api/tests/api/test_phase7_hardening.py`
  - `apps/web/src/entry-client.ts`
  - `apps/web/src/shared/components/AppErrorBoundary.vue`
  - `apps/web/src/shared/utils/sanitize.ts`
  - `apps/web/src/features/editor/composables/useEditorView.ts`
  - `apps/web/src/features/editor/components/EditorShellHeader.vue`
  - `apps/web/src/features/public/views/LandingView.vue`
  - `apps/web/src/features/public/components/PublicNav.vue`
  - `apps/web/src/app/layouts/AuthLayout.vue`
  - `apps/web/src/features/billing/components/UpgradeModal.vue`
  - `apps/web/src/shared/styles/main.css`
  - `.env.example`
  - `apps/api/.env.example`
  - `pnpm-workspace.yaml`
- 验证结果：
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（仍保留现有大量 Vue 模板格式 warnings，但无 error）
  - `pnpm approve-builds --all`：passed
  - `pnpm --dir apps/web build`：passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/alembic/versions apps/api/tests`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests --cov`：42 passed，total 88% 覆盖率；关键安全与运维模块达到 80%+
- Status: IN PROGRESS

## [产品重规划] — 按 product-replan-v2.md 重做
- 完成日期：2026-04-14
- 完成内容：
  - 原有 Phase 0-7 / Milestone 1 路线图被判定为产品体验不达标，按 `docs/milestones/product-replan-v2.md` 重新规划
  - 新实施计划 `docs/milestones/implementation-plan-v2.md` 定义 6 个 Sprint（Sprint 0-6）
  - Sprint 0（项目清理与准备）已完成
- 关键文件：
  - `docs/milestones/product-replan-v2.md`
  - `docs/milestones/implementation-plan-v2.md`
  - `docs/GOAL.md`、`docs/NEXT.md`、`docs/PROGRESS.md`、`CLAUDE.md`
- Status: IN PROGRESS

## [Sprint 0] — 项目清理与准备
- 完成日期：2026-04-14
- 完成内容：

  **后端清理**：
  - 删除 service 文件：`billing_service.py`、`admin_service.py`、`analytics_service.py`、`append_service.py`
  - 删除 model 文件：`billing_order.py`、`billing_webhook_event.py`、`invoice_request.py`、`user_subscription.py`、`quota_adjustment.py`、`analytics_event.py`、`email_delivery_log.py`
  - 删除 endpoint 文件：`billing.py`、`admin.py`、`analytics.py`
  - 删除 schema 文件：`billing.py`、`admin.py`、`analytics.py`
  - 删除 `core/rate_limit.py`、`core/sentry.py`、`core/streaming.py`
  - 精简 `models/__init__.py` → 只导出 User、Task、Document、DocumentSnapshot、AuthToken、Feedback
  - 精简 `router.py` → 只保留 auth、tasks、documents、health、account
  - 精简 `config.py` → 移除 billing/admin/sentry 字段，添加 MiniMax Provider 配置
  - 精简 `pyproject.toml` → 移除 weasyprint、sentry-sdk、slowapi、limits
  - 更新 `main.py` → 移除 Sentry init 和 SlowAPI 中间件
  - 精简 `mail_service.py` → 移除 EmailDeliveryLog 和 billing 邮件，保留验证/重置/反馈邮件
  - 修复 `db.py` 对已删除模型的引用
  - 更新测试：移除 billing/subscription/append/PDF 测试，修复 LLM 路径

  **前端清理**：
  - 删除 feature 目录：admin、analytics、onboarding、feedback、billing
  - 删除 SSR 文件：`entry-server.ts`、`server.mjs`
  - 删除 Sentry：`app/monitoring/sentry.ts`
  - 删除 SEO：`app/seo.ts`、billing store、AdminLayout
  - 精简 `package.json` → 移除 @sentry、@vue/server-renderer、express、compression
  - 简化 build 为纯 SPA
  - 清理 router → 移除 admin 路由和 SSR meta
  - 从所有页面/composable 移除 billing/analytics/onboarding 引用
  - 修复 `LandingView.vue` 语法错误、`useEditorView.ts` useSubscription 残留

- 验证结果：
  - `python -m ruff check app/`：All checks passed
  - `python -m pytest tests/ -q`：24 passed
  - `npx vue-tsc --noEmit`：passed
  - `pnpm build`：✓ built in 11.61s
- Status: DONE

## [Sprint 1] — 内容模型 + AI 服务重写
- 完成日期：2026-04-14
- 完成内容：

  **Phase 1：后端新内容 Schema**
  - 重写 `schemas/content.py`：删除 8 种 block 体系，替换为 `LessonPlanContent`（教案）+ `StudyGuideContent`（学案）结构化模型
  - 新增公共类型：`TeachingObjective`（三维目标）、`TeachingProcessStep`（教学过程步骤）、`AssessmentItem`（测评题）、`KeyPoints`（重难点）
  - 保留 `SectionStatus`（confirmed/pending）概念，提升到 section 级别
  - 新增空模板创建函数：`create_empty_lesson_plan()`、`create_empty_study_guide()`

  **Phase 1（续）：Schema 更新**
  - 重写 `schemas/task.py`：新增 `scene`（使用场景）、`lesson_type`（教案/学案/都生成）、`class_hour`（课时）、`lesson_category`（课型）
  - 重写 `schemas/document.py`：DocumentRewritePayload 改为 section 级操作（section_name/action/instruction），移除 DocumentAppendPayload
  - 新建 `schemas/lesson.py`：GenerationContext 和 SectionRewriteContext

  **Phase 2：后端模型更新 + 迁移**
  - 更新 `models/task.py`：新增 scene/lesson_type/class_hour/lesson_category 列
  - 更新 `models/document.py`：移除 task_id unique 约束（支持 1:many）
  - 新建 Alembic 迁移 `20260414_0006_sprint1_content_model.py`

  **Phase 3：AI 服务重写**
  - 重写 `services/llm_service.py`：Provider 架构（LLMProvider 基类 + FakeProvider/DeepSeekProvider/MiniMaxProvider）
  - 真正的 token-by-token 流式输出（httpx AsyncClient stream=True）
  - 新建 prompt 模板：教案生成、学案生成、section 级重写

  **Phase 3（续）：Generation/Rewrite Service**
  - 重写 `generation_service.py`：一次性流式生成完整教案/学案，支持同时生成教案+学案
  - 重写 `rewrite_service.py`：Section 级重写/扩写/精简

  **Phase 4：后端 Service/Endpoint 适配**
  - 更新 `task_service.py`：create_task 根据 lesson_type 创建 1 或 2 个 document
  - 更新 `document_service.py`：load_content 根据 doc_type 反序列化
  - 更新 endpoints：tasks.py、documents.py 适配新参数和内容结构

  **Phase 5：前端类型更新**
  - 重写 `packages/shared-types/src/content.ts`：新的 LessonPlanContent/StudyGuideContent 类型 + 向后兼容导出
  - 重写 `apps/web/src/shared/utils/content.ts`：Section 级操作 + block 系统兼容 stub
  - 更新前端类型定义：editor/types.ts、task/types.ts
  - 适配 useEditorView.ts 和 useEditor.ts

  **Phase 6：测试 + 验证**
  - 更新后端测试：content_schema、llm_service、tasks、documents、phase3_account、phase7_hardening
  - 前端 type-check + build 通过
  - 后端 ruff + pytest 通过（28 passed）

- 关键文件：
  - `apps/api/app/schemas/content.py`（REWRITE）
  - `apps/api/app/schemas/task.py`（REWRITE）
  - `apps/api/app/schemas/document.py`（REWRITE）
  - `apps/api/app/schemas/lesson.py`（NEW）
  - `apps/api/app/models/task.py`（UPDATE）
  - `apps/api/app/models/document.py`（UPDATE）
  - `apps/api/alembic/versions/20260414_0006_sprint1_content_model.py`（NEW）
  - `apps/api/app/services/llm_service.py`（REWRITE）
  - `apps/api/app/services/generation_service.py`（REWRITE）
  - `apps/api/app/services/rewrite_service.py`（REWRITE）
  - `apps/api/app/services/task_service.py`（UPDATE）
  - `apps/api/app/services/document_service.py`（UPDATE）
  - `apps/api/app/api/v1/endpoints/tasks.py`（UPDATE）
  - `apps/api/app/api/v1/endpoints/documents.py`（UPDATE）
  - `apps/api/app/prompts/lesson_plan_generation_prompt.md`（NEW）
  - `apps/api/app/prompts/study_guide_generation_prompt.md`（NEW）
  - `apps/api/app/prompts/section_rewrite_prompt.md`（NEW）
  - `packages/shared-types/src/content.ts`（REWRITE）
  - `apps/web/src/shared/utils/content.ts`（REWRITE）
- 验证结果：
  - `python -m ruff check app/`：All checks passed
  - `python -m pytest tests/ -q`：28 passed
  - `npx vue-tsc --noEmit`：passed
  - `pnpm build`：✓ built in 10.87s
- Status: DONE

## [Sprint 3] — 创建页 + 流式生成体验

- 完成日期：2026-04-14
- 完成内容：

  **后端流式输出重写**：
  - 重写 `generation_service.py`：删除 `_assemble_streamed_json()`，替换为逐 token 转发 + section 边界检测
  - 新 SSE 事件协议：`section_start`、`section_delta`、`section_complete`、`document`、`done`、`error`
  - 新增 `_SectionTracker` 类：通过正则检测 `"<section_name>_status"` 模式实现启发式 section 边界检测
  - 新增教案/学案 section 名称→中文标题映射表

  **前端 SSE 消费重写**：
  - 重写 `useGeneration.ts`：新增 `StreamingEventHandlers` 接口（类型化事件回调）
  - `consumeGenerationStream()` 支持 `AbortSignal` 参数用于停止生成
  - 保留旧的 `consumeRewriteStream()` / `consumeAppendStream()` 不变

  **编辑器流式集成**：
  - 更新 `useEditorView.ts`：`generationProgress` 新增 `streamingText` 和 `docType` 字段
  - 新增 `stopGeneration()` 函数（通过 AbortController 中断流式连接）
  - 重写 `startGeneration()` 使用新的 `StreamingEventHandlers`

  **StreamingText 组件**：
  - 新建 `StreamingText.vue`：流式文本显示组件，带闪烁光标动画
  - 中式现代风样式：`var(--text)` 文字色，`var(--primary)` 光标色

  **collectSections() 修复**：
  - 重写 `content.ts` 中的 `collectSections()`：从空 stub 改为真正的 section 提取
  - 实现 `collectLessonPlanSections()` 和 `collectStudyGuideSections()`
  - 将结构化内容字段映射为 `SectionBlock[]`（含 ParagraphBlock/ListBlock/TeachingStepBlock 等）
  - 同步修复 `findSection()` 函数

  **创建页重写**：
  - 重写 `TaskCreateView.vue`：3 步向导 → 单页一站式布局
  - 新增全部 9 个表单字段：学科/年级/课题/课时/课型/生成类型/使用场景/补充说明
  - 新增选项常量：`LESSON_CATEGORY_OPTIONS`、`SCENE_OPTIONS`、`LESSON_TYPE_OPTIONS`

  **EditorView + EditorStatusBanner 更新**：
  - 集成 StreamingText 组件到编辑器主面板
  - EditorStatusBanner 新增"停止生成"按钮
  - CSS 更新：创建页一站式布局样式、流式文本样式、生成中 banner flex 布局

- 关键文件：
  - `apps/api/app/services/generation_service.py`（REWRITE）
  - `apps/web/src/features/generation/composables/useGeneration.ts`（REWRITE）
  - `apps/web/src/features/editor/composables/useEditorView.ts`（UPDATE）
  - `apps/web/src/features/editor/components/StreamingText.vue`（NEW）
  - `apps/web/src/shared/utils/content.ts`（REWRITE collectSections）
  - `apps/web/src/features/task/views/TaskCreateView.vue`（REWRITE）
  - `apps/web/src/shared/constants/options.ts`（UPDATE）
  - `apps/web/src/features/editor/views/EditorView.vue`（UPDATE）
  - `apps/web/src/features/editor/components/EditorStatusBanner.vue`（UPDATE）
  - `apps/web/src/shared/styles/main.css`（UPDATE）
  - `apps/web/src/features/editor/styles/editor.css`（UPDATE）
  - `apps/api/tests/api/test_tasks.py`（UPDATE）
- 验证结果：
  - `python -m ruff check app/`：All checks passed
  - `python -m pytest tests/ -q`：28 passed
  - `npx vue-tsc --noEmit`：passed
  - `pnpm build`：✓ built in 13.97s
- Status: DONE

## [Sprint 4] — Section Editor + AI 重写

- 完成日期：2026-04-15
- 完成内容：

  **后端 Rewrite 流式化**：
  - 重写 `rewrite_service.py`：新增 `section_start`、`section_delta`、`section_complete` 流式事件，与 generation 流式协议对齐
  - 重写过程中逐 token 转发给前端，保留最终 `document` 事件

  **前端 Content 工具重写**：
  - 重写 `packages/shared-types/src/content.ts`：删除旧 block 类型系统（Block、SectionBlock、BlockType 等 9 种类型），新增 `SectionInfo` 接口
  - 重写 `apps/web/src/shared/utils/content.ts`：删除 `collectSections()` 和所有 block mutation stub（14 个空函数），新增结构化模型直接操作函数（`getSections`、`getSectionTitle`、`updateSection`、`confirmSection` 等）

  **编辑器组件重写（核心）**：
  - 删除 8 个旧 block 组件：`DocumentBlockItem.vue`、`BlockRenderer.vue`、`EditorSectionCard.vue`、`BlockPreview.vue`、`PendingBlockCard.vue`、`EditorQuickActionsBar.vue`、`EditorSectionSkeleton.vue`、`RichTextField.vue`
  - 新建 `SectionPanel.vue`：可折叠 section 面板，根据 doc_type 和 section.name 动态渲染对应编辑器
  - 新建 `SectionEditors/` 目录（7 个组件）：`ObjectivesEditor`、`KeyPointsEditor`、`GenericListEditor`、`TeachingProcessEditor`、`AssessmentEditor`、`LearningProcessEditor`、`RichTextEditor`
  - 新建 `SectionAiActions.vue`：section 级 AI 操作下拉菜单（重写/扩写/精简 + 自定义指令）
  - 新建 `EditorToolbar.vue`：全部展开/折叠、确认全部
  - 重写 `EditorView.vue`：Tab 切换教案/学案、section 列表渲染、大纲导航、streaming text 集成
  - 重写 `useEditorView.ts`（1088 → ~230 行）：拆分为 4 个 composable
    - `useAutoSave.ts`（~180 行）：自动保存、debounce、冲突处理、重试
    - `useEditorGeneration.ts`（~130 行）：AI 生成流式消费
    - `useEditorRewrite.ts`（~90 行）：section 级 AI 重写流式消费
  - 简化 `EditorShellHeader.vue`：移除 PDF 导出选项
  - 更新 `EditorStatusBanner.vue`：action 类型适配（simplify 替换 polish）
  - 重写 `ExportPreviewModal.vue`：直接展示结构化内容，不再依赖 block 树
  - 重写 `HistoryDrawer.vue`：快照预览改为直接展示结构化内容
  - 更新 `consumeRewriteStream()` 支持 `AbortSignal` 参数

- 关键文件：
  - `apps/api/app/services/rewrite_service.py`（UPDATE）
  - `packages/shared-types/src/content.ts`（REWRITE）
  - `apps/web/src/shared/utils/content.ts`（REWRITE）
  - `apps/web/src/features/editor/views/EditorView.vue`（REWRITE）
  - `apps/web/src/features/editor/composables/useEditorView.ts`（REWRITE）
  - `apps/web/src/features/editor/composables/useAutoSave.ts`（NEW）
  - `apps/web/src/features/editor/composables/useEditorGeneration.ts`（NEW）
  - `apps/web/src/features/editor/composables/useEditorRewrite.ts`（NEW）
  - `apps/web/src/features/editor/components/SectionPanel.vue`（NEW）
  - `apps/web/src/features/editor/components/SectionAiActions.vue`（NEW）
  - `apps/web/src/features/editor/components/EditorToolbar.vue`（NEW）
  - `apps/web/src/features/editor/components/SectionEditors/*.vue`（NEW ×7）
  - `apps/web/src/features/editor/components/EditorShellHeader.vue`（UPDATE）
  - `apps/web/src/features/editor/components/EditorStatusBanner.vue`（UPDATE）
  - `apps/web/src/features/editor/components/ExportPreviewModal.vue`（REWRITE）
  - `apps/web/src/features/editor/components/HistoryDrawer.vue`（REWRITE）
  - `apps/web/src/features/generation/composables/useGeneration.ts`（UPDATE）
- 验证结果：
  - `python -m ruff check app/`：All checks passed
  - `python -m pytest tests/ -q`：28 passed
  - `npx vue-tsc --noEmit`：passed
  - `pnpm build`：✓ built in 21.66s
- Status: DONE
