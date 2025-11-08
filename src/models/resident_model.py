import json
from datetime import datetime
import re


class Resident:
    """
    居民信息模型类
    提供属性访问控制和数据验证
    """
    def __init__(self, name: str, id_card: str, address: str):
        """
        初始化居民对象
        
        Args:
            name: 居民姓名
            id_card: 身份证号
            address: 居民住址
        """
        self._name = name.strip()
        self._id_card = id_card.strip().upper()
        self._address = address.strip()
        
        # 验证数据合法性
        if not self._name:
            raise ValueError("姓名不能为空")
        if not self._validate_id_card(self._id_card):
            raise ValueError("身份证号格式不正确")
        if not self._address:
            raise ValueError("地址不能为空")
    
    @property
    def name(self) -> str:
        """
        获取居民姓名
        """
        return self._name
    
    @name.setter
    def name(self, value: str):
        """
        设置居民姓名，验证非空
        """
        if not value or not value.strip():
            raise ValueError("姓名不能为空")
        self._name = value.strip()
    
    @property
    def id_card(self) -> str:
        """
        获取身份证号
        """
        return self._id_card
    
    @id_card.setter
    def id_card(self, value: str):
        """
        设置身份证号，进行验证
        """
        if not self._validate_id_card(value):
            raise ValueError("身份证号格式不正确")
        self._id_card = value.strip().upper()
    
    @property
    def address(self) -> str:
        """
        获取居民地址
        """
        return self._address
    
    @address.setter
    def address(self, value: str):
        """
        设置居民地址，验证非空
        """
        if not value or not value.strip():
            raise ValueError("地址不能为空")
        self._address = value.strip()
    
    def _validate_id_card(self, id_card: str) -> bool:
        """
        验证身份证号
        1. 长度验证：必须为18位
        2. 出生日期验证
        3. 校验位验证
        
        Args:
            id_card: 身份证号
            
        Returns:
            bool: 验证结果
        """
        # 移除空格并转换为大写
        id_card = id_card.strip().upper()
        
        # 1. 长度验证
        if len(id_card) != 18:
            return False
        
        # 2. 格式验证
        if not re.match(r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dX]$', id_card):
            return False
        
        # 3. 出生日期验证
        try:
            birth_year = int(id_card[6:10])
            birth_month = int(id_card[10:12])
            birth_day = int(id_card[12:14])
            
            # 验证日期是否有效
            datetime(birth_year, birth_month, birth_day)
            
            # 验证日期范围
            if birth_year < 1900 or birth_year > datetime.now().year:
                return False
        except (ValueError, IndexError):
            return False
        
        # 4. 校验位验证
        coefficients = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        check_sum = 0
        for i in range(17):
            check_sum += int(id_card[i]) * coefficients[i]
        
        check_code = check_codes[check_sum % 11]
        
        return id_card[17] == check_code
    
    def to_json(self) -> str:
        """
        将居民信息转换为JSON字符串
        
        Returns:
            str: JSON格式的居民信息
        """
        data = {
            "name": self._name,
            "id_card": self._id_card,
            "address": self._address
        }
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Resident':
        """
        从JSON字符串创建居民对象
        
        Args:
            json_str: JSON格式的居民信息
            
        Returns:
            Resident: 居民对象
        """
        try:
            data = json.loads(json_str)
            
            # 检查必要字段
            required_fields = ['name', 'id_card', 'address']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"缺少必要字段: {field}")
            
            return cls(
                name=data['name'],
                id_card=data['id_card'],
                address=data['address']
            )
        except json.JSONDecodeError:
            raise ValueError("JSON格式错误")


class ResidentManager:
    """
    居民信息管理类
    管理多个居民对象
    """
    def __init__(self):
        """
        初始化居民管理器
        """
        self._residents = []  # 存储居民对象的列表
    
    def add_resident(self, resident: Resident) -> bool:
        """
        添加居民
        
        Args:
            resident: 居民对象
            
        Returns:
            bool: 添加结果，若身份证号已存在则返回False
        """
        # 检查身份证号是否已存在
        for r in self._residents:
            if r.id_card == resident.id_card:
                return False
        
        self._residents.append(resident)
        return True
    
    def remove_resident(self, id_card: str) -> bool:
        """
        根据身份证号删除居民
        
        Args:
            id_card: 身份证号
            
        Returns:
            bool: 删除结果
        """
        for i, resident in enumerate(self._residents):
            if resident.id_card == id_card:
                del self._residents[i]
                return True
        return False
    
    def get_resident_by_id_card(self, id_card: str) -> Resident:
        """
        根据身份证号获取居民
        
        Args:
            id_card: 身份证号
            
        Returns:
            Resident: 居民对象，不存在则返回None
        """
        for resident in self._residents:
            if resident.id_card == id_card:
                return resident
        return None
    
    def to_json_list(self) -> str:
        """
        将所有居民信息转换为JSON列表
        
        Returns:
            str: JSON格式的居民信息列表
        """
        residents_data = []
        for resident in self._residents:
            residents_data.append(json.loads(resident.to_json()))
        
        return json.dumps(residents_data, ensure_ascii=False)