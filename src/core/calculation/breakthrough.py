# src/core/calculation/breakthrough.py
"""突破计算策略"""
from .base import CalculationStrategy, CalculationContext
from src.core.models.character import BaseStats


class BreakthroughStrategy(CalculationStrategy):
    """突破阶段计算策略"""

    def calculate(self, context: CalculationContext) -> BaseStats:
        result = BaseStats()

        self.debug(f"开始计算突破加成: {context.debug_info()}")
        self.debug(f"突破等级: {context.breakthrough_level}")
        self.debug(f"角色拥有 {len(context.schema.breakthrough_stages)} 个突破阶段")

        if context.breakthrough_level <= 0:
            self.debug("突破等级为0，跳过突破加成")
            return result

        # 查找对应的突破阶段
        found_stage = None
        for stage in context.schema.breakthrough_stages:
            if stage.stage == context.breakthrough_level:
                found_stage = stage
                break

        if found_stage:
            # 应用突破阶段加成
            result.HP += stage.hp_bonus
            result.ATK += stage.atk_bonus
            result.DEF += stage.def_bonus

            self.debug(f"应用突破阶段{stage.stage}加成:")
            self.debug(f"  HP加成: +{stage.hp_bonus:.0f} (总HP: {result.HP:.0f})")
            self.debug(f"  ATK加成: +{stage.atk_bonus:.0f} (总ATK: {result.ATK:.0f})")
            self.debug(f"  DEF加成: +{stage.def_bonus:.0f} (总DEF: {result.DEF:.0f})")
        else:
            self.debug(f"未找到突破等级{context.breakthrough_level}对应的阶段")

        self.debug(f"突破策略计算完成，增加HP:{result.HP:.0f}, ATK:{result.ATK:.0f}, DEF:{result.DEF:.0f}")
        return result

    def get_name(self) -> str:
        return "突破策略"