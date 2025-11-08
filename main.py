"""
智慧停车场管理系统主入口文件
"""
import os
import tkinter as tk
from src.database import db
from src.ui.ui_login import LoginWindow


def main():
    """
    主函数
    初始化数据库并启动应用程序
    """
    # 初始化数据库
    db.init_db()
    
    # 创建主窗口
    root = tk.Tk()
    
    # 设置窗口图标 - 使用绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "src", "image", "设计停车场系统 logo.png")
    try:
        # 尝试使用PhotoImage加载PNG图标
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)
    except tk.TclError:
        # 如果图标加载失败，打印错误信息但不影响程序运行
        print(f"无法加载图标: {icon_path}")
    
    # 创建登录窗口
    login_window = LoginWindow(root)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()