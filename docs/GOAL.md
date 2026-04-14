# LessonPilot — 项目总目标

## 一句话定位

AI 赋能的备课工具：**结构化教案编辑器 + AI 填充引擎**。

老师打开产品 → 选学科/年级/主题 → 10 秒后看到结构化教案草稿 → 改几下 → 导出 Word → 15 分钟内完成备课。

## 核心产品原则

1. **老师视角优先** — 从三种老师的实际工作流出发设计（公立校新手/大学生家教/机构老师）
2. **结构感优先** — 给骨架，AI 填肉，老师调整
3. **AI 是引擎不是主角** — 不是聊天生成，是在结构化框架内填充
4. **老师掌控感** — AI 生成内容以"待确认"状态呈现，老师主动接受后合入
5. **教学内容质量第一** — AI 输出的教案/学案内容要真正能用，不能是泛泛而谈

## 目标用户

| 用户 | 场景 | 教案需求 | 学案需求 |
|------|------|---------|---------|
| 公立校新手老师（0-3 年） | 学校要求提交教案 | 学校标准格式 | 正式导学案 |
| 大学生家教老师 | 快速备课 | 简化版 | 讲义/练习 |
| 机构新手老师/小机构老师 | 追求效率+质量 | 中等规范 | 讲义为主 |

## 教案 + 学案

- 教案和学案是**平级选项**，用户可选择：只生成教案 / 只生成学案 / 都生成
- 使用场景（公立校/家教/培训机构）影响模板和导出格式
- MVP 学科：**语文**

## 架构决策（不可违反）

- **教案/学案结构化 JSON 是中枢**：编辑器渲染它，AI 生成它，导出消费它
- **单体优先**：前端 Vue 3 单 app，后端 FastAPI 单服务
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

## UI 设计方向

**中式现代风**：宣纸白 + 墨色 + 石青 + 胆黄配色，思源宋体标题，8-12px 圆角，大量留白。

## 实施路线图

基于 `docs/milestones/implementation-plan-v2.md`，分 6 个 Sprint 重做核心产品体验。

- [x] **Sprint 0 — 项目清理与准备**
  - 删除不需要的代码（billing、admin、analytics、onboarding、feedback、SSR、Sentry、SlowAPI）
  - 精简后端和前端到 MVP 最小依赖
  - 添加 MiniMax LLM Provider 配置
- [x] **Sprint 1 — 内容模型 + AI 服务重写**
  - 新的教案/学案结构化内容 Schema
  - AI Provider 抽象 + DeepSeek/MiniMax/Fake 实现
  - 新 prompt 模板聚焦教学内容质量
  - 真正 token-by-token 流式输出
- [x] **Sprint 2 — 前端 UI 重设计（中式现代风）**
  - 全局设计系统重写
  - Landing、认证页、备课台中式现代风重设计
- [x] **Sprint 3 — 创建页 + 流式生成体验**
  - 一站式创建页（学科/年级/课题/教案学案/使用场景）
  - 真正 token-by-token 流式生成消费
  - StreamingText 逐字显示 + 停止生成
  - collectSections 修复（编辑器可渲染结构化内容）
- [ ] **Sprint 4 — Section Editor + AI 重写**
  - 文档式编辑器重写（Tab 切换教案/学案）
  - Section 级 AI 重写/扩写/精简
- [ ] **Sprint 5 — 导出重写**
  - 学校标准格式 Word 导出
  - 教案表格式教学过程 + 学案分层题目
- [ ] **Sprint 6 — 测试 + 收尾**
  - 完整测试套件
  - 手动验证核心流程

## MVP 范围约束

### 当前要做
- 用户注册/登录
- 一站式创建备课（学科/年级/课题 + 教案/学案选择 + 使用场景）
- AI 流式生成教案/学案（语文，token-by-token）
- Section 式文档编辑器
- Section 级 AI 重写
- 学校标准格式 Word 导出
- 中式现代风 UI
- 备课台（教案列表）

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

## 规划文档

- `docs/milestones/product-replan-v2.md` — 产品重新规划
- `docs/milestones/implementation-plan-v2.md` — 实施计划（6 个 Sprint）
- `docs/NEXT.md` — 当前任务
- `docs/PROGRESS.md` — 进度记录
