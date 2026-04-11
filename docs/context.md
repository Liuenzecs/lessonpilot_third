# LessonPilot — 项目上下文快照

> Last updated: 2026-04-10
> 用途：将此文件全文复制粘贴给外部 AI（如 Opus 4.6），附加具体问题即可获得精准建议。

## 项目简介

AI 赋能的备课工具。老师选择学科/年级/课题，10 秒内获得结构化教案草稿，编辑确认后导出 Word，15 分钟完成备课。

核心产品原则：
- 结构化优先（给骨架，AI 填肉，老师调）
- AI 是引擎不是主角（结构化框架，不是聊天）
- 老师掌控全局（AI 内容以 pending 状态插入，老师确认后合入）
- Content JSON 是中枢（编辑器渲染它，AI 生成它，导出消费它）

## 技术栈

- 前端：Vue 3 + TypeScript + Vite + Pinia + Vue Router + TanStack Query
- 编辑器：Tiptap（ProseMirror wrapper）
- 后端：FastAPI + Python 3.12+ + SQLModel + PostgreSQL
- AI 通信：REST + SSE
- 导出：python-docx (Word)、weasyprint (PDF)
- 共享类型：`@lessonpilot/shared-types`（pnpm workspace 包）
- 开发环境：Docker Compose（PostgreSQL + API + Web）

## 架构决策

- Content JSON Block Tree 是唯一数据层
- 单体优先：前端 Vue 3 单 app，后端 FastAPI 单服务
- pnpm workspace 管理：apps/ 放可部署应用，packages/ 放跨应用共享包
- 编辑器是视图层：Content JSON 是数据层，通过提取/灌入操作连接
- AI 输出必须结构化：后端解析校验，前端只渲染确认后的数据
- AI 内容待确认：所有 AI 生成以 pending 状态插入，老师主动接受后合入
- 不做实时协作、CRDT/OT、WebSocket 状态同步
- API 版本前缀：`/api/v1/`

## 项目目录结构

```
New_lessonpilot/
├── apps/
│   ├── web/                    # Vue 3 前端
│   │   └── src/
│   │       ├── app/            # 路由、布局、全局配置
│   │       ├── features/       # 按功能模块组织
│   │       │   ├── auth/       # 登录注册
│   │       │   ├── task/       # 任务 CRUD
│   │       │   ├── editor/     # 核心：块级编辑器
│   │       │   ├── generation/ # AI 生成交互
│   │       │   └── export/     # Word/PDF 导出
│   │       └── shared/
│   │           ├── components/ # 通用 UI 组件
│   │           ├── composables/
│   │           └── api/        # fetch wrapper + vue-query
│   └── api/                    # FastAPI 后端
│       ├── app/
│       │   ├── api/v1/         # API 路由（按版本）
│       │   │   ├── router.py   # v1 router 聚合
│       │   │   └── endpoints/  # 各端点处理函数
│       │   ├── services/       # 业务逻辑层
│       │   ├── models/         # SQLModel 表模型（User, Task, Document）
│       │   ├── schemas/        # Pydantic 请求/响应 schema
│       │   ├── core/           # 配置、数据库、安全
│       │   └── prompts/        # AI prompt 模板
│       ├── alembic/            # 数据库迁移
│       └── tests/              # 测试
├── packages/
│   └── shared-types/           # 跨应用共享的 TS 类型
│       └── src/
│           ├── content.ts      # Content JSON Block Tree 类型定义
│           └── index.ts        # 统一导出
├── docs/
│   ├── GOAL.md                 # 项目总目标
│   ├── PROGRESS.md             # 进度记录
│   ├── NEXT.md                 # 当前任务
│   ├── context.md              # 本文件
│   ├── advice/                 # 外部 AI 建议文件
│   └── design/                 # UI 设计文档
├── scripts/                    # 构建/部署/迁移脚本
├── docker-compose.yml          # 本地开发环境
└── pnpm-workspace.yaml         # pnpm workspace 配置
```

## 核心数据模型：Content JSON Block Tree

Block 类型：section、paragraph、list、teaching_step、exercise_group、choice_question、fill_blank_question、short_answer_question。

容器块（section、teaching_step、exercise_group）包含 children，叶子块包含内容。
顶层结构：`ContentDocument { version: number, blocks: Block[] }`。
在 Pydantic（`apps/api/app/schemas/content.py`）和 TypeScript（`packages/shared-types/src/content.ts`）中同步定义。

## 当前状态

- Phase 0 已完成：骨架搭建 + 项目重构（apps/ 目录结构、shared-types 包）
- Phase 1 待启动：核心循环（注册登录 + 任务 CRUD + AI 生成 + 编辑器 + 自动保存 + Word 导出）
- 所有 API 端点目前返回 501 Not Implemented

## 阶段路线图

- Phase 0：骨架搭建 ✅
- Phase 1：核心循环（能用）
- Phase 2：编辑器深度完善（好用）
- Phase 3：公域页面 & Auth 完善（有门面）
- Phase 4：账户设置 & 计费（能赚钱）
- Phase 5：UX 打磨（精致）
- Phase 6：运营基础设施（可运营）
- Phase 7：高级功能（按需迭代）

## 当前 API

- `GET /api/v1/health` — 健康检查（已实现）
- `GET/POST /api/v1/tasks` — 任务 CRUD（501 占位）
- `GET/PATCH/DELETE /api/v1/tasks/{id}` — 单个任务操作（501 占位）
- `GET/POST /api/v1/documents` — 文档 CRUD（501 占位）
- `GET/PATCH/DELETE /api/v1/documents/{id}` — 单个文档操作（501 占位）

## 数据库模型

- **User**: id (UUID), email (unique), name, password_hash, created_at
- **Task**: id (UUID), user_id (FK→User), title, subject, grade, topic, task_type, status (draft/generating/ready), timestamps
- **Document**: id (UUID), task_id (FK→Task), user_id (FK→User), doc_type, title, content (JSONB), version, timestamps

## 编码规范

- 前后端文件 < 800 行，函数 < 50 行
- 前端按 feature 组织（features/auth, features/editor 等）
- 后端按 layer 分（api/v1/endpoints → services → models）
- 共享类型放在 `packages/shared-types/`，通过 `@lessonpilot/shared-types` 引用
- AI prompt 模板放在 `apps/api/app/prompts/` 目录，不散落在业务代码中
- 不可变数据模式优先
