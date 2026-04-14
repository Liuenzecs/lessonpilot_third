# Milestone 1 / Phase 7 — 审查与加固

## 目标

以审查报告为输入，对 LessonPilot 当前代码库做一轮系统性加固，覆盖：

- 文档与里程碑治理
- 安全
- 鲁棒性
- UI 与设计系统

## 实现清单

### 1. 文档与治理

- [ ] 新建 `docs/milestones/milestone-1/` 归档目录并补齐说明文档
- [ ] `docs/GOAL.md` 改为 Milestone 1 / Milestone 2 结构
- [ ] `docs/NEXT.md` 切换到 Milestone 1 / Phase 7
- [ ] `docs/PROGRESS.md` 记录 Milestone 1 重组开始
- [ ] `AGENTS.md` 写明 milestone 规则、当前活跃阶段与 Milestone 2 禁止自动进入

### 2. 安全

- [ ] 修正文档中关于 `.env` 的结论，明确：
  - 本地 `.env` 与 `apps/api/.env` 被忽略
  - 真实密钥不允许进入仓库、截图、示例文档
  - DeepSeek key 轮换属于仓库外人工操作
- [ ] 引入 `dompurify`，所有富文本 HTML 渲染统一净化
- [ ] 引入 `slowapi` 进程内限流
- [ ] 为计费 Webhook 增加 HMAC-SHA256 请求头验签
- [ ] 新增 `APP_ENV`，生产环境禁止默认或弱 `JWT_SECRET`

### 3. 鲁棒性

- [ ] 根级错误边界 + `app.config.errorHandler`
- [ ] 自动保存失败可见化与恢复反馈
- [ ] 记录 SSR Pinia 已按请求隔离，不新增无意义全局 reset
- [ ] 数据库连接池配置 + `pool_pre_ping`
- [ ] SSE 断连处理
- [ ] 引入 `pytest-cov` 与关键测试补强

### 4. UI 与设计系统

- [ ] 移除 Landing 内部口径文案
- [ ] 补齐设计 Token 体系
- [ ] 统一 UpgradeModal 与主站风格
- [ ] 用 `lucide-vue-next` 替换公域关键 emoji
- [ ] 全局 `:focus-visible`
- [ ] 登录/注册页品牌感升级
- [ ] 暗色模式与主题持久化

## 关键接口 / 配置变化

- 新配置：
  - `APP_ENV`
  - `DB_POOL_SIZE`
  - `DB_MAX_OVERFLOW`
  - `DB_POOL_TIMEOUT`
  - `DB_POOL_RECYCLE`
- 新行为：
  - 关键接口可能返回 `429`
  - `POST /api/v1/billing/webhooks/gateway` 在 `gateway` 模式下要求 `X-LessonPilot-Signature`
  - 前端新增 `lessonpilot-theme` 本地偏好

## 验收标准

### 安全

- [ ] `v-html` 注入脚本、事件处理器、`javascript:` 链接后不会原样执行
- [ ] 登录 / 注册 / 分析 / Webhook / AI 关键入口命中限流时返回 `429`
- [ ] Webhook 缺签名或签名错误返回 `403`
- [ ] `APP_ENV=production` + 默认 `JWT_SECRET` 时应用启动失败
- [ ] `git status` 和已追踪文件中不出现真实 `.env`

### 鲁棒性

- [ ] 前端运行时异常会进入统一 fallback，而不是白屏
- [ ] 自动保存失败时老师能看到“未同步 / 正在重试 / 已恢复”
- [ ] SSE 客户端断开后，后端会及时停止后续生成
- [ ] 数据库池配置生效，现有接口不回归

### UI

- [ ] Landing 不再显示“收尾 CTA”
- [ ] 公域关键卡片不再使用 emoji 作为主图标
- [ ] UpgradeModal 与主站卡片 / 按钮体系一致
- [ ] 键盘 Tab 遍历时，焦点可见
- [ ] 登录 / 注册页品牌感增强且移动端不回归
- [ ] 亮色 / 暗色主题在公域、认证页、备课台、编辑器、管理后台都可用

### 回归

- [ ] `pnpm --dir apps/web type-check`
- [ ] `pnpm --dir apps/web lint`
- [ ] `pnpm --dir apps/web build`
- [ ] `apps/api/.venv/Scripts/python.exe -m ruff check apps/api/app apps/api/alembic/versions apps/api/tests`
- [ ] `apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests --cov`
