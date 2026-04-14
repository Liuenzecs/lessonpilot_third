# LessonPilot

> 本文件用于约束 Codex/AI 助手的工作方式，内容与 `CLAUDE.md` 保持对齐。

AI 备课助手 — 一份备课，教案学案一起出。

## 架构决策

- **教案/学案结构化 JSON 是中枢**：编辑器渲染它，AI 生成它，导出消费它
- **单体优先**：前端 Vue 3 单 app，后端 FastAPI 单服务，不拆微服务
- **pnpm workspace 管理**：apps/ 放可部署应用，packages/ 放跨应用共享包
- **AI 真正流式输出**：token-by-token 流式，不是 SSE 状态事件
- **AI 输出结构化**：后端解析校验，前端只渲染确认后的数据
- **API 版本前缀**：`/api/v1/`

## 技术栈

- 前端：Vue 3 + TypeScript + Vite + Pinia + Vue Router + TanStack Query
- 编辑器：Tiptap（Section-based document editor）
- 后端：FastAPI + Python 3.12+ + SQLModel + PostgreSQL
- AI 通信：REST + SSE（真正的 token-by-token 流式）
- AI 模型：DeepSeek + MiniMax（通过抽象 Provider 接口支持切换）
- 导出：python-docx（Word，学校标准教案格式）
- 共享类型：`@lessonpilot/shared-types`（packages/shared-types/）

## UI 方向

- 中式现代风：宣纸白 + 石青 + 胆黄 + 思源宋体
- 详见 `CLAUDE.md`

## 项目结构

```text
lessonpilot_third/
├── apps/
│   ├── web/                    # Vue 3 前端（SPA）
│   │   └── src/
│   │       ├── app/            # 路由、布局、全局配置
│   │       ├── features/       # 按功能模块组织
│   │       │   ├── auth/       # 登录/注册/密码重置
│   │       │   ├── task/       # 备课台 + 创建备课
│   │       │   ├── editor/     # Section Editor（核心）
│   │       │   ├── generation/ # AI 流式生成
│   │       │   ├── export/     # Word 导出
│   │       │   ├── public/     # 公域页面（Landing 等）
│   │       │   └── settings/   # 账户设置
│   │       └── shared/
│   │           ├── components/ # 通用 UI 组件
│   │           ├── composables/
│   │           ├── styles/     # 中式现代风设计系统
│   │           └── api/        # fetch wrapper + vue-query
│   └── api/                    # FastAPI 后端
│       ├── app/
│       │   ├── api/v1/endpoints/  # auth, tasks, documents, account, health
│       │   ├── services/       # auth, task, document, generation, rewrite, export, llm
│       │   ├── models/         # User, Task, Document, DocumentSnapshot, AuthToken, Feedback
│       │   ├── schemas/        # 请求/响应 + 教案/学案内容模型
│       │   ├── core/           # 配置、数据库、安全
│       │   └── prompts/        # AI prompt 模板（学科专项）
│       ├── alembic/            # 数据库迁移
│       └── tests/              # 测试
├── packages/
│   └── shared-types/           # 教案/学案 TypeScript 类型
├── docs/
│   ├── GOAL.md / PROGRESS.md / NEXT.md
│   ├── milestones/             # 规划文档
│   └── design/                 # UI 设计文档
├── docker-compose.yml
└── pnpm-workspace.yaml
```

## 当前状态

项目按 `docs/milestones/product-replan-v2.md` 重新规划，按 `docs/milestones/implementation-plan-v2.md` 分 6 个 Sprint 重做。当前准备执行 Sprint 0（项目清理）。

## MVP 范围

**做**：注册登录、一站式创建、AI 流式生成（语文）、Section 编辑器、AI 重写、学校标准 Word 导出、中式现代风 UI、备课台

**不做**：PDF、历史版本、管理后台、分析、SSR、Sentry、复杂计费、暗色模式、Onboarding、反馈、多学科

## 工作流程

### 开始工作前

1. 读 `CLAUDE.md` 了解产品定位和架构
2. 读 `docs/milestones/implementation-plan-v2.md` 了解实施计划
3. 读 `docs/NEXT.md` 了解当前任务
4. 读 `docs/PROGRESS.md` 了解已完成工作

### 工作中

- 聚焦当前 Sprint，不做范围外的事
- 影响产品方向的决策先询问
- 所有设计从老师视角出发
- 每次回复前使用"恩泽"作为称呼

### 完成任务后

1. 在 `docs/PROGRESS.md` 追加记录
2. 更新 `docs/NEXT.md`
3. 不自动进入下一个 Sprint
