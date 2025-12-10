from enum import Enum
from typing import Union


class AttributeType(Enum):
    """属性类型枚举"""
    HP = "hp"
    ATK = "attack"
    DEF = "defence"
    IMPACT = "impact"
    CRIT_RATE = "crit_rate"
    CRIT_DMG = "crit_dmg"
    ANOMALY_MASTERY = "anomaly_mastery"
    ANOMALY_PROFICIENCY = "anomaly_proficiency"
    PEN_RATIO = "pen_ratio"
    PEN = "pen"
    ENERGY_REGEN = "energy_regen"
    SHEER_FORCE = "sheer_force"
    ADRENALINE_ACCUMULATION = "automatic_adrenaline_accumulation"


class AttributeValueType(Enum):
    """属性值类型枚举"""
    NUMERIC_VALUE = "numeric_value"
    PERCENTAGE = "percentage"


class GearAttributeValueType(Enum):
    """驱动盘属性值类型枚举"""
    NUMERIC_VALUE = "numeric_value"
    PERCENTAGE = "percentage"
    RATE_PERCENTAGE = "rate_percentage"
    DMG_BONUS_PERCENTAGE = "dmg_bonus_percentage"


class BaseAttribute:
    """基础属性类"""
    base: float
    attribute_value_type: Union[AttributeValueType, str]


class GrowingAttribute(BaseAttribute):
    """带成长值的属性类"""
    growth: int

    def calculate_value_at_level(self, level: int) -> float:
        """计算指定等级时的属性值"""
        return self.base + (level - 1) * self.growth / 10000.0


class CharacterAttribute:
    """角色属性封装类"""

    def __init__(self):
        self.base_attribute = BaseAttribute()
        self.growing_attribute = GrowingAttribute()
        self.attribute_type = None