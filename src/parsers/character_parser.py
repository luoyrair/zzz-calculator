from dataclasses import dataclass
from typing import Dict, Any

from src.core.attribute_factory import AttributeFactory
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
    result = {}

    for attr_name in ["生命值", "攻击力", "防御力"]:
        attr = AttributeFactory.character_stats_v0(name=attr_name, value=data.get(attr_name, 0.0),
                                                   growth=data[f"{attr_name}增长"])
        result[attr_name] = attr

    # 使用AttributeRegistry创建属性
    for attr_name in ["冲击力", "异常掌控", "异常精通", "能量自动回复", "闪能自动积蓄", "穿透值"]:
        attr = AttributeFactory.character_stats_v1(name=attr_name, value=data.get(attr_name, 0.0))
        result[attr_name] = attr

    # 处理伤害加成属性
    for attr_name in ["暴击率", "暴击伤害", "穿透率", "物理伤害加成", "火属性伤害加成", "冰属性伤害加成",
                      "电属性伤害加成", "以太伤害加成"]:
        attr = AttributeFactory.character_stats_v2(name=attr_name, value=data.get(attr_name, 0.0))
        result[attr_name] = attr

    return result


def parse_breakthrough_data(data: Dict):
    """解析Level字段"""
    breakthrough = []

    for k, v in data.items():
        level_data = JsonBreakthroughLevelData()
        level_data.level_max = v.get("等级最大值", 0)
        level_data.level_min = v.get("等级最小值", 0)

        level_attribute = {}

        for attr_name in ["生命值", "攻击力", "防御力"]:
            attr = AttributeFactory.character_breakthrough(name=attr_name, value=v.get(attr_name, 0.0))
            level_attribute[attr_name] = attr

        level_data.attribute = level_attribute
        breakthrough.append(level_data)

    return breakthrough


def parse_core_passive_data(data: Dict):
    """解析ExtraLevel字段"""
    core_passive = []

    for k, v in data.items():
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

                    attr = AttributeFactory.core_passive_v2(name=v1.get("名称", ""), value=attr_value)
                else:
                    attr = AttributeFactory.core_passive_v1(name=v1.get("名称", ""), value=attr_value)

                attrs[v1.get("名称", "")] = attr

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
                        recommend_data.gear_sub_attribute = AttributeFactory.get_gear_recommend_sub_attribute(
                            v.get("名称"), value_type=2)
                    else:
                        recommend_data.gear_sub_attribute = AttributeFactory.get_gear_recommend_sub_attribute(
                            v.get("名称"), value_type=1)
                else:
                    if isinstance(attr_format, str) and "%" in attr_format:
                        recommend_data.gear_mian_attribute[
                            int(k[:-2]) - 1] = AttributeFactory.get_gear_recommend_mian_attribute(
                            v.get("名称"), value_type=2
                        )
                    else:
                        recommend_data.gear_mian_attribute[
                            int(k[:-2]) - 1] = AttributeFactory.get_gear_recommend_mian_attribute(
                            v.get("名称"), value_type=1
                        )

    elif data == {}:
        return None

    return recommend_data

logger = get_logger("parsers.character")
