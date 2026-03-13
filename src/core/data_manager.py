"""简化版数据管理器"""

from typing import List, Optional

from src.core.interfaces import DataProvider
from src.core.models import Character, Weapon, GearSet
from src.core.runtime_data_loader import RuntimeDataLoader
from src.utils.logger import get_logger


class SimpleDataManager(DataProvider):
    """真实数据管理器 - 从文件加载数据"""

    def __init__(self):
        self.logger = get_logger("core.data_manager")
        self.loader = RuntimeDataLoader()
        self._loaded = False

    def initialize(self) -> bool:
        """初始化并加载数据"""
        success = self.loader.load_all()
        self._loaded = success
        return success

    def get_character(self, character_id: int) -> Optional[Character]:
        if not self._loaded:
            self.initialize()
        return self.loader.get_character_data(character_id)

    def get_all_characters(self) -> List[Character]:
        if not self._loaded:
            self.initialize()
        return list(self.loader.data.characters.values())

    def get_weapon(self, weapon_id: int) -> Optional[Weapon]:
        if not self._loaded:
            self.initialize()
        return self.loader.get_weapon_data(weapon_id)

    def get_all_weapons(self) -> List[Weapon]:
        if not self._loaded:
            self.initialize()
        return self.loader.weapon_factory.get_all_cached()

    def get_gear_set(self, set_id: str) -> Optional[GearSet]:
        if not self._loaded:
            self.initialize()
        return self.loader.get_gear_set_data(set_id)

    def get_all_gear_sets(self) -> List[GearSet]:
        if not self._loaded:
            self.initialize()
        return list(self.loader.data.gear_sets.values())

    def get_equipment_list(self) -> List[tuple]:
        if not self._loaded:
            self.initialize()
        return [
            (set_id, set_data.name)
            for set_id, set_data in self.loader.data.gear_sets.items()
        ]

    def is_available(self) -> bool:
        return self._loaded