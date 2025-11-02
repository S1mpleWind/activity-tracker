from data import*
from data.database import ActivityDatabase
from data.data_analysis import DataAnalyzer
from data.visualize import Visualize
from tracker import *
from tracker.windows.windows_tracker import WindowsTracker
from data.database_utils import*
import time

def test_init():
    db = ActivityDatabase()
    print(db)

def test_clear():
    # 最简单的清空方法
    import os
    if os.path.exists("activity.db"):
        os.remove("activity.db")
        print("✅ 数据库已清空")

def test_switch_window():

    db = ActivityDatabase()
    db.record_window_switch('chrome.exe', 'gmail.com')

    time.sleep(7)  # 暂停3秒

    db.record_window_switch('wegame.exe', 'league of legends')
    print(db.current_session_id)

    print(db.get_current_session_info())

def test_get_current_session():
    db = ActivityDatabase()
    print(db.get_current_session_info())
    db.record_window_switch('chrome.exe', 'gmail.com')
    print(db.current_session_id)
    print(db.get_current_session_info())

def test_datastore():
    conn = sqlite3.connect('activity.db')  # 请确保路径正确
    cursor = conn.cursor()

    # 示例1：查询processes表
    print("=== Processes Table ===")
    cursor.execute('SELECT * FROM processes')
    for row in cursor.fetchall():
        print(row)

    # 示例2：查询最近的窗口会话
    print("\n=== Recent Window Sessions ===")
    cursor.execute('''
                    SELECT ws.id, p.name, ws.window_title, ws.start_time, ws.duration_seconds
                    FROM window_sessions ws
                            JOIN processes p ON ws.process_id = p.id
                    ORDER BY ws.start_time DESC LIMIT 5
                   ''')
    for row in cursor.fetchall():
        print(row)

    # 关闭连接
    conn.close()


def test_data_analysis():
    db = ActivityDatabase()
    da = DataAnalyzer()

    print("=== 直接插入测试数据 ===")

    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()

        # 1. 先插入进程数据
        processes_data = [
            ("chrome.exe", "C:\\chrome.exe"),
            ("code.exe", "C:\\code.exe"),
            ("notepad.exe", "C:\\notepad.exe"),
            ("wechat.exe", "C:\\wechat.exe")
        ]

        process_ids = {}
        for name, path in processes_data:
            cursor.execute('INSERT OR IGNORE INTO processes (name, executable_path) VALUES (?, ?)', (name, path))
            cursor.execute('SELECT id FROM processes WHERE name = ? AND executable_path = ?', (name, path))
            process_id = cursor.fetchone()[0]
            process_ids[name] = process_id
            print(f"插入进程: {name} (ID: {process_id})")

        # 2. 插入窗口会话数据（模拟今天的使用记录）
        import datetime
        now = datetime.datetime.now()

        sessions_data = [
            (process_ids["chrome.exe"], "GitHub主页", now - datetime.timedelta(hours=3), 3600),  # 1小时前，用了1小时
            (process_ids["code.exe"], "main.py", now - datetime.timedelta(hours=2), 1800),  # 2小时前，用了30分钟
            (process_ids["chrome.exe"], "Stack Overflow", now - datetime.timedelta(hours=1), 1200),  # 1小时前，用了20分钟
            (process_ids["notepad.exe"], "notes.txt", now - datetime.timedelta(minutes=30), 600),  # 30分钟前，用了10分钟
            (process_ids["wechat.exe"], "微信聊天", now - datetime.timedelta(minutes=15), 300),  # 15分钟前，用了5分钟
        ]

        for process_id, title, start_time, duration in sessions_data:
            cursor.execute('''
                            INSERT INTO window_sessions (process_id, window_title, start_time, end_time, duration_seconds)
                            VALUES (?, ?, ?, ?, ?)
                            ''',
                            (process_id, title, start_time, start_time + datetime.timedelta(seconds=duration), duration))
            print(f"插入会话: {title} ({duration}秒)")

        conn.commit()

    print("✅ 测试数据插入完成\n")

    # 分析数据
    print("=== 数据分析结果 ===")
    result = da.get_today_summary()

    v = Visualize()
    v.visualize_daily(result)
