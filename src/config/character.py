# src/config/character.py
"""角色配置"""
from dataclasses import dataclass, field
from typing import Dict, Any


class DisplayConfig:
    """显示配置"""

    def __init__(self):
        self.ELEMENT_TYPE_MAPPING = {
            "Physical": "物理", "Fire": "火", "Ice": "冰",
            "Electric": "电", "Ether": "以太"
        }

        self.RARITY_COLOR_MAPPING = {
            3: "#5DBCD2", 4: "#B28BEA", 5: "#FFD700"
        }

    def get_element_display(self, element_data: Dict[str, Any]) -> str:
        if not element_data:
            return "未知"
        element_key = list(element_data.values())[0] if isinstance(element_data, dict) else element_data
        return self.ELEMENT_TYPE_MAPPING.get(element_key, element_key)

    def get_rarity_color(self, rarity: int) -> str:
        return self.RARITY_COLOR_MAPPING.get(rarity, "#000000")

    def to_dict(self) -> Dict[str, Any]:
        return {
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

@dataclass
class CharacterConfig:
    """角色配置"""
    MAX_LEVEL: int = 60
    MIN_LEVEL: int = 1
    MAX_BREAKTHROUGH: int = 6
    MAX_CORE_PASSIVE: int = 7

    # 属性ID映射
    STAT_ID_MAPPING: Dict[int, str] = None
    display_config = DisplayConfig()
    # 属性输出配置
    attribute_output_config: AttributeOutputConfig = field(default_factory=AttributeOutputConfig)

    def __post_init__(self):
        if self.STAT_ID_MAPPING is None:
            self.STAT_ID_MAPPING = {
                111: "HP", 121: "ATK", 131: "DEF",
                122: "Impact", 201: "CRIT_Rate", 211: "CRIT_DMG",
                314: "Anomaly_Mastery", 312: "Anomaly_Proficiency",
                231: "PEN_Ratio", 305: "Energy_Regen"
            }

    def validate(self) -> bool:
        return bool(self.STAT_ID_MAPPING)

