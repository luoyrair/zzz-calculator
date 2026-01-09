"""
格式化工具函数
"""

from typing import Any

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