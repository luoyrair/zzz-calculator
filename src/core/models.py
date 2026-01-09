"""简化版核心数据模型"""

import copy
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Any


@dataclass
class Attribute:
    """统一属性类"""
    source: str
    name: str
    base_value: float
    value_type: int
    """1 = 'flat', 2 = 'percent', 0 = 'growth'"""
    merge_type: int = -1
    """1 = 'additive', 2 = 'multiplicative', -1 = None """

    growth: float = -1
    """-1 = None """

    def get_value(self, level: int) -> float:
        """根据等级获取属性值"""
        if self.value_type == 0:
            # 成长属性：基础值 + (等级-1) * 成长值
            return self.base_value + ((level - 1) * self.growth / 10000.0)
        else:
            # 固定值或百分比属性
            return self.base_value

    def get_enhance_attr(self, source: str, level: int) -> 'Attribute':
        """根据等级获取属性值"""
        value = self.base_value + (level * self.growth)

        return replace(
            self,
            source=source, name=self.name, base_value=value,
            value_type=self.value_type, merge_type=self.merge_type
        )

    def get_enhance_level(self, level: int) -> float:
        return self.base_value + (level * self.growth)


@dataclass
class Character:
    """简化版角色模型"""
    id: int
    name: str
    rarity: int
    weapon_type: str
    element_type: str
    level: int = 60
    breakthrough: int = 6
    core_passive: int = 7

    # 存储原始属性数据
    base_attributes: Dict[str, Attribute] = field(default_factory=dict)
    breakthrough_attributes: List = field(default_factory=list)
    core_passive_attributes: List = field(default_factory=list)
    passive_data: Any = None
    recommend: Any = None

    weapon_id: Optional[int] = None
    gear_set_ids: List[str] = field(default_factory=list)
    gear_pieces: Dict[int, Dict] = field(default_factory=dict)

    def get_base_attributes(self) -> Dict[str, float]:
        """
        获取角色基础属性（根据等级计算）
        只包含角色自身的属性，不包括武器
        """
        result = {}

        # 1. 基础属性（成长属性）
        for attr_name, attr in self.base_attributes.items():
            result[attr_name] = attr.get_value(self.level)

        # 2. 突破加成
        if 0 < self.breakthrough - 1 <= len(self.breakthrough_attributes):
            breakthrough_attrs = self.breakthrough_attributes[self.breakthrough - 1].attribute
            for attr_name, attr in breakthrough_attrs.items():
                if attr_name in result:
                    result[attr_name] += attr.base_value
                else:
                    result[attr_name] = attr.base_value

        # 3. 核心被动加成
        if 0 < self.core_passive - 2 <= len(self.core_passive_attributes):
            core_attrs = self.core_passive_attributes[self.core_passive - 2].attrs
            for attr_name, attr in core_attrs.items():
                if attr_name in result:
                    if attr.merge_type == 2:
                        # 百分比加成
                        result[attr_name] *= (1 + attr.base_value)
                    else:
                        # 固定值加成
                        result[attr_name] += attr.base_value
                else:
                    result[attr_name] = attr.base_value

        if self.core_passive - 1 >= 0:
            if self.weapon_type == "命破":
                result[self.passive_data.target] = 0
                for attr_name, ratio in self.passive_data.mapping[self.core_passive - 1].items():
                    result[self.passive_data.target] += result[attr_name] * ratio
                result[self.passive_data.target] = int(result[self.passive_data.target])

        result["生命值"] = int(result["生命值"])
        result["攻击力"] = int(result["攻击力"])
        result["防御力"] = int(result["防御力"])

        return result

    def get_passive_data(self):
        data = {
            "target": self.passive_data.target,
            "data": {}
        }
        for attr_name, ratio in self.passive_data.mapping[self.core_passive - 1].items():
            data["data"][attr_name] = ratio

        return data

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'rarity': self.rarity,
            'weapon_type': self.weapon_type,
            'element_type': self.element_type,
            'level': self.level,
            'breakthrough': self.breakthrough,
            'core_passive': self.core_passive,
            'base_attributes': self.base_attributes,
            'breakthrough_attributes': self.breakthrough_attributes,
            'core_passive_attributes': self.core_passive_attributes,
            'weapon_id': self.weapon_id,
            'gear_set_ids': self.gear_set_ids,
            'gear_pieces': copy.deepcopy(self.gear_pieces)
        }


@dataclass
class Weapon:
    """武器模型"""
    id: int
    name: str
    rarity: int
    weapon_type: str
    base_attack: Attribute
    advanced_attribute: Attribute
    talent_attributes: List[Attribute] = field(default_factory=list)
    level: int = 60
    refinement: int = 5
    talent: int = 1

    def __post_init__(self):
        self.data_calculation_flag = False
        self.actual_base_attack = Attribute(source="", name="攻击力", base_value=0, value_type=1, merge_type=1)
        self.actual_advanced_attribute = Attribute(source="", name="None", base_value=0, value_type=-1, merge_type=-1)

    def get_attributes(self) -> List[Attribute]:
        """获取武器所有属性"""
        attributes = []

        # 基础攻击力
        attack_attr = copy.deepcopy(self.actual_base_attack)
        attributes.append(attack_attr)

        # 高级属性（已复制并添加来源）
        main_attr = copy.deepcopy(self.actual_advanced_attribute)
        attributes.append(main_attr)

        # 天赋属性（如果有）
        if self.talent_attributes and 0 <= self.talent - 1 < len(self.talent_attributes):
            talent_attr = copy.deepcopy(self.talent_attributes[self.talent - 1])
            attributes.append(talent_attr)

        return attributes

    def set_actual_attributes(self, data_manager):
        """获取武器实际属性值（包含等级和精炼加成）"""
        if not self.data_calculation_flag:
            # 1. 基础攻击力 = 基础值 + 等级加成 + 精炼加成
            self.actual_base_attack.source = self.base_attack.source
            self.actual_base_attack.base_value = self._calculate_actual_base_attack(data_manager)

            # 2. 高级属性 = 基础值 + 精炼加成
            self.actual_advanced_attribute.source = self.advanced_attribute.source
            self.actual_advanced_attribute.name = self.advanced_attribute.name
            self.actual_advanced_attribute.base_value = self._calculate_actual_advanced_attribute(data_manager)
            self.actual_advanced_attribute.value_type = self.advanced_attribute.value_type
            self.actual_advanced_attribute.merge_type = self.advanced_attribute.merge_type

            self.data_calculation_flag = True

    def _calculate_actual_base_attack(self, data_manager) -> float:
        """计算实际基础攻击力"""
        # 基础值
        base_value = self.base_attack.base_value

        # 等级加成
        level_bonus = self._get_level_bonus(data_manager)

        # 精炼加成（基础攻击力的精炼加成）
        refinement_bonus = self._get_refinement_bonus(data_manager)

        return int(base_value * (1 + level_bonus + refinement_bonus))

    def _calculate_actual_advanced_attribute(self, data_manager) -> float:
        """计算实际高级属性值"""
        # 基础值
        base_value = self.advanced_attribute.base_value

        # 精炼加成（高级属性的精炼加成）
        refinement_bonus = self._get_advanced_refinement_bonus(data_manager)

        return base_value * (1 + refinement_bonus)

    def _get_level_bonus(self, data_manager) -> float:
        """获取等级加成值"""

        growth_data = data_manager.weapon_growth_data[str(self.rarity)]

        return growth_data[str(self.level)].get("base_attack", 0) / 10000.0

    def _get_refinement_bonus(self, data_manager) -> float:
        """获取精炼加成（基础攻击力）"""

        stars_data = data_manager.weapon_growth_data["stars"]

        return stars_data[str(self.refinement)].get("base_attack", 0) / 10000.0

    def _get_advanced_refinement_bonus(self, data_manager) -> float:
        """获取高级属性的精炼加成"""

        stars_data = data_manager.weapon_growth_data["stars"]

        return stars_data[str(self.refinement)].get("advanced_attribute", 0) / 10000.0


@dataclass
class GearSet:
    """驱动盘套装"""
    id: str
    name: str
    effect_2: Optional[Attribute] = None
    effect_4: Optional[Attribute] = None


@dataclass
class GearPiece:
    """单个驱动盘"""
    position: int  # 0-5
    main_attribute: Optional[Attribute] = None
    sub_attributes: Dict[int, Attribute] = field(default_factory=dict)  # slot -> Attribute

    def get_all_attributes(self) -> List[Attribute]:
        """获取所有属性"""
        attrs = []
        if self.main_attribute:
            attrs.append(self.main_attribute)
        attrs.extend(self.sub_attributes.values())
        return attrs