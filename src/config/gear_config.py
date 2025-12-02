# src/config/gear_config.py
"""驱动盘配置定义 - 专注数据结构和验证"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from .base_config import BaseConfig
from enum import Enum


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
class GearAttribute:
    """驱动盘属性定义"""
    gear_key: str
    attribute_type: GearAttributeType
    value_type: AttributeValueType
    display_name: str
    base_attribute: Optional[GearAttributeType] = None

    def get_final_attribute_key(self) -> str:
        print(f"[DEBUG] GearAttribute.get_final_attribute_key: {self.gear_key} -> {self.attribute_type.value}")
        return self.attribute_type.value


class GearConfig(BaseConfig):
    """驱动盘配置管理器"""

    def __init__(self):
        self.attribute_config = AttributeConfig()
        self.slot_config = SlotConfig(self.attribute_config)
        self.growth_config = GrowthConfig(self.attribute_config)

    def validate(self) -> bool:
        return (self.attribute_config.validate() and
                self.slot_config.validate() and
                self.growth_config.validate())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attribute_config": self.attribute_config.to_dict(),
            "slot_config": self.slot_config.to_dict(),
            "growth_config": self.growth_config.to_dict()
        }


class AttributeConfig:
    """属性配置 - 管理所有属性定义"""

    def __init__(self):
        self.gear_attributes = self._create_gear_attributes()

    def _create_gear_attributes(self) -> Dict[str, GearAttribute]:
        return {
            # 固定值属性
            "HP_FIXED": GearAttribute("HP_FIXED", GearAttributeType.HP, AttributeValueType.FIXED_VALUE, "生命值"),
            "ATK_FIXED": GearAttribute("ATK_FIXED", GearAttributeType.ATK, AttributeValueType.FIXED_VALUE, "攻击力"),
            "DEF_FIXED": GearAttribute("DEF_FIXED", GearAttributeType.DEF, AttributeValueType.FIXED_VALUE, "防御力"),
            "Anomaly_Proficiency": GearAttribute("Anomaly_Proficiency", GearAttributeType.Anomaly_Proficiency,
                                                 AttributeValueType.FIXED_VALUE, "异常精通"),
            "PEN": GearAttribute("PEN", GearAttributeType.PEN, AttributeValueType.FIXED_VALUE, "穿透值"),

            # 百分比属性
            "HP_PERCENT": GearAttribute("HP_PERCENT", GearAttributeType.HP, AttributeValueType.PERCENTAGE, "生命值%",
                                        GearAttributeType.HP),
            "ATK_PERCENT": GearAttribute("ATK_PERCENT", GearAttributeType.ATK, AttributeValueType.PERCENTAGE, "攻击力%",
                                         GearAttributeType.ATK),
            "DEF_PERCENT": GearAttribute("DEF_PERCENT", GearAttributeType.DEF, AttributeValueType.PERCENTAGE, "防御力%",
                                         GearAttributeType.DEF),
            "Impact": GearAttribute("Impact", GearAttributeType.Impact, AttributeValueType.PERCENTAGE, "冲击力",
                                    GearAttributeType.Impact),
            "Anomaly_Mastery": GearAttribute("Anomaly_Mastery", GearAttributeType.Anomaly_Mastery,
                                             AttributeValueType.PERCENTAGE, "异常掌控", GearAttributeType.Anomaly_Mastery),
            "Energy_Regen": GearAttribute("Energy_Regen", GearAttributeType.Energy_Regen,
                                          AttributeValueType.PERCENTAGE, "能量回复", GearAttributeType.Energy_Regen),

            # 比率属性
            "CRIT_Rate": GearAttribute("CRIT_Rate", GearAttributeType.CRIT_Rate, AttributeValueType.RATE_PERCENTAGE,
                                       "暴击率"),
            "CRIT_DMG": GearAttribute("CRIT_DMG", GearAttributeType.CRIT_DMG, AttributeValueType.RATE_PERCENTAGE,
                                      "暴击伤害"),
            "PEN_Ratio": GearAttribute("PEN_Ratio", GearAttributeType.PEN_Ratio, AttributeValueType.RATE_PERCENTAGE,
                                       "穿透率"),

            # 伤害加成
            "Physical_DMG_Bonus": GearAttribute("Physical_DMG_Bonus", GearAttributeType.Physical_DMG_Bonus,
                                                AttributeValueType.DMG_BONUS_PERCENTAGE, "物理伤害加成"),
            "Fire_DMG_Bonus": GearAttribute("Fire_DMG_Bonus", GearAttributeType.Fire_DMG_Bonus,
                                            AttributeValueType.DMG_BONUS_PERCENTAGE, "火属性伤害加成"),
            "Ice_DMG_Bonus": GearAttribute("Ice_DMG_Bonus", GearAttributeType.Ice_DMG_Bonus,
                                           AttributeValueType.DMG_BONUS_PERCENTAGE, "冰属性伤害加成"),
            "Electric_DMG_Bonus": GearAttribute("Electric_DMG_Bonus", GearAttributeType.Electric_DMG_Bonus,
                                                AttributeValueType.DMG_BONUS_PERCENTAGE, "电属性伤害加成"),
            "Ether_DMG_Bonus": GearAttribute("Ether_DMG_Bonus", GearAttributeType.Ether_DMG_Bonus,
                                             AttributeValueType.DMG_BONUS_PERCENTAGE, "以太伤害加成"),
        }

    def get_gear_attribute(self, gear_key: str) -> Optional[GearAttribute]:
        return self.gear_attributes.get(gear_key)

    def get_display_name(self, gear_key: str) -> str:
        attr = self.get_gear_attribute(gear_key)
        return attr.display_name if attr else gear_key

    def get_gear_key_by_display(self, display_name: str) -> str:
        for gear_key, attr in self.gear_attributes.items():
            if attr.display_name == display_name:
                return gear_key
        return display_name

    def validate(self) -> bool:
        return bool(self.gear_attributes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gear_attributes": {k: {
                "attribute_type": v.attribute_type.value,
                "value_type": v.value_type.value,
                "display_name": v.display_name,
                "base_attribute": v.base_attribute.value if v.base_attribute else None
            } for k, v in self.gear_attributes.items()}
        }


class SlotConfig:
    """槽位配置 - 管理槽位属性限制"""

    def __init__(self, attribute_config: AttributeConfig):
        self.attribute_config = attribute_config
        self.slot_attributes = self._build_slot_attributes()

    def _build_slot_attributes(self) -> Dict[str, List[str]]:
        return {
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

    def validate(self) -> bool:
        for slot_key, attributes in self.slot_attributes.items():
            for attr_key in attributes:
                if not self.attribute_config.get_gear_attribute(attr_key):
                    return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {"slot_attributes": self.slot_attributes}


class GrowthConfig:
    """成长配置 - 管理属性成长数据"""

    def __init__(self, attribute_config: AttributeConfig):
        self.attribute_config = attribute_config
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