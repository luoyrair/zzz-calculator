import copy
import re
from dataclasses import dataclass
from typing import Dict

from src.core.attributes import AttributeName
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
    atte_list = AttributeUtils.create_weapon_base_attribute_list()

    attack = AttributeUtils.get_attribute_by_name(
        atte_list,
        data.get("base_attack", {}).get("名称", ""),
        value_type=1
    )

    if attack is not None:
        attack.base_value = data.get("base_attack", {}).get("值", 0)
        attack.source = 'weapon_base'
    else:
        logger.error("解析音擎基础攻击力失败")
        logger.error("请检查使用的数据信息，请使用最新的数据信息，非项目开发人员提供的数据信息可能和您使用的计算器不适配")

    attr = AttributeUtils.get_attribute_by_name(
        atte_list,
        data.get("advanced_attribute", {}).get("名称", ""),
        unname=AttributeName.ATK,
        unvalue_type=1
    )

    if attr is not None:
        if attr.value_type == 2:
            attr.base_value = data.get("advanced_attribute", {}).get("值", 0) / 10000.0
        else:
            attr.base_value = data.get("advanced_attribute", {}).get("值", 0)

        attr.source = 'weapon_main'
    else:
        logger.error("解析音擎高级属性失败")
        logger.error("请检查使用的数据信息，请使用最新的数据信息，非项目开发人员提供的数据信息可能和您使用的计算器不适配")

    return attack, attr


def parse_talents_data(data: Dict):
    talents_data = JsonTalentsData()
    attrs = []
    attr_list = AttributeUtils.create_weapon_talent_attribute_list()
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

                    attr = AttributeUtils.get_attribute_by_name(attr_list, pattern_info["attribute_id"])
                    if attr:
                        attr = copy.deepcopy(attr)
                        attr.base_value = value

                        if attr.name not in [AttributeName.A_M, AttributeName.E_R]:
                            attr.base_value /= 100

                        attr.source = 'weapon_talent'
                        attrs.append(attr)
                    else:
                        logger.error("解析音擎天赋属性失败")
                        logger.error("请检查使用的数据信息，请使用最新的数据信息，非项目开发人员提供的数据信息可能和您使用的计算器不适配")

                    break

    talents_data.name = talent_name
    talents_data.attrs = attrs

    return talents_data

logger = get_logger("parsers.weapon")