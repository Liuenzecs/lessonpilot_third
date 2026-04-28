# LessonPilot

> 本文件用于约束 AI 助手的工作方式，内容与 `AGENTS.md` 保持对齐。

AI 备课助手 — 一份备课，教案学案一起出。

## 产品定位

**一句话**：新老师输入学科/年级/课题 → AI 流式生成教案和/或学案 → 改两下 → 导出学校标准格式 Word → 15 分钟完成备课。

### 核心产品原则

1. **老师视角优先** — 从三种老师的实际工作流出发设计（公立校新手/大学生家教/机构老师）
2. **结构感优先** — 给骨架，AI 填肉，老师调整
3. **AI 是引擎不是主角** — 不是聊天生成，是在结构化框架内填充
4. **老师掌控感** — AI 生成内容以"待确认"状态呈现，老师主动接受后合入
5. **教学内容质量第一** — AI 输出的教案/学案内容要真正能用，不能是泛泛而谈

### 目标用户

| 用户 | 场景 | 教案需求 | 学案需求 |
|------|------|---------|---------|
| 公立校新手老师（0-3 年） | 学校要求提交教案 | 学校标准格式 | 正式导学案 |
| 大学生家教老师 | 快速备课 | 简化版 | 讲义/练习 |
| 机构新手老师/小机构老师 | 追求效率+质量 | 中等规范 | 讲义为主 |

### 教案 + 学案

- 教案和学案是**平级选项**，用户可选择：只生成教案 / 只生成学案 / 都生成
- 使用场景（公立校/家教/培训机构）影响模板和导出格式
- MVP 学科：**语文**

### 教案内容结构（语文）

```
教案 (LessonPlan)
├── 基本信息：课题/学科/年级/课时/课型
├── 教学目标（三维目标或核心素养）
├── 教学重难点
├── 教学准备
├── 教学过程（主体，80%）
│   └── 每个环节含：教师活动 + 学生活动 + 设计意图 + 时间
├── 板书设计
└── 教学反思（留空）
```

### 学案内容结构（语文）

```
学案 (StudyGuide)
├── 基本信息：课题/学科/年级/班级/姓名/日期
├── 学习目标（"我能..."口吻）
├── 重点难点预测
├── 知识链接（前置知识）
├── 学习流程
│   ├── 自主学习（A/B 级）
│   ├── 合作探究（B/C 级）
│   └── 展示提升（C 级）
├── 达标测评（当堂检测）
├── 拓展延伸（D 级选做）
└── 自主反思
```

## 架构决策（不可违反）

- **教案/学案结构化 JSON 是中枢**：编辑器渲染它，AI 生成它，导出消费它
- **单体优先**：前端 Vue 3 单 app，后端 FastAPI 单服务
- **pnpm workspace 管理**：apps/ 放可部署应用，packages/ 放跨应用共享包
- **生成链路以 section 为原子单位**：后端按 section 顺序生成，section 内仍保留 token delta 流式
- **AI 输出结构化**：后端解析校验，前端只渲染确认后的数据
- **API 版本前缀**：`/api/v1/`

## 技术栈

- 前端：Vue 3 + TypeScript + Vite + Pinia + Vue Router + TanStack Query
- 编辑器：Tiptap（Section-based document editor）
- 后端：FastAPI + Python 3.12+ + SQLModel + PostgreSQL
- AI 通信：REST + SSE（section 级事件 + section 内 token delta）
- AI 模型：DeepSeek / MiniMax（文本生成）+ Local BGE（默认 embedding）
- 导出：python-docx（Word，学校标准教案格式）
- 共享类型：`@lessonpilot/shared-types`（packages/shared-types/）

## UI 设计方向

**教师文档桌 / Google Docs 手感**：

- 以根目录 `DESIGN.md` 为唯一视觉基准
- 核心体验是“顶部文档工具栏 + 左侧目录 + 中间纸张画布 + 右侧检查栏”
- 主色收敛为纸白、暖灰、教学蓝、通过绿、提醒橙、阻断红
- 公域页、备课台、创建页、编辑器、设置页都优先呈现“能备、能查、能导出”的文档工作流
- 减少嵌套卡片和装饰性营销结构，优先可读、可扫、可判断下一步
- 暗色模式不作为主流程能力继续扩展

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
│   │           ├── styles/     # Notion 风格设计系统
│   │           └── api/        # fetch wrapper + vue-query
│   └── api/                    # FastAPI 后端
│       ├── app/
│       │   ├── api/v1/         # API 路由
│       │   │   ├── router.py   # v1 router 聚合
│       │   │   └── endpoints/  # auth, tasks, documents, account, health
│       │   ├── services/       # auth, task, document, generation, rewrite, export, llm
│       │   ├── models/         # User, Task, Document, DocumentSnapshot, AuthToken, Feedback
│       │   ├── schemas/        # 请求/响应 schema + 教案/学案内容模型
│       │   ├── core/           # 配置、数据库、安全
│       │   └── prompts/        # AI prompt 模板（学科专项）
│       ├── alembic/            # 数据库迁移
│       └── tests/              # 测试
├── packages/
│   └── shared-types/           # 教案/学案 TypeScript 类型
├── docs/
│   ├── GOAL.md                 # 项目总目标
│   ├── PROGRESS.md             # 进度记录
│   ├── NEXT.md                 # 当前任务
│   ├── PRODUCT.md              # 产品定位、目标用户、非目标
│   ├── COMPETITIVE.md          # 竞品迁移策略
│   ├── TEACHER_WORKFLOWS.md    # 老师真实工作流
│   ├── QUALITY_RUBRIC.md       # 教案/学案质量标准
│   ├── ACCEPTANCE.md           # 手动验收脚本
│   ├── ROADMAP.md              # 阶段路线图
│   ├── specs/                  # 技术契约
│   ├── decisions/              # 架构决策记录（ADR）
│   ├── milestones/             # 里程碑文档
│   │   ├── product-replan-v2.md     # 产品重新规划
│   │   └── implementation-plan-v2.md # 实施计划
│   └── design/                 # UI 设计文档
├── docker-compose.yml
└── pnpm-workspace.yaml
```

## 开发命令

```bash
# 前端
cd apps/web && pnpm dev --host 127.0.0.1 --port 5173 --strictPort

# 后端
cd apps/api && uvicorn app.main:app --reload

# 数据库
docker compose up -d

# 安装依赖
pnpm install
```

### 本地端口约束

- 前端开发服务固定使用 `5173`。
- 如果 `5173` 被占用，先释放占用该端口的进程，再重新使用 `5173`。
- 不要临时切到 `5174` 或其他端口，除非用户明确指定。

## 编码规范

- 前后端文件 < 800 行，函数 < 50 行
- 前端按 feature 组织
- 后端按 layer 分（endpoints → services → models）
- 共享类型放在 `packages/shared-types/`
- AI prompt 模板放在 `apps/api/app/prompts/`
- 不可变数据模式优先
- 教案/学案类型变更需同步：`packages/shared-types/src/content.ts` ↔ `apps/api/app/schemas/content.py`

## 当前进度

Sprint 0-6（MVP 构建）已全部完成。当前进入 **Cycle 硬化与拓展阶段**。

**当前状态**：Cycle 1-4、Phase 5、Phase 6、Phase 7-10、Phase 11、Phase 12 与 Cycle 12 Hotfix 已完成；Phase 13 `真实试用硬化与首份可交付闭环` 已推进到试用闭环。Phase 14 `老师个人风格记忆` 第一轮已完成并通过用户验收。Phase 15 `备案临时商业化收口` 已完成并通过用户验收，等待下一步指示。

**Cycle 进度**：
- [x] **Cycle 1**：关键 Bug 修复（AI 菜单 + 多行编辑器）
- [x] **Cycle 2**：后端加固（速率限制 + 异常处理 + 前端测试）
- [x] **Cycle 3**：UI/UX 润色（去 AI 味 + 术语统一 + 设计令牌迁移）
- [x] **Cycle 4**：数据库模板库 + AI 输出质量验证

**最近完成内容**：
- 公域导航和页脚临时移除“定价”入口
- `/pricing` 路由重定向到首页，不展示定价页
- 帮助中心与服务条款清理付费、支付、会员、套餐、专业版升级等商业化表述
- 保留登录、注册和备课主功能，不新增后端 API 或数据库变更

**验证结果**：Phase 15 前端备案收口测试、完整前端测试、类型检查与生产构建均已通过

## 文档地图

- `AGENTS.md`：Agent 行为约束、分支约束、回复规范、skills 使用口径
- `CLAUDE.md`：项目总览、产品定位、架构决策、技术栈、当前状态
- `docs/NEXT.md`：当前 Cycle 的任务和验收清单，不放长期 backlog
- `docs/PROGRESS.md`：完成记录，只追加，不替代路线图
- `docs/PRODUCT.md`：产品定位、目标用户、原则和非目标
- `docs/COMPETITIVE.md`：ClassIn / 科大讯飞 / 希沃等平台迁移策略
- `docs/TEACHER_WORKFLOWS.md`：公立校、家教、机构老师真实备课流程
- `docs/QUALITY_RUBRIC.md`：教案/学案内容质量标准
- `docs/ACCEPTANCE.md`：手动验收脚本
- `docs/ROADMAP.md`：阶段路线图和候选方向
- `docs/specs/content-model.md`：结构化内容模型契约
- `docs/specs/section-sse.md`：section 级 SSE 协议
- `docs/specs/import-docx.md`：旧 Word 教案导入规格
- `docs/specs/export-docx.md`：Word 导出规格
- `docs/specs/rag.md`：RAG 规格和生效判定
- `docs/decisions/`：架构决策记录

## 专用 Codex Skills

如本机存在以下 skills，遇到对应任务时应优先使用：

- `lessonpilot-product-strategist`：产品策略、竞品迁移、路线图优先级
- `lessonpilot-teaching-quality-reviewer`：教案/学案内容质量审查
- `lessonpilot-word-template-importer`：学校 Word 模板识别与字段映射
- `lessonpilot-legacy-material-ingestor`：旧 Word/PPT/讲义/资料迁移到结构化内容
- `lessonpilot-rag-knowledge-pack-builder`：语文 RAG 知识包设计、入库与引用验证
- `lessonpilot-export-quality-checker`：导出前体检与 Word 提交质量检查
- `lessonpilot-cycle-maintainer`：`NEXT / PROGRESS / GOAL / CLAUDE` 等文档状态维护
- `lessonpilot-phase-autopilot-runner`：在用户明确授权的阶段内，自动拆分多个内部 Cycle 并持续执行到阶段验收口

## 工作流程

### 开始工作前

1. 读 `AGENTS.md` 确认行为约束、分支约束和回复规范
2. 读 `CLAUDE.md`（本文件）了解产品定位、架构决策和当前状态
3. 读 `docs/NEXT.md` 了解当前 Cycle 的具体任务
4. 读 `docs/PROGRESS.md` 了解已完成的工作
5. 根据任务类型读取文档地图中的专题文档

### 工作中

- **分支约束**：所有开发工作只能在 `ai` 分支上进行，提交和推送也只能到 `ai` 分支
- 聚焦当前 Cycle 的任务
- 遇到影响产品方向或偏离规划的决策时，先停下来询问
- 不要在当前 Cycle 范围之外添加功能
- **老师视角**：所有设计决策都要从老师的实际使用场景出发
- **前端端口固定**：本地前端开发服务固定使用 `5173`；如端口被占用，释放后仍用 `5173`，不要临时换端口
- 真实密钥不允许写入仓库
- 每次回复前使用"恩泽"作为称呼

### 完成任务后

1. 在 `docs/PROGRESS.md` 末尾追加完成记录
2. 更新 `docs/NEXT.md` 为下一个 Cycle
3. **不要在未经确认的情况下自动进入下一个 Cycle**

### 用户验收后

1. 提交代码：`git commit -m "日期 CycleN 做了什么（中文）"`
2. 推送：`git push origin ai`

## MVP 范围约束

### 当前要做
- 用户注册/登录
- 一站式创建备课（学科/年级/课题 + 教案/学案选择 + 使用场景）
- Section 级流式生成教案/学案（section 内 token delta）
- Section 式文档编辑器
- Section 级 AI 重写
- 学校标准格式 Word 导出
- 遵循 `DESIGN.md` 的教师文档桌 UI
- 备课台（教案列表）
- 语文知识增强备课（RAG）

### 暂时不做
- PDF 导出
- 历史版本
- 管理后台
- 分析管道
- SSR
- Sentry
- 复杂计费系统
- 暗色模式
- Onboarding
- 反馈 widget
- 多学科（只做语文）
