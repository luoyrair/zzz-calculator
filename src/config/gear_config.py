# src/config/gear_config.py
"""重构后的驱动盘配置"""
from typing import Dict, Any, List
from .base_config import BaseConfig


class GearConfig(BaseConfig):
    """驱动盘配置"""

    def __init__(self):
        self.slot_config = SlotConfig()
        self.attribute_config = AttributeConfig()
        self.growth_config = GrowthConfig()

    def validate(self) -> bool:
        return (self.slot_config.validate() and
                self.attribute_config.validate() and
                self.growth_config.validate())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot_config": self.slot_config.to_dict(),
            "attribute_config": self.attribute_config.to_dict(),
            "growth_config": self.growth_config.to_dict()
        }


class SlotConfig:
    """槽位配置"""

    def __init__(self):
        self.SLOT_MAIN_ATTRIBUTES = {
            "slot_1": ["HP"],
            "slot_2": ["ATK"],
            "slot_3": ["DEF"],
            "slot_4": ["ATK_PERCENT", "HP_PERCENT", "DEF_PERCENT", "CRIT_RATE", "CRIT_DMG", "ANOMALY_MASTERY"],
            "slot_5": ["ATK_PERCENT", "HP_PERCENT", "DEF_PERCENT", "PENETRATION", "PHYSICAL_DMG", "FIRE_DMG",
                       "ICE_DMG", "ELECTRIC_DMG", "ETHER_DMG"],
            "slot_6": ["ATK_PERCENT", "HP_PERCENT", "DEF_PERCENT", "ANOMALY_PROFICIENCY", "IMPACT", "ENERGY_REGEN"]
        }

    def get_main_attributes_for_slot(self, slot_index: int) -> List[str]:
        slot_key = f"slot_{slot_index}"
        return self.SLOT_MAIN_ATTRIBUTES.get(slot_key, [])

    def validate(self) -> bool:
        return bool(self.SLOT_MAIN_ATTRIBUTES and
                    all(self.SLOT_MAIN_ATTRIBUTES.values()))

    def to_dict(self) -> Dict[str, Any]:
        return {"slot_main_attributes": self.SLOT_MAIN_ATTRIBUTES}


class AttributeConfig:
    """属性配置"""

    def __init__(self):
        self.ATTRIBUTE_DISPLAY_NAMES = {
            "HP": "生命值",
            "ATK": "攻击力",
            "DEF": "防御力",
            "HP_PERCENT": "生命值%",
            "ATK_PERCENT": "攻击力%",
            "DEF_PERCENT": "防御力%",
            "CRIT_RATE": "暴击率",
            "CRIT_DMG": "暴击伤害",
            "ANOMALY_MASTERY": "异常精通",
            "PHYSICAL_DMG": "物理伤害加成",
            "FIRE_DMG": "火属性伤害加成",
            "ICE_DMG": "冰属性伤害加成",
            "ELECTRIC_DMG": "电属性伤害加成",
            "ETHER_DMG": "以太伤害加成",
            "PENETRATION": "穿透率",
            "IMPACT": "冲击力",
            "ANOMALY_PROFICIENCY": "异常掌控",
            "ENERGY_REGEN": "能量回复",
            "PENETRATION_VALUE": "穿透值"
        }

        self.ATTRIBUTE_MAPPING = {
            "CRIT_RATE": "CRIT_RATE",
            "CRIT_DMG": "CRIT_DMG",
            "PENETRATION": "PENETRATION",
            "PHYSICAL_DMG": "ELEMENT_DMG",
            "FIRE_DMG": "ELEMENT_DMG",
            "ICE_DMG": "ELEMENT_DMG",
            "ELECTRIC_DMG": "ELEMENT_DMG",
            "ETHER_DMG": "ELEMENT_DMG",
            "ANOMALY_PROFICIENCY": "ANOMALY_PROFICIENCY",
            "IMPACT": "IMPACT",
            "ENERGY_REGEN": "ENERGY_REGEN"
        }

    def get_display_name(self, attr_key: str) -> str:
        return self.ATTRIBUTE_DISPLAY_NAMES.get(attr_key, attr_key)

    def get_english_key_from_display(self, display_name: str) -> str:
        for eng_key, chn_name in self.ATTRIBUTE_DISPLAY_NAMES.items():
            if chn_name == display_name:
                return eng_key
        return display_name

    def validate(self) -> bool:
        return bool(self.ATTRIBUTE_DISPLAY_NAMES)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "display_names": self.ATTRIBUTE_DISPLAY_NAMES,
            "attribute_mapping": self.ATTRIBUTE_MAPPING
        }


class GrowthConfig:
    """成长配置"""

    def __init__(self):
        self.MAIN_ATTR_GROWTH = {
            "HP": {"base": 550, "growth": 110, "max": 2200},  # 生命值
            "ATK": {"base": 79, "growth": 15.8, "max": 316},  # 攻击力
            "DEF": {"base": 46, "growth": 9.2, "max": 184},  # 防御力
            "HP_PERCENT": {"base": 0.075, "growth": 0.015, "max": 0.3},  # 生命值百分比
            "ATK_PERCENT": {"base": 0.075, "growth": 0.015, "max": 0.3},  # 攻击力百分比
            "DEF_PERCENT": {"base": 0.12, "growth": 0.024, "max": 0.48},  # 防御力百分比
            "CRIT_RATE": {"base": 0.06, "growth": 0.012, "max": 0.24},  # 暴击率
            "CRIT_DMG": {"base": 0.12, "growth": 0.024, "max": 0.48},  # 暴击伤害
            "ANOMALY_MASTERY": {"base": 23, "growth": 4.6, "max": 92},  # 异常精通
            "ELEMENT_DMG": {"base": 0.075, "growth": 0.015, "max": 0.3},  # 属性伤害百分比
            "PENETRATION": {"base": 0.06, "growth": 0.012, "max": 0.24},  # 穿透率
            "IMPACT": {"base": 0.045, "growth": 0.009, "max": 0.18},  # 冲击力
            "ANOMALY_PROFICIENCY": {"base": 0.075, "growth": 0.015, "max": 0.3},  # 异常掌控
            "ENERGY_REGEN": {"base": 0.15, "growth": 0.03, "max": 0.6}  # 能量自动回复
        }

        self.SUB_ATTR_GROWTH = {
            "PENETRATION_VALUE": {"base": 9, "growth": 9, "max": 54},
            "ANOMALY_MASTERY": {"base": 9, "growth": 9, "max": 54},
            "DEF": {"base": 15, "growth": 15, "max": 90},
            "ATK": {"base": 19, "growth": 19, "max": 114},
            "HP": {"base": 112, "growth": 112, "max": 672},
            "CRIT_RATE": {"base": 0.024, "growth": 0.024, "max": 0.144},
            "HP_PERCENT": {"base": 0.03, "growth": 0.03, "max": 0.18},
            "ATK_PERCENT": {"base": 0.03, "growth": 0.03, "max": 0.18},
            "CRIT_DMG": {"base": 0.048, "growth": 0.048, "max": 0.288},
            "DEF_PERCENT": {"base": 0.048, "growth": 0.048, "max": 0.288}
        }

    def get_main_attribute_growth(self, attr_name: str) -> Dict[str, float]:
        return self.MAIN_ATTR_GROWTH.get(attr_name, {})

    def get_sub_attribute_growth(self, attr_name: str) -> Dict[str, float]:
        return self.SUB_ATTR_GROWTH.get(attr_name, {})

    def validate(self) -> bool:
        return bool(self.MAIN_ATTR_GROWTH and self.SUB_ATTR_GROWTH)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "main_attr_growth": self.MAIN_ATTR_GROWTH,
            "sub_attr_growth": self.SUB_ATTR_GROWTH
        }