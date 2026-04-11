## 等待用户验收

1. [ ] 默认验收可直接使用 `LLM_PROVIDER=fake`，不需要 DeepSeek 密钥；若需要真实 AI 生成，再填写 `apps/api/.env` 或根目录 `.env`：
   - `LLM_PROVIDER=deepseek`
   - `DEEPSEEK_API_KEY=...`
   - `DEEPSEEK_MODEL=deepseek-chat`
   - `DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`
2. [ ] 手动验收完整主链路：
   - 注册 / 登录
   - 创建任务
   - 自动进入编辑器并触发生成
   - 接受 / 拒绝 pending 内容
   - 编辑并自动保存
   - 导出 `.docx`
3. [ ] 在非受限本机终端复验 `pnpm --dir apps/web build`
4. [ ] 用户验收通过后，再提交并推送到远程仓库
5. [ ] 未得到新指示前，不自动进入 Phase 2
