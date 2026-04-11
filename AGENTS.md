# LessonPilot

> 本文件用于约束 Codex 的工作方式，内容与 `CLAUDE.md` 保持对齐。

AI 赋能的备课工具 — 结构化教案编辑器 + AI 填充引擎。

## 架构决策

- **Content JSON Block Tree 是中枢**：编辑器渲染它，AI 生成它，导出消费它
- **单体优先**：前端 Vue 3 单 app，后端 FastAPI 单服务，不拆微服务
- **pnpm workspace 管理**：apps/ 放可部署应用，packages/ 放跨应用共享包
- **编辑器是视图层**：content JSON 是数据层，两者通过提取/灌入操作连接
- **AI 输出必须结构化**：后端解析校验，前端只渲染确认后的数据
- **AI 内容待确认**：所有 AI 生成以 pending 状态插入，老师主动接受后合入
- **API 版本前缀**：`/api/v1/`

## 技术栈

- 前端：Vue 3 + TypeScript + Vite + Pinia + Vue Router + TanStack Query
- 编辑器：Tiptap（ProseMirror 封装）
- 后端：FastAPI + Python 3.12+ + SQLModel + PostgreSQL
- AI 通信：REST + SSE
- 导出：python-docx (Word), weasyprint (PDF)
- 共享类型：`@lessonpilot/shared-types`（packages/shared-types/）

## 项目结构

```text
New_lessonpilot/
├── apps/
│   ├── web/                    # Vue 3 前端
│   │   └── src/
│   │       ├── app/            # 路由、布局、全局配置
│   │       ├── features/       # 按功能模块组织
│   │       │   ├── auth/
│   │       │   ├── task/
│   │       │   ├── editor/     # 核心：块级编辑器
│   │       │   ├── generation/ # AI 生成交互
│   │       │   └── export/
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
│       │   ├── models/         # SQLModel 表模型
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
├── docs/                       # 项目文档
│   ├── GOAL.md                 # 项目总目标
│   ├── PROGRESS.md             # 进度记录
│   ├── NEXT.md                 # 当前任务
│   ├── context.md              # 项目上下文快照（发给外部 AI）
│   ├── advice/                 # 外部 AI 建议文件
│   └── design/                 # UI 设计文档
├── scripts/                    # 构建/部署/迁移脚本
├── docker-compose.yml          # 本地开发环境
└── pnpm-workspace.yaml         # pnpm workspace 配置
```

## 开发命令

```bash
# 前端
cd apps/web && pnpm dev

# 后端
cd apps/api && uvicorn app.main:app --reload

# 数据库
docker compose up -d

# 安装所有依赖（workspace 根目录）
pnpm install
```

## 编码规范

- 前后端文件 < 800 行，函数 < 50 行
- 前端按 feature 组织（features/auth, features/editor 等）
- 后端按 layer 分（api/v1/endpoints → services → models）
- 共享类型放在 `packages/shared-types/`，通过 `@lessonpilot/shared-types` 引用
- AI prompt 模板放在 `apps/api/app/prompts/` 目录，不散落在业务代码中
- 不可变数据模式优先
- Content JSON 类型变更需同步：`packages/shared-types/src/content.ts` ↔ `apps/api/app/schemas/content.py`

## 外部 AI 协作

本项目使用外部 AI 模型（如 Opus 4.6）提供高层次建议，Codex 负责读取并执行。

### context.md（项目快照）

- `docs/context.md` 是项目上下文的完整快照，用于复制粘贴给外部 AI
- 用户手动维护此文件，在项目结构或关键决策变更时更新
- **Codex 不要自动修改此文件**

### advice/ 文件夹（外部建议）

- `docs/advice/` 存放外部 AI 的建议文件
- 文件命名格式：`YYYY-MM-DD-topic-slug.md`
- 每个文件包含元数据头：Source、Date、Status（draft/accepted/superseded）、Supersedes
- Codex 只执行 `Status: accepted` 的建议中的 Action Items
- `Status: draft` 的建议只读不执行，等待用户确认
- `Status: superseded` 的建议忽略

### 读取顺序（扩展原有工作流）

1. 读 `GOAL.md`（可能已被外部建议更新）
2. 扫描 `docs/advice/` 中所有 `Status: accepted` 的文件
3. 读 `PROGRESS.md` 和 `NEXT.md`
4. 执行任务时参考 accepted 建议中的 Action Items

### 更新 GOAL.md

如果 accepted 的建议文件包含对 GOAL.md 的替换方案：
1. 先向用户确认是否替换
2. 用户确认后再更新 GOAL.md
3. 在 PROGRESS.md 中记录变更

## 工作流程

### 开始工作前

1. 先读 `docs/GOAL.md` 了解项目总目标、架构决策和技术约束
2. 扫描 `docs/advice/` 中所有 `Status: accepted` 的建议文件
3. 再读 `docs/PROGRESS.md` 了解已完成的工作，**不要重复已完成的工作**
4. 最后读 `docs/NEXT.md` 了解当前任务
5. 如果 `GOAL.md`、`NEXT.md` 或 accepted advice 中写了“参考某设计文档全面落地”，必须把对应设计文档完整读完，再开始实现

### 工作中

- 只聚焦 `docs/NEXT.md` 中列出的任务
- 遇到影响架构或偏离 `GOAL.md` 的决策时，先停下来询问
- 不要在当前任务范围之外重构或重组代码
- 目录结构变更后，及时更新 `docs/context.md` 和 `AGENTS.md` 中的项目结构描述
- 如果阶段要求或 accepted advice 写的是“全面落地”某份设计文档，该设计文档就是强制验收规范，不是可选参考
- 如果设计文档与阶段清单、已实现代码或用户新指令之间出现冲突，先停下来询问，不要自行折中
- 不要用“功能基本可用”替代“设计文档已落地”；交互、视觉层级和关键体验流也属于实现范围

### 完成任务后

1. 在 `docs/PROGRESS.md` 末尾追加完成记录，格式如下：
   ```
   ## [Phase X] — 简要标题
   - 完成日期：YYYY-MM-DD
   - 完成内容：具体做了什么
   - 关键文件：列出变更的文件
   - 验证结果：lint/test/build 结果
   - Status: DONE
   ```
2. 如果当前阶段要求“参考某设计文档全面落地”，在写入 `Status: DONE` 前必须逐项对照 phase 清单和设计文档自查；只要有任何关键交互、视觉结构或验收项未完成，就不能写 `DONE`
3. 如果之前的完成记录被用户判定为未达标，必须先在 `docs/PROGRESS.md` 中明确纠正状态，再写新的完成记录
4. 更新 `docs/NEXT.md` 为下一阶段的任务（如果没有新指令则标记"等待用户指示"）
5. **不要在未经确认的情况下自动进入下一阶段**

### 用户验收后

1. 用户验收通过后，提交代码并推送到远程仓库
2. 提交消息格式：`日期 阶段 做了什么（中文描述）`，例如：`2026-04-10 Phase0 骨架搭建：前后端项目初始化、Content JSON schema定义、Docker Compose配置`
3. 推送命令：`git push origin main`

## 其他规则

- 称呼：每次回复前必须使用“恩泽”作为称呼
