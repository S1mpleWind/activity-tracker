"""
通用工具函数模块
"""
from datetime import datetime
from typing import Tuple


def normalize_date(date_str: str) -> str:
    """
    将各种日期格式标准化为 YYYY-MM-DD
    
    支持的输入格式：
    - 2026-01-26 (标准格式)
    - 2026-1-26 (无前导零)
    - 2026/01/26 (斜杠分隔)
    - 2026.1.26 (点分隔)
    
    Args:
        date_str: 日期字符串
        
    Returns:
        str: 标准化后的日期字符串 (YYYY-MM-DD)
        
    Raises:
        ValueError: 如果日期格式无效
        
    Examples:
        >>> normalize_date("2026-1-26")
        '2026-01-26'
        >>> normalize_date("2026/1/5")
        '2026-01-05'
    """
    # 替换常见分隔符为 -
    date_str = date_str.replace('/', '-').replace('.', '-')
    parts = date_str.split('-')
    
    if len(parts) != 3:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD format.")
    
    year, month, day = parts
    # 补零并返回标准格式
    normalized = f"{year.zfill(4)}-{month.zfill(2)}-{day.zfill(2)}"
    
    # 验证日期有效性
    datetime.strptime(normalized, "%Y-%m-%d")
    
    return normalized


def normalize_date_range(start: str, end: str) -> Tuple[str, str]:
    """
    标准化日期范围
    
    Args:
        start: 开始日期字符串
        end: 结束日期字符串
        
    Returns:
        Tuple[str, str]: (标准化后的开始日期, 标准化后的结束日期)
        
    Raises:
        ValueError: 如果日期格式无效
        
    Examples:
        >>> normalize_date_range("2026-1-1", "2026-1-31")
        ('2026-01-01', '2026-01-31')
    """
    return normalize_date(start), normalize_date(end)
