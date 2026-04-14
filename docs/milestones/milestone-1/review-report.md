# LessonPilot 项目审查报告（已核实版本）

## 说明

本文件基于用户提供的审查报告，对当前仓库做了一次核实整理。

- 目的不是原样照抄外部报告，而是把每一项问题标成：
  - `已验证，需修复`
  - `已部分覆盖，仍需收口`
  - `结论需修正`
  - `仓库外人工动作`
- 本文件是 **Milestone 1 / Phase 7** 的输入之一，最终实现以代码事实和当前 `GOAL.md / NEXT.md` 为准。

## 一、Phase 1-6 完成度

- 结论：**Phase 1-6 已完成并有用户手动验收记录**。
- 备注：
  - Phase 2 曾被用户退回并严格返工，最终重新验收通过。
  - 当前 Milestone 1 新增的 Phase 7 不是否定前 1-6，而是在已完成基础上做加固。

## 二、安全问题

### C1. DeepSeek API Key 泄露

- 状态：`结论需修正` + `仓库外人工动作`
- 核实结果：
  - `.env` 与 `apps/api/.env` 被 `.gitignore` 忽略，不属于“仓库中已追踪泄露”。
  - 但本地环境文件中出现真实密钥仍然是风险点。
- Phase 7 处理口径：
  - 代码与文档补齐密钥治理规则。
  - 真实 key 轮换由人工在仓库外完成，不在代码中伪装为“已轮换”。

### C2. Stored XSS — `v-html` 渲染 AI 内容

- 状态：`已验证，需修复`
- 核实结果：
  - `apps/web/src/features/editor/components/BlockPreview.vue` 存在多处 `v-html`。
  - 当前没有统一 HTML 净化层。

### C3. 无速率限制

- 状态：`已验证，需修复`
- 核实结果：
  - 当前后端没有 `slowapi` 或等价限流实现。
  - 登录、注册、分析事件、Webhook、AI 入口均无显式限流。

### C4. Billing Webhook 无签名验证

- 状态：`已验证，需修复`
- 核实结果：
  - `POST /api/v1/billing/webhooks/gateway` 当前未按请求头做 HMAC 验签。
  - 现有 `payload.signature` 只是业务字段，不是网关请求级签名校验。

### C5. JWT Secret 使用默认值

- 状态：`已验证，需修复`
- 核实结果：
  - 当前 `apps/api/app/core/config.py` 的 `jwt_secret` 仍有开发默认值。
  - 缺少 `production` 环境下的启动阻断。

## 三、鲁棒性问题

### R1. 全局错误边界缺失

- 状态：`已验证，需修复`
- 核实结果：
  - 当前 `entry-client.ts` 没有接入 `app.config.errorHandler`。
  - 只有 Sentry 初始化，没有根级 fallback UI。

### R2. 编辑器自动保存失败静默丢失

- 状态：`已部分覆盖，仍需收口`
- 核实结果：
  - 目前已有保存状态与冲突处理。
  - 但“未同步 / 正在重试 / 已恢复”这类网络失败恢复反馈还不完整。

### R3. SSR 中的 Pinia 隔离

- 状态：`结论需修正`
- 核实结果：
  - `apps/web/src/entry-server.ts` 每次请求都会重新 `createLessonPilotApp({ ssr: true })`。
  - 当前实现已基本满足“每请求独立 app / pinia”要求。
- Phase 7 处理口径：
  - 增加注释与回归验证，防止未来退化。
  - 不额外添加无意义的全局 `pinia.state.value = {}`。

### R4. 数据库连接池配置

- 状态：`已验证，需修复`
- 核实结果：
  - 当前 engine 创建未暴露明确池配置，也没有 `pool_pre_ping`。

### R5. SSE 连接断开处理

- 状态：`已验证，需修复`
- 核实结果：
  - 生成、rewrite、append 链路目前没有 `Request.is_disconnected()` 检查。

### R6. 后端测试覆盖率

- 状态：`已部分覆盖，仍需收口`
- 核实结果：
  - 当前功能回归测试较多，但尚未引入 `pytest-cov`。
  - 需要把安全与运维关键模块覆盖率补到更高水位。

## 四、UI 与设计系统问题

### U1. Landing 出现内部文案“收尾 CTA”

- 状态：`已验证，需修复`

### U2. 设计 Token 体系不完整

- 状态：`已部分覆盖，仍需收口`
- 核实结果：
  - `main.css` 已有颜色、阴影、动效 token。
  - 但 spacing / typography / radius / z-index 体系仍不完整。

### U3. UpgradeModal 与主站视觉脱节

- 状态：`已验证，需修复`
- 核实结果：
  - `UpgradeModal.vue` 仍依赖独立的 `billing.css`。

### U4. Emoji 作为公域关键图标

- 状态：`已验证，需修复`
- 核实结果：
  - Landing 痛点卡片与用户场景卡片仍使用 emoji。

### U5. 缺少系统化 `focus-visible`

- 状态：`已部分覆盖，仍需收口`
- 核实结果：
  - 个别卡片已有 `:focus-visible`。
  - 但缺少全局统一规则，表单、菜单、按钮并未系统覆盖。

### U6. 登录 / 注册页品牌感不足

- 状态：`已验证，需修复`

### U7. 暗色模式缺失

- 状态：`已验证，需修复`

## 五、Phase 7 采用口径

Milestone 1 / Phase 7 将把以上项目全部纳入，但采用以下收口方式：

- 以当前仓库事实为准，不把不成立的判断继续当成 bug 叙述。
- 对于需要仓库外处理的项目，只补规则、约束和启动防护，不伪造外部动作已完成。
- 对于已部分覆盖的问题，不推倒重来，而是在现有实现上做系统化补齐。
