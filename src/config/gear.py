# src/config/gear.py
"""驱动盘配置"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any


class GearAttributeType(Enum):
    """驱动盘属性类型"""
    HP = "HP"
    ATK = "ATK"
    DEF = "DEF"
    Impact = "Impact"
    CRIT_Rate = "CRIT_Rate"
    CRIT_DMG = "CRIT_DMG"
    Anomaly_Mastery = "Anomaly_Mastery"
    Anomaly_Proficiency = "Anomaly_Proficiency"
    PEN_Ratio = "PEN_Ratio"
    PEN = "PEN"
    Energy_Regen = "Energy_Regen"
    Physical_DMG_Bonus = "Physical_DMG_Bonus"
    Fire_DMG_Bonus = "Fire_DMG_Bonus"
    Ice_DMG_Bonus = "Ice_DMG_Bonus"
    Electric_DMG_Bonus = "Electric_DMG_Bonus"
    Ether_DMG_Bonus = "Ether_DMG_Bonus"


class AttributeValueType(Enum):
    """属性值类型"""
    FIXED_VALUE = "fixed_value"
    PERCENTAGE = "percentage"
    RATE_PERCENTAGE = "rate_percentage"
    DMG_BONUS_PERCENTAGE = "dmg_bonus_percentage"


@dataclass
class AttributeConfig:
    """属性配置"""
    gear_attributes: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self):
        if not self.gear_attributes:
            self.gear_attributes = {
                "HP_FIXED": {"attribute_type": "HP", "value_type": "FIXED_VALUE", "display_name": "生命值"},
                "ATK_FIXED": {"attribute_type": "ATK", "value_type": "FIXED_VALUE", "display_name": "攻击力"},
                "DEF_FIXED": {"attribute_type": "DEF", "value_type": "FIXED_VALUE", "display_name": "防御力"},
                "Anomaly_Proficiency": {
                    "attribute_type": "Anomaly_Proficiency", "value_type": "FIXED_VALUE",
                    "display_name": "异常精通"
                },
                "PEN": {"attribute_type": "PEN", "value_type": "FIXED_VALUE","display_name": "穿透值"},

                "HP_PERCENT": {
                    "attribute_type": "HP", "value_type": "PERCENTAGE",
                    "display_name": "生命值%", "base_attribute": "HP"
                },
                "ATK_PERCENT": {
                    "attribute_type": "ATK", "value_type": "PERCENTAGE",
                    "display_name": "攻击力%", "base_attribute": "ATK"
                },
                "DEF_PERCENT": {
                    "attribute_type": "DEF", "value_type": "PERCENTAGE",
                    "display_name": "防御力%", "base_attribute": "DEF"
                },
                "Impact": {
                    "attribute_type": "Impact", "value_type": "PERCENTAGE",
                    "display_name": "冲击力", "base_attribute": "Impact"
                },
                "Anomaly_Mastery": {
                    "attribute_type": "Anomaly_Mastery", "value_type": "PERCENTAGE",
                    "display_name": "异常掌控", "base_attribute": "Anomaly_Mastery",
                },
                "Energy_Regen": {
                    "attribute_type": "Energy_Regen", "value_type": "PERCENTAGE",
                    "display_name": "能量回复", "base_attribute": "Energy_Regen"
                },

                "CRIT_Rate": {"attribute_type": "CRIT_Rate", "value_type": "RATE_PERCENTAGE", "display_name": "暴击率"},
                "CRIT_DMG": {"attribute_type": "CRIT_DMG", "value_type": "RATE_PERCENTAGE", "display_name": "暴击伤害"},
                "PEN_Ratio": {"attribute_type": "PEN_Ratio", "value_type": "RATE_PERCENTAGE", "display_name": "穿透率"},

                "Physical_DMG_Bonus": {
                    "attribute_type": "Physical_DMG_Bonus", "value_type": "dmg_bonus_percentage",
                    "display_name": "物理伤害加成"
                },
                "Fire_DMG_Bonus": {
                    "attribute_type": "Fire_DMG_Bonus", "value_type": "dmg_bonus_percentage",
                    "display_name": "火属性伤害加成"},
                "Ice_DMG_Bonus": {
                    "attribute_type": "Ice_DMG_Bonus", "value_type": "dmg_bonus_percentage",
                    "display_name":  "冰属性伤害加成"
                },
                "Electric_DMG_Bonus": {
                    "attribute_type": "Electric_DMG_Bonus", "value_type": "dmg_bonus_percentage",
                    "display_name": "电属性伤害加成"
                },
                "Ether_DMG_Bonus": {
                    "attribute_type": "Ether_DMG_Bonus", "value_type": "dmg_bonus_percentage",
                    "display_name": "以太伤害加成"
                },
            }

    def get_gear_attribute(self, gear_key: str) -> Dict:
        return self.gear_attributes.get(gear_key)

    def get_display_name(self, gear_key: str) -> str:
        attr = self.get_gear_attribute(gear_key)
        return attr["display_name"] if attr else gear_key

    def get_gear_key_by_display(self, display_name: str) -> str:
        for gear_key, attr in self.gear_attributes.items():
            if attr["display_name"] == display_name:
                return gear_key
        return display_name

    def is_percentage_type(self, gear_key: str) -> bool:
        """判断是否为百分比类型"""
        attr = self.get_gear_attribute(gear_key)
        if not attr:
            return False

        value_type = attr.get("value_type", "")
        return value_type in ["PERCENTAGE", "RATE_PERCENTAGE", "DMG_BONUS_PERCENTAGE"]

    def get_value_type(self, gear_key: str) -> str:
        """获取值类型"""
        attr = self.get_gear_attribute(gear_key)
        return attr.get("value_type", "FIXED_VALUE") if attr else "FIXED_VALUE"

    def validate(self) -> bool:
        return bool(self.gear_attributes)


@dataclass
class SlotConfig:
    """槽位配置 - 管理槽位属性限制"""

    def __init__(self):
        self.attribute_config = AttributeConfig()
        self.slot_attributes = {
            "slot_1": ["HP_FIXED"],
            "slot_2": ["ATK_FIXED"],
            "slot_3": ["DEF_FIXED"],
            "slot_4": ["HP_PERCENT", "ATK_PERCENT", "DEF_PERCENT", "CRIT_Rate", "CRIT_DMG", "Anomaly_Proficiency"],
            "slot_5": ["ATK_PERCENT", "HP_PERCENT", "DEF_PERCENT", "PEN_Ratio", "Physical_DMG_Bonus", "Fire_DMG_Bonus",
                       "Ice_DMG_Bonus", "Electric_DMG_Bonus", "Ether_DMG_Bonus"],
            "slot_6": ["ATK_PERCENT", "HP_PERCENT", "DEF_PERCENT", "Anomaly_Mastery", "Impact", "Energy_Regen"]
        }

    def get_main_attributes_for_slot(self, slot_index: int) -> List[str]:
        return self.slot_attributes.get(f"slot_{slot_index}", [])

    # def validate(self) -> bool:
    #     for slot_key, attributes in self.slot_attributes.items():
    #         for attr_key in attributes:
    #             if not self.attribute_config.get_gear_attribute(attr_key):
    #                 return False
    #     return True

    def to_dict(self) -> Dict[str, Any]:
        return {"slot_attributes": self.slot_attributes}


@dataclass
class GrowthConfig:
    """成长配置 - 管理属性成长数据"""

    def __init__(self):
        self.attribute_config = AttributeConfig()
        self.main_attr_growth = self._create_main_attr_growth()
        self.sub_attr_growth = self._create_sub_attr_growth()

    def _create_main_attr_growth(self) -> Dict[str, Dict[str, float]]:
        return {
            "HP_FIXED": {"base": 550, "growth": 110, "max": 2200},
            "ATK_FIXED": {"base": 79, "growth": 15.8, "max": 316},
            "DEF_FIXED": {"base": 46, "growth": 9.2, "max": 184},
            "Anomaly_Proficiency": {"base": 23, "growth": 4.6, "max": 92},
            "Impact": {"base": 0.045, "growth": 0.009, "max": 0.18},
            "HP_PERCENT": {"base": 0.075, "growth": 0.015, "max": 0.3},
            "ATK_PERCENT": {"base": 0.075, "growth": 0.015, "max": 0.3},
            "DEF_PERCENT": {"base": 0.12, "growth": 0.024, "max": 0.48},
            "CRIT_Rate": {"base": 0.06, "growth": 0.012, "max": 0.24},
            "CRIT_DMG": {"base": 0.12, "growth": 0.024, "max": 0.48},
            "PEN_Ratio": {"base": 0.06, "growth": 0.012, "max": 0.24},
            "Anomaly_Mastery": {"base": 0.075, "growth": 0.015, "max": 0.3},
            "Energy_Regen": {"base": 0.15, "growth": 0.03, "max": 0.6},
            "Physical_DMG_Bonus": {"base": 0.075, "growth": 0.015, "max": 0.3},
            "Fire_DMG_Bonus": {"base": 0.075, "growth": 0.015, "max": 0.3},
            "Ice_DMG_Bonus": {"base": 0.075, "growth": 0.015, "max": 0.3},
            "Electric_DMG_Bonus": {"base": 0.075, "growth": 0.015, "max": 0.3},
            "Ether_DMG_Bonus": {"base": 0.075, "growth": 0.015, "max": 0.3},
        }

    def _create_sub_attr_growth(self) -> Dict[str, Dict[str, float]]:
        return {
            "HP_FIXED": {"base": 112, "growth": 112, "max": 672},
            "ATK_FIXED": {"base": 19, "growth": 19, "max": 114},
            "DEF_FIXED": {"base": 15, "growth": 15, "max": 90},
            "HP_PERCENT": {"base": 0.03, "growth": 0.03, "max": 0.18},
            "ATK_PERCENT": {"base": 0.03, "growth": 0.03, "max": 0.18},
            "DEF_PERCENT": {"base": 0.048, "growth": 0.048, "max": 0.288},
            "CRIT_Rate": {"base": 0.024, "growth": 0.024, "max": 0.144},
            "CRIT_DMG": {"base": 0.048, "growth": 0.048, "max": 0.288},
            "Anomaly_Proficiency": {"base": 9, "growth": 9, "max": 54},
            "PEN": {"base": 9, "growth": 9, "max": 54}
        }

    def get_main_attribute_growth(self, gear_key: str) -> Dict[str, float]:
        return self.main_attr_growth.get(gear_key, {})

    def get_sub_attribute_growth(self, gear_key: str) -> Dict[str, float]:
        return self.sub_attr_growth.get(gear_key, {})

    def validate(self) -> bool:
        return bool(self.main_attr_growth and self.sub_attr_growth)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "main_attr_growth": self.main_attr_growth,
            "sub_attr_growth": self.sub_attr_growth
        }


@dataclass
class GearConfig:
    """驱动盘配置"""
    attribute_config: AttributeConfig = field(default_factory=AttributeConfig)
    slot_config: SlotConfig = field(default_factory=SlotConfig)
    growth_config: GrowthConfig = field(default_factory=GrowthConfig)

    def validate(self) -> bool:
        return (self.attribute_config.validate() and
                self.growth_config.validate())
