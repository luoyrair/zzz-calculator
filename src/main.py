import tkinter as tk
from src.ui.main_window import MainWindow


def main():
    """主函数"""
    root = tk.Tk()
    app = MainWindow(root)

    # 设置窗口图标（如果有）
    # try:
    #     root.iconbitmap('icon.ico')
    # except:
    #     pass

    # 运行应用程序
    root.mainloop()


if __name__ == "__main__":
    main()