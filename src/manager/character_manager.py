import json
from typing import Dict, List, Optional

from src.config.manager import config_manager


class CharacterManager:
    """角色管理器 - 管理角色名称-ID映射"""

    def __init__(self):
        self._name_id_mapping: Dict[int, str] = {}
        self._id_name_mapping: Dict[str, int] = {}
        self._load_character_mappings()

    def _load_character_mappings(self):
        """加载角色名称-ID映射"""
        mapping_file = config_manager.file.character_id_name_mapping_file
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

                    print(f"加载了 {len(self._name_id_mapping)} 个角色映射")
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            self._name_id_mapping = {}
            self._id_name_mapping = {}
        except Exception as e:
            print(f"加载角色映射失败: {e}")
            self._name_id_mapping = {}
            self._id_name_mapping = {}

    def get_available_characters(self) -> List[Dict[str, str]]:
        """获取可用角色列表"""
        return [{"id": char_id, "name": char_name}
                for char_id, char_name in self._name_id_mapping.items()]

    def get_character_id_by_name(self, character_name: str) -> Optional[int]:
        """根据名称获取角色ID"""
        return self._id_name_mapping.get(character_name)

    def get_character_name_by_id(self, character_id: int) -> Optional[str]:
        """根据ID获取角色名称"""
        return self._name_id_mapping.get(character_id)