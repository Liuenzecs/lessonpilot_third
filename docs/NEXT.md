## 当前状态

- Sprint 0（项目清理与准备）已完成。
- Sprint 1（内容模型 + AI 服务重写）已完成。
- 下一步是 **Sprint 2 — 创建页重做**。
- 在你手动确认前，不自动开始 Sprint 2。

## Sprint 1 完成情况

### 后端内容模型
- [x] 重写 schemas/content.py — LessonPlanContent + StudyGuideContent 结构化模型
- [x] 重写 schemas/task.py — 新增 scene/lesson_type/class_hour/lesson_category
- [x] 重写 schemas/document.py — Section 级 rewrite payload
- [x] 新建 schemas/lesson.py — GenerationContext + SectionRewriteContext
- [x] 更新 models/task.py — 新增 4 个列
- [x] 更新 models/document.py — 移除 task_id unique 约束
- [x] 新建 Alembic 迁移

### AI 服务
- [x] 重写 llm_service.py — Provider 架构（Fake/DeepSeek/MiniMax）
- [x] 新建 prompt 模板（教案/学案/重写）
- [x] 重写 generation_service.py — 一次性流式生成
- [x] 重写 rewrite_service.py — Section 级重写

### Service/Endpoint
- [x] 更新 task_service.py — 根据 lesson_type 创建 1-2 个 document
- [x] 更新 document_service.py — doc_type 反序列化
- [x] 更新 tasks/documents endpoints

### 前端
- [x] 重写 shared-types/content.ts — 新类型 + 向后兼容
- [x] 重写 utils/content.ts — Section 操作 + block stub
- [x] 更新 editor/task 类型定义
- [x] 适配 useEditorView.ts 和 useEditor.ts
- [x] type-check + build 通过

### 验证
- [x] 后端 ruff check 通过
- [x] 后端 28 个测试全部通过
- [x] 前端 type-check 通过
- [x] 前端 build 通过

## 下一步：Sprint 2 — 创建页重做

详见 `docs/milestones/implementation-plan-v2.md` Sprint 2 部分。
