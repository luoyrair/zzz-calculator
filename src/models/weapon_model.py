"""音擎数据模型"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from src.models.attributes import AttributeType
import math

from src.models.character_attributes import CharacterAttributesModel


@dataclass
class WeaponLevelData:
    """音擎等级数据"""
    level: int
    base_atk_rate: float  # 基础攻击力成长率 (万分比)
    random_attr_rate: float  # 随机属性成长率 (万分比)


@dataclass
class WeaponStarData:
    """音擎突破数据"""
    star: int
    base_atk_star_rate: float  # 基础攻击力突破加成率 (万分比)
    random_attr_star_rate: float  # 随机属性突破加成率 (万分比)


@dataclass
class WeaponTalent:
    """音擎天赋"""
    star: int
    name: str
    description: str


@dataclass
class WeaponSchema:
    """音擎数据架构"""
    weapon_id: int
    name: str
    rarity: int  # 稀有度: 1-5

    # 基础属性（总是攻击力）
    base_attr_type: AttributeType = AttributeType.ATK
    base_attr_value: float = 0.0  # 基础攻击力数值

    # 随机属性
    random_attr_type: AttributeType = AttributeType.ATK
    random_attr_value: float = 0.0  # 随机属性基础值
    random_attr_is_percentage: bool = False  # 是否为百分比

    # 等级数据
    level_data: Dict[int, WeaponLevelData] = field(default_factory=dict)

    # 突破数据
    star_data: Dict[int, WeaponStarData] = field(default_factory=dict)

    # 天赋
    talents: Dict[int, WeaponTalent] = field(default_factory=dict)

    def calculate_final_values(self, level: int, star: int = None) -> tuple[float, float]:
        """计算最终属性值"""
        if star is None:
            star = _get_star_by_level(level)

            # 找到对应的等级数据
        level_info = self.level_data.get(level)
        star_info = self.star_data.get(star)

        if not level_info:
            return self.base_attr_value, self.random_attr_value

        # 计算基础攻击力：基础值 + 等级加成 + 星级加成
        base_atk = self.base_attr_value

        # 等级加成（基于基础值的加成）
        if level_info.base_atk_rate != 0:
            level_bonus = self.base_attr_value * (level_info.base_atk_rate / 10000.0)
            base_atk += level_bonus

        # 星级加成（也是基于基础值的加成）
        if star_info and star_info.base_atk_star_rate != 0:
            star_bonus = self.base_attr_value * (star_info.base_atk_star_rate / 10000.0)
            base_atk += star_bonus

        # 计算随机属性
        random_attr = self.random_attr_value

        if star_info and star_info.random_attr_star_rate != 0:
            random_attr *= (1 + star_info.random_attr_star_rate / 10000.0)

        # 数值取整
        base_atk = math.floor(base_atk)
        if not self.random_attr_is_percentage:
            random_attr = math.floor(random_attr)

        return base_atk, random_attr

    def _get_level_info(self, level: int) -> Optional[WeaponLevelData]:
        """获取等级信息"""
        # 找到小于等于目标等级的最大等级
        valid_levels = [lvl for lvl in self.level_data.keys() if lvl <= level]
        if not valid_levels:
            return None

        max_level = max(valid_levels)
        return self.level_data.get(max_level)

    def apply_to_character(self, character_attrs: CharacterAttributesModel,
                           level: int, star: int = None) -> None:
        """将音擎属性应用到角色属性上"""
        base_atk, random_attr = self.calculate_final_values(level, star)

        # 添加基础攻击力
        character_attrs.attack += base_atk

        # 根据随机属性类型添加到对应属性
        current_value = getattr(character_attrs, self.random_attr_type.value, 0.0)
        new_value = current_value + random_attr
        setattr(character_attrs, self.random_attr_type.value, new_value)

    def get_stats_dict(self, level: int, star: int = None) -> Dict[str, float]:
        """获取音擎属性字典"""
        base_atk, random_attr = self.calculate_final_values(level, star)

        stats = {
            "base_attack": base_atk,
        }

        # 添加随机属性
        attr_key = self.random_attr_type.value
        if self.random_attr_is_percentage:
            attr_key += "_percent"
        stats[attr_key] = random_attr

        return stats

def _get_star_by_level(level: int) -> int:
    """根据等级确定星级"""
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
        return 5