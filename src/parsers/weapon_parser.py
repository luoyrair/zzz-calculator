import re
from dataclasses import dataclass
from typing import Dict

from src.core.attribute_factory import AttributeFactory
from src.utils.attribute_utils import AttributeUtils
from src.utils.data_utils import DataUtils
from src.utils.logger import get_logger


class JsonTalentsData:
    name: str
    attrs: list


@dataclass
class JsonWeaponParsedData:
    weapon_id: int
    name: str
    rarity: int
    weapon_type: str
    attrs: any
    talents: JsonTalentsData


def parse_weapon_data(data: Dict):
    # 清洗数据
    sanitized_data = DataUtils.sanitize_json_data(data)

    _id = sanitized_data.get("id", 0)
    rarity = sanitized_data.get("稀有度", 0)
    weapon_type = next(iter(sanitized_data.get("武器类型", {}).values()), "未知")
    attrs = parse_base_data(sanitized_data)
    talents = parse_talents_data(sanitized_data["天赋"])

    result = JsonWeaponParsedData(
        weapon_id=_id,
        name=sanitized_data.get("名称", ""),
        rarity=rarity,
        weapon_type=weapon_type,
        attrs=attrs,
        talents=talents
    )

    return result

def parse_base_data(data: Dict):

    if data.get("base_attack", {}).get("名称", ""):
        attack = AttributeFactory.weapon_base_atk(data.get("base_attack", {}).get("值", 0))
    else:
        attack = None
        logger.error("解析音擎基础攻击力失败")
        logger.error("请检查使用的数据信息，请使用最新的数据信息，非项目开发人员提供的数据信息可能和您使用的计算器不适配")

    advanced_attribute = data.get("advanced_attribute", {})

    if advanced_attribute.get("名称", ""):
        attr_value = advanced_attribute.get("值", 0)
        attr_format = advanced_attribute.get("格式", "")

        # 规范化数值
        attr_value = DataUtils.normalize_value(attr_value, 'float')
        if isinstance(attr_format, str) and "%" in attr_format:
            if attr_value != 0:
                attr_value /= 10000.0
            attr = AttributeFactory.weapon_main_attr(name=advanced_attribute.get("名称", ""),
                                                     value=attr_value, value_type=2)
        else:
            attr = AttributeFactory.weapon_main_attr(name=advanced_attribute.get("名称", ""),
                                                     value=attr_value, value_type=1)
    else:
        attr = None
        logger.error("解析音擎高级属性失败")
        logger.error("请检查使用的数据信息，请使用最新的数据信息，非项目开发人员提供的数据信息可能和您使用的计算器不适配")

    return attack, attr

def parse_talents_data(data: Dict):
    talents_data = JsonTalentsData()
    attrs = []
    talent_name = None
    attribute_patterns = AttributeUtils.get_weapon_attribute_patterns()

    for k, v in data.items():
        talent_name = v.get('名称', '')
        desc = v.get('描述', '')

        if talent_name and desc:
            text = desc.lstrip()
            for pattern_info in attribute_patterns:
                pattern = re.compile(pattern_info['pattern'])
                match = pattern.match(text)
                if match:
                    value_str = match.group(1)
                    value = DataUtils.normalize_value(value_str, 'float')

                    if isinstance(pattern, str) and "%" in pattern:

                        attr = AttributeFactory.weapon_talent(name=pattern_info["attribute_id"],
                                                              value=value, value_type=2)
                    else:
                        attr = AttributeFactory.weapon_talent(name=pattern_info["attribute_id"],
                                                              value=value, value_type=1)
                    attrs.append(attr)
                    break
        else:
            logger.error("解析音擎天赋属性失败")
            logger.error("请检查使用的数据信息，请使用最新的数据信息，非项目开发人员提供的数据信息可能和您使用的计算器不适配")

    talents_data.name = talent_name
    talents_data.attrs = attrs

    return talents_data

logger = get_logger("parsers.weapon")