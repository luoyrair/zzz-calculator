# src/core/calculation/core_passive.py
"""核心技计算策略"""
from .base import CalculationStrategy, CalculationContext
from src.core.models.character import BaseStats


class CorePassiveStrategy(CalculationStrategy):
    """核心技等级计算策略"""

    def calculate(self, context: CalculationContext) -> BaseStats:
        result = BaseStats()

        self.debug(f"开始计算核心技加成: {context.debug_info()}")
        self.debug(f"核心技等级: {context.core_passive_level}")
        self.debug(f"角色拥有 {len(context.schema.core_passive_bonuses)} 个核心技加成")

        # 详细输出所有核心技加成
        for bonus in context.schema.core_passive_bonuses:
            self.debug(f"  等级{bonus.level}: {len(bonus.bonuses)}个加成")

        if context.core_passive_level <= 1:
            self.debug("核心技等级为1，跳过核心技加成")
            return result

        # 查找对应等级或更低等级的加成
        # 核心技加成是累积的：等级7包含所有之前等级的加成
        found_bonuses = []
        for bonus in context.schema.core_passive_bonuses:
            if bonus.level == context.core_passive_level:
                found_bonuses.append(bonus)
                self.debug(f"  包含等级{bonus.level}的加成")

        if found_bonuses:
            self.debug(f"找到{len(found_bonuses)}个核心技等级加成:")
            for bonus in found_bonuses:
                self.debug(f"  处理等级{bonus.level}:")
                for attr_type, value in bonus.bonuses.items():
                    attr_name = attr_type.value
                    if hasattr(result, attr_name):
                        current_value = getattr(result, attr_name)
                        new_value = current_value + value
                        setattr(result, attr_name, new_value)
                        self.debug(f"    应用{attr_name}: {current_value} + {value} = {new_value}")

                        # 特殊处理百分比属性
                        if attr_name in ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio", "Energy_Regen"]:
                            self.debug(f"      {attr_name}百分比值: {new_value:.2%}")
        else:
            self.debug(f"未找到核心技等级{context.core_passive_level}对应的加成")

        # 统计应用了多少个加成
        applied_count = len([v for v in vars(result).values() if v != 0])
        self.debug(f"核心技策略计算完成，应用了 {applied_count} 个属性加成")

        # 详细输出最终结果
        if applied_count > 0:
            self.debug("核心技加成最终结果:")
            for field_name in vars(result).keys():
                value = getattr(result, field_name)
                if value != 0:
                    if field_name in ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio"]:
                        self.debug(f"  {field_name}: {value:.2%}")
                    else:
                        self.debug(f"  {field_name}: {value}")

        return result

    def get_name(self) -> str:
        return "核心技策略"