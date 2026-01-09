"""
属性相关工具函数
"""

import copy
import re
from typing import List, Dict, Optional, Tuple, Any

from src.core.attributes import (
    AttributeName,
    character_attribute, breakthrough_attribute, core_passive_attribute,
    weapon_base_attribute, weapon_talents_attribute,
    gear_set_effect_attribute,
    character_recommend_attribute, gear_recommend_sub_attribute,
)


class AttributeUtils:
    """属性工具类"""

    @staticmethod
    def get_weapon_attribute_patterns() -> List[Dict[str, Any]]:
        """获取武器属性正则模式"""
        return [
            {'pattern': r'^生命值上限提升(\d+(?:\.\d+)?)%', 'attribute_id': AttributeName.HP},
            {'pattern': r'^攻击力提升(\d+(?:\.\d+)?)%', 'attribute_id': AttributeName.ATK},
            {'pattern': r'^电属性伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttributeName.EL_D_B},
            {'pattern': r'^冰属性伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttributeName.IC_D_B},
            {'pattern': r'^装备者造成的火属性伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttributeName.FI_D_B},
            {'pattern': r'^物理伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttributeName.PH_D_B},
            {'pattern': r'^暴击伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttributeName.C_D},
            {'pattern': r'^暴击率提升(\d+(?:\.\d+)?)%', 'attribute_id': AttributeName.C_R},
            {'pattern': r'^装备者的能量自动回复提升(\d+(?:\.\d+)?)点/秒', 'attribute_id': AttributeName.E_R},
            {'pattern': r'^装备者的\[异常掌控\]提升(\d+(?:\.\d+)?)点', 'attribute_id': AttributeName.A_M}
        ]

    @staticmethod
    def get_gear_set_attribute_patterns() -> List[Tuple[str, str, float]]:
        """获取驱动盘套装属性正则模式"""
        return [
            (r'攻击力\+(\d+)%', AttributeName.ATK, 0.01),
            (r'生命值\+(\d+)%', AttributeName.HP, 0.01),
            (r'防御力\+(\d+)%', AttributeName.DEF, 0.01),
            (r'暴击率\+(\d+)%', AttributeName.C_R, 0.01),
            (r'暴击伤害\+(\d+)%', AttributeName.C_D, 0.01),
            (r'物理伤害\+(\d+)%', AttributeName.PH_D_B, 0.01),
            (r'火属性伤害\+(\d+)%', AttributeName.FI_D_B, 0.01),
            (r'冰属性伤害\+(\d+)%', AttributeName.IC_D_B, 0.01),
            (r'电属性伤害\+(\d+)%', AttributeName.EL_D_B, 0.01),
            (r'以太伤害\+(\d+)%', AttributeName.ET_D_B, 0.01),
            (r'异常精通\+(\d+)点', AttributeName.A_P, 1),
            (r'异常掌控\+(\d+)%', AttributeName.A_M, 0.01),
            (r'穿透率\+(\d+)%', AttributeName.PEN_R, 0.01),
            (r'能量自动回复\+(\d+)%', AttributeName.E_R, 0.01),
            (r'冲击力\+(\d+)%', AttributeName.IMP, 0.01),
        ]

    @staticmethod
    def get_attribute_by_name(
            attr_list: List,
            name: str,
            unname: Optional[str] = None,
            value_type: Optional[int] = None,
            unvalue_type: Optional[int] = None,
            merge_type: Optional[int] = None,
            unmerge_type: Optional[int] = None
    ):
        """获取属性对象（替代原有的get_attr函数）"""
        for attr in attr_list:
            if attr.name == name:
                if unmerge_type and attr.merge_type == unmerge_type:
                    continue
                if merge_type and attr.merge_type == merge_type:
                    return attr
                if unvalue_type and attr.value_type == unvalue_type:
                    if unname and attr.name == unname:
                        continue
                    else:
                        return attr
                if value_type and attr.value_type == value_type:
                    return attr
                return attr
        return None

    @staticmethod
    def create_character_base_attribute_list() -> List:
        """创建角色基础属性列表的深拷贝"""
        return copy.deepcopy(character_attribute)

    @staticmethod
    def create_breakthrough_attribute_list() -> List:
        """创建突破属性列表的深拷贝"""
        return copy.deepcopy(breakthrough_attribute)

    @staticmethod
    def create_core_passive_attribute_list() -> List:
        """创建核心被动属性列表的深拷贝"""
        return copy.deepcopy(core_passive_attribute)

    @staticmethod
    def create_character_recommend_attribute_list() -> List:
        """创建角色推荐数据属性列表的深拷贝"""
        return copy.deepcopy(character_recommend_attribute)

    @staticmethod
    def create_weapon_base_attribute_list() -> List:
        """创建武器基础属性列表的深拷贝"""
        return copy.deepcopy(weapon_base_attribute)

    @staticmethod
    def create_weapon_talent_attribute_list() -> List:
        """创建武器天赋属性列表的深拷贝"""
        return copy.deepcopy(weapon_talents_attribute)

    @staticmethod
    def create_gear_set_effect_attribute_list() -> List:
        """创建驱动盘套装属性列表的深拷贝"""
        return copy.deepcopy(gear_set_effect_attribute)

    @staticmethod
    def create_gear_recommend_sub_attribute_list() -> List:
        """创建驱动盘推荐副属性列表的深拷贝"""
        return copy.deepcopy(gear_recommend_sub_attribute)

    @staticmethod
    def parse_attribute_value_from_text(text: str, patterns: List[Tuple[str, str, float]]) -> Optional[
        Tuple[str, float]]:
        """从文本中解析属性值和类型"""
        for pattern, attr_name, factor in patterns:
            match = re.match(pattern, text)
            if match:
                try:
                    value = float(match.group(1)) * factor
                    return attr_name, value
                except (ValueError, AttributeError):
                    continue
        return None