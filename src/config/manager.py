"""配置管理器"""
from src.config.slot_config import SlotConfig
from .file import FileConfig
from .s import DisplayConfig


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self.file = FileConfig()
        self.slot_config = SlotConfig()
        self.display_config = DisplayConfig()

config_manager = ConfigManager()