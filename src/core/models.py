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
    """角色模型"""
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
    promotions_attributes: List = field(default_factory=list)
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
        if 0 < self.breakthrough - 1 <= len(self.promotions_attributes):
            promotions_attrs = self.promotions_attributes[self.breakthrough - 1]["attribute"]
            for attr_name, attr in promotions_attrs.items():
                if attr_name in result:
                    result[attr_name] += attr.base_value
                else:
                    result[attr_name] = attr.base_value

        # 3. 核心被动加成
        if 0 < self.core_passive - 2 <= len(self.core_passive_attributes):
            core_attrs = self.core_passive_attributes[self.core_passive - 2]["attrs"]
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
                result[self.passive_data["target"]] = 0
                for (attr_name, ratio) in self.passive_data["mapping"]:
                    result[self.passive_data["target"]] += result[attr_name] * ratio
                result[self.passive_data["target"]] = int(result[self.passive_data["target"]])

        result["生命值"] = int(result["生命值"])
        result["攻击力"] = int(result["攻击力"])
        result["防御力"] = int(result["防御力"])

        return result

    def get_passive_data(self):
        data = {
            "target": self.passive_data["target"],
            "data": {}
        }
        for (attr_name, ratio) in self.passive_data["mapping"]:
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
            'promotions_attributes': self.promotions_attributes,
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

        # 导入享元（延迟导入避免循环依赖）
        from src.core.weapon_growth import weapon_growth
        self._growth = weapon_growth

    def _ensure_growth_loaded(self):
        """确保成长数据已加载"""
        if not self._growth.is_loaded():
            raise RuntimeError(
                f"武器成长数据未加载，无法计算武器 {self.name} 的实际属性"
            )

    def _calculate_actual_attributes(self):
        """计算实际属性值（内部方法）"""
        self._ensure_growth_loaded()

        # 1. 计算实际基础攻击力
        base_value = self.base_attack.base_value
        level_growth = self._growth.get_level_growth(self.level)
        refinement_growth = self._growth.get_base_stat_growth(self.refinement)

        actual_base = base_value * (1 + level_growth + refinement_growth)

        self.actual_base_attack = Attribute(
            source=self.base_attack.source,
            name=self.base_attack.name,
            base_value=int(actual_base),  # 游戏里是整数
            value_type=self.base_attack.value_type,
            merge_type=self.base_attack.merge_type
        )

        # 2. 计算实际高级属性
        base_adv = self.advanced_attribute.base_value
        adv_growth = self._growth.get_advanced_stat_growth(self.refinement)

        actual_adv = base_adv * (1 + adv_growth)

        self.actual_advanced_attribute = Attribute(
            source=self.advanced_attribute.source,
            name=self.advanced_attribute.name,
            base_value=actual_adv,
            value_type=self.advanced_attribute.value_type,
            merge_type=self.advanced_attribute.merge_type
        )

        self.data_calculation_flag = True

    def ensure_attributes_calculated(self):
        """确保实际属性已计算"""
        if not self.data_calculation_flag:
            self._calculate_actual_attributes()

    def get_attributes(self) -> List[Attribute]:
        """
        获取武器所有属性
        确保返回前已计算实际值
        """
        self.ensure_attributes_calculated()

        attributes = []

        # 基础攻击力
        if self.actual_base_attack:
            attributes.append(copy.deepcopy(self.actual_base_attack))

        # 高级属性
        if self.actual_advanced_attribute:
            attributes.append(copy.deepcopy(self.actual_advanced_attribute))

        # 天赋属性
        if self.talent_attributes and 0 <= self.talent - 1 < len(self.talent_attributes):
            talent_attr = copy.deepcopy(self.talent_attributes[self.talent - 1])
            attributes.append(talent_attr)

        return attributes

    def get_base_attack_value(self) -> int:
        """获取基础攻击力实际值（快捷方法）"""
        self.ensure_attributes_calculated()
        return int(self.actual_base_attack.base_value) if self.actual_base_attack else 0

    def get_advanced_attribute_value(self) -> float:
        """获取高级属性实际值（快捷方法）"""
        self.ensure_attributes_calculated()
        return self.actual_advanced_attribute.base_value if self.actual_advanced_attribute else 0.0

    def to_dict(self) -> Dict:
        """转换为字典（用于序列化）"""
        return {
            'id': self.id,
            'name': self.name,
            'rarity': self.rarity,
            'weapon_type': self.weapon_type,
            'level': self.level,
            'refinement': self.refinement,
            'talent': self.talent,
            'base_attack': self.base_attack,
            'advanced_attribute': self.advanced_attribute,
            'talent_attributes': self.talent_attributes
        }


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