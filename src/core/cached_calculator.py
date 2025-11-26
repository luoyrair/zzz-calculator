# src/core/cached_calculator.py
"""简化版带缓存的属性计算器"""
import hashlib
import json
from typing import Dict, Any, List

from .calculator import GearCalculator
from .models import CalculationResult


class CachedGearCalculator(GearCalculator):
    """带缓存的驱动盘属性计算器 - 单一职责：缓存管理"""

    def __init__(self, gear_config, cache_size: int = 100):
        super().__init__(gear_config)
        self.cache_size = cache_size
        self._cache: Dict[str, CalculationResult] = {}
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "size": 0
        }

    def _generate_cache_key(self, gear_data: List[Dict[str, Any]], base_hp: float,
                            base_atk: float, base_crit_rate: float, base_crit_dmg: float) -> str:
        """生成缓存键"""
        # 创建数据的紧凑表示
        cache_data = {
            "gear_data": self._simplify_gear_data(gear_data),
            "base_stats": {
                "hp": round(base_hp, 2),
                "atk": round(base_atk, 2),
                "crit_rate": round(base_crit_rate, 4),
                "crit_dmg": round(base_crit_dmg, 4)
            }
        }

        # 使用MD5哈希作为缓存键
        data_str = json.dumps(cache_data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()

    def _simplify_gear_data(self, gear_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """简化装备数据用于缓存键生成"""
        simplified = []

        for gear in gear_data:
            simple_gear = {}

            # 简化主属性
            main_attr = gear.get("main_attr")
            if main_attr:
                simple_gear["main"] = {
                    "name": main_attr.get("name"),
                    "value": round(main_attr.get("value", 0), 4)
                }

            # 简化副属性
            sub_attrs = []
            for sub_attr in gear.get("sub_attrs", []):
                if sub_attr:
                    sub_attrs.append({
                        "name": sub_attr.get("name"),
                        "value": round(sub_attr.get("value", 0), 4)
                    })
            simple_gear["subs"] = sub_attrs

            simplified.append(simple_gear)

        return simplified

    def calculate_all_stats(self, gear_data: List[Dict[str, Any]],
                            base_hp: float, base_atk: float, base_def: float,
                            impact: int, base_crit_rate: float, base_crit_dmg: float,
                            anomaly_mastery: int, anomaly_proficiency: int, penetration: float, energy_regen: int
                            ) -> CalculationResult:
        """带缓存的完整属性计算"""
        cache_key = self._generate_cache_key(gear_data, base_hp, base_atk, base_crit_rate, base_crit_dmg)

        # 检查缓存
        if cache_key in self._cache:
            self._cache_stats["hits"] += 1
            return self._cache[cache_key]

        # 缓存未命中，进行计算
        self._cache_stats["misses"] += 1
        result = super().calculate_all_stats(gear_data,
                                             base_hp, base_atk, base_def, impact,
                                             base_crit_rate, base_crit_dmg,
                                             anomaly_mastery, anomaly_proficiency, penetration, energy_regen)

        # 更新缓存
        self._update_cache(cache_key, result)

        return result

    def _update_cache(self, cache_key: str, result: CalculationResult):
        """更新缓存"""
        # 如果缓存已满，移除最旧的条目
        if len(self._cache) >= self.cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        # 添加新条目
        self._cache[cache_key] = result
        self._cache_stats["size"] = len(self._cache)

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = self._cache_stats.copy()

        total_requests = stats["hits"] + stats["misses"]
        stats["hit_rate"] = stats["hits"] / total_requests if total_requests > 0 else 0
        stats["total_requests"] = total_requests

        return stats

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "size": 0
        }


class IncrementalCalculator(CachedGearCalculator):
    """增量计算器 - 优化连续计算性能"""

    def __init__(self, gear_config, cache_size: int = 50):
        super().__init__(gear_config, cache_size)
        self._last_calculation = None
        self._last_cache_key = None

    def calculate_all_stats(self, gear_data: List[Dict[str, Any]],
                            base_hp: float, base_atk: float, base_def: float,
                            impact: int, base_crit_rate: float, base_crit_dmg: float,
                            anomaly_mastery: int, anomaly_proficiency: int, penetration: float, energy_regen: int
                            ) -> CalculationResult:
        """增量计算实现"""
        current_key = self._generate_cache_key(gear_data, base_hp, base_atk, base_crit_rate, base_crit_dmg)

        # 如果数据没有变化，返回上次结果
        if self._last_cache_key == current_key and self._last_calculation is not None:
            self._cache_stats["hits"] += 1
            return self._last_calculation

        # 否则进行完整计算
        result = super().calculate_all_stats(gear_data,
                                             base_hp, base_atk, base_def, impact,
                                             base_crit_rate, base_crit_dmg,
                                             anomaly_mastery, anomaly_proficiency, penetration, energy_regen)

        # 保存当前状态
        self._last_calculation = result
        self._last_cache_key = current_key

        return result

    def force_recalculate(self):
        """强制重新计算"""
        self._last_cache_key = None
        self._last_calculation = None
        self.clear_cache()


class CalculatorFactory:
    """计算器工厂"""

    @staticmethod
    def create_calculator(gear_config, use_cache: bool = True, use_incremental: bool = True):
        """创建计算器实例"""
        if not use_cache:
            return GearCalculator(gear_config)
        elif use_incremental:
            return IncrementalCalculator(gear_config)
        else:
            return CachedGearCalculator(gear_config)

    @staticmethod
    def create_default_calculator(gear_config):
        """创建默认计算器（使用增量缓存）"""
        return IncrementalCalculator(gear_config)

    @staticmethod
    def create_simple_calculator(gear_config):
        """创建简单计算器（无缓存）"""
        return GearCalculator(gear_config)