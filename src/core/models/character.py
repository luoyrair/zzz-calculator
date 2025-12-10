# src/core/models/character.py
"""角色业务模型"""
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Optional, Dict, List, Any


class AttributeType(Enum):
    """属性类型枚举"""
    HP = "HP"
    ATK = "ATK"
    DEF = "DEF"
    IMPACT = "Impact"
    CRIT_RATE = "CRIT_Rate"
    CRIT_DMG = "CRIT_DMG"
    ANOMALY_MASTERY = "Anomaly_Mastery"
    ANOMALY_PROFICIENCY = "Anomaly_Proficiency"
    PEN_RATIO = "PEN_Ratio"
    PEN = "PEN"
    ENERGY_REGEN = "Energy_Regen"
    SHEER_FORCE = "Sheer_Force"
    ADRENALINE_ACCUMULATION = "Automatic_Adrenaline_Accumulation"


@dataclass
class BaseStats:
    """基础属性容器"""
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
    Sheer_Force: float = 0.0
    Automatic_Adrenaline_Accumulation: float = 0.0

    def reset(self):
        """重置所有属性为0"""
        for f in fields(self):
            setattr(self, f.name, 0)

    def merge(self, other: 'BaseStats'):
        """合并另一个BaseStats的属性"""
        for f in fields(self):
            current_value = getattr(self, f.name)
            other_value = getattr(other, f.name, 0)
            setattr(self, f.name, current_value + other_value)


@dataclass
class CharacterBaseStats(BaseStats):
    """角色基础属性（不含装备）"""
    Level: int = 1
    BreakthroughLevel: int = 0
    CorePassiveLevel: int = 1


@dataclass
class FinalCharacterStats(CharacterBaseStats):
    """角色最终属性（含装备加成）"""
    gear_bonuses: BaseStats = field(default_factory=BaseStats)

    def __post_init__(self):
        """初始化后自动应用装备加成"""
        # 确保 gear_bonuses 是 BaseStats 类型
        if not isinstance(self.gear_bonuses, BaseStats):
            self.gear_bonuses = BaseStats()

        # 应用装备加成
        self.apply_gear_bonuses()

    def apply_gear_bonuses(self):
        """应用驱动盘加成到最终属性 - 修复百分比加成"""
        print(f"[FinalStats] 应用装备加成:")

        # 遍历所有可能的基础属性
        for field_name in [f.name for f in fields(BaseStats)]:
            if hasattr(self, field_name) and hasattr(self.gear_bonuses, field_name):
                base_value = getattr(self, field_name)
                bonus_value = getattr(self.gear_bonuses, field_name, 0)

                if bonus_value != 0:
                    # 直接相加（已经处理了百分比转换）
                    new_value = base_value + bonus_value
                    setattr(self, field_name, new_value)

                    if field_name in ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio", "Energy_Regen"]:
                        print(f"  {field_name}: {base_value:.2%} + {bonus_value:.2%} = {new_value:.2%}")
                    else:
                        print(f"  {field_name}: {base_value:.0f} + {bonus_value:.0f} = {new_value:.0f}")


@dataclass
class GrowthCurve:
    """角色成长曲线"""
    base_hp: float
    hp_growth: float
    base_atk: float
    atk_growth: float
    base_def: float
    def_growth: float
    impact: int
    base_crit_rate: float
    base_crit_dmg: float
    anomaly_mastery: int
    anomaly_proficiency: int
    pen_ratio: float
    pen_value: int
    energy_regen: float
    adrenaline_accumulation: float


@dataclass
class BreakthroughStage:
    """突破阶段加成"""
    stage: int
    hp_bonus: float
    atk_bonus: float
    def_bonus: float


@dataclass
class CorePassiveBonus:
    """核心技等级加成"""
    level: int
    bonuses: Dict[AttributeType, float]


@dataclass
class SheerForceConversion:
    """贯穿力转换系数"""
    hp_to_sheer_force: float
    atk_to_sheer_force: float

    def __repr__(self):
        return f"SheerForceConversion(HP→{self.hp_to_sheer_force}, ATK→{self.atk_to_sheer_force})"


@dataclass
class CharacterSchema:
    """角色数据架构"""
    character_id: int
    name: str
    code_name: str
    rarity: int
    weapon_type: str
    element_type: str

    growth_curve: GrowthCurve
    breakthrough_stages: List[BreakthroughStage]
    core_passive_bonuses: List[CorePassiveBonus]
    sheer_force_conversion: Optional[SheerForceConversion] = None