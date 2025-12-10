import json
from dataclasses import field, dataclass
from typing import Dict, List

from test.models.attributes import CharacterAttribute, AttributeValueType, AttributeType


class JsonStats:
    """JSON中处理后的Stats字段"""
    hp: CharacterAttribute
    attack: CharacterAttribute
    defence: CharacterAttribute
    impact: CharacterAttribute
    crit_rate: CharacterAttribute
    crit_dmg: CharacterAttribute
    anomaly_mastery: CharacterAttribute
    anomaly_proficiency: CharacterAttribute
    pen_ratio: CharacterAttribute
    pen: CharacterAttribute
    energy_regen: CharacterAttribute
    energy_limit: CharacterAttribute
    automatic_adrenaline_accumulation: CharacterAttribute
    max_adrenaline: CharacterAttribute


class JsonLevelData:
    """JSON中的Level字段数据"""
    level_max: int = 0
    level_min: int = 0
    hp_max: CharacterAttribute
    attack: CharacterAttribute
    defence: CharacterAttribute


class JsonExtraLevelData:
    """ExtraLevel数据"""
    max_level: int = 0
    extra: List[CharacterAttribute]


class JsonPassiveExtraProperty:
    """Passive中的ExtraProperty详细结构"""
    target: str
    value: int = 0


class JsonPassiveLevel:
    """Passive中的Level数据"""
    level: int = 0
    extra_property: Dict[str, JsonPassiveExtraProperty] = field(default_factory=dict)


@dataclass
class JsonParsedData:
    stats: JsonStats = JsonStats()
    level: Dict[int, JsonLevelData] = JsonLevelData()
    extra: Dict[int, JsonExtraLevelData] = JsonExtraLevelData()
    passive: Dict[str, Dict[str, JsonPassiveLevel]] = JsonPassiveLevel()


def create_attribute_with_growth(data, base_key, growth_key, attr_type):
    """创建带成长属性的Attribute"""
    attr = CharacterAttribute()
    attr.growing_attribute.base = data.get(base_key, 0)
    attr.growing_attribute.growth = data.get(growth_key, 0)
    attr.growing_attribute.attribute_value_type = attr_type
    return attr


def create_attribute_without_growth(data, base_key, attr_type):
    """创建不带成长属性的Attribute"""
    attr = CharacterAttribute()
    attr.base_attribute.base = data.get(base_key, 0)
    attr.base_attribute.attribute_value_type = attr_type
    return attr


def parse_stats_from_dict(data: dict) -> JsonStats:
    """从字典解析Stats字段"""
    stats = JsonStats()

    stat_mapping = {
        "hp": ["HpMax", "HpGrowth", 0],
        "attack": ["Attack", "AttackGrowth", 0],
        "defence": ["Defence", "DefenceGrowth", 0],
        "impact": ["BreakStun", 0],
        "crit_rate": ["Crit", 1],
        "crit_dmg": ["CritDamage", 1],
        "anomaly_mastery": ["ElementAbnormalPower", 0],
        "anomaly_proficiency": ["ElementMystery", 0],
        "pen_ratio": ["PenRate", 1],
        "energy_regen": ["SpRecover", 0],
        "pen": ["PenDelta", 0],
        "energy_limit": ["SpBarPoint", 0],
        "max_adrenaline": ["RpMax", 0],
        "automatic_adrenaline_accumulation": ["RpRecover", 0],
    }

    type_mapping = {
        0: AttributeValueType.NUMERIC_VALUE.value,
        1: AttributeValueType.PERCENTAGE.value
    }

    for attr_key, config in stat_mapping.items():
        if len(config) == 3:  # 有成长值
            base_key, growth_key, type_key = config
            attr = create_attribute_with_growth(data, base_key, growth_key, type_mapping[type_key])
            setattr(stats, attr_key, attr)
        elif len(config) == 2:  # 无成长值
            base_key, type_key = config
            attr = create_attribute_without_growth(data, base_key, type_mapping[type_key])
            setattr(stats, attr_key, attr)

    return stats


def load_character_data(file_path: str):
    """从JSON文件加载并解析角色数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
        return parse_character_data(raw_data)
    except Exception as e:
        print(f"加载JSON文件失败 {file_path}: {e}")


def parse_character_data(raw_data: dict) -> JsonParsedData:
    """解析完整的角色数据"""
    # 解析基础属性
    stats = parse_stats_from_dict(raw_data.get("Stats", {}))

    # 解析等级数据
    level_data = parse_level_data(raw_data.get("Level", {}))

    # 解析额外等级数据
    extra_level_data = parse_extra_level_data(raw_data.get("ExtraLevel", {}))

    # 解析被动技能数据
    passive_data = parse_passive_data(raw_data.get("Passive", {}))

    result = JsonParsedData(
        stats=stats,
        level=level_data,
        extra=extra_level_data,
        passive=passive_data,
    )
    return result


def parse_level_data(level_dict: dict) -> Dict[int, JsonLevelData]:
    """解析Level字段"""
    level_map = {}

    for level_key, level_info in level_dict.items():
        try:
            level_item = JsonLevelData()
            level_item.level_max = level_info.get("LevelMax", 0)
            level_item.level_min = level_info.get("LevelMin", 0)

            # 创建HP属性
            hp_attr = CharacterAttribute()
            hp_attr.base_attribute.base = level_info.get("HpMax", 0)
            hp_attr.base_attribute.attribute_value_type = AttributeValueType.NUMERIC_VALUE
            level_item.hp_max = hp_attr

            # 创建防御属性
            def_attr = CharacterAttribute()
            def_attr.base_attribute.base = level_info.get("Defence", 0)
            def_attr.base_attribute.attribute_value_type = AttributeValueType.NUMERIC_VALUE
            level_item.defence = def_attr

            # 创建攻击属性
            atk_attr = CharacterAttribute()
            atk_attr.base_attribute.base = level_info.get("Attack", 0)
            atk_attr.base_attribute.attribute_value_type = AttributeValueType.NUMERIC_VALUE
            level_item.attack = atk_attr

            level_map[int(level_key)] = level_item
        except Exception as e:
            print(f"解析Level字段{level_key}时出错: {e}")

    return level_map


def parse_extra_level_data(extra_dict: dict) -> Dict[int, JsonExtraLevelData]:
    """解析ExtraLevel字段"""
    extra_map = {}
    attribute_type_map = get_attribute_type_map()

    for level_key, level_info in extra_dict.items():
        extra_attrs = []

        for extra_id, extra_data in level_info.get("Extra", {}).items():
            base_extra_id = int(extra_id) // 100
            attr = CharacterAttribute()
            attr.attribute_type = attribute_type_map[base_extra_id].value
            attr.base_attribute.base = extra_data.get("Value", 0)
            attr.base_attribute.attribute_value_type = extra_data.get("Format", 0)
            extra_attrs.append(attr)

        extra_item = JsonExtraLevelData()
        extra_item.max_level = level_info.get("MaxLevel", 0)
        extra_item.extra = extra_attrs
        extra_map[int(level_key)] = extra_item

    return extra_map


def parse_passive_data(passive_dict: dict) -> Dict[str, Dict[str, JsonPassiveLevel]]:
    """解析Passive字段"""
    passive_levels = {}
    attribute_type_map = get_attribute_type_map()

    if "Level" in passive_dict:
        for level_key, level_info in passive_dict["Level"].items():
            extra_props = {}

            if "ExtraProperty" in level_info and level_info["ExtraProperty"]:
                for prop_id, prop_data in level_info["ExtraProperty"].items():
                    extra_prop = JsonPassiveExtraProperty()
                    extra_prop.target = attribute_type_map[prop_data.get("Target", 0)].value
                    extra_prop.value = prop_data.get("Value", 0)
                    extra_props[attribute_type_map[int(prop_id)].value] = extra_prop

            passive_level = JsonPassiveLevel()
            passive_level.level = level_info.get("Level", 0)
            passive_level.extra_property = extra_props

            passive_levels[level_key] = passive_level

    return {"Level": passive_levels}


def get_attribute_type_map() -> Dict[int, AttributeType]:
    """获取属性类型映射"""
    return {
        111: AttributeType.HP,
        121: AttributeType.ATK,
        122: AttributeType.IMPACT,
        123: AttributeType.SHEER_FORCE,
        131: AttributeType.DEF,
        201: AttributeType.CRIT_RATE,
        211: AttributeType.CRIT_DMG,
        231: AttributeType.PEN_RATIO,
        232: AttributeType.PEN,
        305: AttributeType.ENERGY_REGEN,
        312: AttributeType.ANOMALY_PROFICIENCY,
        314: AttributeType.ANOMALY_MASTERY,
    }


if __name__ == "__main__":
    character_data = load_character_data("../../data/characters/1091.json")
    if character_data:
        print(character_data.extra[6].extra[0].base_attribute.base)