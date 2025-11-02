# data/windows/window_tracker.py
# a subclass for windows system
import win32gui
import win32process
import psutil
from typing import Tuple, Optional, List, Dict, Any
from tracker.process_tracker import BaseTracker


class WindowsTracker(BaseTracker):
    """Windows 平台进程追踪器"""

    def __init__(self, config: Any = None):
        super().__init__(config)
        print("初始化 Windows 进程追踪器")

    def get_foreground_info(self) -> Tuple[Optional[str], Optional[str]]:
        """
        get the infomation of foreground window
        :param
        :return: a tuple of [process_name, window_title]
        """
        try:
            # 1. get the handle of the frontground window
            hwnd = win32gui.GetForegroundWindow()

            # 2. get the title of the window
            window_title = win32gui.GetWindowText(hwnd)

            # 3. check if should ignore
            if not window_title or self._should_ignore_process( window_title):
                return None, None

            # 4. get the pid
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # 5. use psutil to search the corresponding name of pid
            process = psutil.Process(pid)
            process_name = process.name()

            return process_name, window_title

        except psutil.NoSuchProcess:
            # 进程已结束
            return None, window_title if window_title else None
        except psutil.AccessDenied:
            # 无权限访问进程
            return None, window_title if window_title else None
        except Exception as e:
            print(f"获取前台窗口信息失败: {e}")
            return None, None


    def get_background_processes(self) -> List[Dict[str, Any]]:
        """Windows OS, fetching background processes info
        :param
        :return return a list of dictionary{process_name, window_title}
        """
        background_apps = []

        def enum_callback(hwnd, results):
            """
            callback function
            :param hwnd:
            :param results:
            :return:
            """
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                foreground_hwnd = win32gui.GetForegroundWindow()

                # exclude the foreground window
                if hwnd != foreground_hwnd:
                    window_title = win32gui.GetWindowText(hwnd)
                    # filter the space in window title
                    if window_title and window_title.strip():
                        try:
                            # get the process name using pid
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process = psutil.Process(pid)
                            process_name = process.name()
                            #print("entering try")
                            # print(process_name)
                            if not self._should_ignore_process(window_title):
                                background_apps.append({
                                    'process_name': process_name,
                                    'window_title': window_title
                                    #'pid': pid,
                                    #'platform': 'windows'
                                    # TODO: pid function is of no use right now
                                })
                        except:
                            pass

        win32gui.EnumWindows(enum_callback, background_apps)
        return background_apps

    def get_windows_process_details(pid: int) -> Dict[str, Any]:
        """Windows show details
        TODO: pass
        """
        try:
            process = psutil.Process(pid)
            return {
                'name': process.name(),
                'exe': process.exe(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'status': process.status(),
                'create_time': process.create_time()
            }
        except:
            return {}