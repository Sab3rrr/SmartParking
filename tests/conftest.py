import pytest
import os
import sys

# 添加项目根目录到Python路径，以便导入项目模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def test_db_path():
    """提供测试数据库路径的fixture"""
    return "test_parking.db"

@pytest.fixture
def sample_resident_data():
    """提供示例居民数据的fixture"""
    return {
        "name": "测试居民",
        "id_card": "110101199001011237",
        "phone": "13800138000",
        "plate": "京A12345",
        "address": "测试地址",
        "balance": 100.0,
        "birth_date": "1990-01-01"
    }