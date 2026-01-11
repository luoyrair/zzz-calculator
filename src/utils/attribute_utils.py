"""
属性相关工具函数
"""
import re
from typing import List, Dict, Optional, Tuple, Any

from src.core.attribute_factory import AttrName


class AttributeUtils:
    """属性工具类"""

    @staticmethod
    def get_weapon_attribute_patterns() -> List[Dict[str, Any]]:
        """获取武器属性正则模式"""
        return [
            {'pattern': r'^生命值上限提升(\d+(?:\.\d+)?)%', 'attribute_id': AttrName.HP},
            {'pattern': r'^攻击力提升(\d+(?:\.\d+)?)%', 'attribute_id': AttrName.ATK},
            {'pattern': r'^电属性伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttrName.EL_D_B},
            {'pattern': r'^冰属性伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttrName.IC_D_B},
            {'pattern': r'^装备者造成的火属性伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttrName.FI_D_B},
            {'pattern': r'^物理伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttrName.PH_D_B},
            {'pattern': r'^暴击伤害提升(\d+(?:\.\d+)?)%', 'attribute_id': AttrName.C_D},
            {'pattern': r'^暴击率提升(\d+(?:\.\d+)?)%', 'attribute_id': AttrName.C_R},
            {'pattern': r'^装备者的能量自动回复提升(\d+(?:\.\d+)?)点/秒', 'attribute_id': AttrName.E_R},
            {'pattern': r'^装备者的\[异常掌控\]提升(\d+(?:\.\d+)?)点', 'attribute_id': AttrName.A_M}
        ]

    @staticmethod
    def get_gear_set_attribute_patterns() -> List[Tuple[str, str, float]]:
        """获取驱动盘套装属性正则模式"""
        return [
            (r'攻击力\+(\d+)%', AttrName.ATK, 0.01),
            (r'生命值\+(\d+)%', AttrName.HP, 0.01),
            (r'防御力\+(\d+)%', AttrName.DEF, 0.01),
            (r'暴击率\+(\d+)%', AttrName.C_R, 0.01),
            (r'暴击伤害\+(\d+)%', AttrName.C_D, 0.01),
            (r'物理伤害\+(\d+)%', AttrName.PH_D_B, 0.01),
            (r'火属性伤害\+(\d+)%', AttrName.FI_D_B, 0.01),
            (r'冰属性伤害\+(\d+)%', AttrName.IC_D_B, 0.01),
            (r'电属性伤害\+(\d+)%', AttrName.EL_D_B, 0.01),
            (r'以太伤害\+(\d+)%', AttrName.ET_D_B, 0.01),
            (r'异常精通\+(\d+)点', AttrName.A_P, 1),
            (r'异常掌控\+(\d+)%', AttrName.A_M, 0.01),
            (r'穿透率\+(\d+)%', AttrName.PEN_R, 0.01),
            (r'能量自动回复\+(\d+)%', AttrName.E_R, 0.01),
            (r'冲击力\+(\d+)%', AttrName.IMP, 0.01),
        ]

    @staticmethod
    def parse_attribute_value_from_text(text: str, patterns: List[Tuple[str, str, float]]) -> Optional[Tuple[str, float, int]]:
        """从文本中解析属性值和类型"""
        for pattern, attr_name, factor in patterns:
            match = re.match(pattern, text)
            if match:
                try:
                    if isinstance(pattern, str) and "%" in pattern:
                        value_type = 2
                    else:
                        value_type = 1
                    value = float(match.group(1)) * factor
                    return attr_name, value, value_type
                except (ValueError, AttributeError):
                    continue
        return None