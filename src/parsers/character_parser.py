import copy
from dataclasses import dataclass
from typing import Dict, Any

from src.utils.attribute_utils import AttributeUtils
from src.utils.data_utils import DataUtils
from src.utils.logger import get_logger


class JsonBreakthroughLevelData:
    level_max: int = 0
    level_min: int = 0
    attribute: Dict = None


class JsonCorePassiveData:
    level: int = 0
    attrs: Dict = None


class JsonPassiveData:
    target: str = None
    mapping: list[dict] = None


class JsonRecommendGearSetData:
    Slot4 = None
    Slot2 = None


@dataclass
class JsonRecommendData:
    gear_set:JsonRecommendGearSetData = None
    gear_mian_attribute: Dict[int, Any] = None
    gear_sub_attribute = None

    def __post_init__(self):
        self.gear_mian_attribute = {}


@dataclass
class JsonCharacterParsedData:
    character_id: int
    name: str
    code_name: str
    rarity: int
    weapon_type: str
    element_type: str
    stats: Dict = None
    breakthrough: list[JsonBreakthroughLevelData] = None
    core_passive: list[JsonCorePassiveData] = None
    passive: JsonPassiveData = None
    recommend : JsonRecommendData = None


def parse_character_data(data: Dict):
    _id = data.get("id", 0)
    rarity = data.get("稀有度", 0)
    weapon_type = next(iter(data.get("武器类型", {}).values()), "未知")
    element_type = next(iter(data.get("元素类型", {}).values()), "未知")

    # 清洗数据
    sanitized_data = DataUtils.sanitize_json_data(data)

    stats = parse_stats_from_dict(sanitized_data.get("统计", {}))
    breakthrough = parse_breakthrough_data(sanitized_data.get("等级", {}))
    core_passive = parse_core_passive_data(sanitized_data.get("核心技等级", {}))
    passive = parse_passive_data(sanitized_data.get("核心被动", {}))
    recommend = parse_recommend_data(sanitized_data.get("推荐", {}))

    result = JsonCharacterParsedData(
        character_id=_id,
        name=sanitized_data.get("名称", ""),
        code_name=sanitized_data.get("代号", ""),
        rarity=rarity,
        weapon_type=weapon_type,
        element_type=element_type,
        stats=stats,
        breakthrough=breakthrough,
        core_passive=core_passive,
        passive=passive,
        recommend=recommend
    )

    return result


def parse_stats_from_dict(data: Dict):
    """从字典解析Stats字段"""
    attr_list = AttributeUtils.create_character_base_attribute_list()

    attr_list[0].base_value = data.get(attr_list[0].name, 0)
    attr_list[0].growth = data.get('生命值增长', 0)
    attr_list[0].source = 'stats'
    attr_list[1].base_value = data.get(attr_list[1].name, 0)
    attr_list[1].growth = data.get('攻击力增长', 0)
    attr_list[1].source = 'stats'
    attr_list[2].base_value = data.get(attr_list[2].name, 0)
    attr_list[2].growth = data.get('防御力增长', 0)
    attr_list[2].source = 'stats'

    attr_list[3].base_value = data.get(attr_list[3].name, 0)
    attr_list[3].source = 'stats'
    attr_list[4].base_value = data.get(attr_list[4].name, 0)
    attr_list[4].source = 'stats'
    attr_list[5].base_value = data.get(attr_list[5].name, 0)
    attr_list[5].source = 'stats'
    attr_list[6].base_value = data.get(attr_list[6].name, 0) / 100.0
    attr_list[6].source = 'stats'
    attr_list[7].base_value = data.get(attr_list[7].name, 0) / 100.0
    attr_list[7].source = 'stats'

    attr_list[8].base_value = data.get(attr_list[8].name, 0) / 10000.0
    attr_list[8].source = 'stats'
    attr_list[9].base_value = data.get(attr_list[9].name, 0) / 10000.0
    attr_list[9].source = 'stats'
    attr_list[10].base_value = float(data.get(attr_list[10].name, 0))
    attr_list[10].source = 'stats'

    attr_list[11].base_value = data.get(attr_list[11].name, 0)
    attr_list[11].source = 'stats'

    stats = {
        attr_list[0].name: attr_list[0],
        attr_list[1].name: attr_list[1],
        attr_list[2].name: attr_list[2],
        attr_list[3].name: attr_list[3],
        attr_list[4].name: attr_list[4],
        attr_list[5].name: attr_list[5],
        attr_list[6].name: attr_list[6],
        attr_list[7].name: attr_list[7],
        attr_list[8].name: attr_list[8],
        attr_list[9].name: attr_list[9],
        attr_list[10].name: attr_list[10],
        attr_list[11].name: attr_list[11],
        attr_list[12].name: attr_list[12],
        attr_list[13].name: attr_list[13],
        attr_list[14].name: attr_list[14],
        attr_list[15].name: attr_list[15],
        attr_list[16].name: attr_list[16],
    }

    return stats


def parse_breakthrough_data(data: Dict):
    """解析Level字段"""
    breakthrough = []
    attr_list = AttributeUtils.create_breakthrough_attribute_list()

    for k, v in data.items():
        level_data = JsonBreakthroughLevelData()
        level_data.level_max = v.get("等级最大值", 0)
        level_data.level_min = v.get("等级最小值", 0)
        attr_list[0].base_value = v.get(attr_list[0].name, 0)
        attr_list[0].source = 'breakthrough'
        attr_list[1].base_value = v.get(attr_list[1].name, 0)
        attr_list[1].source = 'breakthrough'
        attr_list[2].base_value = v.get(attr_list[2].name, 0)
        attr_list[2].source = 'breakthrough'
        level_attribute = {
            attr_list[0].name: copy.deepcopy(attr_list[0]),
            attr_list[1].name: copy.deepcopy(attr_list[1]),
            attr_list[2].name: copy.deepcopy(attr_list[2]),
        }
        level_data.attribute = level_attribute
        breakthrough.append(level_data)

    return breakthrough


def parse_core_passive_data(data: Dict):
    """解析ExtraLevel字段"""
    core_passive = []

    for k, v in data.items():
        attr_list = AttributeUtils.create_core_passive_attribute_list()
        attrs = {}
        core_passive_data = JsonCorePassiveData()
        core_passive_data.level = v.get("最高等级", 0)

        for k1, v1 in v.get("附加", {}).items():
            try:
                attr_value = v1.get("值", 0)
                attr_format = v1.get("格式", 0)

                # 规范化数值
                attr_value = DataUtils.normalize_value(attr_value, 'float')

                # 如果格式是百分比格式字符串，需要转换数值
                if isinstance(attr_format, str) and "%" in attr_format:
                    if attr_value != 0:
                        attr_value /= 10000.0

                    attr = AttributeUtils.get_attribute_by_name(attr_list, v1.get("名称", ""), merge_type=2)
                    attr.base_value = attr_value
                else:
                    attr = AttributeUtils.get_attribute_by_name(attr_list, v1.get("名称", ""), unmerge_type=2)
                    attr.base_value = attr_value

                attr.source = 'core_passive'
                attrs[attr.name] = attr

            except Exception as e:
                logger.error(f"解析额外属性 {k} {v1.get('名称', '')} 失败: {str(e)}")

        core_passive_data.attrs = attrs
        core_passive.append(core_passive_data)

    return core_passive


def parse_passive_data(data: Dict):
    """解析Passive字段"""
    passive_data = JsonPassiveData()
    mapping = []

    for k, v in data["等级"].items():
        if len(v["附加属性"]) != 0:
            d = {}
            for k1, v1 in v["附加属性"].items():
                if not passive_data.target or passive_data.target != v1.get("目标", ""):
                    passive_data.target = v1.get("目标", "")
                d[k1] = v1.get("值", 0) / 10000.0
            mapping.append(d)
        else:
            return None

    passive_data.mapping = mapping
    return passive_data

def parse_recommend_data(data: Dict):
    main_attr_list = AttributeUtils.create_character_recommend_attribute_list()
    sub_attr_list = AttributeUtils.create_gear_recommend_sub_attribute_list()
    recommend_data = JsonRecommendData()

    if data != {}:
        gear_set = JsonRecommendGearSetData()
        gear_set.Slot4 = data["4件套"]
        gear_set.Slot2 = data["2件套"]
        recommend_data.gear_set = gear_set
        for k, v in data.items():
            if isinstance(v, dict):
                attr_format = v.get("格式", 0)
                if k == "*号盘副属性":
                    if isinstance(attr_format, str) and "%" in attr_format:
                        recommend_data.gear_sub_attribute = AttributeUtils.get_attribute_by_name(sub_attr_list,
                                                                                                 v.get("名称"),
                                                                                                 value_type=2)
                    else:
                        recommend_data.gear_sub_attribute = AttributeUtils.get_attribute_by_name(sub_attr_list,
                                                                                                 v.get("名称"),
                                                                                                 unvalue_type=2)
                else:
                    if isinstance(attr_format, str) and "%" in attr_format:
                        recommend_data.gear_mian_attribute[int(k[:-2]) - 1] = AttributeUtils.get_attribute_by_name(
                            main_attr_list, v.get("名称"), value_type=2)
                    else:
                        recommend_data.gear_mian_attribute[int(k[:-2]) - 1] = AttributeUtils.get_attribute_by_name(
                            main_attr_list, v.get("名称"), unvalue_type=2)

    elif data == {}:
        return None

    return recommend_data

logger = get_logger("parsers.character")