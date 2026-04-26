# ADR-0001: 以结构化 JSON 作为内容中枢

## 状态

Accepted

## 背景

LessonPilot 的目标不是生成一段不可控长文本，而是帮助老师完成可编辑、可确认、可导出的备课文档。

如果只保存 Markdown 或纯文本：

- 前端难以做 section 级编辑。
- AI 重写难以定位具体教学环节。
- Word 导出难以稳定映射学校格式。
- RAG 引用难以挂到具体 section。
- 老师确认状态难以可靠保存。

## 决策

LessonPilot 以教案/学案结构化 JSON 作为内容中枢。

所有核心链路围绕同一份结构：

- 编辑器渲染。
- 生成。
- 重写。
- 自动保存。
- Word 导出。
- 引用展示。

## 结果

收益：

- section 级生成和重写更稳定。
- 老师可以逐节确认。
- Word 导出可控。
- 未来模板、质量检查和旧资料导入都能基于统一结构扩展。

代价：

- 前后端类型必须同步。
- AI 输出必须解析和校验。
- 对不同学科扩展时需要谨慎演进 schema。

## 约束

类型变更必须同步修改：

- `packages/shared-types/src/content.ts`
- `apps/api/app/schemas/content.py`

并补充对应测试和导出逻辑。
