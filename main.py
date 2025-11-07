"""
智慧停车场管理系统主入口文件
"""
import tkinter as tk
import db
from ui.ui_login import LoginWindow


def main():
    """
    主函数
    初始化数据库并启动应用程序
    """
    # 初始化数据库
    db.init_db()
    
    # 创建主窗口
    root = tk.Tk()
    
    # 设置窗口图标（可选）
    # root.iconbitmap("icon.ico")
    
    # 创建登录窗口
    login_window = LoginWindow(root)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()