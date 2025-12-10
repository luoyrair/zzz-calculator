# src/core/calculation/cache.py
"""缓存策略"""
from typing import Dict
from .base import CalculationStrategy, CalculationContext
from src.core.models.character import BaseStats


class CacheStrategy(CalculationStrategy):
    """缓存策略"""

    def __init__(self, wrapped_strategy: CalculationStrategy):
        self.wrapped = wrapped_strategy
        self.cache: Dict[str, BaseStats] = {}
        self.hit_count = 0
        self.miss_count = 0

    def calculate(self, context: CalculationContext) -> BaseStats:
        cache_key = f"{self.wrapped.get_name()}_{context.get_cache_key()}"

        self.debug(f"检查缓存: {cache_key}")
        self.debug(f"缓存状态: 命中={self.hit_count}次, 未命中={self.miss_count}次")

        if cache_key in self.cache:
            self.hit_count += 1
            self.debug(f"缓存命中! (总计命中{self.hit_count}次)")
            return self.cache[cache_key]

        self.miss_count += 1
        self.debug(f"缓存未命中，执行原始计算 (总计未命中{self.miss_count}次)")

        result = self.wrapped.calculate(context)
        self.cache[cache_key] = result

        self.debug(f"缓存结果: {cache_key} -> {self._result_summary(result)}")
        return result

    def get_name(self) -> str:
        return f"缓存({self.wrapped.get_name()})"

    def clear_cache(self):
        """清空缓存"""
        cache_size = len(self.cache)
        self.debug(f"清空缓存，原有 {cache_size} 个缓存项")
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0

    def _result_summary(self, result: BaseStats) -> str:
        """生成结果摘要"""
        non_zero = [(k, v) for k, v in vars(result).items() if v != 0]
        if not non_zero:
            return "空结果"

        summary = []
        for k, v in non_zero[:3]:  # 只显示前3个属性
            if k in ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio"]:
                summary.append(f"{k}:{v:.2%}")
            else:
                summary.append(f"{k}:{v:.0f}")

        if len(non_zero) > 3:
            summary.append(f"...等{len(non_zero)}个属性")

        return ", ".join(summary)