"""
格式化工具函数 - 添加设置检查
"""

from typing import Any

from src.config.constants import ColorConstants
from src.config.settings import settings_manager
from src.utils.logger import get_logger


class FormatUtils:
    """格式化工具类"""

    def format_stats_with_recommendation(self, attributes: dict, base_color: str):
        """格式化属性数据，标记推荐属性（只标记属性名）"""
        formatted = []

        for name, value in attributes.items():
            formatted_value = self.format_attribute_display(name, value)

            # 检查是否为推荐属性
            is_recommended = self.is_recommended_attribute(name)

            # 如果为推荐属性，属性名使用橙色，否则使用基础颜色
            if is_recommended:
                # 属性名用橙色，属性值用基础颜色
                formatted.append((name, formatted_value, ColorConstants.RECOMMENDED_COLOR, base_color))
            else:
                # 属性名和属性值都用基础颜色
                formatted.append((name, formatted_value, ColorConstants.BASIC_COLOR, base_color))

        return formatted

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
    def is_recommended_attribute(attribute_name: str) -> bool:
        """检查属性是否为推荐属性 - 添加设置检查"""

        from src.core.state_manager import StateManager
        state = StateManager.instance().get_state()

        # 直接从状态管理器获取推荐数据
        recommend_data = state.recommend_data if state.current_character else None

        # 首先检查设置：是否使用原始推荐数据
        settings = settings_manager.get_settings()
        if not settings.auto_select.use_original_recommendations:
            return False

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

logger = get_logger("FormatUtils")