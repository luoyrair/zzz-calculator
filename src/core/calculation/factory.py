# src/core/calculation/factory.py
"""计算策略工厂"""
from typing import Dict, Type

from .base import CalculationStrategy
from .breakthrough import BreakthroughStrategy
from .cache import CacheStrategy
from .chain import CalculationChain
from .core_passive import CorePassiveStrategy
from .level import LevelGrowthStrategy
from .sheer_force import SheerForceStrategy


class StrategyFactory:
    """计算策略工厂"""

    _strategy_types: Dict[str, Type[CalculationStrategy]] = {
        'level': LevelGrowthStrategy,
        'breakthrough': BreakthroughStrategy,
        'core_passive': CorePassiveStrategy,
        'sheer_force': SheerForceStrategy,
    }

    @classmethod
    def create_strategy(cls, strategy_name: str, use_cache: bool = True) -> CalculationStrategy:
        """创建策略实例"""
        print(f"[Factory] 创建策略: {strategy_name} (使用缓存: {use_cache})")

        if strategy_name not in cls._strategy_types:
            print(f"[Factory] 错误: 未知的策略类型: {strategy_name}")
            raise ValueError(f"未知的策略类型: {strategy_name}")

        strategy = cls._strategy_types[strategy_name]()
        print(f"[Factory] 策略 {strategy_name} 创建成功: {strategy.get_name()}")

        if use_cache:
            print(f"[Factory] 为策略 {strategy_name} 添加缓存包装")
            strategy = CacheStrategy(strategy)
            print(f"[Factory] 缓存包装完成: {strategy.get_name()}")

        return strategy

    @classmethod
    def create_default_chain(cls, use_cache: bool = True) -> CalculationChain:
        """创建默认计算链"""
        print(f"\n[Factory] 开始创建默认计算链 (使用缓存: {use_cache})")
        chain = CalculationChain()
        strategies = ['level', 'breakthrough', 'core_passive', 'sheer_force']

        print(f"[Factory] 默认策略顺序: {strategies}")

        for strategy_name in strategies:
            strategy = cls.create_strategy(strategy_name, use_cache)
            chain.add_strategy(strategy)

        print(f"[Factory] 默认计算链创建完成，共{len(strategies)}个策略")
        return chain