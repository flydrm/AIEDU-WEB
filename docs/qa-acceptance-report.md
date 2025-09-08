### QA 验收报告（MVP）

日期：${TODAY}
分支：feature/safety-logging

#### 一、环境与版本
- Python: 3.11
- Node: 20.x
- 后端端口: 8000
- 前端端口: 5173（代理 /api 与 /metrics 到 8000）

#### 二、自动化结果
- 后端测试：12/12 通过（`pytest -q`）
- 前端构建：通过（`npm --prefix web run build`）
- E2E：烟雾用例已落地，CI 可通过 PR 标签 `run-e2e` 触发（本地可在 dev server 下执行）

#### 三、功能验收（抽样/全量按手册）
- 首页：通过，标题与底部导航可见
- 聊天（SSE）：通过，发送→助手回复流式输出；停止可中断，断线退避重连生效
- 今日微课：通过，返回当日卡片/故事/家庭/逻辑项并展示
- 家长中心：通过，夜间模式切换；指标可获取并展示
- 内容安全：通过，返回检查与建议

#### 四、契约与观测
- OpenAPI：通过，`/openapi.json` 可用
- 探针：通过，`/health`、`/ready`（breaker 状态）
- 指标：通过，`/metrics` 含 HTTP 指标、`llm_requests_total`、`llm_failover_total`
- 日志：通过，structlog JSON，Trace-Id 贯穿请求起止

#### 五、问题与建议
- 建议增加：
  - 更多 E2E 用例与 a11y 自动化（axe）
  - Grafana 看板与告警基线
  - 前端性能预算（Lighthouse）与 SSE 断线/重连统计上报

#### 六、结论
- 结论：满足 PM 验收标准，建议通过。
- 建议：合并至 master 后进入试运行，后续按建议项纳入迭代计划。