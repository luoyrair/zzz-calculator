"""
数据提供者接口定义
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.core.models import Character, Weapon, GearSet


class DataProvider(ABC):
    """数据提供者接口 - 所有数据源的统一接口"""

    @abstractmethod
    def get_character(self, character_id: int) -> Optional[Character]:
        """获取角色"""
        pass

    @abstractmethod
    def get_all_characters(self) -> List[Character]:
        """获取所有角色"""
        pass

    @abstractmethod
    def get_weapon(self, weapon_id: int) -> Optional[Weapon]:
        """获取武器"""
        pass

    @abstractmethod
    def get_all_weapons(self) -> List[Weapon]:
        """获取所有武器"""
        pass

    @abstractmethod
    def get_gear_set(self, set_id: str) -> Optional[GearSet]:
        """获取驱动盘套装"""
        pass

    @abstractmethod
    def get_all_gear_sets(self) -> List[GearSet]:
        """获取所有驱动盘套装"""
        pass

    @abstractmethod
    def get_equipment_list(self) -> List[tuple]:
        """获取装备列表 [(id, name), ...]"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        pass


class DataProviderAware(ABC):
    """需要数据提供者的类的基础接口"""

    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider