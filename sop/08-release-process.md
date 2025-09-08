# 发布流程SOP（Docker/K8s，Python 3.11 Web）

## 目的
建立标准化的发布流程，确保每次发布都安全、可靠、可追溯。

## 发布流程概览

```mermaid
graph LR
    A[版本规划] --> B[功能冻结]
    B --> C[测试验证]
    C --> D[镜像构建/签名/SBOM]
    D --> E[灰度发布(K8s/金丝雀/蓝绿)]
    E --> F[全量发布]
    F --> G[实时监控(APM/Logs/Metrics/Trace)]
    G --> H[发布复盘]
```

## 1. 版本规划

### 1.1 版本号规范
遵循 SemVer：主.次.修订（Major.Minor.Patch）

### 1.2 发布周期
- **大版本**: 3-6个月
- **功能版本**: 2-4周
- **修复版本**: 按需发布
- **紧急修复**: 24小时内

### 1.3 版本计划模板
```markdown
# 版本 1.2.0 发布计划

## 发布日期
2024-01-15

## 发布内容
### 新功能
- [ ] 智能对话功能优化
- [ ] 新增10个故事主题
- [ ] 家长报告功能

### 优化
- [ ] 启动速度优化30%
- [ ] 内存占用减少20%

### 修复
- [ ] 修复相机权限崩溃问题
- [ ] 修复横屏显示异常

## 风险评估
- 数据库升级需要迁移
- 新API需要后端配合

## 回滚方案
- 保留上一个稳定容器镜像 Tag（如 app:prev-stable）
- 预备数据库降级脚本/回滚策略（审慎评估数据丢失风险）
```

## 2. 功能冻结

### 2.1 冻结检查清单
- [ ] 所有计划功能已完成
- [ ] 代码已合并到release分支
- [ ] 不再接受新功能
- [ ] 只允许bug修复
- [ ] 通知所有相关人员

### 2.2 创建发布分支
```bash
# 从develop创建release分支
git checkout develop
git pull origin develop
git checkout -b release/1.2.0

# 更新版本号（示例）
# pyproject.toml / package.json / chart/values.yaml（镜像tag）
# 确保后端与前端版本对齐，并记录于CHANGELOG.md

# 提交版本号更改
git add .
git commit -m "chore: bump version to 1.2.0"
git push origin release/1.2.0
```

## 3. 测试验证

### 3.1 测试清单
```markdown
## 功能测试（后端/前端）
- [ ] 新功能测试完成（用例覆盖）
- [ ] 回归测试通过（关键路径）
- [ ] 边界/异常场景测试
- [ ] 合同测试（OpenAPI Schema、schemathesis）

## 兼容性测试（Web）
- 浏览器矩阵（Chrome/Edge/Firefox/Safari 近两个大版本）
- 终端矩阵（Desktop/Mobile 常见分辨率）
- 后端依赖（Python3.11、DB版本、Redis、消息队列）

## 性能与可靠性
- [ ] API P95/P99 延迟与吞吐
- [ ] 错误率/超时率
- [ ] 资源使用（CPU/内存/连接池）
- [ ] 关键场景压测（k6/locust）
```

### 3.2 自动化测试
```bash
uv run ruff . && uv run mypy .
uv run coverage run -m pytest && uv run coverage report --fail-under=80
uv run pip-audit -P || true
uv run bandit -q -r app || true
```

## 4. 发布准备

### 4.1 镜像构建
```dockerfile
# Dockerfile（示例）
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml poetry.lock* requirements*.txt* /app/
RUN pip install --no-cache-dir -U pip && \
    (pip install --no-cache-dir uv || true) && \
    (uv pip install -r requirements.txt || pip install -r requirements.txt)
COPY . /app
CMD ["uvicorn", "app.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
# 构建与签名（示例）
docker build -t registry.example.com/app:${GIT_SHA} .
cosign sign --key cosign.key registry.example.com/app:${GIT_SHA}
syft packages registry.example.com/app:${GIT_SHA} -o spdx-json > sbom.json
```

### 4.2 镜像签名与SBOM策略
- Cosign 对镜像签名；公钥验证纳入部署流水线
- Syft/Grype 生成并扫描 SBOM（SPDX/CycloneDX）
- 产物与签名、SBOM 一并归档与可追溯

### 4.3 产物与配置
- 配置与密钥：12-Factor（环境变量/密钥管理），严禁硬编码
- 构建产物：容器镜像 + Helm/Manifests + SBOM

### 4.4 发布材料准备
```markdown
## 对外材料
- 变更日志（Changelog）
- 公开公告（如适用）

## 内部材料
- 发布说明（范围/影响/风险/回滚）
- 测试与验收报告
- 运行手册/应急预案
```

## 5. 灰度发布

### 5.1 灰度策略
K8s Deployment 使用分批/金丝雀/蓝绿发布；按流量或实例比例推进，实时回看指标。

### 5.2 监控指标
- 错误率、P95/P99 延迟、吞吐、资源占用
- 业务关键指标（转化、留存、活跃）

### 5.3 灰度控制
- 网关/服务网格权重路由（Istio/Traefik/Nginx Ingress）逐步放量
- 特性开关（后端/前端）按用户/租户/比例控制

## 6. 全量发布

### 6.1 发布前检查
- [ ] 灰度数据正常
- [ ] 无严重bug反馈
- [ ] 性能指标达标
- [ ] 后端服务就绪
- [ ] 客服团队准备

### 6.2 发布操作
- 容器注册表推送、签名验证（Cosign）
- 部署：ArgoCD/GitOps 或 kubectl/helm

### 6.3 发布通知
```markdown
主题：v1.2.0 生产发布完成（服务/组件清单）

更新内容：主要功能/修复摘要 + 链接（变更日志、看板）
监控与回滚：关键指标链接（Grafana/APM/Logs）、回滚指令与条件
责任人：技术/产品/值班信息
```

## 7. 发布监控

### 7.1 实时监控
- 日志：结构化 JSON，集中收集（ELK/Datadog/Cloud Logging）
- 指标：Prometheus/Grafana，错误率/延迟/吞吐/资源
- 追踪：OpenTelemetry + backend（Tempo/Jaeger/Datadog）

### 7.2 监控仪表板
```markdown
## 发布后24小时监控（示例）

### 服务稳定性
- 错误率：< 0.5%
- P95 延迟：< 200ms（核心接口）
- 可用性（SLO）：99.9%

### 性能与资源
- 吞吐：RPS/QPS
- CPU/内存/连接池占用
- 缓存命中率

### 业务指标
- 核心转化/完成率
- 活跃/留存
```

## 8. 发布总结

### 8.1 发布复盘会议
```markdown
## 复盘会议议程

1. **数据回顾** (10分钟)
   - 发布指标汇总
   - 目标达成情况

2. **问题分析** (20分钟)
   - 发现的问题
   - 原因分析
   - 影响评估

3. **经验总结** (15分钟)
   - 做得好的地方
   - 需要改进的地方
   - 最佳实践

4. **改进计划** (15分钟)
   - 具体改进措施
   - 责任人和时间
   - 跟进机制
```

### 8.2 发布报告模板
```markdown
# v1.2.0 发布总结报告（Web）

## 发布概况
- 版本号：1.2.0
- 发布日期：2025-01-15
- 发布范围：全量用户

## 关键指标
| 指标 | 目标 | 实际 | 结果 |
|------|------|------|------|
| 错误率 | <0.5% | 0.3% | ✅ |
| P95 延迟 | <200ms | 180ms | ✅ |
| 可用性 | 99.9% | 99.95% | ✅ |

## 主要问题与解决
1. CDN 边缘节点异常 → 切换回源并调整缓存策略
2. 后端连接池耗尽 → 增加池大小并优化超时与重试

## 经验教训与改进
- 提前压测关键路径，完善容量计划
- 增强可观测性告警阈值与分级
```

## 9. 紧急回滚

### 9.1 回滚决策
```markdown
## 回滚标准
触发以下任一条件立即回滚：
- 崩溃率 > 1%
- 核心功能不可用
- 数据丢失风险
- 安全漏洞
```

### 9.2 回滚操作
```bash
# 回滚到上一个稳定镜像（示例）
kubectl rollout undo deployment/app-deploy
```

## 最佳实践

### DO ✅
1. **充分测试**: 不要急于发布
2. **逐步推进**: 灰度发布很重要
3. **实时监控**: 及时发现问题
4. **快速响应**: 问题及时处理
5. **总结经验**: 持续改进流程

### DON'T ❌
1. **仓促发布**: 赶时间牺牲质量
2. **忽视反馈**: 用户反馈很重要
3. **缺乏准备**: 回滚方案要ready
4. **单点依赖**: 避免关键人缺席
5. **重复错误**: 同样问题不二犯

---

*面向 Python 3.11 Web 的发布经验*  
*确保每次发布都平稳可靠*