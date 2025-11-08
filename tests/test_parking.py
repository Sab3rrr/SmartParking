import pytest
import os
import datetime
from src.database.db import init_db, register_resident, get_resident_by_plate, create_parking_record, get_resident_by_phone

class TestParkingSystem:
    """停车场系统测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 使用测试数据库
        self.test_db_path = "test_parking.db"
        
        # 设置测试数据库路径
        import config.cfg as cfg
        self.original_db_path = cfg.DB_PATH
        cfg.DB_PATH = self.test_db_path
        
        # 初始化测试数据库
        init_db()
        
        # 添加测试居民数据
        self.test_plate = "京A12345"
        register_resident(
            name="测试居民",
            id_card="110101199001011234",
            phone="13800138000",
            plate=self.test_plate,
            address="测试地址",
            balance=100.0,
            birth_date="1990-01-01"
        )
        
    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 恢复原始数据库路径
        import config.cfg as cfg
        cfg.DB_PATH = self.original_db_path
        
        # 删除测试数据库文件
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_create_parking_record(self):
        """测试创建停车记录"""
        # 创建停车记录
        entry_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_id = create_parking_record(
            plate=self.test_plate,
            phone="13800138000",
            entry_time=entry_time,
            record_type="resident"
        )
        
        # 验证记录ID
        assert record_id is not None
        assert isinstance(record_id, int)
        assert record_id > 0
    
    def test_register_resident(self):
        """测试注册居民"""
        # 使用时间戳生成唯一数据
        import time
        timestamp = int(time.time())
        
        # 注册新居民
        result = register_resident(
            name="新居民",
            phone=f"139001{timestamp % 100000:05d}",  # 使用时间戳生成唯一手机号
            plate=f"京Z{timestamp % 100000:05d}",      # 使用时间戳生成唯一车牌号
            address="新地址",
            balance=50.0,
            id_card="110101199002021234",
            birth_date="1990-02-02"
        )
        
        assert result is True
        
        # 验证居民是否已注册
        resident = get_resident_by_phone(f"139001{timestamp % 100000:05d}")
        assert resident is not None
        assert resident["name"] == "新居民"
        assert resident["id_card"] == "110101199002021234"
    
    def test_register_duplicate_resident(self):
        """测试注册重复居民"""
        # 尝试使用相同手机号注册
        result = register_resident(
            name="重复居民",
            id_card="110101199003033456",
            phone="13800138000",  # 相同手机号
            plate="京C98765",
            address="重复地址",
            balance=30.0,
            birth_date="1990-03-03"
        )
        
        assert result is False
        
        # 尝试使用相同车牌号注册
        result = register_resident(
            name="重复居民2",
            id_card="110101199004044567",
            phone="13700137000",
            plate=self.test_plate,  # 相同车牌号
            address="重复地址2",
            balance=40.0,
            birth_date="1990-04-04"
        )
        
        assert result is False