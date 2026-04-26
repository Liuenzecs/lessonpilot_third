# Phase 5：知识可信闭环

## Phase Charter

- Phase name：知识可信闭环
- Goal：让语文重点篇目生成具备可见的知识命中状态和可追溯引用证据。
- Why now：当前 RAG 基础链路已存在，但知识覆盖、路由维护和命中反馈仍偏工程化，老师无法稳定判断“这次是否真的参考了资料”。
- Allowed scope：RAG 知识包、知识路由、知识诊断 API、生成 SSE、编辑器状态展示、RAG 文档与验收脚本。
- Non-goals：全学科扩张、管理后台、旧 Word 导入、学校模板记忆、生产部署、真实密钥配置。
- Commit/push policy：实现与验证后停在验收口，不自动提交或推送。

## Implementation Slice

1. 知识包基础
   - 将知识种子整理为 JSON manifest。
   - 每条 chunk 保持教学可用的精炼内容，不写入受版权限制的全文。
   - metadata 写入 `pack_id / pack_version / trigger_terms / embedding_runtime`。

2. 命中与诊断
   - 路由从 manifest 的 domain trigger 配置读取。
   - 新增诊断 API，返回 disabled / unmatched / matched_empty / ready / degraded。
   - 生成链路在检索后推送 `rag_status` SSE 事件。

3. 老师可见状态
   - 编辑器显示“知识增强状态”。
   - 命中时展示 domain 与参考资料数量。
   - 未命中或降级时使用老师可理解的提示，不暴露内部异常。

4. 验收与文档
   - 更新 `docs/specs/rag.md`、`docs/rag-current.md`、`docs/ACCEPTANCE.md`。
   - 阶段完成时更新 `docs/PROGRESS.md` 与 `docs/NEXT.md`，停在用户验收口。

## Acceptance Script

1. 执行知识入库脚本，确认首批知识包导入且重复运行不新增重复 chunk。
2. 分别诊断：
   - `红楼梦薛宝钗人物分析`
   - `春 朱自清 第一课时`
   - `桃花源记文言文教学`
   - 一个未覆盖课题
3. 创建语文任务并生成，确认编辑器能看到知识增强状态。
4. 打开 section 引用，确认命中 RAG 时 `section_references` 非空。
5. 关闭 RAG 或模拟 embedding 失败，确认生成优雅降级。

## Stop Condition

本阶段实现到验收口即停止，不自动进入迁移能力、导出质量或上课包阶段。
