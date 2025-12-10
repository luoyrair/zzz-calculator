# src/core/calculation/sheer_force.py
"""贯穿力计算策略"""
from .base import CalculationStrategy, CalculationContext
from src.core.models.character import BaseStats


class SheerForceStrategy(CalculationStrategy):
    """贯穿力计算策略"""

    def calculate(self, context: CalculationContext) -> BaseStats:
        result = BaseStats()

        self.debug(f"开始计算贯穿力: {context.debug_info()}")

        if not context.schema.sheer_force_conversion:
            result.Sheer_Force = 0.0
            self.debug("角色没有贯穿力转换配置，贯穿力为0")
            return result

        if not context.base_stats:
            self.debug("警告: 计算贯穿力需要基础属性，但base_stats为空")
            raise ValueError("计算贯穿力需要基础属性")

        conversion = context.schema.sheer_force_conversion

        self.debug(f"贯穿力转换系数: HP→贯穿力={conversion.hp_to_sheer_force}, "
                   f"ATK→贯穿力={conversion.atk_to_sheer_force}")
        self.debug(f"基础属性: HP={context.base_stats.HP:.0f}, ATK={context.base_stats.ATK:.0f}")

        # 计算贯穿力
        hp_contribution = context.base_stats.HP * conversion.hp_to_sheer_force
        atk_contribution = context.base_stats.ATK * conversion.atk_to_sheer_force
        result.Sheer_Force = hp_contribution + atk_contribution

        self.debug(
            f"贯穿力计算: {hp_contribution:.1f}(来自HP) + {atk_contribution:.1f}(来自ATK) = {result.Sheer_Force:.1f}")

        if result.Sheer_Force > 0:
            self.debug(
                f"最终贯穿力: {result.Sheer_Force:.1f} (约为总ATK的 {result.Sheer_Force / context.base_stats.ATK * 100:.1f}%)")
        else:
            self.debug("贯穿力计算结果为0")

        return result

    def get_name(self) -> str:
        return "贯穿力策略"