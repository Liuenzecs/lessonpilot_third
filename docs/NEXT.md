# 当前任务：数学公式生成、编辑器展示与 Word 导出修复（待验收）

## 本轮目标

解决生成内容中的数学公式“乱码”问题，让 LessonPilot 能在结构化 JSON 仍作为内容中枢的前提下，稳定保留、展示并导出可编辑的 Word 原生公式。

## 已授权范围

- 不改变后端 API、数据库表和文档内容模型。
- 不引入完整数学公式编辑器，只做可编辑原文 + 公式预览。
- 优先解决生成、重写、编辑器展示和 Word 导出链路。
- 不自动提交 / 推送，等待用户验收。

## 已实现

- 后端新增 LaTeX 文本保护：生成 / 重写解析 JSON 前会保护 `\frac`、`\theta`、`\sqrt`、`\(...\)` 等反斜杠写法。
- 后端新增控制字符修复：对已被 JSON 转坏的常见公式片段做递归修复。
- Prompt 增加公式输出约束：行内公式使用 `\\(...\\)`，独立公式使用 `$$...$$`，JSON 字符串里的反斜杠必须双写。
- 前端引入 KaTeX，新增 `FormulaText` 渲染组件与公式解析工具。
- 编辑器目标、重难点、教学准备、教学过程、测评题、答案、解析、板书 / 反思和流式输出区域支持公式预览。
- Word 导出新增 OMML 公式写入：常见 LaTeX 公式会导出为 Word 原生 `m:oMath`，支持分式、根号、上下标、希腊字母和常用运算符。
- 保持老师可编辑原始文本，不把结构化内容改成富公式 block。

## 验证结果

- `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests/test_generation_service.py -q`：4 passed
- `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests/test_export.py -q`：12 passed
- `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app/services/formula_text.py apps/api/app/services/generation_service.py apps/api/tests/test_generation_service.py`：passed
- `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/tests`：passed
- `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests -q`：150 passed
- `pnpm --dir apps/web type-check`：passed
- `pnpm --dir apps/web test --run`：44 passed
- `pnpm --dir apps/web build`：passed

## 待用户验收

- 生成一个含数学公式的教案或学案，例如“勾股定理 第一课时”或“二次函数配方法练习”。
- 检查生成过程和最终 section 中的 `\\(...\\)` / `$$...$$` 公式是否显示为正常数学排版。
- 手动编辑一段公式文本，确认下方公式预览随内容更新。
- 导出 Word 后打开 `.docx`，确认公式不是 LaTeX 源码，而是 Word 中可选中、可编辑的公式对象。
- 确认原有语文教案 / 学案生成、改写、确认、引用和导出入口不受影响。

## 停止条件

本轮停在公式展示修复验收口；不自动进入下一阶段，不自动提交推送。
