"""
数据库操作模块
实现停车场管理系统的数据库初始化和CRUD操作
"""
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from config import DB_PATH, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD


def init_db() -> None:
    """
    初始化数据库
    创建所需的表结构并设置默认管理员账号
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建居民表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS residents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        id_card TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        plate TEXT UNIQUE NOT NULL,
        address TEXT NOT NULL,
        balance REAL DEFAULT 0.0,
        birth_date TEXT NOT NULL
    )
    ''')
    
    # 创建停车记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT NOT NULL,
        phone TEXT,
        entry_time TEXT NOT NULL,
        exit_time TEXT,
        type TEXT NOT NULL, -- 'resident' 或 'visitor'
        fee REAL DEFAULT 0.0
    )
    ''')
    
    # 创建管理员表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # 检查是否已存在管理员账号
    cursor.execute("SELECT * FROM admins WHERE username = ?", (DEFAULT_ADMIN_USERNAME,))
    if not cursor.fetchone():
        # 创建默认管理员账号
        hashed_password = hashlib.sha256(DEFAULT_ADMIN_PASSWORD.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO admins (username, password) VALUES (?, ?)",
            (DEFAULT_ADMIN_USERNAME, hashed_password)
        )
    
    conn.commit()
    conn.close()


def register_resident(
    name: str,
    phone: str,
    plate: str,
    address: str,
    balance: float,
    id_card: str,
    birth_date: str
) -> bool:
    """
    注册新居民
    
    Args:
        name: 姓名
        phone: 手机号
        plate: 车牌号
        address: 地址
        balance: 余额
        id_card: 身份证号
        birth_date: 出生日期
        
    Returns:
        bool: 注册结果
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO residents 
            (name, id_card, phone, plate, address, balance, birth_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, id_card, phone, plate, address, balance, birth_date)
        )
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # 手机号或车牌号已存在
        conn.close()
        return False


def get_resident_by_phone(phone: str) -> Optional[Dict]:
    """
    根据手机号获取居民信息
    
    Args:
        phone: 手机号
        
    Returns:
        Dict: 居民信息，不存在则返回None
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使返回结果可以通过列名访问
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM residents WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_resident_by_plate(plate: str) -> Optional[Dict]:
    """
    根据车牌号获取居民信息
    
    Args:
        plate: 车牌号
        
    Returns:
        Dict: 居民信息，不存在则返回None
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM residents WHERE plate = ?", (plate,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return dict(row)
    return None


def create_parking_record(
    plate: str,
    phone: Optional[str],
    entry_time: str,
    record_type: str
) -> int:
    """
    创建停车记录
    
    Args:
        plate: 车牌号
        phone: 手机号
        entry_time: 进场时间
        record_type: 记录类型 ('resident' 或 'visitor')
        
    Returns:
        int: 记录ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO parking_records 
        (plate, phone, entry_time, type)
        VALUES (?, ?, ?, ?)
        """,
        (plate, phone, entry_time, record_type)
    )
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id


def close_parking_record(record_id: int, exit_time: str, fee: float) -> bool:
    """
    关闭停车记录（结算）
    
    Args:
        record_id: 记录ID
        exit_time: 出场时间
        fee: 费用
        
    Returns:
        bool: 操作结果
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE parking_records 
            SET exit_time = ?, fee = ? 
            WHERE id = ? AND exit_time IS NULL
            """,
            (exit_time, fee, record_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    except Exception:
        conn.close()
        return False


def update_resident_balance(resident_id: int, amount: float) -> bool:
    """
    更新居民余额
    
    Args:
        resident_id: 居民ID
        amount: 金额（正数为充值，负数为扣款）
        
    Returns:
        bool: 操作结果
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE residents SET balance = balance + ? WHERE id = ?",
            (amount, resident_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    except Exception:
        conn.close()
        return False


def get_active_parking_record(plate: str) -> Optional[Dict]:
    """
    获取车辆的当前活跃停车记录
    
    Args:
        plate: 车牌号
        
    Returns:
        Dict: 停车记录，不存在则返回None
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT * FROM parking_records 
        WHERE plate = ? AND exit_time IS NULL 
        ORDER BY entry_time DESC LIMIT 1
        """,
        (plate,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_parking_records(plate: Optional[str] = None,
                       start_time: Optional[str] = None,
                       end_time: Optional[str] = None,
                       record_type: Optional[str] = None) -> List[Dict]:
    """
    查询停车记录
    
    Args:
        plate: 车牌号（可选）
        start_time: 开始时间（可选）
        end_time: 结束时间（可选）
        record_type: 记录类型（可选）
        
    Returns:
        List[Dict]: 停车记录列表
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM parking_records WHERE 1=1"
    params = []
    
    if plate:
        query += " AND plate = ?"
        params.append(plate)
    
    if start_time:
        query += " AND entry_time >= ?"
        params.append(start_time)
    
    if end_time:
        query += " AND entry_time <= ?"
        params.append(end_time)
    
    if record_type:
        query += " AND type = ?"
        params.append(record_type)
    
    query += " ORDER BY entry_time DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_all_residents() -> List[Dict]:
    """
    获取所有居民信息
    
    Returns:
        List[Dict]: 居民信息列表
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM residents ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def verify_admin(username: str, password: str) -> bool:
    """
    验证管理员账号
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        bool: 验证结果
    """
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM admins WHERE username = ? AND password = ?",
        (username, hashed_password)
    )
    
    result = cursor.fetchone() is not None
    conn.close()
    
    return result


def get_revenue_statistics(start_date: str, end_date: str) -> List[Tuple[str, float]]:
    """
    获取收入统计数据
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        List[Tuple[str, float]]: 日期和收入的列表
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT 
            date(entry_time) as date,
            SUM(fee) as revenue
        FROM 
            parking_records
        WHERE 
            exit_time IS NOT NULL AND
            entry_time >= ? AND
            entry_time <= ?
        GROUP BY 
            date(entry_time)
        ORDER BY 
            date(entry_time)
        """,
        (start_date, end_date)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def get_current_parked_count() -> Dict[str, int]:
    """
    获取当前在场车辆数
    
    Returns:
        Dict[str, int]: 包含总数量、居民车辆数和访客车辆数
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总数量
    cursor.execute("SELECT COUNT(*) FROM parking_records WHERE exit_time IS NULL")
    total_count = cursor.fetchone()[0]
    
    # 居民车辆数
    cursor.execute(
        "SELECT COUNT(*) FROM parking_records WHERE exit_time IS NULL AND type = 'resident'"
    )
    resident_count = cursor.fetchone()[0]
    
    # 访客车辆数
    visitor_count = total_count - resident_count
    
    conn.close()
    
    return {
        'total': total_count,
        'resident': resident_count,
        'visitor': visitor_count
    }