# src/utils/formatter.py
"""格式化工具"""


def format_value(value: float, is_percentage: bool = False) -> str:
    """格式化数值"""
    if is_percentage:
        return f"{value * 100:.1f}%"
    else:
        return f"{value:.0f}"


def format_percentage(value: float) -> str:
    """格式化百分比"""
    return f"{value * 100:.1f}%"


def format_attribute(attr_name: str, value: float) -> str:
    """格式化属性"""
    if "Rate" in attr_name or "DMG" in attr_name or "Regen" in attr_name:
        return format_percentage(value)
    else:
        return format_value(value)