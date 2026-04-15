# 当前任务：Cycle 2 — 后端加固

## 目标
为生产部署做准备：添加速率限制、全局异常处理、前端测试基础设施。

## 任务清单

### 2.1 速率限制
- [ ] 新建 `apps/api/app/core/rate_limit.py` — 轻量内存级限流中间件
  - 登录端点：每 IP 每分钟 10 次
  - AI 生成端点：每用户每小时 20 次
  - 通用 API：每分钟 60 次
- [ ] 修改 `apps/api/app/main.py` — 注册限流中间件
- [ ] 修改 `apps/api/app/core/config.py` — 添加限流配置项

### 2.2 全局异常处理
- [ ] 修改 `apps/api/app/main.py` — 添加 `RequestValidationError`、`HTTPException`、通用 `Exception` 异常处理器
- [ ] 修改 `apps/api/app/services/generation_service.py` — parse 失败时 log.warning + 发送 SSE warning 事件
- [ ] 修改 `apps/api/app/services/rewrite_service.py` — 净化错误消息，不暴露内部细节

### 2.3 前端测试基础
- [ ] 新建 `apps/web/vitest.config.ts`
- [ ] 修改 `apps/web/package.json` — 添加 vitest、@vue/test-utils、happy-dom
- [ ] 新建 `apps/web/src/shared/utils/__tests__/content.test.ts`
- [ ] 新建 `apps/web/src/features/editor/composables/__tests__/useEditorView.test.ts`

## 验收标准
- 速率限制中间件可正常拦截高频请求
- 全局异常处理器捕获未处理异常并返回友好消息
- 前端 vitest 测试可通过
- 所有 CI 检查通过（type-check / lint / build / pytest / ruff）

## 后续 Cycle 预览
- **Cycle 3**：UI/UX 润色（去 AI 味 + 术语统一 + 设计令牌迁移）
- **Cycle 4**：数据库模板库 + AI 输出质量验证
