# src/core/attribute_calculator.py
"""属性计算服务 - 处理所有属性类型转换和计算逻辑"""
from src.config.gear_config import GearAttribute, AttributeValueType
from src.core.character_models import BaseCharacterStats, CharacterData


class AttributeCalculator:
    """属性计算器 - 专门处理属性类型转换和计算"""

    def __init__(self, gear_config):
        self.gear_config = gear_config

    def calculate_gear_attribute_contribution(self, gear_key: str, gear_value: float,
                                              base_stats: BaseCharacterStats) -> CharacterData:
        """计算单个驱动盘属性的贡献"""
        print(f"[DEBUG] AttributeCalculator: gear_key='{gear_key}', gear_value={gear_value}")  # 新增调试

        gear_attr = self.gear_config.attribute_config.get_gear_attribute(gear_key)
        if not gear_attr:
            print(f"[ERROR] 未找到gear_key='{gear_key}'对应的属性定义")  # 新增调试
            return CharacterData()

        print(
            f"[DEBUG] 找到属性: {gear_attr.display_name}, 类型={gear_attr.attribute_type.value}, 值类型={gear_attr.value_type.value}")  # 新增调试

        return self._calculate_contribution_by_type(gear_attr, gear_value, base_stats)

    def _calculate_contribution_by_type(self, gear_attr: GearAttribute, gear_value: float,
                                        base_stats: BaseCharacterStats) -> CharacterData:
        """根据属性类型计算贡献"""
        print(f"[DEBUG] 计算贡献: {gear_attr.display_name}, 值={gear_value}, 类型={gear_attr.value_type.value}")
        bonus = CharacterData()
        final_key = gear_attr.get_final_attribute_key()
        print(f"[DEBUG] 最终属性键: {final_key}")

        if gear_attr.value_type == AttributeValueType.FIXED_VALUE:
            # 固定值直接叠加
            self._add_fixed_value(bonus, final_key, gear_value)

        elif gear_attr.value_type == AttributeValueType.PERCENTAGE:
            # 百分比加成基于基础属性
            if gear_attr.base_attribute:
                base_value = getattr(base_stats, gear_attr.base_attribute.value, 0)
                actual_value = base_value * gear_value
                self._add_fixed_value(bonus, final_key, actual_value)

        elif gear_attr.value_type == AttributeValueType.RATE_PERCENTAGE:
            # 比率百分比直接叠加
            self._add_percentage_value(bonus, final_key, gear_value)

        elif gear_attr.value_type == AttributeValueType.DMG_BONUS_PERCENTAGE:
            # 伤害加成百分比直接叠加
            self._add_percentage_value(bonus, final_key, gear_value)

        return bonus

    def _add_fixed_value(self, bonus: CharacterData, attr_key: str, value: float):
        """添加固定值"""
        print(f"[DEBUG] _add_fixed_value: attr_key='{attr_key}', value={value}")  # 新增调试
        if hasattr(bonus, attr_key):
            current = getattr(bonus, attr_key)
            setattr(bonus, attr_key, current + value)
            print(f"[DEBUG]  成功添加: {attr_key} = {current} + {value} = {getattr(bonus, attr_key)}")  # 新增调试
        else:
            print(f"[ERROR] CharacterData没有属性'{attr_key}'")  # 新增调试

    def _add_percentage_value(self, bonus: CharacterData, attr_key: str, value: float):
        """添加百分比值"""
        if hasattr(bonus, attr_key):
            current = getattr(bonus, attr_key)
            setattr(bonus, attr_key, current + value)