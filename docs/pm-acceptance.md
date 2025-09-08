### PM 验收文档（MVP）

#### 1. 范围
- 聊天（SSE/非流）
- 今日微课
- 内容安全
- 家长中心
- 运维与观测（/health /ready /metrics；结构化日志）

#### 2. 验收清单
- 功能：
  - 聊天：连贯、适龄、围绕“勇敢/逻辑/爱家人”；可中途停止；断线自恢复
  - 微课：2 卡 + 1 故事 + 1 家庭 + 1 逻辑；可刷新
  - 安全：输出风格温柔；不含惊吓与不当表达
  - 家长：夜间模式；指标可见
- 观测：
  - /ready：熔断状态正常
  - /metrics：HTTP/LLM/failover（若启 embeddings，则含 embeddings/rerank）
  - 日志：含 `X-Trace-Id`，问题可快速串联
- 质量：
  - 单测/集成测通过；前端构建通过；E2E 烟雾完成

#### 3. 通过标准
- 清单全部通过；无 P0/P1；如有轻微问题，纳入下一迭代不阻断上线。

#### 4. 附件
- PRD：`docs/prd.md`
- 架构：`docs/architecture.md`
- QA 测试计划：`docs/qa-test-plan.md`
- RD 开发指南：`docs/rd-dev-guide.md`
- QA 验收报告：`docs/qa-acceptance-report.md`

