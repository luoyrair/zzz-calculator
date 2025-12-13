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
        """应用驱动盘加成到最终属性 - 修复后的版本"""
        print(f"[FinalStats] 应用装备加成:")

        # 定义不同类型的属性处理方式
        direct_percentage_attrs = ["crit_rate", "crit_dmg", "pen_ratio", "energy_regen",
                                   "physical_dmg_bonus", "fire_dmg_bonus", "ice_dmg_bonus",
                                   "electric_dmg_bonus", "ether_dmg_bonus"]

        # 基础数值属性（需要基于基础属性计算百分比的）
        base_value_attrs = ["hp", "attack", "defence", "impact", "anomaly_mastery", "pen"]

        # 遍历所有属性
        for field_name in [f.name for f in fields(BaseStats)]:
            if hasattr(self, field_name) and hasattr(self.gear_bonuses, field_name):
                bonus_value = getattr(self.gear_bonuses, field_name, 0)

                if bonus_value == 0:
                    continue

                base_value = getattr(self, field_name)

                if field_name in direct_percentage_attrs:
                    # 直接百分比属性：直接相加
                    new_value = base_value + bonus_value
                    setattr(self, field_name, new_value)
                    print(f"  {field_name}: {base_value:.2%} + {bonus_value:.2%} = {new_value:.2%}")

                elif field_name in base_value_attrs and isinstance(bonus_value, float) and bonus_value <= 1:
                    # 基于基础属性的百分比加成（小数形式）
                    # 注意：这里假设bonus_value是百分比值（如0.1表示10%）
                    # 如果装备加成已经计算了实际数值，这里应该直接相加
                    if hasattr(self.gear_bonuses, f"{field_name}_is_percentage") and getattr(self.gear_bonuses,
                                                                                             f"{field_name}_is_percentage"):
                        # 如果标记为百分比，需要乘以基础值
                        actual_bonus = base_value * bonus_value
                        new_value = base_value + actual_bonus
                        setattr(self, field_name, new_value)
                        print(
                            f"  {field_name}: {base_value:.0f} + {base_value:.0f} * {bonus_value:.2%} = {new_value:.0f}")
                    else:
                        # 直接相加（装备加成已经是实际数值）
                        new_value = base_value + bonus_value
                        setattr(self, field_name, new_value)
                        print(f"  {field_name}: {base_value:.0f} + {bonus_value:.0f} = {new_value:.0f}")

                else:
                    # 其他属性（固定值）
                    new_value = base_value + bonus_value
                    setattr(self, field_name, new_value)
                    print(f"  {field_name}: {base_value:.0f} + {bonus_value:.0f} = {new_value:.0f}")