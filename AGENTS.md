# LessonPilot — Agent 行为约束

> 本文件定义 AI 助手的行为规范。产品定位、架构决策、技术栈、项目结构等详见 `CLAUDE.md`。

## 工作流程

### 开始工作前

1. 读 `AGENTS.md`（本文件）确认行为约束、分支约束和回复规范
2. 读 `CLAUDE.md` 了解产品定位、架构决策和当前状态
3. 读 `docs/NEXT.md` 了解当前 Cycle 的具体任务
4. 读 `docs/PROGRESS.md` 了解已完成的工作
5. 涉及产品方向、竞品迁移、质量标准、RAG、导出或验收时，优先读取 `docs/` 下对应专题文档

### 工作中

- **分支约束**：所有开发工作只能在 `ai` 分支上进行
- 聚焦当前 Cycle 的任务，不做范围外的事
- 遇到影响产品方向或偏离规划的决策时，先停下来询问
- **老师视角**：所有设计决策都要从老师的实际使用场景出发
- 真实密钥不允许写入仓库
- 每次回复前使用"恩泽"作为称呼
- 文档口径不一致时，先以 `AGENTS.md` 约束行为，以 `CLAUDE.md` 约束产品和架构事实，再用 `docs/NEXT.md` 判断当前任务边界
- 不把长期路线图、竞品分析或技术规格塞进 `docs/NEXT.md`；`NEXT.md` 只维护当前 Cycle

### 专用 Codex Skills

如果本机可用，遇到对应任务时优先使用以下 LessonPilot 专用 skills：

- `lessonpilot-product-strategist`：产品策略、竞品迁移、路线图优先级
- `lessonpilot-teaching-quality-reviewer`：教案/学案内容质量审查
- `lessonpilot-word-template-importer`：学校 Word 模板识别与字段映射
- `lessonpilot-legacy-material-ingestor`：旧 Word/PPT/讲义/资料迁移到结构化内容
- `lessonpilot-rag-knowledge-pack-builder`：语文 RAG 知识包设计、入库与引用验证
- `lessonpilot-export-quality-checker`：导出前体检与 Word 提交质量检查
- `lessonpilot-cycle-maintainer`：`NEXT / PROGRESS / GOAL / CLAUDE` 等文档状态维护
- `lessonpilot-phase-autopilot-runner`：在用户明确授权的阶段内，自动拆分多个内部 Cycle 并持续执行到阶段验收口

### 完成任务后

1. 在 `docs/PROGRESS.md` 末尾追加完成记录
2. 更新 `docs/NEXT.md` 为下一个 Cycle
3. **不要在未经确认的情况下自动进入下一个 Cycle**

### 用户验收后

1. 提交代码：`git commit -m "日期 CycleN 做了什么（中文）"`
2. 推送：`git push origin ai`
