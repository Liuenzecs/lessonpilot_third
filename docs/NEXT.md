## 当前状态

- Sprint 0（项目清理与准备）已完成。
- Sprint 1（内容模型 + AI 服务重写）已完成。
- Sprint 2（前端 UI 重设计）已完成。
- Sprint 3（创建页 + 流式生成体验）已完成。
- 下一步是 **Sprint 4 — Section Editor + AI 重写**。
- 在你手动确认前，不自动开始 Sprint 4。

## Sprint 3 完成情况

### 后端流式输出
- [x] 重写 generation_service.py — 逐 token 转发 + section 边界检测
- [x] 新 SSE 事件协议（section_start/section_delta/section_complete）
- [x] _SectionTracker 启发式 section 检测

### 前端 SSE 消费
- [x] 重写 useGeneration.ts — StreamingEventHandlers + AbortController
- [x] consumeGenerationStream 支持 signal 参数

### 编辑器流式集成
- [x] useEditorView.ts — streamingText/docType 字段 + stopGeneration()
- [x] StreamingText.vue — 逐字显示 + 闪烁光标
- [x] EditorStatusBanner — 停止生成按钮

### collectSections 修复
- [x] collectLessonPlanSections — 6 section 映射
- [x] collectStudyGuideSections — 9 section 映射

### 创建页重写
- [x] 一站式布局 — 全部 9 字段
- [x] 新增选项常量（课型/场景/生成类型）

### 验证
- [x] 后端 ruff check 通过
- [x] 后端 28 个测试全部通过
- [x] 前端 type-check 通过
- [x] 前端 build 通过

## 下一步：Sprint 4 — Section Editor + AI 重写

详见 `docs/milestones/implementation-plan-v2.md` Sprint 4 部分。
