# LessonPilot 实施计划 v2

> 状态：draft
> 日期：2026-04-14
> 基于：product-replan-v2.md

---

## 代码审查结论

### 后端

| 组件 | 判定 | 说明 |
|------|------|------|
| `core/config.py` | ADAPT | 添加 MiniMax 配置，精简 billing/admin/sentry 字段 |
| `core/security.py` | REUSE | JWT + bcrypt 认证完整可用 |
| `core/db.py` | REUSE | 数据库连接池配置 OK |
| `models/user.py` | REUSE | 用户模型完整 |
| `models/task.py` | ADAPT | 新增 `scene`（使用场景）、`lesson_type`（教案/学案/都生成）、`class_hour`（课时）、`lesson_category`（课型）字段 |
| `models/document.py` | ADAPT | `doc_type` 扩展为 `lesson_plan | study_guide`，content JSON 结构改为教案/学案模板 |
| `services/auth_service.py` | REUSE | 完整可用 |
| `services/llm_service.py` | REWRITE | 完全重写：新 Provider 架构 + 真正流式输出 + 新 prompt |
| `services/generation_service.py` | REWRITE | 完全重写：新内容模型 + 一次性流式生成 |
| `services/rewrite_service.py` | REWRITE | 重写为 section 级操作 |
| `services/append_service.py` | DELETE | 功能合并到 rewrite |
| `services/export_service.py` | REWRITE | 学校标准格式 Word 导出 |
| `services/billing_service.py` | DELETE | MVP 暂不需要 |
| `services/admin_service.py` | DELETE | MVP 暂不需要 |
| `services/analytics_service.py` | DELETE | MVP 暂不需要 |
| `services/mail_service.py` | ADAPT | 保留注册验证邮件，精简其他 |
| `schemas/content.py` | REWRITE | 从 8 种 block → 教案/学案结构化模型 |
| `pyproject.toml` | ADAPT | 添加 httpx（MiniMax 用），精简依赖 |

### 前端

| 组件 | 判定 | 说明 |
|------|------|------|
| `shared/api/client.ts` | REUSE | HTTP 客户端完整可用 |
| `shared/api/errors.ts` | ADAPT | 精简为 MVP 需要的错误类型 |
| `app/stores/auth.ts` | REUSE | 认证 store 完整 |
| `app/router/index.ts` | ADAPT | 移除 admin/多余路由，调整创建流程 |
| `features/auth/` | REUSE | 登录/注册完整，仅调 UI |
| `features/editor/` | REWRITE | 完全重写为 Section Editor |
| `features/task/` | ADAPT | 创建页改为一站式，列表页调 UI |
| `features/public/` | REWRITE | 中式现代风 UI 重设计 |
| `features/export/` | REWRITE | 新导出流程 |
| `features/generation/` | REWRITE | 真正流式消费 |
| `features/admin/` | DELETE | MVP 不需要 |
| `features/analytics/` | DELETE | MVP 不需要 |
| `features/onboarding/` | DELETE | MVP 不需要 |
| `features/feedback/` | DELETE | MVP 不需要 |
| `features/billing/` | DELETE | MVP 不需要（保留基础 store） |
| `shared/styles/` | REWRITE | 中式现代风设计系统 |
| `entry-server.ts` | DELETE | MVP 不做 SSR |
| `server.mjs` | DELETE | MVP 不做 SSR |

---

## 实施阶段

### Sprint 0：项目清理与准备（1-2 小时）

**目标**：清理不需要的代码，建立新的基础

**后端**：
- [ ] 删除不需要的 service 文件：`billing_service.py`、`admin_service.py`、`analytics_service.py`、`append_service.py`
- [ ] 删除不需要的 model 文件：`billing_order.py`、`billing_webhook_event.py`、`invoice_request.py`、`user_subscription.py`、`quota_adjustment.py`、`analytics_event.py`、`email_delivery_log.py`
- [ ] 删除不需要的 endpoint 文件：`billing.py`、`admin.py`、`analytics.py`
- [ ] 删除不需要的 schema 文件：`billing.py`、`admin.py`、`analytics.py`
- [ ] 精简 `models/__init__.py`，只导出 User、Task、Document、DocumentSnapshot、AuthToken、Feedback
- [ ] 精简 `router.py`，只保留 auth、tasks、documents、health、account
- [ ] 精简 `config.py`，移除 billing/admin/sentry 相关字段，添加 MiniMax 配置
- [ ] 精简 `pyproject.toml`，移除 weasyprint、sentry-sdk、slowapi 依赖
- [ ] 更新 `main.py`，移除 Sentry 和 SlowAPI 中间件
- [ ] 删除 `core/rate_limit.py`、`core/sentry.py`、`core/streaming.py`

**前端**：
- [ ] 删除不需要的 feature 目录：admin、analytics、onboarding、feedback、billing
- [ ] 删除 SSR 相关文件：`entry-server.ts`、`server.mjs`
- [ ] 精简 `package.json`，移除 @sentry、@vue/server-renderer、express、compression
- [ ] 精简 `vite.config`，移除 SSR 配置
- [ ] 简化 `build` 脚本，只做 SPA 构建
- [ ] 清理 router，移除 admin/多余路由

### Sprint 1：内容模型 + AI 服务重写（核心，3-4 小时）

**目标**：建立新的内容数据模型和 AI 生成服务

**后端 - 新内容 Schema**：
- [ ] 重写 `schemas/content.py`：
  - `LessonPlanContent`（教案结构）
  - `StudyGuideContent`（学案结构）
  - `TeachingObjective`（教学目标）
  - `TeachingProcessStep`（教学过程步骤：含教师活动/学生活动/设计意图）
  - `AssessmentQuestion`（达标测评题目，含 ABCD 分级）
  - `BoardDesign`（板书设计）
- [ ] 重写 `schemas/task.py`：新增 `scene`、`lesson_type`、`class_hour`、`lesson_category` 字段
- [ ] 重写 `schemas/document.py`：适配新内容结构
- [ ] 新建 `schemas/lesson.py`：教案/学案生成相关 schema

**后端 - AI 服务重写**：
- [ ] 重写 `services/llm_service.py`：
  - 抽象 `LLMProvider` 接口（Protocol）
  - 实现 `DeepSeekProvider`（改造现有）
  - 实现 `MiniMaxProvider`（新增）
  - 保留 `FakeProvider`（开发测试用）
  - 所有 Provider 支持真正的 **token-by-token 流式输出**
  - 新的 prompt 模板，聚焦教学内容质量
- [ ] 新建 prompt 模板：
  - `lesson_plan_generation_prompt.md`：教案生成（一次性，语文）
  - `study_guide_generation_prompt.md`：学案生成
  - `section_rewrite_prompt.md`：Section 级重写
- [ ] 重写 `services/generation_service.py`：
  - 一次性流式生成完整教案/学案
  - 按 section 顺序逐步输出
  - 支持同时生成教案+学案
  - 支持 `scene` 影响 prompt 内容和详细程度
- [ ] 重写 `services/rewrite_service.py`：
  - Section 级重写/扩写/精简
  - 流式输出

**后端 - Task/Document 更新**：
- [ ] 更新 `models/task.py`：新增字段
- [ ] 更新 `models/document.py`：适配新内容结构
- [ ] 更新 `services/task_service.py`：适配新字段
- [ ] 更新 `services/document_service.py`：适配新内容结构
- [ ] 更新 `api/v1/endpoints/tasks.py`：新创建参数
- [ ] 更新 `api/v1/endpoints/documents.py`：新文档操作
- [ ] 新建 Alembic 迁移

**前端 - 类型更新**：
- [ ] 重写 `packages/shared-types/src/content.ts`：新的教案/学案类型定义
- [ ] 重写 `shared/utils/content.ts`：新的内容操作工具

### Sprint 2：前端 UI 重设计（中式现代风，3-4 小时）

**目标**：全局视觉系统重设计

**设计系统**：
- [ ] 重写 `shared/styles/main.css`：
  - 新配色：宣纸白 `#faf8f3`、石青 `#3a7ca5`、胆黄 `#d4a843`、墨色 `#2c2c2c`
  - 新字体：思源宋体（标题）+ 系统无衬线体（正文）
  - 8-12px 圆角（不是 18-28px）
  - 细线边框，轻投影
  - 中式装饰元素（可选的细微纹样）
  - 保持响应式和暗色模式基础

**Landing 页**：
- [ ] 重写 `features/public/views/LandingView.vue`：中式现代风
- [ ] 重写 `features/public/styles/public.css`
- [ ] 更新 `features/public/components/PublicNav.vue`
- [ ] 更新 `features/public/components/PublicFooter.vue`

**认证页**：
- [ ] 更新 `app/layouts/AuthLayout.vue`：中式现代风
- [ ] 更新 `features/auth/views/LoginView.vue`
- [ ] 更新 `features/auth/views/RegisterView.vue`

**备课台**：
- [ ] 重写 `features/task/views/TaskListView.vue`：中式现代风卡片列表
- [ ] 重写 `features/task/styles/workspace.css`

### Sprint 3：创建页 + 流式生成体验（2-3 小时）

**目标**：一站式创建 + AI 流式生成

**创建页**：
- [ ] 重写 `features/task/views/TaskCreateView.vue`：
  - 一站式布局：学科/年级/课题/课时/课型 + 教案/学案/都生成 + 使用场景 + 补充要求
  - 中式现代风 UI
  - 提交后直接进入编辑器（同页面切换为编辑模式）

**流式生成消费**：
- [ ] 重写 `features/generation/useGeneration.ts`：
  - 真正的 token-by-token 流式消费
  - 解析 SSE 中的 JSON delta
  - 实时更新编辑器内容
  - 支持停止生成

**编辑器 - 流式显示**：
- [ ] 新建 `features/editor/components/StreamingText.vue`：文字逐字出现的动画组件

### Sprint 4：Section Editor + AI 重写（3-4 小时）

**目标**：文档式编辑器

**编辑器重写**：
- [ ] 重写 `features/editor/views/EditorView.vue`：
  - Tab 切换：教案 / 学案
  - Section 级折叠/展开
  - 直接点击编辑文字
  - 自动保存
  - 简单富文本（加粗/列表/缩进）
- [ ] 重写 `features/editor/composables/useEditorView.ts`：
  - 简化（当前 1170 行 → 目标 <500 行）
  - 管理教案/学案内容状态
  - 自动保存逻辑
  - AI 操作入口
- [ ] 新建 `features/editor/components/SectionPanel.vue`：可折叠的 section 面板
- [ ] 新建 `features/editor/components/SectionEditor.ts`：section 内富文本编辑
- [ ] 新建 `features/editor/components/EditorToolbar.vue`：简洁工具栏
- [ ] 重写 `features/editor/styles/editor.css`：中式现代风 + 宣纸色背景
- [ ] 简化 `features/editor/components/EditorShellHeader.vue`：标题 + 保存状态 + 导出按钮

**AI 重写 UI**：
- [ ] 新建 `features/editor/components/SectionAiActions.vue`：Section 级 AI 操作按钮
- [ ] Section 级重写/扩写/精简的交互流程

### Sprint 5：导出重写（1-2 小时）

**目标**：学校标准格式 Word 导出

**后端导出**：
- [ ] 重写 `services/export_service.py`：
  - 教案 Word：表头 + 三维目标 + 表格式教学过程 + 板书设计
  - 学案 Word：学生信息栏 + 学习目标 + 分层题目 + 反思区
  - 使用场景影响导出格式（公立校严格 / 家教简化 / 机构中等）
  - 排版体现中式审美

**前端导出**：
- [ ] 重写 `features/export/useExport.ts`：
  - 选择导出教案/学案/都导出
  - 下载 Word 文件

### Sprint 6：测试 + 收尾（1-2 小时）

**后端测试**：
- [ ] 重写 `tests/conftest.py`：适配新模型
- [ ] 重写 `tests/api/test_auth.py`：保留基本 auth 测试
- [ ] 新建 `tests/test_lesson_content.py`：教案/学案内容 schema 验证
- [ ] 新建 `tests/api/test_generation.py`：AI 生成流式测试
- [ ] 新建 `tests/api/test_export.py`：导出格式测试
- [ ] 运行完整测试套件

**前端验证**：
- [ ] `pnpm type-check` 通过
- [ ] `pnpm lint` 通过
- [ ] `pnpm build` 通过
- [ ] 手动验证核心流程：创建 → 生成 → 编辑 → 导出

**文档更新**：
- [ ] 更新 `GOAL.md`：新里程碑结构
- [ ] 更新 `PROGRESS.md`：记录重做过程
- [ ] 更新 `NEXT.md`：当前状态
- [ ] 更新 `CLAUDE.md`/`AGENTS.md`：新架构说明

---

## 工作量估算

| Sprint | 范围 | 预估时间 |
|--------|------|---------|
| Sprint 0 | 项目清理 | 1-2 小时 |
| Sprint 1 | 内容模型 + AI | 3-4 小时 |
| Sprint 2 | UI 重设计 | 3-4 小时 |
| Sprint 3 | 创建 + 流式 | 2-3 小时 |
| Sprint 4 | 编辑器 | 3-4 小时 |
| Sprint 5 | 导出 | 1-2 小时 |
| Sprint 6 | 测试收尾 | 1-2 小时 |
| **总计** | | **14-21 小时** |

---

## 关键技术决策

### 1. 流式输出实现

**后端**：
- 使用 FastAPI 的 `StreamingResponse` + `text/event-stream`
- 每个 chunk 是一个 JSON delta：`{"section": "teaching_objectives", "delta": "..."}`
- AI Provider 使用 `stream=True` 调用 LLM API，逐 token 读取并转发

**前端**：
- 使用 `fetch` + `ReadableStream` 消费 SSE
- 解析每个 delta，实时更新对应 section 的内容
- 使用 Vue 的响应式系统自动渲染更新

### 2. 内容存储格式

Document 的 `content` JSON 字段存储完整的教案/学案结构：
```json
{
  "type": "lesson_plan",
  "header": { "title": "...", "subject": "...", "grade": "...", ... },
  "sections": [
    { "id": "...", "type": "objectives", "title": "教学目标", "content": "...", "collapsed": false },
    { "id": "...", "type": "key_points", "title": "教学重难点", "content": "...", "collapsed": false },
    { "id": "...", "type": "teaching_process", "title": "教学过程",
      "steps": [
        { "phase": "导入新课", "duration": 5, "teacher_activity": "...", "student_activity": "...", "design_intent": "..." },
        ...
      ]
    },
    ...
  ]
}
```

### 3. 编辑器方案

- 使用 Tiptap，但不再是 block 编辑器
- 每个 section 是一个 Tiptap 实例（或一个文档内的不同 section）
- Section 折叠通过 CSS + Vue 控制
- AI 操作通过浮层菜单触发

---

## 风险与注意事项

1. **MiniMax API 接入**：需要确认 MiniMax 的 API 格式和流式输出支持
2. **思源宋体加载**：字体文件较大，需要考虑加载策略（CDN + 子集化）
3. **数据库迁移**：从旧 block 结构迁移到新教案结构需要迁移脚本
4. **Prompt 质量**：AI 生成质量是核心，需要多次迭代优化 prompt
5. **Word 导出排版**：python-docx 的排版能力有限，复杂表格可能需要额外处理
