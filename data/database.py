import sqlite3
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from .database_utils import*


class ActivityDatabase:
    def __init__(self, db_path: str = "activity.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.current_session_id: Optional[int] = None
        self._init_database()

    # initialize the database
    def _init_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # The Table of process
            sql1 = '''CREATE TABLE IF NOT EXISTS processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    executable_path TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, executable_path))'''
            cursor.execute(sql1)

            # The table of window conversation
            sql2 = '''CREATE TABLE IF NOT EXISTS window_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,
    window_title TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    is_foreground BOOLEAN DEFAULT 1,
    FOREIGN KEY (process_id) REFERENCES processes (id))'''
            cursor.execute(sql2)

            # 索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_processes_name ON processes(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_time ON window_sessions(start_time)')

            conn.commit()

    def record_window_switch(self, process_name: str, window_title: str,
                             executable_path: Optional[str] = None) -> bool:
        """
        Record the incident of switching between two windows.
        Call this function when a different foreground window has been detected

        :param:
            process_name: 进程名称
            window_title: 窗口标题
            executable_path: 可执行文件路径（可选）

        :return:
            bool: 记录是否成功
        """
        try:
            # jump all the invalid data
            if not process_name or not window_title.strip():
                return False

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 1. get or create the record of process
                process_id = get_or_create_process(self.db_path, process_name, executable_path)
                if process_id is None:
                    print("❌ 获取进程ID失败")
                    return False

                # 2. end the current conversation
                if self.current_session_id is not None:
                    #print('has current_session_id')
                    self.stop_current_session(None)

                # 3. start a new conversation
                self.current_session_id = start_window_session(self.db_path, process_id, window_title)

                # 🎯 检验新对话是否创建成功
                if self.current_session_id is None:
                    print("❌ 创建新会话失败")
                    return False

                # # 验证会话是否真的存在于数据库中
                # if not self._verify_session_exists(self.current_session_id):
                #     print("❌ 会话在数据库中不存在")
                #     self.current_session_id = None
                #     return False

                # print(f"✅ 成功创建会话: ID={self.current_session_id}, 进程={process_name}, 窗口={window_title}")
                return True

        except Exception as e:
            print(f"❌ 窗口切换记录失败: {e}")
            return False

    def get_current_session_info(self) -> Optional[Tuple]:
        """
        获取当前活跃会话信息

        Returns:
            Optional[Tuple]: (process_name, window_title, start_time, session_id) 或 None
        """
        # 检查是否有当前会话
        if self.current_session_id is None:
            return None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 查询当前会话的详细信息
                cursor.execute('''
                                SELECT p.name as process_name,
                                        ws.window_title,
                                        ws.start_time,
                                        ws.id  as session_id
                                FROM window_sessions ws
                                        JOIN processes p ON ws.process_id = p.id
                                WHERE ws.id = ?
                                    AND ws.end_time IS NULL
                                ''', (self.current_session_id,))

                result = cursor.fetchone()

                if result:
                    #process_name, window_title, start_time, session_id = result
                    return result
                else:
                    print('数据库中没有找到对应的会话，重置当前会话ID')
                    self.current_session_id = None
                    return None

        except Exception as e:
            print(f"❌ 获取当前会话信息失败: {e}")
            return None

    def stop_current_session(self,endTime:Optional[datetime]) -> bool:
        """
        停止当前活跃会话
        Returns:
            bool: 是否成功停止
        """
        if self.current_session_id is None : return False

        # TODO : acccomplish in utils
        
        try:
            return end_window_session(self.db_path, self.current_session_id,endTime)

        except Exception as e:
            print("falied when stop_current_session()",e)
            return False

    def delete_today_data(self) -> int:
        """删除今日的所有 window_sessions 记录（本地时间），并返回删除的行数"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Count rows to be deleted
                cursor.execute(
                    "SELECT COUNT(*) FROM window_sessions WHERE DATE(start_time) = DATE(?)",
                    (today,)
                )
                count = cursor.fetchone()[0] or 0

                # Delete rows
                cursor.execute(
                    "DELETE FROM window_sessions WHERE DATE(start_time) = DATE(?)",
                    (today,)
                )
                conn.commit()
                return count

        except Exception as e:
            print(f"Error deleting today's data: {e}")
            return 0

    def delete_range(self, start_date: str, end_date: str) -> int:
        """删除指定范围内的 window_sessions 记录（使用本地时间），返回删除的行数"""
        try:
            # Ensure correct date format
            start = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Count rows
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM window_sessions
                    WHERE DATE (start_time) >= DATE (?)
                      AND DATE (start_time) <= DATE (?)
                    """,
                    (start, end)
                )
                count = cursor.fetchone()[0] or 0

                # Delete rows
                cursor.execute(
                    """
                    DELETE
                    FROM window_sessions
                    WHERE DATE(start_time) >= DATE(?)
                      AND DATE(start_time) <= DATE(?)
                    """,
                    (start, end)
                )
                conn.commit()
                return count

        except Exception as e:
            print(f"Error deleting range data: {e}")
            return 0

    def close(self) -> None:
        """关闭数据库连接（如有需要）"""
        pass

    def __enter__(self):
        """上下文管理器支持"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭"""
        self.close()

