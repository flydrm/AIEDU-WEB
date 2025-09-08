# 代码审查SOP

## 目的
建立标准化的代码审查流程，提高代码质量，促进知识共享，减少缺陷。

## 代码审查原则

### 1. 基本原则
- **建设性**: 提供有建设性的反馈，不攻击个人
- **具体性**: 指出具体问题和改进建议
- **及时性**: 24小时内完成review
- **学习性**: 把review当作学习机会
- **务实性**: 关注实际问题，不纠结风格

## 审查流程

### 1. 提交代码审查

#### 1.1 自查清单
```markdown
提交PR前，请确认：
- [ ] 代码已自测通过
- [ ] 符合编码规范
- [ ] 添加必要注释
- [ ] 更新相关文档
- [ ] 通过CI检查
```

#### 1.2 PR描述规范
```markdown
## 概述
简述这个PR的目的和主要改动

## 改动内容
- 功能1：具体说明
- 功能2：具体说明
- 修复：具体问题

## 测试说明
- 如何测试
- 测试结果
- 边界条件

## 风险评估
- 可能的影响
- 兼容性考虑
- 性能影响

## 截图/录屏（如涉及UI）
[添加相关截图]

## 相关链接
- Issue: #123
- 设计稿: [链接]
- 需求文档: [链接]
```

### 2. 执行代码审查

#### 2.1 审查重点

##### 功能正确性
```kotlin
// ❌ 错误示例：可能的空指针
fun processData(data: String?) {
    val length = data.length  // 可能崩溃
}

// ✅ 正确示例：空安全处理
fun processData(data: String?) {
    val length = data?.length ?: 0
}
```

##### 代码质量
```kotlin
// ❌ 错误示例：过长的函数
fun processUserData() {
    // 100行代码...
}

// ✅ 正确示例：合理拆分
fun processUserData() {
    validateUser()
    updateProfile()
    sendNotification()
}

private fun validateUser() { /* ... */ }
private fun updateProfile() { /* ... */ }
private fun sendNotification() { /* ... */ }
```

##### 性能问题
```kotlin
// ❌ 错误示例：主线程IO操作
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val data = readFromFile()  // 阻塞主线程
    }
}

// ✅ 正确示例：异步处理
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch(Dispatchers.IO) {
            val data = readFromFile()
            withContext(Dispatchers.Main) {
                updateUI(data)
            }
        }
    }
}
```

##### 安全问题
```kotlin
// ❌ 错误示例：硬编码敏感信息
class ApiService {
    private val apiKey = "sk-1234567890"  // 安全风险
}

// ✅ 正确示例：从安全存储读取
class ApiService {
    private val apiKey = BuildConfig.API_KEY
}
```

#### 2.2 审查清单

```markdown
## 代码审查清单

### 🔴 注释质量（最高优先级）
- [ ] 所有类都有完整的类注释
- [ ] 复杂方法都有详细的中文注释
- [ ] 业务逻辑都有流程说明
- [ ] 交互流程都有步骤描述
- [ ] 异常处理都有原因说明
- [ ] 算法实现都有思路讲解
- [ ] 二次开发指南完整

### 功能性
- [ ] 功能实现正确
- [ ] 边界条件处理
- [ ] 异常处理完善
- [ ] 无逻辑错误

### 可维护性
- [ ] 代码易读易懂
- [ ] 注释完整准确
- [ ] 合理的命名
- [ ] 模块化设计

### 性能
- [ ] 无明显性能问题
- [ ] 合理的算法选择
- [ ] 避免内存泄漏
- [ ] 异步处理恰当

### 安全性
- [ ] 无安全漏洞
- [ ] 数据验证完整
- [ ] 权限检查正确
- [ ] 敏感信息保护

### 测试
- [ ] 测试覆盖充分
- [ ] 测试用例合理
- [ ] 边界条件测试
- [ ] 异常场景测试

### 规范性
- [ ] 符合编码规范
- [ ] 符合架构设计
- [ ] 依赖管理合理
- [ ] 文档更新同步
```

### 3. 反馈方式

#### 3.1 评论规范

##### 🔴 注释相关的反馈（优先处理）
```markdown
// 缺少注释
📝 **必须修复**: 这个复杂的算法逻辑需要添加详细的中文注释，说明实现思路和步骤。

// 注释不清晰
📝 **建议改进**: 这里的注释太简单了，建议补充：
1. 为什么要这样处理
2. 有什么注意事项
3. 后续如何扩展

// 缺少交互说明
📝 **必须修复**: UI交互流程需要完整注释，包括：
- 用户操作步骤
- 各种状态的处理
- 异常情况的反馈
```

##### 提出问题
```markdown
// 建设性的评论
❓ **Question**: 这里为什么使用同步方式？是否考虑过异步处理？建议在注释中说明原因。

// 而不是
这代码有问题。
```

##### 建议改进
```markdown
// 具体的建议
💡 **Suggestion**: 建议将这个方法拆分成更小的函数，提高可读性：
```kotlin
fun processData() {
    val validated = validateData()
    val transformed = transformData(validated)
    saveData(transformed)
}
```

// 而不是
代码太长了。
```

##### 指出问题
```markdown
// 明确的问题说明
🐛 **Issue**: 这里可能存在空指针异常，建议添加空检查：
```kotlin
data?.let { 
    processData(it) 
} ?: handleEmptyData()
```

// 而不是
有bug。
```

##### 表扬优点
```markdown
// 认可好的实践
👍 **Good**: 很好的错误处理方式，考虑了各种异常情况！

// 学习借鉴
📚 **Learning**: 学到了，原来协程可以这样优雅地处理并发！
```

#### 3.2 评论标记

使用标准标记帮助区分评论性质：

- **[必须修改]**: 必须修改才能合并
- **[建议修改]**: 强烈建议但不强制
- **[讨论]**: 需要讨论的设计问题
- **[疑问]**: 不理解需要解释
- **[学习]**: 学到的好方法

### 4. 响应审查

#### 4.1 回应规范

```markdown
// 接受建议
✅ 已修改，确实这样更清晰，谢谢！

// 解释原因
💭 这里使用同步是因为需要保证数据一致性，已添加注释说明。

// 提出不同意见
🤔 我理解您的担心，但这里这样做是因为...，您觉得如何？

// 需要帮助
❓ 不太明白这个建议，能详细说明一下吗？
```

#### 4.2 修改追踪

```bash
# 标记已解决的评论
git commit -m "fix: 解决PR评论中的空指针问题"

# 批量响应
感谢review！已按建议修改：
- ✅ 修复空指针问题 (commit: abc123)
- ✅ 优化函数长度 (commit: def456)
- ❓ 关于异步处理，想进一步讨论
```

## 最佳实践

### DO ✅

1. **及时Review**: 收到通知后尽快处理
2. **认真对待**: 把review当作重要工作
3. **相互学习**: 从他人代码中学习
4. **保持友善**: 建设性和专业的态度
5. **关注重点**: 优先关注功能和安全

### DON'T ❌

1. **人身攻击**: 评论代码不评论人
2. **吹毛求疵**: 不纠结无关紧要的风格
3. **敷衍了事**: 不要只写"LGTM"
4. **拖延时间**: 不要让PR等待太久
5. **情绪化**: 保持专业和理性

## 特殊情况处理

### 1. 紧急修复
```markdown
🚨 **紧急修复流程**
1. 标记为 [HOTFIX]
2. 最少1人快速review
3. 重点检查修复正确性
4. 事后补充完整review
```

### 2. 大型重构
```markdown
🔧 **重构PR处理**
1. 提前沟通设计方案
2. 分批提交避免太大
3. 提供详细说明文档
4. 安排专门review会议
```

### 3. 新人代码
```markdown
👶 **新人友好**
1. 更详细的解释
2. 提供参考示例
3. 耐心和鼓励
4. 安排mentor指导
```

## 工具辅助

### 1. 自动化检查
```yaml
# .github/workflows/pr-check.yml
- name: Kotlin Lint
  run: ./gradlew ktlintCheck

- name: Detekt
  run: ./gradlew detekt

- name: Unit Tests
  run: ./gradlew test
```

### 2. Review工具
- **GitHub**: PR评论、建议修改
- **GitLab**: MR讨论、行内评论
- **Bitbucket**: 内联评论、任务追踪

### 3. 辅助插件
- **Octotree**: 代码树形浏览
- **Git History**: 查看文件历史
- **GitHub CLI**: 命令行review

## 度量指标

### Review质量指标
- **响应时间**: 平均review时间
- **缺陷密度**: review后发现的bug数
- **返工率**: 需要多次修改的比例
- **覆盖率**: 代码review覆盖率

### 持续改进
```markdown
## 月度Review总结
- 本月review数量：XX个
- 平均响应时间：XX小时
- 发现问题类型：
  - 功能问题：XX%
  - 性能问题：XX%
  - 安全问题：XX%
- 改进建议：
  1. 加强XX方面的检查
  2. 优化XX流程
```

---

*基于AI启蒙时光项目code review实践*  
*强调建设性反馈和持续学习*