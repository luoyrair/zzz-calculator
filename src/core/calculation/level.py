# src/core/calculation/level.py
"""等级成长计算策略"""
from src.core.models.character import BaseStats
from .base import CalculationStrategy, CalculationContext


class LevelGrowthStrategy(CalculationStrategy):
    """等级成长计算策略"""

    def calculate(self, context: CalculationContext) -> BaseStats:
        result = BaseStats()
        curve = context.schema.growth_curve

        self.debug(f"开始计算等级成长: {context.debug_info()}")
        self.debug(f"成长曲线数据: HP基础={curve.base_hp}, HP成长={curve.hp_growth}")
        self.debug(f"ATK基础={curve.base_atk}, ATK成长={curve.atk_growth}")
        self.debug(f"DEF基础={curve.base_def}, DEF成长={curve.def_growth}")

        # 成长值计算
        result.HP = curve.base_hp + (context.level - 1) * curve.hp_growth
        result.ATK = curve.base_atk + (context.level - 1) * curve.atk_growth
        result.DEF = curve.base_def + (context.level - 1) * curve.def_growth

        self.debug(f"计算后属性: HP={result.HP:.1f}, ATK={result.ATK:.1f}, DEF={result.DEF:.1f}")

        # 其他固定属性
        result.Impact = curve.impact
        result.CRIT_Rate = curve.base_crit_rate
        result.CRIT_DMG = curve.base_crit_dmg
        result.Anomaly_Mastery = curve.anomaly_mastery
        result.Anomaly_Proficiency = curve.anomaly_proficiency
        result.PEN_Ratio = curve.pen_ratio
        result.PEN = curve.pen_value
        result.Energy_Regen = curve.energy_regen
        result.Automatic_Adrenaline_Accumulation = curve.adrenaline_accumulation

        self.debug(f"固定属性: Impact={result.Impact}, CRIT_Rate={result.CRIT_Rate:.2%}, "
                   f"CRIT_DMG={result.CRIT_DMG:.2%}")
        self.debug(f"异常掌控={result.Anomaly_Mastery}, 异常精通={result.Anomaly_Proficiency}")
        self.debug(f"穿透率={result.PEN_Ratio:.2%}, 穿透={result.PEN}")
        self.debug(f"能量回复={result.Energy_Regen:.2f}, 肾上腺素积累={result.Automatic_Adrenaline_Accumulation:.2f}")

        self.debug(f"等级成长策略计算完成，总计 {len([v for v in vars(result).values() if v != 0])} 个非零属性")
        return result

    def get_name(self) -> str:
        return "等级成长策略"