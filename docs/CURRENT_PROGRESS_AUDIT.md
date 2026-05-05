# CURRENT_PROGRESS_AUDIT

> 审计日期：2026-05-05
> 审计范围：前端（Vue 3）、后端（FastAPI）、数据库（PostgreSQL + pgvector）、AI 生成管道、导出管道、文档、配置
> 审计方法：5 个并行探索代理深度读取所有源码文件，交叉验证

---

## 1. Executive Summary

LessonPilot（AI 备课助手）是一个面向中国 K-12 语文教师的公益免费 AI 备课工具。项目当前定位为**纯公益项目**，暂不做商业化，不设会员订阅、不接支付、不建付费墙。

**当前状态**：项目已从工程原型阶段进入功能完备阶段。核心备课流程（注册→创建备课→AI 流式生成→Section 级编辑→Word/PPTX 导出→历史复用）已完整实现，代码中无 mock 数据、无 TODO 占位。前端约 13,940 行源码（95 个文件），后端约 75 个 API 端点、22 个服务层、22 张数据库表、17 个迁移。

**关键数据**：
- 前端核心功能完成度：**95%+**（认证/备课台/编辑器/生成/导出均为 100%）
- 后端核心功能完成度：**95%+**（所有服务层均为真实实现）
- 数据库模型与 TypeScript 类型一致性：**高**（Python/TS 内容模型完全对齐）
- 公益免费机制完成度：**0%**（无使用统计、无成本追踪、无防滥用、无管理后台）
- 内容安全/审核：**0%**（无 LLM 输出过滤、无内容审核）

**一句话结论**：LessonPilot 的核心备课功能已经具备让一位真实老师完整跑通一次备课流程的能力，但在公益运营所需的成本控制、使用统计、防滥用、内容安全方面存在系统性缺失，这些是决定公益试点成败的关键短板。

---

## 2. Current Architecture

### 技术栈

| 层 | 技术 | 版本 |
|---|---|---|
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Vue Router + TanStack Query | Vue 3.5 |
| 编辑器 | Tiptap（Section-based document editor） | - |
| 后端 | FastAPI + Python 3.12+ + SQLModel + PostgreSQL | FastAPI >= 0.115 |
| AI 模型 | DeepSeek / MiniMax（文本生成）+ Local BGE bge-m3（embedding） | - |
| 向量存储 | PostgreSQL + pgvector | pg16 |
| 导出 | python-docx（Word）+ python-pptx（课件） | - |
| 共享类型 | @lessonpilot/shared-types（packages/shared-types/） | workspace |
| 包管理 | pnpm workspace（monorepo） | - |

### 目录结构

```
lessonpilot_third/
├── apps/
│   ├── web/                    # Vue 3 前端 SPA（~13,940 行，95 文件）
│   │   └── src/
│   │       ├── app/            # 路由（20 条）、布局（3 个）、全局配置
│   │       ├── features/       # 12 个功能模块（auth, task, editor, generation, export, public, settings, sharing, reimport, calendar, class-groups, question-bank）
│   │       └── shared/         # API client, toast, theme, content utils, formula
│   └── api/                    # FastAPI 后端
│       ├── app/
│       │   ├── api/v1/         # 16 个端点模块，~75 个 API
│       │   ├── services/       # 22 个服务文件（全部真实实现）
│       │   ├── models/         # 22 张表对应的 SQLModel 模型
│       │   ├── schemas/        # 20 个 schema 文件
│       │   ├── prompts/        # 4 个 prompt 模板
│       │   ├── data/           # 知识包 JSON（仅语文）
│       │   └── core/           # 配置、数据库、安全、限流
│       └── alembic/            # 17 个迁移文件
├── packages/
│   └── shared-types/           # TypeScript 共享类型
├── docs/                       # 项目文档（22+ 文件）
├── docker-compose.yml          # PostgreSQL + pgvector
└── pnpm-workspace.yaml
```

### 架构决策

- 结构化 JSON 是中枢：编辑器渲染它，AI 生成它，导出消费它
- 单体优先：前端 Vue 3 单 app，后端 FastAPI 单服务
- 生成链路以 section 为原子单位：后端按 section 顺序生成，section 内 token delta 流式
- AI 输出结构化：后端解析校验，前端只渲染确认后的数据
- API 版本前缀：`/api/v1/`

---

## 3. Feature Completion Matrix

| 功能模块 | 完成度 | 真实/Mock | 备注 |
|---------|--------|-----------|------|
| 登录/注册/邮箱验证/密码重置 | **100%** | 真实 | 5 个页面，bcrypt + JWT，邮箱验证令牌 |
| 新建备课任务 | **100%** | 真实 | 学科/年级/课题/场景/模板选择 |
| Section 级教案流式生成 | **100%** | 真实 | SSE 12 种事件类型，按 section 流式 |
| Section 级学案流式生成 | **100%** | 真实 | 9 个 section，含分层练习 |
| AI Section 重写/扩展/简化 | **100%** | 真实 | 3 种操作，SSE 流式 |
| 教案编辑器 | **100%** | 真实 | Tiptap，7 种 section 编辑器，自动保存 |
| 学案编辑器 | **100%** | 真实 | 含分层练习编辑器 |
| Word 导出 | **100%** | 真实 | 教案 + 学案，学校模板支持，公式渲染 |
| PPTX/课件导出 | **80%** | 真实 | 仅教案，无自定义模板，基础幻灯片 |
| 旧 Word 教案导入 | **100%** | 真实 | 单文件 + 批量（最多 10） |
| Word 回导（reimport） | **100%** | 真实 | diff + 逐 section 接受/拒绝 |
| 学校模板上传/解析/导出 | **100%** | 真实 | 字段映射 + 自定义布局 |
| RAG 知识检索 | **100%** | 真实 | pgvector + 本地 BGE + 引用系统 |
| 知识包 | **30%** | 真实 | 仅语文 `chinese_literature_v1.json` |
| 个人资产库 | **100%** | 真实 | 上传/预览/复用推荐 |
| 教师风格记忆 | **100%** | 真实 | 风格样本采集 + 注入生成 |
| 质量检查 + 自动修复 | **100%** | 真实 | 15+ 规则，含对齐图 |
| 分享链接 + 评论 | **100%** | 真实 | token-based，可过期，可评论 |
| 教学日历 | **100%** | 真实 | 学期/周/日 + 教学单元 |
| 班级分组 + 差异化 | **100%** | 真实 | 多班级变体生成 |
| 题库 | **60%** | 真实 | 结构完整，但种子数据极少（28 行） |
| 教学反思 | **100%** | 真实 | 反思表单 + 注入下次生成 |
| 备课包（教学包） | **100%** | 真实 | 学案 + PPT 大纲 + 讲稿 |
| 历史记录/版本复用 | **100%** | 真实 | 快照（最多 10 个）+ 恢复 |
| 备课台/任务列表 | **100%** | 真实 | 搜索/筛选/排序/分页/复制 |
| 公域页面 | **95%** | 真实 | 定价页为占位符（ComingSoon） |
| 设置页 | **100%** | 真实 | 个人资料/风格/密码/数据管理 |
| **公益免费使用机制** | **0%** | 不存在 | 无使用统计、无成本追踪 |
| **使用统计/成本统计** | **0%** | 不存在 | 无任何追踪代码 |
| **防滥用/基础限额** | **20%** | 真实 | 内存级限流（单实例），无配额系统 |
| **管理后台** | **0%** | 不存在 | 无任何管理页面或 API |
| **内容安全审核** | **0%** | 不存在 | 无 LLM 输出过滤 |
| **错误反馈机制** | **10%** | 真实 | API 存在（feedback_entries 表），前端未接入 |
| **桌面端/PWA** | **0%** | 不存在 | 无 service worker、无 manifest |
| **手机端** | **70%** | 部分 | 移动端布局存在但非 mobile-first |

---

## 4. Frontend Status

### 完成度总结

| 区域 | 文件数 | 完成度 |
|------|--------|--------|
| 认证（5 页面） | 8 | 100% |
| 备课台（8 视图） | 15+ | 100% |
| 编辑器（20+ 文件） | 25+ | 100% |
| 生成（SSE 消费） | 1 | 100% |
| 导出（Blob 下载） | 1 | 100% |
| 公域页面（10 视图） | 15+ | 95% |
| 设置（4 标签） | 4 | 100% |
| 共享组件 | 13+ | 100% |
| 路由（20 条） | 5 | 100% |

### 技术评估

- **API 客户端**：封装的 fetch，Bearer token 认证，自动 401 处理，`VITE_API_BASE_URL` 环境变量
- **状态管理**：Pinia + TanStack Query，无冗余状态
- **样式系统**：纯 CSS + CSS 变量，无 UI 框架依赖（无 Tailwind、无 Element Plus）
- **无障碍**：无专门的无障碍审计
- **国际化**：无 i18n，全中文界面
- **测试**：49 个前端测试

### 缺失项

1. **反馈组件**：`useFeedbackMutation` composable 存在但未在任何视图中接入
2. **用量展示**：settings.css 中有 `.usage-bar` 样式但未连接数据
3. **管理后台**：无任何管理页面
4. **PWA**：无 service worker、无 manifest
5. **SSR**：应用工厂支持但无服务器入口

---

## 5. Backend Status

### API 端点清单

16 个端点模块，约 **75 个 API 端点**：

| 模块 | 端点数 | 状态 |
|------|--------|------|
| health | 1 | 完成 |
| auth | 8 | 完成（bcrypt + JWT + 邮箱验证） |
| tasks | 8 | 完成（CRUD + 复制 + 生成） |
| documents | 15 | 完成（CRUD + 重写 + 历史 + 导出 + 导入 + 质量 + 包） |
| account | 6 | 完成（资料 + 密码 + 数据导出 + 注销 + 反馈） |
| templates | 9 | 完成（CRUD + 学校模板预览/保存） |
| knowledge | 6 | 完成（CRUD + 诊断 + 向量搜索） |
| personal-assets | 5 | 完成（预览 + 保存 + 推荐） |
| import | 4 | 完成（单文件 + 批量导入） |
| style-profile | 3 | 完成（CRUD + AI 建议） |
| questions | 4 | 完成（章节列表 + 搜索 + 种子） |
| sharing | 7 | 完成（链接 CRUD + 公开查看 + 评论） |
| calendar | 9 | 完成（学期/周/日 CRUD） |
| class-groups | 6 | 完成（CRUD + 差异化变体） |
| semesters/units | 5 | 完成（单元 CRUD + 包生成） |
| reflections | 2 | 完成（创建 + 列表） |

### 服务层

22 个服务文件，**全部为真实实现，无 mock**：

- auth, account, mail, document, task, template
- llm（3 provider: Fake/DeepSeek/MiniMax）
- generation, rewrite, export, courseware
- knowledge, knowledge_pack
- import, reimport, personal_asset
- quality, quality_fix
- style_profile, style_analysis
- share, question_bank
- calendar, class_group
- semester_package, reflection

### 后端测试

176 个后端测试，覆盖率 80%+。

### 安全问题

| 级别 | 问题 | 文件 |
|------|------|------|
| **CRITICAL** | .env 文件包含真实 DeepSeek 和 MiniMax API 密钥且已提交到仓库 | `apps/api/.env` |
| HIGH | JWT 无刷新令牌机制，登出为 no-op | `auth_service.py` |
| HIGH | 无角色/管理员权限控制（ADMIN_ALLOWLIST_EMAILS 配置存在但未使用） | `config.py` |
| MEDIUM | 限流为内存级（单实例），非 Redis 支持 | `rate_limit.py` |
| MEDIUM | CORS 允许所有方法和头 | `main.py` |
| LOW | 分享 token 无暴力破解限流 | `share_service.py` |

### 性能问题

- 题库计数使用 `len(session.exec(count_stmt).all())` 而非 `SELECT COUNT(*)`
- 日历学期详情存在 N+1 查询（周循环 + 日循环 + 任务查找）
- 账户注销在 Python 循环中逐条删除记录
- 限流字典无清理机制，可能内存泄漏

---

## 6. Database Status

### 表清单（22 张）

| 表名 | 模型 | 行为 |
|------|------|------|
| users | User | 完整，email unique |
| auth_tokens | AuthToken | 完整，SHA-256 令牌哈希 |
| tasks | Task | 完整，含自引用 FK |
| documents | Document | 完整，JSON 内容 + 版本号 |
| document_snapshots | DocumentSnapshot | 完整，最多 10 个快照 |
| feedback_entries | Feedback | 完整 |
| knowledge_chunks | KnowledgeChunk | 完整，pgvector 1024 维 |
| templates | Template | 完整，含公开/私有 |
| template_sections | TemplateSection | 完整，CASCADE 删除 |
| personal_assets | PersonalAsset | 完整 |
| teaching_packages | TeachingPackage | 完整 |
| teacher_style_profiles | TeacherStyleProfile | 完整，1:1 用户 |
| style_samples | StyleSample | 完整 |
| questions | Question | 部分缺陷（无长度约束、无 timezone） |
| share_links | ShareLink | 完整 |
| share_comments | ShareComment | 完整 |
| semesters | Semester | 完整 |
| week_schedules | WeekSchedule | 完整 |
| lesson_schedule_entries | LessonScheduleEntry | 完整 |
| class_groups | ClassGroup | 完整 |
| teaching_units | TeachingUnit | 完整 |
| teaching_reflections | TeachingReflection | 完整 |

### 仅存在于迁移中的表（7 张，无 Python 模型）

| 表名 | 迁移 | 状态 |
|------|------|------|
| user_subscriptions | 0004 | 无模型，不可用 |
| billing_orders | 0004 | 无模型，不可用 |
| billing_webhook_events | 0004 | 无模型，不可用 |
| invoice_requests | 0004 | 无模型，不可用 |
| analytics_events | 0005 | 无模型，不可用（**影响使用统计**） |
| quota_adjustments | 0005 | 无模型，不可用 |
| email_delivery_logs | 0005 | 无模型，不可用 |

### 关键问题

1. **Alembic env.py 只导入 4 个模型**（Document, DocumentSnapshot, Task, User），其余 18 个未导入。`autogenerate` 会尝试删除未导入的表。
2. **Question 模型**：列无长度约束、DateTime 无 timezone、无 updated_at。
3. **无管理员角色**：User 表无 role/admin 字段。
4. **无软删除**：所有内容只能硬删除，无 deleted_at / is_archived。
5. **无使用追踪表**：analytics_events 存在但不可用。

### 类型一致性

Python Pydantic 内容模型与 TypeScript 共享类型**完全对齐**。每个字段、枚举值、嵌套结构在两端一一对应。`@lessonpilot/shared-types` 包在前端 15 个文件中被引用。

---

## 7. AI Generation Pipeline

### 架构

```
用户点击"生成" → POST /tasks/{id}/generate → 返回 stream_url
                                              ↓
前端 fetch stream_url (SSE) ← 后端逐 section 生成 ← LLM API 流式调用
                                              ↓
逐 section 渲染 ← SSE 事件（section_start → section_delta → section_done）
                                              ↓
全部完成 → document_done → 保存到 DB
```

### Section 顺序

**教案（6 sections）**：objectives → key_points → preparation → teaching_process → board_design → reflection

**学案（9 sections）**：learning_objectives → key_difficulties → prior_knowledge → self_study → collaboration → presentation → assessment → extension → self_reflection

### 提示词模板

| 文件 | 用途 | 状态 |
|------|------|------|
| `section_generation_prompt.md` | **主要**：逐 section 生成 | 真实可用 |
| `section_rewrite_prompt.md` | Section 重写/扩展/简化 | 真实可用 |
| `lesson_plan_generation_prompt.md` | 全量教案生成（遗留） | 未使用 |
| `study_guide_generation_prompt.md` | 全量学案生成（遗留） | 有 bug（硬编码"语文"） |

### LLM Provider

| Provider | 模型 | 状态 |
|----------|------|------|
| DeepSeek | deepseek-v4-flash | 真实可用 |
| MiniMax | MiniMax-Text-01 | 真实可用 |
| Fake | N/A | 开发测试用 |

### 上下文注入

生成时注入以下上下文：
- RAG 知识检索（含引用标记 `[cite:id]`）
- 个人资产推荐
- 教师风格偏好
- 教学反思改进建议
- 班级差异化提示
- 模板 section 提示

### 内容验证与归一化

- 每个 section 有 Pydantic TypeAdapter 校验
- 中英文字段名自动映射
- 目标维度归一化
- 题型归一化
- 代码围栏清理
- 验证失败时降级为空值 + 警告事件

### 缺失项

| 项目 | 状态 | 影响 |
|------|------|------|
| **Token 计数 / 成本追踪** | 不存在 | 无法知道每次生成花了多少钱 |
| **内容安全审核** | 不存在 | LLM 可能输出不当内容 |
| **API 重试机制** | 不存在 | 网络抖动直接失败 |
| **Provider 降级** | 不存在 | 主 provider 故障无法切换 |
| **结构化输出强制** | 不存在 | 依赖 prompt 工程和后处理，脆弱 |
| **多学科知识包** | 仅语文 | 数学/英语等无法触发 RAG |

---

## 8. Export Pipeline

### Word 导出（DOCX）

| 特性 | 状态 |
|------|------|
| 教案导出 | 完成（元数据表 + 目标 + 重难点 + 教学过程表 + 板书 + 反思） |
| 学案导出 | 完成（学生信息表 + 学习目标 + 重难点 + 三级学习过程 + 达标测评 + 拓展） |
| 学校模板导出 | 完成（自定义列头/排序/布局/空白区） |
| LaTeX 公式渲染 | 完成（LaTeX → Word OMML） |
| 场景适配 | 完成（家教 4 列 / 公立校 5 列） |
| 仅导出已确认 section | 完成 |
| 字体/排版 | 完成（宋体正文 + 微软雅黑标题） |

### PPTX 课件导出

| 特性 | 状态 |
|------|------|
| 教案→课件 | 完成（标题页 + 目标 + 重难点 + 逐步骤 + 提问 + 板书 + 作业） |
| 学案→课件 | **不支持**（返回 400） |
| 自定义模板 | **不支持** |
| 讲稿备注 | 完成（设计意图 + 学生活动） |
| 提问提取 | 启发式（基于"？""提问""讨论""思考"关键词） |

---

## 9. 公益免费使用与成本控制状态

### 当前状态

| 能力 | 状态 | 详情 |
|------|------|------|
| 使用统计 | **不存在** | analytics_events 表存在但无模型，无追踪代码 |
| 成本统计 | **不存在** | LLM API 调用无 token 计数，usage 字段被忽略 |
| 基础限额 | **20%** | 内存级限流（20 次/小时/用户），单实例有效，重启丢失 |
| 防滥用 | **20%** | 限流 + 注册验证码，但无 CAPTCHA、无 IP 黑名单 |
| 日志追踪 | **部分** | 结构化日志存在，但无使用量聚合 |
| 错误反馈 | **10%** | feedback_entries 表 + API 存在，前端未接入 |
| 管理后台 | **不存在** | 无管理员角色、无管理页面、无管理 API |
| 成本预算/预警 | **不存在** | 无任何成本控制机制 |

### 风险评估

**如果直接开放给真实老师使用**：

1. **AI 调用成本不可控**：DeepSeek/MiniMax 按 token 计费，当前无任何计数或限额。一个用户可以无限次生成，成本完全敞口。
2. **无法检测滥用**：没有使用频率统计，无法发现异常用户。
3. **无法衡量价值**：不知道老师用了多少次、导出了多少次、是否真的在用。
4. **无法迭代改进**：没有反馈闭环，不知道老师在哪里卡住了。
5. **无法管理**：没有管理后台，无法封禁用户、查看状态、处理投诉。

---

## 10. Docs and Project Management Status

### 文档状态

| 文档 | 状态 | 问题 |
|------|------|------|
| CLAUDE.md | **过时** | 进度停在 Phase 17，实际已到 Phase 19 |
| docs/GOAL.md | **过时** | 进度冻结在 Sprint 0-6 / Cycle 1-4 |
| docs/NEXT.md | **当前** | 准确反映 Phase 19 |
| docs/PROGRESS.md | **当前** | 巨大的追加式文件，1500+ 行 |
| docs/ROADMAP.md | **错误** | P1/P2 项目被虚假标记为已完成 |
| docs/PRODUCT.md | **当前** | 无商业化导向 |
| docs/ACCEPTANCE.md | **当前** | Phase 15 验收明确要求去除商业化文案 |
| docs/COMPETITIVE.md | **当前** | 竞品迁移策略仍有效 |
| docs/TEACHER_WORKFLOWS.md | **当前** | 教师工作流准确 |
| docs/QUALITY_RUBRIC.md | **当前** | 质量标准仍有效 |
| docs/specs/* | **当前** | 内容模型/SSE/导入/导出/RAG 规格均准确 |
| docs/decisions/ADR-0001 | **当前** | 结构化 JSON 决策仍有效 |
| docs/milestones/milestone-1/* | **过时** | 引用已删除的代码（billing, admin, Sentry） |
| docs/milestones/product-replan-v2.md | **部分过时** | 仍为 draft 状态，仍列出商业化为未来方向 |
| docs/milestones/phase-15-*.md | **当前** | 明确记录商业化清理为临时措施 |
| docs/design/editor-ui.md | **过时** | Notion 风格设计，已被 DESIGN.md 替代 |
| docs/design/public-pages-ui.md | **严重过时** | 包含完整三级定价设计（Free/Pro/Team），与当前公益定位矛盾 |
| DESIGN.md (root) | **当前** | 教师文档桌设计系统，唯一视觉权威 |

### 商业化残留

以下文档仍包含商业化内容，与公益定位矛盾：
1. **docs/design/public-pages-ui.md**：完整的三级定价页面设计（Free/29 元/99 元）、订阅管理、支付集成、发票流程
2. **docs/milestones/product-replan-v2.md**：列出完整计费为 Phase 3 未来目标
3. **docs/milestones/phase-15-filing-commercial-cleanup.md**：声明商业化移除为"临时措施"
4. **ROADMAP.md**：列出"complex billing"为 deferred 而非 eliminated

### 缺失的文档

- **公益使用政策**：无任何文档声明项目为公益免费性质
- **隐私政策文本**：public-pages-ui.md 描述了隐私页面设计，但无实际隐私政策文本
- **学生数据保护政策**：无专门文档
- **使用统计/成本追踪设计**：无规格文档
- **防滥用方案**：无设计文档
- **管理后台设计**：无规格文档

---

## 11. Known Problems and Technical Debt

### CRITICAL（阻塞公益试点）

| # | 问题 | 影响 | 修复难度 |
|---|------|------|---------|
| 1 | .env 文件包含真实 API 密钥且已提交到仓库 | 密钥泄露风险 | 低（轮换密钥 + .gitignore） |
| 2 | 无 AI 调用成本追踪 | 成本完全不可控 | 中 |
| 3 | 无使用统计 | 无法衡量公益效果 | 中 |
| 4 | 无内容安全审核 | LLM 可能输出不当内容 | 中 |
| 5 | 无管理后台 | 无法管理用户和内容 | 高 |

### HIGH（影响稳定性）

| # | 问题 | 影响 | 修复难度 |
|---|------|------|---------|
| 6 | 限流为内存级（单实例） | 多实例部署时限流失效 | 中 |
| 7 | LLM API 无重试机制 | 网络抖动导致生成失败 | 低 |
| 8 | Alembic env.py 只导入 4 个模型 | autogenerate 会破坏数据库 | 低 |
| 9 | Question 模型缺陷 | 无长度约束、无 timezone | 低 |
| 10 | ROADMAP.md 虚假完成标记 | 误导项目状态判断 | 低 |

### MEDIUM（技术债）

| # | 问题 | 影响 | 修复难度 |
|---|------|------|---------|
| 11 | 7 张迁移表无 Python 模型 | 数据库僵尸表 | 中 |
| 12 | 前端反馈组件未接入 | 反馈 API 闲置 | 低 |
| 13 | PPTX 仅支持教案 | 学案无法导出课件 | 中 |
| 14 | 题库种子数据极少 | 题库功能几乎不可用 | 中 |
| 15 | 知识包仅语文 | 其他学科无 RAG 增强 | 高 |
| 16 | 邮件仅纯文本 | 用户体验差 | 低 |
| 17 | N+1 查询（日历/题库） | 性能瓶颈 | 中 |
| 18 | 限流字典无清理 | 潜在内存泄漏 | 低 |
| 19 | 无 Provider 降级 | 单点故障 | 中 |
| 20 | CORS 过于宽松 | 安全风险 | 低 |

### LOW（改善项）

| # | 问题 | 影响 | 修复难度 |
|---|------|------|---------|
| 21 | docs/design/ 目录完全过时 | 误导开发者 | 低 |
| 22 | CLAUDE.md 进度过时 | 上下文错误 | 低 |
| 23 | 无软删除模式 | 误删不可恢复 | 中 |
| 24 | 登出为 no-op | 无法强制失效令牌 | 中 |
| 25 | study_guide prompt 硬编码"语文" | 遗留路径 bug | 低 |

---

## 12. Top Risks

| 优先级 | 风险 | 概率 | 影响 | 缓解措施 |
|--------|------|------|------|---------|
| **P0** | API 密钥已泄露到 git 历史 | **已发生** | CRITICAL | 立即轮换所有密钥，添加到 .gitignore |
| **P0** | AI 调用成本敞口（无追踪无限制） | 高 | CRITICAL | 必须在开放试用前加上 token 计数 + 配额 |
| **P0** | LLM 输出无安全审核 | 中 | CRITICAL | 至少加关键词过滤 |
| **P1** | 无使用统计，无法衡量公益效果 | 确定 | HIGH | 加 analytics_events 模型 + 前端埋点 |
| **P1** | 无管理后台，无法处理投诉/封禁 | 确定 | HIGH | 最小管理 API |
| **P1** | 单实例限流，无法水平扩展 | 确定 | MEDIUM | 迁移到 Redis 限流 |
| **P2** | 知识包仅语文，多学科无法使用 | 确定 | MEDIUM | 先聚焦语文，暂可接受 |
| **P2** | 反馈闭环断裂（API 有前端无） | 确定 | MEDIUM | 接入前端反馈组件 |
| **P2** | 文档与代码不同步 | 确定 | LOW | 更新 CLAUDE.md/ROADMAP.md |
| **P3** | 数据库僵尸表（7 张无模型） | 确定 | LOW | 清理或实现模型 |

### 公益运营特有风险

| 风险 | 详情 |
|------|------|
| 成本失控 | 免费开放后，AI API 调用成本可能快速增长，无预算上限 |
| 滥用风险 | 恶意用户可能批量生成内容用于非教学用途 |
| 内容责任 | AI 生成内容可能包含事实错误，公益模式下责任归属不明确 |
| 隐私风险 | 教师备课内容可能包含学生姓名、学校信息等敏感数据 |
| 可持续性 | 纯公益模式无收入，长期运行需要持续投入 |
| 版权风险 | 知识包内容可能涉及教材版权 |
| 数据安全 | 备课数据存储在服务器上，需要有明确的数据保护政策 |

---

## 13. Recommended Next Steps

### 接下来 2 周：成本控制 + 安全底线

| # | 任务 | 优先级 | 工作量 |
|---|------|--------|--------|
| 1 | 轮换所有 API 密钥，确保 .env 在 .gitignore 中 | P0 | 0.5 天 |
| 2 | 实现 LLM API token 计数和成本追踪 | P0 | 2 天 |
| 3 | 实现每用户日/月生成配额（公益性限额） | P0 | 2 天 |
| 4 | 加 LLM 输出基础关键词过滤 | P0 | 1 天 |
| 5 | 接入前端反馈组件 | P1 | 0.5 天 |
| 6 | 修复 Alembic env.py 模型导入 | P1 | 0.5 天 |
| 7 | 更新 CLAUDE.md/ROADMAP.md 文档状态 | P1 | 1 天 |

### 接下来 4 周：公益试用准备

| # | 任务 | 优先级 | 工作量 |
|---|------|--------|--------|
| 8 | 实现 analytics_events 模型 + 基础使用统计 API | P1 | 3 天 |
| 9 | 最小管理 API（用户列表、禁用、查看统计） | P1 | 3 天 |
| 10 | 前端使用统计展示（生成次数、导出次数） | P1 | 2 天 |
| 11 | 添加 LLM API 重试机制 | P1 | 1 天 |
| 12 | 补充题库种子数据 | P2 | 2 天 |
| 13 | 编写公益使用政策/隐私政策文本 | P1 | 2 天 |

### 接下来 8 周：公益试点运营

| # | 任务 | 优先级 | 工作量 |
|---|------|--------|--------|
| 14 | 限流迁移到 Redis（多实例支持） | P2 | 2 天 |
| 15 | 成本预算预警（月度预算上限告警） | P2 | 2 天 |
| 16 | 清理 7 张僵尸表或实现对应模型 | P2 | 2 天 |
| 17 | PPTX 支持学案导出 | P2 | 3 天 |
| 18 | 清理过时文档（design/ 目录、milestone-1/） | P2 | 1 天 |
| 19 | 邮件 HTML 模板 | P3 | 2 天 |
| 20 | N+1 查询优化 | P2 | 2 天 |

---

## Top 10 Problems（按优先级）

| 优先级 | 问题 | 为什么重要 | 影响范围 | 建议处理方式 |
|--------|------|-----------|---------|-------------|
| 1 | API 密钥泄露到 git 历史 | 任何有仓库访问权的人都能获取 DeepSeek/MiniMax API 密钥 | 全局安全 | 立即轮换密钥 + .gitignore |
| 2 | AI 调用成本完全不可控 | 无 token 计数、无配额、无预算上限，免费开放后成本敞口 | 运营可持续性 | 实现 token 计数 + 用户配额 |
| 3 | 无内容安全审核 | LLM 可能输出不当内容（错误知识、偏见表述等），公益项目声誉风险更大 | 内容质量 | 加输出过滤 + 关键词检测 |
| 4 | 真实老师无法完整跑通一次备课 | 虽然功能完备，但无使用统计、无反馈闭环，不知道老师会在哪里卡住 | 用户验证 | 先找 1 位真实老师手动测试 |
| 5 | 无使用统计和成本数据 | 无法衡量公益效果、无法做迭代决策、无法向支持方证明价值 | 产品迭代 | 实现 analytics 模型 |
| 6 | 无管理后台 | 无法处理用户投诉、无法封禁恶意用户、无法查看系统状态 | 运营能力 | 最小管理 API |
| 7 | 反馈闭环断裂 | feedback API 存在但前端未接入，老师遇到问题时无法报告 | 用户体验 | 接入前端反馈组件 |
| 8 | 单实例限流无水平扩展 | 内存级限流重启丢失，多实例失效，公益试点如果流量增长会出问题 | 可扩展性 | 迁移到 Redis |
| 9 | 知识包仅语文 | 多学科无法使用 RAG 增强，但当前 MVP 聚焦语文可接受 | 功能范围 | 先聚焦语文 |
| 10 | 文档与代码严重不同步 | CLAUDE.md 停在 Phase 17、ROADMAP.md 虚假完成标记、design/ 目录完全过时 | 工程协作 | 更新文档 |

---

## Three Roadmaps

### 路线 A：最小可用公益 MVP

**目标**：尽快让一位真实老师能完整使用一次备课流程。

**必做任务**：
1. 轮换 API 密钥 + .gitignore
2. 实现 LLM token 计数（记录每次调用的 prompt_tokens + completion_tokens）
3. 实现每用户每日生成限额（如 20 次/天）
4. 加 LLM 输出基础关键词过滤
5. 接入前端反馈组件
6. 修复 Alembic env.py
7. 找 1 位真实语文老师做手动测试

**不做任务**：
- 管理后台
- Redis 限流
- 多学科知识包
- PPTX 学案导出
- HTML 邮件
- PWA
- 文档清理

**预计顺序**：密钥安全 → token 计数 → 配额 → 过滤 → 反馈 → env.py → 手动测试

**验收标准**：
- 一位真实语文老师能完成：注册 → 创建备课 → AI 生成教案 → 编辑调整 → 导出 Word
- 知道这次测试花了多少 AI 调用成本
- 老师能提交反馈

### 路线 B：公益试点验证版

**目标**：让 5-20 位真实老师连续使用 2-4 周，验证真实教学价值。

**必做任务**：
- 路线 A 全部任务
- analytics_events 模型 + 使用统计 API
- 最小管理 API（用户列表/禁用/统计查看）
- 前端使用统计展示（个人生成次数、导出次数）
- 公益使用政策文本
- 隐私政策文本
- 成本月度预算上限 + 告警

**数据埋点**：
| 事件 | 数据 |
|------|------|
| task_create | 学科、年级、课题、场景 |
| generation_start | task_id、doc_type |
| generation_complete | task_id、sections_count、total_tokens |
| generation_error | task_id、section、error_type |
| section_edit | section_name、edit_type（手动/AI重写） |
| document_export | format（docx/pptx）、template_used |
| document_share | permission、has_comments |
| feedback_submit | mood、message |

**用户反馈收集方式**：
1. 前端反馈组件（mood + message + page_path）
2. 生成后满意度评分（3 秒弹出）
3. 导出后质量评分
4. 每周一次简短问卷

**成本统计方式**：
- 每次 LLM API 调用记录 prompt_tokens + completion_tokens + 模型 + 时间
- 按 provider 分别计算成本（DeepSeek ~¥0.001/1K tokens, MiniMax 类似）
- 按用户、按天、按月聚合
- 月度预算上限（如 ¥500/月）自动降级到限制模式

**风险**：
- 老师可能因为内容质量不高而放弃
- 成本可能超出预期
- 可能收到不当内容投诉
- 可能涉及教材版权问题

### 路线 C：公益长期运行预备版

**目标**：不是商业化，而是让项目能免费、稳定、低成本地运行 6 个月以上。

**必做任务**：
- 路线 B 全部任务
- Redis 限流（多实例支持）
- Provider 降级（主 provider 故障自动切换备用）
- 数据库僵尸表清理
- N+1 查询优化
- LLM API 重试机制
- 账户注销级联删除优化

**技术前置**：
- 容器化部署（Docker Compose 完善）
- CI/CD 基础管道
- 监控告警（至少：服务存活 + 错误率 + 成本）

**成本控制方案**：
- 用户配额：免费用户每日 N 次生成
- 月度总预算上限
- 高峰期排队机制
- 缓存高频相同 topic 的生成结果
- 评估开源/本地模型替代方案

**防滥用方案**：
- 邮箱验证必须完成才能使用
- 每日生成配额
- IP + 用户维度限流
- 异常模式检测（短时间大量请求）
- CAPTCHA（注册时）

**隐私与合规风险**：
- 编写并公示隐私政策
- 备课数据存储在中国大陆服务器
- 教师备课内容不用于 AI 训练
- 学生数据保护（避免在备课内容中包含学生隐私）
- 定期数据清理策略

**后台管理需求**：
- 用户管理（列表、禁用、配额调整）
- 使用统计看板（生成次数、成本趋势、活跃用户）
- 内容审核队列（标记的异常内容）
- 系统健康监控

**后续公益协作可能性**（考虑但不立即实现）：
- 捐赠入口
- 公益基金支持
- 学校/教研组公益试点
- 开源协作
- 志愿教师共建模板
- 公益版使用协议

---

## 14. Questions for External Brainstorming

1. 当前项目是否适合继续以公益免费方式推进？还是应该考虑某种形式的可持续模式？
2. 下一步应该优先补成本控制、使用统计，还是先找真实老师测试？
3. 免费公益模式下，怎样控制 AI 成本？是否需要基础限额？限额多少合适？
4. 是否需要老师反馈与错误纠正闭环？如何设计？
5. 当前最可能导致公益试点失败的点是什么？（成本？内容质量？用户体验？）
6. 当前架构是否适合后续开放给更多老师免费使用？瓶颈在哪里？
7. 是否应该将 AI 生成内容标注为"AI 辅助生成，请老师核实"？
8. 知识包内容是否涉及教材版权？如何合规使用？
9. 是否需要最小后台管理能力才能开始试点？
10. 公益项目是否有法律风险（如内容错误导致的教学事故）？

---

## 15. Appendix

### 审计检查的关键文件

**前端**（apps/web/src/）：
- features/auth/ (8 files)
- features/task/ (15+ files)
- features/editor/ (25+ files)
- features/generation/ (1 file)
- features/export/ (1 file)
- features/public/ (15+ files)
- features/settings/ (4 files)
- features/sharing/ (5 files)
- features/reimport/ (3 files)
- features/calendar/ (3 files)
- features/class-groups/ (3 files)
- shared/ (13+ files)
- app/router/ (5 files)
- package.json, vite.config.ts

**后端**（apps/api/）：
- app/api/v1/endpoints/ (16 files)
- app/services/ (22 files)
- app/models/ (18 files)
- app/schemas/ (20 files)
- app/prompts/ (4 files)
- app/core/ (6 files)
- app/data/ (1 file)
- alembic/versions/ (17 files)
- main.py, pyproject.toml

**共享类型**（packages/shared-types/）：
- src/content.ts, src/index.ts

**文档**（docs/）：
- 22+ 文档文件

**配置**：
- docker-compose.yml, pnpm-workspace.yaml
- .env.example, apps/api/.env

### 审计命令

```bash
# 后端测试
cd apps/api && python -m pytest --tb=short -q

# 前端测试
cd apps/web && pnpm test

# 数据库迁移状态
cd apps/api && alembic current

# Git 状态
git log --oneline -20
git diff --stat
```

### 发现依据

- 前端源码逐文件审计（95 个文件）
- 后端源码逐文件审计（80+ 个文件）
- 数据库模型和迁移逐个审计（22 张表、17 个迁移）
- 文档逐个审计（22+ 个文件）
- AI 提示词逐个审计（4 个模板）
- 安全扫描（密钥泄露、SQL 注入、XSS）
