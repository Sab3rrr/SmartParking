def generate_id_card(area_code="110101", birth_date="19900101"):
    """
    生成有效的身份证号
    
    Args:
        area_code: 地区代码，默认为北京市东城区
        birth_date: 出生日期，格式为YYYYMMDD
        
    Returns:
        str: 有效的18位身份证号
    """
    # 前17位
    id_17 = area_code + birth_date + "123"
    
    # 校验位计算
    coefficients = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    check_sum = 0
    for i in range(17):
        check_sum += int(id_17[i]) * coefficients[i]
    
    check_code = check_codes[check_sum % 11]
    
    return id_17 + check_code

# 生成几个有效的身份证号
print("有效的身份证号示例:")
print(generate_id_card("110101", "19900101"))  # 张三
print(generate_id_card("110101", "19900202"))  # 李四
print(generate_id_card("110101", "19900303"))  # 王五