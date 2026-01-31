# 快速开始指南

## 🚀 5分钟快速上手

### 1. 安装依赖
```bash
pip install -r requirementlist
```

### 2. 运行应用
```bash
python gui.py
```

### 3. 基本操作

#### Dashboard（仪表板）
- 点击 **"Start Tracking"** 开始追踪
- 应用会记录你的每个窗口切换
- 点击 **"Stop Tracking"** 停止追踪
- 点击 **"Clear Today"** 删除今日记录

#### Analysis（分析）
- 输入 **Start YYYY-MM-DD** 和 **End YYYY-MM-DD**
- 点击 **"Load Range"** 查看该时间段的应用统计
- 点击 **"Today"** 快速查看今日数据
- 显示饼图和详细统计表

#### Classifier（分类器）⭐ 新增
- 输入开始日期和结束日期
- 点击 **"Classify"** 按钮
- 查看各类别的占比分析
- 或点击 **"Today"** 查看今日分类

---

## 📊 分类器详解

### 分类标签
- **work** 🏢 - 工作相关应用（VS Code, GitHub, Excel, Slack等）
- **learning** 📚 - 学习相关应用（Jupyter, Coursera, Stack Overflow等）
- **communication** 💬 - 社交应用（微信, QQ, Gmail, Telegram等）
- **entertainment** 🎮 - 娱乐应用（YouTube, Netflix, Steam等）
- **system** ⚙️ - 系统应用（Windows Explorer, Settings等）
- **other** ❓ - 其他未分类应用

### 使用流程

```
打开GUI
  ↓
选择 "Classifier" 标签页
  ↓
输入日期范围（或点击"Today"）
  ↓
点击 "Classify" 按钮
  ↓
查看分类结果
  ├─ 饼图（直观展示占比）
  └─ 统计表（详细数据）
```

---

## 💻 代码使用示例

### 获取今日分类统计

```python
from data.activity_classifier import ActivityClassifier
from datetime import datetime

# 初始化分类器
classifier = ActivityClassifier()

# 获取今日分类
today = datetime.now().strftime("%Y-%m-%d")
result = classifier.get_daily_classification(today)

# 打印结果
print(f"总使用时间: {result['total_hours']:.1f}小时\n")

for category, stats in result['statistics'].items():
    if stats['minutes'] > 0:
        print(f"{category.upper()}")
        print(f"  时间: {stats['hours']:.1f}小时 ({stats['minutes']}分钟)")
        print(f"  占比: {stats['percentage']:.1f}%")
        print(f"  会话数: {stats['session_count']}")
        print()
```

### 获取特定类别的应用排行

```python
from data.activity_classifier import ActivityClassifier

classifier = ActivityClassifier()

# 获取本周工作应用排行
apps = classifier.get_top_apps_by_category(
    '2024-01-22', 
    '2024-01-28', 
    'work', 
    limit=5
)

for app in apps:
    print(f"{app['app']}: {app['hours']:.1f}小时 ({app['session_count']}次)")
```

### 对比多个日期范围

```python
from data.activity_classifier import ActivityClassifier

classifier = ActivityClassifier()

# 周一
monday = classifier.get_daily_classification('2024-01-22')

# 周五
friday = classifier.get_daily_classification('2024-01-26')

# 比较
print("周一 vs 周五 - 工作时间对比:")
monday_work = monday['statistics']['work']['hours']
friday_work = friday['statistics']['work']['hours']
print(f"周一: {monday_work:.1f}小时")
print(f"周五: {friday_work:.1f}小时")
print(f"差异: {friday_work - monday_work:+.1f}小时")
```

---

## 🔧 自定义分类

### 方法1：修改现有关键词

```python
from data.activity_classifier import ActivityClassifier

classifier = ActivityClassifier()

# 为工作类添加新关键词
classifier.categories['work']['keywords'].extend([
    'confluence',
    'jira',
    'asana'
])
```

### 方法2：创建子类自定义分类

```python
from data.activity_classifier import ActivityClassifier

class MyClassifier(ActivityClassifier):
    def __init__(self):
        super().__init__()
        
        # 修改现有分类
        self.categories['work']['keywords'] = [
            'code', 'github', 'gitlab', 'visual studio',
            'confluence', 'jira', 'asana', 'notion'
        ]
        
        # 添加新分类
        self.categories['shopping'] = {
            'keywords': ['amazon', 'ebay', 'taobao', '淘宝', '京东'],
            'color': '#FF69B4'
        }
    
    def classify_activity(self, app_name, window_title):
        # 可在这里添加自定义逻辑
        return super().classify_activity(app_name, window_title)

# 使用自定义分类器
custom = MyClassifier()
result = custom.get_daily_classification('2024-01-25')
```

---

## 📈 数据分析示例

### 获取最活跃的时间段

```python
from data.data_analysis import DataAnalyzer
from collections import Counter

analyzer = DataAnalyzer()

# 获取今日所有活动
activities = analyzer.get_today_activities()

# 统计各小时的活动数
hours = []
for activity in activities:
    from datetime import datetime
    hour = datetime.fromisoformat(activity['start_time']).hour
    hours.append(hour)

counter = Counter(hours)
print("今日各小时活动频率:")
for hour in sorted(counter.keys()):
    print(f"{hour:02d}:00 - {counter[hour]} 个会话")
```

### 对比应用使用时间

```python
from data.data_analysis import DataAnalyzer

analyzer = DataAnalyzer()

# 获取本周数据
weekly = analyzer.get_usage_between('2024-01-22', '2024-01-28')

# 按时长排序
weekly_sorted = sorted(weekly, key=lambda x: x['minutes'], reverse=True)

print("本周应用使用排行 Top 10:")
for i, app in enumerate(weekly_sorted[:10], 1):
    print(f"{i}. {app['name']}: {app['hours']:.1f}小时")
```

---

## 🐛 常见问题

**Q: 数据保存在哪里？**
A: 数据保存在 `activity.db` 文件中（SQLite数据库），通常在程序运行目录。

**Q: 为什么没有记录到某些应用？**
A: 这些应用可能在忽略列表中。可以在 `config.py` 中查看 `IGNORE_WINDOW_KEYWORDS`。

**Q: 如何导出数据？**
A: 可以直接复制 `activity.db` 文件，或使用 SQLite 工具导出数据。

**Q: 分类器如何知道新应用？**
A: 新应用默认归类为 "other"，可通过添加关键词来改进分类。

**Q: 可以删除特定日期的数据吗？**
A: 可以，在 Dashboard 的 "Clear Range" 中输入日期范围。

---

## 📚 详细文档

- **PROJECT_ANALYSIS.md** - 项目全面分析
- **IMPLEMENTATION_GUIDE.md** - 完整实现指南
- **CLEANUP_SUMMARY.md** - 代码完善总结

---

## 🎯 下一步

1. **运行应用**：`python gui.py`
2. **开始追踪**：点击 Dashboard 中的 "Start Tracking"
3. **查看分析**：使用 Analysis 和 Classifier 查看数据
4. **优化配置**：根据需要修改 config.py 和分类规则

---

祝你使用愉快！🎉

