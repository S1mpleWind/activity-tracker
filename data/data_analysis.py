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