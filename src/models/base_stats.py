from dataclasses import fields, dataclass, field


@dataclass
class BaseStats:
    """基础属性容器"""
    hp: float = 0.0
    attack: float = 0.0
    defence: float = 0.0
    impact: int = 0
    crit_rate: float = 0.0
    crit_dmg: float = 0.0
    anomaly_mastery: int = 0
    anomaly_proficiency: int = 0
    pen_ratio: float = 0.0
    pen: int = 0
    energy_regen: float = 0.0
    energy_generation_rate: int = 0
    energy_limit: int = 0
    physical_dmg_bonus: float = 0.0
    fire_dmg_bonus: float = 0.0
    ice_dmg_bonus: float = 0.0
    electric_dmg_bonus: float = 0.0
    ether_dmg_bonus: float = 0.0
    sheer_force: float = 0.0
    automatic_adrenaline_accumulation: float = 0.0
    adrenaline_generation_rate: int = 0
    max_adrenaline: int = 0
    sheer_dmg_bonus: float = 0.0

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

    def apply_gear_bonuses(self):
        """应用驱动盘加成到最终属性"""
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

                    if field_name in ["crit_rate", "crit_dmg", "pen_ratio", "energy_regen"]:
                        print(f"  {field_name}: {base_value:.2%} + {bonus_value:.2%} = {new_value:.2%}")
                    else:
                        print(f"  {field_name}: {base_value:.0f} + {bonus_value:.0f} = {new_value:.0f}")