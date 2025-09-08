# 开发环境与工具指南SOP（Python 3.11 Web）

## 目的
提供 Python Web 项目本地开发、运行、调试、问题修复与发布所需的环境与工具指南。

## 1. 项目导入与配置

### 1.1 首次导入项目
```bash
git clone https://github.com/company/project.git
cd project

# 使用 uv（推荐）或 poetry/pip
pip install -U uv || true
uv sync  # 或 poetry install / pip install -r requirements.txt
```

### 1.2 环境配置检查
```text
检查清单：
- Python: 3.11.x
- Node.js: LTS（如涉及前端）
- 包管理: uv/poetry/pip 与锁定文件
- 数据库: Postgres/MySQL/SQLite
- Redis/消息队列（按需）
```

### 1.3 配置文件设置
```env
# .env（不要提交到Git）
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
API_KEY=xxxxx

# pyproject.toml（片段）
[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.11"
```

## 2. 运行项目

### 2.1 运行配置
```bash
uv run uvicorn app.presentation.api.main:app --host 0.0.0.0 --port 8080 --reload
```

### 2.2 前端
```bash
pnpm install && pnpm dev  # 或 npm/yarn
```

### 2.3 本地调试
```text
- Swagger UI/Redoc 文档联调
- Postman/Insomnia API 测试
- httpx/pytest-asyncio 自动化
```

## 3. 功能入口导航

### 3.1 服务与路由
```text
app/presentation/api: FastAPI 路由层
app/application: 用例层
app/domain: 领域模型与接口
app/infrastructure: DB/缓存/外部客户端
```

### 3.2 快速定位
```text
// 使用快捷定位与分层检索示例
```

### 3.3 路由结构（后端示例）
```python
# app/presentation/api/v1/__init__.py
from fastapi import APIRouter
from .stories import router as stories

api = APIRouter(prefix="/api/v1")
api.include_router(stories)
```

## 4. 调试技巧

### 4.1 断点调试
```text
IDE（PyCharm/VS Code）断点/变量/调用栈；uvicorn --reload 便于快速迭代
```

### 4.2 日志调试
```text
// 日志调试（本地/生产）
```

### 4.3 前端调试（如适用）
```text
// 前端调试说明
```

### 4.4 性能调试
```text
// 性能调试说明
```

## 5. 常见问题修复

### 5.1 构建错误修复
```text
/**
 * 常见构建错误及解决方案
 */

// 1. 依赖冲突
// 错误：Duplicate class found
// 解决：统一依赖与锁文件，避免冲突
implementation("com.example:library:1.0") {
    exclude(group = "com.conflict", module = "module")
}

// 2. 版本不兼容：统一依赖与锁文件，使用兼容矩阵（Python/Node/DB）
// 错误：Module was compiled with an incompatible version
// 解决：统一版本管理
object Versions {
    const val kotlin = "1.9.0"
    const val compose = "1.5.0"
    const val hilt = "2.47"
}

// 3. 资源冲突
// 错误：Resource compilation failed
// 解决：检查资源命名，避免重复
// 使用前缀：ic_story_back.xml 而不是 back.xml

// 4. 清理重建
// 终极解决方案
./gradlew clean
./gradlew build
// 或在Android Studio: Build -> Clean Project -> Rebuild Project
```

### 5.2 运行时错误修复
```text
步骤：复现（最小用例）→ 收集（日志/trace/请求）→ 定位（断点/二分）→ 修复验证
分类：
- 4xx：入参/权限/资源；统一错误体与指引
- 5xx：异常捕获与降级；超时/重试/熔断；回滚策略
```

### 5.3 前端问题修复
```text
常见：布局错位、样式覆盖、跨域、缓存异常、包体积
建议：分环境构建、CSP/跨域策略、按需加载、压缩与缓存
```

## 6. 打包发布

### 6.1 容器化与部署
参考发布流程 SOP 的 Docker/K8s 章节与 CI 配置

## 7. 版本管理

### 7.1 版本号规范
```text
遵循 SemVer：主.次.修订（与镜像Tag/Chart版本一致），记录于 CHANGELOG.md
```

### 7.2 发布检查清单
```text
质量门禁：ruff/mypy/pytest/coverage≥80%/pip-audit/bandit 通过
发布：镜像构建签名/SBOM、Helm/Manifests 校验、灰度/回滚预案
观测：Dashboards 可用、告警阈值设置并验证
文档：Changelog、发布说明、运行手册/演练记录
```

## 8. 团队协作

### 8.1 代码规范检查
```bash
# pre-commit 示例
pre-commit run --all-files  # 包含 ruff/black/isort/mypy/yamllint 等
```

### 8.2 分支管理
```bash
# 功能开发流程
git checkout develop
git pull origin develop
git checkout -b feature/story-voice-support

# 开发完成后
git add .
git commit -m "feat(story): 添加故事语音播放功能

- 集成TTS引擎
- 支持语速调节  
- 添加播放控制UI"

git push origin feature/story-voice-support
# 创建Pull Request
```

## 最佳实践

### DO ✅
1. **经常同步代码**：每天开始工作前pull最新代码
2. **使用快捷键**：提高开发效率
3. **及时提交**：小步提交，方便回滚
4. **保持整洁**：定期清理无用代码和资源
5. **文档同步**：代码改动同步更新文档

### DON'T ❌
1. **提交大文件**：使用Git LFS管理大文件
2. **硬编码配置**：使用BuildConfig或配置文件
3. **忽略警告**：及时处理编译警告
4. **跳过测试**：确保测试通过再提交
5. **直接改主分支**：始终通过PR合并代码

---

*Android Studio操作指南 v1.0*  
*基于AI启蒙时光项目实践*