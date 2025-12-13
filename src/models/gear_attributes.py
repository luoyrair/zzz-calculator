from typing import Union

from src.models.attributes import GearAttributeValueType, AttributeType


class Attribute:
    """驱动盘属性的基础类"""

    def __init__(self, name: str = "", attribute_type: AttributeType = None,
                 attribute_value_type: GearAttributeValueType = None,
                 base: float = 0.0, growth: Union[float, int] = 0):
        self.name = name
        self.attribute_type = attribute_type
        self.attribute_value_type = attribute_value_type
        self.base = base
        self.growth = growth

    def calculate_value_at_level(self, level: int) -> float:
        """计算指定等级时的属性值"""
        return self.base + level * self.growth

    def is_percentage_type(self) -> bool:
        """判断是否为百分比类型"""
        return self.attribute_value_type in [
            GearAttributeValueType.PERCENTAGE,
            GearAttributeValueType.RATE_PERCENTAGE,
            GearAttributeValueType.DMG_BONUS_PERCENTAGE
        ]

    def __repr__(self):
        return f"Attribute(name={self.name}, type={self.attribute_type}, value_type={self.attribute_value_type})"


class SubAttribute(Attribute):
    """驱动盘的副属性类"""

    def __init__(self, name: str = "", attribute_type: AttributeType = None,
                 attribute_value_type: GearAttributeValueType = None,
                 base: float = 0.0, growth: Union[float, int] = 0):
        super().__init__(name, attribute_type, attribute_value_type, base, growth)
        self.enhancement_level: int = 0

    def calculate_value_at_enhancement_level(self) -> float:
        """计算强化等级时的属性值"""
        return self.base + self.enhancement_level * self.growth


# 主属性工厂函数
def create_main_attribute_numeric(name: str, attribute_type: AttributeType, base: float, growth: float) -> Attribute:
    """创建数值型主属性"""
    return Attribute(
        name=name,
        attribute_type=attribute_type,
        attribute_value_type=GearAttributeValueType.NUMERIC_VALUE,
        base=base,
        growth=growth
    )

def create_main_attribute_percentage(name: str, attribute_type: AttributeType, base: float, growth: float) -> Attribute:
    """创建百分比型主属性"""
    return Attribute(
        name=name,
        attribute_type=attribute_type,
        attribute_value_type=GearAttributeValueType.PERCENTAGE,
        base=base,
        growth=growth
    )

def create_main_attribute_rate_percentage(name: str, attribute_type: AttributeType, base: float, growth: float) -> Attribute:
    """创建比率百分比型主属性（如暴击率）"""
    return Attribute(
        name=name,
        attribute_type=attribute_type,
        attribute_value_type=GearAttributeValueType.RATE_PERCENTAGE,
        base=base,
        growth=growth
    )

def create_main_attribute_dmg_bonus_percentage(name: str, attribute_type: AttributeType, base: float, growth: float) -> Attribute:
    """创建伤害加成百分比型主属性"""
    return Attribute(
        name=name,
        attribute_type=attribute_type,
        attribute_value_type=GearAttributeValueType.DMG_BONUS_PERCENTAGE,
        base=base,
        growth=growth
    )

# 副属性工厂函数
def create_sub_attribute_numeric(name: str, attribute_type: AttributeType, base: float, growth: float) -> SubAttribute:
    """创建数值型副属性"""
    return SubAttribute(
        name=name,
        attribute_type=attribute_type,
        attribute_value_type=GearAttributeValueType.NUMERIC_VALUE,
        base=base,
        growth=growth
    )

def create_sub_attribute_percentage(name: str, attribute_type: AttributeType, base: float, growth: float) -> SubAttribute:
    """创建百分比型副属性"""
    return SubAttribute(
        name=name,
        attribute_type=attribute_type,
        attribute_value_type=GearAttributeValueType.PERCENTAGE,
        base=base,
        growth=growth
    )

def create_sub_attribute_rate_percentage(name: str, attribute_type: AttributeType, base: float, growth: float) -> SubAttribute:
    """创建比率百分比型副属性"""
    return SubAttribute(
        name=name,
        attribute_type=attribute_type,
        attribute_value_type=GearAttributeValueType.RATE_PERCENTAGE,
        base=base,
        growth=growth
    )


class GearMainAttributes:
    """驱动盘主属性集合，每个属性都是独立的实例"""

    # 生命值（数值和百分比是分开的）
    hp_numeric = create_main_attribute_numeric("生命值", AttributeType.HP, 550, 110)
    hp_percentage = create_main_attribute_percentage("生命值百分比", AttributeType.HP, 0.075, 0.015)

    # 攻击力
    attack_numeric = create_main_attribute_numeric("攻击力", AttributeType.ATK, 79, 15.8)
    attack_percentage = create_main_attribute_percentage("攻击力百分比", AttributeType.ATK, 0.075, 0.015)

    # 防御力
    defence_numeric = create_main_attribute_numeric("防御力", AttributeType.DEF, 46, 9.2)
    defence_percentage = create_main_attribute_percentage("防御力百分比", AttributeType.DEF, 0.075, 0.015)

    # 异常精通
    anomaly_proficiency = create_main_attribute_numeric("异常精通", AttributeType.ANOMALY_PROFICIENCY, 23, 4.6)

    # 冲击力
    impact = create_main_attribute_percentage("冲击力", AttributeType.IMPACT, 0.045, 0.009)

    # 暴击率
    crit_rate = create_main_attribute_rate_percentage("暴击率", AttributeType.CRIT_RATE, 0.06, 0.012)

    # 暴击伤害
    crit_dmg = create_main_attribute_rate_percentage("暴击伤害", AttributeType.CRIT_DMG, 0.12, 0.024)

    # 穿透率
    pen_ratio = create_main_attribute_rate_percentage("穿透率", AttributeType.PEN_RATIO, 0.06, 0.012)

    # 异常掌控
    anomaly_mastery = create_main_attribute_percentage("异常掌控", AttributeType.ANOMALY_MASTERY, 0.075, 0.015)

    # 能量自动回复
    energy_regen = create_main_attribute_rate_percentage("能量自动回复", AttributeType.ENERGY_REGEN, 0.15, 0.03)

    # 各种伤害加成
    physical_dmg_bonus = create_main_attribute_dmg_bonus_percentage("物理伤害加成", AttributeType.PHYSICAL_DMG_BONUS,
                                                                    0.075, 0.015)
    fire_dmg_bonus = create_main_attribute_dmg_bonus_percentage("火属性伤害加成", AttributeType.FIRE_DMG_BONUS, 0.075,
                                                                0.015)
    ice_dmg_bonus = create_main_attribute_dmg_bonus_percentage("冰属性伤害加成", AttributeType.ICE_DMG_BONUS, 0.075,
                                                               0.015)
    electric_dmg_bonus = create_main_attribute_dmg_bonus_percentage("电属性伤害加成", AttributeType.ELECTRIC_DMG_BONUS,
                                                                    0.075, 0.015)
    ether_dmg_bonus = create_main_attribute_dmg_bonus_percentage("以太伤害加成", AttributeType.ETHER_DMG_BONUS, 0.075,
                                                                 0.015)


class GearSubAttributes:
    """驱动盘副属性集合，每个属性都是独立的实例"""

    # 生命值
    hp_numeric = create_sub_attribute_numeric("生命值", AttributeType.HP, 112, 112)
    hp_percentage = create_sub_attribute_percentage("生命值百分比", AttributeType.HP, 0.03, 0.03)

    # 攻击力
    attack_numeric = create_sub_attribute_numeric("攻击力", AttributeType.ATK, 19, 19)
    attack_percentage = create_sub_attribute_percentage("攻击力百分比", AttributeType.ATK, 0.03, 0.03)

    # 防御力
    defence_numeric = create_sub_attribute_numeric("防御力", AttributeType.DEF, 15, 15)
    defence_percentage = create_sub_attribute_percentage("防御力百分比", AttributeType.DEF, 0.048, 0.048)

    # 暴击率
    crit_rate = create_sub_attribute_rate_percentage("暴击率", AttributeType.CRIT_RATE, 0.024, 0.024)

    # 暴击伤害
    crit_dmg = create_sub_attribute_rate_percentage("暴击伤害", AttributeType.CRIT_DMG, 0.048, 0.048)

    # 异常精通
    anomaly_proficiency = create_sub_attribute_numeric("异常精通", AttributeType.ANOMALY_PROFICIENCY, 9, 9)

    # 穿透力
    pen = create_sub_attribute_numeric("穿透力", AttributeType.PEN, 9, 9)
