"""
系统配置文件
定义停车场管理系统的基本配置参数
"""
import os

# 停车费率（每小时）
PARKING_RATE_PER_HOUR = 5.0

# 时间格式
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# 数据库路径 - 使用绝对路径确保正确访问
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "src", "database", "parking.db")

# 默认管理员账号
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"