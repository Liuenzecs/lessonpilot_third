## 当前状态

- Sprint 0（项目清理与准备）已完成。
- Sprint 1（内容模型 + AI 服务重写）已完成。
- Sprint 2（前端 UI 重设计）已完成。
- Sprint 3（创建页 + 流式生成体验）已完成。
- Sprint 4（Section Editor + AI 重写）已完成。
- Sprint 5（导出重写）已完成。
- 下一步是 **Sprint 6 — 测试 + 收尾**。
- 在你手动确认前，不自动开始 Sprint 6。

## Sprint 5 完成情况

### 后端导出服务重写
- [x] 重写 `services/export_service.py` — 删除全部旧 block 导出代码（~675 行），替换为结构化模型导出
- [x] 教案 Word 导出：表头信息栏 + 三维目标 + 重难点 + 教学准备 + 表格式教学过程 + 板书设计 + 反思留空区
- [x] 学案 Word 导出：学生信息表 + 学习目标 + 重难点 + 知识链接 + 三段式学习流程 + 达标测评 + 拓展延伸 + 反思留空区
- [x] 使用场景影响排版：公立校完整 5 列表格、家教简化 4 列（省略设计意图）
- [x] 只导出 status 为 confirmed 的 section
- [x] 中式现代风配色（墨色正文、石青标题、象牙表格头）
- [x] 删除 HTML 导出和 PDF 导出（MVP 不需要）

### 后端端点更新
- [x] 更新 `documents.py` 导出端点 — 接入真实导出服务，替换空字节占位
- [x] 导出文件名包含教案/学案标识

### 前端导出更新
- [x] 重写 `useExport.ts` — 新增 `exportMultipleDocx` 支持批量导出
- [x] 更新 `EditorShellHeader.vue` — 多 document 时显示"导出全部"选项
- [x] 更新 `useEditorView.ts` — 新增 `handleExportAll()` 连续导出教案+学案
- [x] 更新 `EditorView.vue` — 传递新 props 和 events

### 后端测试
- [x] 新建 `tests/test_export.py` — 10 个测试覆盖教案/学案导出、场景差异、confirmed 过滤、空内容

### 验证
- [x] 后端 ruff check 通过（export_service.py 零 lint 错误）
- [x] 后端 38 个测试全部通过（28 旧 + 10 新）
- [x] 前端 type-check 通过
- [x] 前端 build 通过

## 下一步：Sprint 6 — 测试 + 收尾

详见 `docs/milestones/implementation-plan-v2.md` Sprint 6 部分。
