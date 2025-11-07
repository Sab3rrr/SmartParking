from pydantic import BaseModel, field_validator
from datetime import date
import re


class ResidentPydantic(BaseModel):
    """
    居民信息Pydantic数据模型
    用于数据验证和序列化
    """
    name: str
    id_card: str
    birth_date: date
    address: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        验证姓名不能为空且不能全为空格
        """
        if not v or not v.strip():
            raise ValueError('姓名不能为空')
        return v.strip()
    
    @field_validator('id_card')
    @classmethod
    def validate_id_card(cls, v: str) -> str:
        """
        验证身份证号
        1. 格式验证：17位数字+1位校验位（数字或X）
        2. 校验位验证：使用GB11643-1999算法
        """
        # 移除空格
        v = v.strip()
        
        # 格式验证
        if not re.match(r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$', v):
            raise ValueError('身份证号格式不正确')
        
        # 校验位验证
        # 系数列表
        coefficients = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        # 校验位映射表
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        # 计算校验和
        check_sum = 0
        for i in range(17):
            check_sum += int(v[i]) * coefficients[i]
        
        # 计算校验位
        check_code = check_codes[check_sum % 11]
        
        # 验证校验位
        if v[17].upper() != check_code:
            raise ValueError('身份证号校验位错误')
        
        return v.upper()
    
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        """
        验证出生日期
        1. 不早于1900-01-01
        2. 不晚于当前日期
        """
        if v < date(1900, 1, 1):
            raise ValueError('出生日期不能早于1900年1月1日')
        if v > date.today():
            raise ValueError('出生日期不能晚于当前日期')
        return v
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        """
        验证地址不能为空且不能全为空格
        """
        if not v or not v.strip():
            raise ValueError('地址不能为空')
        return v.strip()