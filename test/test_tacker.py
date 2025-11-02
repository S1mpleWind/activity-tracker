from tracker.windows.windows_tracker import*
#? check the initialization of the tracker

def test_should_ignore_process():
    window_title = "system"
    tracker = WindowsTracker()
    assert tracker._should_ignore_process(window_title) is False

def test_windows_tracker():
    windows_tracker = WindowsTracker()
    windows_tracker.start_tracking()

    info = windows_tracker.get_foreground_info()
    process = windows_tracker.get_background_processes()

    print(info)
    print(process)

    windows_tracker.stop_tracking()


