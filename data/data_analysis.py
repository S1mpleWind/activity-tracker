import sqlite3
from typing import List, Dict, Any
from datetime import datetime, timedelta


class DataAnalyzer:
    def __init__(self, db_path: str = "activity.db"):
        self.db_path = db_path

    def get_today_summary(self) -> Dict[str, Any]:
        """
        获取今日使用摘要
        :param
        :return: A dictionary containing :
                                        total hours:
                                        total minutes:
                                        list [ app usage]
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 总使用时间
            cursor.execute('''
                            SELECT SUM(duration_seconds)
                            FROM window_sessions
                            WHERE DATE (start_time) = DATE ('now')
                            ''')
            total_seconds = cursor.fetchone()[0] or 0

            # 按应用统计
            cursor.execute('''
                            SELECT p.name, SUM(ws.duration_seconds) as total_seconds
                            FROM window_sessions ws
                                    JOIN processes p ON ws.process_id = p.id
                            WHERE DATE (ws.start_time) = DATE ('now')
                            GROUP BY p.name
                            ORDER BY total_seconds DESC
                            ''')

            app_usage = []
            for name, seconds in cursor.fetchall():
                app_usage.append({
                    'name': name,
                    'hours': round(seconds / 3600, 2),
                    'minutes': seconds // 60
                })

            return {
                'total_hours': round(total_seconds / 3600, 2),
                'total_minutes': total_seconds // 60,
                'app_usage': app_usage
            }


#TODO： ============== the following functions are not accomplished / need test =====================

    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的活动记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            SELECT p.name, ws.window_title, ws.start_time, ws.duration_seconds
                            FROM window_sessions ws
                                    JOIN processes p ON ws.process_id = p.id
                            ORDER BY ws.start_time DESC LIMIT ?
                            ''', (limit,))

            activities = []
            for name, title, start_time, duration in cursor.fetchall():
                activities.append({
                    'process': name,
                    'window_title': title,
                    'start_time': start_time,
                    'duration_minutes': duration // 60
                })

            return activities

    def get_top_apps(self, days: int = 1, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最常用的应用"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            SELECT p.name, SUM(ws.duration_seconds) as total_seconds
                            FROM window_sessions ws
                                    JOIN processes p ON ws.process_id = p.id
                            WHERE DATE (ws.start_time) >= DATE ('now', ?)
                            GROUP BY p.name
                            ORDER BY total_seconds DESC
                               LIMIT ?
                           ''', (f'-{days} days', limit))

            top_apps = []
            for name, seconds in cursor.fetchall():
                top_apps.append({
                    'name': name,
                    'total_hours': round(seconds / 3600, 2),
                    'total_minutes': seconds // 60
                })

            return top_apps

    def get_daily_usage(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取每日使用时间"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            SELECT DATE (start_time), SUM (duration_seconds)
                            FROM window_sessions
                            WHERE DATE (start_time) >= DATE ('now', ?)
                            GROUP BY DATE (start_time)
                            ORDER BY DATE (start_time)
                            ''', (f'-{days} days',))

            daily_usage = []
            for date_str, seconds in cursor.fetchall():
                daily_usage.append({
                    'date': date_str,
                    'total_hours': round(seconds / 3600, 2),
                    'total_minutes': seconds // 60
                })

            return daily_usage

    def get_today_activities(self) -> List[Dict[str, Any]]:
        """获取今日的所有活动记录（按时间排序）

        返回每条记录的进程名、窗口标题、开始时间和持续分钟数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                            SELECT p.name, ws.window_title, ws.start_time, ws.duration_seconds
                            FROM window_sessions ws
                                    JOIN processes p ON ws.process_id = p.id
                            WHERE DATE(ws.start_time) = DATE('now')
                            ORDER BY ws.start_time
                            ''')

            activities = []
            for name, title, start_time, duration in cursor.fetchall():
                activities.append({
                    'process': name,
                    'window_title': title,
                    'start_time': start_time,
                    'duration_minutes': duration // 60
                })

            return activities

    def get_usage_between(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取在指定日期范围内（包含两端）的按应用聚合使用时间

        Args:
            start_date: 起始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'

        Returns:
            List[Dict]: 每个应用的 {'name','hours','minutes'} 列表，按时长降序
        """
        # Normalize dates - basic validation
        try:
            # ensure parseable
            _ = datetime.strptime(start_date, "%Y-%m-%d")
            _ = datetime.strptime(end_date, "%Y-%m-%d")
        except Exception:
            raise ValueError("start_date 和 end_date 必须为 'YYYY-MM-DD' 格式")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 先检查是否有该日期范围内的数据
            cursor.execute('''
                            SELECT COUNT(*) FROM window_sessions 
                            WHERE DATE(start_time) >= DATE(?) AND DATE(start_time) <= DATE(?)
                            ''', (start_date, end_date))
            count = cursor.fetchone()[0]
            print(f"DEBUG: 日期范围 {start_date} 到 {end_date} 中有 {count} 条记录")
            
            cursor.execute('''
                            SELECT p.name, SUM(ws.duration_seconds) as total_seconds
                            FROM window_sessions ws
                                    JOIN processes p ON ws.process_id = p.id
                            WHERE DATE(ws.start_time) >= DATE(?) AND DATE(ws.start_time) <= DATE(?)
                            GROUP BY p.name
                            ORDER BY total_seconds DESC
                            ''', (start_date, end_date))

            app_usage = []
            for name, seconds in cursor.fetchall():
                seconds = seconds or 0
                app_usage.append({
                    'name': name,
                    'hours': round(seconds / 3600, 2),
                    'minutes': seconds // 60
                })
            
            print(f"DEBUG: 获取到 {len(app_usage)} 个应用的使用数据")

            return app_usage