# src/services/weapon.py
"""音擎业务服务"""
from typing import Optional, Dict, Any, List

from src.core.models.weapon import WeaponSchema
from src.data.converter.weapon import WeaponSchemaConverter
from src.data.models.weapon import JsonWeaponData


class WeaponCalculator:
    """音擎计算器"""

    @staticmethod
    def calculate_level_star(level: int) -> int:
        if level <= 9:
            return 0
        elif level <= 19:
            return 1
        elif level <= 29:
            return 2
        elif level <= 39:
            return 3
        elif level <= 49:
            return 4
        elif level <= 60:
            return 5
        else:
            return 0

    @staticmethod
    def calculate_weapon_stats(schema: WeaponSchema,
                               level: int,
                               stars: Optional[int] = None) -> Dict[str, float]:
        """计算音擎属性"""
        import math

        if stars is None:
            stars = WeaponCalculator.calculate_level_star(level)

        # 基础属性（固定攻击力）
        base_value = schema.base_property.base_value
        level_data = schema.level_data.get(level)
        star_data = schema.star_data.get(stars)

        if level_data and star_data:
            base_atk = base_value + (base_value * level_data.rate / 10000) + (base_value * star_data.star_rate / 10000)
            base_atk = math.floor(base_atk)
        else:
            base_atk = base_value

        # 随机属性
        rand_value = schema.rand_property.base_value
        if star_data:
            rand_value = rand_value + (rand_value * star_data.rand_rate / 10000)
            if schema.rand_property.is_percentage:
                rand_value = round(rand_value) / 100
            else:
                rand_value = math.floor(rand_value)

        # 构建结果
        result = {
            "ATK_FIXED": base_atk
        }

        # 根据随机属性类型添加
        rand_name = schema.rand_property.name
        if rand_name == "暴击率":
            result["CRIT_Rate"] = rand_value
        elif rand_name == "暴击伤害":
            result["CRIT_DMG"] = rand_value
        elif rand_name == "异常精通":
            result["Anomaly_Proficiency"] = rand_value
        elif rand_name == "攻击力":
            result["ATK_PERCENT"] = rand_value

        return result


class WeaponService:
    """音擎服务"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self._weapon_cache: Dict[int, WeaponSchema] = {}

    def load_weapon_by_id(self, weapon_id: int) -> Optional[WeaponSchema]:
        """加载音擎数据"""
        if weapon_id in self._weapon_cache:
            return self._weapon_cache[weapon_id]

        file_path = self.config_manager.file.get_weapon_file_path(str(weapon_id))
        if not file_path.exists():
            print(f"音擎文件不存在: {file_path}")
            return None

        try:
            json_data = JsonWeaponData.from_json_file(str(file_path))
            if json_data.Id == 0:
                print(f"音擎数据加载失败: {weapon_id}")
                return None

            schema = WeaponSchemaConverter.convert(json_data)
            self._weapon_cache[weapon_id] = schema
            return schema

        except Exception as e:
            print(f"加载音擎数据异常 {weapon_id}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_weapon_attributes_for_character(self, weapon_id: int,
                                            level: int,
                                            stars: Optional[int] = None) -> Dict[str, float]:
        """获取音擎对角色属性的加成"""
        schema = self.load_weapon_by_id(weapon_id)
        if not schema:
            return {}

        try:
            stats = WeaponCalculator.calculate_weapon_stats(schema, level, stars)
            print(f"[WeaponService] 音擎属性: {stats}")
            return stats

        except Exception as e:
            print(f"计算音擎属性异常 {weapon_id}: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def list_available_weapons(self) -> List[Dict[str, Any]]:
        """列出所有可用的音擎"""
        weapons_dir = self.config_manager.file.weapons_dir
        weapons = []

        for file_path in weapons_dir.glob("*.json"):
            try:
                weapon_id = int(file_path.stem)
                schema = self.load_weapon_by_id(weapon_id)
                if schema:
                    weapons.append({
                        "id": schema.weapon_id,
                        "name": schema.name,
                        "rarity": schema.rarity,
                        "weapon_type": schema.weapon_type
                    })
            except Exception:
                continue

        return sorted(weapons, key=lambda x: x["id"])

    def clear_cache(self, weapon_id: Optional[int] = None):
        """清空缓存"""
        if weapon_id:
            self._weapon_cache.pop(weapon_id, None)
        else:
            self._weapon_cache.clear()