### QA 测试计划（MVP）

#### 1. 目标与范围
- 覆盖后端契约、容错与观测、前端关键路径、基础 a11y 与响应式。

#### 2. 环境
- 后端：8000；前端：5173；`APP_ENV` 默认为 dev。
- 可选：配置 `AI_PROVIDERS` 以启用 embeddings。

#### 3. 用例清单（核心）
- 契约
  - `/openapi.json` 可用
  - `/health` 200；`/ready` 返回 breaker 状态
  - `/metrics` 包含 HTTP/LLM/failover（dev 环境放行）；若启用 embeddings，增加 embeddings/rerank 指标
- AI 聊天
  - 非流式：返回 `chat.completion`
  - 流式：SSE 输出 `data: ...` 与 `data: [DONE]`；停止按钮可中断
  - 退避重连：断网后恢复（可手动模拟）
- 今日微课
  - 列表包含“卡片/故事/家庭/逻辑”项；刷新生效
- 家长中心
  - 夜间模式切换；查看指标文本
- 安全
  - 基本文案复写（温柔/避免惊吓词）
- RAG
  - 提问“红色/勇敢”等关键词时，回答包含与数据集匹配的知识点片段

#### 4. 响应式与 a11y
- 断点：375/768/1280 下底部导航不遮挡内容
- a11y：输入框/按钮/链接具名（通过 getByRole / getByLabel）；可键盘操作

#### 5. 自动化
- 单测/集成测：`pytest -q`（含 UUID Trace-Id 与 /metrics）
- 前端构建：`npm --prefix web run build`
- E2E（烟雾）：`E2E_BASE_URL=http://localhost:5173 npx playwright test`

#### 6. 通过准则
- 功能路径通过；指标可观测；日志有 Trace-Id；无 P0/P1 线上阻断问题。

