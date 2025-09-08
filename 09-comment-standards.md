# 中文注释规范SOP 【极其重要】

## 🔴 为什么注释如此重要？

### 痛点问题
1. **新人上手慢**：没有注释，新人需要花大量时间理解代码
2. **知识流失快**：人员离职后，业务逻辑无人知晓
3. **沟通成本高**：反复询问"这段代码是做什么的"
4. **修改风险大**：不理解原意，修改容易引入bug
5. **维护困难**：半年后连自己都看不懂当初写的代码

### 注释的价值
1. **代码即文档**：减少额外文档维护成本
2. **知识传承**：业务逻辑得以保留和传递
3. **提高效率**：快速理解和修改代码
4. **降低风险**：避免理解偏差导致的错误
5. **团队协作**：促进团队成员间的理解

## 注释规范要求

### 1. 类注释规范

```kotlin
/**
 * 故事生成仓库实现类
 * 
 * 功能概述：
 * 负责AI故事的生成、缓存和管理，是数据层的核心组件
 * 
 * 主要职责：
 * 1. 调用远程AI服务生成个性化故事
 * 2. 管理本地故事缓存，支持离线使用
 * 3. 实现故事内容的安全过滤
 * 4. 处理网络异常和降级策略
 * 
 * 技术特点：
 * - 使用协程处理异步操作
 * - 实现三级降级策略（AI服务→备用服务→本地缓存）
 * - 支持断网情况下的基本功能
 * 
 * 依赖说明：
 * - AIApiService: 远程AI服务接口
 * - StoryDao: 本地数据库访问
 * - ContentFilter: 内容安全过滤器
 * 
 * 使用示例：
 * ```
 * val story = storyRepository.generateStory("恐龙")
 * ```
 * 
 * 注意事项：
 * - AI服务调用有配额限制，需要合理使用
 * - 缓存清理策略会保留最近7天的数据
 * - 所有生成的内容都会经过儿童适宜性过滤
 * 
 * @author 张三
 * @since 1.0.0
 * @see StoryRepository 接口定义
 * @see AIApiService AI服务接口
 */
@Singleton
class StoryRepositoryImpl @Inject constructor(
    private val apiService: AIApiService,
    private val storyDao: StoryDao,
    private val contentFilter: ContentFilter
) : StoryRepository {
    // 实现代码...
}
```

### 2. 方法注释规范

```kotlin
/**
 * 生成个性化AI故事
 * 
 * 功能说明：
 * 根据用户输入的主题，调用AI服务生成适合儿童的个性化故事。
 * 包含智能降级机制，确保在各种网络环境下都能提供服务。
 * 
 * 业务流程：
 * 1. 验证输入主题的合法性
 * 2. 检查本地缓存是否有最近的相似故事
 * 3. 调用主AI服务（GEMINI-2.5-PRO）生成故事
 * 4. 如果主服务失败，尝试备用服务（GPT-5-PRO）
 * 5. 如果都失败，返回本地缓存的故事
 * 6. 对生成的内容进行安全过滤
 * 7. 保存到本地缓存供离线使用
 * 
 * @param topic 故事主题，支持的主题包括：
 *              - 动物类：恐龙、小兔子、大象等
 *              - 童话类：公主、王子、魔法等
 *              - 科幻类：太空、机器人、未来等
 *              - 日常类：上学、玩耍、家庭等
 * 
 * @param userAge 用户年龄（3-6岁），用于调整故事复杂度
 * 
 * @return Result<Story> 成功返回Story对象，包含：
 *         - id: 故事唯一标识
 *         - title: 故事标题
 *         - content: 故事内容（300-500字）
 *         - questions: 配套的理解问题（3-5个）
 *         失败返回具体错误信息
 * 
 * @throws IllegalArgumentException 当主题为空或包含不适当内容时
 * @throws NetworkException 当网络连接失败时
 * @throws QuotaExceededException 当AI服务配额用完时
 * 
 * 性能说明：
 * - 正常情况：2-5秒返回结果
 * - 网络较差：可能需要10-15秒
 * - 离线模式：立即返回缓存结果
 * 
 * 二次开发指南：
 * 1. 添加新主题：在SUPPORTED_TOPICS常量中添加
 * 2. 调整故事长度：修改StoryRequest中的length参数
 * 3. 更换AI模型：在AIModelConfig中配置新模型
 * 4. 自定义过滤规则：继承ContentFilter类
 * 
 * 更新历史：
 * - 2024-01-15: 添加内容过滤功能
 * - 2024-01-20: 优化降级策略
 * - 2024-01-25: 支持年龄个性化
 */
override suspend fun generateStory(
    topic: String,
    userAge: Int = 5
): Result<Story> = withContext(Dispatchers.IO) {
    try {
        // 步骤1: 参数验证
        validateTopic(topic)
        
        // 步骤2: 尝试从缓存获取
        getCachedStory(topic, userAge)?.let {
            return@withContext Result.success(it)
        }
        
        // 步骤3: 调用AI服务生成
        val story = generateFromAI(topic, userAge)
        
        // 步骤4: 内容过滤
        val filteredStory = contentFilter.filter(story)
        
        // 步骤5: 保存到缓存
        saveToCache(filteredStory)
        
        Result.success(filteredStory)
    } catch (e: Exception) {
        // 记录详细错误信息，方便排查
        Timber.e(e, "生成故事失败 - 主题: $topic, 年龄: $userAge")
        
        // 降级处理
        handleError(e, topic, userAge)
    }
}
```

### 3. 复杂逻辑注释

```kotlin
/**
 * 计算用户学习进度
 * 
 * 算法说明：
 * 使用加权平均算法计算综合进度，不同维度有不同权重：
 * - 故事完成率（40%）：已完成故事数 / 总故事数
 * - 问题正确率（30%）：正确回答数 / 总问题数
 * - 学习时长（20%）：实际学习时长 / 目标时长
 * - 连续天数（10%）：连续学习天数 / 7天
 * 
 * 计算公式：
 * progress = 0.4 * storyRate + 0.3 * questionRate + 0.2 * timeRate + 0.1 * streakRate
 * 
 * 特殊处理：
 * 1. 如果连续学习超过7天，额外加5%进度奖励
 * 2. 如果当天学习超过30分钟，额外加3%进度奖励
 * 3. 最终进度值限制在0-100之间
 */
fun calculateLearningProgress(stats: LearningStats): Float {
    // 计算各维度进度
    val storyRate = stats.completedStories.toFloat() / max(stats.totalStories, 1)
    val questionRate = stats.correctAnswers.toFloat() / max(stats.totalQuestions, 1)
    val timeRate = min(stats.todayMinutes.toFloat() / TARGET_DAILY_MINUTES, 1f)
    val streakRate = min(stats.streakDays.toFloat() / 7f, 1f)
    
    // 加权计算
    var progress = 0.4f * storyRate + 0.3f * questionRate + 0.2f * timeRate + 0.1f * streakRate
    
    // 连续学习奖励
    if (stats.streakDays >= 7) {
        progress += 0.05f
    }
    
    // 超时学习奖励
    if (stats.todayMinutes >= 30) {
        progress += 0.03f
    }
    
    // 限制范围
    return (progress * 100).coerceIn(0f, 100f)
}
```

### 4. UI交互注释

```kotlin
/**
 * 故事生成界面
 * 
 * 界面功能：
 * 让用户输入故事主题，生成个性化的AI故事
 * 
 * 交互流程：
 * 1. 用户进入界面，看到可爱的熊猫引导动画
 * 2. 用户在输入框输入想要的故事主题（如"恐龙"）
 * 3. 点击"生成故事"按钮，按钮变为不可点击状态
 * 4. 显示加载动画（旋转的熊猫）和提示文字"小熊猫正在创作..."
 * 5. 生成成功后，自动跳转到故事阅读页面
 * 6. 生成失败时，显示友好的错误提示，按钮恢复可点击
 * 
 * UI状态说明：
 * - Idle: 初始状态，等待用户输入
 * - Loading: 正在生成故事，显示加载动画
 * - Success: 生成成功，准备跳转
 * - Error: 生成失败，显示错误信息
 * 
 * 设计要点：
 * 1. 输入框使用大字体（24sp），方便儿童识别
 * 2. 按钮采用鲜艳颜色和大尺寸（高度64dp）
 * 3. 加载动画要有趣，保持儿童注意力
 * 4. 错误提示要友好，不能让儿童感到挫败
 * 
 * 无障碍支持：
 * - 所有可交互元素都有contentDescription
 * - 支持TalkBack朗读
 * - 最小触摸目标48dp
 * 
 * @param viewModel 故事生成的ViewModel
 * @param onStoryGenerated 故事生成成功的回调
 * @param onBack 返回按钮的回调
 */
@Composable
fun StoryGenerateScreen(
    viewModel: StoryViewModel = hiltViewModel(),
    onStoryGenerated: (Story) -> Unit,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // 顶部导航栏
        TopBar(
            title = "创作故事",
            onBack = onBack
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // 熊猫引导动画
        PandaAnimation(
            mood = when (uiState) {
                is StoryUiState.Loading -> "thinking"  // 思考中的表情
                is StoryUiState.Error -> "sad"         // 失败时难过
                is StoryUiState.Success -> "happy"     // 成功时开心
                else -> "neutral"                      // 默认表情
            }
        )
        
        // ... 其他UI组件
    }
}
```

### 5. 业务规则注释

```kotlin
/**
 * 验证故事主题的合法性
 * 
 * 业务规则：
 * 1. 主题不能为空
 * 2. 主题长度限制2-10个字符
 * 3. 不能包含敏感词汇
 * 4. 必须是支持的主题类型
 * 
 * 敏感词过滤：
 * - 暴力相关词汇
 * - 不适合儿童的内容
 * - 政治敏感内容
 * 
 * 支持的主题（会定期更新）：
 * - 动物世界：恐龙、熊猫、兔子、大象、老虎等
 * - 童话故事：公主、王子、城堡、魔法、精灵等  
 * - 科学探索：太空、星星、机器人、发明家等
 * - 日常生活：上学、玩耍、朋友、家庭、节日等
 * 
 * @param topic 用户输入的主题
 * @throws IllegalArgumentException 当主题不符合规则时
 * 
 * 扩展说明：
 * 如需添加新的主题类型，请：
 * 1. 在SUPPORTED_TOPICS中添加新主题
 * 2. 在对应的AI提示词模板中添加新类型
 * 3. 更新用户界面的主题推荐列表
 */
private fun validateTopic(topic: String) {
    // 规则1: 非空检查
    require(topic.isNotBlank()) { 
        "主题不能为空，请输入你想听的故事主题" 
    }
    
    // 规则2: 长度检查
    require(topic.length in 2..10) { 
        "主题长度需要在2-10个字之间" 
    }
    
    // 规则3: 敏感词检查
    require(!containsSensitiveWords(topic)) { 
        "这个主题不太适合，换一个试试吧" 
    }
    
    // 规则4: 主题类型检查（可选，宽松模式）
    if (STRICT_MODE) {
        require(isTopicSupported(topic)) { 
            "暂时还不支持这个主题，试试其他的吧" 
        }
    }
}
```

### 6. 配置和常量注释

```kotlin
/**
 * AI服务配置
 * 
 * 配置说明：
 * 管理所有AI模型的配置信息，包括API地址、密钥、超时时间等
 * 
 * 环境说明：
 * - 开发环境：使用测试API，有调用次数限制
 * - 生产环境：使用正式API，需要计费
 * 
 * 安全说明：
 * - API密钥通过环境变量注入，不要硬编码
 * - 所有密钥都需要加密存储
 * - 定期轮换密钥，提高安全性
 */
object AIModelConfig {
    /**
     * 主AI模型 - GEMINI-2.5-PRO
     * 
     * 特点：
     * - 响应速度快（1-3秒）
     * - 创造力强，故事生动
     * - 支持多语言
     * - 价格适中
     * 
     * 限制：
     * - 每分钟60次调用
     * - 每次最多2000字输出
     * - 需要付费订阅
     */
    const val PRIMARY_MODEL = "GEMINI-2.5-PRO"
    const val PRIMARY_API_URL = BuildConfig.GEMINI_API_URL
    const val PRIMARY_API_KEY = BuildConfig.GEMINI_API_KEY
    
    /**
     * 备用AI模型 - GPT-5-PRO
     * 
     * 使用场景：
     * - 主模型故障时自动切换
     * - 需要更高质量输出时
     * - 特定主题的优化处理
     * 
     * 注意：
     * - 成本较高，谨慎使用
     * - 响应时间3-5秒
     */
    const val FALLBACK_MODEL = "GPT-5-PRO"
    const val FALLBACK_API_URL = BuildConfig.GPT_API_URL
    const val FALLBACK_API_KEY = BuildConfig.GPT_API_KEY
    
    /**
     * 超时配置
     * 
     * 经验值：
     * - 正常网络：5秒足够
     * - 弱网环境：需要15-30秒
     * - 用户可接受等待：最多30秒
     */
    const val CONNECTION_TIMEOUT = 30_000L  // 连接超时：30秒
    const val READ_TIMEOUT = 30_000L        // 读取超时：30秒
    const val WRITE_TIMEOUT = 30_000L       // 写入超时：30秒
    
    /**
     * 重试策略
     * 
     * 策略说明：
     * - 网络错误：重试3次
     * - 服务器错误（5xx）：重试2次  
     * - 客户端错误（4xx）：不重试
     * - 使用指数退避算法
     */
    const val MAX_RETRY_COUNT = 3
    const val INITIAL_RETRY_DELAY = 1000L   // 首次重试延迟：1秒
    const val MAX_RETRY_DELAY = 10000L      // 最大重试延迟：10秒
}
```

## 注释模板

### 1. 新功能开发模板
```kotlin
/**
 * [功能名称]
 * 
 * 功能概述：
 * [一句话说明这个功能做什么]
 * 
 * 业务背景：
 * [为什么需要这个功能]
 * 
 * 实现方案：
 * [简述技术实现方案]
 * 
 * 注意事项：
 * [使用时需要注意什么]
 * 
 * @author [你的名字]
 * @since [版本号]
 */
```

### 2. Bug修复模板
```kotlin
/**
 * 修复：[问题描述]
 * 
 * 问题原因：
 * [导致bug的根本原因]
 * 
 * 解决方案：
 * [如何修复的]
 * 
 * 影响范围：
 * [这个修复会影响哪些功能]
 * 
 * @fixedBy [你的名字]
 * @date [修复日期]
 * @issue [Issue编号]
 */
```

### 3. 性能优化模板
```kotlin
/**
 * 性能优化：[优化点]
 * 
 * 优化前：
 * - 性能指标：[具体数据]
 * - 存在问题：[性能瓶颈]
 * 
 * 优化后：
 * - 性能指标：[具体数据]
 * - 提升效果：[提升百分比]
 * 
 * 优化方案：
 * [具体的优化措施]
 * 
 * @optimizedBy [你的名字]
 * @date [优化日期]
 */
```

## 注释检查工具

### 1. 自动检查脚本
```bash
#!/bin/bash
# check-comments.sh

echo "🔍 检查代码注释覆盖率..."

# 检查类注释
echo -n "检查类注释... "
CLASS_COUNT=$(find app/src/main -name "*.kt" -exec grep -l "^class\|^interface" {} \; | wc -l)
CLASS_WITH_COMMENT=$(find app/src/main -name "*.kt" -exec grep -B5 "^class\|^interface" {} \; | grep -c "^\*/")
echo "$CLASS_WITH_COMMENT/$CLASS_COUNT 个类有注释"

# 检查复杂方法注释
echo -n "检查方法注释... "
COMPLEX_METHOD=$(find app/src/main -name "*.kt" -exec awk '/fun/{p=1} p&&/{/{c++} p&&/}/{c--; if(c==0){if(NR-s>10)print FILENAME":"s"-"NR; p=0}} p&&!s{s=NR}' {} \; | wc -l)
echo "发现 $COMPLEX_METHOD 个复杂方法需要注释"

# 检查TODO项
echo -n "检查TODO项... "
TODO_COUNT=$(grep -r "TODO\|FIXME" app/src/main --include="*.kt" | wc -l)
echo "发现 $TODO_COUNT 个TODO项"

# 生成报告
echo ""
echo "📊 注释覆盖率报告"
echo "=================="
COVERAGE=$((CLASS_WITH_COMMENT * 100 / CLASS_COUNT))
echo "类注释覆盖率: $COVERAGE%"

if [ $COVERAGE -lt 80 ]; then
    echo "❌ 注释覆盖率低于80%，请补充注释"
    exit 1
else
    echo "✅ 注释覆盖率达标"
fi
```

### 2. IDE配置

```xml
<!-- .idea/inspectionProfiles/Project_Default.xml -->
<component name="InspectionProjectProfileManager">
  <profile version="1.0">
    <option name="myName" value="Project Default" />
    
    <!-- 强制要求类注释 -->
    <inspection_tool class="KDocMissingDocumentation" enabled="true" level="WARNING" enabled_by_default="true">
      <option name="CHECK_CLASSES" value="true" />
      <option name="CHECK_METHODS" value="true" />
      <option name="CHECK_PROPERTIES" value="false" />
      <option name="IGNORE_DEPRECATED" value="true" />
    </inspection_tool>
    
    <!-- 检查注释质量 -->
    <inspection_tool class="CommentQuality" enabled="true" level="WARNING" enabled_by_default="true">
      <option name="MIN_COMMENT_LENGTH" value="10" />
      <option name="CHECK_CHINESE" value="true" />
    </inspection_tool>
  </profile>
</component>
```

## 最佳实践

### DO ✅
1. **写给未来的自己**：假设6个月后的你完全忘记了这段代码
2. **解释为什么**：不仅说明做什么，更要说明为什么这样做
3. **保持更新**：代码修改时同步更新注释
4. **使用中文**：业务逻辑用中文表达更清晰
5. **添加示例**：复杂功能提供使用示例

### DON'T ❌
1. **废话注释**：`// 获取用户` getUserInfo() 
2. **过时注释**：注释和代码不一致
3. **注释代码**：用版本控制，不要注释掉代码
4. **英文装逼**：明明中文更清楚非要用英文
5. **敷衍了事**：写个"临时方案"就完了

## 注释质量评分标准

### 整体评分框架（100分制）

#### 1. 类/接口注释覆盖率（35分）
**核心原则**：核心功能类必须100%注释覆盖

**权重分配**：
- **Domain层**（权重1.5）
  - UseCase类：业务逻辑核心，必须详细注释
  - Repository接口：数据契约定义，必须清晰
  - Model类：领域模型，必须说明业务含义

- **Presentation层**（权重1.3）
  - ViewModel：UI逻辑中心，必须完整注释
  - 核心Screen：用户交互界面，必须说明交互流程
  - State类：状态管理，必须说明各状态含义

- **Data层**（权重1.2）
  - RepositoryImpl：数据实现，必须说明策略
  - Manager类：系统管理器，必须说明职责
  - Entity/DAO：数据结构，必须说明字段

- **其他辅助类**（权重1.0）
  - Utils/Helper：工具类，基本注释即可
  - Constants：常量类，说明用途即可

- **测试类**（权重0.5）
  - 单元测试：简要说明测试目的
  - UI测试：说明测试场景

#### 2. 复杂方法注释（25分）
**复杂度判定标准**：
- 方法行数 > 20行
- 控制流语句（if/when/for/while/try）> 3个
- 业务逻辑关键路径（如支付、认证、数据同步）
- 算法实现（如推荐算法、评分计算）

**注：测试方法不计入复杂方法统计**

#### 3. UI组件交互注释（20分）
**必须注释的交互**：
- 点击事件处理流程
- 手势交互（滑动、长按、拖拽）
- 状态变化触发条件
- 动画效果说明
- 无障碍支持说明

#### 4. 中文注释使用率（20分）
**分层要求**：
- Domain层：80%以上（16-20分）- 业务逻辑必须用中文
- Presentation层：70%以上（14-18分）- UI交互用中文说明
- Data层：60%以上（12-16分）- 数据策略用中文
- 测试类：40%以上（8-12分）- 测试意图用中文
- **整体平均：60%以上及格，80%以上优秀**

### 评分等级

| 总分 | 等级 | 标准 | 行动建议 |
|------|------|------|----------|
| 95-100 | A+ (卓越) | 生产级标准，可直接发布 | 保持标准，定期review |
| 90-94 | A (优秀) | 高质量代码，易于维护 | 补充个别遗漏即可 |
| 85-89 | B (良好) | 基本达标，略有不足 | 重点补充核心类注释 |
| 75-84 | C (及格) | 勉强可用，需要改进 | 系统性补充注释 |
| 60-74 | D (差) | 注释严重不足 | 立即整改，不可发布 |
| <60 | F (不及格) | 完全不符合标准 | 重新培训，全面整改 |

### 权重计算示例

```kotlin
// 示例1：Domain层UseCase（权重1.5）
class GenerateStoryUseCase {  // 缺少注释扣1.5分
    fun execute() { }
}

// 示例2：测试类（权重0.5）  
class StoryViewModelTest {    // 缺少注释仅扣0.5分
    fun testGenerate() { }
}

// 示例3：核心ViewModel（权重1.3）
class StoryViewModel {        // 缺少注释扣1.3分
    fun generateStory() { }   // 复杂方法缺少注释额外扣分
}
```

## 总结

> **记住：代码是写给人看的，顺便让机器执行。**
> 
> 好的注释能够：
> - 让新人1天上手，而不是1周
> - 让bug修复1小时完成，而不是1天
> - 让功能扩展顺利进行，而不是推倒重来
> 
> **投资注释，就是投资未来的开发效率！**

---

*注释规范版本：1.0*  
*强制执行，不是建议*  
*最后更新：2024年12月*