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

## [Sprint 5] — 导出重写

- 完成日期：2026-04-15
- 完成内容：

  **后端导出服务重写**：
  - 重写 `services/export_service.py`：删除全部旧 block 导出代码（~675 行），替换为基于 `LessonPlanContent` / `StudyGuideContent` 结构化模型的 Word 导出
  - 教案 Word 导出：表头信息栏 + 三维目标（知识与技能/过程与方法/情感态度）+ 重难点 + 教学准备 + 表格式教学过程（5 列表格：环节/时长/教师活动/学生活动/设计意图）+ 板书设计 + 反思留空区
  - 学案 Word 导出：学生信息表格 + 学习目标 + 重难点 + 知识链接 + 三段式学习流程（自主学习 A 级/合作探究 B 级/展示提升 C 级）+ 达标测评 + 拓展延伸 D 级 + 反思留空区
  - 使用场景影响排版：公立校完整 5 列教学过程表格、家教简化为 4 列（省略设计意图列）、机构使用完整表格
  - 只导出 status 为 confirmed 的 section（反思区始终保留留空）
  - 中式现代风配色：墨色 `#2c2c2c` 正文、石青 `#3a7ca5` 标题、象牙 `#f0ebe0` 表头
  - 删除 HTML 导出（`_build_export_html`）和 PDF 导出（`_build_simple_pdf`、`build_pdf`）

  **后端端点更新**：
  - 更新 `documents.py` 导出端点：接入真实 `build_docx()` 替换空字节占位
  - 导出文件名包含教案/学案标识（如 `《春》_教案.docx`）

  **前端导出更新**：
  - 重写 `useExport.ts`：删除 `exportPdf`（MVP 不需要），新增 `exportMultipleDocx` 支持批量导出多个 document
  - 更新 `EditorShellHeader.vue`：新增 `hasMultipleDocs` prop，多 document 时显示"导出全部（教案 + 学案）"选项
  - 更新 `useEditorView.ts`：新增 `handleExportAll()` 依次导出教案和学案两个 document
  - 更新 `EditorView.vue`：传递 `hasMultipleDocs` prop 和 `@export-all` event

  **后端测试**：
  - 新建 `tests/test_export.py`：10 个测试覆盖教案基本导出、空内容导出、公立校/家教场景差异、pending section 排除、confirmed section 包含、学案基本导出、学案学生信息、学案测评题、空学案

- 关键文件：
  - `apps/api/app/services/export_service.py`（REWRITE）
  - `apps/api/app/api/v1/endpoints/documents.py`（UPDATE）
  - `apps/web/src/features/export/composables/useExport.ts`（UPDATE）
  - `apps/web/src/features/editor/components/EditorShellHeader.vue`（UPDATE）
  - `apps/web/src/features/editor/composables/useEditorView.ts`（UPDATE）
  - `apps/web/src/features/editor/views/EditorView.vue`（UPDATE）
  - `apps/api/tests/test_export.py`（NEW）
- 验证结果：
  - `python -m ruff check app/`：All checks passed
  - `python -m pytest tests/ -q`：38 passed
  - `npx vue-tsc --noEmit`：passed
  - `pnpm build`：✓ built in 14.31s
- Status: DONE

## [Sprint 6] — 测试 + 收尾

- 完成日期：2026-04-15
- 完成内容：

  **Phase 1：测试文件重组**：
  - 重命名 `test_documents_phase2.py` → `test_documents.py`
  - 重命名 `test_phase3_account.py` → `test_account.py`
  - 重命名 `test_phase7_hardening.py` → `test_security.py`
  - 清理旧 Phase 编号

  **Phase 2：后端单元测试补齐**（38 → 90 个测试，+52 个）：
  - 新建 `tests/test_security_unit.py`：6 个测试覆盖 hash_password/verify_password/JWT 生命周期
  - 新建 `tests/test_auth_service.py`：13 个测试覆盖密码验证、注册、认证、token 生命周期、重置密码
  - 新建 `tests/test_account_service.py`：11 个测试覆盖个人信息更新、密码修改、反馈创建、数据导出、账户删除
  - 新建 `tests/test_task_service.py`：10 个测试覆盖创建（3 种 lesson_type）、分页、权限、复制、级联删除
  - 新建 `tests/test_document_service.py`：10 个测试覆盖内容反序列化、版本管理、快照、冲突检测、历史裁剪
  - 修复 `test_security.py` 中未使用变量 lint 错误

  **Phase 3：覆盖率配置**：
  - 在 `pyproject.toml` 添加 `[tool.coverage.run]` 和 `[tool.coverage.report]`
  - 配置 `fail_under = 80`，`source = ["app"]`
  - 运行 `pytest --cov`：总覆盖率 **88.86%**，超过 80% 门控

  **Phase 4：前端验证**：
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（仅有 Vue 模板格式 warnings，无 error）
  - `pnpm --dir apps/web build`：passed

  **Phase 6：文档更新**：
  - 更新 `GOAL.md`：Sprint 6 标记完成
  - 更新 `PROGRESS.md`：追加 Sprint 6 完成记录
  - 更新 `NEXT.md`：MVP 完成状态

- 关键文件：
  - `apps/api/tests/test_security_unit.py`（NEW）
  - `apps/api/tests/test_auth_service.py`（NEW）
  - `apps/api/tests/test_account_service.py`（NEW）
  - `apps/api/tests/test_task_service.py`（NEW）
  - `apps/api/tests/test_document_service.py`（NEW）
  - `apps/api/tests/api/test_documents.py`（RENAMED）
  - `apps/api/tests/api/test_account.py`（RENAMED）
  - `apps/api/tests/api/test_security.py`（RENAMED）
  - `apps/api/pyproject.toml`（UPDATE — 覆盖率配置）
  - `docs/GOAL.md`（UPDATE）
  - `docs/PROGRESS.md`（UPDATE）
  - `docs/NEXT.md`（UPDATE）
- 验证结果：
  - `python -m ruff check app/ tests/`：All checks passed
  - `python -m pytest tests/ -q`：90 passed
  - `python -m pytest tests/ --cov`：88.86% total coverage（≥ 80% 门控）
  - `npx vue-tsc --noEmit`：passed
  - `pnpm build`：passed
- Status: DONE

---

## Cycle 硬化与拓展阶段（Sprint 0-6 之后）

## [Cycle 1] — 关键 Bug 修复
- 完成日期：2026-04-16
- 完成内容：

  **Bug 1：AI 菜单 mouseleave 消失**
  - 根因：`SectionAiActions.vue` 的 `@mouseleave="closeMenu"` + CSS `top: calc(100% + 6px)` 造成 6px 空隙
  - 修复：CSS 改为 `top: 100%` + `padding-top: 6px`（padding 属于元素内部，不触发 mouseleave）
  - 修复：Vue 组件改为延迟关闭（setTimeout 150ms），mouseenter 时取消定时器
  - 同时将 `z-index: 20` 替换为 `var(--z-dropdown)`

  **Bug 2：列表编辑器不支持多行文本**
  - `GenericListEditor.vue`：将 `<input type="text">` 替换为自动增高的 `<textarea>`
    - Enter 键不再拦截，自然换行
    - 保留 Backspace 在空项时的合并行为
    - 新增项通过底部"+ 添加"按钮
  - `ObjectivesEditor.vue`：同理替换为 `<textarea>`
  - `editor.css`：为 `.item-input` 和 `.objective-content` 添加 `resize: none; overflow: hidden; min-height: 38px; font-family: inherit`
  - 同时将硬编码的 `#fff` 替换为 `var(--surface-strong)`

  **文档更新**：
  - `CLAUDE.md`：当前进度改为 Cycle 硬化阶段，工作流程从 Sprint 改为 Cycle
  - `PROGRESS.md`：追加 Sprint 0-6 完成分隔线 + Cycle 1 记录
  - `NEXT.md`：重写为 Cycle 2 任务清单

- 关键文件：
  - `apps/web/src/features/editor/components/SectionAiActions.vue`（UPDATE）
  - `apps/web/src/features/editor/styles/editor.css`（UPDATE）
  - `apps/web/src/features/editor/components/SectionEditors/GenericListEditor.vue`（REWRITE）
  - `apps/web/src/features/editor/components/SectionEditors/ObjectivesEditor.vue`（REWRITE）
  - `CLAUDE.md`（UPDATE）
  - `docs/PROGRESS.md`（UPDATE）
  - `docs/NEXT.md`（REWRITE）
- 验证结果：
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web lint`：passed（仅有 Vue 模板格式 warnings，无新增 error）
  - `pnpm --dir apps/web build`：passed（✓ built in 13.16s）
- Status: DONE

## [Cycle 2] — 后端加固
- 完成日期：2026-04-16
- 完成内容：

  **2.1 速率限制**
  - 新建 `apps/api/app/core/rate_limit.py`：轻量内存级滑动窗口限流中间件
    - 登录端点：每 IP 每分钟 10 次
    - AI 生成端点：每用户每小时 20 次
    - 通用 API：每 IP 每分钟 60 次
    - 支持通过 `rate_limit_enabled` 配置开关（测试环境可关闭）
  - 修改 `apps/api/app/core/config.py`：添加 4 个限流配置项
  - 修改 `apps/api/app/main.py`：注册 `RateLimitMiddleware`

  **2.2 全局异常处理**
  - 修改 `apps/api/app/main.py`：添加三个异常处理器
    - `RequestValidationError` → 422 + 结构化错误详情
    - `HTTPException` → 统一 JSON 响应格式
    - 通用 `Exception` → 500 + 友好消息 + logger.exception 记录
  - 修改 `apps/api/app/services/generation_service.py`：
    - parse 失败时 `logger.warning` 记录
    - 发送 SSE `warning` 事件通知前端
    - 异常时净化错误消息，不暴露内部细节
  - 修改 `apps/api/app/services/rewrite_service.py`：
    - JSON 解析失败时 `logger.warning` 记录
    - SSE error 事件净化为友好消息
    - 全局 `logger.exception` 记录完整堆栈

  **2.3 前端测试基础**
  - 新建 `apps/web/vitest.config.ts`：vitest 配置（happy-dom、globals、coverage）
  - 修改 `apps/web/package.json`：添加 vitest、@vue/test-utils、happy-dom + test 脚本
  - 新建 `apps/web/src/shared/utils/__tests__/content.test.ts`：18 个测试
    - cloneSerializable、getSectionTitle、getSections
    - update/set/accept 系列、confirmAll、getSectionStatuses
    - getStudyGuideSectionContent
  - 新建 `apps/web/src/features/editor/composables/__tests__/useEditorView.test.ts`：7 个测试
    - 返回属性完整性、空文档安全性、pending/sections 状态

  **文档更新**：
  - `PROGRESS.md`：追加 Cycle 2 记录
  - `NEXT.md`：重写为 Cycle 3 任务清单

- 关键文件：
  - `apps/api/app/core/rate_limit.py`（NEW）
  - `apps/api/app/core/config.py`（UPDATE）
  - `apps/api/app/main.py`（UPDATE）
  - `apps/api/app/services/generation_service.py`（UPDATE）
  - `apps/api/app/services/rewrite_service.py`（UPDATE）
  - `apps/web/vitest.config.ts`（NEW）
  - `apps/web/package.json`（UPDATE）
  - `apps/web/src/shared/utils/__tests__/content.test.ts`（NEW）
  - `apps/web/src/features/editor/composables/__tests__/useEditorView.test.ts`（NEW）
  - `docs/PROGRESS.md`（UPDATE）
  - `docs/NEXT.md`（REWRITE）
- 验证结果：
  - `pytest`：90 passed
  - `ruff check`：All checks passed
  - `pnpm type-check`：passed
  - `pnpm lint`：passed（仅有已有 warnings，无新增 error）
  - `pnpm build`：passed
  - `pnpm test`：25 passed（18 content + 7 useEditorView）
- Status: DONE

## [Cycle 4] — 稳定性优先收口（section 流式 + 本地 BGE + Notion 化）
- 完成日期：2026-04-19
- 完成内容：

  **1. 编辑器稳定性修复**
  - 后端生成与重写统一为 section 级 SSE 协议：`section_start / section_delta / section_document / section_done / document_done`
  - `section_document` 改为回传完整文档载荷，前端不再拿“半个文档”强行合并，类型和运行时一致
  - 学案 `self_study / collaboration / presentation` 全部统一通过 `learning_process` 读写，修复之前会误写到顶层字段的缺陷
  - 编辑器 section 完成后立即合并服务器文档，修复“生成时可见，结束后短暂不可见”的稳定性问题

  **2. RAG 改本地 BGE**
  - 默认 embedding provider 切到 `local_bge + BAAI/bge-m3 + cpu`
  - `.env.example` 与 `apps/api/.env.example` 补齐 `EMBEDDING_PROVIDER / EMBEDDING_MODEL / EMBEDDING_DEVICE / RAG_* / MINIMAX_*`
  - 知识新增接口与种子脚本开始写入 `embedding_runtime` 元数据，便于后续知识版本追踪
  - `seed_knowledge.py` 修复字符串语法错误，新增批量重试与更可读的 embedding 错误日志
  - `knowledge` 端点的 embedding 失败提示改为 provider 感知，不再裸抛内部异常文案

  **3. Notion 风格收口**
  - 工作台、创建页、编辑器主流程按 `DESIGN.md` 做一轮收口：容器宽度、留白、section 卡片密度、工具条降噪、引用徽标区和文档阅读宽度统一
  - 创建页改为显式引入 `workspace.css`，修复直接进入创建页时样式不完整的问题
  - 用户菜单移除主题切换入口，主流程固定亮色；暗色主题降级为内部实验能力

  **4. 文档与说明同步**
  - 新增 `docs/rag-current.md`：说明当前 RAG 能力、边界、配置与后续完善方向
  - 新增 `docs/rag-sales.md`：沉淀客户介绍话术
  - 更新 `CLAUDE.md`、`GOAL.md`、`NEXT.md`，统一为“稳定性优先 + 完全 Notion + RAG 改本地 BGE”的当前口径

- 关键文件：
  - `apps/api/app/services/generation_service.py`
  - `apps/api/app/services/rewrite_service.py`
  - `apps/api/app/services/knowledge_service.py`
  - `apps/api/app/api/v1/endpoints/knowledge.py`
  - `apps/api/scripts/seed_knowledge.py`
  - `.env.example`
  - `apps/api/.env.example`
  - `apps/web/src/features/editor/views/EditorView.vue`
  - `apps/web/src/features/editor/styles/editor.css`
  - `apps/web/src/features/task/styles/workspace.css`
  - `apps/web/src/features/task/views/TaskCreateView.vue`
  - `apps/web/src/shared/components/UserMenu.vue`
  - `docs/rag-current.md`
  - `docs/rag-sales.md`
  - `CLAUDE.md`
  - `docs/GOAL.md`
  - `docs/NEXT.md`

- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m py_compile apps/api/scripts/seed_knowledge.py`：passed
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests -q`：119 passed（2 条既有 Pydantic deprecation warnings）
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web test --run`：25 passed
  - `pnpm --dir apps/web build`：passed
- Status: DONE

## [Cycle 3] — UI/UX 润色
- 完成日期：2026-04-16
- 完成内容：

  **3.1 去 AI 味**
  - 编辑器 UI：替换 8 个文件中的 "AI" 文案
    - `SectionAiActions.vue`：按钮 "AI" → "生成"，title "AI 操作" → "辅助编辑"
    - `EditorStatusBanner.vue`："AI 正在重写" → "正在重写"，fallback "教案内容" → "内容"
    - `useEditorGeneration.ts`：toast "本节 AI 内容已生成" → "本节内容已生成"，错误消息净化
    - `useEditorRewrite.ts`：toast "AI 重写完成" → "重写完成"，错误 "AI 重写失败" → "重写失败"
    - `HistoryDrawer.vue`：历史标签 "AI 生成" → "自动生成"，"AI 重写" → "重写"
    - `ExportPreviewModal.vue`："先接受 AI 建议" → "先接受建议内容"，fallback "教案预览" → "文档预览"
    - `TaskCreateView.vue`：toast "你会看到 AI 逐步输出内容" → "内容将逐步生成到编辑器中"
    - `TaskListView.vue`："AI 帮你快速生成" → "快速生成教案"，"体验 AI 备课" → "开启高效备课"
    - `HeroProductPreview.vue`："AI 生成中" → "生成中"，"AI 待确认" → "待确认"，"AI 补充内容" → "补充内容"
  - 营销文案：替换 6 个文件中的 "AI" 表述
    - `AuthLayout.vue`："AI 内联" → 删除，"AI 先给你骨架" → "自动生成骨架"
    - `LandingView.vue`：eyebrow 和 hero text 重写
    - `PublicFooter.vue`："AI 备课助手" → "备课助手"
    - `AboutView.vue`："AI 备课工具" → "备课工具"
    - `HelpView.vue`："AI 行为" → "生成行为"
    - `PricingView.vue`："局部 AI 重写" → "局部重写"
  - `content.ts`：重写 20+ 处 AI 文案
    - 功能标题 "AI 生成结构化教案" → "一键生成结构化教案"
    - 功能描述 "AI 帮你重写" → "一键重写"，"局部 AI 润色" → "局部润色"
    - FAQ 标题 "AI 功能" → "生成与编辑"，重写所有 FAQ 问答
    - 隐私政策 "AI 备课" → "备课服务"，"训练 AI 模型" → "训练模型"
    - 条款 "AI 内容免责声明" → "内容免责声明"
    - 更新日志 "AI 生成/AI 补充" → "自动生成/补充"

  **3.2 术语统一**
  - "回到备课台" → "返回备课台"：修复 4 个文件（EditorView、NotFoundView、NetworkErrorView、ServerErrorView）
  - "查看帮助" → "去帮助中心"：修复 NetworkErrorView
  - 学案 fallback 文案：EditorShellHeader "教案编辑器" → "文档编辑器"，ExportPreviewModal "教案预览" → "文档预览"

  **3.3 设计令牌迁移**
  - 新增令牌（main.css :root + dark）：
    - 颜色：`--secondary`、`--warning`、`--on-primary`
    - RGB 通道：`--primary-rgb`、`--text-rgb`、`--danger-rgb`、`--success-rgb`、`--secondary-rgb`、`--accent-rgb`、`--white-rgb`、`--cream-rgb`、`--shadow-dark-rgb`、`--backdrop-rgb`
    - 语义令牌：`--text-secondary`、`--surface-secondary`、`--surface-cream`、`--secondary-soft`、`--secondary-border`
    - 复合令牌：`--ring`、`--ring-visible`、`--shadow-dropdown`、`--shadow-elevated`
  - 替换 main.css 中所有硬编码色值为 var() 引用
  - 替换 public.css 中 ~30 处硬编码 rgba + hex 为令牌引用
  - 替换 editor.css 中 ~30 处硬编码 rgba + hex 为令牌引用
  - 替换 workspace.css 中 ~7 处硬编码色值为令牌引用
  - 替换 settings.css 中 ~9 处硬编码色值为令牌引用
  - 修复 2 个 phantom token（`--text-secondary`、`--surface-secondary`）定义缺失问题

- 关键文件：
  - `apps/web/src/shared/styles/main.css`（UPDATE — 令牌系统扩展）
  - `apps/web/src/features/public/styles/public.css`（UPDATE — 色值迁移）
  - `apps/web/src/features/editor/styles/editor.css`（UPDATE — 色值迁移）
  - `apps/web/src/features/task/styles/workspace.css`（UPDATE — 色值迁移）
  - `apps/web/src/features/settings/styles/settings.css`（UPDATE — 色值迁移）
  - `apps/web/src/features/editor/components/SectionAiActions.vue`（UPDATE）
  - `apps/web/src/features/editor/components/EditorStatusBanner.vue`（UPDATE）
  - `apps/web/src/features/editor/composables/useEditorGeneration.ts`（UPDATE）
  - `apps/web/src/features/editor/composables/useEditorRewrite.ts`（UPDATE）
  - `apps/web/src/features/editor/components/HistoryDrawer.vue`（UPDATE）
  - `apps/web/src/features/editor/components/ExportPreviewModal.vue`（UPDATE）
  - `apps/web/src/features/editor/components/EditorShellHeader.vue`（UPDATE）
  - `apps/web/src/features/task/views/TaskCreateView.vue`（UPDATE）
  - `apps/web/src/features/task/views/TaskListView.vue`（UPDATE）
  - `apps/web/src/features/public/components/HeroProductPreview.vue`（UPDATE）
  - `apps/web/src/app/layouts/AuthLayout.vue`（UPDATE）
  - `apps/web/src/features/public/views/LandingView.vue`（UPDATE）
  - `apps/web/src/features/public/components/PublicFooter.vue`（UPDATE）
  - `apps/web/src/features/public/views/AboutView.vue`（UPDATE）
  - `apps/web/src/features/public/views/HelpView.vue`（UPDATE）
  - `apps/web/src/features/public/views/PricingView.vue`（UPDATE）
  - `apps/web/src/features/public/views/NotFoundView.vue`（UPDATE）
  - `apps/web/src/features/public/views/NetworkErrorView.vue`（UPDATE）
  - `apps/web/src/features/public/views/ServerErrorView.vue`（UPDATE）
  - `apps/web/src/features/public/content.ts`（UPDATE）
  - `docs/PROGRESS.md`（UPDATE）
  - `docs/NEXT.md`（REWRITE）
- 验证结果：
  - `pytest`：90 passed
  - `ruff check`：All checks passed
  - `pnpm type-check`：passed
  - `pnpm lint`：passed（仅有已有 warnings，无新增 error）
  - `pnpm build`：passed
  - `pnpm test`：25 passed（18 content + 7 useEditorView）
- Status: DONE

## [Cycle 4] — Section 生成兼容性热修复
- 完成日期：2026-04-19
- 完成内容：
  - 为 `objectives / collaboration / presentation / assessment` 等结构化 section 增加模型返回归一化兼容层，支持常见字段别名、中文枚举和值形态后再做 schema 校验，避免解析失败后直接回退为空
  - 空 section 上点击“生成”时，不再机械沿用空内容重写逻辑；后端会改走 section 重新生成链路
  - `reflection / self_reflection` 在老师显式点击生成时，改为生成可编辑的反思草稿，不再固定回退为空字符串
  - 修正后端 `KeyPoints` 的 `keyPoints` / `key_points` 兼容与序列化，收口一处前后端结构不一致
  - 补充回归测试，覆盖目标归一化、题目归一化、空目标生成、空反思草稿生成
- 关键文件：
  - `apps/api/app/schemas/content.py`
  - `apps/api/app/services/generation_service.py`
  - `apps/api/app/services/rewrite_service.py`
  - `apps/api/tests/test_content_schema.py`
  - `apps/api/tests/test_generation_service.py`
  - `apps/api/tests/api/test_documents.py`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests -q`：123 passed（保留 2 条既有 Pydantic deprecation warnings）
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
- Status: DONE

## [Cycle 4] — RAG 文档补充与知识入库验真
- 完成日期：2026-04-20
- 完成内容：
  - 新增面向小白的 RAG 说明文档，系统讲清楚 LessonPilot 中知识入库、embedding、检索、prompt 注入、citation 与 `section_references` 的整条链路
  - 补齐“为什么这次没有触发 RAG”的排查说明，明确区分“路由命中但知识库为空”和“真正检索命中并写入引用”这两种状态
  - 在本地 API 虚拟环境安装缺失依赖 `sentence-transformers` 与 `torch`，恢复本地 `BGE-M3` embedding 能力
  - 重新执行知识入库脚本，成功写入 16 条《红楼梦》知识卡，恢复语文文学类课题的知识增强生成基础
  - 通过真实后端生成链路重新生成“薛宝钗人物分析（RAG验证）”，确认生成过程中出现 citation 事件，且最终文档 `section_references` 非空
  - 核验到 lesson plan 的 `preparation / board_design` 与 study guide 的 `learning_objectives / key_difficulties / prior_knowledge` 已落入真实引用来源，证明这次不是普通生成而是 RAG 生效
- 关键文件：
  - `docs/rag-implementation.md`
  - `apps/api/scripts/seed_knowledge.py`
  - `apps/api/app/services/knowledge_service.py`
  - `apps/api/app/core/config.py`
- 验证结果：
  - `cd apps/api && .\.venv\Scripts\python.exe -m scripts.seed_knowledge`：成功入库，`knowledge_chunks = 16`
  - 真实生成验证任务：`ef57f1ef-86ed-47bf-b570-9375c3ccc885`
  - lesson plan 文档：`34590d92-a638-49ca-987c-21177d3a456f`，`section_references` 非空
  - study guide 文档：`3ff51269-fcd8-4f21-ac99-780b1315b84d`，`section_references` 非空
- Status: DONE

## [Cycle 4] — 前端卡片层级与去 AI 感文案收口
- 完成日期：2026-04-20
- 完成内容：
  - 重做前端共享表面体系，`app-card` 默认改为 whisper border + 无阴影，状态卡补齐统一样式，避免页面壳层、内容卡和浮层全部使用同等级阴影
  - 收口公域页、Auth、备课台、创建页、设置页的卡片密度与留白节奏，减少“大卡套小卡”叠加感，让主页面更接近 `DESIGN.md` 的 Notion 式文档层级
  - 收口编辑器壳层：顶部 header 改为轻量顶栏，outline panel 更窄更轻，主文档面板成为唯一视觉中心；section 引用区与流式区改成内嵌提示条
  - 统一主流程文案，弱化 `AI / 生成 / 重写 / 扩写` 的工具感表达，改为“起草 / 整理 / 改写 / 补充展开 / 压缩表达”等老师视角语言；帮助、隐私、条款仍保留必要真实披露
  - 新增前端断言，覆盖 Landing 主文案、创建页主文案与 CTA、编辑器 section 操作标签，并保留原有 action enum 契约不变
  - 顺手清理一批前端 lint error（未使用导入、未使用变量、正则转义），让前端 lint quiet、测试和构建恢复通过
- 关键文件：
  - `apps/web/src/shared/styles/main.css`
  - `apps/web/src/features/public/styles/public.css`
  - `apps/web/src/features/task/styles/workspace.css`
  - `apps/web/src/features/editor/styles/editor.css`
  - `apps/web/src/features/public/content.ts`
- 验证结果：
  - `pnpm --dir apps/web test`：29 passed
  - `pnpm --dir apps/web lint -- --quiet`：passed
  - `pnpm --dir apps/web build`：passed（含 `vue-tsc`）
- Status: DONE

## [Cycle 4] — 产品文档与 Codex skills 基础建设
- 完成日期：2026-04-26
- 完成内容：
  - 创建 7 个 LessonPilot 专用 Codex skills：
    - `lessonpilot-product-strategist`：产品策略、竞品迁移、路线图优先级
    - `lessonpilot-teaching-quality-reviewer`：教案/学案内容质量审查
    - `lessonpilot-word-template-importer`：学校 Word 模板识别与字段映射
    - `lessonpilot-legacy-material-ingestor`：旧 Word/PPT/讲义/资料迁移到结构化内容
    - `lessonpilot-rag-knowledge-pack-builder`：语文 RAG 知识包设计、入库与引用验证
    - `lessonpilot-export-quality-checker`：导出前体检与 Word 提交质量检查
    - `lessonpilot-cycle-maintainer`：`NEXT / PROGRESS / GOAL / CLAUDE` 等文档状态维护
  - 新增产品与执行文档，沉淀产品定位、竞品迁移策略、老师真实工作流、质量标准、验收脚本和路线图
  - 新增 `docs/specs/` 技术契约文档，记录内容模型、section SSE、Word 导出和 RAG 规格
  - 新增 ADR，明确“结构化 JSON 是内容中枢”的架构决策
  - 更新 `docs/NEXT.md`，把新增 docs 与 skills 纳入本轮待验收项，但不自动进入下一阶段
- 关键文件：
  - `docs/PRODUCT.md`（NEW）
  - `docs/COMPETITIVE.md`（NEW）
  - `docs/TEACHER_WORKFLOWS.md`（NEW）
  - `docs/QUALITY_RUBRIC.md`（NEW）
  - `docs/ACCEPTANCE.md`（NEW）
  - `docs/ROADMAP.md`（NEW）
  - `docs/specs/content-model.md`（NEW）
  - `docs/specs/section-sse.md`（NEW）
  - `docs/specs/export-docx.md`（NEW）
  - `docs/specs/rag.md`（NEW）
  - `docs/decisions/ADR-0001-structured-json-as-core.md`（NEW）
  - `docs/NEXT.md`（UPDATE）
  - `C:/Users/realfeeling1/.codex/skills/lessonpilot-*`（NEW）
- 验证结果：
  - 7 个新增 skill 均已通过 `quick_validate.py` 结构校验（使用 `PYTHONUTF8=1` 规避 Windows 默认 GBK 解码问题）
  - 本次仅新增文档和本地 Codex skills，未改动产品运行代码，未运行前后端测试
- Status: DONE（待用户确认新增文档与 skills 方向）

## [Cycle 4] — Agent 入口文档同步与提交准备
- 完成日期：2026-04-26
- 完成内容：
  - 完善 `AGENTS.md`：明确正式工作前先读行为约束，再读 `CLAUDE / NEXT / PROGRESS`，并补充文档口径冲突时的优先级
  - 在 `AGENTS.md` 中加入 7 个 LessonPilot 专用 Codex skills 的使用场景，方便后续 agent 按任务触发
  - 完善 `CLAUDE.md`：补齐 `docs/` 文档地图、当前新增文档状态和专用 skills 使用口径
  - 更新 `docs/NEXT.md`，将 `AGENTS / CLAUDE` 同步纳入本轮已完成事项
  - 准备按用户要求提交并推送当前 `ai` 分支
- 关键文件：
  - `AGENTS.md`
  - `CLAUDE.md`
  - `docs/NEXT.md`
  - `docs/PROGRESS.md`
- 验证结果：
  - 本次仅同步项目文档入口，未改动产品运行代码，未运行前后端测试
- Status: DONE（待提交推送）

## [Cycle 4] — 阶段级自动执行 Skill
- 完成日期：2026-04-26
- 完成内容：
  - 新增 `lessonpilot-phase-autopilot-runner` 本机 Codex skill，用于在用户明确授权的阶段内自动拆分多个内部 Cycle 并持续推进
  - 明确该 skill 的边界：不能切换 Plan mode、不能自动替用户验收、不能绕过 `AGENTS.md`、不能无授权进入下一阶段
  - 为该 skill 补充 phase charter、execution loop、stop gates 三份 reference，要求先有阶段目标、范围、验收标准和提交推送策略
  - 同步 `AGENTS.md / CLAUDE.md / docs/NEXT.md` 中的 skills 列表，从 7 个扩展为 8 个
- 关键文件：
  - `AGENTS.md`
  - `CLAUDE.md`
  - `docs/NEXT.md`
  - `docs/PROGRESS.md`
  - `C:/Users/realfeeling1/.codex/skills/lessonpilot-phase-autopilot-runner`（NEW）
- 验证结果：
  - `lessonpilot-phase-autopilot-runner` 已通过 `quick_validate.py` 结构校验（使用 `PYTHONUTF8=1`）
  - 本次未改动产品运行代码，未运行前后端测试
- Status: DONE

## [Phase 5] — 知识可信闭环自动推进至验收口
- 完成日期：2026-04-26
- 完成内容：
  - 新增语文重点篇目知识包 manifest，首批覆盖 `红楼梦 / 春 / 背影 / 桃花源记 / 岳阳楼记 / 天净沙·秋思`
  - 将 RAG 课题路由从代码常量迁移到知识包配置，支持 trigger terms 命中证据
  - 重写知识入库脚本，写入 `pack_id / pack_version / trigger_terms / embedding_runtime`，并以 `domain + title` 避免重复入库
  - 新增 `POST /api/v1/knowledge/diagnose`，返回 `disabled / unmatched / matched_empty / ready / degraded` 等老师可理解状态
  - 生成 SSE 新增 `rag_status` 事件，编辑器状态条展示知识增强命中、未命中和降级提示
  - 修复 Pydantic section 值中的 `[cite:...]` 未被递归清洗的问题，提升 `section_references` 落库可靠性
  - DeepSeek 配置切到 `deepseek-v4-flash`，并通过 `DEEPSEEK_THINKING=disabled` 显式关闭 thinking
  - 更新 `docs/NEXT.md`、`docs/milestones/phase-5-knowledge-trust.md`、`docs/specs/rag.md`、`docs/specs/section-sse.md`、`docs/rag-current.md`、`docs/ACCEPTANCE.md`
- 关键文件：
  - `apps/api/app/data/knowledge_packs/chinese_literature_v1.json`
  - `apps/api/app/services/knowledge_pack_service.py`
  - `apps/api/app/services/knowledge_service.py`
  - `apps/api/app/services/generation_service.py`
  - `apps/api/app/api/v1/endpoints/knowledge.py`
  - `apps/api/scripts/seed_knowledge.py`
  - `apps/web/src/features/editor/components/EditorStatusBanner.vue`
  - `apps/web/src/features/editor/composables/useEditorGeneration.ts`
  - `.env.example`
  - `apps/api/.env.example`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests -q`：131 passed（保留 2 条既有 Pydantic deprecation warning）
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web test --run`：31 passed
  - `pnpm --dir apps/web build`：passed
  - `docker compose up -d postgres`：本地 `pgvector/pgvector:pg16` PostgreSQL 已启动并 healthy
  - `cd apps/api && .\.venv\Scripts\python.exe -m scripts.seed_knowledge`：passed，成功导入 16 条新知识；第二次执行显示“没有新的知识条目需要导入”
  - 本地知识库当前 `knowledge_chunks = 32`：`红楼梦=17`、`春=3`、`背影=3`、`桃花源记=3`、`岳阳楼记=3`、`天净沙·秋思=3`
  - 真实向量检索验证：`红楼梦薛宝钗人物分析`、`春 朱自清 第一课时`、`桃花源记文言文教学` 均命中对应 domain 并召回 3 条 chunk
- Status: DONE（待用户验收，不自动提交推送）

## [Phase 6] — 迁移与提交闭环自动推进至验收口
- 完成日期：2026-04-27
- 完成内容：
  - 新增 `.docx` 旧教案导入预览接口：识别教学目标、教学重难点、教学准备、教学过程、板书设计、教学反思，并保留未识别内容与 warning
  - 新增导入确认接口：将预览结果创建为普通 `Task + Document`，导入内容默认保持 `pending`
  - 新增导出前体检接口：返回 `ready / needs_fixes / blocked`、问题、提醒和修复建议
  - 前端新增 `/tasks/import` 导入旧教案页面，备课台和创建页均可进入，支持上传、预览、元信息修正与确认导入
  - 编辑器新增导出前体检按钮与结果面板，阻断项暂不建议导出，提醒项可由老师确认后继续导出
  - 更新 `docs/NEXT.md`、`docs/milestones/phase-6-migration-submission.md`、`docs/specs/import-docx.md`、`docs/specs/export-docx.md`、`docs/ACCEPTANCE.md`
- 关键文件：
  - `apps/api/app/services/import_service.py`
  - `apps/api/app/services/quality_service.py`
  - `apps/api/app/api/v1/endpoints/imports.py`
  - `apps/api/app/api/v1/endpoints/documents.py`
  - `apps/api/app/schemas/lesson_import.py`
  - `apps/api/app/schemas/quality.py`
  - `apps/web/src/features/task/views/LessonPlanImportView.vue`
  - `apps/web/src/features/editor/components/ExportQualityPanel.vue`
  - `apps/web/src/features/editor/composables/useEditorView.ts`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests -q`：138 passed（保留 2 条既有 Pydantic deprecation warning）
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web test --run`：34 passed
  - `pnpm --dir apps/web build`：passed
- Status: DONE（待用户验收，不自动提交推送）

## [Phase 7-10] — 学校格式与个人备课资产闭环自动推进至验收口
- 完成日期：2026-04-27
- 完成内容：
  - 新增学校 Word 模板上传预览、确认保存、个人模板列表和删除能力，模板保存为结构化 export spec
  - 将模板归属扩展到用户维度，Word 导出支持 `template_id`，可按个人学校模板渲染元信息、栏目顺序、教学过程表格列和空白区域
  - 导出前体检升级为质量检查 2.0，新增目标空泛、目标-过程承接、重难点展开、学生活动主动性、学案测评覆盖等检查，并返回 `alignment_map`
  - 新增上课包生成能力，从已确认教案生成学案草稿、PPT 大纲和课堂口播稿，所有内容默认 pending
  - 新增个人资料库，支持 `.docx` / `.pptx` 上传预览、确认保存、列表、删除和用户隔离
  - 前端备课台新增“学校模板”“个人资料库”入口，编辑器新增学校模板选择与上课包面板，体检面板展示一致性结果
  - 更新 `docs/NEXT.md`、`docs/milestones/phase-7-10-teaching-asset-loop.md`、`docs/specs/school-template.md`、`docs/specs/quality-check-v2.md`、`docs/specs/teaching-package.md`、`docs/specs/personal-assets.md`、`docs/specs/export-docx.md`、`docs/ACCEPTANCE.md`
- 关键文件：
  - `apps/api/app/services/template_service.py`
  - `apps/api/app/services/export_service.py`
  - `apps/api/app/services/quality_service.py`
  - `apps/api/app/services/personal_asset_service.py`
  - `apps/api/app/services/teaching_package_service.py`
  - `apps/web/src/features/task/views/SchoolTemplatesView.vue`
  - `apps/web/src/features/task/views/PersonalAssetsView.vue`
  - `apps/web/src/features/editor/components/TeachingPackagePanel.vue`
  - `apps/web/src/features/editor/components/ExportQualityPanel.vue`
- 验证结果：
  - `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests -q`：142 passed
  - `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
  - `pnpm --dir apps/web type-check`：passed
  - `pnpm --dir apps/web test --run`：38 passed
  - `pnpm --dir apps/web build`：passed
- Status: DONE（待用户验收，不自动提交推送）

## [Phase 7-10] — 本地前端端口规则收口
- 完成日期：2026-04-27
- 完成内容：
  - 明确本地前端开发服务固定使用 `5173`
  - 若 `5173` 被占用，后续 agent 需先释放占用进程，再重新使用 `5173`
  - 禁止未经用户明确指定时临时切换到 `5174` 或其他端口
- 关键文件：
  - `AGENTS.md`
  - `CLAUDE.md`
- 验证结果：
  - 已停止 `5173` 与 `5174` 上的旧前端监听进程
- Status: DONE（规则已写入，不涉及用户验收）
