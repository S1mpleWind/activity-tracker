import sqlite3
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any


def get_or_create_process(db_path: str, process_name: str,
                          executable_path: Optional[str] = None) -> Optional[int]:
    """
    获取或创建进程记录（使用 UPSERT 方式）

    Args:
        db_path: 数据库文件路径
        process_name: 进程名称
        executable_path: 可执行文件路径

    Returns:
        Optional[int]: 进程ID，失败返回None
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # 使用 INSERT OR REPLACE 实现 UPSERT
            cursor.execute('''
                INSERT OR REPLACE INTO processes (name, executable_path, last_seen)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (process_name, executable_path))

            # 获取进程ID（新插入的或已存在的）
            cursor.execute('''
                           SELECT id
                           FROM processes
                           WHERE name = ?
                             AND (executable_path = ? OR (executable_path IS NULL AND ? IS NULL))
                           ''', (process_name, executable_path, executable_path))

            result = cursor.fetchone()
            conn.commit()

            return result[0] if result else None

    except sqlite3.Error as e:
        print(f"❌ 数据库错误 - 获取/创建进程失败: {e}")
        return None

#============
# 在 utils.py 中添加

def get_session_details(db_path: str, session_id: int) -> Optional[Tuple]:
    """
    获取会话详细信息

    Args:
        db_path: 数据库路径
        session_id: 会话ID

    Returns:
        Optional[Tuple]: (进程名, 窗口标题, 开始时间, 会话ID)
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            SELECT p.name,
                                    ws.window_title,
                                    ws.start_time,
                                    ws.id
                            FROM window_sessions ws
                                    JOIN processes p ON ws.process_id = p.id
                            WHERE ws.id = ?
                            ''', (session_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"❌ 获取会话详情失败: {e}")
        return None


# 在 utils.py 中添加这个函数

def start_window_session(db_path: str, process_id: int, window_title: str) -> Optional[int]:
    """
    开始一个新的窗口会话

    Args:
        db_path: 数据库文件路径
        process_id: 进程ID
        window_title: 窗口标题

    Returns:
        Optional[int]: 会话ID，失败返回None
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            start_time = datetime.now()
            # 插入新的窗口会话记录
            cursor.execute('''
                           INSERT INTO window_sessions (process_id, window_title, start_time, is_foreground)
                           VALUES (?, ?, CURRENT_TIMESTAMP, 1)
                           ''', (process_id, window_title))

            session_id = cursor.lastrowid
            conn.commit()

            print(f"✅ 开始新会话: 进程ID={process_id}, 窗口='{window_title}', 会话ID={session_id},开始时间={start_time}")
            return session_id

    except sqlite3.Error as e:
        print(f"❌ 数据库错误 - 开始会话失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 未知错误 - 开始会话失败: {e}")
        return None


def end_window_session(db_path: str, session_id: int) -> bool:
    """
    结束窗口会话

    Args:
        db_path: 数据库文件路径
        session_id: 会话ID

    Returns:
        bool: 是否成功
    """
    #print('ending........')
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # get current time for display
            cursor.execute('SELECT CURRENT_TIMESTAMP')
            current_time = cursor.fetchone()[0]

            cursor.execute('''
                           UPDATE window_sessions
                           SET end_time         = CURRENT_TIMESTAMP,
                               duration_seconds = CAST((julianday(CURRENT_TIMESTAMP) - julianday(start_time)) * 86400 AS INTEGER)
                           WHERE id = ?
                             AND end_time IS NULL
                           ''', (session_id,))

            rows_affected = cursor.rowcount
            conn.commit()

            if rows_affected > 0:
                print(f"✅ 结束会话: 会话ID={session_id} , 结束时间={ current_time }")
                return True
            else:
                print(f"⚠️ 会话已结束或不存在: 会话ID={session_id}")
                return False

    except sqlite3.Error as e:
        print(f"❌ 数据库错误 - 结束会话失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误 - 结束会话失败: {e}")
        return False

