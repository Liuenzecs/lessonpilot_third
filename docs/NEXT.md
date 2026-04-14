## 当前状态

- Sprint 0（项目清理与准备）已完成。
- 下一步是 **Sprint 1 — 内容模型 + AI 服务重写**。
- 在你手动确认前，不自动开始 Sprint 1。

## Sprint 0 完成情况

### 后端清理
- [x] 删除不需要的 service 文件：`billing_service.py`、`admin_service.py`、`analytics_service.py`、`append_service.py`
- [x] 删除不需要的 model 文件：`billing_order.py`、`billing_webhook_event.py`、`invoice_request.py`、`user_subscription.py`、`quota_adjustment.py`、`analytics_event.py`、`email_delivery_log.py`
- [x] 删除不需要的 endpoint 文件：`billing.py`、`admin.py`、`analytics.py`
- [x] 删除不需要的 schema 文件：`billing.py`、`admin.py`、`analytics.py`
- [x] 精简 `models/__init__.py`，只导出 User、Task、Document、DocumentSnapshot、AuthToken、Feedback
- [x] 精简 `router.py`，只保留 auth、tasks、documents、health、account
- [x] 精简 `config.py`，移除 billing/admin/sentry 相关字段，添加 MiniMax 配置
- [x] 精简 `pyproject.toml`，移除 weasyprint、sentry-sdk、slowapi 依赖
- [x] 更新 `main.py`，移除 Sentry 和 SlowAPI 中间件
- [x] 删除 `core/rate_limit.py`、`core/sentry.py`、`core/streaming.py`
- [x] 精简 `mail_service.py`，移除 EmailDeliveryLog、billing 邮件
- [x] 修复所有测试（24 passed）

### 前端清理
- [x] 删除不需要的 feature 目录：admin、analytics、onboarding、feedback、billing
- [x] 删除 SSR 相关文件：`entry-server.ts`、`server.mjs`
- [x] 精简 `package.json`，移除 @sentry、@vue/server-renderer、express、compression
- [x] 简化 `build` 脚本，只做 SPA 构建
- [x] 清理 router，移除 admin 路由和 SSR meta
- [x] 移除所有 billing 引用和 useSubscription 残留
- [x] 修复 LandingView.vue 语法错误
- [x] type-check + build 通过

## 下一步：Sprint 1 — 内容模型 + AI 服务重写

详见 `docs/milestones/implementation-plan-v2.md` Sprint 1 部分。
