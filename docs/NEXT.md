## 当前状态

- Sprint 0（项目清理与准备）已完成。
- Sprint 1（内容模型 + AI 服务重写）已完成。
- Sprint 2（前端 UI 重设计）已完成。
- Sprint 3（创建页 + 流式生成体验）已完成。
- Sprint 4（Section Editor + AI 重写）已完成。
- 下一步是 **Sprint 5 — 导出重写**。
- 在你手动确认前，不自动开始 Sprint 5。

## Sprint 4 完成情况

### 后端 Rewrite 流式化
- [x] 重写 rewrite_service.py — 新增 section_start/section_delta/section_complete 事件
- [x] 逐 token 转发，与 generation 流式协议对齐

### 前端 Content 工具
- [x] 删除 shared-types/content.ts 中旧 block 类型系统
- [x] 重写 shared/utils/content.ts — 删除 block stub，新增结构化模型直接操作函数

### 编辑器组件重写
- [x] 删除 8 个旧 block 组件
- [x] 新建 SectionPanel.vue — 可折叠 section 面板
- [x] 新建 SectionEditors/ 目录（7 个组件）
- [x] 新建 SectionAiActions.vue — AI 操作下拉菜单
- [x] 新建 EditorToolbar.vue
- [x] 重写 EditorView.vue — Tab 切换 + section 列表
- [x] 重写 useEditorView.ts → 拆为 4 个 composable（useAutoSave + useEditorGeneration + useEditorRewrite）
- [x] 简化 EditorShellHeader.vue — 移除 PDF
- [x] 重写 ExportPreviewModal.vue — 直接展示结构化内容
- [x] 重写 HistoryDrawer.vue — 快照预览改为结构化内容

### SSE 消费
- [x] consumeRewriteStream 支持 AbortSignal

### 验证
- [x] 后端 ruff check 通过
- [x] 后端 28 个测试全部通过
- [x] 前端 type-check 通过
- [x] 前端 build 通过

## 下一步：Sprint 5 — 导出重写

详见 `docs/milestones/implementation-plan-v2.md` Sprint 5 部分。
