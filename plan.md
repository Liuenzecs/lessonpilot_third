# 编辑器 UI 修复计划

## 问题诊断

通过代码审查，发现 5 个问题的根本原因如下：

### 问题 1 & 3：编辑器页面布局别扭 + Section 框太小

**根因**：Sprint 4 重写了 `SectionPanel.vue`，使用了新的 CSS class 名（`section-panel`、`section-header`、`section-body` 等），但 `editor.css` 从未同步更新。**这些新 class 名在 CSS 中完全没有定义**。

受影响的缺失 class：
- `section-panel`、`section-header`、`section-title`、`section-body`
- `collapse-toggle`、`collapse-icon`
- `status-badge`、`status-pending`、`status-confirmed`
- `confirm-btn`
- `streaming-content`、`streaming-text`（SectionPanel 内的）、`streaming-cursor`
- `doc-tabs`、`doc-tab`
- `editor-toolbar`、`toolbar-btn`

CSS 文件中仍保留的是旧 class 名（`section-card`、`section-card-head` 等），但没有任何组件使用这些旧名。

### 问题 2：流式生成完毕后内容自动隐藏

**根因**：`useEditorGeneration.ts` 中 `onSectionComplete()` 清空 `streamingText`。理论上 `onDocument()` 事件会将内容应用到 `draftDocument`，编辑器应该渲染新内容。但由于 SectionPanel 缺少 CSS（问题 1），编辑器区域虽然存在但不可见，用户看到的就是"内容消失了"。

此外，`onSectionComplete` 和 `onDocument` 之间存在时间差：streaming text 先被清空，document 事件后到。应改为在 `onDocument` 应用文档后再清空 streaming text。

### 问题 4：教案/学案按钮点了不切换

**根因**：`useEditorView.ts` 第 58-62 行的 `activeDocument` 计算逻辑有 bug：

```typescript
const activeDocument = computed(() => {
  const docs = documentsQuery.data.value?.items ?? [];
  if (docs.length <= 1) return draftDocument.value ?? docs[0] ?? null;
  return draftDocument.value ?? docs[activeDocTabIndex.value] ?? docs[0];
});
```

`draftDocument` 始终从 `primaryDocument`（index 0）加载，且总是 truthy。所以即使用户点击"学案"tab 设置 `activeDocTabIndex = 1`，计算属性仍然返回 `draftDocument.value`（教案）。需要添加 tab 切换时重新加载对应文档到 `draftDocument` 的逻辑。

### 问题 5：AI 流式生成中有格式问题

**根因**：`SectionPanel.vue` 中的 `.streaming-content` / `.streaming-text` class 没有定义 CSS，缺少 `white-space: pre-wrap`。AI 生成的内容包含换行和列表格式，但被渲染为纯文本，所有格式丢失。

## 修复方案

### Phase 1：修复 SectionPanel 及相关组件的 CSS（问题 1、3、5）

**文件**：`apps/web/src/features/editor/styles/editor.css`

为 `SectionPanel.vue` 中所有使用的 class 添加完整 CSS 定义：

1. `.section-panel` — 卡片样式（border、border-radius、padding、background）
2. `.section-header` — flex 布局、行高、cursor
3. `.section-title` — 标题字号、字重
4. `.section-body` — 内边距、间距
5. `.collapse-toggle` / `.collapse-icon` — 折叠按钮样式
6. `.status-badge` / `.status-pending` / `.status-confirmed` — 状态徽标
7. `.confirm-btn` — 确认按钮
8. `.streaming-content` / `.streaming-text` — 流式文本（含 `white-space: pre-wrap`）
9. `.streaming-cursor` — 闪烁光标动画
10. `.doc-tabs` / `.doc-tab` — 标签切换样式（含 active 状态）
11. `.editor-toolbar` / `.toolbar-btn` — 工具栏样式

同时清理不再使用的旧 class（`section-card` 等）。

设计原则：
- 保持中式现代风（宣纸白底、石青强调色、8-12px 圆角、轻投影）
- Section 卡片最小高度充足，内容不拥挤
- 标题字号足够大，与正文区分明显
- Tab 有明确的 active/inactive 状态区分

### Phase 2：修复 Tab 切换逻辑（问题 4）

**文件**：`apps/web/src/features/editor/composables/useEditorView.ts`

1. 添加 `watch(activeDocTabIndex, ...)` 监听器
2. 当 tab 切换时，从 `documentsQuery.data` 中取对应文档，调用 `applyServerDocument()` 加载到 `draftDocument`
3. 同时重置 `collapsedSections` 和相关状态
4. 修正 `activeDocument` 的计算逻辑：tab 切换后 `draftDocument` 应更新为对应文档

### Phase 3：修复流式文本消失问题（问题 2）

**文件**：`apps/web/src/features/editor/composables/useEditorGeneration.ts`

1. `onSectionComplete` 不再立即清空 `streamingText`，改为只记录完成计数
2. 在 `onDocument` 应用文档后，再清空对应 section 的 `streamingText`
3. `onDone` 最终清空所有流式状态

**文件**：`apps/web/src/features/editor/components/SectionPanel.vue`

1. 当 section 有 `sectionData`（非空内容）且不在 streaming/rewriting 状态时，即使 streamingText 已清空，也应显示编辑器内容
2. 确保 streaming text 和编辑器内容之间的过渡平滑

### Phase 4：验证与微调

1. 启动前端开发服务器，验证所有修复
2. 检查生成流式 → 完成后内容保留的完整流程
3. 检查教案/学案切换是否正常工作
4. 检查响应式布局在不同宽度下的表现

## 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| CSS 变更影响其他页面 | 低 | 所有修改限于 editor.css，且只影响编辑器路由 |
| Tab 切换逻辑引入新 bug | 中 | 添加 watch 时加入保存检查，避免丢失未保存编辑 |
| 流式文本不清空导致内存问题 | 低 | onDone 事件确保最终清空 |

## 影响范围

- `apps/web/src/features/editor/styles/editor.css` — 添加约 150 行 CSS
- `apps/web/src/features/editor/composables/useEditorView.ts` — 修改约 20 行
- `apps/web/src/features/editor/composables/useEditorGeneration.ts` — 修改约 15 行
- `apps/web/src/features/editor/components/SectionPanel.vue` — 可能微调模板
