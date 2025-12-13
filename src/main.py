# main.py
"""主入口文件"""
import tkinter as tk
from src.ui.main_window import MainWindow


def main():
    """主函数"""
    root = tk.Tk()
    app = MainWindow(root)

    # 运行应用程序
    root.mainloop()


if __name__ == "__main__":
    main()