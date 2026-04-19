# LessonPilot RAG 实现详解

## 这份文档是给谁看的

这份文档是给第一次接触 RAG、第一次接触这个项目的人看的。

如果你是下面这几类人，这份文档都适合你：

- 你知道“大模型会生成内容”，但不知道“RAG 到底是什么”
- 你知道项目里有 `knowledge_chunks`、`embedding`、`section_references`，但不明白它们怎么串起来
- 你想排查“为什么这次生成没有走到 RAG”
- 你想以后扩到别的学科，比如数学、英语、历史

这份文档会尽量不用黑话。就算必须出现术语，我也会先解释它是什么意思。

---

## 一句话先讲清楚：我们项目里的 RAG 是什么

在 LessonPilot 里，RAG 不是“聊天问答机器人”。

它更像是：

1. 先把教研资料切成很多小知识卡片
2. 给每张知识卡片做向量化
3. 老师输入课题时，系统先去知识库里找“和这个课题最相关”的几张卡片
4. 把这些卡片塞进 prompt
5. 再让大模型按 section 去写教案/学案
6. 如果模型用了某张知识卡片，还会把出处记录下来，最后显示给老师

所以它不是“先生成，再去找知识”。

它是：

`先检索知识 -> 再生成内容 -> 再保留引用证据`

---

## 二、先理解 5 个核心名词

### 1. 知识库

这里的知识库不是一个 Word 文件夹，也不是一堆 PDF。

在这个项目里，知识库最终会被整理成数据库表里的很多条记录，每条记录叫一个 `KnowledgeChunk`。

对应代码：

- [knowledge.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/models/knowledge.py)

每条记录大概长这样：

- `domain`：属于哪个知识域，比如“红楼梦”
- `knowledge_type`：这条知识是什么类型，比如人物分析、情节摘要、诗词赏析
- `title`：标题
- `content`：正文
- `source`：来源
- `chapter`：章节
- `embedding`：这条知识的向量
- `metadata_`：额外信息

你可以把它理解成：

“数据库里的一个小知识卡片”

---

### 2. Embedding

Embedding 可以理解成“把一段文字翻译成机器更擅长比较相似度的一串数字”。

比如：

- “薛宝钗人物分析”
- “《红楼梦》中薛宝钗的性格特点”

这两句话字面不完全一样，但意思很近。

模型把它们都转成向量后，这两个向量在数学空间里会更接近。

于是系统就能做一件事：

“不是按关键词死匹配，而是按语义相似度找知识”

当前项目默认用的是本地 BGE：

- `EMBEDDING_PROVIDER=local_bge`
- `EMBEDDING_MODEL=BAAI/bge-m3`

对应代码：

- [config.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/core/config.py)
- [knowledge_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/knowledge_service.py)

---

### 3. 检索

检索不是在数据库里做 `LIKE '%薛宝钗%'` 这种字符串搜索。

这里做的是“向量检索”。

流程是：

1. 先把老师当前输入的课题，比如“薛宝钗人物分析”，也转成向量
2. 再和数据库里所有知识 chunk 的向量做相似度比较
3. 取最相近的前几条

代码位置：

- [knowledge_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/knowledge_service.py)

关键函数：

- `resolve_rag_domain()`
- `retrieve_knowledge()`
- `format_knowledge_context()`

---

### 4. Prompt 注入

检索到知识以后，不是直接把知识展示给老师就结束了。

它还会被拼进生成 prompt 里。

也就是说，大模型在写“教学目标”“合作探究”“达标测评”这些 section 之前，就已经看过系统检索到的知识了。

项目里注入的位置在：

- [generation_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/generation_service.py)
- [section_generation_prompt.md](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/prompts/section_generation_prompt.md)

当前 prompt 会明确告诉模型：

- 下面这些是参考资料
- 如果你用了它们，请在对应文本后加 `[cite:资料ID]`

这一步非常关键。

因为如果不要求模型留下引用标记，后面系统就不知道“它到底用了哪条知识”。

---

### 5. Citation / section_references

模型生成 section 时，如果用了某条知识，理论上会在文本里带上：

```text
[cite:某个chunk_id]
```

然后后端会做两件事：

1. 把这个 `[cite:...]` 从正文里删掉，不让老师看到脏标记
2. 反过来去数据库里查这个 `chunk_id` 对应的是哪条知识，把引用元数据保存到 `section_references`

最后老师在编辑器里看到的不是 `[cite:xxx]`，而是：

- “参考资料”徽标
- tooltip 里的来源、标题、章节、内容摘要

相关代码：

- [knowledge_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/knowledge_service.py)
- [generation_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/generation_service.py)

---

## 三、RAG 在这个项目里的全链路

下面按真实顺序讲一遍。

---

### 第 0 步：数据库先准备好知识表

项目通过 Alembic migration 新增了 `knowledge_chunks` 表，并启用了 `pgvector` 扩展。

对应文件：

- [20260418_0009_rag_knowledge_chunks.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/alembic/versions/20260418_0009_rag_knowledge_chunks.py)

这一步做了几件事：

- `CREATE EXTENSION IF NOT EXISTS vector`
- 创建 `knowledge_chunks` 表
- 给 `embedding` 建 HNSW 向量索引

为什么要索引？

因为以后知识库一多，不能每次生成都慢慢全表比相似度。向量索引能让检索更快。

---

### 第 1 步：把知识导入 knowledge_chunks

项目里已经有一个种子脚本：

- [seed_knowledge.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/scripts/seed_knowledge.py)

这个脚本现在做的事情是：

1. 定义一批《红楼梦》知识条目
2. 检查数据库里有没有同名标题，避免重复导入
3. 批量调用 embedding 服务给每条知识生成向量
4. 把结果写入 `knowledge_chunks`

导入时还会把当前 embedding 运行时信息写进 `metadata_`，比如：

- provider 是谁
- model 是谁
- device 是 cpu 还是 gpu
- version 标识是什么

为什么这么做？

因为以后如果你换了 embedding 模型，旧知识和新知识的向量可能不能混用。把运行时记录下来，后面才知道要不要重建知识库。

---

### 第 2 步：老师创建任务并点击生成

当老师在前端创建一个任务，比如：

- 学科：语文
- 课题：薛宝钗人物分析

后端会进入 section 级生成流程。

对应代码：

- [generation_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/generation_service.py)

这个服务不会一次把整篇教案吐完，而是按 section 一个个来：

- 教学目标
- 教学重难点
- 教学准备
- 教学过程
- 板书设计
- 教学反思

学案也是一样。

---

### 第 3 步：先判断这次要不要走 RAG

系统不会对所有课题都做 RAG。

它会先通过 `resolve_rag_domain(topic)` 判断当前课题能不能命中某个知识域。

对应代码：

- [knowledge_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/knowledge_service.py)

当前规则很简单：

- 如果课题里出现“红楼梦”“薛宝钗”“林黛玉”等关键词
- 就把这次任务路由到 `红楼梦` 这个 domain

当前配置还受这几个环境变量控制：

- `RAG_ENABLED`
- `RAG_TRIGGER_MODE`
- `RAG_TOP_K`
- `RAG_MAX_KNOWLEDGE_TOKENS`

它们定义在：

- [config.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/core/config.py)

目前最重要的是：

- `RAG_TRIGGER_MODE=topic_route`

意思是：

“只有课题命中既定规则，才检索知识”

不是全量总开。

---

### 第 4 步：把课题转成向量，再去知识库检索

如果路由命中了，系统会调用：

- `retrieve_knowledge()`

它会把：

- `topic`
- `requirements`

拼成一个查询文本，然后生成 query embedding。

接着执行 SQL：

- 在 `knowledge_chunks` 里找 `domain = 当前domain`
- 按 `embedding <=> query_embedding` 排序
- 取前 `top_k`

这里的 `<=>` 是 pgvector 的向量距离操作符。

简单理解就是：

“离得越近，语义越相关”

---

### 第 5 步：把检索结果拼成一段知识上下文

检索到的 chunk 不会直接原样塞进模型。

系统会通过：

- `format_knowledge_context()`

把它们整理成类似下面这种结构：

```text
## 参考资料

[资料] ID: xxx
来源：红楼梦人物辞典
类型：character_profile
章节：全书
内容：薛宝钗是……
```

然后这段文本会被塞进 section prompt。

对应 prompt 文件：

- [section_generation_prompt.md](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/prompts/section_generation_prompt.md)

---

### 第 6 步：模型按 section 生成

这时真正负责写内容的是文本模型，不是 embedding 模型。

当前文本模型 provider 是：

- `DeepSeek`
- 或 `MiniMax`
- 或本地 fake provider（测试用）

也就是说：

- embedding 模型负责“找资料”
- 文本模型负责“写教案/学案”

这两个角色不要混淆。

如果模型在生成时参考了某条知识，理论上就会在对应文本末尾加：

```text
[cite:chunk_id]
```

---

### 第 7 步：后端清洗 citation，并保存引用元数据

section 生成完成后，后端会执行两步引用处理：

#### 第一步：删掉正文里的 `[cite:...]`

因为老师不需要看到这些机器标记。

#### 第二步：根据 `chunk_id` 反查知识卡片元数据

系统会调用：

- `build_citation_metadata()`

把这些信息挂到内容对象的：

- `section_references`

里。

最终每个 section 可能变成类似这样：

```json
{
  "objectives": [...],
  "objectives_status": "pending",
  "section_references": {
    "objectives": [
      {
        "chunk_id": "xxx",
        "source": "红楼梦人物辞典",
        "title": "薛宝钗人物分析",
        "knowledge_type": "character_profile",
        "chapter": "全书",
        "content_snippet": "薛宝钗是……"
      }
    ]
  }
}
```

注意：

- 老师看到的正文里不会有 `[cite:...]`
- 但数据库里会有 `section_references`

这就是“RAG 是否真的生效”的最硬证据之一。

---

### 第 8 步：前端把参考资料显示给老师

当文档回到前端时，编辑器不会把 citation 当正文显示。

它会在 section 头部渲染“参考资料”相关 UI。

当前这条链路的目的是让老师知道：

- 这段内容不是完全裸生成
- 它参考了哪些资料
- 来源是什么

这对于老师建立信任很重要。

---

## 四、项目里哪些文件分别负责什么

如果你以后要改 RAG，先从下面这些文件找：

### 1. 配置层

- [config.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/core/config.py)

负责：

- 是否启用 RAG
- RAG 触发模式
- embedding provider / model / device
- top_k
- 最大注入 token 数

---

### 2. 数据库存储层

- [knowledge.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/models/knowledge.py)
- [20260418_0009_rag_knowledge_chunks.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/alembic/versions/20260418_0009_rag_knowledge_chunks.py)

负责：

- `knowledge_chunks` 表结构
- vector 扩展
- embedding 索引

---

### 3. 知识服务层

- [knowledge_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/knowledge_service.py)

负责：

- 路由到哪个 domain
- 生成 embedding
- 向量检索
- citation 提取与清洗
- 把 chunk_id 变成 section_references

---

### 4. 知识管理接口

- [knowledge.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/api/v1/endpoints/knowledge.py)

负责：

- 新增知识
- 查询知识
- 搜索知识
- 删除知识

这是一层“运营入口”。

以后如果你要做后台知识管理页，最终也会调用这组接口。

---

### 5. 生成主链路

- [generation_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/generation_service.py)

负责：

- 在生成前调用 RAG
- 把知识上下文注入 section prompt
- 生成后保存 section_references

---

### 6. 知识导入脚本

- [seed_knowledge.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/scripts/seed_knowledge.py)

负责：

- 准备初始知识
- 生成向量
- 写入数据库

---

## 五、当前版本为什么“看起来开了 RAG，但有时实际上没生效”

这是最容易让新人误会的地方。

RAG 不是“开关开了就一定生效”。

它至少要同时满足下面 4 个条件：

### 条件 1：总开关开着

也就是：

- `RAG_ENABLED=true`

---

### 条件 2：当前课题能命中路由规则

比如：

- “薛宝钗人物分析”会命中 `红楼梦`

但：

- “数学-导数”当前不会命中任何 domain

因为规则里暂时只有文学类里的 `红楼梦` 域。

---

### 条件 3：知识库里真的有数据

如果 `knowledge_chunks` 表是空的，那么就算命中 domain，也检索不到任何内容。

这是最常见的“伪开启”状态：

- 开关开着
- 规则也命中了
- 但库里没数据
- 最终还是退化成普通生成

---

### 条件 4：模型真的用了检索内容并留下 citation

即使检索到了知识，也还要看模型有没有实际引用。

如果模型没有输出 `[cite:chunk_id]`，那最终：

- 正文不会有引用痕迹
- `section_references` 也可能是空

所以判断 RAG 是否“真正落地”，不能只看日志里“检索到了几条知识”，还要看：

- 文档里 `section_references` 是否非空

---

## 六、怎么验证一次生成是不是“真的 RAG 生效了”

下面是项目里最可靠的验法。

### 方法 A：看知识表里有没有数据

```sql
select count(*) from knowledge_chunks;
```

如果是 `0`，那本次基本不可能形成真正的知识增强。

---

### 方法 B：看生成后的文档有没有 `section_references`

比如查某个任务的两个文档：

```sql
select id, doc_type, (content->'section_references')::text
from documents
where task_id = '某个任务ID';
```

如果你看到的是：

```text
{}
```

那说明没有保留下任何引用证据。

如果你看到某个 section 对应的引用数组，才算真的生效了。

---

### 方法 C：看编辑器里有没有“参考资料”

如果前端 section 头部出现“参考资料”并且能点开 tooltip，看见：

- 来源
- 标题
- 章节
- 摘要

那说明至少从后端到前端这条 citation 展示链路是通的。

---

## 七、当前版本的边界和局限

### 1. 现在还不是全学科 RAG

虽然系统名字叫 LessonPilot，但当前 RAG v1 主要还是：

- 语文
- 文学类
- 尤其是《红楼梦》相关

这不是 bug，是当前产品阶段的边界。

---

### 2. 当前路由规则还很“硬编码”

现在的 domain 命中规则写在：

- [knowledge_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/knowledge_service.py)

它还不是后台可配置规则。

也就是说，今天要支持“导数”，不是改个开关就行，而是还要：

1. 增加数学 domain 规则
2. 导入数学知识包

---

### 3. 模型是否留下 citation 仍有不确定性

当前项目已经在 prompt 里要求模型插入 `[cite:资料ID]`，但大模型不是数据库，它不会 100% 严格执行。

所以目前的“引用闭环”是：

- 已具备
- 但不是百分百稳定

这也是后续可以继续优化的地方。

---

### 4. 当前知识库运营能力还很轻

现在已经有知识接口和种子脚本，但还没有真正成熟的：

- 后台批量导入
- 去重
- 审核
- 版本管理
- 失效清理

所以当前更像“工程版 RAG 基础设施”，还不是“运营成熟版知识平台”。

---

## 八、如果以后要扩到数学“导数”，要做哪些事

很多人会误以为：

“把 `RAG_ENABLED=true` 打开就行了。”

其实不够。

至少要做下面这些：

### 第一步：增加数学 domain 路由规则

比如在 `_RAG_RULES` 里新增：

- `导数`
- `函数单调性`
- `极值`
- `切线`
- `变化率`

等关键词。

---

### 第二步：真的导入数学知识包

比如导入：

- 导数概念讲解
- 常见题型
- 易错点
- 例题解析
- 分层练习
- 教学设计建议

如果没有这些知识 chunk，路由命中也没用。

---

### 第三步：看现有 section schema 是否适合数学

语文的：

- 教学目标
- 教学过程
- 合作探究
- 达标测评

和数学的这些字段表面一样，但内容组织逻辑不同。

数学更依赖：

- 概念递进
- 例题顺序
- 变式训练
- 易错点拆解

所以未来真正扩学科时，除了 RAG，还要考虑 prompt 和模板层。

---

## 九、最适合小白记住的结论

如果你只记住 4 句话，就记下面这 4 句：

1. RAG 不是“生成完再补知识”，而是“先找知识，再生成”。
2. 这个项目里的知识库存放在 `knowledge_chunks` 表。
3. 真正判断 RAG 是否生效，最硬的证据不是开关，而是 `section_references`。
4. 现在的 RAG v1 主要是语文文学域，不是全学科通用。

---

## 十、快速排障清单

如果你发现“这次生成好像没走到 RAG”，按下面顺序排：

### 1. 看开关

- `RAG_ENABLED` 是不是 `true`

### 2. 看触发模式

- `RAG_TRIGGER_MODE` 是不是 `topic_route`
- 当前课题有没有命中 `_RAG_RULES`

### 3. 看知识库

- `knowledge_chunks` 里有没有数据
- 对应 `domain` 下有没有数据

### 4. 看 embedding 是否正常

- 本地 BGE 是否能加载
- 是否报模型下载或依赖错误

### 5. 看生成后的引用证据

- `section_references` 是否为空

### 6. 看前端展示

- 编辑器里有没有“参考资料”

---

## 十一、相关文件索引

为了方便你继续读代码，这里把最关键文件再列一遍：

- [config.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/core/config.py)
- [knowledge.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/models/knowledge.py)
- [knowledge_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/knowledge_service.py)
- [knowledge.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/api/v1/endpoints/knowledge.py)
- [generation_service.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/app/services/generation_service.py)
- [seed_knowledge.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/scripts/seed_knowledge.py)
- [20260418_0009_rag_knowledge_chunks.py](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/apps/api/alembic/versions/20260418_0009_rag_knowledge_chunks.py)
- [rag-current.md](C:/Users/realfeeling1/Desktop/创业项目/lessonpilot_third/docs/rag-current.md)

---

## 十二、最后一句话总结

LessonPilot 当前的 RAG，本质上是：

`知识入库（knowledge_chunks） + 本地向量化（BGE） + 按课题路由 + 向量检索 + section prompt 注入 + citation 回写 + 编辑器展示`

只要其中任意一环没通，系统就会退化成“普通生成”。

所以你以后排查时，不要只看“开关开没开”，而要看：

`知识有没有进去 -> 检索有没有命中 -> 引用有没有落库`
