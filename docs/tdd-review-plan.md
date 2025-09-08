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
2) OpenAPI 合同校对（10min）：字段/类型/必填/错误体（含 SSE 错误帧）
3) 前端方案A（卡片+底栏）快速走查（10min）：路由/组件/触达区/可达性
4) 测试金字塔与覆盖清单（10min）：FE/E2E 加入关键路径
5) 核心用例走查与边界（20min）：Chat 流式/微课/安全/家长面板
6) 行动项与达成共识（5min）

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

## 前端集成与E2E（UI 方案A）

### 路由与页面
- `/` 首页：今日推荐（两张知识卡 + 今日故事），快速入口（Chat/微课/安全）
- `/chat` Chat：SSE 流式对话区（逐段追加），输入框，发送/停止/重试
- `/lesson` 今日微课：2卡+1故事+1亲情+1逻辑；点读/播放/下一条
- `/parent` 家长中心：TTS/夜间开关、指标摘要（时长/正确率/亲情打卡）
- `/safety` 安全检查：文本输入→检测重写

### E2E 关键路径（Playwright）
- 首页加载
  - 断言：顶部栏/今日推荐卡片可见；底部导航固定显示；触达区≥48px
- 今日微课
  - 断言：返回 2卡+1故事+1亲情+1逻辑；点击“点读/播放/下一条”触发 UI 更新
- Chat（流式）
  - 发送后 2s 内出现首段；中途“停止”立即停止追加；“重试”重新开始
  - 断线重连（模拟 500ms 断网）：最多 2 次退避重连；最终 [DONE] 收尾
- 安全检查
  - 输入“拿刀打人”→ 输出包含“安全工具/不友善的行为”，changed=True
- 家长中心
  - 开关项可点击；导航往返状态保留

### 可访问性与响应式
- a11y：axe 严重问题=0；可见焦点；图片有替代文本；颜色对比度 AA
- 断点：375/768/1280
  - 底部导航在移动端固定可见；内容不重叠；Chat 流式区滚动正常

### 性能预算（关键页面）
- 首页/微课：LCP < 2.5s（3G 目标 < 3.5s）；交互延迟 < 100ms
- Chat（首字时延）：< 800ms（网络正常）；TTS 首播 < 1.5s（启用时）

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
 - 前端：LCP/交互延迟达标；SSE 重连退避策略生效；按键触达≥48px

## E2E/a11y（S2–S4）
- Playwright：跨断点（375/768/1280）关键路径通过
- a11y：axe 扫描关键页面 0 严重问题

## 定义完成（DoD）
- 全部上述用例具备测试实现，CI 通过；覆盖率≥80%
- 评审意见已落实（PR/Issue 关联）
 - 前端方案A落地：五大页面可用（/、/chat、/lesson、/parent、/safety），E2E 关键路径通过
 - 性能与可达性达标（LCP/交互延迟；a11y 严重问题=0；触达≥48px）

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
  - test_homepage_cards_and_bottom_nav
  - test_lesson_today_flow_buttons
  - test_chat_stream_sse_flow_done_and_cancel
  - test_safety_rewrite_interaction
  - test_parent_toggles_persist
  - test_responsive_core_paths_375_768_1280
  - test_a11y_key_pages_no_critical
```