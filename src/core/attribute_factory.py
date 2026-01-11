"""属性工厂 - 直接创建有实际值的属性实例"""
from src.core.models import Attribute


class AttrName:
    """属性名称常量"""
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


class AttributeFactory:
    """属性工厂 - 直接创建带有具体值的属性实例"""

    @staticmethod
    def create(source: str, name: str, value: float = -1,
               value_type: int = 1, merge_type: int = -1,
               growth: float = -1) -> Attribute:
        """创建属性实例"""
        return Attribute(
            source=source,
            name=name,
            base_value=value,
            value_type=value_type,
            merge_type=merge_type,
            growth=growth
        )

    # ========== 角色相关 ==========

    @classmethod
    def character_stats_v0(cls, name: str, value: float, growth: int, source: str = 'stats') -> Attribute:
        """有成长值的角色属性"""
        return cls.create(source, name, value, value_type=0, growth=growth)

    @classmethod
    def character_stats_v1(cls, name: str, value: float, source: str = 'stats') -> Attribute:
        """数值是值的角色属性"""
        if value > 0:
            if name == AttrName.E_R and source == AttrName.A_A_A:
                value = value / 100
        return cls.create(source, name, value, value_type=1, growth=-1)

    @classmethod
    def character_stats_v2(cls, name: str, value: float = 0.0, source: str = 'stats') -> Attribute:
        """数值是百分比的角色属性"""
        if value > 0:
            if name == AttrName.C_R or name == AttrName.C_D:
                value = value / 10000
        return cls.create(source, name, value, value_type=2, growth=-1)

    # ========== 突破属性 ==========

    @classmethod
    def character_breakthrough(cls, name: str, value: float, source: str = "breakthrough") -> Attribute:
        """角色突破属性"""
        return cls.create(source, name, value, value_type=1, merge_type=1)

    # ========== 核心被动 ==========

    @classmethod
    def core_passive_v1(cls, name: str, value: float, source: str = "core_passive") -> Attribute:
        """核心被动数值是值的角色属性"""
        return cls.create(source, name, value, value_type=1, merge_type=1)

    @classmethod
    def core_passive_v2(cls, name: str, value: float, source: str = "core_passive") -> Attribute:
        """核心被动数值是百分比的角色属性"""
        if name == AttrName.HP:
            merge_type = 2
        else:
            merge_type = 1
        return cls.create(source, name, value, value_type=2, merge_type=merge_type)

    # ========== 武器属性 ==========

    @classmethod
    def weapon_base_atk(cls, value: float, source: str = "weapon_base") -> Attribute:
        """武器基础攻击力"""
        return cls.create(source, AttrName.ATK, value, value_type=1, merge_type=1)

    @classmethod
    def weapon_main_attr(cls, name: str, value: float, value_type: int,
                         source: str = "weapon_main") -> Attribute:
        """武器主要属性"""
        if value_type == 2:
            if name in [AttrName.C_R, AttrName.C_D, AttrName.PEN]:
                merge_type = 1
            else:
                merge_type = 2
        else:
            merge_type = 1

        return cls.create(source, name, value, value_type=value_type, merge_type=merge_type)

    @classmethod
    def weapon_talent(cls, name: str, value: float, value_type: int, source: str = "weapon_talent") -> Attribute:
        """武器天赋生命值"""
        if value_type == 2:
            value = value / 100
            if name in [AttrName.HP, AttrName.ATK]:
                merge_type = 2
            else:
                merge_type = 1
        else:
            merge_type = 1
        return cls.create(source, name, value, value_type=value_type, merge_type=merge_type)

    # ========== 驱动盘属性 ==========

    @classmethod
    def gear_main(cls, name: str, value_type: int, level: int = 0, source: str = "gear") -> Attribute:
        """驱动盘主属性"""

        # 属性公式定义
        value = -1
        merge_type = -1

        # 三围属性（生命/攻击/防御）
        if name in [AttrName.HP, AttrName.ATK, AttrName.DEF]:
            if value_type == 2:  # 百分比型
                value = 0.075 + (level * 0.015)
                merge_type = 2
            else:  # 数值型
                bases = {AttrName.HP: 550, AttrName.ATK: 79, AttrName.DEF: 46}
                growths = {AttrName.HP: 110, AttrName.ATK: 15.8, AttrName.DEF: 9.2}
                value = bases[name] + (level * growths[name])
                merge_type = 1

        # 特殊百分比属性（merge_type=1）
        elif name in [AttrName.C_R, AttrName.C_D, AttrName.A_M, AttrName.PEN]:
            value_type = 2
            bases = {AttrName.C_R: 0.06, AttrName.C_D: 0.12, AttrName.A_M: 0.075, AttrName.PEN: 0.06}
            growths = {AttrName.C_R: 0.012, AttrName.C_D: 0.024, AttrName.A_M: 0.015, AttrName.PEN: 0.012}
            value = bases[name] + (level * growths[name])
            merge_type = 1

        # 特殊百分比属性（merge_type=2）
        elif name in [AttrName.IMP, AttrName.E_R]:
            value_type = 2
            bases = {AttrName.IMP: 0.045, AttrName.E_R: 0.15}
            growths = {AttrName.IMP: 0.009, AttrName.E_R: 0.03}
            value = bases[name] + (level * growths[name])
            merge_type = 2

        # 伤害加成类属性
        elif name in [AttrName.PH_D_B, AttrName.FI_D_B, AttrName.IC_D_B, AttrName.EL_D_B, AttrName.ET_D_B]:
            value_type = 2
            value = 0.075 + (level * 0.015)
            merge_type = 1

        # 特殊数值属性
        elif name == AttrName.A_P:
            value = 23 + (level * 4.6)
            merge_type = 1

        return cls.create(source, name, value, value_type, merge_type)

    @classmethod
    def gear_sub(cls, name: str, value_type: int, level: int = 0, source: str = "gear") -> Attribute:
        """驱动盘副属性"""
        value = -1
        merge_type = -1

        if name == AttrName.HP:
            if value_type == 1:
                merge_type = 1
                value = 112 + (level * 112)
            else:
                merge_type = 2
                value = 0.03 + (level * 0.03)
        elif name == AttrName.ATK:
            if value_type == 1:
                merge_type = 1
                value = 19 + (level * 19)
            else:
                merge_type = 2
                value = 0.03 + (level * 0.03)
        elif name == AttrName.DEF:
            if value_type == 1:
                merge_type = 1
                value = 15 + (level * 15)
            else:
                merge_type = 2
                value = 0.048 + (level * 0.048)
        elif name == AttrName.C_R:
            value_type = 2
            merge_type = 1
            value = 0.024 + (level * 0.024)
        elif name == AttrName.C_D:
            value_type = 2
            merge_type = 1
            value = 0.048 + (level * 0.048)
        elif name in [AttrName.A_P, AttrName.PEN]:
            merge_type = 1
            value = 9 + (level * 9)
            if name == AttrName.A_P:
                value_type = 1
            else:
                value_type = 2

        return cls.create(source, name, value, value_type=value_type, merge_type=merge_type)

    # ========== 驱动盘套装效果 ==========

    @classmethod
    def gear_set(cls, name: str, value: float, value_type: int, source: str = "gear_set") -> Attribute:
        """套装效果"""
        if value_type == 2:
            if name in ["生命值", "攻击力", "防御力", "冲击力", "异常掌控", "能量自动回复"]:
                merge_type = 2
            else:
                merge_type = 1
        elif value_type == 1:
            merge_type = 1
        else:
            value = -1
            value_type = -1
            merge_type = -1

        return cls.create(source, name, value, value_type=value_type, merge_type=merge_type)

    # ========== 推荐属性 ==========

    @classmethod
    def get_gear_recommend_sub_attribute(cls, name: str, value_type: int, source: str = ""):
        return cls.create(source, name, value_type=value_type)

    @classmethod
    def get_gear_recommend_mian_attribute(cls, name: str, value_type: int, source: str = ""):
        return cls.create(source, name, value_type=value_type)
