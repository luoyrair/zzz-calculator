# src/core/calculation/percentage.py
"""百分比加成处理器"""
from enum import Enum
from typing import Dict


class PercentageType(Enum):
    """百分比类型枚举"""
    RATE_PERCENTAGE = "rate"
    DAMAGE_BONUS = "damage_bonus"
    ATTRIBUTE_PERCENTAGE = "attribute"
    DIRECT_VALUE = "direct"


class PercentageHandler:
    """百分比加成处理器"""

    _percentage_type_mapping: Dict[str, PercentageType] = {
        'CRIT_Rate': PercentageType.RATE_PERCENTAGE,
        'CRIT_DMG': PercentageType.RATE_PERCENTAGE,
        'PEN_Ratio': PercentageType.RATE_PERCENTAGE,
        'HP': PercentageType.ATTRIBUTE_PERCENTAGE,
        'ATK': PercentageType.ATTRIBUTE_PERCENTAGE,
        'DEF': PercentageType.ATTRIBUTE_PERCENTAGE,
        'Impact': PercentageType.ATTRIBUTE_PERCENTAGE,
        'Anomaly_Mastery': PercentageType.ATTRIBUTE_PERCENTAGE,
        'Energy_Regen': PercentageType.ATTRIBUTE_PERCENTAGE,
        'Anomaly_Proficiency': PercentageType.DIRECT_VALUE,
        'PEN': PercentageType.DIRECT_VALUE,
        'Sheer_Force': PercentageType.DIRECT_VALUE,
    }

    @classmethod
    def calculate_percentage(cls, attr_name: str, base_value: float,
                             percentage: float, base_attribute: float = 0) -> float:
        """根据属性类型计算百分比加成"""
        percentage_type = cls._percentage_type_mapping.get(attr_name, PercentageType.DIRECT_VALUE)

        if percentage_type == PercentageType.RATE_PERCENTAGE:
            return base_value + percentage
        elif percentage_type == PercentageType.ATTRIBUTE_PERCENTAGE:
            return base_value + (base_attribute * percentage)
        elif percentage_type == PercentageType.DIRECT_VALUE:
            return base_value + percentage
        else:
            return base_value + percentage