# src/ui/character_manager.py
"""角色管理器 - 主要负责名称-ID映射"""
import json
from typing import Dict, List, Optional

from src.config import config_manager


class CharacterManager:
    """角色管理器 - 管理角色名称-ID映射"""

    def __init__(self):
        self._name_id_mapping: Dict[str, str] = {}
        self._id_name_mapping: Dict[str, str] = {}
        self._load_mappings()

    def _load_mappings(self):
        """加载名称-ID映射"""
        mapping_file = config_manager.file.id_name_mapping_file
        try:
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
                    # 确保映射是双向的
                    self._name_id_mapping = mappings
                    self._id_name_mapping = {v: k for k, v in mappings.items()}
        except Exception as e:
            print(f"加载角色映射失败: {e}")
            self._name_id_mapping = {}
            self._id_name_mapping = {}

    def get_available_characters(self) -> List[Dict[str, str]]:
        """获取可用角色列表"""
        return [{"id": char_id, "name": char_name}
                for char_id, char_name in self._name_id_mapping.items()]

    def get_character_id_by_name(self, character_name: str) -> Optional[str]:
        """根据名称获取角色ID"""
        return self._id_name_mapping.get(character_name)

    def get_character_name_by_id(self, character_id: str) -> Optional[str]:
        """根据ID获取角色名称"""
        return self._name_id_mapping.get(character_id)

    def add_character_mapping(self, character_id: str, character_name: str):
        """添加角色映射"""
        self._name_id_mapping[character_id] = character_name
        self._id_name_mapping[character_name] = character_id
        self._save_mappings()

    def _save_mappings(self):
        """保存映射到文件"""
        mapping_file = config_manager.file.id_name_mapping_file
        try:
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self._name_id_mapping, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存角色映射失败: {e}")