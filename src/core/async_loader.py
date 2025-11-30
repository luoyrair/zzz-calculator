# src/core/async_loader.py
"""重构后的异步加载器 - 适配新架构"""
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List

from src.config import config_manager
from src.core.character_models import RawCharacterData  # 新增导入


@dataclass
class LoadResult:
    """加载结果"""
    success: bool
    data: Any = None
    error: str = ""
    file_path: str = ""
    from_cache: bool = False


class CharacterLoader:
    """角色数据加载器 - 适配新架构"""

    def __init__(self, use_async: bool = True):
        self.use_async = use_async
        self.thread_pool = ThreadPoolExecutor(max_workers=3) if use_async else None
        self._cache: Dict[str, RawCharacterData] = {}  # 缓存类型改为RawCharacterData

    def load_character(self, character_id: str, callback: Callable = None) -> Optional[RawCharacterData]:
        """加载角色数据 - 返回RawCharacterData对象"""
        # 检查缓存
        if character_id in self._cache:
            result = LoadResult(True, self._cache[character_id], "", "", True)
            if callback:
                callback(result)
            return result.data

        file_path = config_manager.file.get_character_file_path(character_id)

        if self.use_async and self.thread_pool and callback:
            # 异步加载
            future = self.thread_pool.submit(self._load_file_sync, file_path, character_id)
            future.add_done_callback(lambda f: self._handle_async_result(f, character_id, callback))
            return None
        else:
            # 同步加载
            return self._load_file_sync(file_path, character_id)

    def _load_file_sync(self, file_path: Path, character_id: str = "") -> Optional[RawCharacterData]:
        """同步加载文件 - 返回RawCharacterData对象"""
        try:
            if not file_path.exists():
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # 转换为RawCharacterData对象
            raw_data = self._convert_to_raw_character_data(json_data)

            # 缓存数据
            if character_id:
                self._cache[character_id] = raw_data

            return raw_data

        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
            return None

    def _convert_to_raw_character_data(self, json_data: Dict[str, Any]) -> RawCharacterData:
        """将JSON数据转换为RawCharacterData对象"""
        return RawCharacterData(
            Id=json_data.get("Id", 0),
            Name=json_data.get("Name", ""),
            CodeName=json_data.get("CodeName", ""),
            Rarity=json_data.get("Rarity", 4),
            WeaponType=json_data.get("WeaponType", {}),
            ElementType=json_data.get("ElementType", {}),
            SpecialElementType=json_data.get("SpecialElementType", {}),
            Stats=json_data.get("Stats", {}),
            Level=json_data.get("Level", {}),
            ExtraLevel=json_data.get("ExtraLevel", {}),
            Passive=json_data.get("Passive", {}),
            FairyRecommend=json_data.get("FairyRecommend", {})
        )

    def _handle_async_result(self, future, character_id: str, callback: Callable):
        """处理异步结果"""
        try:
            data = future.result()
            if data and character_id:
                self._cache[character_id] = data

            result = LoadResult(True, data, "", "", False)
            callback(result)

        except Exception as e:
            result = LoadResult(False, None, str(e), "", False)
            callback(result)

    def clear_cache(self, character_id: str = None):
        """清空缓存"""
        if character_id:
            self._cache.pop(character_id, None)
        else:
            self._cache.clear()

    def shutdown(self):
        """关闭线程池"""
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)


class CharacterManager:
    """角色管理器 - 适配新架构"""

    def __init__(self):
        self.loader = CharacterLoader()
        self._available_characters: Dict[str, str] = {}
        self._load_character_mapping()

    def _load_character_mapping(self):
        """加载角色映射"""
        mapping_file = config_manager.file.id_name_mapping_file
        try:
            if mapping_file.exists():
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    self._available_characters = json.load(f)
        except Exception as e:
            print(f"加载角色映射失败: {e}")

    def get_available_characters(self) -> List[Dict[str, str]]:
        """获取可用角色列表"""
        return [{"id": char_id, "name": char_name}
                for char_id, char_name in self._available_characters.items()]

    def get_character_id_by_name(self, character_name: str) -> Optional[str]:
        """根据名称获取角色ID"""
        for char_id, char_name in self._available_characters.items():
            if char_name == character_name:
                return char_id
        return None

    def preload_character(self, character_id: str):
        """预加载角色数据"""
        self.loader.load_character(character_id)