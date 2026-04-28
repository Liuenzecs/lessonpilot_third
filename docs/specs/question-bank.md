# 语文重点篇目分层题库规格

## 目标

为学案生成提供精选题目支撑，不再完全依赖 AI 即时生成题目，提升题目质量和教师信任度。

## 数据模型

```python
class Question(SQLModel, table=True):
    id: UUID = primary key
    chapter: str          # 篇目名称，如 "春"、"桃花源记"
    grade: str            # 年级，如 "七年级上"
    question_type: str    # choice | fill_blank | short_answer
    difficulty: str       # A（基础）| B（理解）| C（拓展）| D（选做）
    prompt: str           # 题干
    options: list[str]    # 选项列表（选择题），JSON 存储
    answer: str           # 参考答案
    analysis: str         # 解析
    source: str           # 来源，如 "2024北京中考" 或 "原创"
    tags: list[str]       # 标签，如 ["修辞手法", "比喻"]
    subject: str          # 默认 "语文"
    created_at: datetime
```

## 初始数据规模

覆盖 7-9 年级语文重点篇目，每课 15-20 道分层题：

- 七年级上：《春》《济南的冬天》《从百草园到三味书屋》《论语十二章》《天上的街市》《皇帝的新装》
- 七年级下：《邓稼先》《说和做》《黄河颂》《最后一课》《紫藤萝瀑布》
- 八年级上：《消息二则》《藤野先生》《回忆我的母亲》《背影》《中国石拱桥》《苏州园林》《孟子三章》《愚公移山》
- 八年级下：《社戏》《回延安》《大自然的语言》《恐龙无处不有》《桃花源记》《小石潭记》《核舟记》
- 九年级上：《沁园春·雪》《我爱这土地》《乡愁》《岳阳楼记》《醉翁亭记》《湖心亭看雪》
- 九年级下：《祖国啊我亲爱的祖国》《孔乙己》《变色龙》《送东阳马生序》《出师表》

## 选题服务

- `get_chapters(subject?)` → 篇目列表
- `get_questions(chapter, difficulty?, type?, limit?)` → 题目列表
- `select_questions_for_study_guide(chapter, count_per_level)` → 按层选题（A级2道、B级2道、C级1道、D级1道）

## 学案生成集成

- 学案生成 prompt 中注入题库题目：
  - 自主学习（A级）：优先从题库选题
  - 合作探究（B级）：优先从题库选题
  - 展示提升（C级）：优先从题库选题
  - 拓展延伸（D级）：优先从题库选题
- 题库未覆盖的篇目：AI 照常生成题目
- 生成结果中标记题目来源（"来自题库" vs "AI 生成"）

## API 端点

```
GET  /api/v1/questions/chapters          → 篇目列表
GET  /api/v1/questions?chapter=X&...     → 题目搜索/筛选
GET  /api/v1/questions/{id}              → 单题详情
POST /api/v1/questions/seed              → 加载种子数据（管理用）
```

## 前端

- 题库浏览页：按篇目筛选、按难度/题型过滤
- 编辑器中学案题目区：标记"来自题库"或"AI 生成"
