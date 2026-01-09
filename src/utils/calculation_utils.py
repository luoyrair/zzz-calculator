"""
计算相关工具函数
"""

import math
from typing import Dict, Tuple

from src.core.models import Attribute


class CalculationUtils:
    """计算工具类"""

    @staticmethod
    def get_cache_key(character, weapon=None, gear_sets=None, gear_pieces=None) -> str:
        """生成缓存键 - 包含副属性信息"""
        key_parts = []

        if character:
            key_parts.append(
                f"character_{character.id}_{character.level}_{character.breakthrough}_{character.core_passive}")

        if weapon:
            key_parts.append(f"weapon_{weapon.id}_{weapon.level}_{weapon.refinement}")

        if gear_sets:
            set_ids = sorted(gear_sets.keys())
            key_parts.append(f"sets_{'_'.join(set_ids)}")

        if gear_pieces:
            for pos in sorted(gear_pieces.keys()):
                piece = gear_pieces[pos]
                piece_key = []

                # 主属性
                if piece.main_attribute:
                    piece_key.append(f"main_{piece.main_attribute.name}_{piece.main_attribute.base_value}")

                # 副属性
                if piece.sub_attributes:
                    for sub_idx in sorted(piece.sub_attributes.keys()):
                        sub_attr = piece.sub_attributes[sub_idx]
                        if sub_attr:
                            piece_key.append(f"sub{sub_idx}_{sub_attr.name}_{sub_attr.base_value}")

                if piece_key:
                    key_parts.append(f"gear{pos}_{'_'.join(piece_key)}")

        return "|".join(key_parts)

    @staticmethod
    def evict_oldest_cache(cache_dict: Dict):
        """驱逐最旧的缓存项"""
        if cache_dict:
            # 移除第一个条目（近似LRU）
            oldest_key = next(iter(cache_dict))
            cache_dict.pop(oldest_key)

    def cache_result(self, cache_key: str, result: Dict[str, float], cache_dict: Dict):
        """缓存计算结果"""
        cache_dict[cache_key] = result.copy()

        # 限制缓存大小
        if len(cache_dict) > 100:
            self.evict_oldest_cache(cache_dict)

    @staticmethod
    def add_to_dict(target_dict: Dict[str, float], key: str, value: float):
        """将值添加到字典中，如果键已存在则累加"""
        if key in target_dict:
            target_dict[key] += value
        else:
            target_dict[key] = value

    def process_attribute(self, attr, percentage_bonuses, flat_bonuses, weapon_base_attack):
        """处理单个属性，将其分类到相应的加成集合中"""
        if attr.merge_type == 2:
            # 百分比加成
            self.add_to_dict(percentage_bonuses, attr.name, attr.base_value)
        elif attr.name == '攻击力' and attr.value_type == 1:
            # 武器基础攻击力（特殊处理）
            weapon_base_attack = attr.base_value
        else:
            # 其他固定值加成
            self.add_to_dict(flat_bonuses, attr.name, attr.base_value)

        return weapon_base_attack

    @staticmethod
    def add_attribute_to_dicts(attr: Attribute,
                               percentage_bonuses: Dict[str, float],
                               flat_bonuses: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """将属性添加到相应的字典"""
        if attr.merge_type == 2:
            if attr.name in percentage_bonuses:
                percentage_bonuses[attr.name] += attr.base_value
            else:
                percentage_bonuses[attr.name] = attr.base_value
        else:
            if attr.name in flat_bonuses:
                flat_bonuses[attr.name] += attr.base_value
            else:
                flat_bonuses[attr.name] = attr.base_value

        return percentage_bonuses, flat_bonuses

    @staticmethod
    def calculate_final_attributes(
            character_base: Dict[str, float],
            result: Dict[str, float],
            percentage_bonuses: Dict[str, float],
            flat_bonuses: Dict[str, float],
            weapon_base_attack: float = 0,
            passive_data: Dict = None,
    ) -> Dict[str, float]:
        """计算最终属性值"""

        for attr_name in set(list(character_base.keys()) +
                             list(percentage_bonuses.keys()) +
                             list(flat_bonuses.keys())):

            # 获取基础值
            base_value = character_base.get(attr_name, 0)

            # 特殊处理攻击力
            if attr_name == '攻击力':
                base_value += weapon_base_attack

            # 获取固定值加成
            flat_bonus = flat_bonuses.get(attr_name, 0)
            final_value = base_value + flat_bonus

            # 对于非百分比属性，应用百分比加成
            if attr_name not in ['穿透率', '暴击率', '暴击伤害',
                                 '物理伤害加成', '火属性伤害加成', '冰属性伤害加成',
                                 '电属性伤害加成', '以太伤害加成']:
                percentage = percentage_bonuses.get(attr_name, 0)
                value_with_percentage = math.ceil(base_value * percentage)
                final_value += value_with_percentage

            result[attr_name] = final_value

        if passive_data:
            result[passive_data["target"]] = 0
            for attr_name, ratio in passive_data["data"].items():
                result[passive_data["target"]] += result[attr_name] * ratio
            result[passive_data["target"]] = int(result[passive_data["target"]])

        return result

    @staticmethod
    def calculate_percentage_bonus(base_value: float, percentage: float) -> float:
        """计算百分比加成值"""
        return base_value * percentage

    @staticmethod
    def calculate_enhanced_value(base_value: float, growth: float, level: int) -> float:
        """计算强化后的属性值"""
        if growth < 0:  # 没有成长值
            return base_value
        return base_value + (level * growth)