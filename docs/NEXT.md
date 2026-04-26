# 当前任务：Phase 5 知识可信闭环（待验收）

## 本阶段目标

把现有“工程版 RAG”推进成老师可感知的“知识可信层”：

- 扩充语文重点篇目知识包
- 生成前能判断是否命中知识库
- 生成中能展示命中 / 未命中 / 降级状态
- 生成后继续通过 `section_references` 留下引用证据

## 已实现

- [x] 将知识种子迁移为可维护的知识包 manifest
- [x] 首批覆盖 `红楼梦`、`春`、`背影`、`桃花源记`、`岳阳楼记`、`天净沙·秋思`
- [x] 路由规则改为从知识包配置读取
- [x] 种子脚本写入 `pack_id / pack_version / trigger_terms / embedding_runtime`
- [x] 新增 `POST /api/v1/knowledge/diagnose` 知识命中诊断 API
- [x] 生成 SSE 新增 `rag_status` 事件
- [x] 前端编辑器展示知识增强状态
- [x] 修复 Pydantic section 值中 citation 未被清洗为 `section_references` 的问题
- [x] 更新 RAG 规格、SSE 规格、当前能力说明与验收脚本
- [x] DeepSeek 默认配置切到 `deepseek-v4-flash`，并显式关闭 thinking

## 本轮待验收

- [x] 启动本地 PostgreSQL 后执行 `cd apps/api && .\.venv\Scripts\python.exe -m scripts.seed_knowledge`
- [x] 手动验证重复执行知识入库不会制造重复 chunk
- [x] 验证 `红楼梦薛宝钗人物分析`、`春 朱自清 第一课时`、`桃花源记文言文教学` 能命中知识包并召回 chunk
- [ ] 创建对应语文任务并生成，确认编辑器显示知识增强状态
- [ ] 命中 RAG 时确认 `section_references` 非空，且 section 顶部参考资料 tooltip 正常
- [ ] 诊断一个未覆盖课题，确认显示普通生成提示
- [ ] 用 DeepSeek 真实链路生成一次，确认 `deepseek-v4-flash + thinking disabled` 可返回结构化 section JSON

## 验收标准

- 首批重点篇目知识包能一键入库，重复执行不会制造重复 chunk
- 老师创建或生成语文重点篇目时，能看见“知识库命中 / 未命中”的明确状态
- 至少 3 个代表性课题检索返回相关 chunk
- 至少 2 个生成文档产生非空 `section_references`
- 未命中知识库、关闭 RAG、embedding 失败时均优雅退化，不向老师暴露内部异常
- 前后端测试、类型检查、构建与静态检查通过

## 暂不进入下一阶段

本阶段不自动提交 / 推送，不自动进入迁移能力、导出质量或上课包阶段；等待用户验收后再按项目 commit 格式执行。
