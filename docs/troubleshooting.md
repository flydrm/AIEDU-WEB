### 排障手册（运行与监控）

本手册帮助你在服务异常时快速定位根因并恢复服务。涉及指标、日志、探针与常见问题处理步骤。

#### 1. 观测面板
- 指标端点：`GET /metrics`（Prometheus 暴露格式）
  - http_requests_total{path,method,status}
  - http_request_duration_seconds{path,method,status}
  - llm_requests_total{provider,result}
  - llm_failover_total{from,to}
- 就绪探针：`GET /ready`（含各 provider 的 circuit breaker 状态）
- 健康探针：`GET /health`

#### 2. 日志（结构化 JSON）
- 入口：每个请求在处理中打印一条结构化日志，包含 path/method/trace_id
- 追踪：服务在响应头 `X-Trace-Id` 返回 trace_id，可用于串联前后端日志
- 建议：在部署环境将 stdout 收集到 ELK/Datadog 等日志系统

#### 3. 常见故障排查流程
1) 大面积 5xx（502/504）：
   - 查看 `/metrics` 的 `llm_requests_total{result}` 是否 spike 在 `timeout/5xx`
   - 查看 `llm_failover_total` 是否增长，判断是否为上游提供商故障
   - `/ready` 检查 breaker 是否全部 open；如是，考虑临时切换优先级或替换 base_url
2) 429 过载：
   - 查看 `http_requests_total` 是否突增，与来源 IP 或 UA 关联
   - 调整限流/退避参数；必要时在网关或 WAF 层限流
3) SSE 断流/卡顿：
   - 前端确认是否自动重连；查看 `http_request_duration_seconds` 是否显著上升
   - 后端检查上游 streaming 是否输出 DONE
4) 网络抖动导致超时：
   - 检查 `timeout` 配置与网络连通性；必要时提高超时或增加 provider 备份
5) 单一 provider 频繁失败：
   - 通过 `llm_requests_total{provider}` 与 `llm_failover_total` 定位问题 provider
   - 临时下线（配置级）或后移优先级；联系上游排查

#### 4. 配置项（环境变量建议）
- AI_BREAKER_FAILURES（默认 3）：熔断失败阈值
- AI_BREAKER_COOLDOWN（默认 30s）：熔断冷却时间
- AI_PROVIDERS：JSON 列表，包含 base_url/api_key/timeout
- CORS_ORIGINS：前端域名，生产环境请收紧

#### 5. 故障演练建议
- 定期注入 429/5xx/timeout 故障，验证重试/熔断/故障转移是否按预期
- 对关键 API 设置告警阈值（例如 p95/p99 时延、错误率、failover 次数）

#### 6. FAQ
- Q: 如何快速定位某个用户的请求？
  - A: 让前端传入 `X-Trace-Id`，后端会原样回传。用该值在日志系统全文检索。
- Q: 如何判断是否需要扩容？
  - A: 观察 `http_request_duration_seconds` 分位数是否升高、错误率是否升高、CPU/内存消耗是否接近阈值。
- Q: 如何新增一个 LLM 提供商？
  - A: 在 `AI_PROVIDERS` 追加新条目（base_url/api_key/timeout），无需改代码。

