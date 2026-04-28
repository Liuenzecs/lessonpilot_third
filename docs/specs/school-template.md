# 学校 Word 模板规格

## 目标

让老师把学校常用 `.docx` 模板保存为个人导出规格，减少导出后的格式返工。

## 模板预览

模板预览读取：

- 段落中的标题、栏目名、静态说明
- 表格中的元信息字段
- 教学过程表格列
- 反思、签字、二次备课等空白区域

返回内容包括：

- `template_type`：`lesson_plan / study_guide / mixed`
- `field_mappings`：模板字段到 LessonPilot 内容字段的映射
- `section_order`：导出栏目顺序
- `table_layouts`：元信息表和教学过程表格列
- `blank_areas`：需要保留的空白区域
- `unsupported_items`：无法映射但需要老师知情的内容
- `warnings`：解析风险提示

## 保存与导出

保存后的模板归属于当前用户。导出时如提供 `template_id`，服务端按模板规格渲染；模板缺失、无权限或规格不完整时回退到默认导出。

v1 不承诺像素级复刻原 Word，只保证字段、栏目顺序、核心表格和空白区域可用。
