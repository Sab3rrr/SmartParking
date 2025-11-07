"""
管理员界面模块
实现停车场管理系统的管理员端界面功能
"""
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from datetime import datetime, timedelta

import db
import utils
import config
from models.resident_pydantic import ResidentPydantic
from models.resident_model import Resident


class AdminWindow:
    """
    管理员窗口类
    提供完整的停车场管理功能
    """
    def __init__(self, root, login_window):
        """
        初始化管理员窗口
        
        Args:
            root: Tkinter根窗口
            login_window: 登录窗口引用
        """
        self.root = root
        self.login_window = login_window
        self.root.title("智慧停车场 - 管理员端")
        self.root.geometry("1000x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 窗口居中显示
        self._center_window()
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("微软雅黑", 12))
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TEntry", font=("微软雅黑", 10))
        
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
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        
        # 设置窗口位置
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """
        创建管理员界面的所有控件
        """
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧导航栏
        self.nav_frame = ttk.Frame(main_frame, width=180)
        self.nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # 右侧主内容区域
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建导航按钮
        self._create_nav_buttons()
        
        # 默认显示仪表盘
        self._show_dashboard()
    
    def _create_nav_buttons(self):
        """
        创建左侧导航按钮
        """
        nav_buttons = [
            ("仪表盘", self._show_dashboard),
            ("居民管理", self._show_resident_management),
            ("在场车辆", self._show_current_vehicles),
            ("停车记录", self._show_parking_records),
            ("收入统计", self._show_revenue_statistics),
            ("系统设置", self._show_system_settings),
            ("退出登录", self._logout)
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(self.nav_frame, text=text, command=command, width=15)
            btn.pack(pady=5, padx=10, fill=tk.X)
    
    def _clear_content(self):
        """
        清空主内容区域
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_dashboard(self):
        """
        显示仪表盘
        """
        self._clear_content()
        
        # 标题
        ttk.Label(self.content_frame, text="仪表盘", font=("微软雅黑", 16, "bold")).pack(pady=10)
        
        # 统计卡片
        stats_frame = ttk.Frame(self.content_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # 获取当前统计数据
        parked_count = db.get_current_parked_count()
        
        # 总车辆数
        total_frame = ttk.LabelFrame(stats_frame, text="总车辆数", width=200, height=100)
        total_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        ttk.Label(total_frame, text=str(parked_count['total']), font=("微软雅黑", 24, "bold")).pack(pady=20)
        
        # 居民车辆数
        resident_frame = ttk.LabelFrame(stats_frame, text="居民车辆", width=200, height=100)
        resident_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        ttk.Label(resident_frame, text=str(parked_count['resident']), font=("微软雅黑", 24, "bold")).pack(pady=20)
        
        # 访客车辆数
        visitor_frame = ttk.LabelFrame(stats_frame, text="访客车辆", width=200, height=100)
        visitor_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        ttk.Label(visitor_frame, text=str(parked_count['visitor']), font=("微软雅黑", 24, "bold")).pack(pady=20)
        
        # 今日收入
        today = datetime.now().strftime("%Y-%m-%d")
        today_revenue = db.get_revenue_statistics(today + " 00:00:00", today + " 23:59:59")
        total_revenue = sum(revenue for _, revenue in today_revenue)
        
        revenue_frame = ttk.LabelFrame(stats_frame, text="今日收入", width=200, height=100)
        revenue_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        ttk.Label(revenue_frame, text=utils.format_balance(total_revenue), font=("微软雅黑", 20, "bold")).pack(pady=20)
        
        # 最近停车记录
        ttk.Label(self.content_frame, text="最近停车记录", font=("微软雅黑", 14)).pack(pady=10, anchor=tk.W)
        
        columns = ("id", "plate", "entry_time", "type", "status")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # 查询最近10条记录
        records = db.get_parking_records()[:10]
        
        for record in records:
            status = "在场" if not record['exit_time'] else "已离场"
            tree.insert("", tk.END, values=(
                record['id'],
                record['plate'],
                utils.format_datetime_for_display(record['entry_time']),
                "居民" if record['type'] == 'resident' else "访客",
                status
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def _show_resident_management(self):
        """
        显示居民管理界面
        """
        self._clear_content()
        
        # 标题
        ttk.Label(self.content_frame, text="居民管理", font=("微软雅黑", 16, "bold")).pack(pady=10)
        
        # 搜索框
        search_frame = ttk.Frame(self.content_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="搜索：").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=search_var, width=30).pack(side=tk.LEFT, padx=10)
        
        def search():
            keyword = search_var.get().strip()
            # 这里可以实现搜索逻辑
            messagebox.showinfo("提示", f"搜索关键词：{keyword}")
        
        ttk.Button(search_frame, text="搜索", command=search).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="新增居民", command=self._add_resident).pack(side=tk.RIGHT)
        
        # 居民列表
        columns = ("id", "name", "phone", "plate", "balance", "address")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        
        tree.heading("id", text="ID")
        tree.heading("name", text="姓名")
        tree.heading("phone", text="手机号")
        tree.heading("plate", text="车牌号")
        tree.heading("balance", text="余额")
        tree.heading("address", text="地址")
        
        tree.column("id", width=50)
        tree.column("name", width=100)
        tree.column("phone", width=120)
        tree.column("plate", width=100)
        tree.column("balance", width=100)
        tree.column("address", width=300)
        
        # 获取所有居民
        residents = db.get_all_residents()
        
        for resident in residents:
            tree.insert("", tk.END, values=(
                resident['id'],
                resident['name'],
                resident['phone'],
                resident['plate'],
                utils.format_balance(resident['balance']),
                resident['address']
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 按钮组
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        def edit_resident():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("提示", "请选择要编辑的居民")
                return
            
            item = tree.item(selected[0])
            resident_id = item['values'][0]
            # 这里可以实现编辑逻辑
            messagebox.showinfo("提示", f"编辑居民ID：{resident_id}")
        
        def delete_resident():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("提示", "请选择要删除的居民")
                return
            
            if messagebox.askyesno("确认", "确定要删除该居民吗？"):
                # 这里可以实现删除逻辑
                messagebox.showinfo("提示", "删除功能待实现")
        
        ttk.Button(btn_frame, text="编辑", command=edit_resident).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="删除", command=delete_resident).pack(side=tk.LEFT, padx=10)
    
    def _show_current_vehicles(self):
        """
        显示在场车辆界面
        """
        self._clear_content()
        
        # 标题
        ttk.Label(self.content_frame, text="在场车辆", font=("微软雅黑", 16, "bold")).pack(pady=10)
        
        # 车辆列表
        columns = ("id", "plate", "entry_time", "type", "duration")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        
        tree.heading("id", text="记录ID")
        tree.heading("plate", text="车牌号")
        tree.heading("entry_time", text="进场时间")
        tree.heading("type", text="类型")
        tree.heading("duration", text="停车时长")
        
        tree.column("id", width=80)
        tree.column("plate", width=120)
        tree.column("entry_time", width=200)
        tree.column("type", width=100)
        tree.column("duration", width=120)
        
        # 查询所有未离场的记录
        records = db.get_parking_records()
        active_records = [r for r in records if not r['exit_time']]
        
        for record in active_records:
            duration = utils.calculate_duration(record['entry_time'])
            tree.insert("", tk.END, values=(
                record['id'],
                record['plate'],
                utils.format_datetime_for_display(record['entry_time']),
                "居民" if record['type'] == 'resident' else "访客",
                duration
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def _show_parking_records(self):
        """
        显示停车记录查询界面
        """
        self._clear_content()
        
        # 标题
        ttk.Label(self.content_frame, text="停车记录查询", font=("微软雅黑", 16, "bold")).pack(pady=10)
        
        # 查询条件
        filter_frame = ttk.LabelFrame(self.content_frame, text="查询条件")
        filter_frame.pack(fill=tk.X, pady=10)
        
        # 车牌号
        ttk.Label(filter_frame, text="车牌号：").grid(row=0, column=0, padx=10, pady=10)
        plate_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=plate_var, width=15).grid(row=0, column=1, padx=10, pady=10)
        
        # 类型
        ttk.Label(filter_frame, text="类型：").grid(row=0, column=2, padx=10, pady=10)
        type_var = tk.StringVar(value="all")
        ttk.Combobox(filter_frame, textvariable=type_var, values=["all", "resident", "visitor"], width=10).grid(row=0, column=3, padx=10, pady=10)
        
        # 日期范围
        ttk.Label(filter_frame, text="开始日期：").grid(row=1, column=0, padx=10, pady=10)
        start_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=start_date_var, width=15).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(filter_frame, text="结束日期：").grid(row=1, column=2, padx=10, pady=10)
        end_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=end_date_var, width=15).grid(row=1, column=3, padx=10, pady=10)
        
        # 查询按钮
        def do_query():
            plate = plate_var.get().strip()
            record_type = None if type_var.get() == "all" else type_var.get()
            start_time = start_date_var.get().strip() + " 00:00:00" if start_date_var.get().strip() else None
            end_time = end_date_var.get().strip() + " 23:59:59" if end_date_var.get().strip() else None
            
            # 查询记录
            records = db.get_parking_records(plate, start_time, end_time, record_type)
            
            # 清空表格
            for item in tree.get_children():
                tree.delete(item)
            
            # 填充数据
            for record in records:
                fee_text = utils.format_balance(record['fee']) if record['exit_time'] else "-"
                exit_time_text = utils.format_datetime_for_display(record['exit_time']) if record['exit_time'] else "-"
                
                tree.insert("", tk.END, values=(
                    record['id'],
                    record['plate'],
                    record['phone'] if record['phone'] else "-",
                    utils.format_datetime_for_display(record['entry_time']),
                    exit_time_text,
                    "居民" if record['type'] == 'resident' else "访客",
                    fee_text
                ))
        
        ttk.Button(filter_frame, text="查询", command=do_query).grid(row=0, column=4, rowspan=2, padx=20, pady=10)
        
        # 记录表格
        columns = ("id", "plate", "phone", "entry_time", "exit_time", "type", "fee")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def _show_revenue_statistics(self):
        """
        显示收入统计界面
        """
        self._clear_content()
        
        # 标题
        ttk.Label(self.content_frame, text="收入统计", font=("微软雅黑", 16, "bold")).pack(pady=10)
        
        # 统计选项
        stats_frame = ttk.Frame(self.content_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # 日期选择
        ttk.Label(stats_frame, text="统计周期：").pack(side=tk.LEFT, padx=10)
        period_var = tk.StringVar(value="week")
        period_frame = ttk.Frame(stats_frame)
        period_frame.pack(side=tk.LEFT)
        
        ttk.Radiobutton(period_frame, text="本周", variable=period_var, value="week").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_frame, text="本月", variable=period_var, value="month").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(period_frame, text="自定义", variable=period_var, value="custom").pack(side=tk.LEFT, padx=5)
        
        # 自定义日期
        custom_frame = ttk.Frame(stats_frame)
        custom_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(custom_frame, text="从：").pack(side=tk.LEFT)
        start_date_var = tk.StringVar()
        ttk.Entry(custom_frame, textvariable=start_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(custom_frame, text="到：").pack(side=tk.LEFT)
        end_date_var = tk.StringVar()
        ttk.Entry(custom_frame, textvariable=end_date_var, width=12).pack(side=tk.LEFT, padx=5)
        
        # 统计按钮
        def do_statistics():
            period = period_var.get()
            
            if period == "week":
                # 本周
                today = datetime.now()
                start_date = today - timedelta(days=today.weekday())
                end_date = today
            elif period == "month":
                # 本月
                today = datetime.now()
                start_date = today.replace(day=1)
                end_date = today
            else:
                # 自定义
                if not start_date_var.get() or not end_date_var.get():
                    messagebox.showinfo("提示", "请输入自定义日期范围")
                    return
                try:
                    start_date = datetime.strptime(start_date_var.get(), "%Y-%m-%d")
                    end_date = datetime.strptime(end_date_var.get(), "%Y-%m-%d")
                except ValueError:
                    messagebox.showinfo("提示", "日期格式错误，请使用YYYY-MM-DD格式")
                    return
            
            # 格式化日期
            start_str = start_date.strftime("%Y-%m-%d 00:00:00")
            end_str = end_date.strftime("%Y-%m-%d 23:59:59")
            
            # 获取统计数据
            statistics = db.get_revenue_statistics(start_str, end_str)
            
            # 清空表格
            for item in tree.get_children():
                tree.delete(item)
            
            # 填充数据
            total_revenue = 0
            for date_str, revenue in statistics:
                tree.insert("", tk.END, values=(date_str, utils.format_balance(revenue)))
                total_revenue += revenue
            
            # 显示总收入
            total_label.config(text=f"总收入：{utils.format_balance(total_revenue)}")
        
        ttk.Button(stats_frame, text="统计", command=do_statistics).pack(side=tk.LEFT, padx=20)
        
        # 统计结果表格
        columns = ("date", "revenue")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        
        tree.heading("date", text="日期")
        tree.heading("revenue", text="收入")
        
        tree.column("date", width=200)
        tree.column("revenue", width=150)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 总收入
        total_label = ttk.Label(self.content_frame, text="总收入：¥ 0.00", font=("微软雅黑", 14))
        total_label.pack(pady=10, anchor=tk.E)
    
    def _show_system_settings(self):
        """
        显示系统设置界面
        """
        self._clear_content()
        
        # 标题
        ttk.Label(self.content_frame, text="系统设置", font=("微软雅黑", 16, "bold")).pack(pady=10)
        
        # 设置项
        settings_frame = ttk.Frame(self.content_frame)
        settings_frame.pack(fill=tk.X, pady=20)
        
        # 停车费率设置
        ttk.Label(settings_frame, text="停车费率（元/小时）：").grid(row=0, column=0, padx=50, pady=20, sticky=tk.W)
        rate_var = tk.StringVar(value=str(config.PARKING_RATE_PER_HOUR))
        ttk.Entry(settings_frame, textvariable=rate_var, width=10).grid(row=0, column=1, pady=20)
        
        def update_rate():
            try:
                new_rate = float(rate_var.get().strip())
                if new_rate < 0:
                    messagebox.showerror("错误", "费率不能为负数")
                    return
                config.PARKING_RATE_PER_HOUR = new_rate
                messagebox.showinfo("成功", "费率更新成功")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的费率")
        
        ttk.Button(settings_frame, text="更新费率", command=update_rate).grid(row=0, column=2, padx=20, pady=20)
        
        # 管理员管理
        admin_frame = ttk.LabelFrame(self.content_frame, text="管理员管理")
        admin_frame.pack(fill=tk.X, pady=20, padx=50)
        
        def add_admin():
            username = simpledialog.askstring("添加管理员", "请输入用户名：")
            if username:
                password = simpledialog.askstring("添加管理员", "请输入密码：", show="*")
                if password:
                    # 这里可以实现添加管理员的逻辑
                    messagebox.showinfo("提示", "添加管理员功能待实现")
        
        def change_password():
            old_password = simpledialog.askstring("修改密码", "请输入旧密码：", show="*")
            if old_password:
                # 这里可以实现修改密码的逻辑
                messagebox.showinfo("提示", "修改密码功能待实现")
        
        ttk.Button(admin_frame, text="添加管理员", command=add_admin).pack(side=tk.LEFT, padx=30, pady=20)
        ttk.Button(admin_frame, text="修改密码", command=change_password).pack(side=tk.LEFT, padx=30, pady=20)
    
    def _add_resident(self):
        """
        添加居民（管理员模式）
        """
        # 创建注册窗口
        register_window = tk.Toplevel(self.root)
        register_window.title("添加居民")
        register_window.geometry("500x450")
        register_window.resizable(False, False)
        
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
                    messagebox.showinfo("成功", "添加成功！")
                    register_window.destroy()
                    # 刷新居民列表
                    self._show_resident_management()
                else:
                    messagebox.showerror("错误", "手机号或车牌号已存在")
                    
            except ValueError as e:
                messagebox.showerror("错误", str(e))
            except Exception as e:
                messagebox.showerror("错误", f"添加失败：{str(e)}")
        
        button_frame = ttk.Frame(register_window)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="添加", command=register).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=register_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def _logout(self):
        """
        退出登录
        """
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            self.root.destroy()
            self.login_window.deiconify()
    
    def _on_close(self):
        """
        窗口关闭事件处理
        """
        self.root.destroy()
        self.login_window.deiconify()