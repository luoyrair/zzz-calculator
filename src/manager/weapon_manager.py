# src/ui/weapon_manager.py
"""音擎管理器"""
import json
from typing import Dict, List, Optional

from src.config.manager import config_manager
from src.models.character_attributes import CharacterAttributesModel
from src.models.weapon_model import WeaponSchema
from src.parsers.weapon_parsers import WeaponConverter


class WeaponManager:
    """音擎管理器 - 管理音擎名称-ID映射"""

    def __init__(self):
        self._weapons: Dict[int, WeaponSchema] = {}
        self._name_id_mapping: Dict[int, str] = {}
        self._id_name_mapping: Dict[str, int] = {}
        self._load_weapon_mappings()

    def _load_weapon_mappings(self):
        """加载音擎名称-ID映射"""
        mapping_file = config_manager.file.weapon_id_name_mapping_file
        try:
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)

                    # 清空现有映射
                    self._name_id_mapping.clear()
                    self._id_name_mapping.clear()

                    # 转换类型：JSON中的键是字符串，需要转换为int
                    for char_id_str, char_name in mappings.items():
                        try:
                            char_id = int(char_id_str)
                            self._name_id_mapping[char_id] = char_name
                            self._id_name_mapping[char_name] = char_id
                        except ValueError:
                            print(f"警告: 无法转换ID '{char_id_str}' 为整数，跳过此条目")

                    print(f"加载了 {len(self._name_id_mapping)} 个音擎映射")
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            self._name_id_mapping = {}
            self._id_name_mapping = {}
        except Exception as e:
            print(f"加载音擎映射失败: {e}")
            self._name_id_mapping = {}
            self._id_name_mapping = {}

    def get_available_weapons(self) -> List[Dict[str, str]]:
        """获取可用音擎列表"""
        return [{"id": weapon_id, "name": weapon_name}
                for weapon_id, weapon_name in self._name_id_mapping.items()]

    def get_weapon_id_by_name(self, weapon_name: str) -> Optional[int]:
        """根据名称获取音擎ID"""
        return self._id_name_mapping.get(weapon_name)

    def get_weapon_name_by_id(self, weapon_id: int) -> Optional[str]:
        """根据ID获取音擎名称"""
        return self._name_id_mapping.get(weapon_id)

    def load_weapon(self, weapon_id: int) -> Optional[WeaponSchema]:
        """加载音擎"""
        if weapon_id in self._weapons:
            return self._weapons[weapon_id]

        file_path = config_manager.file.get_weapon_file_path(str(weapon_id))
        if not file_path.exists():
            print(f"音擎文件不存在: {file_path}")
            return None

        try:
            weapon = WeaponConverter.load_from_file(file_path)
            self._weapons[weapon_id] = weapon
            return weapon
        except Exception as e:
            print(f"加载音擎失败 {weapon_id}: {e}")
            return None

    def apply_weapon_to_character(self, character_attrs: CharacterAttributesModel,
                                  weapon_id: int, level: int, star: int = None) -> bool:
        """将音擎属性应用到角色"""
        weapon = self.load_weapon(weapon_id)
        if not weapon:
            return False

        try:
            weapon.apply_to_character(character_attrs, level, star)
            return True
        except Exception as e:
            print(f"应用音擎属性失败 {weapon_id}: {e}")
            return False

    def get_weapon_stats(self, weapon_id: int, level: int, star: int = None) -> Optional[Dict[str, float]]:
        """获取音擎属性"""
        weapon = self.load_weapon(weapon_id)
        if not weapon:
            return None

        try:
            return weapon.get_stats_dict(level, star)
        except Exception as e:
            print(f"获取音擎属性失败 {weapon_id}: {e}")
            return None

    def calculate_weapon_attack(self, weapon_id: int, level: int, star: int = None) -> Optional[float]:
        """计算音擎攻击力"""
        weapon = self.load_weapon(weapon_id)
        if not weapon:
            return None

        try:
            base_atk, _ = weapon.calculate_final_values(level, star)
            return base_atk
        except Exception as e:
            print(f"计算音擎攻击力失败 {weapon_id}: {e}")
            return None

    def clear_cache(self):
        """清空缓存"""
        self._weapons.clear()