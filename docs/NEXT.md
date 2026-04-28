# 当前任务：等待下一步指示（Phase 14 已验收）

## 本阶段目标

让 LessonPilot 逐步记住老师常用的目标写法、教学过程风格和学校提交措辞，使后续生成内容更像“我平时会交的教案”，而不是每次都从通用模板重新开始。

## 已授权范围

- 新增用户私有的个人风格档案。
- 设置页可查看、编辑和启用 / 关闭风格记忆。
- 生成和局部重写时读取当前用户风格档案并注入 prompt。
- 文档更新 Phase 14 规格、验收脚本和进度记录。
- 不做跨用户共享，不把风格数据混入公共知识库。
- 不做不可控的全自动学习；v1 先做老师显式维护的风格偏好。
- 不扩展全学科，不做学校后台、团队共享或复杂画像系统。
- 不自动提交 / 推送，等待用户验收。

## 本轮实施切片

- [x] 新增 Phase 14 阶段文档和当前任务边界。
- [x] 后端新增个人风格档案模型、迁移、schema、service 和 API。
- [x] 生成 / 重写链路注入老师个人风格提示。
- [x] 设置页新增“风格记忆”入口，可编辑目标写法、过程风格、学校措辞和禁用词。
- [x] 补充后端 / 前端测试。
- [x] 更新 `docs/ACCEPTANCE.md`、`docs/PROGRESS.md`、`CLAUDE.md`。

## 验证结果

- `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests/test_account_service.py apps/api/tests/test_style_profile.py -q`：17 passed
- `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests/api/test_documents.py -q`：8 passed
- `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests -q`：157 passed
- `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
- `pnpm --dir apps/web type-check`：passed
- `pnpm --dir apps/web test --run`：46 passed
- `pnpm --dir apps/web build`：passed

## 验收结论

- 用户已要求提交推送，Phase 14 第一轮视为通过验收。
- 当前不自动进入下一阶段。

## 停止条件

等待用户明确指定下一阶段或新的 Cycle。
