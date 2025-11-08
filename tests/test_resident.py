import pytest
import os
from src.models.resident_model import Resident, ResidentManager
from src.database.db import register_resident, get_resident_by_plate, get_resident_by_phone

class TestResident:
    """居民模型测试类"""
    
    def test_create_resident(self):
        """测试创建居民对象"""
        # 创建一个有效的居民对象
        resident = Resident(
            name="张三",
            id_card="110101199001011237",
            address="北京市朝阳区某某街道"
        )
        
        # 验证属性
        assert resident.name == "张三"
        assert resident.id_card == "110101199001011237"
        assert resident.address == "北京市朝阳区某某街道"
    
    def test_resident_validation(self):
        """测试居民数据验证"""
        # 测试空姓名
        with pytest.raises(ValueError, match="姓名不能为空"):
            Resident(
                name="",
                id_card="110101199001011237",
                address="北京市朝阳区某某街道"
            )
        
        # 测试无效身份证号
        with pytest.raises(ValueError, match="身份证号格式不正确"):
            Resident(
                name="张三",
                id_card="123456789012345678",
                address="北京市朝阳区某某街道"
            )
        
        # 测试空地址
        with pytest.raises(ValueError, match="地址不能为空"):
            Resident(
                name="张三",
                id_card="110101199001011237",
                address=""
            )


class TestResidentManager:
    """居民管理器测试类"""
    
    def test_add_resident(self):
        """测试添加居民"""
        manager = ResidentManager()
        
        # 创建居民对象
        resident = Resident(
            name="李四",
            id_card="110101199002021234",
            address="北京市海淀区某某街道"
        )
        
        # 添加居民
        result = manager.add_resident(resident)
        assert result is True
        
        # 尝试添加相同身份证的居民
        duplicate_resident = Resident(
            name="王五",
            id_card="110101199002021234",  # 相同身份证号
            address="北京市西城区某某街道"
        )
        
        result = manager.add_resident(duplicate_resident)
        assert result is False