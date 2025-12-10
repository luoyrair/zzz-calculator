# src/services/character.py
"""角色业务服务"""
from typing import Optional, Dict

from src.core.builder.character import CharacterBuilder
from src.core.models.character import CharacterBaseStats
from src.data.models.character import JsonCharacterData
from src.data.converter.character import CharacterSchemaConverter


class CharacterService:
    """角色服务"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.schema_converter = CharacterSchemaConverter(config_manager)
        self._character_cache: Dict[str, CharacterBuilder] = {}

    def load_character_by_id(self, character_id: str) -> bool:
        """加载角色"""
        try:
            if character_id in self._character_cache:
                return True

            file_path = self.config_manager.file.get_character_file_path(character_id)
            if not file_path.exists():
                return False

            # 加载JSON数据
            json_data = JsonCharacterData.from_json_file(str(file_path))
            if json_data.Id == 0:
                return False

            # 转换为标准架构
            schema = self.schema_converter.convert(json_data)

            # 创建构建器
            builder = CharacterBuilder(schema)

            # 缓存
            self._character_cache[character_id] = builder

            return True

        except Exception as e:
            print(f"加载角色异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_character_builder(self, character_id: str) -> Optional[CharacterBuilder]:
        """获取角色构建器"""
        if character_id not in self._character_cache:
            if not self.load_character_by_id(character_id):
                return None
        return self._character_cache[character_id]

    def calculate_character_stats(self, level: int, breakthrough_level: int,
                                 core_passive_level: int) -> Optional[CharacterBaseStats]:
        """计算角色属性"""
        # 这个方法需要根据实际情况实现
        # 这里需要您提供一个角色ID或角色名称来获取构建器
        return None

    def get_character_display_info(self, character_id: str = None) -> Dict[str, any]:
        """获取角色显示信息"""
        if character_id and character_id in self._character_cache:
            builder = self._character_cache[character_id]
            return builder.get_display_info()
        return {}

    def clear_cache(self, character_id: str = None):
        """清空缓存"""
        if character_id:
            self._character_cache.pop(character_id, None)
        else:
            self._character_cache.clear()