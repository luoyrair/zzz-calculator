# src/config/__init__.py
"""统一配置管理器"""
from .base_config import BaseConfig
from .character_config import CharacterConfig
from .gear_config import GearConfig
from .file_config import FileConfig


class ConfigManager:
    """统一配置管理器"""

    def __init__(self):
        self.character = CharacterConfig()
        self.gear = GearConfig()
        self.file = FileConfig()
        self._initialized = False

    def initialize(self) -> bool:
        """初始化所有配置"""
        if self._initialized:
            return True

        try:
            # 验证所有配置
            configs = [
                ("角色配置", self.character),
                ("驱动盘配置", self.gear),
                ("文件配置", self.file)
            ]

            all_valid = True
            for name, config in configs:
                if not config.validate():
                    print(f"❌ {name}验证失败")
                    all_valid = False
                else:
                    print(f"✅ {name}验证通过")

            self._initialized = all_valid
            return all_valid

        except Exception as e:
            print(f"❌ 配置初始化失败: {e}")
            return False

    def reload(self) -> bool:
        """重新加载配置"""
        self._initialized = False
        return self.initialize()

    def get_config_summary(self) -> dict:
        """获取配置摘要"""
        return {
            "character": self.character.to_dict(),
            "gear": self.gear.to_dict(),
            "file": self.file.to_dict(),
            "initialized": self._initialized
        }


# 全局配置管理器实例
config_manager = ConfigManager()