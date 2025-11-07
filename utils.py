"""
工具函数模块
提供停车场管理系统所需的辅助功能
"""
from datetime import datetime
import math
from typing import Optional

from config import TIME_FORMAT, PARKING_RATE_PER_HOUR


def calc_fee(entry_time: str, exit_time: str) -> float:
    """
    计算停车费用
    
    Args:
        entry_time: 进场时间字符串
        exit_time: 出场时间字符串
        
    Returns:
        float: 停车费用（向上取整小时计算）
    """
    # 转换时间字符串为datetime对象
    entry_dt = datetime.strptime(entry_time, TIME_FORMAT)
    exit_dt = datetime.strptime(exit_time, TIME_FORMAT)
    
    # 计算停车时长（秒）
    duration_seconds = (exit_dt - entry_dt).total_seconds()
    
    # 转换为小时并向上取整
    duration_hours = math.ceil(duration_seconds / 3600)
    
    # 计算费用
    fee = duration_hours * PARKING_RATE_PER_HOUR
    
    return fee


def now_str() -> str:
    """
    获取当前时间的字符串表示
    
    Returns:
        str: 当前时间，格式为TIME_FORMAT
    """
    return datetime.now().strftime(TIME_FORMAT)


def validate_phone(phone: str) -> bool:
    """
    验证手机号格式
    
    Args:
        phone: 手机号
        
    Returns:
        bool: 验证结果
    """
    # 简单的中国大陆手机号验证
    import re
    return bool(re.match(r'^1[3-9]\d{9}$', phone))


def format_balance(balance: float) -> str:
    """
    格式化余额显示
    
    Args:
        balance: 余额
        
    Returns:
        str: 格式化后的余额字符串
    """
    return f"¥ {balance:.2f}"


def format_datetime_for_display(dt_str: str) -> str:
    """
    格式化日期时间用于显示
    
    Args:
        dt_str: 日期时间字符串
        
    Returns:
        str: 格式化后的字符串
    """
    try:
        dt = datetime.strptime(dt_str, TIME_FORMAT)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return dt_str


def calculate_duration(entry_time: str, exit_time: Optional[str] = None) -> str:
    """
    计算停车时长并格式化显示
    
    Args:
        entry_time: 进场时间
        exit_time: 出场时间（可选，默认为当前时间）
        
    Returns:
        str: 格式化的时长字符串
    """
    from datetime import datetime
    
    entry_dt = datetime.strptime(entry_time, TIME_FORMAT)
    if exit_time:
        end_dt = datetime.strptime(exit_time, TIME_FORMAT)
    else:
        end_dt = datetime.now()
    
    duration_seconds = (end_dt - entry_dt).total_seconds()
    
    # 计算小时和分钟
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    
    if hours > 0:
        return f"{hours}小时{minutes}分钟"
    else:
        return f"{minutes}分钟"