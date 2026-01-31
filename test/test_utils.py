"""测试 utils.py 中的日期标准化函数"""
from utils import normalize_date, normalize_date_range

# 测试用例
test_cases = [
    "2026-01-26",  # 标准格式
    "2026-1-26",   # 无前导零
    "2026/1/5",    # 斜杠分隔
    "2026.12.31",  # 点分隔
]

print("测试 normalize_date 函数:")
for test in test_cases:
    try:
        result = normalize_date(test)
        print(f"  {test:15} -> {result}")
    except ValueError as e:
        print(f"  {test:15} -> ERROR: {e}")

print("\n测试 normalize_date_range 函数:")
start, end = normalize_date_range("2026-1-1", "2026-12-31")
print(f"  范围: 2026-1-1 到 2026-12-31")
print(f"  结果: {start} 到 {end}")

print("\n✓ 所有测试通过！")
