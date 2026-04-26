# 当前 RAG 能力说明

## 定位

LessonPilot 当前的 RAG 不是“知识问答机器人”，而是“知识增强生成”。

主流程是：

1. 知识资料入库到 `knowledge_chunks`
2. 用 embedding 建立向量表示
3. 生成前按知识包 trigger terms 判断是否命中知识域
4. 命中后做向量召回
5. 把召回结果注入 section 级生成 prompt
6. 模型生成内容并带上引用标记
7. 落库时清理 `[cite:...]`，把引用元数据保存在 `section_references`
8. 编辑器显示知识增强状态，并用引用徽标和悬浮卡片给老师展示来源

## 当前实现

- 存储层：PostgreSQL + `pgvector`，表为 `knowledge_chunks`
- embedding：默认 `local_bge + BAAI/bge-m3 + cpu`
- 生成模型：DeepSeek / MiniMax 继续只负责文本生成
- 检索触发：`RAG_TRIGGER_MODE=topic_route`，路由来自知识包 manifest
- 当前知识域：`红楼梦`、`春`、`背影`、`桃花源记`、`岳阳楼记`、`天净沙·秋思`
- 检索输出：按 domain 检索，默认 `RAG_TOP_K=8`
- 引用链路：生成时可插入 `[cite:chunk_id]`，落库后转成 `section_references`
- 状态链路：生成流返回 `rag_status`，前端显示命中、未命中或降级状态
- 前端展示：编辑器 section 头部支持“参考资料”徽标和 tooltip

## 当前边界

- v1 仍聚焦语文备课，不是全学科通用知识库
- 当前知识包仍是首批语文重点篇目，不覆盖全学段全篇目
- 检索质量评估仍以人工验证为主，暂未引入离线评测面板
- 本地 BGE 首次加载模型会更慢，但稳定性比把 embedding 绑在 MiniMax 上更高

## 为什么改成本地 BGE

- 主生成链路不再依赖 MiniMax embedding 的计费与权限边界
- Token Plan 对文本生成能力描述明确，但对当前 embedding 路线覆盖并不稳定
- 本地模型更适合做可控、可复验、可离线排障的知识增强

## 当前配置

根目录 `.env.example` 与 `apps/api/.env.example` 已提供以下配置：

- `EMBEDDING_PROVIDER=local_bge`
- `EMBEDDING_MODEL=BAAI/bge-m3`
- `EMBEDDING_DEVICE=cpu`
- `RAG_ENABLED=true`
- `RAG_TRIGGER_MODE=topic_route`
- `RAG_MAX_KNOWLEDGE_TOKENS=3000`
- `RAG_TOP_K=8`

说明：

- `MINIMAX_*` 默认只用于文本生成
- 只有当 `EMBEDDING_PROVIDER=minimax` 时，才会使用 `MINIMAX_EMBEDDING_MODEL`

## 下一步完善建议

- 为知识包增加后台导入、去重和版本管理
- 加离线评测：命中率、引用覆盖率、老师采纳率
- 扩充语文重点篇目知识库，再考虑扩到其他学科
