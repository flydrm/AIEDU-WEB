# 测试策略SOP

## 目的
建立全面的测试策略，确保软件质量，减少缺陷，提升用户体验。

## 测试金字塔

```
                /\
               /  \
              / E2E \           (10%)
             /______\
            /  集成  \          (20%)
           /________\
          /   单元    \         (70%)
         /__________\
```

## 1. 单元测试

### 1.1 测试范围
- **ViewModel**: 业务逻辑和状态管理
- **UseCase**: 用例逻辑
- **Repository**: 数据处理逻辑
- **Utility**: 工具类和扩展函数

### 1.2 测试原则
- **F.I.R.S.T原则**
  - **F**ast: 快速执行
  - **I**ndependent: 相互独立
  - **R**epeatable: 可重复运行
  - **S**elf-validating: 自我验证
  - **T**imely: 及时编写

### 1.3 测试示例

#### ViewModel测试
```kotlin
@ExperimentalCoroutinesApi
class StoryViewModelTest {
    
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()
    
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()
    
    private lateinit var generateStoryUseCase: GenerateStoryUseCase
    private lateinit var viewModel: StoryViewModel
    
    @Before
    fun setup() {
        generateStoryUseCase = mockk()
        viewModel = StoryViewModel(generateStoryUseCase)
    }
    
    @Test
    fun `生成故事成功时应更新UI状态`() = runTest {
        // Given - 准备测试数据
        val topic = "恐龙"
        val expectedStory = Story(
            id = "1",
            title = "小恐龙历险记",
            content = "很久很久以前...",
            questions = listOf(
                Question("恐龙吃什么？", listOf("草", "肉", "都吃"), 2)
            )
        )
        coEvery { generateStoryUseCase(topic) } returns Result.success(expectedStory)
        
        // When - 执行测试动作
        viewModel.generateStory(topic)
        advanceUntilIdle()
        
        // Then - 验证结果
        val state = viewModel.uiState.value
        assertThat(state.isLoading).isFalse()
        assertThat(state.story).isEqualTo(expectedStory)
        assertThat(state.error).isNull()
    }
    
    @Test
    fun `网络错误时应显示友好提示`() = runTest {
        // Given
        val topic = "恐龙"
        coEvery { generateStoryUseCase(topic) } returns Result.failure(
            NetworkException("网络连接失败")
        )
        
        // When
        viewModel.generateStory(topic)
        advanceUntilIdle()
        
        // Then
        val state = viewModel.uiState.value
        assertThat(state.isLoading).isFalse()
        assertThat(state.error).isEqualTo("网络不太好，请稍后再试")
        assertThat(state.story).isNull()
    }
}
```

#### Repository测试
```kotlin
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
```kotlin
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

## 2. UI测试

### 2.1 Compose UI测试
```kotlin
class HomeScreenTest {
    
    @get:Rule
    val composeTestRule = createComposeRule()
    
    @Test
    fun 首页应显示所有功能按钮() {
        // Given
        composeTestRule.setContent {
            AIEnlightenmentTheme {
                HomeScreen(
                    onNavigateToStory = {},
                    onNavigateToDialogue = {},
                    onNavigateToCamera = {},
                    onNavigateToProfile = {}
                )
            }
        }
        
        // Then
        composeTestRule.onNodeWithText("故事世界").assertIsDisplayed()
        composeTestRule.onNodeWithText("智能对话").assertIsDisplayed()
        composeTestRule.onNodeWithText("探索相机").assertIsDisplayed()
        composeTestRule.onNodeWithText("我的").assertIsDisplayed()
    }
    
    @Test
    fun 点击故事按钮应触发导航() {
        // Given
        var navigateCalled = false
        composeTestRule.setContent {
            HomeScreen(
                onNavigateToStory = { navigateCalled = true },
                onNavigateToDialogue = {},
                onNavigateToCamera = {},
                onNavigateToProfile = {}
            )
        }
        
        // When
        composeTestRule.onNodeWithText("故事世界").performClick()
        
        // Then
        assertThat(navigateCalled).isTrue()
    }
}
```

### 2.2 测试ID最佳实践
```kotlin
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

### 3.1 API集成测试
```kotlin
class ApiIntegrationTest {
    
    private lateinit var mockWebServer: MockWebServer
    private lateinit var apiService: ApiService
    
    @Before
    fun setup() {
        mockWebServer = MockWebServer()
        apiService = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
    
    @After
    fun tearDown() {
        mockWebServer.shutdown()
    }
    
    @Test
    fun `成功响应应正确解析`() = runTest {
        // Given
        val mockResponse = MockResponse()
            .setResponseCode(200)
            .setBody("""
                {
                    "id": "123",
                    "title": "测试故事",
                    "content": "这是测试内容"
                }
            """)
        mockWebServer.enqueue(mockResponse)
        
        // When
        val response = apiService.getStory("123")
        
        // Then
        assertThat(response.id).isEqualTo("123")
        assertThat(response.title).isEqualTo("测试故事")
    }
    
    @Test
    fun `网络错误应抛出异常`() = runTest {
        // Given
        mockWebServer.enqueue(MockResponse().setResponseCode(500))
        
        // When & Then
        assertThrows<HttpException> {
            apiService.getStory("123")
        }
    }
}
```

### 3.2 数据库集成测试
```kotlin
@RunWith(AndroidJUnit4::class)
class DatabaseIntegrationTest {
    
    private lateinit var database: AppDatabase
    private lateinit var storyDao: StoryDao
    
    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        database = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        storyDao = database.storyDao()
    }
    
    @After
    fun tearDown() {
        database.close()
    }
    
    @Test
    fun 插入和查询故事应正常工作() = runTest {
        // Given
        val story = StoryEntity(
            id = "test-1",
            title = "测试故事",
            content = "测试内容",
            createdAt = System.currentTimeMillis()
        )
        
        // When
        storyDao.insert(story)
        val stories = storyDao.getAllStories()
        
        // Then
        assertThat(stories).hasSize(1)
        assertThat(stories[0].id).isEqualTo("test-1")
    }
}
```

## 4. 端到端测试

### 4.1 用户流程测试
```kotlin
@LargeTest
@RunWith(AndroidJUnit4::class)
class UserJourneyTest {
    
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)
    
    @Test
    fun 完整的故事生成流程() {
        // 1. 启动应用
        onView(withText("AI启蒙时光")).check(matches(isDisplayed()))
        
        // 2. 点击故事功能
        onView(withText("故事世界")).perform(click())
        
        // 3. 输入主题
        onView(withId(R.id.topic_input))
            .perform(typeText("小兔子"), closeSoftKeyboard())
        
        // 4. 生成故事
        onView(withText("生成故事")).perform(click())
        
        // 5. 等待加载完成
        Thread.sleep(3000) // 实际项目中使用IdlingResource
        
        // 6. 验证故事显示
        onView(withText("小兔子")).check(matches(isDisplayed()))
        
        // 7. 回答问题
        onView(withText("下一题")).perform(click())
        
        // 8. 完成故事
        onView(withText("完成")).check(matches(isDisplayed()))
    }
}
```

## 5. 性能测试

### 5.1 基准测试
```kotlin
@RunWith(AndroidJUnit4::class)
class PerformanceBenchmark {
    
    @get:Rule
    val benchmarkRule = BenchmarkRule()
    
    @Test
    fun measureStoryGeneration() {
        benchmarkRule.measureRepeated {
            runBlocking {
                // 测试故事生成性能
                val useCase = GenerateStoryUseCase(repository)
                useCase.invoke("test")
            }
        }
    }
}
```

### 5.2 内存泄漏检测
```kotlin
class MemoryLeakTest {
    
    @Test
    fun viewModelShouldNotLeakActivity() {
        // 使用LeakCanary检测
        val scenario = launchActivity<MainActivity>()
        
        scenario.onActivity { activity ->
            // 获取ViewModel引用
            val viewModel = ViewModelProvider(activity).get(MainViewModel::class.java)
            
            // 模拟配置变更
            activity.recreate()
            
            // 确保旧Activity被回收
            assertThat(activity.isDestroyed).isTrue()
        }
    }
}
```

## 6. 测试数据管理

### 6.1 测试数据工厂
```kotlin
object TestDataFactory {
    
    fun createStory(
        id: String = "test-${UUID.randomUUID()}",
        title: String = "测试故事",
        content: String = "这是测试内容"
    ) = Story(id, title, content, emptyList())
    
    fun createUser(
        name: String = "测试用户",
        age: Int = 5
    ) = User(name, age)
    
    fun createStoryList(count: Int = 3) = List(count) { index ->
        createStory(
            id = "test-$index",
            title = "故事$index"
        )
    }
}
```

### 6.2 测试配置
```kotlin
// 测试专用配置
object TestConfig {
    const val MOCK_API_URL = "http://localhost:8080/"
    const val TEST_TIMEOUT = 5000L
    const val TEST_USER_TOKEN = "test-token-123"
}

// 测试规则
class TestCoroutineRule : TestWatcher() {
    override fun starting(description: Description?) {
        Dispatchers.setMain(TestCoroutineDispatcher())
    }
    
    override fun finished(description: Description?) {
        Dispatchers.resetMain()
    }
}
```

## 7. 测试报告

### 7.1 覆盖率报告
```bash
# 生成测试覆盖率报告
./gradlew jacocoTestReport

# 查看报告
open app/build/reports/jacoco/test/html/index.html
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
```yaml
# GitHub Actions配置
- name: Run Unit Tests
  run: ./gradlew test
  
- name: Run UI Tests
  run: ./gradlew connectedAndroidTest
  
- name: Upload Test Results
  uses: actions/upload-artifact@v2
  if: failure()
  with:
    name: test-results
    path: app/build/reports/tests
```

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

*基于AI启蒙时光项目测试实践*  
*追求高质量和高覆盖率*