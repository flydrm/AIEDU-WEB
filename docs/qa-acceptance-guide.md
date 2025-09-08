### QA 验收执行手册（MVP）

#### 1. 环境准备
- Python 3.11；Node 20
- 后端启动：
  ```bash
  uvicorn app.presentation.api.main:app --host 0.0.0.0 --port 8000
  ```
- 前端启动（代理到 8000）：
  ```bash
  npm --prefix web install
  npm --prefix web run dev
  # 打包验证（可选）：npm --prefix web run build && npm --prefix web run preview
  ```

#### 2. API 契约与功能验证（必做）
1) OpenAPI 契约：`GET /openapi.json` 能返回 JSON；字段齐全
2) 健康/就绪：`GET /health` == 200；`GET /ready` 返回 breaker 状态数组
3) 指标：`GET /metrics` 包含以下指标：
   - http_requests_total / http_request_duration_seconds
   - llm_requests_total / llm_failover_total
4) Chat 非流：`POST /api/v1/ai/chat`（`stream=false`）返回 `chat.completion` 对象
5) Chat 流：`POST /api/v1/ai/chat`（`stream=true`）SSE 输出，包含 `data: ...` 与 `[DONE]`
6) 今日微课：`GET /api/v1/lesson/today` 返回日期与 items（card/story/family/logic）
7) 内容安全：`POST /api/v1/safety/inspect` 返回审查与可能的 rewrite 建议

建议：使用 curl 或 REST 客户端，附带 `X-Trace-Id`，核对响应头是否回传。

#### 3. 前端关键路径（必做）
- 首页：显示 “Kids AI” 标题、底部导航存在
- 聊天：输入框输入文本，点击发送，出现 “我” 与 “小助手” 两类气泡；可点击“停止”中断
- 微课：页面可见“今日微课”，能够刷新并列出卡片/故事等项
- 家长中心：切换夜间模式，点击“查看服务指标”展示 Prometheus 文本
- 安全：输入文本，点击“检查”显示 JSON 结果

断点检查：375/768/1280 宽度下，底部导航不遮挡内容，交互可达

#### 4. 自动化验证
- 后端测试：
  ```bash
  pytest -q
  ```
- 前端构建：
  ```bash
  npm --prefix web run build
  ```
- E2E 烟雾：
  ```bash
  E2E_BASE_URL=http://localhost:5173 npx playwright test
  ```
  CI 中可在 PR 上添加 `run-e2e` 标签触发。

#### 5. 观测与排障
- 结构化日志：按 `X-Trace-Id` 检索 `request.start/request.end`
- 指标阈值：关注 5xx、429、timeout 的 `llm_requests_total{result}`；`llm_failover_total` 是否突增
- 详见 `docs/troubleshooting.md`

#### 6. 验收结论模板
- 功能项（通过/不通过 + 备注）
- API 契约（通过/不通过 + 备注）
- 观测（日志/指标/探针齐全，是否满足排障）
- 性能/稳定（手动并发/断网小试验结果）
- 阻断问题清单（若有）与建议

