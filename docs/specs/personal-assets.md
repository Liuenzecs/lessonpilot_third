# 个人资料库规格

## 目标

让老师把旧教案、讲义、PPT 和教学笔记带进 LessonPilot，作为个人私有备课资产复用。

## 支持范围

v1 支持：

- `.docx`：旧教案、学案、讲义、教学笔记
- `.pptx`：PPT 大纲、课堂问题链、课件文案

暂不支持：

- `.doc`
- PDF
- 图片 OCR
- 学校级共享资料库

## 预览与确认

资料上传后先进入预览：

- `asset_type`：旧教案、学案/讲义、PPT 大纲、教学笔记、参考资料
- `title / subject / grade / topic`
- `extracted_sections`
- `unmapped_sections`
- `reuse_suggestions`
- `warnings`

确认入库后保存为当前用户私有资产。所有私有资料不得进入公共知识包，不得被其他用户检索。

## 私有复用

Phase 11 起，个人资料可作为生成参考：

- `GET /api/v1/personal-assets/recommend` 根据 `subject / grade / topic / keywords` 返回当前用户的推荐资料片段。
- 推荐结果只来自当前用户的 `PersonalAsset`，不得返回公共知识包或其他用户数据。
- v1 使用可解释匹配：标题、课题、年级、栏目标题、正文片段命中关键词后排序。
- 生成请求可传 `use_personal_assets` 和 `personal_asset_ids`；未传时保持普通生成。
- 生成流返回 `asset_status`，用于展示“我的资料命中 / 未命中 / 未启用 / 降级”。
- 个人资料引用写入 `section_references`，`knowledge_type` 使用 `personal_asset`，前端展示为“我的资料”。
