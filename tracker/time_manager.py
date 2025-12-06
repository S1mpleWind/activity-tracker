# time_manager.py
import time
from datetime import datetime, timedelta
from threading import Lock
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TimeManager:
    """
    简洁的时间管理器
    职责：
    1. 维护内部时钟（模拟时间流逝）
    2. 比较内部时钟与真实时间的差异
    3. 提供简单的接口：检查是否有休眠/关机事件
    """
    
    def __init__(self, max_gap_seconds: int = 60):
        """
        初始化时间管理器
        
        Args:
            max_gap_seconds: 最大允许时间差（秒），超过则认为系统休眠
        """

        import logging

        # 添加基础配置 - 这会确保日志输出到控制台
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


        self.max_gap = timedelta(seconds=max_gap_seconds)
        self._lock = Lock()
        
        # 初始化时间
        now = datetime.now()
        self._internal_clock = now      # 内部时钟
        self._last_update_time = now    # 最后一次更新时间
        
        logger.info(f"时间管理器初始化，最大时间差: {max_gap_seconds}秒")
        # print(f"时间管理器初始化，最大时间差: {max_gap_seconds}秒")
    
    def update_internal_clock(self) -> None:
        """
        更新内部时钟（调用此函数表示"时间在流逝"）
        通常在每次检测到活动时调用
        """
        with self._lock:
            now = datetime.now()
            self._internal_clock = now
            self._last_update_time = now
    
    def advance_internal_clock(self, seconds: float = 1.0) -> None:
        """
        让内部时钟前进指定秒数（模拟时间流逝）
        用于周期性调用，模拟时间的正常流逝
        """
        with self._lock:
            self._internal_clock += timedelta(seconds=seconds)
    
    def check_for_sleep(self) -> Tuple[bool, Optional[datetime], Optional[datetime]]:
        """
        检查是否有休眠/关机事件
        
        Returns:
            Tuple[bool, Optional[datetime], Optional[datetime]]:
            - bool: 是否检测到休眠
            - Optional[datetime]: 休眠开始时间（如果检测到休眠）
            - Optional[datetime]: 系统恢复时间（如果检测到休眠）
        """
        with self._lock:
            current_real_time = datetime.now()
            time_gap = current_real_time - self._internal_clock
            
            # 更新时间戳以便下次比较
            self._internal_clock = current_real_time
            self._last_update_time = current_real_time
            
            # 检查是否有显著时间跳跃
            if time_gap > self.max_gap:
                sleep_start_time = self._internal_clock - time_gap
                wake_time = current_real_time
                
                logger.info(f"检测到休眠事件: 时间跳跃 {time_gap}")
                return True, sleep_start_time, wake_time
            
            return False, None, None
    
    def get_internal_clock(self) -> datetime:
        """获取当前内部时钟时间"""
        with self._lock:
            return self._internal_clock
    
    def get_real_time(self) -> datetime:
        """获取当前真实时间"""
        return datetime.now()
    
    def get_time_gap(self) -> timedelta:
        """获取内部时钟与真实时间的差异"""
        with self._lock:
            return datetime.now() - self._internal_clock
    
    def reset(self) -> None:
        """重置内部时钟到当前真实时间"""
        with self._lock:
            now = datetime.now()
            self._internal_clock = now
            self._last_update_time = now
            logger.info("时间管理器已重置")