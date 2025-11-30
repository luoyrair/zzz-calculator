# src/utils/character_utils.py
"""角色计算工具函数 - 适配新架构"""
from typing import Dict

from src.core.character_models import BaseCharacterStats, RawCharacterData


def calculate_sheer_force(raw_data: RawCharacterData, base_stats: BaseCharacterStats,
                          extra_level: int = 0) -> float:
    """计算贯穿力 - 适配新架构

    Args:
        raw_data: 原始角色数据
        base_stats: 基础角色属性
        extra_level: 核心技等级
    """
    try:
        if not raw_data:
            return 0.0

        # 使用基础属性值
        effective_hp = base_stats.HP
        effective_atk = base_stats.ATK

        # 从被动数据中获取贯穿力加成系数
        passive_data = raw_data.Passive.get("Level", {})
        character_id = raw_data.Id

        # 构建被动技能key
        passive_level = extra_level if extra_level >= 1 else 1
        passive_key = f"{character_id}50{passive_level:01d}"

        passive_info = passive_data.get(passive_key, {})
        extra_property = passive_info.get("ExtraProperty", {})

        # 获取攻击力和生命值转贯穿力的系数
        attack_to_pen = 0.0
        hp_to_pen = 0.0

        for prop_id, prop_data in extra_property.items():
            if prop_data.get("Target") == 123:  # 贯穿力目标ID
                if prop_id == "121":  # 攻击力转贯穿力
                    attack_to_pen = prop_data.get("Value", 0) / 10000.0
                elif prop_id == "111":  # 生命值转贯穿力
                    hp_to_pen = prop_data.get("Value", 0) / 10000.0

        # 计算贯穿力
        penetration = (effective_atk * attack_to_pen + effective_hp * hp_to_pen)
        return penetration

    except Exception as e:
        print(f"计算贯穿力失败: {e}")
        return 0.0


def calculate_character_base_stats(raw_data: RawCharacterData, level: int,
                                   extra_level: int, stat_config) -> BaseCharacterStats:
    """计算角色基础属性 - 返回BaseCharacterStats对象"""
    try:
        # 使用新架构的BaseCharacterStats
        base_stats = BaseCharacterStats()

        # 计算突破阶段 (根据等级确定)
        breakthrough = _calculate_breakthrough_level(level)

        # 使用新架构的计算方法
        base_stats.calculate_from_raw(raw_data, level, breakthrough, extra_level)

        # 计算贯穿力 (需要单独处理，因为依赖最终属性)
        base_stats.Sheer_Force = calculate_sheer_force(raw_data, base_stats, extra_level)

        return base_stats

    except Exception as e:
        print(f"计算角色基础属性错误: {e}")
        return get_default_base_stats()


def _calculate_breakthrough_level(level: int) -> int:
    """根据等级计算突破阶段"""
    if level <= 10:
        return 0
    elif level <= 20:
        return 1
    elif level <= 30:
        return 2
    elif level <= 40:
        return 3
    elif level <= 50:
        return 4
    else:
        return 5


def get_default_base_stats() -> BaseCharacterStats:
    """获取默认基础属性"""
    return BaseCharacterStats(
        HP=1000,
        ATK=100,
        DEF=50,
        Impact=0,
        CRIT_Rate=0.05,
        CRIT_DMG=0.50,
        Anomaly_Mastery=0,
        Anomaly_Proficiency=0,
        PEN_Ratio=0.0,
        Energy_Regen=0.0,
        Sheer_Force=0.0,
        Automatic_Adrenaline_Accumulation=0.0
    )


def get_default_stats() -> Dict[str, float]:
    """获取默认属性 (兼容旧代码)"""
    default_stats = get_default_base_stats()
    return {
        "HP": default_stats.HP,
        "ATK": default_stats.ATK,
        "DEF": default_stats.DEF,
        "CRIT_Rate": default_stats.CRIT_Rate,
        "CRIT_DMG": default_stats.CRIT_DMG,
        "Impact": default_stats.Impact,
        "PEN_Ratio": default_stats.PEN_Ratio,
        "Anomaly_Mastery": default_stats.Anomaly_Mastery,
        "Anomaly_Proficiency": default_stats.Anomaly_Proficiency,
        "Sheer_Force": default_stats.Sheer_Force,
        "Energy_Regen": default_stats.Energy_Regen,
        "Automatic_Adrenaline_Accumulation": default_stats.Automatic_Adrenaline_Accumulation
    }


def get_default_display_info(character_id: str) -> Dict[str, str]:
    """获取默认显示信息"""
    return {
        "id": character_id,
        "name": "未知角色",
        "code_name": "未知",
        "rarity": "4",
        "weapon_type": "未知",
        "element_type": "未知"
    }