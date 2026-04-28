# 项目重构与 Phase 规划

- Source: Opus 4.6
- Date: 2026-04-10
- Status: accepted
- Supersedes: (none)
- Question asked: 请评估当前目录结构，给出更好的目录组织方案；重新规划 Phase 路线图

## 1. 目录结构评估

整体结构是合理的

关于 Python 后端：Python 生态没有 npm workspace 的概念，`api/` 保持独立就好，不需要强行纳入 workspace 管理。

关于移动端扩展：用了 `apps/` 结构之后，未来加 `apps/mobile/`（React Native 或 Flutter）非常自然，`packages/shared-types/` 里的 TS 类型可以直接复用。

---

## 2. Phase 规划



### Phase 1 — 核心循环（能用）

目标：一个老师能完整走完"注册 → 创建任务 → AI 生成 → 编辑 → 导出 Word"这条路。

后端：
- Auth：注册、登录、JWT 签发/验证、登出
- Task CRUD 完整实现
- Document CRUD 完整实现
- AI 生成端点（SSE 流式输出）
- Word 导出端点

前端：
- 登录/注册页（功能完整，样式基础即可）
- 任务创建向导（3 步：学科 → 年级 → 主题）
- 备课台列表页（展示任务卡片，支持打开/删除）
- 编辑器基础版（渲染 Content JSON，支持基础文本编辑）
- AI 生成进度 UI（SSE 接收 + 进度展示）
- 自动保存（防抖 + 保存状态指示器）
- Word 导出按钮

这一阶段结束后，产品可以给种子用户试用。

---

### Phase 2 — 编辑器深度完善（好用）

目标：编辑器是产品核心，这一阶段让它真正好用。

- 所有 Block 类型完整渲染（teaching_step、exercise_group、各类题型）
- AI pending/confirm 流程（AI 内容高亮显示，老师逐块接受/拒绝）
- 局部 AI 重写（选中段落 → 右键/浮动菜单 → AI 重写）
- Block 级操作（添加、删除、上下移动）
- PDF 导出
- 键盘快捷键
- 版本历史（基础版：保存最近 10 个快照）
- 编辑器参考 `docs/design/editor-ui.md` 全面落地

---

### Phase 3 — 公域页面 & Auth 完善（有门面）

目标：产品有完整的公开门面，可以对外传播。

- Landing 首页（完整设计，含 Hero、功能展示、用户场景、CTA）
- 定价页（三档方案，月付/年付切换）
- FAQ / 帮助中心页
- 关于我们页
- 隐私政策、服务条款页
- 404 页面
- 公域导航栏 + 全局 Footer
- 忘记密码 / 重置密码流程
- 邮箱验证（异步发送，不阻断注册流程）
- 参考 `docs/design/public-pages-ui.md` 全面落地

---

### Phase 4 — 账户设置 & 计费（能赚钱）

目标：产品可以收费，用户可以管理自己的账户。

- 账户设置页（个人信息、密码安全、订阅方案、数据管理四个 Tab）
- 免费额度限制（每月 5 份教案，后端计数 + 前端提示）
- 订阅方案（免费版/专业版）
- 支付集成（微信支付 + 支付宝，推荐用 Ping++ 或直接对接）
- 用量追踪（后端记录，前端展示进度条）
- 超额升级引导弹窗
- 发票申请流程（简单版：填信息发邮件给你处理）

---

### Phase 5 — UX 打磨（精致）

目标：产品从"能用"变成"好用"，细节到位。

- 新用户引导（首次登录空状态 + 引导步骤）
- 所有页面的空状态设计
- 全局 Loading 骨架屏
- Toast 通知系统（操作成功/失败反馈）
- 错误页面（404、500、网络错误）
- 右下角反馈悬浮按钮
- 响应式审查（公域页面完全响应式，编辑器平板可用）
- 页面切换动画、按钮交互反馈等微动效
- 导出 Word 的排版质量优化

---

### Phase 6 — 运营基础设施（可运营）

目标：产品可以独立运营，不需要你手动处理每件事。

- 事务性邮件（欢迎邮件、密码重置、用量预警）
- 公域页面 SEO（meta tags、OG tags、sitemap、robots.txt）
- 基础数据分析（页面 PV、注册转化、付费转化漏斗）
- 错误监控（Sentry 接入前后端）
- 简易管理后台（用户列表、用量统计、手动调整配额）
- 性能优化（路由懒加载、图片优化、API 响应缓存）

---

### Phase 7 — 高级功能（按需迭代）

这一阶段根据用户反馈决定优先级，不强制全做：

- 教案模板库（官方模板 + 用户收藏）
- 复制为新教案
- 全文搜索和筛选
- 更多 AI 功能（生成练习题、建议教学活动）
- 批量导出
- 移动端适配（如果数据显示有需求）

---

## 3. 设计文档的位置和实现时机

放在这里：

```
docs/
└── design/
    ├── editor-ui.md        ← 编辑器 UI 设计
    └── public-pages-ui.md  ← 公域页面 UI 设计
```

实现时机：
- `editor-ui.md` → Phase 1 参考基础布局，Phase 2 全面落地
- `public-pages-ui.md` → Phase 3 全面落地

`docs/` 放在项目根目录，和 `apps/`、`packages/` 平级。这样不管是你自己查阅还是给 AI 提供上下文，路径都很清晰。

## Claude Action Items

- [x] 重命名本建议文件为 YYYY-MM-DD-topic-slug.md 格式
- [x] 重构目录：web/ → apps/web/，api/ → apps/api/
- [x] 创建 packages/shared-types/，将 content.ts 移入
- [x] 创建 docs/design/ 目录
- [x] 创建 scripts/ 目录
- [x] 创建 pnpm-workspace.yaml
- [x] 更新 docker-compose.yml 路径
- [x] 更新 CI 配置路径
- [x] 更新 GOAL.md 为新 Phase 规划
- [x] 更新 NEXT.md 为 Phase 1 任务
- [x] 更新 PROGRESS.md 记录变更
- [x] 更新 CLAUDE.md 项目结构描述和规则
- [x] 更新 context.md 反映新目录结构
