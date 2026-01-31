"""测试活动分类器的中英文混合匹配能力"""
from data.activity_classifier import ActivityClassifier

classifier = ActivityClassifier()

# 测试用例
test_cases = [
    ("chrome", "YouTube - 音乐播放", "entertainment"),
    ("WeChat", "微信聊天窗口", "communication"),
    ("explorer", "我的文件夹", "system"),
    ("Code", "Python项目 - Visual Studio Code", "work"),
    ("bilibili", "哔哩哔哩 - 学习视频", "entertainment"),
    ("钉钉", "工作群聊天", "work"),
    ("QQ", "聊天窗口", "communication"),
    ("chrome", "抖音 - 娱乐短视频", "entertainment"),
    ("terminal", "PowerShell终端", "system"),
    ("notepad", "记事本 - 未知文档", "other"),
]

print("测试活动分类器 - 中英文混合匹配\n")
print("=" * 80)

passed = 0
failed = 0

for app_name, window_title, expected in test_cases:
    result = classifier.classify_activity(app_name, window_title)
    status = "✓" if result == expected else "✗"
    
    if result == expected:
        passed += 1
    else:
        failed += 1
    
    print(f"{status} App: {app_name:20} | Window: {window_title:30} | Expected: {expected:15} | Got: {result:15}")

print("=" * 80)
print(f"\n测试结果: {passed} 通过, {failed} 失败")

if failed == 0:
    print("✓ 所有测试通过！")
else:
    print(f"✗ 有 {failed} 个测试失败")
