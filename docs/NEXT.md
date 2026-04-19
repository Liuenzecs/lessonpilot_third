# 当前任务：稳定性优先收口（待验收）

## 本轮目标

把主链路从“能跑”收口到“稳定可演示、可继续扩展”：

- 编辑器生成与重写统一为 section 级 SSE 协议
- RAG embedding 默认改为本地 `BGE-M3`
- 主流程 UI 统一到 `DESIGN.md` 的 Notion 风格
- 项目文档、配置模板与安全口径同步

## 已实现

- [x] 后端生成链路改为按 section 顺序生成，事件统一为 `section_start / section_delta / section_document / section_done / document_done`
- [x] 重写链路切到同一套 SSE 协议，不再保留旧 consumer 分叉
- [x] `StudyGuideContent` 的 `self_study / collaboration / presentation` 全部统一通过 `learning_process` 读写
- [x] section 完成后立即回传完整 `section_document`，前端即时合并到草稿文档
- [x] 编辑器支持引用徽标 / tooltip，老师能看到当前 section 的参考资料
- [x] embedding 默认配置切为 `local_bge + BAAI/bge-m3 + cpu`
- [x] 知识新增与种子脚本会写入 embedding runtime 元数据
- [x] `.env.example` 与 `apps/api/.env.example` 已补齐 RAG / embedding 配置
- [x] 工作台、创建页、编辑器主流程已按 `DESIGN.md` 做一轮 Notion 化收口
- [x] 公域和主流程不再暴露主题切换入口
- [x] 已补 `docs/rag-current.md` 与 `docs/rag-sales.md`

## 本轮待验收

- [ ] 手动走一遍“创建任务 → section 级生成 → 局部重写 → 查看引用 → 导出”
- [ ] 确认工作台 / 创建页 / 编辑器的视觉方向已经符合“完全 Notion”
- [ ] 确认本地 BGE 方案满足当前语文知识增强需求

## 验收标准

- 生成过程中，每一节完成后内容持续可见，不再出现“生成后短暂消失”
- 学案三段式 section 保存与渲染全部落在 `learning_process`
- RAG 在 `RAG_ENABLED=false` 时能优雅降级，在开启时能返回引用元数据
- 前后端测试、类型检查、构建与静态检查通过
- 文档状态一致，不再出现 `GOAL / NEXT / PROGRESS` 各自描述不同步

## 暂不进入下一阶段

未经过你确认前，不自动进入模板库运营化、知识包扩学科或部署阶段。
