"""
约束条件相关工具函数
"""

from typing import Tuple


class ConstraintUtils:
    """约束条件工具类"""

    # 角色等级约束
    @staticmethod
    def get_breakthrough_by_character_level(level: int) -> int:
        """根据角色等级获取突破等级"""
        if level <= 10:
            return 1
        elif level <= 20:
            return 2
        elif level <= 30:
            return 3
        elif level <= 40:
            return 4
        elif level <= 50:
            return 5
        else:
            return 6

    @staticmethod
    def get_character_level_range_by_breakthrough(breakthrough: int) -> Tuple[int, int]:
        """根据突破等级获取角色等级范围"""
        if breakthrough == 1:
            return 1, 10
        elif breakthrough == 2:
            return 11, 20
        elif breakthrough == 3:
            return 21, 30
        elif breakthrough == 4:
            return 31, 40
        elif breakthrough == 5:
            return 41, 50
        elif breakthrough == 6:
            return 51, 60
        return 1, 60

    @staticmethod
    def get_core_passive_by_character_level(level: int) -> int:
        """根据角色等级获取核心被动等级"""
        if level >= 60:
            return 7
        elif level >= 55:
            return 6
        elif level >= 45:
            return 5
        elif level >= 35:
            return 4
        elif level >= 25:
            return 3
        elif level >= 15:
            return 2
        else:
            return 1

    @staticmethod
    def get_character_level_range_by_core_passive(core_passive: int) -> Tuple[int, int]:
        """根据核心被动等级获取角色等级范围"""
        if core_passive == 7:
            return 60, 60
        elif core_passive == 6:
            return 55, 60
        elif core_passive == 5:
            return 45, 60
        elif core_passive == 4:
            return 35, 60
        elif core_passive == 3:
            return 25, 60
        elif core_passive == 2:
            return 15, 60
        else:
            return 1, 10

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
