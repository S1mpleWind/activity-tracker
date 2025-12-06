import sqlite3
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any


def get_or_create_process(db_path: str, process_name: str,
                          executable_path: Optional[str] = None) -> Optional[int]:
    """
    获取或创建进程记录（使用 UPSERT 方式）
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # 使用本地时间
            cursor.execute('''
                INSERT OR REPLACE INTO processes (name, executable_path, last_seen)
                VALUES (?, ?, datetime('now','localtime'))
            ''', (process_name, executable_path))

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



def get_session_details(db_path: str, session_id: int) -> Optional[Tuple]:
    """
    获取会话详细信息
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



def start_window_session(db_path: str, process_id: int, window_title: str) -> Optional[int]:
    """
    开始一个新的窗口会话
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO window_sessions (process_id, window_title, start_time, is_foreground)
                VALUES (?, ?, datetime('now','localtime'), 1)
            ''', (process_id, window_title))

            session_id = cursor.lastrowid
            conn.commit()

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"开始新会话: 进程ID={process_id}, 窗口='{window_title}', 会话ID={session_id}, 开始时间={current_time}")
            return session_id

    except sqlite3.Error as e:
        print(f"❌ 数据库错误 - 开始会话失败: {e}")
        return None



def end_window_session(db_path: str, session_id: int, specific_time: Optional[datetime]) -> bool:
    """
    结束窗口会话
    如果 specific_time（用户指定时间）不为 None，就用它作为结束时间
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            if specific_time is not None:
                # 转换为字符串，格式与 SQLite 兼容
                end_time_str = specific_time.strftime("%Y-%m-%d %H:%M:%S")
                print(end_time_str)

                # 更新 end_time 与 duration
                cursor.execute('''
                    UPDATE window_sessions
                    SET end_time = ?,
                        duration_seconds =
                            CAST((julianday(?) - julianday(start_time)) * 86400 AS INTEGER)
                    WHERE id = ?
                      AND end_time IS NULL
                ''', (end_time_str, end_time_str, session_id))

                used_time = end_time_str
            else:
                # 使用本地时间
                cursor.execute("SELECT datetime('now','localtime')")
                local_now = cursor.fetchone()[0]

                cursor.execute('''
                    UPDATE window_sessions
                    SET end_time         = datetime('now','localtime'),
                        duration_seconds = CAST(
                               (julianday(datetime('now','localtime')) - julianday(start_time))
                               * 86400 AS INTEGER)
                    WHERE id = ?
                      AND end_time IS NULL
                ''', (session_id,))

                used_time = local_now

            rows_affected = cursor.rowcount
            conn.commit()

            if rows_affected > 0:
                print(f"结束会话: 会话ID={session_id}, 结束时间={used_time}")
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
