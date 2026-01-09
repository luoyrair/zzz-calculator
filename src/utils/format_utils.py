"""
格式化工具函数
"""

from typing import Any, Dict, List, Tuple
from src.config.constants import ColorConstants


class FormatUtils:
    """格式化工具类"""

    @staticmethod
    def format_attribute_display(name: str, value: Any) -> str:
        """格式化属性显示"""
        if name in ['暴击率', '暴击伤害', '穿透率',
                    '物理伤害加成', '火属性伤害加成', '冰属性伤害加成',
                    '电属性伤害加成', '以太伤害加成']:
            if isinstance(value, (int, float)):
                return f"{value:.1%}"

        if name == '能量自动回复':
            if isinstance(value, float):
                return f"{value:.1f}"

        if isinstance(value, float):
            # 检查是否为整数的浮点数
            if value.is_integer():
                return str(int(value))
            return f"{value:.1f}"

        return str(value)

    @staticmethod
    def format_percentage(value: float, decimal_places: int = 1) -> str:
        """格式化百分比"""
        return f"{value * 100:.{decimal_places}f}%"

    @staticmethod
    def format_float(value: float, decimal_places: int = 1) -> str:
        """格式化浮点数"""
        return f"{value:.{decimal_places}f}"

    @staticmethod
    def format_stats_for_display(attributes: Dict[str, float], color: str) -> List[Tuple[str, str, str]]:
        """格式化属性数据用于显示"""
        formatted = []

        for name, value in attributes.items():
            formatted_value = FormatUtils.format_attribute_display(name, value)
            formatted.append((name, formatted_value, color))

        return formatted

    @staticmethod
    def format_gear_set_display(set_name: str, effect_desc: str) -> str:
        """格式化套装显示"""
        return f"{set_name}: {effect_desc}"

    @staticmethod
    def format_character_info(name: str, weapon_type: str, element_type: str) -> str:
        """格式化角色信息显示"""
        return f"{name} | {weapon_type} | {element_type}"

    @staticmethod
    def format_weapon_info(name: str, weapon_type: str, main_attr_name: str, main_attr_value: Any) -> str:
        """格式化武器信息显示"""
        if isinstance(main_attr_value, float) and 0 < main_attr_value < 1:
            main_attr_value = f"{main_attr_value * 100:.1f}%"

        return f"{name} | {weapon_type} | {main_attr_name} {main_attr_value}"

    @staticmethod
    def get_element_color(element_type: str) -> str:
        """获取元素颜色"""
        return ColorConstants.ELEMENT_COLORS.get(element_type, "#808080")

    @staticmethod
    def get_rarity_color(rarity: int) -> str:
        """获取稀有度颜色"""
        return ColorConstants.RARITY_COLORS.get(rarity, "#808080")

    @staticmethod
    def format_enhance_level(level: int, max_level: int = 15) -> str:
        """格式化强化等级"""
        return f"+{level}" if level > 0 else "0"

    @staticmethod
    def format_sub_attributes(attributes: Dict[int, Any]) -> str:
        """格式化副属性显示"""
        if not attributes:
            return "无"

        parts = []
        for idx, attr in sorted(attributes.items()):
            if attr:
                value_str = FormatUtils.format_attribute_display(attr.name, attr.base_value)
                parts.append(f"{idx + 1}:{attr.name} {value_str}")

        return " | ".join(parts)

    @staticmethod
    def is_recommended_attribute(attribute_name: str, recommend_data: Any) -> bool:
        """检查属性是否为推荐属性"""

        if not recommend_data:
            return False

        # 检查驱动盘主属性推荐
        if hasattr(recommend_data, 'gear_mian_attribute') and recommend_data.gear_mian_attribute:
            for pos, attr in recommend_data.gear_mian_attribute.items():
                if attr and attr.name == attribute_name:
                    return True

        # 检查驱动盘副属性推荐
        if hasattr(recommend_data, 'gear_sub_attribute') and recommend_data.gear_sub_attribute:
            if recommend_data.gear_sub_attribute.name == attribute_name:
                return True

        return False

    @staticmethod
    def is_recommended_gear_set(set_id: str, recommend_data: Any) -> bool:
        """检查驱动盘套装是否为推荐套装"""

        if not recommend_data or not hasattr(recommend_data, 'gear_set'):
            return False

        gear_set_data = recommend_data.gear_set
        if not gear_set_data:
            return False

        # 将set_id转换为字符串进行比较
        set_id_str = str(set_id)

        # 检查4件套推荐
        if hasattr(gear_set_data, 'Slot4'):
            slot4 = str(gear_set_data.Slot4)
            if slot4 == set_id_str:
                return True

        # 检查2件套推荐
        if hasattr(gear_set_data, 'Slot2'):
            slot2 = str(gear_set_data.Slot2)
            if slot2 == set_id_str:
                return True

        return False