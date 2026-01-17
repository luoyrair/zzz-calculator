"""
计算相关工具函数
"""

import math
from typing import Dict, Tuple

from src.core.models import Attribute


class CalculationUtils:
    """计算工具类"""

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
            if percentage_bonuses.get(attr_name, 0) > 0:
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
