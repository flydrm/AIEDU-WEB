# Web 项目执行清单（SOP 精炼版）

## 0. 总则（必须）
- [ ] 类/复杂方法/交互/业务规则/配置，均有 Docstring + 中文注释
- [ ] API 契约（OpenAPI）先于联调，变更即更新
- [ ] 质量左移：本地通过 lint/type/test/security 后再提 PR

## 1. 需求
- [ ] 用户故事“三段式”+ 验收标准
- [ ] MoSCoW 优先级与范围边界
- [ ] 风险与降级方案记录

## 2. 架构/设计
- [ ] Clean Architecture 分层：presentation/application/domain/infrastructure
- [ ] 依赖注入与接口抽象（仓库/客户端）
- [ ] 12-Factor 配置外置；日志/指标/追踪纳入设计
- [ ] ADR 编号与决策留档

## 3. 开发
- [ ] 环境：Python 3.11；uv/poetry/pip 锁定依赖
- [ ] 规范：ruff、black、isort、mypy 严格通过
- [ ] 命名/文件结构与约定一致
- [ ] 异步端点避免阻塞 IO；httpx AsyncClient 规范

## 4. 测试
- [ ] 单元(≥70%)：用例/仓库/Schema/Utils
- [ ] 集成(≈20%)：API、DB、外部依赖（测试容器/替身）
- [ ] E2E(≈10%)：关键路径、跨断点(375/768/1280)、a11y 基检
- [ ] 覆盖率 ≥ 80%，报告入库

## 5. 代码审查
- [ ] PR 自检清单附上（功能/注释/测试/文档）
- [ ] 关注：功能正确、类型/风格、性能、异步、安全
- [ ] 注释质量：中文业务逻辑与交互流程完整

## 6. UX/UI
- [ ] 断点与响应式：布局/字体/图片/交互适配
- [ ] 触控目标 ≥ 44-48px；状态/反馈齐全
- [ ] a11y：语义标签、对比度 AA、焦点可见、键盘可达
- [ ] 设计 tokens（CSS variables）统一消费

## 7. 发布
- [ ] 容器化：最小镜像、签名（Cosign）、SBOM（Syft）
- [ ] 灰度/蓝绿：发布计划与回滚标准明确
- [ ] 观测：APM/Logs/Metrics/Trace；Web Vitals 阈值设定
- [ ] 发布材料：Changelog、运行手册、复盘模版

## 8. 调试/运维
- [ ] 全局异常处理；统一错误体
- [ ] 结构化日志：request_id/trace_id/耗时/状态码
- [ ] 资源：连接池/文件句柄/线程回收；超时/重试/熔断
- [ ] 前后端联调：CORS、DevTools、SourceMap、Sentry

## 9. 功能导航
- [ ] 路由 → 用例 → 仓库 → DB/Client 链路可追
- [ ] 新功能按五步走：Domain → UseCase → RepoImpl → Router → 前端/测试

## 10. 验收门槛（出 PR 前最后检查）
- [ ] ruff/black/isort/mypy 全绿
- [ ] pytest + coverage ≥ 80%
- [ ] pip-audit/bandit 通过或注明风险与隔离
- [ ] OpenAPI/文档/CHANGELOG 同步
- [ ] 关键路径 E2E 与 a11y 通过

—
适用：Python 3.11 Web（FastAPI/现代前端）。版本：1.0

