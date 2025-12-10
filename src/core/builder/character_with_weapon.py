# src/core/builder/character_with_weapon.py
"""包含音擎的角色构建器"""
from src.core.calculation.flow import AttackCalculationFlow, HpDefCalculationFlow
from src.core.models.character import CharacterBaseStats


class CharacterBuilderWithWeapon:
    """包含音擎的角色构建器"""

    def __init__(self, schema, weapon_service=None):
        self.schema = schema
        self.weapon_service = weapon_service
        self.attack_flow = AttackCalculationFlow(schema, weapon_service)
        self.hp_def_flow = HpDefCalculationFlow(schema)

    def set_weapon(self, weapon_id: int, level: int, stars: int = None):
        """设置音擎"""
        self.attack_flow.set_weapon(weapon_id, level, stars)
        return self

    def build_base_stats(self, level: int, breakthrough_level: int,
                         core_passive_level: int) -> CharacterBaseStats:
        """构建基础属性"""
        stats = CharacterBaseStats()
        stats.Level = level
        stats.BreakthroughLevel = breakthrough_level
        stats.CorePassiveLevel = core_passive_level

        print(f"\n{'=' * 50}")
        print(f"开始构建角色属性")
        print(f"{'=' * 50}\n")

        # 1. 计算HP
        stats.HP = self.hp_def_flow.calculate_final_hp(
            level, breakthrough_level, core_passive_level
        )

        # 2. 计算DEF
        stats.DEF = self.hp_def_flow.calculate_final_def(
            level, breakthrough_level, core_passive_level
        )

        # 3. 计算攻击力
        stats.ATK = self.attack_flow.calculate_final_attack(
            level, breakthrough_level, core_passive_level
        )

        # 4. 设置固定属性
        curve = self.schema.growth_curve
        stats.Impact = curve.impact
        stats.CRIT_Rate = curve.base_crit_rate
        stats.CRIT_DMG = curve.base_crit_dmg
        stats.Anomaly_Mastery = curve.anomaly_mastery
        stats.Anomaly_Proficiency = curve.anomaly_proficiency
        stats.PEN_Ratio = curve.pen_ratio
        stats.PEN = curve.pen_value
        stats.Energy_Regen = curve.energy_regen
        stats.Automatic_Adrenaline_Accumulation = curve.adrenaline_accumulation

        # 5. 应用音擎的其他属性加成
        weapon_bonuses = self.attack_flow.get_weapon_bonuses()
        for attr_name, value in weapon_bonuses.items():
            if hasattr(stats, attr_name):
                current_value = getattr(stats, attr_name)
                setattr(stats, attr_name, current_value + value)

        # 6. 计算贯穿力
        if self.schema.sheer_force_conversion:
            stats.Sheer_Force = self._calculate_sheer_force(stats)

        print(f"\n{'=' * 50}")
        print(f"角色属性构建完成")
        print(f"{'=' * 50}")

        return stats

    def _calculate_sheer_force(self, stats: CharacterBaseStats) -> float:
        """计算贯穿力"""
        conversion = self.schema.sheer_force_conversion
        sheer_force = (
                stats.HP * conversion.hp_to_sheer_force +
                stats.ATK * conversion.atk_to_sheer_force
        )
        return sheer_force