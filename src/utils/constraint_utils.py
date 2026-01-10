"""
约束条件相关工具函数
"""

from typing import Tuple, Optional
from src.config.settings import settings_manager


class ConstraintUtils:
    """约束条件工具类"""

    # 等级范围定义
    LEVEL_RANGES = {
        1: (1, 10),  # 突破1: 1-10级
        2: (11, 20),  # 突破2: 11-20级
        3: (21, 30),  # 突破3: 21-30级
        4: (31, 40),  # 突破4: 31-40级
        5: (41, 50),  # 突破5: 41-50级
        6: (51, 60),  # 突破6: 51-60级
    }

    # 核心被动等级要求
    CORE_PASSIVE_REQUIREMENTS = {
        1: 0,  # 等级1: 无要求
        2: 15,  # 等级2: 15级
        3: 25,  # 等级3: 25级
        4: 35,  # 等级4: 35级
        5: 45,  # 等级5: 45级
        6: 55,  # 等级6: 55级
        7: 60,  # 等级7: 60级
    }

    def __init__(self):
        self.settings_manager = settings_manager

    def get_breakthrough_by_character_level(self, level: int, mode: Optional[int] = None) -> int:
        """根据角色等级获取突破等级"""
        if mode is None:
            settings = self.settings_manager.get_settings()
            mode = settings.level_constraints.character_level_constraint_mode

        print(f"[DEBUG ConstraintUtils] get_breakthrough_by_character_level: level={level}, mode={mode}")

        if mode == 1:
            # 模式1：默认模式
            # 突破等级 = 等级最小值≤当前等级的最大等级最小值对应的突破等级
            for breakthrough in sorted(self.LEVEL_RANGES.keys(), reverse=True):
                min_level, max_level = self.LEVEL_RANGES[breakthrough]
                if level >= min_level:
                    return breakthrough

        elif mode == 2:
            # 模式2
            # 突破等级 = 等级最大值≥当前等级且当前等级>等级最大值的等级最小值的等级最大值对应的突破等级
            for breakthrough in sorted(self.LEVEL_RANGES.keys(), reverse=True):
                min_level, max_level = self.LEVEL_RANGES[breakthrough]
                if max_level >= level > min_level:
                    return breakthrough
            # 如果当前等级等于某个突破等级的最小值，返回前一个突破等级
            for breakthrough in sorted(self.LEVEL_RANGES.keys()):
                min_level, max_level = self.LEVEL_RANGES[breakthrough]
                if level == min_level:
                    return max(1, breakthrough - 1)

        elif mode == 3:
            # 模式3：渐进模式（需要额外的状态管理）
            # 这里需要存储当前的突破等级，暂时先使用模式1
            return self.get_breakthrough_by_character_level(level, mode=1)

        return 1  # 默认返回1

    def get_character_level_range_by_breakthrough(self, breakthrough: int, mode: Optional[int] = None) -> Tuple[
        int, int]:
        """根据突破等级获取角色等级范围"""
        if mode is None:
            settings = self.settings_manager.get_settings()
            mode = settings.level_constraints.breakthrough_constraint_mode

        min_level, max_level = self.LEVEL_RANGES.get(breakthrough, (1, 60))

        if mode == 1:
            # 模式1：默认模式，等级设置为突破等级的等级最大值
            return max_level, max_level
        elif mode == 2:
            # 模式2：等级设置为突破等级的等级最小值
            return min_level, min_level

        return min_level, max_level

    def get_core_passive_by_character_level(self, level: int) -> int:
        """根据角色等级获取核心被动等级"""
        for core_passive in sorted(self.CORE_PASSIVE_REQUIREMENTS.keys(), reverse=True):
            required_level = self.CORE_PASSIVE_REQUIREMENTS[core_passive]
            if level >= required_level:
                return core_passive
        return 1

    def get_character_level_range_by_core_passive(self, core_passive: int) -> Tuple[int, int]:
        """根据核心被动等级获取角色等级范围"""
        required_level = self.CORE_PASSIVE_REQUIREMENTS.get(core_passive, 0)
        return required_level, 60  # 最低要求等级，最高60

    # 武器等级约束
    @staticmethod
    def get_refinement_by_weapon_level(level: int) -> int:
        """根据音擎等级获取突破等级"""
        if level <= 10:
            return 0
        elif level <= 20:
            return 1
        elif level <= 30:
            return 2
        elif level <= 40:
            return 3
        elif level <= 50:
            return 4
        else:
            return 5

    @staticmethod
    def get_weapon_level_range_by_refinement(refinement: int) -> Tuple[int, int]:
        """根据突破等级获取音擎等级范围"""
        if refinement == 0:
            return 1, 10
        elif refinement == 1:
            return 11, 20
        elif refinement == 2:
            return 21, 30
        elif refinement == 3:
            return 31, 40
        elif refinement == 4:
            return 41, 50
        elif refinement == 5:
            return 51, 60
        return 1, 60
