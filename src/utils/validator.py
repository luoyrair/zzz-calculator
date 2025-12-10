# src/utils/validator.py
"""验证工具"""


def validate_level(level: int, min_level: int = 1, max_level: int = 60) -> bool:
    """验证等级"""
    return min_level <= level <= max_level


def validate_breakthrough(breakthrough_level: int, max_breakthrough: int = 6) -> bool:
    """验证突破等级"""
    return 0 <= breakthrough_level <= max_breakthrough


def validate_core_passive(core_passive_level: int, max_core_passive: int = 7) -> bool:
    """验证核心技等级"""
    return 1 <= core_passive_level <= max_core_passive


def validate_stats(stats: dict) -> bool:
    """验证属性"""
    required_fields = ['HP', 'ATK', 'DEF', 'CRIT_Rate', 'CRIT_DMG']
    return all(field in stats for field in required_fields)