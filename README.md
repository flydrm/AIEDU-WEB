# 项目文档索引（Python 3.11 Web）

本项目的 Web 开发 SOP 文档位于 `sop/` 目录。

## 快速入口

- [SOP 总览](./sop/README.md)
- [SOP 总结](./sop/SUMMARY.md)

## 分章节索引

- [01 需求开发](./sop/01-requirements-development.md)
- [02 需求讨论](./sop/02-requirements-discussion.md)
- [03 架构设计](./sop/03-architecture-design.md)
- [04 UX/UI 设计](./sop/04-ux-ui-design.md)
- [05 开发流程](./sop/05-development-process.md)
- [06 代码审查](./sop/06-code-review.md)
- [07 测试策略](./sop/07-testing-strategy.md)
- [08 发布流程](./sop/08-release-process.md)
- [09 Docstring 与中文注释规范（重点）](./sop/09-comment-standards.md)
- [10 开发环境指南](./sop/10-dev-environment-guide.md)
- [11 调试与问题修复](./sop/11-debugging-troubleshooting.md)
- [12 功能入口快速定位](./sop/12-feature-navigation-guide.md)

### 家长手册
- [家长使用手册](./docs/parent-guide.md)

## 导出与资料

- PMO/PM 需求分析（Markdown）：`./docs/requirements-analysis-mvp.md`
- PMO/PM 需求分析（PDF）：`./docs/requirements-analysis-mvp.pdf`
- 每周报告（PDF）：`./docs/weekly-report.pdf`

### 一键导出 PDF（需要 Node 环境）

```bash
# 安装工具依赖（首次）
npm --prefix tools install

# 将 Markdown 导出为 PDF
node tools/md2pdf.js ./docs/requirements-analysis-mvp.md ./docs/requirements-analysis-mvp.pdf

# 或使用 npm script（推荐）
npm --prefix tools run pdf
```

GitHub Actions（手动触发）：`.github/workflows/export-pdf.yml`

### 每周报告导出（CSV/PDF）

```bash
# CSV（后端接口）
curl -sS http://localhost:8000/api/v1/parent/mastery/weekly.csv -o docs/weekly.csv

# PDF（工具脚本，需后端已启动）
npm --prefix tools install
REPORT_BASE_URL=http://localhost:8000 npm --prefix tools run weekly
```

## 测试运行

### 单元/集成（pytest）
```bash
pytest
```

当前测试用例以占位跳过形式落地，待 S1/S2 实现后逐步去掉 skip 并完善。

### E2E（Playwright）
```bash
# 后端：另一个终端启动
uvicorn app.presentation.api.main:app --host 0.0.0.0 --port 8000

# 前端：代理到 8000
npm --prefix web install
npm --prefix web run dev

# 运行 E2E（从仓库根目录）
E2E_BASE_URL=http://localhost:5173 npx playwright test
```

CI 中可通过为 PR 打上 `run-e2e` 标签触发浏览器端到端用例。

## 运行与容器

### 本地启动
```bash
uv run uvicorn app.presentation.api.main:app --host 0.0.0.0 --port 8000 --reload
```
## 前端（Vite + React + TS）

```bash
npm --prefix web install
npm --prefix web run dev    # http://localhost:5173
npm --prefix web run build
npm --prefix web run preview
```

路由：`/`、`/chat`（SSE）、`/lesson`、`/safety`、`/parent`

环境变量（可选）：
- `AI_PROVIDERS`：JSON 数组，含 `name/base_url/api_key/timeout`
- `AI_BASE_URL` + `AI_API_KEY`：单 provider 简化配置
- `AI_BREAKER_FAILURES`/`AI_BREAKER_COOLDOWN`：熔断阈值与冷却

### Docker
```bash
docker build -t kids-ai-app:latest .
docker run -p 8080:8080 -e AI_BASE_URL=... -e AI_API_KEY=... kids-ai-app:latest
```

