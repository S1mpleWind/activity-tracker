# Activity Tracker - 使用与集成指南

## 最近更新

### 完善的功能
1. ✅ 删除所有未实现的 stub 函数
2. ✅ 完善 `database.py` 中的上下文管理器支持
3. ✅ 创建 `ActivityClassifier` 分类器类
4. ✅ 在 GUI 中集成分类器界面和功能

---

## 一、类结构与完善的方法

### 1. ActivityDatabase 类 (data/database.py)

**已完善的方法：**

```python
class ActivityDatabase:
    def __init__(self, db_path: str = "activity.db")
    def record_window_switch(process_name, window_title, executable_path) -> bool
    def get_current_session_info() -> Optional[Tuple]
    def stop_current_session(endTime) -> bool
    def delete_today_data() -> int
    def delete_range(start_date, end_date) -> int
    def close() -> None
    def __enter__() -> self
    def __exit__(exc_type, exc_val, exc_tb)
```

**使用示例：**

```python
# 上下文管理器用法
with ActivityDatabase() as db:
    db.record_window_switch("chrome.exe", "Gmail")
    time.sleep(10)
    db.stop_current_session(None)
    
# 手动使用
db = ActivityDatabase()
db.record_window_switch("code.exe", "main.py")
db.close()
```

### 2. DataAnalyzer 类 (data/data_analysis.py)

**已实现的方法：**

```python
def get_today_summary() -> Dict  # 今日摘要
def get_recent_activities(limit) -> List  # 最近活动
def get_top_apps(days, limit) -> List  # 最常用应用
def get_daily_usage(days) -> List  # 每日使用时间
def get_today_activities() -> List  # 今日所有活动
def get_usage_between(start_date, end_date) -> List  # 时间范围内的使用
```

### 3. ActivityClassifier 类 (data/activity_classifier.py) ⭐ 新增

**核心方法：**

```python
def classify_activity(app_name, window_title) -> str
    # 对应用活动进行分类
    # 返回: 'work', 'learning', 'communication', 'entertainment', 'system', 'other'

def get_classified_statistics(start_date, end_date) -> Dict
    # 获取指定日期范围的分类统计
    # 返回包含各类别的分钟、小时、百分比和会话数

def get_top_apps_by_category(start_date, end_date, category, limit) -> List
    # 获取某类别中最常用的应用

def get_daily_classification(date) -> Dict
    # 单日分类统计

def get_weekly_classification(start_date) -> Dict
    # 周分类统计（7天）
```

**分类标签和关键词：**

| 分类 | 关键词示例 | 颜色 |
|-----|----------|------|
| work | code, github, excel, outlook, slack, teams | #FF6B6B |
| learning | jupyter, python, coursera, stackoverflow | #4ECDC4 |
| communication | wechat, qq, gmail, telegram, discord | #45B7D1 |
| entertainment | youtube, netflix, steam, game, spotify | #FFA07A |
| system | explorer, windows, settings, terminal | #95E1D3 |
| other | 其他 | #999999 |

**使用示例：**

```python
from data.activity_classifier import ActivityClassifier

classifier = ActivityClassifier()

# 获取单日分类统计
today = datetime.now().strftime("%Y-%m-%d")
result = classifier.get_daily_classification(today)

print("今日统计：")
for category, stats in result['statistics'].items():
    print(f"{category}: {stats['hours']:.1f}小时 ({stats['percentage']:.1f}%)")

# 获取周统计
week_result = classifier.get_weekly_classification('2024-01-22')

# 获取某类别的顶级应用
work_apps = classifier.get_top_apps_by_category('2024-01-22', '2024-01-28', 'work', limit=5)
for app in work_apps:
    print(f"{app['app']}: {app['hours']:.1f}小时")
```

### 4. Visualize 类 (data/visualize.py)

**已实现的方法：**

```python
def plot_pie_figure(data, figsize) -> Figure
    # 绘制饼图（返回matplotlib Figure对象）

def plot_bar_figure(data, figsize) -> Figure
    # 绘制水平条形图（适合标签较多的情况）

def visualize_daily(daily_data)
    # 打印并绘制今日数据
```

### 5. BaseTracker 类 (tracker/process_tracker.py)

**已完善的方法：**

```python
def start_tracking() -> None
def stop_tracking() -> None
def _should_ignore_process(window_title) -> bool
```

**抽象方法（由子类实现）：**

```python
@abstractmethod
def get_foreground_info() -> Tuple[Optional[str], Optional[str]]

@abstractmethod
def get_background_processes() -> List[Dict[str, Any]]
```

---

## 二、GUI 集成 (gui.py)

### 新增功能

**三个主要界面：**

1. **Dashboard** - 跟踪管理
   - 开始/停止追踪
   - 删除今日数据
   - 按日期范围删除数据

2. **Analysis** - 数据分析
   - 按时间范围查询
   - 显示应用使用排行
   - 生成饼图/条形图

3. **Classifier** ⭐ 新增 - 活动分类
   - 按类别分类统计
   - 显示分类饼图
   - 详细统计表

### GUI 中的分类器使用

```python
# 在App类中已初始化
self.classifier = ActivityClassifier()

# 分类器方法
def load_classifier(self):
    """按日期范围加载分类"""
    
def load_classifier_today(self):
    """加载今日分类"""
    
def _display_classifier_results(result):
    """显示分类结果"""
```

**调用流程：**

```
用户输入日期范围
    ↓
load_classifier() / load_classifier_today()
    ↓
classifier.get_classified_statistics()
    ↓
_display_classifier_results()
    ↓
生成饼图 + 统计表显示
```

---

## 三、数据流与集成示例

### 完整的追踪-分析-分类流程

```python
from data.database import ActivityDatabase
from data.data_analysis import DataAnalyzer
from data.activity_classifier import ActivityClassifier
from tracker.windows.windows_tracker import WindowsTracker
import time

# 1. 初始化
db = ActivityDatabase("activity.db")
tracker = WindowsTracker()
analyzer = DataAnalyzer()
classifier = ActivityClassifier()

# 2. 开始追踪（通常在GUI中循环执行）
tracker.start_tracking()
for i in range(600):  # 10分钟的示例
    process_name, window_title = tracker.get_foreground_info()
    
    if process_name:
        # 记录窗口切换
        db.record_window_switch(process_name, window_title)
    
    time.sleep(1)

db.stop_current_session(None)

# 3. 数据分析
today = "2024-01-25"
summary = analyzer.get_today_summary()
print(f"总时间: {summary['total_hours']}小时")

# 4. 活动分类
classified = classifier.get_daily_classification(today)

print("\n分类统计：")
for category, stats in classified['statistics'].items():
    if stats['minutes'] > 0:
        print(f"{category.upper()}: {stats['hours']:.1f}小时 ({stats['percentage']:.1f}%)")
        
        # 获取该类别的顶级应用
        top_apps = classifier.get_top_apps_by_category(today, today, category, limit=3)
        for app in top_apps:
            print(f"  - {app['app']}: {app['hours']:.1f}小时")
```

### 分类器在 GUI 中的调用

```python
class App(customtkinter.CTk):
    def __init__(self):
        # ... 其他初始化 ...
        self.classifier = ActivityClassifier()
    
    def load_classifier(self):
        """从UI获取日期范围并执行分类"""
        start = self.classifier_start_entry.get()
        end = self.classifier_end_entry.get()
        
        try:
            # 获取分类结果
            result = self.classifier.get_classified_statistics(start, end)
            
            # 显示结果
            self._display_classifier_results(result)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _display_classifier_results(self, result):
        """展示分类结果（饼图+统计表）"""
        # 1. 创建结果框架
        # 2. 使用 Visualize 绘制饼图
        # 3. 创建统计表格显示百分比、时长等
```

---

## 四、数据库查询示例

### 为分类器提供原始数据

```python
import sqlite3

# 获取原始会话数据用于分类
def get_raw_sessions(db_path, start_date, end_date):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.name, ws.window_title, ws.duration_seconds
            FROM window_sessions ws
            JOIN processes p ON ws.process_id = p.id
            WHERE DATE(ws.start_time) >= DATE(?)
              AND DATE(ws.start_time) <= DATE(?)
              AND ws.end_time IS NOT NULL
            ORDER BY ws.start_time
        ''', (start_date, end_date))
        
        return cursor.fetchall()

# 按类别统计
def get_stats_by_category(db_path, start_date, end_date, classifier):
    sessions = get_raw_sessions(db_path, start_date, end_date)
    
    stats = {
        'work': 0, 'learning': 0, 'entertainment': 0,
        'communication': 0, 'system': 0, 'other': 0
    }
    
    for app_name, window_title, duration in sessions:
        category = classifier.classify_activity(app_name, window_title)
        stats[category] += duration
    
    return stats
```

---

## 五、关键改进点

### 🔧 已完善的功能

| 项目 | 状态 | 说明 |
|------|------|------|
| database.py stub 函数 | ✅ 删除 | 删除了5个未实现的方法 |
| 上下文管理器 | ✅ 完善 | 支持 `with` 语句 |
| 分类器类 | ✅ 新增 | ActivityClassifier 类完整实现 |
| GUI 分类界面 | ✅ 新增 | 三个分类操作界面 |
| visualize.py | ✅ 清理 | 删除重复代码和 stub 方法 |
| windows_tracker.py | ✅ 修复 | 删除有问题的静态方法 |

### 🎯 下一步建议

1. **扩展分类关键词** - 根据实际使用定制分类规则
2. **添加自定义分类** - 允许用户定义新的分类
3. **导出功能** - 支持导出分类统计为 CSV/PDF
4. **时间线视图** - 按时间显示活动分类变化
5. **趋势分析** - 显示不同类别的周/月趋势

---

## 六、运行与测试

```bash
# 安装依赖
pip install -r requirementlist

# 运行GUI应用
python gui.py

# 运行测试
python -m pytest test/

# 直接测试分类器
python -c "
from data.activity_classifier import ActivityClassifier
classifier = ActivityClassifier()
result = classifier.get_daily_classification('2024-01-25')
print(result['statistics'])
"
```

---

## 七、常见问题

**Q: 分类器如何处理新应用？**
A: 新应用会被归类为 'other'，可通过编辑 `ActivityClassifier` 中的 `categories` 字典来添加关键词。

**Q: 可以自定义分类吗？**
A: 可以，创建 `ActivityClassifier` 的子类并重写 `classify_activity()` 方法。

**Q: 分类结果如何优化？**
A: 可以根据窗口标题、应用路径等进行更精细的分类逻辑。

