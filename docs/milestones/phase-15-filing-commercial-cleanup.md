# Phase 15：备案临时商业化收口

## Summary

本阶段服务个人网站备案：临时从公开网页移除定价、会员、套餐、付费、支付、退款、专业版升级等商业化表述。保留登录、注册和备课主功能，不恢复计费后端能力。

## Key Decisions

- `/pricing` 不展示页面，直接重定向首页。
- 公域导航和页脚不出现“定价”入口。
- 帮助中心和服务条款改为账户、数据、服务性质和内容免责声明口径。
- 本阶段是备案临时上线口径，不代表长期商业化路线被删除。

## Acceptance Criteria

- 首页、帮助中心、服务条款、隐私政策、登录页、注册页无商业化入口和相关表述。
- `/pricing` 自动回到首页。
- 登录、注册、备课台、创建备课、编辑器和 Word 导出入口不退化。
- 不新增后端 API，不修改数据库，不恢复任何计费或订阅能力。

## Validation

- `pnpm --dir apps/web test --run src/features/public/views/__tests__/FilingCleanup.test.ts`：passed
- `pnpm --dir apps/web type-check`：passed
- `pnpm --dir apps/web test --run`：49 passed
- `pnpm --dir apps/web build`：passed
