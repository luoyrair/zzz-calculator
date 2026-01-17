import re
from typing import Dict, List, Tuple, Optional

from src.core.attribute_factory import AttrName, AttributeFactory


class JsonGearSetData:
    """驱动盘套装"""
    gear_set_id: int
    gear_set_name: str
    effect2 = None
    effect4 = None


class JsonGearSetParsedData:
    gear_set_effects: Dict


def parse_gear_set_data(data):
    attribute_patterns = [
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

    d = {}
    for k, v in data.items():
        d[k] = {}
        gear_set_data = JsonGearSetData()
        gear_set_data.gear_set_id = k
        gear_set_data.gear_set_name = v["名称"]

        # 解析2件套效果
        result = parse_attribute_value_from_text(v["2件套"], attribute_patterns)
        if result:
            attr_name, value, value_type = result
            attr = AttributeFactory.gear_set(attr_name, value, value_type)
            gear_set_data.effect2 = attr

        d[k] = gear_set_data

    gear_set_parse_data = JsonGearSetParsedData()
    gear_set_parse_data.gear_set_effects = d

    return gear_set_parse_data

def parse_attribute_value_from_text(text: str, patterns: List[Tuple[str, str, float]]) -> Optional[
    Tuple[str, float, int]]:
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