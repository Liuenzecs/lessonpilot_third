# 课件 PPTX 导出规格

## 目标

从教案结构化 JSON 自动生成课堂教学课件（PPTX），连接"备课"和"上课"。

## 课件大纲结构

```
Slide[]
  ├── index: int                    # 幻灯片序号
  ├── slide_type: str               # title | objectives | key_points | teaching_step | questions | summary | homework
  ├── title: str                    # 幻灯片标题
  ├── bullet_points: list[str]      # 要点列表
  ├── speaker_notes: str            # 演讲者备注（来自设计意图 + 教师活动）
  └── step: TeachingProcessStep | None  # 关联的教学环节（仅 teaching_step 类型）
```

## 教案 → 课件映射规则

| 教案 Section | 课件 Slide(s) | 内容来源 |
|-------------|--------------|---------|
| 基本信息 | 1 页标题页 | 课题/学科/年级/课时/课型 |
| 教学目标 | 1 页 | objectives（每条一点） |
| 教学重难点 | 1 页 | key_points + difficulties |
| 教学过程 | N 页（每环节 1 页） | teacher_activity 为要点，design_intent 为备注 |
| 板书设计 | 1 页摘要页 | board_design 全文 |
| 作业/反思 | 1 页作业页 | 留空模板 |

## PPTX 生成

- 使用 `python-pptx` 库
- 默认使用空白布局，手动构建文本框
- 配色：与 Word 导出一致的 `#2c2c2c`（墨色）、`#3a7ca5`（石青）等
- 字体：标题使用微软雅黑 28pt，正文宋体 18pt
- 教学环节幻灯片：左侧环节名称 + 右侧要点，备注设为设计意图

## API

- 复用 `GET /api/v1/documents/{id}/export?format=pptx`
- 响应 Content-Type: `application/vnd.openxmlformats-officedocument.presentationml.presentation`

## 前端

- 导出菜单增加"导出课件（PPTX）"按钮
- 右侧面板增加"课件大纲预览"：显示 slide 列表，可调整顺序
