"""配置常量"""

from enum import Enum
from pathlib import Path
import sys


class AppConstants:
    """应用常量"""

    # 应用信息
    APP_NAME = "ZZZ属性计算器"
    VERSION = "1.0.0"
    AUTHOR = "开发团队"

    # 系统相关
    IS_FROZEN = getattr(sys, 'frozen', False)
    IS_BUNDLED = hasattr(sys, '_MEIPASS')

    # 路径相关
    @staticmethod
    def get_base_dir():
        """获取基础目录"""
        if AppConstants.IS_FROZEN:
            # 打包后的exe模式
            return Path(sys.executable).parent
        else:
            # 开发模式
            return Path(__file__).parent.parent.parent

    # 计算相关
    MAX_CHARACTER_LEVEL = 60
    MAX_WEAPON_LEVEL = 60
    MAX_GEAR_ENHANCE_LEVEL = 15
    MAX_EXTRA_LEVEL = 7


class PathConstants:
    """路径常量"""

    @staticmethod
    def get_data_dir():
        """获取数据目录"""
        base_dir = AppConstants.get_base_dir()
        return base_dir / 'data'

    @staticmethod
    def get_logs_dir():
        """获取日志目录"""
        base_dir = AppConstants.get_base_dir()
        return base_dir / 'logs'

    def get_config_dir(self):
        """获取配置目录"""
        return self.get_data_dir() / 'config'

    def get_settings_dir(self):
        """获取配置目录"""
        return self.get_data_dir() / 'app'

    # 子目录
    CHARACTERS_DIR = "characters"
    WEAPONS_DIR = "weapons"
    EQUIPMENT_DIR = "equipment"
    PRESETS_DIR = "presets"

    GROWTH_DIR = "growth"

    # 文件路径
    CHARACTER_IDS_FILE = "character_ids.json"
    WEAPON_IDS_FILE = "weapon_ids.json"
    EQUIPMENT_IDS_FILE = "equipment_ids.json"
    CHARACTER_MAPPING_FILE = "character_id_name_mapping.json"
    WEAPON_MAPPING_FILE = "weapon_id_name_mapping.json"
    EQUIPMENT_FILE = "equipment.json"
    FAILED_DOWNLOADS_FILE = "failed_downloads.json"

    @staticmethod
    def get_full_path(relative_path: str) -> Path:
        """获取完整路径"""
        data_dir = PathConstants.get_data_dir()
        return data_dir / relative_path


class Environment(Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

    @classmethod
    def detect(cls):
        """检测当前环境"""
        import os
        env_var = os.environ.get("ZZZ_ENV", "").lower()

        if env_var == "production":
            return cls.PRODUCTION
        elif env_var == "testing":
            return cls.TESTING
        else:
            return cls.DEVELOPMENT

    @property
    def is_development(self):
        return self == Environment.DEVELOPMENT

    @property
    def is_production(self):
        return self == Environment.PRODUCTION

    @property
    def is_testing(self):
        return self == Environment.TESTING


class ColorConstants:
    """颜色常量"""

    # 状态颜色
    STATUS_SUCCESS = "green"
    STATUS_WARNING = "orange"
    STATUS_ERROR = "red"
    STATUS_INFO = "blue"
    STATUS_DEFAULT = "black"

    # 稀有度颜色
    RARITY_COLORS = {
        1: "#808080",  # 灰色
        2: "#008000",  # 绿色
        3: "#0000FF",  # 蓝色
        4: "#B28BEA",  # 紫色
        5: "#FFD700"  # 金色
    }

    # 元素颜色
    ELEMENT_COLORS = {
        "物理": "#808080",
        "火": "#FF4500",
        "冰": "#00BFFF",
        "电": "#FFD700",
        "以太": "#9370DB"
    }

    # UI 颜色
    UI_BACKGROUND = "#F5F5F5"
    UI_BORDER = "#CCCCCC"
    UI_HIGHLIGHT = "#E3F2FD"
    UI_DISABLED = "#E0E0E0"
    BASIC_COLOR = '#000000'
    RECOMMENDED_COLOR = '#FF4500'
    BASIC_ATTRIBUTE_COLOR = "#FF4500"  # 火红色
    CHARACTER_ATTRIBUTE_COLOR = "#00BFFF"  # 浅蓝色

class DataType:
    CHARACTER = "character"
    WEAPON = "weapon"
    GEAR_SET = "gear_set"