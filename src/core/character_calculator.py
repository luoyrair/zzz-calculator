# src/core/character_calculator.py
"""重构后的角色计算器 - 使用工具函数"""
from typing import Dict, Any, List
from src.utils.character_utils import (
    calculate_character_stats,
    get_default_stats,
    get_default_display_info
)


class CharacterCalculator:
    """角色计算器 - 单一职责：计算角色相关属性"""

    def __init__(self, loader, config_manager):
        self.loader = loader
        self.config_manager = config_manager

        # 缓存计算结果
        self._calculation_cache: Dict[str, Dict[str, Any]] = {}

    def get_character_base_stats(self, character_id: str,
                                 level: int = 60,
                                 passive_level: int = 0) -> Dict[str, float]:
        """获取角色基础属性"""
        cache_key = f"{character_id}_{level}_{passive_level}"

        # 检查缓存
        if cache_key in self._calculation_cache:
            print(f"缓存命中: {cache_key}")
            return self._calculation_cache[cache_key]

        try:
            # 加载角色数据
            character_data = self.loader.load_character(character_id)
            if not character_data:
                print(f"角色数据不存在: {character_id}")
                return get_default_stats()

            # 使用工具函数计算属性
            stats = calculate_character_stats(character_data, level, self.config_manager.character.stat_config)

            # 缓存结果
            self._calculation_cache[cache_key] = stats

            print(f"计算角色属性成功: {character_id}, 等级: {level}")
            return stats

        except Exception as e:
            print(f"计算角色属性失败: {character_id}, 错误: {e}")
            return get_default_stats()

    def get_character_display_info(self, character_id: str) -> Dict[str, str]:
        """获取角色显示信息"""
        try:
            character_data = self.loader.load_character(character_id)
            if not character_data:
                return get_default_display_info(character_id)

            return {
                "id": character_id,
                "name": character_data.get("Name", "未知角色"),
                "code_name": character_data.get("CodeName", "未知"),
                "rarity": str(character_data.get("Rarity", 4)),
                "weapon_type": self.config_manager.character.display_config.get_weapon_display(
                    character_data.get("WeaponType", {})
                ),
                "element_type": self.config_manager.character.display_config.get_element_display(
                    character_data.get("ElementType", {})
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

    def preload_character_data(self, character_id: str):
        """预加载角色数据"""
        try:
            self.loader.preload_character(character_id)
            print(f"预加载角色数据: {character_id}")
        except Exception as e:
            print(f"预加载角色数据失败: {character_id}, 错误: {e}")

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


# 全局实例管理
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