# 当前状态

- Sprint 0-6 已全部完成。
- **MVP 实施计划全部交付。**
- 后端：90 个测试，88.86% 覆盖率，ruff 零错误
- 前端：type-check / lint / build 全部通过
- 等待用户手动验收核心流程（Phase 5）。

## 手动验收清单

- [ ] 注册 → 登录
- [ ] 创建备课（教案+学案，公立校场景）
- [ ] AI 流式生成（观察 token-by-token 效果）
- [ ] Section 级编辑（确认/修改内容）
- [ ] Section 级 AI 重写（rewrite/expand/simplify）
- [ ] 导出 Word（教案 + 学案分别导出）
- [ ] 备课台列表操作（搜索、复制、删除）

验收通过后，提交代码：`git commit -m "Sprint6 测试收尾：90个测试、88.86%覆盖率、文件重命名、覆盖率门控"`
