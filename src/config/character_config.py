# src/config/character_config.py
"""重构后的角色配置"""
from typing import Dict, Any

from .base_config import BaseConfig


class CharacterConfig(BaseConfig):
    """角色配置 - 新架构"""

    def __init__(self):
        self.stat_config = StatConfig()
        self.level_config = LevelConfig()
        self.display_config = DisplayConfig()
        self.attribute_output_config = AttributeOutputConfig()

    def validate(self) -> bool:
        return (self.stat_config.validate() and
                self.level_config.validate() and
                self.display_config.validate())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stat_config": self.stat_config.to_dict(),
            "level_config": self.level_config.to_dict(),
            "display_config": self.display_config.to_dict()
        }


class StatConfig:
    """属性配置 - 简化版本，主要功能已移至character_models"""

    def __init__(self):
        # 基础属性ID映射
        self.STAT_ID_MAPPING = {
            111: "HP", 121: "ATK", 131: "DEF",
            122: "Impact", 201: "CRIT_Rate", 211: "CRIT_DMG",
            314: "Anomaly_Mastery", 312: "Anomaly_Proficiency",
            231: "PEN_Ratio", 305: "Energy_Regen"
        }

    def validate(self) -> bool:
        return bool(self.STAT_ID_MAPPING)

    def to_dict(self) -> Dict[str, Any]:
        return {"stat_mapping": self.STAT_ID_MAPPING}


class LevelConfig:
    """等级配置"""

    def __init__(self):
        self.MAX_LEVEL = 60
        self.MIN_LEVEL = 1
        self.MAX_EXTRA_LEVEL = 7

    def validate(self) -> bool:
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_level": self.MAX_LEVEL,
            "max_extra_level": self.MAX_EXTRA_LEVEL
        }


class DisplayConfig:
    """显示配置"""

    def __init__(self):
        self.WEAPON_TYPE_MAPPING = {
            "Sword": "剑", "Blade": "刀", "Axe": "斧",
            "Hammer": "锤", "Spear": "枪", "Bow": "弓",
            "Gun": "枪械", "Fist": "拳套", "Wand": "法杖"
        }
        """错误的WeaponType实现"""

        self.ELEMENT_TYPE_MAPPING = {
            "Physical": "物理", "Fire": "火", "Ice": "冰",
            "Electric": "电", "Ether": "以太"
        }

        self.RARITY_COLOR_MAPPING = {
            3: "#5DBCD2", 4: "#B28BEA", 5: "#FFD700"
        }

    def get_weapon_display(self, weapon_data: Dict[str, Any]) -> str:
        if not weapon_data:
            return "未知"
        weapon_key = list(weapon_data.values())[0] if isinstance(weapon_data, dict) else weapon_data
        return self.WEAPON_TYPE_MAPPING.get(weapon_key, weapon_key)

    def get_element_display(self, element_data: Dict[str, Any]) -> str:
        if not element_data:
            return "未知"
        element_key = list(element_data.values())[0] if isinstance(element_data, dict) else element_data
        return self.ELEMENT_TYPE_MAPPING.get(element_key, element_key)

    def get_rarity_color(self, rarity: int) -> str:
        return self.RARITY_COLOR_MAPPING.get(rarity, "#000000")

    def validate(self) -> bool:
        return bool(self.WEAPON_TYPE_MAPPING and self.ELEMENT_TYPE_MAPPING)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "weapon_types": self.WEAPON_TYPE_MAPPING,
            "element_types": self.ELEMENT_TYPE_MAPPING,
            "rarity_colors": self.RARITY_COLOR_MAPPING
        }


class AttributeOutputConfig:
    """属性输出配置 - 根据武器类型智能配置显示顺序"""

    def __init__(self):
        # 命破武器类型的特殊输出顺序 - 使用BaseCharacterStats属性名
        self.MINGPO_WEAPON_OUTPUT_ORDER = [
            "HP", "ATK", "DEF", "Impact",
            "CRIT_Rate", "CRIT_DMG", "Anomaly_Mastery",
            "Anomaly_Proficiency", "Sheer_Force", "Automatic_Adrenaline_Accumulation"
        ]

        # 其他武器类型的默认输出顺序 - 使用BaseCharacterStats属性名
        self.DEFAULT_OUTPUT_ORDER = [
            "HP", "ATK", "DEF", "Impact",
            "CRIT_Rate", "CRIT_DMG", "Anomaly_Mastery",
            "Anomaly_Proficiency", "PEN_Ratio", "Energy_Regen"
        ]

        # 属性显示名称映射 - 使用BaseCharacterStats属性名
        self.ATTRIBUTE_DISPLAY_NAMES = {
            "HP": "生命值",
            "ATK": "攻击力",
            "DEF": "防御力",
            "Impact": "冲击力",
            "CRIT_Rate": "暴击率",
            "CRIT_DMG": "暴击伤害",
            "Anomaly_Mastery": "异常掌控",
            "Anomaly_Proficiency": "异常精通",
            "Sheer_Force": "贯穿力",
            "PEN_Ratio": "穿透率",
            "Energy_Regen": "能量自动回复",
            "Automatic_Adrenaline_Accumulation": "闪能自动累积"
        }

        # 命破武器类型标识
        self.MINGPO_WEAPON_TYPES = {"命破"}

    def get_output_order(self, weapon_type: str) -> list:
        """根据武器类型获取属性输出顺序"""
        if weapon_type in self.MINGPO_WEAPON_TYPES:
            return self.MINGPO_WEAPON_OUTPUT_ORDER
        else:
            return self.DEFAULT_OUTPUT_ORDER

    def get_display_name(self, attr_key: str) -> str:
        """获取属性显示名称"""
        return self.ATTRIBUTE_DISPLAY_NAMES.get(attr_key, attr_key)

    def is_base_attribute(self, attr_key: str) -> bool:
        """判断是否为基础属性（贯穿力不是基础属性）"""
        return attr_key != "Sheer_Force"