### RD 开发指南

#### 1. 启动
- 后端：`uvicorn app.presentation.api.main:app --host 0.0.0.0 --port 8000`
- 前端：`npm --prefix web install && npm --prefix web run dev`（代理 `/api` `/metrics` → 8000）

#### 2. 目录结构（关键）
- `app/presentation/api`：路由、错误映射、metrics/ready/health、中间件（Trace-Id、CORS、时延）
- `app/application/use_cases`：用例编排（`ChatCompletionUseCase` 注入 RAG 上下文）
- `app/infrastructure/ai`：OpenAI 兼容客户端（重试/熔断/Failover）、Embeddings/Rerank 客户端
- `app/infrastructure/rag`：`SimpleRetriever`、`HybridRetriever`
- `content/kids_3yo_dataset.json`：知识卡/故事数据集

#### 3. 开发规范
- 注释：模块/函数 docstring；中文/英文均可，聚焦“意图与边界”。
- 错误：不要吞异常；到 API 层用 `error_mapper` 统一 HTTP 化。
- 指标：新增模块请补充 Prom 指标（请求计数/耗时/错误），保持可观测。

#### 4. 配置
- Provider：`AI_PROVIDERS`（数组：name/base_url/api_key/timeout）；简化：`AI_BASE_URL/AI_API_KEY`
- 熔断：`AI_BREAKER_FAILURES/AI_BREAKER_COOLDOWN`
- 环境：`APP_ENV=prod` 时 `/metrics` 受限

#### 5. 测试
- 后端：`pytest`；新增功能请补充单测/集成测
- 前端：构建必须通过；E2E 可手动跑或在 PR 打 `run-e2e` 标签

#### 6. RAG 接入
- 默认 TF‑IDF；如配置 embeddings，将自动启用 `HybridRetriever`
- 若需 reranker：实现 `/v1/rerank` 客户端调用并在用例层融合得分

#### 7. 提交流程
- 分支开发 → PR → CI 通过 → 代码评审 → 合并 master → 打标签

