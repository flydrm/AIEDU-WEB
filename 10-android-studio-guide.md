# Android Studio操作指南SOP

## 目的
提供详细的Android Studio使用指南，包括项目运行、功能入口定位、调试技巧、问题修复和打包发布等操作规范。

## 1. 项目导入与配置

### 1.1 首次导入项目
```bash
# 1. 克隆项目
git clone https://github.com/company/ai-enlightenment-time.git
cd ai-enlightenment-time

# 2. 打开Android Studio
# File -> Open -> 选择项目根目录

# 3. 等待项目同步
# Android Studio会自动下载依赖，可能需要5-10分钟
```

### 1.2 环境配置检查
```kotlin
/**
 * 检查清单：
 * 1. JDK版本：11或17
 * 2. Gradle版本：8.1.1
 * 3. Android SDK：API 24-34
 * 4. Kotlin版本：1.9.x
 */

// 查看配置：File -> Project Structure
// - SDK Location: 检查Android SDK路径
// - Project: 检查Gradle和JDK版本
// - Modules: 检查编译SDK版本
```

### 1.3 配置文件设置
```properties
# local.properties (不要提交到Git)
sdk.dir=/Users/yourname/Library/Android/sdk
# API密钥配置
GEMINI_API_KEY=your_gemini_api_key_here
GPT_API_KEY=your_gpt_api_key_here

# gradle.properties
# 内存配置，提高构建速度
org.gradle.jvmargs=-Xmx4096m -XX:+UseParallelGC
org.gradle.parallel=true
org.gradle.caching=true
# 使用国内镜像
ALIYUN_MAVEN_URL=https://maven.aliyun.com/repository/public
```

## 2. 运行项目

### 2.1 运行配置
```kotlin
/**
 * 运行配置步骤：
 * 1. 点击顶部工具栏的设备选择器
 * 2. 选择模拟器或真机
 * 3. 点击绿色运行按钮（Shift+F10）
 * 
 * 推荐测试设备：
 * - 模拟器：Pixel 5 (API 31)
 * - 屏幕尺寸：用于测试手机适配
 * - 平板模拟器：Pixel C (API 31)
 * - 屏幕尺寸：用于测试平板适配
 */
```

### 2.2 创建模拟器
```
1. Tools -> AVD Manager
2. Create Virtual Device
3. 选择设备：
   - Phone -> Pixel 5 (适合测试手机)
   - Tablet -> Pixel C (适合测试平板)
4. 选择系统镜像：
   - API 31 (Android 12) - 推荐
   - 下载x86_64镜像以获得更好性能
5. 配置选项：
   - RAM: 2048MB
   - Internal Storage: 2048MB
   - 启用硬件加速
```

### 2.3 真机调试
```kotlin
/**
 * 真机调试设置：
 * 
 * 1. 手机端设置：
 *    - 设置 -> 关于手机 -> 连续点击"版本号"7次
 *    - 设置 -> 开发者选项 -> 启用"USB调试"
 * 
 * 2. 连接设备：
 *    - 使用USB线连接手机和电脑
 *    - 在手机上允许USB调试
 *    - Android Studio会自动识别设备
 * 
 * 3. 无线调试（Android 11+）：
 *    - 开发者选项 -> 无线调试
 *    - 使用配对码配对
 *    - adb connect 192.168.x.x:port
 */
```

## 3. 功能入口导航

### 3.1 应用架构概览
```kotlin
/**
 * AI启蒙时光 - 功能入口地图
 * 
 * MainActivity (主入口)
 *     │
 *     ├── HomeScreen (首页)
 *     │   ├── 故事生成入口 -> StoryScreen
 *     │   ├── 智能对话入口 -> DialogueScreen
 *     │   ├── 拍照识别入口 -> CameraScreen
 *     │   └── 个人中心入口 -> ProfileScreen
 *     │
 *     └── ParentLoginScreen (家长入口)
 *         └── ParentDashboardScreen
 *             ├── 学习报告
 *             ├── 时间限制设置
 *             ├── 内容偏好设置
 *             └── 隐私设置
 */
```

### 3.2 快速定位功能代码
```kotlin
// 使用Android Studio快捷键快速定位：

// 1. 查找类（Cmd+O / Ctrl+N）
"StoryScreen" -> 故事界面
"DialogueScreen" -> 对话界面
"CameraScreen" -> 相机界面

// 2. 查找文件（Cmd+Shift+O / Ctrl+Shift+N）
"navigation" -> 导航配置
"theme" -> 主题配置

// 3. 全局搜索（Cmd+Shift+F / Ctrl+Shift+F）
"generateStory" -> 故事生成功能
"sendMessage" -> 对话发送功能
"captureImage" -> 拍照功能

// 4. 查找使用（Cmd+B / Ctrl+B）
// 在函数名上使用，查看所有调用位置
```

### 3.3 导航结构代码
```kotlin
/**
 * 导航配置文件位置：
 * app/src/main/java/com/enlightenment/ai/presentation/navigation/EnlightenmentNavHost.kt
 * 
 * 添加新页面步骤：
 * 1. 创建Screen组件
 * 2. 在Screen sealed class中添加路由
 * 3. 在NavHost中添加composable
 * 4. 在相应位置添加导航调用
 */

// 示例：添加新功能页面
sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Story : Screen("story/{storyId}")  // 带参数路由
    object NewFeature : Screen("new_feature")  // 新增功能
}

// NavHost中添加
composable(Screen.NewFeature.route) {
    NewFeatureScreen(
        onBack = { navController.popBackStack() }
    )
}
```

## 4. 调试技巧

### 4.1 断点调试
```kotlin
/**
 * 设置断点：
 * 1. 在代码行号左侧点击设置断点（红点）
 * 2. 点击Debug按钮运行（Shift+F9）
 * 3. 程序会在断点处暂停
 * 
 * 调试窗口功能：
 * - Variables: 查看当前变量值
 * - Watches: 监视特定表达式
 * - Call Stack: 查看调用栈
 * - Evaluate: 实时执行代码
 */

// 常用调试场景示例
fun generateStory(topic: String) {
    // 在这里设置断点，检查输入参数
    viewModelScope.launch {
        try {
            // 在这里设置断点，检查网络请求前的状态
            val result = storyUseCase(topic)
            
            // 在这里设置断点，检查返回结果
            result.onSuccess { story ->
                // 检查story对象的内容
                _uiState.value = UiState.Success(story)
            }
        } catch (e: Exception) {
            // 在这里设置断点，检查异常信息
            Timber.e(e, "Story generation failed")
        }
    }
}
```

### 4.2 日志调试
```kotlin
/**
 * 使用Timber进行日志输出
 * 
 * 日志级别：
 * - Timber.v() : Verbose (最详细)
 * - Timber.d() : Debug (调试信息)
 * - Timber.i() : Info (一般信息)
 * - Timber.w() : Warning (警告)
 * - Timber.e() : Error (错误)
 */

// 在关键位置添加日志
class StoryViewModel : ViewModel() {
    init {
        Timber.d("StoryViewModel初始化")
    }
    
    fun generateStory(topic: String) {
        Timber.d("开始生成故事，主题：$topic")
        
        viewModelScope.launch {
            try {
                Timber.d("调用API前，检查网络状态")
                val result = storyUseCase(topic)
                
                Timber.d("API调用完成，结果：${result.isSuccess}")
            } catch (e: Exception) {
                Timber.e(e, "生成故事失败")
            }
        }
    }
}

/**
 * 查看日志：
 * 1. 打开Logcat窗口（View -> Tool Windows -> Logcat）
 * 2. 选择设备和应用包名
 * 3. 使用过滤器：
 *    - 包名过滤：package:com.enlightenment.ai
 *    - 标签过滤：tag:StoryViewModel
 *    - 级别过滤：level:error
 */
```

### 4.3 Layout Inspector
```kotlin
/**
 * UI调试神器 - Layout Inspector
 * 
 * 使用步骤：
 * 1. 运行应用到目标界面
 * 2. Tools -> Layout Inspector
 * 3. 选择进程：com.enlightenment.ai
 * 
 * 功能：
 * - 3D视图查看层级
 * - 查看每个组件的属性
 * - 实时更新UI变化
 * - 导出视图层级
 */

// 常见UI问题调试
@Composable
fun ProblematicScreen() {
    // 使用Modifier.border调试布局边界
    Box(
        modifier = Modifier
            .fillMaxSize()
            .border(2.dp, Color.Red)  // 调试时添加边框
    ) {
        // 内容
    }
}
```

### 4.4 性能调试
```kotlin
/**
 * 性能分析工具
 * 
 * 1. CPU Profiler
 *    - View -> Tool Windows -> Profiler
 *    - 选择CPU时间线
 *    - Record开始记录
 *    - 执行要分析的操作
 *    - Stop停止记录
 * 
 * 2. Memory Profiler
 *    - 监控内存使用
 *    - 捕获堆转储
 *    - 分析内存泄漏
 * 
 * 3. Network Profiler
 *    - 监控网络请求
 *    - 查看请求详情
 *    - 分析响应时间
 */

// 代码中添加性能追踪
class PerformanceTracker {
    inline fun <T> measureTime(
        tag: String,
        block: () -> T
    ): T {
        val start = System.currentTimeMillis()
        val result = block()
        val duration = System.currentTimeMillis() - start
        Timber.d("$tag 耗时: ${duration}ms")
        return result
    }
}

// 使用示例
val story = performanceTracker.measureTime("生成故事") {
    storyRepository.generateStory(topic)
}
```

## 5. 常见问题修复

### 5.1 构建错误修复
```kotlin
/**
 * 常见构建错误及解决方案
 */

// 1. 依赖冲突
// 错误：Duplicate class found
// 解决：在app/build.gradle.kts中排除冲突
implementation("com.example:library:1.0") {
    exclude(group = "com.conflict", module = "module")
}

// 2. 版本不兼容
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
```kotlin
/**
 * 运行时错误调试步骤
 */

// 1. 空指针异常（NullPointerException）
// 查看堆栈跟踪，定位具体行
// 使用安全调用操作符
data?.let { 
    // 安全使用data
} ?: run {
    // 处理null情况
}

// 2. 类型转换异常（ClassCastException）
// 使用安全类型转换
val result = data as? ExpectedType
if (result != null) {
    // 使用result
}

// 3. 并发修改异常（ConcurrentModificationException）
// 使用线程安全的集合
val safeList = Collections.synchronizedList(mutableListOf<Item>())
// 或使用协程的通道
val channel = Channel<Item>()
```

### 5.3 UI问题修复
```kotlin
/**
 * 常见UI问题及解决方案
 */

// 1. Compose预览不工作
@Preview(showBackground = true)
@Composable
fun StoryScreenPreview() {
    // 提供mock数据
    AIEnlightenmentTheme {
        StoryScreen(
            uiState = StoryUiState(
                story = Story(
                    id = "1",
                    title = "预览故事",
                    content = "这是预览内容"
                )
            )
        )
    }
}

// 2. 主题不生效
// 确保在最外层包裹主题
setContent {
    AIEnlightenmentTheme {  // 必须包裹主题
        Surface {
            MainNavigation()
        }
    }
}

// 3. 键盘遮挡输入框
// 在AndroidManifest.xml中设置
<activity
    android:name=".MainActivity"
    android:windowSoftInputMode="adjustResize">
</activity>
```

## 6. 打包发布

### 6.1 签名配置
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            // 使用环境变量保护密钥
            storeFile = file(System.getenv("KEYSTORE_FILE") ?: "keystore.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }
    
    buildTypes {
        release {
            isMinifyEnabled = true  // 启用代码混淆
            isShrinkResources = true  // 移除未使用的资源
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

### 6.2 混淆规则
```proguard
# proguard-rules.pro

# 保留实体类
-keep class com.enlightenment.ai.domain.model.** { *; }

# 保留Hilt相关
-keep class dagger.hilt.** { *; }
-keep class javax.inject.** { *; }

# 保留Retrofit接口
-keep interface com.enlightenment.ai.data.remote.api.** { *; }

# Gson
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.google.gson.** { *; }

# 保留自定义View
-keep class com.enlightenment.ai.presentation.common.** { *; }
```

### 6.3 构建APK/AAB
```bash
# 构建APK
./gradlew assembleRelease
# 输出位置：app/build/outputs/apk/release/app-release.apk

# 构建AAB（推荐用于Google Play）
./gradlew bundleRelease
# 输出位置：app/build/outputs/bundle/release/app-release.aab

# 查看APK信息
# Build -> Analyze APK -> 选择APK文件
# 可以查看：
# - APK大小分析
# - DEX文件内容
# - 资源文件
# - 签名信息
```

### 6.4 多渠道打包
```kotlin
// app/build.gradle.kts
android {
    flavorDimensions += "channel"
    productFlavors {
        create("googleplay") {
            dimension = "channel"
            applicationIdSuffix = ".gp"
            versionNameSuffix = "-GP"
            buildConfigField("String", "CHANNEL", "\"GooglePlay\"")
        }
        create("huawei") {
            dimension = "channel"
            applicationIdSuffix = ".hw"
            versionNameSuffix = "-HW"
            buildConfigField("String", "CHANNEL", "\"Huawei\"")
        }
    }
}

// 构建特定渠道
./gradlew assembleGoogleplayRelease
./gradlew assembleHuaweiRelease
```

## 7. 版本管理

### 7.1 版本号规范
```kotlin
// app/build.gradle.kts
android {
    defaultConfig {
        // 版本号规范：主版本.次版本.修订号
        versionCode = 10203  // 1.2.3 -> 10203
        versionName = "1.2.3"
        
        // 根据Git信息自动生成版本
        val gitCommitCount = "git rev-list --count HEAD".execute()
        versionCode = gitCommitCount.toIntOrNull() ?: 1
        
        val gitTag = "git describe --tags --abbrev=0".execute()
        versionName = gitTag.ifEmpty { "1.0.0" }
    }
}

// 扩展函数执行命令
fun String.execute(): String {
    return try {
        ProcessBuilder(*split(" ").toTypedArray())
            .redirectOutput(ProcessBuilder.Redirect.PIPE)
            .redirectError(ProcessBuilder.Redirect.PIPE)
            .start()
            .inputStream.bufferedReader().readText().trim()
    } catch (e: Exception) {
        ""
    }
}
```

### 7.2 发布检查清单
```kotlin
/**
 * 发布前检查清单
 * 
 * 代码质量：
 * □ 运行所有单元测试：./gradlew test
 * □ 运行UI测试：./gradlew connectedAndroidTest
 * □ 代码静态检查：./gradlew lint
 * □ 检查TODO项：grep -r "TODO" app/src
 * 
 * 功能验证：
 * □ 核心功能正常
 * □ 异常处理完善
 * □ 离线功能可用
 * □ 权限申请正常
 * 
 * 性能检查：
 * □ 启动时间 < 3秒
 * □ 内存使用 < 150MB
 * □ 无内存泄漏
 * □ APK大小合理
 * 
 * 发布材料：
 * □ 更新版本号
 * □ 更新发布日志
 * □ 准备商店截图
 * □ 更新隐私政策
 */
```

## 8. 团队协作

### 8.1 代码规范检查
```bash
# 配置pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
echo "Running code quality checks..."

# Kotlin格式检查
./gradlew ktlintCheck
if [ $? -ne 0 ]; then
    echo "Kotlin代码格式有问题，请运行 ./gradlew ktlintFormat"
    exit 1
fi

# 注释检查
./docs/sop/project/scripts/check-comments.sh
if [ $? -ne 0 ]; then
    echo "代码注释不足，请补充注释"
    exit 1
fi

echo "All checks passed!"
EOF

chmod +x .git/hooks/pre-commit
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