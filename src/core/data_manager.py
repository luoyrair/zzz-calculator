"""简化版数据管理器"""

from typing import List, Optional

from src.core.models import Character, Weapon, GearSet
from src.core.runtime_data_loader import RuntimeDataLoader
from src.utils.logger import get_logger


class SimpleDataManager:
    """简化数据管理器"""

    def __init__(self):
        self.logger = get_logger("core.data_manager")
        self._loaded = False

        self.loader = RuntimeDataLoader()

    def initialize(self):
        """初始化数据管理器"""
        success = self.loader.load_all()
        if not success:
            self.logger.error("数据初始化失败")
            raise RuntimeError("无法加载游戏数据，请确保data目录存在且包含必要的文件")

        self.logger.info("数据管理器初始化成功")

    def get_character(self, character_id: int) -> Optional[Character]:
        """获取角色"""
        return self.loader.get_character_data(character_id)

    def get_all_characters(self) -> List[Character]:
        """获取所有角色"""
        return list(self.loader.data.characters.values())

    def get_weapon(self, weapon_id: int) -> Optional[Weapon]:
        """获取音擎"""
        return self.loader.get_weapon_data(weapon_id)

    def get_all_weapons(self) -> List[Weapon]:
        """获取所有音擎"""
        return list(self.loader.data.weapons.values())

    def get_equipment(self):
        """获取所有驱动盘"""
        return [
            (set_id, set_data.name)
            for set_id, set_data in self.loader.data.gear_sets.items()
        ]

    def get_gear_set(self, set_id: str) -> Optional[GearSet]:
        """获取驱动盘套装"""
        return self.loader.get_gear_set_data(set_id)

    def get_all_gear_sets(self) -> List[GearSet]:
        """获取所有驱动盘套装"""
        return list(self.loader.data.gear_sets.values())

    def is_loaded(self) -> bool:
        """是否已加载数据"""
        return self._loaded