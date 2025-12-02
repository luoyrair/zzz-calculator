# src/core/character_models.py
"""角色业务模型 - 专注业务逻辑"""
from dataclasses import dataclass, field, fields


@dataclass
class CharacterData:
    """角色基础属性数据 - 保持不变"""
    HP: float = 0.0
    ATK: float = 0.0
    DEF: float = 0.0
    Impact: int = 0
    CRIT_Rate: float = 0.0
    CRIT_DMG: float = 0.0
    Anomaly_Mastery: int = 0
    Anomaly_Proficiency: int = 0
    PEN_Ratio: float = 0.0
    PEN: int = 0
    Energy_Regen: float = 0.0
    Energy_Generation_Rate: int = 0
    Energy_Limit: int = 0
    Physical_DMG_Bonus: float = 0.0
    Fire_DMG_Bonus: float = 0.0
    Ice_DMG_Bonus: float = 0.0
    Electric_DMG_Bonus: float = 0.0
    Ether_DMG_Bonus: float = 0.0
    Sheer_Force: float = 0.0
    Automatic_Adrenaline_Accumulation: float = 0.0
    Adrenaline_Generation_Rate: int = 0
    Max_Adrenaline: int = 0
    Sheer_DMG_Bonus: float = 0.0

    def reset(self):
        """重置所有属性为0"""
        for f in fields(self):
            setattr(self, f.name, 0)

    def merge(self, other: 'CharacterData'):
        """合并另一个CharacterData的属性"""
        for f in fields(self):
            current_value = getattr(self, f.name)
            other_value = getattr(other, f.name, 0)
            setattr(self, f.name, current_value + other_value)

@dataclass
class BaseCharacterStats(CharacterData):
    """计算后的角色基础属性（不含装备）"""
    Level: int = 1
    BreakthroughLevel: int = 0
    CorePassiveLevel: int = 1

@dataclass
class FinalCharacterStats(BaseCharacterStats):
    """包含装备加成后的最终属性"""
    gear_bonuses: CharacterData = field(default_factory=CharacterData)

    def apply_gear_bonuses(self):
        """应用驱动盘加成到最终属性"""
        for field_name in [f.name for f in fields(CharacterData)]:
            base_value = getattr(self, field_name)
            bonus_value = getattr(self.gear_bonuses, field_name, 0)
            setattr(self, field_name, base_value + bonus_value)