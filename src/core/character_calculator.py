# src/core/character_calculator.py
"""重构后的角色计算器 - 适配新架构"""
from typing import Dict, Any, List

from src.core.character_models import BaseCharacterStats  # 新增导入
from src.utils.character_utils import (
    calculate_character_base_stats,
    get_default_stats,
    get_default_display_info
)


class CharacterCalculator:
    """角色计算器 - 适配新架构"""

    def __init__(self, loader, config_manager):
        self.loader = loader
        self.config_manager = config_manager

        # 缓存计算结果
        self._calculation_cache: Dict[str, Dict[str, Any]] = {}

    def get_character_detailed_stats(self, character_id: str,
                                   level: int = 60,
                                   extra_level: int = 0) -> Dict[str, Any]:
        """获取角色详细属性 - 使用新架构"""
        cache_key = f"{character_id}_{level}_{extra_level}_detailed"

        if cache_key in self._calculation_cache:
            return self._calculation_cache[cache_key]

        try:
            # 加载角色数据 (现在返回RawCharacterData)
            raw_data = self.loader.load_character(character_id)
            if not raw_data:
                return self._get_default_detailed_stats()

            # 计算基础属性 - 返回BaseCharacterStats对象
            base_stats = calculate_character_base_stats(
                raw_data, level, extra_level, self.config_manager.character.stat_config
            )

            # 构建有序输出
            ordered_attributes = self._build_ordered_attributes(character_id, base_stats)

            result = {
                "character_info": self.get_character_display_info(character_id),
                "attributes": ordered_attributes,
                "base_stats": base_stats,  # 使用BaseCharacterStats对象
                "level": level,
                "extra_level": extra_level
            }

            self._calculation_cache[cache_key] = result
            return result

        except Exception as e:
            print(f"获取角色详细属性失败: {character_id}, 错误: {e}")
            return self._get_default_detailed_stats()

    def _format_attribute_value(self, attr_key: str, value: float) -> str:
        """格式化属性值显示"""
        if attr_key in ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio"]:
            return f"{value:.1%}"
        elif attr_key in ["HP", "ATK", "DEF", "Impact",
                          "Anomaly_Mastery", "Anomaly_Proficiency", "Sheer_Force"]:
            return f"{value:,.0f}"
        elif attr_key in ["Energy_Regen", "Automatic_Adrenaline_Accumulation"]:
            return f"{value:.1f}"
        else:
            return str(value)

    def _build_ordered_attributes(self, character_id: str, base_stats: BaseCharacterStats) -> Dict[str, Any]:
        """构建有序属性显示"""
        output_config = self.config_manager.character.attribute_output_config
        display_info = self.get_character_display_info(character_id)
        weapon_type = display_info.get("weapon_type", "")
        output_order = output_config.get_output_order(weapon_type)

        ordered_attributes = {}
        for attr_key in output_order:
            value = getattr(base_stats, attr_key, 0)
            ordered_attributes[attr_key] = {
                "value": value,
                "display_name": output_config.get_display_name(attr_key),
                "is_base_attribute": output_config.is_base_attribute(attr_key),
                "formatted_value": self._format_attribute_value(attr_key, value)
            }

        return ordered_attributes

    def _get_default_detailed_stats(self) -> Dict[str, Any]:
        """获取默认详细属性"""
        output_config = self.config_manager.character.attribute_output_config
        default_order = output_config.DEFAULT_OUTPUT_ORDER
        base_stats = get_default_stats()

        ordered_stats = {}
        for attr_key in default_order:
            if attr_key in base_stats:
                ordered_stats[attr_key] = {
                    "value": base_stats[attr_key],
                    "display_name": output_config.get_display_name(attr_key),
                    "is_base_attribute": output_config.is_base_attribute(attr_key),
                    "formatted_value": self._format_attribute_value(attr_key, base_stats[attr_key])
                }

        return {
            "character_info": get_default_display_info(""),
            "attributes": ordered_stats,
            "base_stats": None,
            "level": 1,
            "extra_level": 0
        }

    def get_character_display_info(self, character_id: str) -> Dict[str, str]:
        """获取角色显示信息"""
        try:
            raw_data = self.loader.load_character(character_id)
            if not raw_data:
                return get_default_display_info(character_id)

            return {
                "id": character_id,
                "name": raw_data.Name,
                "code_name": raw_data.CodeName,
                "rarity": str(raw_data.Rarity),
                "weapon_type": self.config_manager.character.display_config.get_weapon_display(
                    raw_data.WeaponType
                ),
                "element_type": self.config_manager.character.display_config.get_element_display(
                    raw_data.ElementType
                )
            }

        except Exception as e:
            print(f"获取角色显示信息失败: {character_id}, 错误: {e}")
            return get_default_display_info(character_id)

    def get_available_characters(self) -> List[Dict[str, str]]:
        """获取可用角色列表"""
        try:
            # 使用加载器获取角色列表
            characters = self.loader.get_available_characters()
            return characters

        except Exception as e:
            print(f"获取角色列表失败: {e}")
            return []

    def clear_cache(self, character_id: str = None):
        """清空缓存"""
        if character_id:
            # 删除指定角色的所有缓存
            keys_to_remove = [key for key in self._calculation_cache.keys()
                              if key.startswith(character_id)]
            for key in keys_to_remove:
                del self._calculation_cache[key]
            print(f"清空角色缓存: {character_id}")
        else:
            self._calculation_cache.clear()
            print("清空所有缓存")


# 全局实例管理 (保持不变)
_character_calculator_instance = None


def create_character_calculator(loader, config_manager):
    """创建角色计算器实例"""
    return CharacterCalculator(loader, config_manager)


def get_character_calculator(loader=None, config_manager=None):
    """获取角色计算器（延迟初始化）"""
    global _character_calculator_instance
    if _character_calculator_instance is None and loader is not None and config_manager is not None:
        _character_calculator_instance = CharacterCalculator(loader, config_manager)
    return _character_calculator_instance