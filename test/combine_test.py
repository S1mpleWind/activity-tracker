from tracker.windows.windows_tracker import*

from data import*
from data.database import ActivityDatabase
from data.data_analysis import DataAnalyzer
from data.visualize import Visualize
from tracker import *
from tracker.windows.windows_tracker import WindowsTracker
from data.database_utils import*
import time


def not_format_test_a_period():
    """
    test a period in a day
    :return:
    """
    tracker = WindowsTracker()
    db = ActivityDatabase()
    da = DataAnalyzer()
    v = Visualize()

    tracker.start_tracking()

    for i in range(600):
        if i % 20 == 0 : print("running %f minutes" % (i/10))
        # 获取当前窗口
        current_process, current_title = tracker.get_foreground_info()

        # 获取当前会话信息
        current_session = db.get_current_session_info()

        if current_session is None:
            # 没有当前会话，创建新会话
            db.record_window_switch(current_process, current_title)

        else:
            # 检查窗口是否变化
            session_process, session_title, _, _ = current_session
            if current_process != session_process or current_title != session_title:
                # 窗口变化了，创建新会话
                db.record_window_switch(current_process, current_title)

        time.sleep(6)

    tracker.stop_tracking()
    db.stop_current_session()

    result = da.get_daily_usage()

    v.visualize_daily(result)

def __main__():
    not_format_test_a_period()

if __name__ == '__main__':
    __main__()


