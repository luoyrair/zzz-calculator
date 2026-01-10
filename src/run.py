#!/usr/bin/env python3
import sys
from pathlib import Path

# Windows 平台：隐藏控制台窗口
if sys.platform == "win32":
    import ctypes
    # 隐藏控制台窗口
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置日志
from src.utils.logger import logger_manager

if __name__ == "__main__":
    # 获取日志记录器
    logger = logger_manager.get_logger("main")
    logger.info("=" * 50)
    logger.info("ZZZ Calculator 启动")
    logger.info("=" * 50)

    try:
        # 导入并运行主UI
        from src.ui.ui_app import ZZZUIApplication

        app = ZZZUIApplication()
        exit_code = app.run()
        logger.info(f"应用程序退出，代码: {exit_code}")
        logger_manager.shutdown()
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"应用程序启动失败: {e}", exc_info=True)
        logger_manager.shutdown()
        sys.exit(1)
