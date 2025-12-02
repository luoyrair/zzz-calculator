# src/services/character_service.py
"""角色业务服务 - 协调各层工作"""
from typing import Optional, Dict, Any

from src.core.character_builder import CharacterBuilder
from src.core.character_models import BaseCharacterStats
from src.data.json_models import JsonCharacterData
from src.data.schema_converter import SchemaConverter


class CharacterService:
    """角色服务 - 高层协调"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.schema_converter = SchemaConverter(config_manager)
        self._current_builder: Optional[CharacterBuilder] = None
        self._character_cache: Dict[str, CharacterBuilder] = {}

    def load_character_by_id(self, character_id: str) -> bool:
        """加载角色"""
        try:
            # 检查缓存
            if character_id in self._character_cache:
                self._current_builder = self._character_cache[character_id]
                print(f"从缓存加载角色: {character_id}")
                return True

            # 构建文件路径
            file_path = self.config_manager.file.get_character_file_path(character_id)
            if not file_path.exists():
                print(f"角色文件不存在: {file_path}")
                return False

            print(f"加载角色文件: {file_path}")

            # 1. 加载JSON数据
            json_data = JsonCharacterData.from_json_file(str(file_path))

            if json_data.Id == 0:
                print(f"JSON解析失败: {character_id}")
                return False

            print(f"JSON数据加载成功:")
            print(f"  ID: {json_data.Id}")
            print(f"  名称: {json_data.Name}")
            print(f"  攻击力: {json_data.Stats.Attack}")
            print(f"  攻击成长: {json_data.Stats.AttackGrowth}")

            # 2. 转换为标准架构
            schema = self.schema_converter.convert(json_data)

            print(f"架构转换成功:")
            print(f"  基础攻击力: {schema.growth_curve.base_atk}")
            print(f"  攻击成长率: {schema.growth_curve.atk_growth}")

            # 3. 创建构建器
            builder = CharacterBuilder(schema)

            # 4. 缓存并设置当前
            self._character_cache[character_id] = builder
            self._current_builder = builder

            print(f"角色加载完成: {character_id}")
            return True

        except Exception as e:
            print(f"加载角色失败: {character_id}, 错误: {e}")
            import traceback
            traceback.print_exc()
            return False

    def calculate_character_stats(self, level: int, breakthrough_level: int,
                                  core_passive_level: int) -> Optional[BaseCharacterStats]:
        """计算角色属性"""
        if not self._current_builder:
            print("没有可用的角色构建器")
            return None

        try:
            print(f"计算属性: 等级={level}, 突破={breakthrough_level}, 核心技={core_passive_level}")
            stats = self._current_builder.build_base_stats(
                level, breakthrough_level, core_passive_level
            )

            print(f"计算结果:")
            print(f"  HP: {stats.HP}")
            print(f"  ATK: {stats.ATK}")
            print(f"  DEF: {stats.DEF}")
            print(f"  暴击率: {stats.CRIT_Rate}")
            print(f"  暴击伤害: {stats.CRIT_DMG}")

            return stats
        except Exception as e:
            print(f"计算属性失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_character_display_info(self) -> Dict[str, Any]:
        """获取角色显示信息"""
        if not self._current_builder:
            return {}
        return self._current_builder.get_display_info()

    def clear_cache(self, character_id: str = None):
        """清空缓存"""
        if character_id:
            self._character_cache.pop(character_id, None)
            if self._current_builder and self._current_builder.schema.character_id == int(character_id):
                self._current_builder = None
        else:
            self._character_cache.clear()
            self._current_builder = None