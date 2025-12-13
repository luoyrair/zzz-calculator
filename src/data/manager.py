# src/data/manager.py
"""数据中心管理器"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import json

from src.config.manager import config_manager


@dataclass
class CharacterInfo:
    """角色信息"""
    id: int
    name: str
    rarity: int
    weapon_type: str
    element_type: str
    file_path: Path


@dataclass
class WeaponInfo:
    """音擎信息"""
    id: int
    name: str
    rarity: int
    file_path: Path


@dataclass
class GearSetInfo:
    """装备套装信息"""
    id: int
    name: str
    description: str
    bonuses: Dict[str, float]


class DataManager:
    """统一的数据管理器"""

    def __init__(self):
        self._characters: Dict[int, CharacterInfo] = {}
        self._weapons: Dict[int, WeaponInfo] = {}
        self._gear_sets: Dict[int, GearSetInfo] = {}

        # 加载所有数据
        self.load_all_data()

    def load_all_data(self):
        """加载所有数据"""
        try:
            self.load_characters()
            self.load_weapons()
            self.load_gear_sets()
            print(
                f"数据加载完成: {len(self._characters)}个角色, {len(self._weapons)}个音擎, {len(self._gear_sets)}个套装")
        except Exception as e:
            print(f"数据加载失败: {e}")

    def load_characters(self):
        """加载角色信息"""
        mapping_file = config_manager.file.character_id_name_mapping_file
        if not mapping_file.exists():
            return

        with open(mapping_file, 'r', encoding='utf-8') as f:
            mappings = json.load(f)

        for char_id_str, char_name in mappings.items():
            try:
                char_id = int(char_id_str)
                file_path = config_manager.file.get_character_file_path(str(char_id))
                if file_path.exists():
                    # 从角色文件读取详细信息
                    with open(file_path, 'r', encoding='utf-8') as f:
                        char_data = json.load(f)

                    self._characters[char_id] = CharacterInfo(
                        id=char_id,
                        name=char_name,
                        rarity=char_data.get("Rarity", 0),
                        weapon_type=self._get_weapon_type(char_data.get("WeaponType", {})),
                        element_type=self._get_element_type(char_data.get("ElementType", {})),
                        file_path=file_path
                    )
            except Exception as e:
                print(f"加载角色 {char_id_str} 失败: {e}")

    def _get_weapon_type(self, weapon_data: dict) -> str:
        """从武器类型数据获取显示名称"""
        return next(iter(weapon_data.values()), "未知")

    def _get_element_type(self, element_data: dict) -> str:
        """从元素类型数据获取显示名称"""
        return next(iter(element_data.values()), "未知")

    def load_weapons(self):
        """加载音擎信息"""
        mapping_file = config_manager.file.weapon_id_name_mapping_file
        if not mapping_file.exists():
            return

        with open(mapping_file, 'r', encoding='utf-8') as f:
            mappings = json.load(f)

        for weapon_id_str, weapon_name in mappings.items():
            try:
                weapon_id = int(weapon_id_str)
                file_path = config_manager.file.get_weapon_file_path(str(weapon_id))
                if file_path.exists():
                    # 从音擎文件读取详细信息
                    with open(file_path, 'r', encoding='utf-8') as f:
                        weapon_data = json.load(f)

                    self._weapons[weapon_id] = WeaponInfo(
                        id=weapon_id,
                        name=weapon_name,
                        rarity=weapon_data.get("Rarity", 2),
                        file_path=file_path
                    )
            except Exception as e:
                print(f"加载音擎 {weapon_id_str} 失败: {e}")

    def load_gear_sets(self):
        """加载装备套装信息"""
        equipment_file = config_manager.file.equipment_file
        if not equipment_file.exists():
            return

        with open(equipment_file, 'r', encoding='utf-8') as f:
            equipment_data = json.load(f)

        for set_id_str, set_data in equipment_data.items():
            try:
                set_id = int(set_id_str)
                self._gear_sets[set_id] = GearSetInfo(
                    id=set_id,
                    name=set_data.get("name", ""),
                    description=set_data.get("desc2", ""),
                    bonuses=self._parse_bonuses(set_data.get("desc2", ""))
                )
            except Exception as e:
                print(f"加载套装 {set_id_str} 失败: {e}")

    def _parse_bonuses(self, description: str) -> Dict[str, float]:
        """解析套装加成描述"""
        bonuses = {}
        # 这里可以添加更复杂的解析逻辑
        return bonuses

    # 查询方法
    def get_all_characters(self) -> List[CharacterInfo]:
        """获取所有角色"""
        return list(self._characters.values())

    def get_character(self, character_id: int) -> Optional[CharacterInfo]:
        """获取指定角色"""
        return self._characters.get(character_id)

    def get_character_by_name(self, name: str) -> Optional[CharacterInfo]:
        """通过名称获取角色"""
        for char in self._characters.values():
            if char.name == name:
                return char
        return None

    def get_all_weapons(self) -> List[WeaponInfo]:
        """获取所有音擎"""
        return list(self._weapons.values())

    def get_weapon(self, weapon_id: int) -> Optional[WeaponInfo]:
        """获取指定音擎"""
        return self._weapons.get(weapon_id)

    def get_weapon_by_name(self, name: str) -> Optional[WeaponInfo]:
        """通过名称获取音擎"""
        for weapon in self._weapons.values():
            if weapon.name == name:
                return weapon
        return None

    def get_all_gear_sets(self) -> List[GearSetInfo]:
        """获取所有装备套装"""
        return list(self._gear_sets.values())

    def get_gear_set(self, set_id: int) -> Optional[GearSetInfo]:
        """获取指定套装"""
        return self._gear_sets.get(set_id)


# 创建全局数据管理器实例
data_manager = DataManager()