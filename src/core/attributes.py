from src.core.models import Attribute


class AttributeName:
    HP = "生命值"
    ATK = "攻击力"
    DEF = "防御力"
    IMP = "冲击力"
    C_R = "暴击率"
    C_D = "暴击伤害"
    A_M = "异常掌控"
    A_P = "异常精通"
    PEN_R = "穿透率"
    PEN = "穿透值"
    E_R = "能量自动回复"
    PH_D_B = "物理伤害加成"
    FI_D_B = "火属性伤害加成"
    IC_D_B = "冰属性伤害加成"
    EL_D_B = "电属性伤害加成"
    ET_D_B = "以太伤害加成"
    S_F = "贯穿力"
    A_A_A = "闪能自动积蓄"


character_attribute = [
    Attribute(source="", name="生命值", base_value=-1, value_type=0, growth=-1),
    Attribute(source="", name="攻击力", base_value=-1, value_type=0, growth=-1),
    Attribute(source="", name="防御力", base_value=-1, value_type=0, growth=-1),
    Attribute(source="", name="冲击力", base_value=-1, value_type=1),
    Attribute(source="", name="异常掌控", base_value=-1, value_type=1),
    Attribute(source="", name="异常精通", base_value=-1, value_type=1),
    Attribute(source="", name="能量自动回复", base_value=-1.0, value_type=1),
    Attribute(source="", name="闪能自动积蓄", base_value=-1, value_type=1),
    Attribute(source="", name="暴击率", base_value=-1.0, value_type=2),
    Attribute(source="", name="暴击伤害", base_value=-1.0, value_type=2),
    Attribute(source="", name="穿透率", base_value=0.0, value_type=2),
    Attribute(source="", name="穿透值", base_value=-1, value_type=1),
    Attribute(source="", name="物理伤害加成", base_value=0.0, value_type=2),
    Attribute(source="", name="火属性伤害加成", base_value=0.0, value_type=2),
    Attribute(source="", name="冰属性伤害加成", base_value=0.0, value_type=2),
    Attribute(source="", name="电属性伤害加成", base_value=0.0, value_type=2),
    Attribute(source="", name="以太伤害加成", base_value=0.0, value_type=2),
]

breakthrough_attribute = [
    Attribute(source="", name="生命值", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="攻击力", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="防御力", base_value=-1, value_type=1, merge_type=1),
]

core_passive_attribute = [
    Attribute(source="", name="生命值", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="生命值", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="攻击力", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="冲击力", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="异常掌控", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="异常精通", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="能量自动回复", base_value=-1.0, value_type=1, merge_type=1),
    Attribute(source="", name="暴击率", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="暴击伤害", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="穿透率", base_value=-1.0, value_type=2, merge_type=1),
]

character_recommend_attribute = [
    Attribute(source="", name="生命值", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="攻击力", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="防御力", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="冲击力", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="暴击率", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="暴击伤害", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="异常掌控", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="异常精通", base_value=-1, value_type=1, merge_type=-1),
    Attribute(source="", name="穿透率", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="能量自动回复", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="物理伤害加成", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="火属性伤害加成", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="冰属性伤害加成", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="电属性伤害加成", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="以太伤害加成", base_value=-1.0, value_type=2, merge_type=-1),
]

weapon_base_attribute = [
    Attribute(source="", name="攻击力", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="生命值", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="攻击力", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="防御力", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="冲击力", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="异常掌控", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="异常精通", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="能量自动回复", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="暴击率", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="暴击伤害", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="穿透率", base_value=-1.0, value_type=2, merge_type=1),
]

weapon_talents_attribute = [
    Attribute(source="", name="生命值", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="攻击力", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="暴击率", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="暴击伤害", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="异常掌控", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="能量自动回复", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="物理伤害加成", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="火属性伤害加成", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="冰属性伤害加成", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="电属性伤害加成", base_value=-1.0, value_type=2, merge_type=1),
]

gear_main_attribute = [
    Attribute(source="", name="生命值", base_value=550, value_type=1, merge_type=1, growth=110),
    Attribute(source="", name="生命值", base_value=0.075, value_type=2, merge_type=2, growth=0.015),
    Attribute(source="", name="攻击力", base_value=79, value_type=1, merge_type=1, growth=15.8),
    Attribute(source="", name="攻击力", base_value=0.075, value_type=2, merge_type=2, growth=0.015),
    Attribute(source="", name="防御力", base_value=46, value_type=1, merge_type=1, growth=9.2),
    Attribute(source="", name="防御力", base_value=0.075, value_type=2, merge_type=2, growth=0.015),
    Attribute(source="", name="冲击力", base_value=0.045, value_type=2, merge_type=2, growth=0.009),
    Attribute(source="", name="暴击率", base_value=0.06, value_type=2, merge_type=1, growth=0.012),
    Attribute(source="", name="暴击伤害", base_value=0.12, value_type=2, merge_type=1, growth=0.024),
    Attribute(source="", name="穿透率", base_value=0.06, value_type=2, merge_type=1, growth=0.012),
    Attribute(source="", name="异常掌控", base_value=0.075, value_type=2, merge_type=2, growth=0.015),
    Attribute(source="", name="异常精通", base_value=23, value_type=1, merge_type=1, growth=4.6),
    Attribute(source="", name="能量自动回复", base_value=0.15, value_type=2, merge_type=2, growth=0.03),
    Attribute(source="", name="物理伤害加成", base_value=0.075, value_type=2, merge_type=1, growth=0.015),
    Attribute(source="", name="火属性伤害加成", base_value=0.075, value_type=2, merge_type=1, growth=0.015),
    Attribute(source="", name="冰属性伤害加成", base_value=0.075, value_type=2, merge_type=1, growth=0.015),
    Attribute(source="", name="电属性伤害加成", base_value=0.075, value_type=2, merge_type=1, growth=0.015),
    Attribute(source="", name="以太伤害加成", base_value=0.075, value_type=2, merge_type=1, growth=0.015),
]

gear_sub_attribute = [
    Attribute(source="", name="生命值", base_value=112, value_type=1, merge_type=1, growth=112),
    Attribute(source="", name="生命值", base_value=0.03, value_type=2, merge_type=2, growth=0.03),
    Attribute(source="", name="攻击力", base_value=19, value_type=1, merge_type=1, growth=19),
    Attribute(source="", name="攻击力", base_value=0.03, value_type=2, merge_type=2, growth=0.03),
    Attribute(source="", name="防御力", base_value=15, value_type=1, merge_type=1, growth=15),
    Attribute(source="", name="防御力", base_value=0.048, value_type=2, merge_type=2, growth=0.048),
    Attribute(source="", name="暴击率", base_value=0.024, value_type=2, merge_type=1, growth=0.024),
    Attribute(source="", name="暴击伤害", base_value=0.048, value_type=2, merge_type=1, growth=0.048),
    Attribute(source="", name="穿透值", base_value=9, value_type=1, merge_type=1, growth=9),
    Attribute(source="", name="异常精通", base_value=9, value_type=1, merge_type=1, growth=9),
]

gear_set_effect_attribute = [
    Attribute(source="", name="生命值", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="攻击力", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="防御力", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="冲击力", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="暴击率", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="暴击伤害", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="异常掌控", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="异常精通", base_value=-1, value_type=1, merge_type=1),
    Attribute(source="", name="穿透率", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="能量自动回复", base_value=-1.0, value_type=2, merge_type=2),
    Attribute(source="", name="物理伤害加成", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="火属性伤害加成", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="冰属性伤害加成", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="电属性伤害加成", base_value=-1.0, value_type=2, merge_type=1),
    Attribute(source="", name="以太伤害加成", base_value=-1.0, value_type=2, merge_type=1),
]

gear_recommend_sub_attribute = [
    Attribute(source="", name="生命值", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="攻击力", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="暴击率", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="暴击伤害", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="异常掌控", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="火属性伤害加成", base_value=-1.0, value_type=2, merge_type=-1),
    Attribute(source="", name="以太伤害加成", base_value=-1.0, value_type=2, merge_type=-1),
]