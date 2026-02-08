import abc
import psutil
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any


class BaseTracker(abc.ABC):
    """
    进程追踪器抽象基类
    定义所有平台都需要实现的接口
    """

    def __init__(self, config: Any = None):
        self.config = config

        self.current_foreground_pid = None
        self.current_process_name = None
        self.current_window_title = None

        self.last_activity_time = datetime.now()
        self.is_tracking = False
        self.activity_history = []

    @abc.abstractmethod
    def get_foreground_info(self) -> Tuple[Optional[str], Optional[str]]:
        """获取前台窗口信息 - 必须由子类实现"""
        pass

    @abc.abstractmethod
    def get_background_processes(self) -> List[Dict[str, Any]]:
        """获取后台进程列表 - 必须由子类实现"""
        pass


    def start_tracking(self):
        """开始追踪"""
        self.is_tracking = True

    def stop_tracking(self):
        """停止追踪"""
        self.is_tracking = False


    def _should_ignore_process(self, window_title:str) -> bool:
        if not self.config or not hasattr(self.config, 'IGNORE_WINDOW_KEYWORDS'):
            default_ignore = [
                "Program Manager", "Desktop", "Settings", "系统", "桌面"
            ]
            return any(keyword in window_title for keyword in default_ignore)

        return any(keyword in window_title for keyword in self.config.IGNORE_WINDOW_KEYWORDS)
