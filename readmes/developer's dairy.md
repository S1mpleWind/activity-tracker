# Activity-Tracker

Develop an activity-tracker, that can monitor your process 
and help you visualize the time you spent on different apps

---

## Code Tree
```
📁 activity_tracker/
├── 📁 tracker/
│   ├── 📄 __init__.py
│   │
│   ├── 📄 process_tracker.py    # 进程追踪功能
|   ├── 📁 windows/
|   │   ├── 📄__init__.py
│   │   └── 📄windows[core](core)_tracker.py
|   ├── 📁 macos/
|   │   ├── 📄__init__.py
│   │   └── 📄macos_tracker.py
|   └── 📁 linux/[core](core)
|       ├── 📄__init__.py
│       └── 📄linux_tracker.py
| 
├── 📁 data/
|   ├── 📄 data_analysis.py     # 分析数据
|   ├── 📄 database_utils.py
|   ├── 📄 visualize.py  
│   └── 📄 database.py          # 数据库操作
├── 📄 config.py                # 配置文件
├── 📄 test.py                  # run a small test
└── 📄 tracker.py               # 主程[core](core)序


To be added:
tray_app.py
```

---

### process_tracker.py

responsible to track all the process info
- [x] foreground_windows : to be completed in subclassed
- [x] background_process

Subclasses:
1.  **windows_tracker**: implement this first
    1. *the current algorithm only focus on the foreground window*
    2. the background activities will also be tracked
2. macos_tracker
3. linux_tracker

---

### database.py

responsible to store all the infomation from `tracker` in database

It now contains 2 TABLES:
1. `process table`: only record the name of process
2. `window_session table`: record the window_session correspond to specific process

```sql
# processes table ( 1 record )
id | name       | executable_path
1  | chrome.exe | C:\chrome.exe

# window_sessions table ( 3 records)  
id | process_id | window_title   | start_time
1  | 1          | GitHub         | 09:00:00
2  | 1          | Stack Overflow | 10:00:00
3  | 1          | Google Docs    | 11:00:00
```
Functions:
- [ ] init_database
- [ ] save_activity

### data_analysis.py

Analyze all the collected data , for some apps might now run in the foreground, like some audio players.

### test.py & main.py
run a simple instance on test.py


---

## Developing Plan


1. Implement the `tracker`, *Windows* part first, then try mac/linux
2. Handle the data collected from `tracker`,
   1. init database
   2. analyze data in the base
3. Get the analysis **visualized**

>process_tracker -> windows_tracker -> database -> test.py -> visualize.py