# test_time_manager.py
import sys
from tracker.time_manager import TimeManager
import time
from datetime import datetime

def test_time_manager():
    # 创建时间管理器
    tm = TimeManager(max_gap_seconds=5)  # 5秒阈值便于测试
    
    print("1. 初始化后时间:")
    print(f"   内部时钟: {tm.get_internal_clock()}")
    print(f"   时间差: {tm.get_time_gap()}")
    
    # 模拟正常活动
    print("\n2. 模拟正常活动...")
    for i in range(3):
        tm.update_internal_clock()
        time.sleep(1)
        has_sleep, sleep_start, wake_time = tm.check_for_sleep()
        print(f"   第{i+1}秒 - 休眠检测: {has_sleep}")
    
    # 模拟休眠（不更新时间管理器）
    print("\n3. 模拟休眠（等待6秒）...")
    time.sleep(6)
    
    # 检查是否检测到休眠
    has_sleep, sleep_start, wake_time = tm.check_for_sleep()
    if has_sleep:
        print(f"   ✅ 检测到休眠!")
        print(f"   休眠开始: {sleep_start}")
        print(f"   恢复时间: {wake_time}")
        print(f"   休眠时长: {(wake_time - sleep_start).total_seconds():.1f}秒")
    else:
        print("   ❌ 未检测到休眠")
    
    # 重置并继续
    print("\n4. 重置时间管理器后...")
    tm.reset()
    tm.update_internal_clock()
    has_sleep, _, _ = tm.check_for_sleep()
    print(f"   休眠检测: {has_sleep}")

if __name__ == "__main__":
    test_time_manager()