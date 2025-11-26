# src/main.py
"""重构后的主程序入口"""
import tkinter as tk
import atexit

from src.config import config_manager
from src.ui.main_window import MainWindow
from src.core.service_factory import get_service_factory
from src.utils.file_processor import FileManagementService


def initialize_application():
    """初始化应用程序"""
    # 初始化文件管理服务
    file_service = FileManagementService()

    print("🚀 初始化应用程序...")

    # 初始化数据目录
    init_result = file_service.initialize_data_directory()

    if not init_result["success"]:
        print("❌ 数据目录初始化失败")
        return False

    print("✅ 数据目录初始化完成")

    # 初始化配置
    if not config_manager.initialize():
        print("❌ 配置初始化失败")
        return False

    print("✅ 配置初始化完成")

    # # 检查系统状态
    # status = file_service.get_system_status()
    #
    # if status["data_status"]["completion_rate"] < 100:
    #     print(f"⚠️ 数据不完整: {status['data_status']['completion_rate']:.1f}%")
    #     if status["network_status"] == "connected":
    #         print("💡 检测到网络连接，可以下载缺失数据")
    #     else:
    #         print("💡 请检查网络连接后下载缺失数据")
    # else:
    #     print("✅ 数据完整性检查通过")

    return True


def main():
    """主程序入口"""

    # 初始化应用程序
    if not initialize_application():
        print("❌ 应用程序初始化失败，程序无法启动")
        return

    # 创建主窗口
    root = tk.Tk()
    app = MainWindow(root)

    # 注册退出清理
    atexit.register(cleanup)

    try:
        print("🎮 启动主界面...")
        root.mainloop()
    except Exception as e:
        print(f"程序运行错误: {e}")
    finally:
        cleanup()


def cleanup():
    """清理资源"""
    # 关闭服务
    service_factory = get_service_factory()
    service_factory.shutdown()


if __name__ == "__main__":
    main()