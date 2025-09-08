# Docstring 与中文注释规范SOP（Python 3.11 Web）【极其重要】

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

### 1. 类/模块 Docstring 规范（PEP257 + 中文业务）

```python
class StoryRepositoryImpl:
    """故事仓库实现。

    功能概述：
      - 负责 AI 故事生成与缓存管理
    职责：
      1) 调用外部 AI 服务生成故事
      2) 本地/分布式缓存管理
      3) 内容安全过滤与降级策略
    依赖：AIApiClient, Cache, ContentFilter
    注意：外部调用有配额/超时限制；缓存一致性与过期策略
    """
```

### 2. 函数/方法 Docstring 规范

```python
def generate_story(topic: str, user_age: int = 5) -> Story:
    """生成个性化 AI 故事。

    功能：调用主/备 AI 服务生成故事并进行内容过滤
    业务：非空主题、支持主题白名单、未成年人内容合规
    参数：
      - topic: 故事主题
      - user_age: 年龄用于控制复杂度
    返回：Story（标题/内容/问题）
    异常：ValueError/NetworkError/QuotaExceeded
    性能：正常 2-5s；弱网 10-15s；有缓存快速返回
    扩展：可插拔模型与过滤策略
    """
    ...
```

### 3. 复杂逻辑注释

```python
def calculate_learning_progress(stats: LearningStats) -> float:
    """计算学习进度（加权）。

    公式：0.4*故事完成 + 0.3*答题正确 + 0.2*时长 + 0.1*连续天数
    特殊：连续≥7天 +5%；当日≥30分钟 +3%；返回 0-100
    """
    ...
```

### 4. 交互/API 注释

```python
@router.post("/stories")
async def create_story(req: CreateStoryRequest) -> StoryDTO:
    """生成故事。

    交互：输入主题 -> 用例 -> 内容过滤 -> 返回结果
    状态：201 成功，400/500 失败
    无障碍：错误信息清晰可读
    """
    ...
```

### 5. 业务规则注释

```python
def validate_topic(topic: str) -> None:
    """验证主题合法性：非空、长度、敏感词、类型白名单。"""
    ...
```

### 6. 配置和常量注释

```python
class AIModelConfig:
    """AI 服务配置：密钥来自环境；区分 dev/test/staging/prod；超时与重试策略。"""
    ...
```

## 注释模板

### 1. 新功能开发模板
```python
def feature_entry():
    """[功能名称]

    背景：
    实现：
    注意：
    """
    ...
```

### 2. Bug修复模板
```python
def fix_bug():
    """修复：[问题描述]

    原因：
    方案：
    影响：
    """
    ...
```

### 3. 性能优化模板
```python
def optimize_performance():
    """性能优化：[优化点]

    前：
    后：
    方案：
    """
    ...
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