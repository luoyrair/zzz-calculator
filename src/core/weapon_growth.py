"""
武器成长数据享元模式实现
全局共享的成长数据，所有武器实例共享同一份数据
"""

from dataclasses import dataclass
from typing import Dict, Optional

from src.utils.logger import get_logger

logger = get_logger("core.weapon_growth")


@dataclass
class GrowthData:
    """武器成长数据容器"""
    levels: Dict[str, Dict]  # 等级成长数据
    stars: Dict[str, Dict]  # 精炼成长数据


class WeaponGrowthFlyweight:
    """
    武器成长数据享元 - 单例模式
    所有武器实例共享同一个成长数据实例
    """
    _instance: Optional['WeaponGrowthFlyweight'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._data: Optional[GrowthData] = None
            self._initialized = True
            logger.debug("WeaponGrowthFlyweight 实例创建")

    def load_from_files(self, levels: Dict[str, Dict], stars: Dict[str, Dict]) -> bool:
        """
        从文件加载成长数据
        返回是否加载成功
        """
        try:
            self._data = GrowthData(levels=levels, stars=stars)
            logger.info(f"武器成长数据加载成功: {len(levels)}个等级, {len(stars)}个精炼等级")
            return True

        except Exception as e:
            logger.error(f"加载武器成长数据失败: {e}")
            self._data = None
            return False

    def load_from_dict(self, levels: Dict, stars: Dict):
        """从字典加载成长数据（用于测试）"""
        self._data = GrowthData(levels=levels, stars=stars)
        logger.debug("武器成长数据从字典加载成功")

    def is_loaded(self) -> bool:
        """检查数据是否已加载"""
        return self._data is not None

    def _ensure_loaded(self):
        """确保数据已加载，否则抛出异常"""
        if not self._data:
            raise RuntimeError("武器成长数据未加载，请先调用 load_from_files()")

    # ========== 等级成长相关方法 ==========

    def get_level_growth(self, level: int) -> float:
        """
        获取指定等级的成长值（返回小数，如 0.486）
        levels.json 中的值是万分比，需要除以10000
        """
        self._ensure_loaded()
        level_str = str(level)
        if level_str in self._data.levels:
            # 万分比转小数
            return self._data.levels[level_str].get("base_stat_growth", 0) / 10000.0
        logger.warning(f"未找到等级 {level} 的成长数据")
        return 0.0

    def get_level_growth_raw(self, level: int) -> int:
        """获取原始万分比值（用于调试）"""
        self._ensure_loaded()
        level_str = str(level)
        if level_str in self._data.levels:
            return self._data.levels[level_str].get("base_stat_growth", 0)
        return 0

    # ========== 精炼成长相关方法 ==========

    def get_base_stat_growth(self, refinement: int) -> float:
        """
        获取指定精炼等级的基础攻击力成长值（返回小数）
        stars.json 中的值是万分比，需要除以10000
        """
        self._ensure_loaded()
        ref_str = str(refinement)
        if ref_str in self._data.stars:
            return self._data.stars[ref_str].get("base_stat_growth", 0) / 10000.0
        logger.warning(f"未找到精炼等级 {refinement} 的基础成长数据")
        return 0.0

    def get_advanced_stat_growth(self, refinement: int) -> float:
        """
        获取指定精炼等级的高级属性成长值（返回小数）
        stars.json 中的值是万分比，需要除以10000
        """
        self._ensure_loaded()
        ref_str = str(refinement)
        if ref_str in self._data.stars:
            return self._data.stars[ref_str].get("advanced_stat_growth", 0) / 10000.0
        logger.warning(f"未找到精炼等级 {refinement} 的高级属性成长数据")
        return 0.0

    def get_refinement_range(self, refinement: int) -> tuple:
        """获取指定精炼等级对应的等级范围"""
        self._ensure_loaded()
        ref_str = str(refinement)
        if ref_str in self._data.stars:
            min_level = self._data.stars[ref_str].get("minimum_level", 0)
            max_level = self._data.stars[ref_str].get("maximum_level", 0)
            return min_level, max_level
        return 0, 0

    def get_refinement_by_level(self, level: int) -> int:
        """根据等级获取对应的精炼等级"""
        self._ensure_loaded()
        for ref_str, data in self._data.stars.items():
            min_level = data.get("minimum_level", 0)
            max_level = data.get("maximum_level", 0)
            if min_level < level <= max_level:
                return int(ref_str)
        return 0

    # ========== 批量获取方法 ==========

    def get_all_levels(self) -> Dict:
        """获取所有等级成长数据（用于调试）"""
        self._ensure_loaded()
        return self._data.levels.copy()

    def get_all_stars(self) -> Dict:
        """获取所有精炼成长数据（用于调试）"""
        self._ensure_loaded()
        return self._data.stars.copy()

    def clear(self):
        """清空数据（主要用于测试）"""
        self._data = None
        logger.debug("武器成长数据已清空")


# 创建全局享元实例
weapon_growth = WeaponGrowthFlyweight()