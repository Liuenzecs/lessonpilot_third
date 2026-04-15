# 当前任务：Cycle 3 — UI/UX 润色

## 目标
去 AI 味、统一术语、迁移到 CSS 设计令牌系统，让产品看起来更像正式产品而非 AI 输出。

## 任务清单

### 3.1 去 AI 味
- [ ] 审查所有用户可见文案，去除"AI 生成"、"智能"等表述，改为"备课"、"生成"等自然用语
- [ ] 审查 loading/skeleton 状态文案，确保不是"AI 正在思考"等表述
- [ ] 审查错误提示，确保用户友好且不暴露技术细节

### 3.2 术语统一
- [ ] 统一"备课" vs "教案" vs "学案"使用场景
- [ ] 统一按钮文案风格（确认/取消/保存/删除等）
- [ ] 统一 section 标题命名（教案 vs 学案 section 标题对齐）

### 3.3 设计令牌迁移
- [ ] 将 `apps/web/src/shared/styles/` 中的硬编码色值迁移到 CSS custom properties
- [ ] 确保所有色值使用 CLAUDE.md 定义的中式现代风配色（宣纸白、石青、胆黄等）
- [ ] 建立统一的 spacing / typography / radius / shadow 令牌

## 验收标准
- 用户界面无"AI"字样出现（技术文档除外）
- 所有色值使用 CSS custom properties，无硬编码
- 术语统一，按钮文案一致
- 所有 CI 检查通过（type-check / lint / build / pytest / ruff / vitest）

## 后续 Cycle 预览
- **Cycle 4**：数据库模板库 + AI 输出质量验证
