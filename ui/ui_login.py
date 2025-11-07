"""
登录界面模块
实现停车场管理系统的登录功能
"""
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

import db
import utils
from ui.ui_user import UserWindow
from ui.ui_admin import AdminWindow
from models.resident_pydantic import ResidentPydantic
from models.resident_model import Resident


class LoginWindow:
    """
    登录窗口类
    """
    def __init__(self, root):
        """
        初始化登录窗口
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("智慧停车场管理系统 - 登录")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 窗口居中显示
        self._center_window()
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("微软雅黑", 12))
        self.style.configure("TButton", font=("微软雅黑", 12))
        self.style.configure("TEntry", font=("微软雅黑", 12))
        
        self._create_widgets()
    
    def _center_window(self):
        """
        让窗口在屏幕上居中显示
        """
        # 获取窗口大小
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # 获取屏幕大小
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2) - 100       
        # 设置窗口位置
        self.root.geometry(f"{width}x{height+100}+{x}+{y}")
    
    def _create_widgets(self):
        """
        创建登录界面的所有控件
        """
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="智慧停车场管理系统", font=("微软雅黑", 20, "bold"))
        title_label.pack(pady=20)
        
        # 登录选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 用户登录选项卡
        user_frame = ttk.Frame(notebook, padding=20)
        notebook.add(user_frame, text="用户登录")
        
        # 管理员登录选项卡
        admin_frame = ttk.Frame(notebook, padding=20)
        notebook.add(admin_frame, text="管理员登录")
        
        # 用户登录界面
        self._create_user_login_tab(user_frame)
        
        # 管理员登录界面
        self._create_admin_login_tab(admin_frame)
        
        # 底部按钮框架 - 修改这里
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        # 注册按钮 - 放在左下角
        register_btn = ttk.Button(bottom_frame, text="居民注册", command=self._open_register_window)
        register_btn.pack(side=tk.LEFT, padx=20)
        
        # 退出按钮 - 放在右下角
        exit_btn = ttk.Button(bottom_frame, text="退出系统", command=self.root.quit)
        exit_btn.pack(side=tk.RIGHT, padx=20)
    
    def _create_user_login_tab(self, parent):
        """
        创建用户登录选项卡
        
        Args:
            parent: 父控件
        """
         # 配置网格权重，使内容居中
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        
        # 手机号输入
        ttk.Label(parent, text="手机号:").grid(row=0, column=0, padx=10, pady=15, sticky=tk.E)
        self.user_phone_var = tk.StringVar()
        phone_entry = ttk.Entry(parent, textvariable=self.user_phone_var, width=25)
        phone_entry.grid(row=0, column=1, padx=10, pady=15, sticky=tk.W)
        
        # 车牌号输入
        ttk.Label(parent, text="车牌号:").grid(row=1, column=0, padx=10, pady=15, sticky=tk.E)
        self.user_plate_var = tk.StringVar()
        plate_entry = ttk.Entry(parent, textvariable=self.user_plate_var, width=25)
        plate_entry.grid(row=1, column=1, padx=10, pady=15, sticky=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, pady=30)
        
        # 登录按钮
        login_btn = ttk.Button(button_frame, text="登录", command=self._user_login)
        login_btn.pack(side=tk.LEFT, padx=20)
        
        # 访客停车按钮
        visitor_btn = ttk.Button(button_frame, text="访客停车", command=self._visitor_login)
        visitor_btn.pack(side=tk.LEFT, padx=20)
        
    def _create_admin_login_tab(self, parent):
        """
        创建管理员登录选项卡
        
        Args:
            parent: 父控件
        """
        # 配置网格权重，使内容居中
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        # 用户名输入
        ttk.Label(parent, text="用户名:").grid(row=0, column=0, padx=10, pady=15, sticky=tk.E)
        self.admin_username_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.admin_username_var, width=25).grid(row=0, column=1, padx=10, pady=15, sticky=tk.W)
        
        # 密码输入
        ttk.Label(parent, text="密 码:").grid(row=1, column=0, padx=10, pady=15, sticky=tk.E)   
        self.admin_password_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.admin_password_var, show="*", width=25).grid(row=1, column=1, padx=10, pady=15, sticky=tk.W)
        
        # 登录按钮
        login_btn = ttk.Button(parent, text="管理员登录", command=self._admin_login)
        login_btn.place(relx=0.5, rely=0.85, anchor=tk.CENTER)
    
    def _user_login(self):
        """
        用户登录逻辑
        """
        phone = self.user_phone_var.get().strip()
        plate = self.user_plate_var.get().strip()
        
        # 验证输入
        if not phone or not plate:
            messagebox.showerror("错误", "请输入手机号和车牌号")
            return
        
        if not utils.validate_phone(phone):
            messagebox.showerror("错误", "手机号格式不正确")
            return
        
        # 查询居民信息
        resident = db.get_resident_by_phone(phone)
        
        if resident and resident['plate'] == plate:
            # 登录成功，跳转到用户界面
            self.root.withdraw()  # 隐藏登录窗口
            user_window = tk.Toplevel(self.root)
            UserWindow(user_window, resident, self.root, is_resident=True)
        else:
            # 询问是否以访客身份停车
            if messagebox.askyesno("提示", "未找到居民信息，是否以访客身份停车？"):
                self._visitor_login()
    
    def _visitor_login(self):
        """
        访客登录逻辑
        """
        self.root.withdraw()
        visitor_window = tk.Toplevel(self.root)
        UserWindow(visitor_window, None, self.root, is_resident=False)
    
    def _admin_login(self):
        """
        管理员登录逻辑
        """
        username = self.admin_username_var.get().strip()
        password = self.admin_password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        # 验证管理员账号
        if db.verify_admin(username, password):
            self.root.withdraw()
            admin_window = tk.Toplevel(self.root)
            AdminWindow(admin_window, self.root)
        else:
            messagebox.showerror("错误", "用户名或密码错误")
    
    def _open_register_window(self):
        """
        打开注册窗口
        """
        # 创建注册窗口
        register_window = tk.Toplevel(self.root)
        register_window.title("居民注册")
        register_window.geometry("500x450")
        register_window.resizable(False, False)
        
        # 窗口居中显示
        def center_register_window():
            # 获取窗口大小
            register_window.update_idletasks()
            width = register_window.winfo_width()
            height = register_window.winfo_height()
            
            # 获取屏幕大小
            x = (register_window.winfo_screenwidth() // 2) - (width // 2)
            y = (register_window.winfo_screenheight() // 2) - (height // 2)
            
            # 设置窗口位置
            register_window.geometry(f"{width}x{height}+{x}+{y}")
        
        center_register_window()
        
        # 注册表单
        ttk.Label(register_window, text="姓名:").grid(row=0, column=0, sticky=tk.W, pady=10, padx=20)
        name_var = tk.StringVar()
        ttk.Entry(register_window, textvariable=name_var, width=30).grid(row=0, column=1, pady=10)
        
        ttk.Label(register_window, text="身份证号:").grid(row=1, column=0, sticky=tk.W, pady=10, padx=20)
        id_card_var = tk.StringVar()
        ttk.Entry(register_window, textvariable=id_card_var, width=30).grid(row=1, column=1, pady=10)
        
        ttk.Label(register_window, text="出生日期:").grid(row=2, column=0, sticky=tk.W, pady=10, padx=20)
        birth_date_var = tk.StringVar()
        ttk.Entry(register_window, textvariable=birth_date_var, width=30).grid(row=2, column=1, pady=10)
        ttk.Label(register_window, text="格式：YYYY-MM-DD", font=("微软雅黑", 10)).grid(row=2, column=2, padx=10)
        
        ttk.Label(register_window, text="手机号:").grid(row=3, column=0, sticky=tk.W, pady=10, padx=20)
        phone_var = tk.StringVar()
        ttk.Entry(register_window, textvariable=phone_var, width=30).grid(row=3, column=1, pady=10)
        
        ttk.Label(register_window, text="车牌号:").grid(row=4, column=0, sticky=tk.W, pady=10, padx=20)
        plate_var = tk.StringVar()
        ttk.Entry(register_window, textvariable=plate_var, width=30).grid(row=4, column=1, pady=10)
        
        ttk.Label(register_window, text="地址:").grid(row=5, column=0, sticky=tk.NW, pady=10, padx=20)
        address_var = tk.StringVar()
        ttk.Entry(register_window, textvariable=address_var, width=30).grid(row=5, column=1, pady=10)
        
        ttk.Label(register_window, text="初始余额:").grid(row=6, column=0, sticky=tk.W, pady=10, padx=20)
        balance_var = tk.StringVar(value="0.0")
        ttk.Entry(register_window, textvariable=balance_var, width=30).grid(row=6, column=1, pady=10)
        
        # 注册按钮
        def register():
            try:
                # 获取输入值
                name = name_var.get().strip()
                id_card = id_card_var.get().strip()
                birth_date_str = birth_date_var.get().strip()
                phone = phone_var.get().strip()
                plate = plate_var.get().strip()
                address = address_var.get().strip()
                
                # 验证手机号
                if not utils.validate_phone(phone):
                    messagebox.showerror("错误", "手机号格式不正确")
                    return
                
                # 验证余额
                try:
                    balance = float(balance_var.get().strip())
                    if balance < 0:
                        messagebox.showerror("错误", "余额不能为负数")
                        return
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的余额")
                    return
                
                # 使用Pydantic验证居民信息
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
                
                # 先使用Pydantic验证核心信息
                resident_pydantic = ResidentPydantic(
                    name=name,
                    id_card=id_card,
                    birth_date=birth_date,
                    address=address
                )
                
                # 再使用Resident模型验证
                resident_model = Resident(
                    name=resident_pydantic.name,
                    id_card=resident_pydantic.id_card,
                    address=resident_pydantic.address
                )
                
                # 注册到数据库
                if db.register_resident(
                    name=resident_pydantic.name,
                    id_card=resident_pydantic.id_card,
                    birth_date=birth_date_str,
                    phone=phone,
                    plate=plate,
                    address=resident_pydantic.address,
                    balance=balance
                ):
                    messagebox.showinfo("成功", "注册成功！")
                    register_window.destroy()
                else:
                    messagebox.showerror("错误", "手机号或车牌号已存在")
                    
            except ValueError as e:
                messagebox.showerror("错误", str(e))
            except Exception as e:
                messagebox.showerror("错误", f"注册失败：{str(e)}")
        
        button_frame = ttk.Frame(register_window)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="注册", command=register).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=register_window.destroy).pack(side=tk.LEFT, padx=10)