# src/config/__init__.py
"""配置管理器 - 新架构"""
from .character_config import CharacterConfig
from .gear_config import GearConfig
from .file_config import FileConfig


class ConfigManager:
    """配置管理器"""

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

    def validate_all(self) -> bool:
        """验证所有配置"""
        return self.character.validate() and self.gear.validate()


# 全局配置管理器实例
config_manager = ConfigManager()