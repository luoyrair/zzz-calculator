# src/core/calculation/chain.py
"""计算责任链"""
from typing import List, Optional
from .base import CalculationStrategy, CalculationContext
from src.core.models.character import BaseStats, CharacterBaseStats


class CalculationChain:
    """计算责任链"""

    def __init__(self):
        self.strategies: List[CalculationStrategy] = []
        self.context: Optional[CalculationContext] = None
        self.execution_count = 0

    def add_strategy(self, strategy: CalculationStrategy) -> 'CalculationChain':
        """添加计算策略"""
        self.strategies.append(strategy)
        print(f"[Chain] 添加策略: {strategy.get_name()} (当前共{len(self.strategies)}个策略)")
        return self

    def set_context(self, context: CalculationContext) -> 'CalculationChain':
        """设置计算上下文"""
        self.context = context
        print(f"[Chain] 设置上下文: {context.debug_info()}")
        return self

    def execute(self) -> BaseStats:
        """执行所有计算策略"""
        if not self.context:
            print("[Chain] 错误: 未设置计算上下文")
            raise ValueError("必须先设置计算上下文")

        self.execution_count += 1
        print(f"\n{'=' * 60}")
        print(f"[Chain] 第{self.execution_count}次执行计算链")
        print(f"[Chain] 上下文信息: {self.context.debug_info()}")
        print(f"[Chain] 共{len(self.strategies)}个策略，开始执行...")
        print('=' * 60)

        result = BaseStats()
        total_changes = 0

        for i, strategy in enumerate(self.strategies, 1):
            print(f"\n[Chain] 执行策略 {i}/{len(self.strategies)}: {strategy.get_name()}")
            print(f"{'-' * 40}")

            # 保存执行前的属性快照
            before_snapshot = self._create_stats_snapshot(result)

            # 执行策略
            strategy_result = strategy.calculate(self.context)

            # 合并结果
            result.merge(strategy_result)

            # 保存执行后的属性快照
            after_snapshot = self._create_stats_snapshot(result)

            # 分析变化
            changes = self._analyze_changes(before_snapshot, after_snapshot)
            if changes:
                print(f"[Chain] 策略 {strategy.get_name()} 带来的变化:")
                for change in changes:
                    print(f"  {change}")
                total_changes += len(changes)
            else:
                print(f"[Chain] 策略 {strategy.get_name()} 未带来属性变化")

            # 更新上下文中的基础属性
            if self.context.base_stats is None:
                self.context.base_stats = CharacterBaseStats()
                print(f"[Chain] 初始化base_stats")

            for field in ['HP', 'ATK', 'DEF', 'Sheer_Force']:
                if hasattr(strategy_result, field):
                    current = getattr(self.context.base_stats, field, 0)
                    new_value = current + getattr(strategy_result, field)
                    setattr(self.context.base_stats, field, new_value)
                    print(f"[Chain] 更新base_stats.{field}: {current:.0f} -> {new_value:.0f}")

        print(f"\n{'=' * 60}")
        print(f"[Chain] 计算链执行完成")
        print(f"[Chain] 总计执行了 {total_changes} 次属性修改")
        print(f"[Chain] 最终属性统计: {self._result_summary(result)}")
        print('=' * 60 + '\n')

        return result

    def clear_all_caches(self):
        """清空所有策略的缓存"""
        print(f"[Chain] 开始清空所有策略缓存")
        cache_cleared = 0
        for strategy in self.strategies:
            if hasattr(strategy, 'clear_cache'):
                strategy.clear_cache()
                cache_cleared += 1
                print(f"[Chain] 已清空策略 {strategy.get_name()} 的缓存")

        print(f"[Chain] 总共清空了 {cache_cleared} 个策略的缓存")
        self.execution_count = 0

    def _create_stats_snapshot(self, stats: BaseStats) -> dict:
        """创建属性快照"""
        snapshot = {}
        for field_name, value in vars(stats).items():
            if value != 0:
                snapshot[field_name] = value
        return snapshot

    def _analyze_changes(self, before: dict, after: dict) -> list:
        """分析属性变化"""
        changes = []

        # 检查新增的属性
        for field in after:
            if field not in before:
                changes.append(f"+ {field}: {self._format_value(field, after[field])}")
            elif before[field] != after[field]:
                delta = after[field] - before[field]
                changes.append(
                    f"Δ {field}: {self._format_value(field, before[field])} → {self._format_value(field, after[field])} (+{self._format_value(field, delta)})")

        # 检查删除的属性（理论上不会发生，但保留检查）
        for field in before:
            if field not in after:
                changes.append(f"- {field}: {self._format_value(field, before[field])} (被移除)")

        return changes

    def _result_summary(self, result: BaseStats) -> str:
        """生成结果摘要"""
        non_zero_attrs = [(k, v) for k, v in vars(result).items() if v != 0]
        if not non_zero_attrs:
            return "无有效属性"

        summaries = []
        for k, v in non_zero_attrs:
            summaries.append(f"{k}:{self._format_value(k, v)}")

        return f"{len(non_zero_attrs)}个属性: {', '.join(summaries[:5])}" + ("..." if len(summaries) > 5 else "")

    def _format_value(self, field: str, value: float) -> str:
        """格式化属性值显示"""
        if field in ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio", "Energy_Regen"]:
            return f"{value:.2%}"
        elif field in ["HP", "ATK", "DEF", "Impact", "Anomaly_Mastery",
                       "Anomaly_Proficiency", "PEN", "Sheer_Force"]:
            return f"{value:.0f}"
        elif field == "Automatic_Adrenaline_Accumulation":
            return f"{value:.2f}"
        else:
            return f"{value:.2f}"