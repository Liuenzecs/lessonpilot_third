# LessonPilot — 项目总目标

## 一句话定位

AI 赋能的备课工具：**结构化教案编辑器 + AI 填充引擎**。

老师打开产品 → 选学科/年级/主题 → 10 秒后看到结构化教案草稿 → 改几下 → 导出 Word → 15 分钟内完成备课。

## 核心产品原则

1. **结构感优先于自由输入** — 新手教师最缺的是结构感，默认体验是给骨架，AI 填肉，老师调整
2. **AI 是引擎不是主角** — 不是和 AI 聊天生成教案，而是在结构化框架内由 AI 填充内容
3. **老师掌控感** — 所有 AI 生成内容以"待确认"状态呈现，老师主动接受后才合入
4. **Content JSON 是中枢** — 编辑器渲染它，AI 生成它，导出消费它，三者通过统一契约解耦

## 架构决策（不可违反）

- Content JSON Block Tree 是唯一的数据层，编辑器只是视图层
- 单体优先：前端 Vue 3 单 app，后端 FastAPI 单服务
- AI 输出必须结构化：后端解析校验，前端只渲染确认后的数据
- 不要实时协同、不要 CRDT/OT、不要 WebSocket 状态同步
- API 版本前缀：`/api/v1/`

## 技术栈

- 前端：Vue 3 + TypeScript + Vite + Pinia + Vue Router + TanStack Query
- 编辑器：Tiptap（ProseMirror 封装），通过 content JSON 解耦可替换
- 后端：FastAPI + Python 3.12+ + SQLModel + PostgreSQL
- AI 通信：REST + SSE（不用 WebSocket）
- 导出：python-docx（Word）+ weasyprint（PDF）
- 数据库：PostgreSQL，一个 document 一个 JSONB content 字段

## 阶段路线图

- [x] **Phase 0**：骨架搭建
- [x] **Phase 1 — 核心循环（能用）**
  - 目标：一个老师能完整走完"注册 → 创建任务 → AI 生成 → 编辑 → 导出 Word"
  - 后端：Auth（注册/登录/JWT）、Task CRUD、Document CRUD、AI 生成端点（SSE）、Word 导出
  - 前端：登录/注册页、任务创建向导（学科→年级→主题）、备课台列表页、编辑器基础版、AI 生成进度 UI、自动保存、Word 导出按钮
- [ ] **Phase 2 — 编辑器深度完善（好用）**
  - 目标：编辑器真正好用，成为产品核心
  - 所有 Block 类型完整渲染、AI pending/confirm 流程、局部 AI 重写、Block 级操作、PDF 导出、键盘快捷键、版本历史
  - 参考 `docs/design/editor-ui.md` 全面落地
- [ ] **Phase 3 — 公域页面 & Auth 完善（有门面）**
  - 目标：产品有完整公开门面，可对外传播
  - Landing 首页、定价页、FAQ/帮助中心、关于我们、隐私政策/服务条款、404、公域导航栏 + Footer、忘记密码、邮箱验证
  - 参考 `docs/design/public-pages-ui.md` 全面落地
- [ ] **Phase 4 — 账户设置 & 计费（能赚钱）**
  - 目标：产品可以收费
  - 账户设置页、免费额度限制、订阅方案、支付集成（微信/支付宝）、用量追踪、超额升级引导、发票申请
- [ ] **Phase 5 — UX 打磨（精致）**
  - 目标：从"能用"到"好用"
  - 新用户引导、空状态设计、骨架屏、Toast 通知、错误页面、反馈悬浮按钮、响应式、微动效、Word 排版优化
- [ ] **Phase 6 — 运营基础设施（可运营）**
  - 目标：产品可独立运营
  - 事务性邮件、SEO、数据分析、错误监控（Sentry）、简易管理后台、性能优化
- [ ] **Phase 7 — 高级功能（按需迭代）**
  - 教案模板库、复制为新教案、全文搜索、更多 AI 功能、批量导出、移动端适配

## MVP 不做的事

- 试卷/答题卡上传分析
- PPT 导出
- 实时协同（可能永远不做）
- 多模型切换（先用好一个模型）
