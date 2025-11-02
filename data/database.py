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
                    self.stop_current_session()

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

                print(f"✅ 成功创建会话: ID={self.current_session_id}, 进程={process_name}, 窗口={window_title}")
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
                    process_name, window_title, start_time, session_id = result
                    return ()
                else:
                    print('数据库中没有找到对应的会话，重置当前会话ID')
                    self.current_session_id = None
                    return None

        except Exception as e:
            print(f"❌ 获取当前会话信息失败: {e}")
            return None

    def stop_current_session(self) -> bool:
        """
        停止当前活跃会话
        Returns:
            bool: 是否成功停止
        """
        if self.current_session_id is None : return False
        try:
            return end_window_session(self.db_path, self.current_session_id)

        except Exception as e:
            print("falied when stop_current_session()",e)


    def get_today_activities(self, limit: int = 50) -> List[Tuple]:
        """
        获取今日活动记录

        Args:
            limit: 返回记录数量限制

        Returns:
            List[Tuple]: 活动记录列表
        """
        pass

    def get_usage_statistics(self, days: int = 1) -> Dict[str, Any]:
        """
        获取使用统计

        Args:
            days: 统计天数

        Returns:
            Dict: 统计信息
        """
        pass

    def get_process_usage(self, process_name: str, days: int = 7) -> Dict[str, Any]:
        """
        获取特定进程的使用情况

        Args:
            process_name: 进程名称
            days: 统计天数

        Returns:
            Dict: 进程使用统计
        """
        pass

    def cleanup_old_records(self, days_to_keep: int = 30) -> int:
        """
        清理旧记录

        Args:
            days_to_keep: 保留天数

        Returns:
            int: 删除的记录数量
        """
        pass

    def export_data(self, start_date: str, end_date: str,
                    format_type: str = "json") -> Any:
        """
        导出数据

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            format_type: 导出格式 (json/csv)

        Returns:
            导出数据
        """
        pass

    def get_database_info(self) -> Dict[str, Any]:
        """
        获取数据库信息

        Returns:
            Dict: 数据库统计信息
        """
        pass

    def close(self) -> None:
        """关闭数据库连接"""
        pass

    def __enter__(self):
        """上下文管理器支持"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭"""
        self.close()