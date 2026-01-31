# Activity Tracker 项目分析报告

## 一、项目功能总结

### 核心功能
**Activity Tracker** (TimeScope) 是一个 PC 活动追踪工具，用于记录和分析用户的应用程序使用情况。

#### 主要功能模块：

1. **进程追踪（Tracker）**
   - 实时监控前台应用窗口和进程信息
   - Windows 平台专用实现（`windows_tracker.py`）
   - 支持获取前台窗口信息和后台进程列表
   - 内置时间管理器，检测系统休眠/唤醒事件

2. **数据存储（Database）**
   - SQLite 本地数据库存储
   - 两张主要表：
     - `processes`：记录所有进程信息（名称、路径、首次/最后见时间）
     - `window_sessions`：记录窗口会话（进程ID、窗口标题、开始/结束时间、持续秒数）
   
3. **数据分析（DataAnalyzer）**
   - 获取今日使用摘要（总时间、应用统计）
   - 按应用聚合使用时间统计
   - 获取指定日期范围内的使用数据
   - 获取最近活动记录
   - 获取最常用应用排行

4. **数据可视化（Visualize）**
   - 饼图展示应用使用时间分布
   - 水平条形图展示应用排行
   - 支持嵌入 GUI 中显示

5. **用户界面（GUI）**
   - 基于 `customtkinter` 的 GUI 应用
   - 两个主要界面：
     - **Dashboard**：开始/停止追踪，管理数据（删除今日/范围数据）
     - **Analysis**：查询分析数据，支持今日/时间范围查询，显示图表和统计表

---

## 二、数据库结构与存储格式

### 数据库架构

#### 1. `processes` 表（进程表）
```sql
CREATE TABLE processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,          -- 进程ID（自增）
    name TEXT NOT NULL,                            -- 进程名称（如 chrome.exe）
    executable_path TEXT,                          -- 可执行文件路径（可选）
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 首次见时间
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 最后见时间
    UNIQUE(name, executable_path)                 -- 唯一约束：防止重复记录
)
```

**示例数据：**
```
id | name       | executable_path      | first_seen            | last_seen
1  | chrome.exe | C:\Program Files\... | 2024-01-20 09:00:00   | 2024-01-25 14:30:00
2  | code.exe   | C:\Users\...\code.exe| 2024-01-21 10:15:00   | 2024-01-25 16:45:00
3  | notepad.exe| C:\Windows\notepad.exe| 2024-01-22 11:20:00   | 2024-01-25 13:10:00
```

#### 2. `window_sessions` 表（窗口会话表）
```sql
CREATE TABLE window_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,     -- 会话ID（自增）
    process_id INTEGER NOT NULL,              -- 进程ID（外键）
    window_title TEXT NOT NULL,               -- 窗口标题（如 "GitHub主页"）
    start_time TIMESTAMP NOT NULL,            -- 开始时间
    end_time TIMESTAMP,                       -- 结束时间（可为NULL，表示进行中）
    duration_seconds INTEGER DEFAULT 0,       -- 持续秒数（自动计算）
    is_foreground BOOLEAN DEFAULT 1,          -- 是否前台窗口
    FOREIGN KEY (process_id) REFERENCES processes (id)
)
```

**示例数据：**
```
id | process_id | window_title      | start_time            | end_time              | duration_seconds | is_foreground
1  | 1          | Gmail - 收件箱    | 2024-01-25 09:00:00   | 2024-01-25 09:30:00   | 1800             | 1
2  | 1          | Stack Overflow    | 2024-01-25 09:30:00   | 2024-01-25 10:15:00   | 2700             | 1
3  | 2          | main.py           | 2024-01-25 10:15:00   | 2024-01-25 11:45:00   | 5400             | 1
4  | 3          | notes.txt         | 2024-01-25 11:45:00   | NULL                  | 0                | 1
```

### 数据读取方式

#### 方法 1：使用 DataAnalyzer（推荐）

```python
from data.database import ActivityDatabase
from data.data_analysis import DataAnalyzer

# 初始化分析器
analyzer = DataAnalyzer("activity.db")

# 获取今日摘要
summary = analyzer.get_today_summary()
# 返回：{
#   'total_hours': 8.5,
#   'total_minutes': 510,
#   'app_usage': [
#     {'name': 'chrome.exe', 'hours': 3.2, 'minutes': 192},
#     {'name': 'code.exe', 'hours': 2.5, 'minutes': 150},
#     ...
#   ]
# }

# 获取日期范围内的数据
usage = analyzer.get_usage_between('2024-01-20', '2024-01-25')
# 返回按应用聚合的时长列表

# 获取今日所有活动记录
activities = analyzer.get_today_activities()
# 返回：[
#   {'process': 'chrome.exe', 'window_title': 'Gmail', 'start_time': '2024-01-25 09:00:00', 'duration_minutes': 30},
#   ...
# ]
```

#### 方法 2：直接 SQL 查询

```python
import sqlite3

conn = sqlite3.connect('activity.db')
cursor = conn.cursor()

# 查询今日应用使用时间排行
cursor.execute('''
    SELECT p.name, SUM(ws.duration_seconds) as total_seconds
    FROM window_sessions ws
    JOIN processes p ON ws.process_id = p.id
    WHERE DATE(ws.start_time) = DATE('now')
    GROUP BY p.name
    ORDER BY total_seconds DESC
''')

for app_name, seconds in cursor.fetchall():
    print(f"{app_name}: {seconds // 60} 分钟")

conn.close()
```

#### 方法 3：使用 ActivityDatabase 类

```python
from data.database import ActivityDatabase

db = ActivityDatabase("activity.db")

# 获取今日记录
today_records = db.delete_today_data()  # 仅用于删除

# 获取特定范围
deleted_count = db.delete_range('2024-01-20', '2024-01-25')
```

---

## 三、未使用的函数与代码清理

### database.py 中的 Stub 函数

以下函数声明了但未实现（仅有 `pass`），且在项目中无调用：

| 函数名 | 位置 | 状态 | 建议 |
|------|------|------|------|
| `get_today_activities()` | database.py L174 | Stub | 删除（功能重复，DataAnalyzer 已提供） |
| `get_usage_statistics()` | database.py L183 | Stub | 删除（功能重复） |
| `get_process_usage()` | database.py L193 | Stub | 删除（功能重复） |
| `cleanup_old_records()` | database.py L247 | Stub | 删除（功能未使用） |
| `export_data()` | database.py L259 | Stub | 删除（功能未使用） |
| `get_database_info()` | database.py L273 | Stub | 删除（功能未使用） |
| `close()` | database.py L282 | Stub | 删除（未使用） |

### visualize.py 中的 Stub 函数

| 函数名 | 位置 | 状态 | 建议 |
|------|------|------|------|
| `viualize_weekly()` | visualize.py L20 | Stub | 删除（typo：拼写错误 "viualize"） |
| `visualize_monthly()` | visualize.py L23 | Stub | 删除 |
| `viualize_yearly()` | visualize.py L26 | Stub | 删除 |
| `plot_pie()` | visualize.py L36 | 部分实现 | 删除（被 `plot_pie_figure()` 替代） |

### windows_tracker.py 中的问题

| 函数名 | 位置 | 问题 | 建议 |
|------|------|------|------|
| `get_windows_process_details()` | windows_tracker.py L74 | 缺少 `self` 参数，无调用 | 删除或修复 |

### process_tracker.py 中的 Stub 函数

| 函数名 | 位置 | 状态 | 建议 |
|------|------|------|------|
| `_select_important_process()` | process_tracker.py L38 | Stub | 删除 |

---

## 四、为 Classifier 开发的数据读取方案

### 1. 推荐的数据获取接口

为了支持 **应用分类器** 的开发，你可以创建以下专用接口：

```python
class ActivityData:
    """为分类器提供数据接口"""
    
    def __init__(self, db_path: str = "activity.db"):
        self.db_path = db_path
    
    def get_raw_sessions(self, start_date: str, end_date: str) -> List[Dict]:
        """获取原始会话数据（不聚合）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.name, ws.window_title, ws.start_time, 
                       ws.duration_seconds, ws.id
                FROM window_sessions ws
                JOIN processes p ON ws.process_id = p.id
                WHERE DATE(ws.start_time) >= DATE(?) 
                  AND DATE(ws.start_time) <= DATE(?)
                  AND ws.end_time IS NOT NULL
                ORDER BY ws.start_time
            ''', (start_date, end_date))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'process': row[0],
                    'window_title': row[1],
                    'start_time': row[2],
                    'duration_seconds': row[3],
                    'session_id': row[4]
                })
            return sessions
    
    def get_app_windows(self, app_name: str) -> List[str]:
        """获取特定应用的所有窗口标题"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT ws.window_title
                FROM window_sessions ws
                JOIN processes p ON ws.process_id = p.id
                WHERE p.name = ?
            ''', (app_name,))
            
            return [row[0] for row in cursor.fetchall()]
    
    def get_statistics_by_window(self, start_date: str, end_date: str) -> Dict:
        """按窗口标题统计使用时间"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.name, ws.window_title, 
                       SUM(ws.duration_seconds) as total_seconds,
                       COUNT(*) as session_count
                FROM window_sessions ws
                JOIN processes p ON ws.process_id = p.id
                WHERE DATE(ws.start_time) >= DATE(?) 
                  AND DATE(ws.start_time) <= DATE(?)
                GROUP BY p.name, ws.window_title
                ORDER BY total_seconds DESC
            ''', (start_date, end_date))
            
            stats = {}
            for app, window, seconds, count in cursor.fetchall():
                key = f"{app} | {window}"
                stats[key] = {
                    'app': app,
                    'window': window,
                    'minutes': seconds // 60,
                    'hours': seconds / 3600,
                    'session_count': count
                }
            return stats
```

### 2. 分类器集成示例

```python
from data.activity_data import ActivityData  # 待创建的新模块
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

class ActivityClassifier:
    """活动分类器"""
    
    def __init__(self, db_path: str = "activity.db"):
        self.data_provider = ActivityData(db_path)
        self.classifier = None
        self.category_encoder = LabelEncoder()
    
    def prepare_features(self, sessions: List[Dict]) -> pd.DataFrame:
        """从会话数据提取特征"""
        features = []
        
        for session in sessions:
            feat = {
                'process': session['process'],
                'window_title': session['window_title'],
                'duration_minutes': session['duration_seconds'] / 60,
                'hour_of_day': pd.to_datetime(session['start_time']).hour,
                'day_of_week': pd.to_datetime(session['start_time']).dayofweek,
                # 可继续添加：窗口标题长度、包含关键词等
            }
            features.append(feat)
        
        return pd.DataFrame(features)
    
    def classify(self, start_date: str, end_date: str) -> Dict:
        """分类和统计活动"""
        sessions = self.data_provider.get_raw_sessions(start_date, end_date)
        
        classified = {
            'work': [],      # 工作相关
            'learning': [],  # 学习相关
            'entertainment': [], # 娱乐
            'communication': [], # 社交通信
            'other': []      # 其他
        }
        
        # 分类逻辑（可基于窗口标题、应用名等）
        for session in sessions:
            app = session['process'].lower()
            window = session['window_title'].lower()
            
            if self._is_work(app, window):
                classified['work'].append(session)
            elif self._is_learning(app, window):
                classified['learning'].append(session)
            # ... 其他分类
            else:
                classified['other'].append(session)
        
        # 统计
        stats = {}
        for category, sessions_list in classified.items():
            total_seconds = sum(s['duration_seconds'] for s in sessions_list)
            stats[category] = {
                'count': len(sessions_list),
                'minutes': total_seconds // 60,
                'hours': total_seconds / 3600,
                'percentage': (total_seconds / sum(
                    sum(s['duration_seconds'] for s in v) 
                    for v in classified.values()
                )) * 100
            }
        
        return {
            'statistics': stats,
            'classified_sessions': classified
        }
    
    def _is_work(self, app: str, window: str) -> bool:
        work_keywords = ['code', 'visual studio', 'pycharm', 'github', 
                        'excel', 'word', 'outlook', 'slack', 'meeting']
        return any(kw in app or kw in window for kw in work_keywords)
    
    def _is_learning(self, app: str, window: str) -> bool:
        learning_keywords = ['jupyter', 'python', 'coursera', 'udemy', 
                           'stackoverflow', 'documentation']
        return any(kw in app or kw in window for kw in learning_keywords)
    
    # ... 其他分类方法
```

### 3. 使用示例

```python
# 初始化分类器
classifier = ActivityClassifier()

# 分类和统计
result = classifier.classify('2024-01-20', '2024-01-25')

# 输出结果
for category, stats in result['statistics'].items():
    print(f"\n{category.upper()}:")
    print(f"  会话数: {stats['count']}")
    print(f"  时长: {stats['hours']:.1f}小时 ({stats['minutes']}分钟)")
    print(f"  占比: {stats['percentage']:.1f}%")
```

---

## 五、数据库结构总结

### 核心查询场景

| 场景 | SQL 示例 | 用途 |
|------|--------|------|
| 今日应用排行 | `SELECT p.name, SUM(ws.duration_seconds) ... WHERE DATE(ws.start_time) = DATE('now')` | 统计分析 |
| 特定日期范围 | `WHERE DATE(ws.start_time) BETWEEN ? AND ?` | 日期范围查询 |
| 应用窗口统计 | `GROUP BY p.name, ws.window_title` | 分类器特征提取 |
| 活动时间线 | `ORDER BY ws.start_time DESC LIMIT ?` | 最近活动 |

---

## 六、后续开发建议

1. **创建 `data/activity_data.py`** - 专门为分类器提供数据接口
2. **创建 `classifiers/activity_classifier.py`** - 实现分类逻辑
3. **扩展 GUI** - 在 Analysis 界面添加分类结果展示
4. **删除 stub 函数** - 见第三部分清单
5. **优化数据库** - 考虑添加索引优化复杂查询性能

