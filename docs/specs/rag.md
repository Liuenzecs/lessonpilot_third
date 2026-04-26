# RAG 规格

## 定位

LessonPilot 的 RAG 是知识增强生成，不是问答机器人。

流程：

1. 知识资料进入 `knowledge_chunks`。
2. 本地 BGE 或其他 embedding provider 生成向量。
3. 创建任务时根据课题路由到知识域。
4. 向量检索返回相关 chunk。
5. section prompt 注入参考资料。
6. 模型生成时插入 `[cite:chunk_id]`。
7. 后端清洗 citation，写入 `section_references`。
8. 前端展示参考资料 tooltip。

## 当前实现

- 存储：PostgreSQL + pgvector。
- 默认 embedding：`local_bge + BAAI/bge-m3 + cpu`。
- 生成模型：DeepSeek / MiniMax / Fake。
- 触发模式：`topic_route`。
- 当前重点知识域：语文文学类，尤其《红楼梦》。

## 生效判定

不能只看 `RAG_ENABLED=true`。

真正生效至少需要：

- 课题命中 domain。
- `knowledge_chunks` 有对应数据。
- embedding 生成成功。
- 检索返回相关 chunk。
- 模型输出 citation。
- 最终文档 `section_references` 非空。

## 失败时行为

- embedding 或检索失败时，生成应优雅退化为普通生成。
- 不应向老师暴露内部异常。
- 可在未来 UI 中提示“本次未命中知识库”。

## 后续演进

- 知识包版本管理。
- domain 路由配置化。
- 知识导入后台。
- 引用覆盖率和采纳率评估。
- 语文重点篇目知识库扩容。
