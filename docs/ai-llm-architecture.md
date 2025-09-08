# AI 大模型调用架构方案（OpenAI 兼容｜可定制 base_url/api_key｜容错灾备）

## 1. 目标与约束
- 目标：在无法稳定访问官方 API 的网络条件下，最大保证核心 AI 能力（对话补全/生成）的可用性与体验（低时延、稳定流式、可降级）。
- 约束：
  - 调用协议采用 OpenAI 兼容格式（/v1/chat/completions）。
  - 可配置 base_url 与 api_key（多供应商/自建网关/代理）。
  - 必须提供容错与灾备（重试、熔断、故障转移、降级缓存）。
  - 提供流式（SSE）与非流式两种输出模式。

## 2. 方案总览
- 形态：Clean Architecture 分层
  - presentation（FastAPI 路由）：/api/v1/ai/chat（OpenAPI 对外合同）
  - application（用例）：ChatCompletionUseCase（编排参数/策略）
  - domain（模型/配置）：ProviderConfig、LLMRequest/Response
  - infrastructure（客户端/容错）：OpenAICompatibleClient、FailoverLLMRouter、CircuitBreaker
- 配置：
  - 通过环境变量/配置文件注入多提供方列表（provider_name/base_url/api_key/超时/权重）。
  - 动态主备：按健康度/失败计数与冷却时间自动切换。
- 可观测：
  - 结构化日志 + OTel Trace；指标：成功率/时延P95/失败类型/熔断状态/切换次数。

## 3. OpenAPI 兼容合同（对 FE/QA）
- 请求（POST /api/v1/ai/chat）：
```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "你是中文幼儿启蒙老师。"},
    {"role": "user", "content": "讲一个红色小车的三段故事。"}
  ],
  "stream": true,
  "temperature": 0.6,
  "max_tokens": 512
}
```
- 非流式响应（200）：
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1736382000,
  "model": "gpt-4o-mini",
  "choices": [
    {"index":0, "finish_reason":"stop", "message":{"role":"assistant","content":"..."}}
  ],
  "usage": {"prompt_tokens": 30, "completion_tokens": 120, "total_tokens": 150}
}
```
- 流式响应（SSE）：逐段返回 event:data 行，兼容 OpenAI：
```json
{"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1736382001,"model":"gpt-4o-mini","choices":[{"index":0,"delta":{"content":"第一段..."},"finish_reason":null}]}
```
最后一条：`{"choices":[{"delta":{},"finish_reason":"stop"}]}`，并以 `data: [DONE]` 结束。

## 4. 基于多提供方的容错与灾备
- 重试（Retry）：幂等读取场景采用指数退避（100ms→200ms→400ms），上限 3 次；对 5xx/超时/连接错误重试；对 4xx 不重试（除429可轻度重试）。
- 熔断（Circuit Breaker）：
  - 阈值：60 秒内连续失败 ≥ N（默认3）即打开；冷却窗口（默认 30s）。
  - 半开：窗口结束后放行少量探测请求，成功则关闭；失败则回到打开。
- 故障转移（Failover）：
  - provider 列表按优先级迭代；当前 provider 熔断或超时即切换下一个。
  - 记录健康度并定期回切主用（heal）。
- 降级：
  - 返回简化模板/缓存响应（可选）；向 FE 返回明确降级标志与可读提示。

## 5. 安全与配置
- base_url/api_key 通过环境变量或 Secret 管理（不落盘）。
- 日志脱敏（隐藏密钥、裁剪 prompt）。
- 超时（连接/读取）缺省 10s/30s。
- 可选代理/自建边缘网关（统一鉴权与路由）。

## 6. QA 验证（要点）
- 合同测试：OpenAPI schema + schemathesis（边界值、必填校验）。
- 网络异常：DNS失败/连接超时/读超时/连接被重置 → 观察重试/熔断/切换是否生效。
- 负载：并发 20/50；P95 时延与成功率。
- 流式：中途断线重连、用户取消（abort）、服务端 backpressure。
- 内容：流式/非流式一致性、finish_reason 正确。

## 7. FE 集成建议
- 选用方案A（卡片 + 底部导航），儿童友好且命中率高。
- 流式：EventSource/Fetch+ReadableStream；错误兜底与重连指数退避。
- 非流式：超时与取消（AbortController）。
- 统一错误体（code/message/hint）与“已降级”提示。
- 边界：多段消息合并、Markdown 渲染（安全）。

### 7.1 前端信息架构（方案A）
```
[ 顶部栏  Kids AI ]
------------------------------------------
|  今日推荐                                |
|  ┌────────────┐  ┌────────────┐         |
|  |  知识卡 1  |  |  知识卡 2  |         |
|  | [图片占位] |  | [图片占位] |         |
|  └────────────┘  └────────────┘         |
|  ┌────────────────────────────────────┐  |
|  |  今日故事  (三段，第二段含动作)     |  |
|  |  标题：红色小车去散步               |  |
|  |  [▶ 播放]   [下一条]   [❤ 收藏]     |  |
|  └────────────────────────────────────┘  |
------------------------------------------
[底部导航] 首页 | Chat | 微课 | 家长
```

路由建议：
- `/` 首页（今日推荐，快速入口）
- `/chat` Chat（SSE 流式对话：增量渲染、停止/重试）
- `/lesson` 今日微课（2卡+1故事+1亲情+1逻辑，一键点读/播放）
- `/parent` 家长中心（时长/正确率/亲情打卡，TTS/夜间开关）
- `/safety` 安全检查（文本重写小工具）

组件建议：
- 卡片（标题/图片占位/点读按钮/完成打卡）
- 故事面板（段落流式/操作控件：播放/下一条/收藏）
- SSE 客户端封装（断线退避重连、取消）
- 底部导航（固定，48px 触达区，图标+文案）

可访问性与触控：
- 触达 ≥ 48px，间距 ≥ 16px，焦点可见，文案对比度 AA
- 图片提供替代文本（生成式图片以语义说明）

## 8. 运行与观测
- 关键指标：
  - llm.request.count/success/error/timeout
  - llm.latency.p50/p95/p99
  - llm.provider.breaker.state（labels: provider）
  - llm.failover.count（from→to）
- Trace：为每次调用注入 trace_id/span_id；记录 provider/base_url。

## 9. 目录与关键类（实现建议）
```
app/
├── presentation/
│   ├── api/main.py                # FastAPI app / 中间件（Trace-Id/日志）
│   ├── api/__init__.py            # 挂载 v1 + /metrics + /ready
│   ├── api/error_mapper.py        # 错误映射（4xx/429/5xx/timeout）
│   ├── api/metrics.py             # /metrics（Prom 风格）
│   ├── api/ready.py               # /ready（就绪，breaker 状态）
│   └── api/v1/
│       ├── ai.py                  # /api/v1/ai/chat（SSE/非流）
│       ├── lesson.py              # /api/v1/lesson/today
│       └── safety.py              # /api/v1/safety/inspect
├── application/use_cases/
│   ├── chat_completion.py         # Chat 编排
│   └── lesson_plan.py             # 日常微课规则（2卡+1故+1亲+1逻辑）
├── domain/ai.py                   # LLM 请求/响应模型（对齐OpenAI）
└── infrastructure/ai/
    ├── clients.py                 # OpenAICompatibleClient + FailoverLLMRouter + CircuitBreaker
    ├── errors.py                  # 统一异常
    └── settings.py                # Provider 加载与校验
```

## 10. 演进与扩展
- 增加图像生成/多模态端点。
- 引入令牌预算/配额与成本追踪。
- 持久健康度评估与自愈策略。
- 支持多租户与限流策略。
- 插件化内容安全/重写策略。