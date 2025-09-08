# 测试策略SOP（Python 3.11 Web）

## 目的
建立全面的测试策略，确保软件质量，减少缺陷，提升用户体验。

## 测试金字塔

```
                /\
               /  \
              / E2E \           (10%)  Playwright/pytest + dockerized deps
             /______\
            /  集成  \          (20%)  httpx + Test DB/containers
           /________\
          /   单元    \         (70%)  pytest/pytest-asyncio
         /__________\
```

## 1. 单元测试

### 1.1 测试范围
- **UseCase**: 业务编排逻辑
- **Repository**: 数据访问与适配
- **Schema/DTO**: Pydantic 校验与转换
- **Utilities**: 工具函数

### 1.2 测试原则
- **F.I.R.S.T原则**
  - **F**ast: 快速执行
  - **I**ndependent: 相互独立
  - **R**epeatable: 可重复运行
  - **S**elf-validating: 自我验证
  - **T**imely: 及时编写

### 1.3 测试示例（UseCase）
```python
import pytest


@pytest.mark.asyncio
async def test_use_case_generates_story():
    from app.application.use_cases.generate_story import GenerateStoryUseCase

    class FakeRepo:
        async def generate(self, topic: str):
            from app.domain.models import Story
            return Story(id="1", title="t", content="c")

    story = await GenerateStoryUseCase(FakeRepo())("恐龙")
    assert story.id
```

#### Repository测试
```text
class StoryRepositoryImplTest {
    
    private lateinit var apiService: StoryApiService
    private lateinit var storyDao: StoryDao
    private lateinit var repository: StoryRepository
    
    @Before
    fun setup() {
        apiService = mockk()
        storyDao = mockk()
        repository = StoryRepositoryImpl(apiService, storyDao)
    }
    
    @Test
    fun `API成功时应返回故事并缓存`() = runTest {
        // Given
        val topic = "太空"
        val apiResponse = StoryResponse(
            id = "123",
            title = "太空冒险",
            content = "在遥远的太空..."
        )
        coEvery { apiService.generateStory(any()) } returns apiResponse
        coEvery { storyDao.insert(any()) } just Runs
        
        // When
        val result = repository.generateStory(topic)
        
        // Then
        assertThat(result.isSuccess).isTrue()
        assertThat(result.getOrNull()?.title).isEqualTo("太空冒险")
        coVerify { storyDao.insert(any()) }
    }
    
    @Test
    fun `API失败时应返回缓存数据`() = runTest {
        // Given
        val cachedStory = StoryEntity(
            id = "cached",
            title = "缓存故事",
            content = "这是缓存的故事"
        )
        coEvery { apiService.generateStory(any()) } throws IOException()
        coEvery { storyDao.getRandomStory() } returns cachedStory
        
        // When
        val result = repository.generateStory("any")
        
        // Then
        assertThat(result.isSuccess).isTrue()
        assertThat(result.getOrNull()?.id).isEqualTo("cached")
    }
}
```

### 1.4 Mock最佳实践
```text
// 使用MockK
val mockService = mockk<ApiService> {
    coEvery { getData() } returns TestData.sample
}

// 使用relaxed mock减少样板代码
val mockRepo = mockk<Repository>(relaxed = true)

// 验证调用
coVerify(exactly = 1) { mockService.getData() }

// 捕获参数
val slot = slot<String>()
coEvery { mockService.search(capture(slot)) } returns emptyList()
// 使用后检查: slot.captured
```

## 2. E2E/UI 测试

### 2.1 Playwright 示例（前端）
```ts
import { test, expect } from '@playwright/test';

test('首页加载并显示导航', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page.getByText('首页')).toBeVisible();
});
```
### 2.2 跨视口/设备测试
```ts
import { test } from '@playwright/test';

const viewports = [
  { width: 375, height: 667 },   // iPhone 8
  { width: 768, height: 1024 },  // iPad
  { width: 1280, height: 800 },  // Laptop
];

for (const viewport of viewports) {
  test(`responsive layout @${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto('http://localhost:3000/stories');
    // 断言关键模块在各断点均可见/不重叠
  });
}
```

### 2.2 测试ID最佳实践
```text
// 为复杂UI元素添加testTag
Button(
    modifier = Modifier.testTag("generate_story_button"),
    onClick = onGenerateStory
) {
    Text("生成故事")
}

// 测试中使用
composeTestRule.onNodeWithTag("generate_story_button").performClick()
```

## 3. 集成测试

### 3.1 API集成测试（httpx + FastAPI TestClient）
```python
from fastapi.testclient import TestClient
from app.presentation.api.main import app


def test_health():
    c = TestClient(app)
    r = c.get('/health')
    assert r.status_code == 200
```

### 3.2 数据库集成测试（SQLite 内存库示例）
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def session():
    engine = create_engine('sqlite+pysqlite:///:memory:', echo=False, future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with TestingSessionLocal() as s:
        yield s
```

## 4. 端到端测试

### 4.1 用户流程测试
后端：使用 TestClient 走完关键业务链路；前端：使用 Playwright 覆盖关键路径。

## 5. 性能测试

### 5.1 基准/性能测试
后端：locust/k6 压测关键接口，观察 P95 延迟、错误率、吞吐。

### 5.2 资源与内存
监控进程内存与文件句柄，关注连接池与未关闭资源；容器限制合理配置。

## 6. 测试数据管理

### 6.1 测试数据工厂
```python
from faker import Faker

fake = Faker()

def make_user():
    return {"name": fake.name(), "email": fake.email()}
```

### 6.2 测试配置
```ini
# pytest.ini
[pytest]
addopts = -q --disable-warnings
```

## 7. 测试报告

### 7.1 覆盖率报告
```bash
coverage run -m pytest
coverage html  # 生成 HTML 报告
```

### 7.2 测试结果可视化
```groovy
// build.gradle
testOptions {
    unitTests {
        includeAndroidResources = true
        all {
            testLogging {
                events "passed", "skipped", "failed"
                exceptionFormat "full"
            }
        }
    }
}
```

## 8. 持续测试

### 8.1 CI集成
参考开发流程中的 CI 配置，确保 ruff/mypy/pytest/coverage/pip-audit/bandit 均执行。

### 8.2 测试自动化
```kotlin
// 预提交钩子
#!/bin/sh
# .git/hooks/pre-commit

echo "Running tests..."
./gradlew test

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## 最佳实践

### DO ✅
1. **测试先行**: TDD开发模式
2. **保持独立**: 测试间无依赖
3. **清晰命名**: 描述测试场景
4. **及时更新**: 代码改动同步更新测试
5. **关注边界**: 测试边界条件

### DON'T ❌
1. **测试实现**: 测试行为而非实现
2. **过度mock**: 保持适度的真实性
3. **忽略失败**: 及时修复失败的测试
4. **重复测试**: 避免测试重复逻辑
5. **复杂设置**: 保持测试简单

---

*面向 Python 3.11 Web 的测试实践*  
*追求高质量与高覆盖率*