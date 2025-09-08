# 发布流程SOP

## 目的
建立标准化的发布流程，确保每次发布都安全、可靠、可追溯。

## 发布流程概览

```mermaid
graph LR
    A[版本规划] --> B[功能冻结]
    B --> C[测试验证]
    C --> D[发布准备]
    D --> E[灰度发布]
    E --> F[全量发布]
    F --> G[发布监控]
    G --> H[发布总结]
```

## 1. 版本规划

### 1.1 版本号规范
```
主版本号.次版本号.修订号 (Major.Minor.Patch)

示例：
- 1.0.0：首次发布
- 1.1.0：新增功能
- 1.1.1：Bug修复
- 2.0.0：重大更新
```

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
- 保留上个版本APK
- 数据库降级脚本准备
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

# 更新版本号
# app/build.gradle.kts
versionCode = 120
versionName = "1.2.0"

# 提交版本号更改
git add .
git commit -m "chore: bump version to 1.2.0"
git push origin release/1.2.0
```

## 3. 测试验证

### 3.1 测试清单
```markdown
## 功能测试
- [ ] 新功能测试完成
- [ ] 回归测试通过
- [ ] 边界条件测试
- [ ] 异常场景测试

## 兼容性测试
- [ ] Android 7.0 (API 24)
- [ ] Android 8.0 (API 26)
- [ ] Android 10 (API 29)
- [ ] Android 12 (API 31)
- [ ] Android 14 (API 34)

## 设备测试
- [ ] 小屏手机 (5.0")
- [ ] 普通手机 (6.0")
- [ ] 大屏手机 (6.7")
- [ ] 平板 (10")

## 性能测试
- [ ] 启动时间 < 3秒
- [ ] 内存使用 < 150MB
- [ ] 无ANR问题
- [ ] 电池消耗正常
```

### 3.2 自动化测试
```bash
# 运行所有测试
./gradlew test
./gradlew connectedAndroidTest

# 生成测试报告
./gradlew jacocoTestReport

# 检查测试覆盖率
./gradlew jacocoTestCoverageVerification
```

## 4. 发布准备

### 4.1 构建发布版本
```bash
# 清理构建
./gradlew clean

# 构建Release APK
./gradlew assembleRelease

# 构建App Bundle
./gradlew bundleRelease
```

### 4.2 签名配置
```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_FILE") ?: "keystore.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }
    
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### 4.3 混淆配置
```proguard
# proguard-rules.pro

# 保留实体类
-keep class com.enlightenment.ai.domain.model.** { *; }

# 保留API接口
-keep interface com.enlightenment.ai.data.remote.api.** { *; }

# Gson
-keepattributes Signature
-keepattributes *Annotation*
-keep class sun.misc.Unsafe { *; }

# Retrofit
-keepattributes RuntimeVisibleAnnotations
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}
```

### 4.4 发布材料准备
```markdown
## 应用商店材料
- [ ] 应用图标 (512x512)
- [ ] 功能图 (1024x500)
- [ ] 截图 (手机5张+平板2张)
- [ ] 应用描述 (简短+详细)
- [ ] 更新说明
- [ ] 隐私政策链接
- [ ] 年龄分级

## 内部材料
- [ ] 发布说明文档
- [ ] 测试报告
- [ ] 已知问题列表
- [ ] 回滚方案
```

## 5. 灰度发布

### 5.1 灰度策略
```markdown
## 阶段式发布
1. 内部测试 (100人)
   - 公司员工
   - 持续2天
   
2. 小范围灰度 (5%)
   - 种子用户
   - 持续3天
   
3. 中等灰度 (20%)
   - 活跃用户
   - 持续3天
   
4. 大范围灰度 (50%)
   - 一般用户
   - 持续2天
   
5. 全量发布 (100%)
   - 所有用户
```

### 5.2 监控指标
```kotlin
// 关键监控指标
data class ReleaseMetrics(
    val crashRate: Float,        // 崩溃率 < 0.1%
    val anrRate: Float,          // ANR率 < 0.05%
    val startupTime: Long,       // 启动时间 < 3s
    val memoryUsage: Int,        // 内存使用 < 150MB
    val retentionRate: Float,    // 留存率 > 80%
    val userRating: Float        // 用户评分 > 4.0
)
```

### 5.3 灰度控制
```kotlin
// 远程配置灰度开关
class RemoteConfig {
    fun isFeatureEnabled(feature: String, userId: String): Boolean {
        val rolloutPercentage = getFeatureRollout(feature)
        val userBucket = userId.hashCode() % 100
        return userBucket < rolloutPercentage
    }
}
```

## 6. 全量发布

### 6.1 发布前检查
- [ ] 灰度数据正常
- [ ] 无严重bug反馈
- [ ] 性能指标达标
- [ ] 后端服务就绪
- [ ] 客服团队准备

### 6.2 发布操作
```bash
# Google Play Console
1. 登录 https://play.google.com/console
2. 选择应用
3. 版本管理 > 应用版本
4. 上传APK/AAB
5. 填写版本说明
6. 提交审核

# 国内应用商店
- 华为应用市场
- 小米应用商店
- OPPO软件商店
- VIVO应用商店
- 应用宝
```

### 6.3 发布通知
```markdown
## 发布通知模板

**主题**: AI启蒙时光 v1.2.0 已发布

各位同事：

AI启蒙时光 v1.2.0 已于 2024-01-15 15:00 正式发布。

**主要更新**：
1. 优化智能对话体验
2. 新增10个故事主题
3. 修复已知问题

**发布渠道**：
- Google Play：已上线
- 华为应用市场：审核中
- 其他商店：陆续上线

**注意事项**：
- 请关注用户反馈
- 如有问题及时上报
- 保持手机畅通

技术支持：张三 (13800138000)
产品负责：李四 (13900139000)
```

## 7. 发布监控

### 7.1 实时监控
```kotlin
// Crashlytics监控
FirebaseCrashlytics.getInstance().apply {
    setCustomKey("version", BuildConfig.VERSION_NAME)
    setCustomKey("release_date", "2024-01-15")
    setUserId(userId)
}

// Performance监控
FirebasePerformance.getInstance().apply {
    isPerformanceCollectionEnabled = true
    newTrace("app_startup").apply {
        start()
        // 启动逻辑
        stop()
    }
}
```

### 7.2 监控仪表板
```markdown
## 发布后24小时监控

### 崩溃监控
- 崩溃率：0.08% ✅ (目标<0.1%)
- 影响用户：1,234
- 主要崩溃：NullPointerException in StoryActivity

### 性能监控
- 启动时间：2.3s ✅
- 内存使用：132MB ✅
- 网络成功率：98.5% ✅

### 用户反馈
- Play Store评分：4.3 ✅
- 负面评论：23条
- 主要问题：加载慢、闪退

### 业务指标
- DAU：45,678 (+5%)
- 使用时长：18分钟 (+10%)
- 付费转化：2.3% (+0.5%)
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
# v1.2.0 发布总结报告

## 发布概况
- 版本号：1.2.0
- 发布日期：2024-01-15
- 发布范围：全量用户
- 影响用户：100万+

## 关键指标
| 指标 | 目标 | 实际 | 结果 |
|------|------|------|------|
| 崩溃率 | <0.1% | 0.08% | ✅ |
| 启动时间 | <3s | 2.3s | ✅ |
| 用户评分 | >4.0 | 4.3 | ✅ |

## 主要问题
1. **问题**：部分用户反馈加载慢
   **原因**：CDN节点问题
   **解决**：优化CDN配置

2. **问题**：StoryActivity偶现崩溃
   **原因**：并发访问问题
   **解决**：已hotfix修复

## 经验教训
1. 灰度发布发现问题及时
2. 监控系统运行良好
3. 需要加强性能测试

## 下版本改进
1. 增加自动化测试覆盖
2. 优化发布流程文档
3. 建立快速响应机制
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
# Google Play回滚
1. 进入版本管理
2. 选择之前的稳定版本
3. 点击"推广此版本"
4. 确认回滚

# 通知用户
推送通知："检测到问题，建议暂不更新"
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

*基于AI启蒙时光项目发布经验*  
*确保每次发布都平稳可靠*