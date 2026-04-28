# 当前任务：等待下一步指示（Phase 15 已验收）

## 本阶段目标

为个人网站备案，临时去除公开网页中的定价、会员、套餐、付费、支付、退款、专业版升级等商业化表述。保留登录、注册和备课主功能；`/pricing` 直接跳回首页，不展示定价页。

## 已授权范围

- 移除公域导航和页脚中的“定价”入口。
- `/pricing` 前端路由重定向到首页。
- 清理帮助中心、服务条款等公开页面中的商业化文案。
- 删除不用的定价页组件和未引用的前端计费类型 / 样式残留。
- 不新增后端 API，不修改数据库，不恢复任何计费或订阅能力。
- 不自动提交 / 推送，等待用户验收。

## 本轮实施切片

- [x] 公域导航和页脚移除“定价”入口。
- [x] `/pricing` 路由跳回首页，删除 `PricingView.vue`。
- [x] 帮助中心改为“账户与数据”口径，清理升级、续费、支付、方案限制等文案。
- [x] 服务条款替换“付费与退款说明”为“服务性质说明”。
- [x] 删除未引用的 subscription / billing / invoice 前端类型和样式残留。
- [x] 补充备案收口前端测试。
- [x] 更新 `docs/ACCEPTANCE.md`、`docs/PROGRESS.md`、`CLAUDE.md` 和阶段文档。

## 已验证

- `pnpm --dir apps/web test --run src/features/public/views/__tests__/FilingCleanup.test.ts`：3 passed。
- `pnpm --dir apps/web type-check`：passed。
- `pnpm --dir apps/web test --run`：49 passed。
- `pnpm --dir apps/web build`：passed。

## 验收结论

- 用户已完成 Phase 15 手动验收并要求提交推送。
- 当前不自动进入下一阶段。

## 停止条件

等待用户明确指定下一阶段或新的 Cycle。
