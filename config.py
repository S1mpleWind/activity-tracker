class Config:
    def __init__(self):
        self.IGNORE_WINDOW_KEYWORDS = []
        self.init_ignored_keyword()

    def init_ignored_keyword(self):
        self.IGNORE_WINDOW_KEYWORDS = [
            "Program Manager",
            "Desktop",
            "Settings",
            "系统",
            "system",
            "桌面",
            "Desktop",
            "Microsoft Text Input Application"
        ]