"""
日志工具模块 - 简洁实用
"""

import logging
import sys
from datetime import datetime

from src.config.constants import PathConstants


class AppLogger:
    """应用日志管理器"""

    # 单例实例
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._setup_logging()

    @staticmethod
    def _setup_logging():
        """设置日志配置"""
        try:
            # 创建日志目录
            log_dir = PathConstants.get_logs_dir()
            log_dir.mkdir(exist_ok=True)

            # 生成日志文件名（按日期）
            log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"

            # 配置根日志记录器
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)

            # 清除已有的处理器
            logger.handlers.clear()

            # 文件处理器（输出到文件）
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            # 控制台处理器（只在调试时使用）
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)  # 默认只显示警告及以上
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        except Exception as e:
            print(f"日志配置失败: {e}")

    @staticmethod
    def get_logger(name: str = None) -> logging.Logger:
        """获取指定名称的日志记录器"""
        return logging.getLogger(name)

    @staticmethod
    def set_console_level(level: int = logging.INFO):
        """设置控制台日志级别（用于调试）"""
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)

    @staticmethod
    def shutdown():
        """关闭日志系统"""
        logging.shutdown()


# 创建全局日志管理器
logger_manager = AppLogger()


def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器（快捷函数）"""
    return logger_manager.get_logger(name)


# 预定义常用日志记录器
def get_core_logger():
    """获取核心模块日志记录器"""
    return get_logger("core")


def get_ui_logger():
    """获取UI模块日志记录器"""
    return get_logger("ui")


def get_data_logger():
    """获取数据模块日志记录器"""
    return get_logger("data")