# src/core/models/weapon.py
"""音擎业务模型"""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class WeaponProperty:
    """音擎属性"""
    name: str
    display_name: str
    format: str
    base_value: float
    is_percentage: bool = False

    def format_value(self, value: float) -> str:
        """格式化显示值"""
        if self.is_percentage:
            return f"{value * 100:.1f}%"
        else:
            return f"{value:.0f}"


@dataclass
class WeaponLevelData:
    """音擎等级数据"""
    rate: int
    rate2: int


@dataclass
class WeaponStarData:
    """音擎星阶数据"""
    star_rate: int
    rand_rate: int


@dataclass
class WeaponTalent:
    """音擎天赋"""
    name: str
    description: str


@dataclass
class WeaponSchema:
    """音擎数据架构"""
    weapon_id: int
    name: str
    rarity: int
    weapon_type: str

    base_property: WeaponProperty
    rand_property: WeaponProperty

    level_data: Dict[int, WeaponLevelData]
    star_data: Dict[int, WeaponStarData]
    talents: Dict[int, WeaponTalent]


@dataclass
class CalculatedWeaponStats:
    """计算后的音擎属性"""
    level: int
    stars: int
    base_property_value: float
    rand_property_value: float
    calculated_properties: Dict[str, float] = field(default_factory=dict)