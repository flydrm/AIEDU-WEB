### 架构设计（MVP + 增量）

#### 1. 总览
- 前端：Vite + React + TS；路由 `/` `/chat` `/lesson` `/parent` `/safety`；SSE 客户端（退避+抖动+停止）。
- 后端：FastAPI；中间件（CORS、Trace-Id、时延采集）；/health /ready /metrics；AI 路由 `/api/v1/ai/chat`；个性化 `/api/v1/lesson/today`；安全 `/api/v1/safety/inspect`。
- AI 模块：OpenAI 兼容客户端（重试/熔断/故障转移）；SSE/非流式；Hybrid RAG（TF‑IDF + Embeddings 可选）。
- 观测：Prometheus 指标（HTTP/LLM/embeddings/rerank/failover）、结构化日志（structlog）、/ready 熔断状态。

#### 2. 模块分层
- presentation：API 路由、错误映射、观测与中间件。
- application：用例编排（`ChatCompletionUseCase` 等）。
- domain：请求/响应模型、配置模型。
- infrastructure：AI 客户端、RAG 检索器、设置加载。

#### 3. AI 容错
- Retry：429/5xx/Timeout（指数退避）。
- Circuit Breaker：失败阈值/冷却/半开试探（简化）。
- Failover：按 provider 列表优先级切换；记录 `llm_failover_total{from,to}`。
- Streaming：SSE 直通；后端/前端均支持停止与重连。

#### 4. RAG
- SimpleRetriever：TF‑IDF（CJK 单字 + ASCII 单词分词）。
- HybridRetriever：可选 `EmbeddingsClient`（`/v1/embeddings`），混合打分与回退。
- RerankerClient：预留 `/v1/rerank` 接口，后续接 BGE Reranker 或 LLM 重排。
- Chat 注入：在用例层，将检索结果整理为 system 提示，控制长度与安全风格。

#### 5. 配置
- `AI_PROVIDERS`：数组，包含 `name/base_url/api_key/timeout`；兼容单 provider 的 `AI_BASE_URL/AI_API_KEY`。
- 熔断参数：`AI_BREAKER_FAILURES/AI_BREAKER_COOLDOWN`。
- 环境：`APP_ENV=prod` 时限制 `/metrics` 暴露范围。

#### 6. 指标
- HTTP：`http_requests_total{path,method,status}`，`http_request_duration_seconds{...}`。
- LLM：`llm_requests_total{provider,result}`，`llm_failover_total{from,to}`。
- Embeddings/Rerank：`embeddings_requests_total{provider,result}`，`rerank_requests_total{provider,result}`。

#### 7. 安全
- 内容：安全复写；家长端可查看“解释/推理”。
- 接口：CORS 白名单、/metrics 受限；Trace-Id（UUID）贯穿；日志脱敏。

#### 8. 数据与个性化
- 数据：`kids_3yo_dataset.json`；后续可扩展为 SQLite/向量库（pgvector/FAISS）。
- 个性化：标签与难度字段；后续扩展“掌握度模型 + 调度服务”。

#### 9. 演进路线
- SLO 看板与告警；家长看板卡片化。
- 掌握度建模与间隔重复；轻量 Rerank 上线。
- 多模态（识图讲述/儿化 TTS）。

