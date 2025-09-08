# 路由与功能入口快速定位指南（Web）

## 目的
帮助开发者快速找到各个功能模块的代码入口，理解功能之间的调用关系，提高开发和调试效率。

## 1. 项目功能地图

### 1.1 整体架构概览（后端路由 + 前端路由）
```
backend (FastAPI)
├── app/presentation/api/v1
│   ├── stories.py    # /api/v1/stories
│   ├── dialogue.py   # /api/v1/dialogue
│   └── users.py      # /api/v1/users
├── app/application   # 用例
├── app/domain        # 领域模型/接口
└── app/infrastructure# DB/缓存/外部服务

frontend (Next.js/Vite)
├── routes/pages
│   ├── /             # 首页
│   ├── /stories      # 故事
│   ├── /chat         # 对话
│   └── /profile      # 个人中心
└── components        # 通用组件
```

### 1.2 功能入口映射（后端/前端）
| 功能 | 后端路由 | 用例 | 仓库 | 前端页面 |
|------|----------|------|------|----------|
| 故事生成 | /api/v1/stories | GenerateStoryUseCase | StoryRepository | /stories |
| 智能对话 | /api/v1/dialogue | SendDialogueMessageUseCase | DialogueRepository | /chat |
| 个人资料 | /api/v1/users/me | - | ProfileRepository | /profile |

## 2. 快速定位技巧

### 2.1 导航与检索
```text
- 后端：搜索路由路径/函数名；查看依赖注入与用例调用
- 前端：搜索页面路由/组件；定位数据请求与状态管理
```

### 2.2 代码结构导航
```kotlin
// 使用结构化注释快速定位
/**
 * 🎯 功能入口：AI故事生成
 * 📍 位置：com.enlightenment.ai.presentation.story
 * 🔗 关联：HomeScreen -> 故事按钮 -> StoryScreen
 * 
 * 调用链路：
 * 1. HomeScreen点击"故事世界"
 * 2. Navigation导航到StoryScreen
 * 3. StoryViewModel.generateStory()
 * 4. GenerateStoryUseCase执行
 * 5. StoryRepository调用API
 */
```

## 3. 主要功能模块详解

### 3.1 首页模块
```kotlin
/**
 * 首页功能入口
 * 文件：presentation/home/HomeScreen.kt
 */
@Composable
fun HomeScreen(
    // 导航回调 - 点击各功能按钮时调用
    onNavigateToStory: () -> Unit,      // 跳转到故事
    onNavigateToDialogue: () -> Unit,   // 跳转到对话
    onNavigateToCamera: () -> Unit,     // 跳转到相机
    onNavigateToProfile: () -> Unit,    // 跳转到个人中心
    onNavigateToParent: () -> Unit      // 跳转到家长入口
) {
    // 界面布局
    Column {
        // 顶部标题栏
        TopAppBar(
            title = { Text("AI启蒙时光") },
            actions = {
                // 家长入口按钮
                IconButton(onClick = onNavigateToParent) {
                    Icon(Icons.Default.Settings, "家长中心")
                }
            }
        )
        
        // 功能网格
        LazyVerticalGrid(columns = GridCells.Fixed(2)) {
            // 故事世界入口
            item {
                FeatureCard(
                    title = "故事世界",
                    icon = Icons.Story,
                    onClick = onNavigateToStory
                )
            }
            
            // 智能对话入口
            item {
                FeatureCard(
                    title = "智能对话",
                    icon = Icons.Chat,
                    onClick = onNavigateToDialogue
                )
            }
            
            // 探索相机入口
            item {
                FeatureCard(
                    title = "探索相机",
                    icon = Icons.Camera,
                    onClick = onNavigateToCamera
                )
            }
            
            // 我的资料入口
            item {
                FeatureCard(
                    title = "我的",
                    icon = Icons.Person,
                    onClick = onNavigateToProfile
                )
            }
        }
    }
}
```

### 3.2 AI故事模块
```kotlin
/**
 * AI故事功能完整链路
 */

// 1. 界面入口
// 文件：presentation/story/StoryScreen.kt
@Composable
fun StoryScreen(
    viewModel: StoryViewModel = hiltViewModel(),
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    
    // 故事主题输入
    var topic by remember { mutableStateOf("") }
    
    Column {
        // 输入区域
        OutlinedTextField(
            value = topic,
            onValueChange = { topic = it },
            label = { Text("想听什么故事？") }
        )
        
        // 生成按钮
        Button(
            onClick = { viewModel.generateStory(topic) },
            enabled = topic.isNotBlank() && !uiState.isLoading
        ) {
            Text("生成故事")
        }
        
        // 结果展示
        when (uiState) {
            is StoryUiState.Loading -> LoadingAnimation()
            is StoryUiState.Success -> StoryContent(uiState.story)
            is StoryUiState.Error -> ErrorMessage(uiState.message)
        }
    }
}

// 2. ViewModel层
// 文件：presentation/story/StoryViewModel.kt
@HiltViewModel
class StoryViewModel @Inject constructor(
    private val generateStoryUseCase: GenerateStoryUseCase,
    private val textToSpeech: TextToSpeechManager
) : ViewModel() {
    
    private val _uiState = MutableStateFlow<StoryUiState>(StoryUiState.Idle)
    val uiState: StateFlow<StoryUiState> = _uiState.asStateFlow()
    
    /**
     * 生成故事的入口方法
     * 调用链：UI点击 -> ViewModel -> UseCase -> Repository -> API
     */
    fun generateStory(topic: String) {
        viewModelScope.launch {
            _uiState.value = StoryUiState.Loading
            
            generateStoryUseCase(topic)
                .onSuccess { story ->
                    _uiState.value = StoryUiState.Success(story)
                    // 可选：自动播放语音
                    playStoryAudio(story.content)
                }
                .onFailure { error ->
                    _uiState.value = StoryUiState.Error(
                        getUserFriendlyError(error)
                    )
                }
        }
    }
}

// 3. UseCase层
// 文件：domain/usecase/GenerateStoryUseCase.kt
class GenerateStoryUseCase @Inject constructor(
    private val storyRepository: StoryRepository
) {
    /**
     * 业务逻辑入口
     * 职责：参数验证、业务规则处理
     */
    suspend operator fun invoke(topic: String): Result<Story> {
        // 验证输入
        if (topic.isBlank()) {
            return Result.failure(IllegalArgumentException("主题不能为空"))
        }
        
        // 调用Repository
        return storyRepository.generateStory(topic)
    }
}

// 4. Repository层
// 文件：data/repository/StoryRepositoryImpl.kt
@Singleton
class StoryRepositoryImpl @Inject constructor(
    private val apiService: StoryApiService,
    private val storyDao: StoryDao,
    private val networkRetryPolicy: NetworkRetryPolicy
) : StoryRepository {
    
    /**
     * 数据获取入口
     * 职责：协调远程和本地数据源
     */
    override suspend fun generateStory(topic: String): Result<Story> {
        return try {
            // 优先从网络获取
            val story = networkRetryPolicy.retryableNetworkCall {
                apiService.generateStory(
                    StoryRequest(topic = topic)
                )
            }
            
            // 保存到本地
            storyDao.insertStory(story.toEntity())
            
            Result.success(story.toDomainModel())
        } catch (e: Exception) {
            // 降级到本地缓存
            val cachedStory = storyDao.getRandomStory()
            if (cachedStory != null) {
                Result.success(cachedStory.toDomainModel())
            } else {
                Result.failure(e)
            }
        }
    }
}
```

### 3.3 导航系统
```kotlin
/**
 * 导航配置中心
 * 文件：presentation/navigation/EnlightenmentNavHost.kt
 */
@Composable
fun EnlightenmentNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route,
        modifier = modifier
    ) {
        // 首页
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToStory = {
                    navController.navigate(Screen.Story.route)
                },
                onNavigateToDialogue = {
                    navController.navigate(Screen.Dialogue.route)
                },
                onNavigateToCamera = {
                    navController.navigate(Screen.Camera.route)
                },
                onNavigateToProfile = {
                    navController.navigate(Screen.Profile.route)
                },
                onNavigateToParent = {
                    navController.navigate(Screen.ParentLogin.route)
                }
            )
        }
        
        // AI故事
        composable(Screen.Story.route) {
            StoryScreen(
                onBack = { navController.popBackStack() }
            )
        }
        
        // 智能对话
        composable(Screen.Dialogue.route) {
            DialogueScreen(
                onBack = { navController.popBackStack() }
            )
        }
        
        // 拍照识别
        composable(Screen.Camera.route) {
            CameraScreen(
                onBack = { navController.popBackStack() },
                onImageCaptured = { imageUri ->
                    // 处理拍照结果
                }
            )
        }
        
        // 个人中心
        composable(Screen.Profile.route) {
            ProfileScreen(
                onBack = { navController.popBackStack() }
            )
        }
        
        // 家长验证
        composable(Screen.ParentLogin.route) {
            ParentLoginScreen(
                onSuccess = {
                    navController.navigate(Screen.ParentDashboard.route)
                },
                onBack = { navController.popBackStack() }
            )
        }
        
        // 家长中心
        composable(Screen.ParentDashboard.route) {
            ParentDashboardScreen(
                onBack = { navController.popBackStack() },
                onNavigateToSettings = { settingType ->
                    navController.navigate("settings/$settingType")
                }
            )
        }
    }
}

/**
 * 路由定义
 */
sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Story : Screen("story")
    object Dialogue : Screen("dialogue")
    object Camera : Screen("camera")
    object Profile : Screen("profile")
    object ParentLogin : Screen("parent_login")
    object ParentDashboard : Screen("parent_dashboard")
    
    // 带参数的路由
    object StoryDetail : Screen("story/{storyId}") {
        fun createRoute(storyId: String) = "story/$storyId"
    }
}
```

## 4. 快速添加新功能

### 4.1 添加新功能的标准流程
```kotlin
/**
 * 示例：添加"每日任务"功能
 */

// Step 1: 创建领域模型
// domain/model/DailyTask.kt
data class DailyTask(
    val id: String,
    val title: String,
    val description: String,
    val points: Int,
    val isCompleted: Boolean
)

// Step 2: 定义Repository接口
// domain/repository/DailyTaskRepository.kt
interface DailyTaskRepository {
    suspend fun getDailyTasks(): Result<List<DailyTask>>
    suspend fun completeTask(taskId: String): Result<Unit>
}

// Step 3: 创建UseCase
// domain/usecase/GetDailyTasksUseCase.kt
class GetDailyTasksUseCase @Inject constructor(
    private val repository: DailyTaskRepository
) {
    suspend operator fun invoke(): Result<List<DailyTask>> {
        return repository.getDailyTasks()
    }
}

// Step 4: 实现Repository
// data/repository/DailyTaskRepositoryImpl.kt
@Singleton
class DailyTaskRepositoryImpl @Inject constructor(
    private val apiService: DailyTaskApiService,
    private val taskDao: DailyTaskDao
) : DailyTaskRepository {
    
    override suspend fun getDailyTasks(): Result<List<DailyTask>> {
        // 实现数据获取逻辑
    }
}

// Step 5: 创建ViewModel
// presentation/dailytask/DailyTaskViewModel.kt
@HiltViewModel
class DailyTaskViewModel @Inject constructor(
    private val getDailyTasksUseCase: GetDailyTasksUseCase,
    private val completeTaskUseCase: CompleteTaskUseCase
) : ViewModel() {
    // 状态管理和业务逻辑
}

// Step 6: 创建UI界面
// presentation/dailytask/DailyTaskScreen.kt
@Composable
fun DailyTaskScreen(
    viewModel: DailyTaskViewModel = hiltViewModel(),
    onBack: () -> Unit
) {
    // UI实现
}

// Step 7: 添加导航路由
// 在Navigation中添加新路由
composable(Screen.DailyTask.route) {
    DailyTaskScreen(
        onBack = { navController.popBackStack() }
    )
}

// Step 8: 在首页添加入口
// 在HomeScreen中添加新功能入口
FeatureCard(
    title = "每日任务",
    icon = Icons.Task,
    onClick = { navController.navigate(Screen.DailyTask.route) }
)
```

### 4.2 功能模块清单模板
```kotlin
/**
 * 新功能检查清单
 * 
 * Domain层：
 * □ 创建数据模型 (model/)
 * □ 定义Repository接口 (repository/)
 * □ 实现UseCase (usecase/)
 * 
 * Data层：
 * □ 定义API接口 (remote/api/)
 * □ 创建DTO模型 (remote/model/)
 * □ 实现Repository (repository/)
 * □ 创建DAO接口 (local/dao/)
 * □ 定义Entity (local/entity/)
 * 
 * Presentation层：
 * □ 创建ViewModel (viewmodel/)
 * □ 实现UI界面 (screen/)
 * □ 定义UI状态 (state/)
 * □ 添加导航路由 (navigation/)
 * 
 * DI配置：
 * □ 提供Repository绑定 (RepositoryModule)
 * □ 配置ViewModel (无需手动，Hilt自动处理)
 * 
 * 测试：
 * □ 编写UseCase测试
 * □ 编写ViewModel测试
 * □ 编写UI测试
 */
```

## 5. 调试功能入口

### 5.1 功能追踪工具
```kotlin
/**
 * 功能调用追踪器
 * 用于调试功能调用链路
 */
object FeatureTracker {
    
    private val callStack = mutableListOf<String>()
    
    fun enter(feature: String, extra: String = "") {
        val entry = "${System.currentTimeMillis()} -> $feature $extra"
        callStack.add(entry)
        Timber.d("📍 进入功能: $feature $extra")
    }
    
    fun exit(feature: String) {
        Timber.d("📤 退出功能: $feature")
    }
    
    fun printCallStack() {
        Timber.d("=== 功能调用栈 ===")
        callStack.forEach { entry ->
            Timber.d(entry)
        }
        Timber.d("================")
    }
    
    @Composable
    fun TrackedScreen(
        screenName: String,
        content: @Composable () -> Unit
    ) {
        DisposableEffect(screenName) {
            enter(screenName)
            onDispose {
                exit(screenName)
            }
        }
        content()
    }
}

// 使用示例
@Composable
fun StoryScreen() {
    FeatureTracker.TrackedScreen("StoryScreen") {
        // 界面内容
    }
}
```

### 5.2 功能开关配置
```kotlin
/**
 * 功能开关管理
 * 用于控制功能的启用/禁用
 */
object FeatureFlags {
    
    // 功能开关定义
    var isVoiceEnabled by mutableStateOf(true)
    var isCameraEnabled by mutableStateOf(true)
    var isDebugMenuEnabled by mutableStateOf(BuildConfig.DEBUG)
    
    // 远程配置（可选）
    fun loadRemoteConfig() {
        // 从服务器加载功能开关配置
    }
    
    @Composable
    fun ConditionalFeature(
        flag: Boolean,
        content: @Composable () -> Unit
    ) {
        if (flag) {
            content()
        }
    }
}

// 使用示例
@Composable
fun HomeScreen() {
    Column {
        // 条件显示相机功能
        FeatureFlags.ConditionalFeature(FeatureFlags.isCameraEnabled) {
            FeatureCard(
                title = "探索相机",
                onClick = { /* 导航到相机 */ }
            )
        }
    }
}
```

## 6. 功能依赖关系图

### 6.1 模块依赖关系
```
presentation
    ↓ 依赖
domain (纯Kotlin，无Android依赖)
    ↑ 被依赖
data

具体流程：
UI操作 → ViewModel → UseCase → Repository接口
                                    ↑
                            RepositoryImpl → API/Database
```

### 6.2 数据流向图
```
用户输入 → UI Event → ViewModel Action → UseCase Execute
                                              ↓
UI Update ← ViewModel State ← UseCase Result ←
```

## 最佳实践

### DO ✅
1. **保持功能独立**：每个功能模块应该高内聚低耦合
2. **统一命名规范**：功能相关的类使用一致的前缀
3. **添加导航注释**：在关键位置添加功能说明
4. **使用依赖注入**：通过Hilt管理依赖关系
5. **编写功能文档**：新功能要有使用说明

### DON'T ❌
1. **跨层直接调用**：不要让UI直接调用Repository
2. **硬编码导航**：使用Navigation组件管理
3. **功能耦合**：避免功能之间直接依赖
4. **忽视错误处理**：每个功能都要有错误处理
5. **破坏架构原则**：遵循Clean Architecture

---

*功能入口快速定位指南 v1.0*  
*让功能查找不再是难题*