# src/core/character_schema.py
"""标准化角色业务数据结构"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


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
class GrowthCurve:
    """角色成长曲线"""
    base_hp: float
    hp_growth: float  # 每级成长值
    base_atk: float
    atk_growth: float
    base_def: float
    def_growth: float
    impact: int
    base_crit_rate: float  # 百分比
    base_crit_dmg: float  # 百分比
    anomaly_mastery: int
    anomaly_proficiency: int
    pen_ratio: float  # 百分比
    pen_value: int
    energy_regen: float  # 百分比
    adrenaline_accumulation: float  # 百分比


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
    bonuses: Dict[AttributeType, float]  # 属性 -> 加成值


@dataclass
class SheerForceConversion:
    """贯穿力转换系数"""
    hp_to_sheer_force: float  # 生命值转换系数
    atk_to_sheer_force: float  # 攻击力转换系数


@dataclass
class CharacterSchema:
    """标准化角色数据架构"""
    character_id: int
    name: str
    code_name: str
    rarity: int
    weapon_type: str
    element_type: str
    special_element_type: str

    growth_curve: GrowthCurve
    breakthrough_stages: List[BreakthroughStage]
    core_passive_bonuses: List[CorePassiveBonus]
    sheer_force_conversion: Optional[SheerForceConversion] = None
    passive_abilities: Dict[str, Any] = field(default_factory=dict)