from typing import Dict

from src.core.attribute_factory import AttributeFactory
from src.utils.attribute_utils import AttributeUtils


class JsonGearSetData:
    """驱动盘套装"""
    gear_set_id: int
    gear_set_name: str
    effect2 = None
    effect4 = None


class JsonGearSetParsedData:
    gear_set_effects: Dict


def parse_gear_set_data(data):
    attribute_patterns = AttributeUtils.get_gear_set_attribute_patterns()

    d = {}
    for k, v in data.items():
        d[k] = {}
        gear_set_data = JsonGearSetData()
        gear_set_data.gear_set_id = k
        gear_set_data.gear_set_name = v["名称"]

        # 解析2件套效果
        result = AttributeUtils.parse_attribute_value_from_text(v["2件套"], attribute_patterns)
        if result:
            attr_name, value, value_type = result
            attr = AttributeFactory.gear_set(attr_name, value, value_type)
            gear_set_data.effect2 = attr

        d[k] = gear_set_data

    gear_set_parse_data = JsonGearSetParsedData()
    gear_set_parse_data.gear_set_effects = d

    return gear_set_parse_data