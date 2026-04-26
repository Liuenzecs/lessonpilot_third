# RAG 规格

## 定位

LessonPilot 的 RAG 是知识增强生成，不是问答机器人。

流程：

1. 知识资料进入 `knowledge_chunks`。
2. 本地 BGE 或其他 embedding provider 生成向量。
3. 创建任务时根据知识包 manifest 的 trigger terms 路由到知识域。
4. 向量检索返回相关 chunk。
5. section prompt 注入参考资料。
6. 模型生成时插入 `[cite:chunk_id]`。
7. 后端清洗 citation，写入 `section_references`。
8. 生成流返回 `rag_status`，前端展示知识命中状态。
9. 前端展示参考资料 tooltip。

## 当前实现

- 存储：PostgreSQL + pgvector。
- 默认 embedding：`local_bge + BAAI/bge-m3 + cpu`。
- 生成模型：DeepSeek / MiniMax / Fake。
- 触发模式：`topic_route`。
- 路由来源：`apps/api/app/data/knowledge_packs/chinese_literature_v1.json`。
- 当前重点知识域：`红楼梦`、`春`、`背影`、`桃花源记`、`岳阳楼记`、`天净沙·秋思`。

## 知识包 metadata

种子脚本写入 chunk 时，应在 `metadata_` 中保留：

- `pack_id`
- `pack_version`
- `trigger_terms`
- `embedding_runtime`

重复执行种子脚本时，以 `domain + title` 判断已存在条目，不重复创建 chunk。

## 诊断接口

`POST /api/v1/knowledge/diagnose`

请求：

- `topic`
- `requirements`
- `top_k`

响应包含：

- `status`：`disabled / unmatched / matched_empty / ready / degraded`
- `domain`
- `matched_keywords`
- `chunk_count`
- `preview_chunks`
- `message`

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
- UI 应提示“本次未命中知识库”或“已降级为普通生成”。

## 后续演进

- 知识包版本管理。
- 知识导入后台。
- 引用覆盖率和采纳率评估。
- 语文重点篇目知识库继续扩容。
