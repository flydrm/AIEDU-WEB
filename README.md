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

## 导出与资料

- PMO/PM 需求分析（Markdown）：`./docs/requirements-analysis-mvp.md`
- PMO/PM 需求分析（PDF）：`./docs/requirements-analysis-mvp.pdf`

### 一键导出 PDF（需要 Node 环境）

```bash
# 安装工具依赖（首次）
npm --prefix tools install

# 将 Markdown 导出为 PDF
node tools/md2pdf.js ./docs/requirements-analysis-mvp.md ./docs/requirements-analysis-mvp.pdf
```

