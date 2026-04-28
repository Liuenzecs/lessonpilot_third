# 当前任务：等待用户验收 Phase 17 P1

## 本阶段目标

全部 4 个 Phase 17 P1 任务已完成实施，等待用户手动验收。

详见 `docs/milestones/phase-16-migration-competitiveness.md` 和 `.claude/plans/humble-churning-sky.md`。

## 本轮实施切片

### P1-1：旧教案批量导入

- [x] 后端：batch-preview / batch-confirm 端点，批量导入服务包装函数
- [x] 前端：BatchImportView.vue（多文件选择 → 预览 → 逐项编辑 → 批量确认）
- [x] 备课台入口卡片"批量导入教案"
- [x] 单文件解析逻辑完全复用，单项失败独立报告

### P1-2：教研组分享链接

- [x] 后端：ShareLink / ShareComment 模型 + Alembic 迁移
- [x] 后端：share_service + 7 个 API 端点（创建/列表/更新/删除 + 公开只读视图 + 评论）
- [x] 前端：SharePanel.vue（权限/过期时间/复制链接/管理已有链接）
- [x] 前端：SharedDocumentView.vue（公开只读页，无需登录 + 可选评论）
- [x] 编辑器工具栏"分享"按钮

### P1-3：教学日历 + 学期计划

- [x] 后端：Semester / WeekSchedule / LessonScheduleEntry 三表模型 + 迁移
- [x] 后端：calendar_service + 9 个 API 端点（学期 CRUD + 排课/移课）
- [x] 前端：CalendarView.vue（学期面板 + 水平滚动周网格 + 点击排课 + 移除）
- [x] 备课台入口卡片"教学日历"

### P1-4：Word 修改回导（diff & merge）

- [x] 后端：reimport_service diff 引擎（difflib SequenceMatcher + 结构化比对）
- [x] 后端：preview + merge 端点（merge 前自动拍快照）
- [x] 前端：ReimportPanel.vue（三步向导：上传→逐 section 接受/拒绝→确认合并）
- [x] 编辑器工具栏"回导修改"按钮（仅教案可见）

## 已授权范围

- 全部 4 个 P1 任务均为新增模块，不破坏现有主链路
- 可新增数据库表、API 端点、前端页面
- 回导功能复用现有导入解析器 + 快照系统

## 验证结果

- 后端测试：176 passed
- 前端测试：49 passed
- 类型检查：passed

## 停止条件

- 等待用户手动验收 P1 功能
- 或用户明确指示暂停/调整方向
- **不自动进入 P2 任务，必须等用户确认**

## 验收标准

### P1-1 批量导入
- [ ] 选择 3+ 个 .docx → 批量预览 → 逐项调整元数据 → 批量确认 → 备课台看到全部导入的 task

### P1-2 分享链接
- [ ] 生成分享链接 → 无痕窗口打开 → 看到只读文档 → 留评论（如 comment 权限） → 返回编辑器看到评论

### P1-3 教学日历
- [ ] 创建学期 → 自动生成周 → 将已有 task 分配到不同周/天 → 日历视图正确显示

### P1-4 Word 回导
- [ ] 导出 docx → 在 Word 中修改 → 上传回导 → 看到逐 section diff → 接受部分修改 → 编辑器内容已合并 → 历史版本中有 pre-merge 快照
