# src/config/character_config.py
"""重构后的角色配置"""
from typing import Dict, Any

from .base_config import BaseConfig


class CharacterConfig(BaseConfig):
    """角色配置 - 专注于角色相关配置"""
    
    def __init__(self):
        # 属性配置
        self.stat_config = StatConfig()
        self.level_config = LevelConfig()
        self.display_config = DisplayConfig()
        
    def validate(self) -> bool:
        """验证配置"""
        return (self.stat_config.validate() and 
                self.level_config.validate() and 
                self.display_config.validate())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "stat_config": self.stat_config.to_dict(),
            "level_config": self.level_config.to_dict(),
            "display_config": self.display_config.to_dict()
        }


class StatConfig:
    """属性配置"""

    def __init__(self):
        self.STAT_ID_MAPPING = {
            111: "生命值", 121: "攻击力", 131: "防御力",
            122: "冲击力", 123: "贯穿力", 201: "暴击率",
            211: "暴击伤害", 314: "异常掌控", 312: "异常精通",
            231: "穿透率", 305: "能量自动回复", 320: "闪能自动累积"
        }

        # ExtraLevel 属性ID映射
        self.EXTRA_PROP_MAPPING = {
            11101: (111, "生命值加成"),  # 对应基础属性ID, 显示名称
            12101: (121, "攻击力加成"),
            12201: (122, "冲击力加成"),
            20101: (201, "暴击率加成"),
            21101: (211, "暴击伤害加成"),
            31401: (314, "异常掌控加成"),
            23101: (231, "穿透率加成"),
            31201: (312, "异常精通加成"),
            30501: (305, "能量自动回复"),
        }

        self.BASE_STAT_IDS = [111, 121, 131, 122, 201, 211, 314, 312, 231, 305, 320]
        self.PERCENTAGE_STATS = [201, 211, 231, 305]
        self.DIVIDED_BY_100_STATS = [320]

    def get_stat_name(self, stat_id: int) -> str:
        return self.STAT_ID_MAPPING.get(stat_id, f"未知属性{stat_id}")

    def get_extra_prop_info(self, extra_prop_id: int) -> tuple:
        """获取ExtraLevel属性信息"""
        return self.EXTRA_PROP_MAPPING.get(extra_prop_id, (None, f"未知加成{extra_prop_id}"))

    def get_base_stat_for_extra_prop(self, extra_prop_id: int) -> int:
        """根据ExtraLevel属性ID获取对应的基础属性ID"""
        base_stat, _ = self.get_extra_prop_info(extra_prop_id)
        return base_stat

    def is_percentage_stat(self, stat_id: int) -> bool:
        return stat_id in self.PERCENTAGE_STATS

    def is_divided_by_100_stat(self, stat_id: int) -> bool:
        return stat_id in self.DIVIDED_BY_100_STATS

    def validate(self) -> bool:
        return bool(self.STAT_ID_MAPPING and self.BASE_STAT_IDS)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stat_mapping": self.STAT_ID_MAPPING,
            "extra_prop_mapping": self.EXTRA_PROP_MAPPING,
            "base_stat_ids": self.BASE_STAT_IDS
        }


class LevelConfig:
    """等级配置"""
    
    def __init__(self):
        self.MAX_LEVEL = 60
        self.MIN_LEVEL = 1
        self.MAX_ASCENSION = 6
        self.MAX_PASSIVE_LEVEL = 7
        
        self.ASCENSION_LEVELS = {
            0: 20, 1: 30, 2: 40, 3: 50, 4: 60, 5: 60, 6: 60
        }
        
        self.ASCENSION_LEVELS_LIST = [1, 20, 30, 40, 50, 60]
    
    def get_max_level_for_ascension(self, ascension: int) -> int:
        return self.ASCENSION_LEVELS.get(ascension, 60)
    
    def validate_level_config(self, level: int, ascension: int) -> bool:
        max_level = self.get_max_level_for_ascension(ascension)
        return (self.MIN_LEVEL <= level <= max_level and
                0 <= ascension <= self.MAX_ASCENSION)
    
    def validate(self) -> bool:
        return bool(self.ASCENSION_LEVELS)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_level": self.MAX_LEVEL,
            "max_ascension": self.MAX_ASCENSION,
            "ascension_levels": self.ASCENSION_LEVELS
        }


class DisplayConfig:
    """显示配置"""
    
    def __init__(self):
        self.WEAPON_TYPE_MAPPING = {
            "Sword": "剑", "Blade": "刀", "Axe": "斧",
            "Hammer": "锤", "Spear": "枪", "Bow": "弓",
            "Gun": "枪械", "Fist": "拳套", "Wand": "法杖"
        }
        
        self.ELEMENT_TYPE_MAPPING = {
            "Physical": "物理", "Fire": "火", "Ice": "冰",
            "Electric": "电", "Ether": "以太", "Quantum": "量子",
            "Imaginary": "虚数"
        }
        
        self.RARITY_COLOR_MAPPING = {
            3: "#5DBCD2", 4: "#B28BEA", 5: "#FFD700", 6: "#FF6B6B"
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
    
    def format_stat_value(self, stat_id: int, value: float) -> str:
        """格式化属性值显示"""
        from ..config import config_manager
        
        if config_manager.character.stat_config.is_percentage_stat(stat_id):
            return f"{value:.1%}" if stat_id in [201, 211] else f"{value:.1f}%"
        elif config_manager.character.stat_config.is_divided_by_100_stat(stat_id):
            return f"{value:.1f}"
        else:
            return f"{int(value)}"
    
    def validate(self) -> bool:
        return bool(self.WEAPON_TYPE_MAPPING and self.ELEMENT_TYPE_MAPPING)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "weapon_types": self.WEAPON_TYPE_MAPPING,
            "element_types": self.ELEMENT_TYPE_MAPPING
        }