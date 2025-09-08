# TDD 评审方案（QA/RD/PM 联合）

## 目的
以测试驱动（TDD）统一需求理解与验收标准，确保 MVP 关键能力可度量、可回归、可发布。

## 参与角色与职责
- 架构师：测试范围把关、非功能指标与容错策略校验
- QA：用例设计与边界/异常注入、契约与E2E
- RD：单元/集成测试实现、可测性与桩/替身
- PM：需求验收标准确认、用户价值与可用性口径

## 评审流程（60分钟）
1) 回顾需求与验收（5min）
2) OpenAPI 合同校对（10min）：字段/类型/必填/错误体
3) 测试金字塔与覆盖清单（10min）
4) 核心用例走查与边界（25min）
5) 行动项与达成共识（10min）

## 测试金字塔（目标占比）
- 单元 70%：用例/仓库/工具
- 集成 20%：API + DB/外部替身
- E2E 10%：跨断点、流式/非流式、a11y

## 核心模块与用例（S1–S2）

### 1. OpenAI兼容客户端（非流式优先）
- 正常返回
  - 输入：model+messages（2-3条），temperature≤1，max_tokens≤1024
  - 期望：200；choices[0].message.content 非空；usage 字段存在
- 429 轻重试
  - 模拟：首次429、二次成功
  - 期望：总时长<2s；成功返回；重试次数=1
- 5xx 重试
  - 模拟：前2次 5xx，第三次 200
  - 期望：指数退避被调用；最终成功
- 超时
  - 模拟：连接/读超时
  - 期望：抛出超时错误；错误体 code=TIMEOUT、hint 含重试
- 4xx 非重试
  - 模拟：400/401/403
  - 期望：直接失败；错误体 code=BAD_REQUEST/UNAUTHORIZED/FORBIDDEN

### 2. 熔断与Failover
- 熔断开启
  - 条件：60s 内连续失败≥3
  - 期望：breaker=OPEN；冷却期内直接拒绝并走下一个 provider
- 半开与恢复
  - 条件：冷却后首个探测成功
  - 期望：breaker=CLOSED；恢复主用
- 故障转移
  - 模拟：主 provider 连续超时
  - 期望：切换到备；记录 failover_count+1

### 3. /api/v1/ai/chat（非流式）
- 合同校验
  - 缺少 model/messages → 400
  - 模型名超长/非法 → 422
- 成功
  - 期望：200；object=chat.completion；choices[0].message.content 存在
- 错误体规范
  - 429/5xx：带 code/message/hint；X-Trace-Id 响应头

### 4. /api/v1/ai/chat（流式）
- SSE 起止
  - 期望：首包含 id/object/model/choices[0].delta；尾包 finish_reason=stop；最后 data:[DONE]
- 取消与backpressure
  - 模拟：中途取消
  - 期望：服务端停止下游请求；无资源泄漏

### 5. 个性化（S3）
- 推荐器（规则+近因记忆）
  - 输入：兴趣=红/拼搭/音乐；最近正确率/停留
  - 期望：推荐“2卡+1故事+1亲情+1逻辑”并随表现调整

### 6. 家长教练（S3）
- 引导语生成
  - 期望：1-2句中文正向引导；含“感谢/拥抱/小帮手/复述法”之一

## 非功能测试
- 性能：
  - 非流式：P95<3s；并发20/50成功率≥99%
  - 流式：首字延迟<800ms；中断恢复<3s
- 观测：日志脱敏；指标包含 success/error/timeout/breaker 状态/切换次数；Trace 贯穿
- 安全：密钥不落盘；错误不泄漏敏感信息；内容重写可触发

## E2E/a11y（S2–S4）
- Playwright：跨断点（375/768/1280）关键路径通过
- a11y：axe 扫描关键页面 0 严重问题

## 定义完成（DoD）
- 全部上述用例具备测试实现，CI 通过；覆盖率≥80%
- 评审意见已落实（PR/Issue 关联）

## 附录：测试清单（片段）
```yaml
unit:
  - test_openai_client_success
  - test_openai_client_retry_429
  - test_openai_client_retry_5xx
  - test_openai_client_timeout
  - test_circuit_breaker_open_halfclose
integration:
  - test_chat_api_non_stream_contract
  - test_chat_api_error_body
  - test_failover_switch
e2e:
  - test_stream_sse_flow_and_cancel
  - test_responsive_core_paths
  - test_a11y_homepage
```