from tracker.process_tracker import ProcessTracker
from data.database import ActivityDatabase
import time

def test_basic_functionality():
    """测试基础功能"""
    tracker = ProcessTracker()
    db = ActivityDatabase()

    print("开始测试活动追踪... (运行10次后自动停止)")

    for i in range(10):
        process_name, window_title = tracker.get_active_window_info()
        print(f"{i + 1}. {process_name} - {window_title[:50]}")

        db.save_activity(process_name, window_title)
        time.sleep(5)  # 5秒间隔用于测试

    print("测试完成！数据已保存到数据库。")

if __name__ == "__main__":
    test_basic_functionality()