# Word 教案导入规格

## 目标

让老师上传旧 `.docx` 教案后，先看到结构化预览，再确认创建为 LessonPilot 的普通教案文档。

## 支持范围

- v1 只支持 `.docx` 教案。
- 不支持 `.doc`、PDF、PPT、讲义、学案或批量导入。
- 不调用大模型自动改写导入内容。

## API

### `POST /api/v1/import/lesson-plan/preview`

请求：

- `multipart/form-data`
- 字段：`file`
- 文件大小上限：5MB

响应：

- `metadata`：标题、学科、年级、课题、课时、课型、使用场景
- `content`：映射后的 `LessonPlanContent`
- `mapped_sections`：已识别 section 名称
- `unmapped_sections`：未能确定归属的内容
- `warnings`：老师需要检查的导入风险

### `POST /api/v1/import/lesson-plan/confirm`

请求：

- `metadata`
- `content`

响应：

- `task`
- `document`

确认后创建普通 `Task + Document`，文档内容默认保持 `pending`。

## 映射规则

### 标题识别

常见标题别名：

- `教学目标`、`学习目标`、`三维目标`、`核心素养目标` -> `objectives`
- `教学重难点`、`教学重点`、`教学难点`、`重难点` -> `key_points`
- `教学准备`、`课前准备`、`教具准备` -> `preparation`
- `教学过程`、`教学流程`、`课堂教学过程` -> `teaching_process`
- `板书设计`、`板书` -> `board_design`
- `教学反思`、`课后反思` -> `reflection`

### 教学过程

优先解析表格列：

- 环节
- 时间 / 时长
- 教师活动
- 学生活动
- 设计意图

若表格缺列或段落无法完整识别，应保守导入并给出 warning，不静默丢弃。

## 失败与降级

- 非 `.docx` 文件返回 400。
- 文件过大返回 413。
- 解析失败返回 400，不暴露底层异常。
- 没有识别到核心 section 时仍返回预览，但必须把文本放入 `unmapped_sections` 并提示老师检查。
