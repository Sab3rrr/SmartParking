"""
用户界面模块
实现停车场管理系统的用户端界面功能
"""
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from src.database import db
from src.tool import utils


class UserWindow:
    """
    用户窗口类
    支持居民和访客两种模式
    """
    def __init__(self, root, resident_info, login_window, is_resident=True):
        """
        初始化用户窗口
        
        Args:
            root: Tkinter根窗口
            resident_info: 居民信息（访客模式为None）
            login_window: 登录窗口引用
            is_resident: 是否为居民模式
        """
        self.root = root
        self.resident_info = resident_info
        self.login_window = login_window
        self.is_resident = is_resident
        
        # 设置窗口标题
        if is_resident:
            self.root.title(f"智慧停车场 - 居民端 - {resident_info['name']}")
        else:
            self.root.title("智慧停车场 - 访客端")
        
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.minsize(700, 500)  # 设置最小窗口大小
        
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
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        
        # 设置窗口位置
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """
        创建用户界面的所有控件
        """
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部信息区域
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        if self.is_resident:
            # 居民信息显示
            info_text = f"姓名：{self.resident_info['name']}  |  车牌：{self.resident_info['plate']}  |  余额：{utils.format_balance(self.resident_info['balance'])}"
            ttk.Label(top_frame, text=info_text, font=("微软雅黑", 14)).pack(anchor=tk.W)
        else:
            # 访客模式输入
            ttk.Label(top_frame, text="访客停车，请输入车牌号：").pack(side=tk.LEFT)
            self.visitor_plate_var = tk.StringVar()
            ttk.Entry(top_frame, textvariable=self.visitor_plate_var, width=15).pack(side=tk.LEFT, padx=10)
        
        # 功能按钮区域 - 使用网格布局实现响应式设计
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill=tk.X)
        
        # 配置网格布局的权重，使按钮能够均匀分布
        for i in range(3):
            button_frame.columnconfigure(i, weight=1)
        
        # 第一行按钮
        entry_btn = ttk.Button(button_frame, text="进场登记", command=self._entry_register)
        entry_btn.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        exit_btn = ttk.Button(button_frame, text="离场结算", command=self._exit_settlement)
        exit_btn.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        query_btn = ttk.Button(button_frame, text="当前费用查询", command=self._query_current_fee)
        query_btn.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        
        # 第二行按钮
        if self.is_resident:
            recharge_btn = ttk.Button(button_frame, text="充值", command=self._recharge)
            recharge_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
            
            records_btn = ttk.Button(button_frame, text="查看记录", command=self._view_records)
            records_btn.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
            
            # 退出登录按钮放在居民模式的第二行第三列
            logout_btn = ttk.Button(button_frame, text="退出登录", command=self._logout)
            logout_btn.grid(row=1, column=2, padx=10, pady=5, sticky="ew")
        else:
            # 访客模式的退出登录按钮居中显示在第二行
            logout_btn = ttk.Button(button_frame, text="退出登录", command=self._logout)
            logout_btn.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # 信息显示区域
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(info_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.info_text = tk.Text(info_frame, height=15, width=80, font=("微软雅黑", 12), 
                                 yscrollcommand=scrollbar.set, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.info_text.yview)
        self.info_text.config(state=tk.DISABLED)
    
    def _append_info(self, text):
        """
        向信息显示区域添加文本
        
        Args:
            text: 要添加的文本
        """
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, text + "\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def _entry_register(self):
        """
        进场登记
        """
        if self.is_resident:
            plate = self.resident_info['plate']
            phone = self.resident_info['phone']
        else:
            plate = self.visitor_plate_var.get().strip()
            if not plate:
                messagebox.showerror("错误", "请输入车牌号")
                return
            phone = None
        
        # 检查是否已有未结算的记录
        existing_record = db.get_active_parking_record(plate)
        if existing_record:
            messagebox.showinfo("提示", "该车辆已经在停车场内")
            return
        
        # 创建停车记录
        entry_time = utils.now_str()
        record_type = 'resident' if self.is_resident else 'visitor'
        
        record_id = db.create_parking_record(
            plate=plate,
            phone=phone,
            entry_time=entry_time,
            record_type=record_type
        )
        
        if record_id > 0:
            self._append_info(f"进场成功！ 车牌：{plate}  进场时间：{utils.format_datetime_for_display(entry_time)}")
        else:
            messagebox.showerror("错误", "进场登记失败")
    
    def _exit_settlement(self):
        """
        离场结算
        """
        if self.is_resident:
            plate = self.resident_info['plate']
        else:
            plate = self.visitor_plate_var.get().strip()
            if not plate:
                messagebox.showerror("错误", "请输入车牌号")
                return
        
        # 获取停车记录
        record = db.get_active_parking_record(plate)
        if not record:
            messagebox.showerror("错误", "未找到该车辆的停车记录")
            return
        
        # 计算费用
        exit_time = utils.now_str()
        fee = utils.calc_fee(record['entry_time'], exit_time)
        
        if self.is_resident:
            # 居民模式：从余额扣款
            if self.resident_info['balance'] < fee:
                if messagebox.askyesno("余额不足", f"当前余额：{utils.format_balance(self.resident_info['balance'])}\n需支付：{utils.format_balance(fee)}\n是否前往充值？"):
                    self._recharge()
                return
            
            # 扣款并更新余额
            if db.update_resident_balance(self.resident_info['id'], -fee):
                # 关闭停车记录
                if db.close_parking_record(record['id'], exit_time, fee):
                    # 更新本地居民信息
                    self.resident_info = db.get_resident_by_phone(self.resident_info['phone'])
                    self._refresh_resident_info()
                    self._append_info(f"离场成功！ 费用：{utils.format_balance(fee)}  剩余余额：{utils.format_balance(self.resident_info['balance'])}")
                else:
                    messagebox.showerror("错误", "结算失败")
        else:
            # 访客模式：模拟支付
            if messagebox.askyesno("费用确认", f"停车费用：{utils.format_balance(fee)}\n确认支付？"):
                # 关闭停车记录
                if db.close_parking_record(record['id'], exit_time, fee):
                    self._append_info(f"支付成功！ 费用：{utils.format_balance(fee)}")
                else:
                    messagebox.showerror("错误", "支付失败")
    
    def _query_current_fee(self):
        """
        查询当前费用
        """
        if self.is_resident:
            plate = self.resident_info['plate']
        else:
            plate = self.visitor_plate_var.get().strip()
            if not plate:
                messagebox.showerror("错误", "请输入车牌号")
                return
        
        # 获取停车记录
        record = db.get_active_parking_record(plate)
        if not record:
            messagebox.showinfo("提示", "未找到该车辆的停车记录")
            return
        
        # 计算当前费用（使用当前时间）
        current_time = utils.now_str()
        fee = utils.calc_fee(record['entry_time'], current_time)
        duration = utils.calculate_duration(record['entry_time'])
        
        self._append_info(f"当前费用查询：")
        self._append_info(f"车牌：{plate}")
        self._append_info(f"进场时间：{utils.format_datetime_for_display(record['entry_time'])}")
        self._append_info(f"停车时长：{duration}")
        self._append_info(f"预计费用：{utils.format_balance(fee)}")
    
    def _recharge(self):
        """
        充值功能
        """
        # 创建充值窗口
        recharge_window = tk.Toplevel(self.root)
        recharge_window.title("余额充值")
        recharge_window.geometry("300x200")
        recharge_window.resizable(False, False)
        
        # 窗口居中显示
        recharge_window.update_idletasks()
        width = recharge_window.winfo_width()
        height = recharge_window.winfo_height()
        x = (recharge_window.winfo_screenwidth() // 2) - (width // 2)
        y = (recharge_window.winfo_screenheight() // 2) - (height // 2)
        recharge_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # 充值金额输入
        ttk.Label(recharge_window, text="充值金额：").pack(pady=20)
        amount_var = tk.StringVar()
        ttk.Entry(recharge_window, textvariable=amount_var, width=20).pack(pady=10)
        
        # 充值按钮
        def do_recharge():
            try:
                amount = float(amount_var.get().strip())
                if amount <= 0:
                    messagebox.showerror("错误", "请输入有效的充值金额")
                    return
                
                # 更新余额
                if db.update_resident_balance(self.resident_info['id'], amount):
                    # 更新本地居民信息
                    self.resident_info = db.get_resident_by_phone(self.resident_info['phone'])
                    self._refresh_resident_info()
                    messagebox.showinfo("成功", f"充值成功！\n当前余额：{utils.format_balance(self.resident_info['balance'])}")
                    recharge_window.destroy()
                else:
                    messagebox.showerror("错误", "充值失败")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的金额")
        
        button_frame = ttk.Frame(recharge_window)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="确认充值", command=do_recharge).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=recharge_window.destroy).pack(side=tk.LEFT, padx=10)
    
    def _view_records(self):
        """
        查看停车记录
        """
        # 创建记录窗口
        records_window = tk.Toplevel(self.root)
        records_window.title("停车记录查询")
        records_window.geometry("800x500")
        
        # 窗口居中显示
        records_window.update_idletasks()
        width = records_window.winfo_width()
        height = records_window.winfo_height()
        x = (records_window.winfo_screenwidth() // 2) - (width // 2)
        y = (records_window.winfo_screenheight() // 2) - (height // 2)
        records_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # 创建表格
        columns = ("id", "plate", "entry_time", "exit_time", "fee")
        tree = ttk.Treeview(records_window, columns=columns, show="headings")
        
        # 设置列标题
        tree.heading("id", text="记录ID")
        tree.heading("plate", text="车牌号")
        tree.heading("entry_time", text="进场时间")
        tree.heading("exit_time", text="出场时间")
        tree.heading("fee", text="费用")
        
        # 设置列宽
        tree.column("id", width=80)
        tree.column("plate", width=100)
        tree.column("entry_time", width=200)
        tree.column("exit_time", width=200)
        tree.column("fee", width=100)
        
        # 查询记录
        records = db.get_parking_records(phone=self.resident_info['phone'])
        
        # 填充数据
        for record in records:
            fee_text = utils.format_balance(record['fee']) if record['exit_time'] else "-"
            exit_time_text = utils.format_datetime_for_display(record['exit_time']) if record['exit_time'] else "-"
            
            tree.insert("", tk.END, values=(
                record['id'],
                record['plate'],
                utils.format_datetime_for_display(record['entry_time']),
                exit_time_text,
                fee_text
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 关闭按钮
        ttk.Button(records_window, text="关闭", command=records_window.destroy).pack(pady=10)
    
    def _refresh_resident_info(self):
        """
        刷新居民信息显示
        """
        # 找到顶部信息标签并更新
        if self.is_resident:
            top_frame = self.root.winfo_children()[0].winfo_children()[0]
            info_label = top_frame.winfo_children()[0]
            info_text = f"姓名：{self.resident_info['name']}  |  车牌：{self.resident_info['plate']}  |  余额：{utils.format_balance(self.resident_info['balance'])}"
            info_label.config(text=info_text)
    
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