"""
武器工厂 - 负责创建武器实例并注入成长数据享元
"""

from typing import Dict, List, Optional
from pathlib import Path

from src.core.models import Weapon, Attribute
from src.core.weapon_growth import weapon_growth
from src.utils.logger import get_logger

logger = get_logger("core.weapon_factory")


class WeaponFactory:
    """
    武器工厂
    职责：
    1. 管理武器成长数据（通过享元）
    2. 创建武器实例
    3. 缓存已创建的武器（可选）
    """

    def __init__(self):
        self._cache: Dict[int, Weapon] = {}  # id -> Weapon
        self.growth = weapon_growth  # 引用全局享元
        logger.debug("WeaponFactory 初始化")

    def initialize(self, levels_path: Path, stars_path: Path) -> bool:
        """
        初始化成长数据
        返回是否成功
        """
        return self.growth.load_from_files(levels_path, stars_path)

    @staticmethod
    def create_weapon(data: Dict) -> Weapon:
        """
        从原始数据创建武器实例
        data 格式来自 weapons.pkl
        """
        # 创建武器实例（不包含成长数据）
        weapon = Weapon(
            id=int(data['weapon_id']),
            name=data['name'],
            rarity=data['rarity'],
            weapon_type=data['weapon_type'],
            base_attack=data['attrs'][0],
            advanced_attribute=data['attrs'][1],
            talent_attributes=data['talents']['attrs']
        )

        weapon.ensure_attributes_calculated()

        # 武器实例会自动使用全局享元
        # 不需要额外设置

        logger.debug(f"创建武器: {weapon.name} (ID: {weapon.id})")
        return weapon

    @staticmethod
    def create_weapon_with_values(_id: int,
                                  name: str,
                                  rarity: int,
                                  weapon_type: str,
                                  base_attack: Attribute,
                                  advanced_attribute: Attribute,
                                  talent_attributes: List[Attribute] = None,
                                  level: int = 60,
                                  refinement: int = 5,
                                  talent: int = 1) -> Weapon:
        """
        使用具体值创建武器（主要用于测试）
        """
        weapon = Weapon(
            id=_id,
            name=name,
            rarity=rarity,
            weapon_type=weapon_type,
            base_attack=base_attack,
            advanced_attribute=advanced_attribute,
            talent_attributes=talent_attributes or [],
            level=level,
            refinement=refinement,
            talent=talent
        )

        logger.debug(f"创建测试武器: {name}")
        return weapon

    def get_weapon(self, weapon_id: int) -> Optional[Weapon]:
        """从缓存获取武器"""
        return self._cache.get(weapon_id)

    def cache_weapon(self, weapon: Weapon):
        """缓存武器实例"""
        self._cache[weapon.id] = weapon
        logger.debug(f"武器已缓存: {weapon.name} (ID: {weapon.id})")

    def cache_weapons(self, weapons: List[Weapon]):
        """批量缓存武器"""
        for weapon in weapons:
            self._cache[weapon.id] = weapon
        logger.debug(f"已缓存 {len(weapons)} 个武器")

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.debug("武器缓存已清空")

    def get_all_cached(self) -> List[Weapon]:
        """获取所有缓存的武器"""
        return list(self._cache.values())

    @property
    def is_growth_loaded(self) -> bool:
        """检查成长数据是否已加载"""
        return self.growth.is_loaded()


# 创建全局工厂实例（可选）
weapon_factory = WeaponFactory()