# character_models.py
from dataclasses import dataclass, field, fields
from typing import Dict, List, Tuple


@dataclass
class CorePassiveBonus:
    """核心技等级加成配置"""
    prop_mapping: Dict[str, Tuple[str, str]] = field(default_factory=lambda: {
        "11101": ("HP", "fixed"),  # 生命值 -> HP
        "11102": ("HP", "percentage"),
        "12101": ("ATK", "fixed"),  # 基础攻击力 -> ATK
        "12201": ("IMPACT", "fixed"),
        "20101": ("CRIT_Rate", "fixed"),  # 暴击率 -> CRIT_Rate
        "21101": ("CRIT_DMG", "fixed"),
        "23101": ("PEN_Ratio", "fixed"),
        "31201": ("Anomaly_Proficiency", "fixed"),
        "30501": ("Energy_Regen", "fixed"),
        "31401": ("Anomaly_Mastery", "fixed")  # 异常精通 -> Anomaly_Mastery
    })

@dataclass
class CharacterData:
    """角色基础属性数据"""
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
class RawCharacterData:
    """从JSON解析的原始角色数据"""
    Id: int
    Name: str
    CodeName: str
    Rarity: int
    WeaponType: Dict
    ElementType: Dict
    SpecialElementType: Dict
    Stats: Dict
    Level: Dict
    ExtraLevel: Dict
    Passive: Dict
    FairyRecommend: Dict


@dataclass
class BaseCharacterStats(CharacterData):
    """计算后的角色基础属性（不含装备）"""
    Level: int = 1
    BreakthroughLevel: int = 0
    CorePassiveLevel: int = 1
    _core_passive_bonus = CorePassiveBonus()

    def calculate_from_raw(self, raw_data: RawCharacterData, level: int, breakthrough: int, core_passive_level: int):
        """从原始数据计算基础属性"""
        self.reset()
        self.Level = level
        self.BreakthroughLevel = breakthrough

        # 1. 计算基础属性（从Stats）
        self._apply_base_stats(raw_data.Stats)

        # 2. 应用突破阶段加成（从Level）
        self._apply_breakthrough_bonus(raw_data, breakthrough)

        # 3. 应用核心技等级加成（从ExtraLevel）
        self._apply_core_passive_bonus(raw_data, core_passive_level)

    def _apply_base_stats(self, stats: Dict):
        """应用基础属性"""
        self.HP = self._calculate_base_with_growth(stats.get("HpMax", 0), stats.get("HpGrowth", 0), self.Level)
        self.ATK = self._calculate_base_with_growth(stats.get("Attack", 0), stats.get("AttackGrowth", 0), self.Level)
        self.DEF = self._calculate_base_with_growth(stats.get("Defence", 0), stats.get("DefenceGrowth", 0), self.Level)
        self.CRIT_Rate = stats.get("Crit", 0) / 10000.0  # 转换为小数
        self.CRIT_DMG = stats.get("CritDamage", 0) / 10000.0  # 转换为小数
        self.Anomaly_Mastery = stats.get("ElementAbnormalPower", 0)
        self.Anomaly_Proficiency = stats.get("ElementMystery", 0)
        self.PEN_Ratio = stats.get("PenRate", 0) / 100.0
        self.PEN = stats.get("PenDelta", 0)
        self.Energy_Regen = stats.get("SpRecover", 0) / 100.0
        self.Energy_Limit = stats.get("SpBarPoint", 0)
        self.Automatic_Adrenaline_Accumulation = stats.get("RpRecover", 0) / 100.0
        self.Max_Adrenaline = stats.get("RpMax", 0)

    def _apply_breakthrough_bonus(self, raw_data: RawCharacterData, breakthrough: int):
        """应用突破阶段的属性加成（对应Level中的数据）"""
        if breakthrough > 0 and str(breakthrough) in raw_data.Level:
            level_data = raw_data.Level[str(breakthrough)]
            # Level中存储的是该突破阶段的基础属性值
            self.HP += level_data.get("HpMax", 0)
            self.ATK += level_data.get("Attack", 0)
            self.DEF += level_data.get("Defence", 0)

    def _apply_core_passive_bonus(self, raw_data: RawCharacterData, core_passive_level: int):
        """应用核心技等级的属性加成"""
        if str(core_passive_level) in raw_data.ExtraLevel:
            extra_data = raw_data.ExtraLevel[str(core_passive_level)]["Extra"]

            for prop_id, prop_data in extra_data.items():
                value = prop_data["Value"]
                format_str = prop_data.get("Format", "")

                # 获取映射关系
                mapping = self._core_passive_bonus.prop_mapping.get(prop_id)
                if not mapping:
                    continue

                target_attr, value_type = mapping

                if hasattr(self, target_attr):
                    current_value = getattr(self, target_attr)

                    if value_type == "percentage":
                        # 百分比加成：基于当前值计算
                        bonus_value = current_value * (value / 10000.0)  # 600 -> 6%
                        setattr(self, target_attr, current_value + bonus_value)
                    elif value_type == "fixed":
                        # 固定值加成
                        if target_attr == "CRIT_Rate":
                            # 暴击率需要特殊处理：除以10000
                            setattr(self, target_attr, current_value + value / 10000.0)
                        else:
                            setattr(self, target_attr, current_value + value)

    def _calculate_base_with_growth(self, base_value: int, growth_value: int, level: int) -> float:
        """计算基础值 + 成长值"""
        return base_value + (0 if level == 0 else (level - 1) * growth_value / 10000.0)


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