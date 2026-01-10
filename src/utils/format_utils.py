"""
格式化工具函数 - 添加设置检查
"""

from typing import Any

from src.config.constants import ColorConstants
from src.config.settings import settings_manager


class FormatUtils:
    """格式化工具类"""

    @staticmethod
    def generate_placeholder_data(character=None):
        """动态生成占位数据（按需调用）"""

        # 获取显示设置
        settings = settings_manager.get_settings()
        basic_content_mode = settings.display.basic_attributes_display_mode

        print(f"[DEBUG LeftPanel] 基础属性内容模式: {basic_content_mode} (1=角色基础属性, 2=所有属性)")

        # 1. 基础属性（所有角色都有的）
        basic_attrs = [
            ("生命值", "0"),
            ("攻击力", "0"),
            ("防御力", "0"),
            ("冲击力", "0"),
            ("暴击率", "0.0%"),
            ("暴击伤害", "0.0%"),
            ("异常掌控", "0"),
            ("异常精通", "0"),
        ]

        if basic_content_mode == 2:
            # 模式2：显示所有属性
            basic_attrs.extend([
                ("穿透率", "0.0%"),
                ("穿透值", "0"),
                ("能量自动回复", "0.0"),
                ("物理伤害加成", "0.0%"),
                ("火属性伤害加成", "0.0%"),
                ("冰属性伤害加成", "0.0%"),
                ("电属性伤害加成", "0.0%"),
                ("以太伤害加成", "0.0%"),
                ("贯穿力", "0"),
                ("闪能自动积蓄", "0.0"),
                ("贯穿伤害加成", "0.0%"),
            ])
        elif character and basic_content_mode == 1:
            # 模式1：显示角色基础属性，根据角色类型添加特定属性
            if character.weapon_type == "命破":
                # 命破角色：加上贯穿力、闪能自动积蓄、对应的属性伤害加成
                basic_attrs.extend([("贯穿力", "0"), ("闪能自动积蓄", "0.0"), ])
            else:
                # 非命破角色：加上穿透率、能量自动回复、穿透值、对应的属性伤害加成
                basic_attrs.extend([("穿透率", "0.0%"), ("能量自动回复", "0.0"), ("穿透值", "0"), ])

            # 添加对应的属性伤害加成
            basic_attrs.append((f"{character.element_type}伤害加成", "0.0%"))
        else:
            # 没有角色或模式1但没有角色时，显示基础属性
            pass

        # 格式：(name, value, name_color, value_color)
        basic_data = [
            (name, value, ColorConstants.BASIC_COLOR, ColorConstants.BASIC_ATTRIBUTE_COLOR)
            for name, value in basic_attrs
        ]

        character_data = [
            (name, value, ColorConstants.BASIC_COLOR, ColorConstants.CHARACTER_ATTRIBUTE_COLOR)
            for name, value in basic_attrs
        ]

        print(f"[DEBUG LeftPanel] 生成占位数据: {len(basic_attrs)} 个属性")
        print(
            f"[DEBUG LeftPanel] 角色类型: {character.weapon_type if character else '无'}, 元素类型: {character.element_type if character else '无'}")

        return basic_data, character_data

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