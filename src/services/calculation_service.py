# src/services/calculation_service.py
"""计算服务"""
import time
from typing import Dict

from src.config import config_manager
from src.core.cached_calculator import IncrementalCalculator
from src.core.calculator import GearCalculator
from src.core.character_calculator import CharacterCalculator
from src.core.models import GearDataManager, CalculationResult
from src.core.service_factory import get_service_factory


class CalculationService:
    """计算服务 - 单一职责：协调各种计算任务"""

    def __init__(self, use_cache: bool = True):
        self.data_manager = GearDataManager()
        self.character_calculator = CharacterCalculator(get_service_factory().character_calculator, config_manager)

        # 根据配置选择计算器
        if use_cache:
            self.gear_calculator = IncrementalCalculator(config_manager.gear)
        else:
            self.gear_calculator = GearCalculator(config_manager.gear)

        self._performance_stats = {
            "total_calculations": 0,
            "total_time_ms": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

    def calculate_gear_stats(self) -> CalculationResult:
        """计算驱动盘属性"""
        start_time = time.time()

        try:
            gear_data = self.data_manager.get_gear_data_for_calculation()
            stats = self.data_manager.character_stats

            result = self.gear_calculator.calculate_all_stats(
                gear_data,
                stats.base_hp,
                stats.base_atk,
                stats.base_def,
                stats.impact,
                stats.base_crit_rate,
                stats.base_crit_dmg,
                stats.anomaly_mastery,
                stats.anomaly_proficiency,
                stats.penetration,
                stats.energy_regen
            )

            # 更新性能统计
            calculation_time = (time.time() - start_time) * 1000
            self._update_performance_stats(calculation_time)

            return result

        except Exception as e:
            raise CalculationError(f"属性计算失败: {str(e)}")

    def calculate_character_base_stats(self, character_id: str,
                                       level: int = 60,
                                       passive_level: int = 0) -> Dict[str, float]:
        """计算角色基础属性"""
        try:
            return self.character_calculator.get_character_base_stats(
                character_id, level, passive_level
            )
        except Exception as e:
            raise CalculationError(f"角色属性计算失败: {str(e)}")

    def update_character_config(self, level: int, ascension: int,
                                passive_level: int, character_id: str = ""):
        """更新角色配置并重新计算属性"""
        # 更新配置
        self.data_manager.update_character_config(level, ascension, passive_level, character_id)

        # 如果提供了角色ID，重新计算基础属性
        if character_id:
            try:
                base_stats = self.calculate_character_base_stats(character_id, level, passive_level)
                print(base_stats)

                # 更新数据管理器中的基础属性
                self.data_manager.character_stats.base_hp = base_stats["base_hp"]
                self.data_manager.character_stats.base_atk = base_stats["base_atk"]
                self.data_manager.character_stats.base_def = base_stats["base_def"]
                self.data_manager.character_stats.impact = base_stats["impact"]
                self.data_manager.character_stats.base_crit_rate = base_stats["base_crit_rate"]
                self.data_manager.character_stats.base_crit_dmg = base_stats["base_crit_dmg"]
                self.data_manager.character_stats.anomaly_mastery = base_stats["anomaly_mastery"]
                self.data_manager.character_stats.anomaly_proficiency = base_stats["anomaly_proficiency"]
                self.data_manager.character_stats.penetration = base_stats["penetration"]
                self.data_manager.character_stats.energy_regen = base_stats["energy_regen"]


            except CalculationError:
                # 如果角色计算失败，使用默认值
                print("⚠️ 角色属性计算失败，使用默认值")

    def _update_performance_stats(self, calculation_time: float):
        """更新性能统计"""
        self._performance_stats["total_calculations"] += 1
        self._performance_stats["total_time_ms"] += calculation_time

        # 更新缓存统计
        if hasattr(self.gear_calculator, 'get_cache_stats'):
            cache_stats = self.gear_calculator.get_cache_stats()
            self._performance_stats["cache_hits"] = cache_stats.get("hits", 0)
            self._performance_stats["cache_misses"] = cache_stats.get("misses", 0)


class CalculationError(Exception):
    """计算错误异常"""
    pass


class CalculationServiceFactory:
    """计算服务工厂"""

    @staticmethod
    def create_default_service() -> CalculationService:
        """创建默认计算服务（使用缓存）"""
        return CalculationService(use_cache=True)

    @staticmethod
    def create_optimization_service() -> CalculationService:
        """创建优化计算服务（不使用缓存，用于批量计算）"""
        return CalculationService(use_cache=False)