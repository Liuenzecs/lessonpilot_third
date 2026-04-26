# Section SSE 协议

## 目标

生成和重写都使用同一套 section 级 SSE 协议，避免前端出现旧 consumer 分叉和“生成后短暂不可见”问题。

## 事件顺序

常规生成：

1. `status`
2. `rag_status`
3. `progress`
4. `section_start`
5. `section_delta`
6. `section_document`
7. `citations` 可选
8. `section_done`
9. 重复下一个 section
10. `status`
11. `document_done`

局部重写：

1. `status`
2. `section_start`
3. `section_delta`
4. `section_document`
5. `section_done`
6. `status`
7. `document_done`

## 关键事件

### section_start

表示某个 section 开始生成。

必须包含：

- `section_name`
- `title`

生成任务还应包含：

- `doc_type`

### section_delta

表示当前 section 的 token/text delta。

必须包含：

- `section_name`
- `delta`

### section_document

表示某个 section 已完成并落库。

必须回传完整 document payload，而不是局部内容。

必须包含：

- `id`
- `task_id`
- `user_id`
- `doc_type`
- `title`
- `content`
- `version`
- `created_at`
- `updated_at`
- `section_name`
- `section_title`

### rag_status

常规生成时返回一次，表示本次生成的知识增强状态。

`status` 可取：

- `disabled`：RAG 已关闭。
- `unmatched`：课题未命中任何知识域。
- `matched_empty`：命中知识域，但数据库中没有对应 chunk。
- `ready`：命中知识域并检索到可注入的 chunk。
- `degraded`：命中知识域，但检索或 embedding 临时失败，已降级普通生成。

必须包含：

- `status`
- `message`
- `matched_keywords`
- `chunk_count`
- `retrieved_count`

可选包含：

- `domain`

### citations

当 section 使用 RAG 引用时返回。

前端最终应以 `section_document.content.section_references` 为准。

### document_done

表示本次生成或改写流程结束。

## 前端处理原则

- delta 仅用于临时流式展示。
- `section_document` 到达后立即用服务端完整文档替换本地草稿。
- 不要用半文档 patch 拼接复杂状态。
- 重写和生成共用 consumer。
