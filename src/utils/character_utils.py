# src/utils/character_utils.py
"""角色计算工具函数 - 不依赖实例状态的纯函数"""
from typing import Dict, Any


def _get_extra_props_from_config(stat_config: Any) -> Dict[str, int]:
    """从StatConfig中获取ExtraLevel属性ID映射"""
    # 检查StatConfig是否有EXTRA_PROP_MAPPING属性
    if not hasattr(stat_config, 'EXTRA_PROP_MAPPING'):
        return _get_default_extra_props()

    extra_mapping = stat_config.EXTRA_PROP_MAPPING

    # 根据EXTRA_PROP_MAPPING创建属性键映射
    result = {}

    # 通过基础属性ID反向查找Extra属性ID
    base_to_extra = {}
    for extra_id, (base_id, _) in extra_mapping.items():
        base_to_extra[base_id] = extra_id

    # 映射到具体的属性键
    result['hp'] = base_to_extra.get(111, 11101)
    result['atk'] = base_to_extra.get(121, 12101)
    result['impact'] = base_to_extra.get(122, 12201)
    result['crit_rate'] = base_to_extra.get(201, 20101)
    result['crit_dmg'] = base_to_extra.get(211, 21101)
    result['anomaly_mastery'] = base_to_extra.get(314, 31401)
    result['penetration'] = base_to_extra.get(231, 23101)
    result['anomaly_proficiency'] = base_to_extra.get(312, 31201)
    result['energy_regen'] = base_to_extra.get(305, 30501)

    return result


def _get_default_extra_props() -> Dict[str, int]:
    """获取默认的ExtraLevel属性ID映射"""
    return {
        'hp': 11101,  # 生命值加成
        'atk': 12101,  # 攻击力加成
        'impact': 12201,  # 冲击力加成
        'crit_rate': 20101,  # 暴击率加成
        'crit_dmg': 21101,  # 暴击伤害加成
        'anomaly_mastery': 31401,  # 异常掌控加成
        'penetration': 23101,  # 穿透率加成
        'anomaly_proficiency': 31201
    }

def calculate_character_stats(character_data: Dict[str, Any], level: int,
                            stat_config) -> Dict[str, float]:
    """计算角色属性 - 整合配置使用"""
    try:
        stats_data = character_data.get("Stats", {})
        level_data = character_data.get("Level", {})
        extra_level_data = character_data.get("ExtraLevel", {})

        # 获取等级段映射
        level_segment = get_level_segment(level)
        extra_level_segment = get_extra_level_segment(level)

        # 从Level数据中获取当前等级的加成
        level_bonus = level_data.get(level_segment, {})

        # 从ExtraLevel数据中获取额外加成
        extra_bonus_data = extra_level_data.get(extra_level_segment, {}).get("Extra", {}) if extra_level_segment else {}

        # 使用配置或默认常量
        if stat_config:
            # 使用配置中的属性ID
            extra_props = _get_extra_props_from_config(stat_config)

        # 计算结果
        result = {
            "base_hp": _calculate_base_stat_with_bonus(stats_data, "HpMax", "HpGrowth", level, level_bonus, "HpMax", extra_bonus_data, extra_props['hp']),
            "base_atk": _calculate_base_stat_with_bonus(stats_data, "Attack", "AttackGrowth", level, level_bonus, "Attack", extra_bonus_data, extra_props['atk']),
            "base_def": _calculate_base_stat_with_bonus(stats_data, "Defence", "DefenceGrowth", level, level_bonus, "Defence", None, None),
            "impact": _calculate_simple_stat_with_bonus(stats_data, "BreakStun", extra_bonus_data, extra_props['impact'], level),
            "base_crit_rate": _calculate_crit_stat(stats_data, "Crit", extra_bonus_data, extra_props['crit_rate'], level),
            "base_crit_dmg": _calculate_crit_stat(stats_data, "CritDamage", extra_bonus_data, extra_props['crit_dmg'], level),
            "anomaly_mastery": _calculate_simple_stat_with_bonus(stats_data, "ElementAbnormalPower", extra_bonus_data, extra_props['anomaly_mastery'], level),
            "penetration": _calculate_penetration_stat(stats_data, level, extra_bonus_data),
            "anomaly_proficiency": _calculate_simple_stat_with_bonus(stats_data, "ElementMystery", extra_bonus_data, extra_props['anomaly_proficiency'], level),
            "energy_regen": _calculate_energy_regen_stat(stats_data, "SpRecover", extra_bonus_data, extra_props['energy_regen'], level),
        }

        return result

    except Exception as e:
        print(f"计算角色属性错误: {e}")
        import traceback
        traceback.print_exc()
        return get_default_stats()


def _calculate_base_stat_with_bonus(stats_data: Dict, base_key: str, growth_key: str, level: int,
                                    level_bonus: Dict, level_bonus_key: str,
                                    extra_bonus_data: Dict, extra_prop_id: int) -> float:
    """计算基础属性（生命值、攻击力、防御力）"""
    # 基础值 + 成长值
    base_value = _calculate_base_with_growth(stats_data, base_key, growth_key, level)

    # 等级加成
    level_bonus_value = level_bonus.get(level_bonus_key, 0)

    # ExtraLevel加成
    extra_bonus_value = get_extra_value(extra_bonus_data, extra_prop_id) if level > 10 and extra_bonus_data else 0

    return base_value + level_bonus_value + extra_bonus_value


def _calculate_base_with_growth(stats_data: Dict, base_key: str, growth_key: str, level: int) -> float:
    """计算基础值 + 成长值"""
    base_value = stats_data.get(base_key, 0)
    growth_value = stats_data.get(growth_key, 0)
    return base_value + (0 if level == 0 else (level - 1) * growth_value / 10000.0)


def _calculate_simple_stat_with_bonus(stats_data: Dict, stat_key: str,
                                      extra_bonus_data: Dict, extra_prop_id: int, level: int) -> float:
    """计算简单属性（冲击力、异常掌控等）"""
    base_value = stats_data.get(stat_key, 0)
    extra_bonus_value = get_extra_value(extra_bonus_data, extra_prop_id) if level > 10 and extra_bonus_data else 0
    return base_value + extra_bonus_value


def _calculate_crit_stat(stats_data: Dict, stat_key: str,
                         extra_bonus_data: Dict, extra_prop_id: int, level: int) -> float:
    """计算暴击属性（暴击率、暴击伤害）"""
    base_value = stats_data.get(stat_key, 500 if stat_key == "Crit" else 5000)
    extra_bonus_value = get_extra_value(extra_bonus_data, extra_prop_id) if level > 10 and extra_bonus_data else 0
    return (base_value + extra_bonus_value) / 10000.0


def _calculate_penetration_stat(stats_data: Dict, level: int, extra_bonus_data: Dict) -> float:
    """计算穿透率"""
    base_penetration = stats_data.get("PenRate", 0) / 100.0
    extra_bonus_penetration = (
                get_extra_value(extra_bonus_data, 23101) / 100.0) if level > 10 and extra_bonus_data else 0
    return base_penetration  + extra_bonus_penetration

def _calculate_energy_regen_stat(stats_data: Dict, stat_key: str,
                                      extra_bonus_data: Dict, extra_prop_id: int, level: int) -> float:
    """计算简单属性（冲击力、异常掌控等）"""
    base_value = stats_data.get(stat_key, 0) / 100.0
    extra_bonus_value = get_extra_value(extra_bonus_data, extra_prop_id) if level > 10 and extra_bonus_data else 0
    return base_value + extra_bonus_value

def get_extra_value(extra_data: Dict, prop_id: int) -> float:
    """从Extra数据中获取属性值"""
    if not extra_data:
        return 0

    prop_key = str(prop_id)
    if prop_key in extra_data:
        prop_info = extra_data[prop_key]
        if isinstance(prop_info, dict):
            return prop_info.get("Value", 0)
    return 0


def get_level_segment(level: int) -> str:
    """获取等级段（对应JS中的AA数组）"""
    if level <= 10:
        return "1"
    elif level <= 20:
        return "2"
    elif level <= 30:
        return "3"
    elif level <= 40:
        return "4"
    elif level <= 50:
        return "5"
    else:
        return "6"


def get_extra_level_segment(level: int) -> str:
    """根据等级获取突破阶段"""
    if level <= 15:
        return "1"
    elif level <= 25:
        return "2"
    elif level <= 35:
        return "3"
    elif level <= 45:
        return "4"
    elif level <= 55:
        return "5"
    else:
        return "6"


def get_default_stats() -> Dict[str, float]:
    """获取默认属性"""
    return {
        "base_hp": 1000,
        "base_atk": 100,
        "base_def": 50,
        "base_crit_rate": 0.05,
        "base_crit_dmg": 0.50,
        "impact": 0,
        "penetration": 0,
        "anomaly_mastery": 0
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


def validate_character_config(level: int, ascension: int, passive_level: int) -> bool:
    """验证角色配置有效性"""
    # 根据游戏实际等级限制
    if not (1 <= level <= 60):
        return False

    # 突破等级验证
    max_ascension = 6
    if not (0 <= ascension <= max_ascension):
        return False

    # 被动技能等级验证
    if not (0 <= passive_level <= 7):
        return False

    return True


def format_stat_display(stat_value: float, stat_type: str) -> str:
    """格式化属性值显示"""
    if stat_type in ["base_crit_rate", "base_crit_dmg", "penetration"]:
        return f"{stat_value:.1%}"
    elif stat_type in ["base_hp", "base_atk", "base_def", "impact", "anomaly_mastery"]:
        return f"{stat_value:,.0f}"
    else:
        return str(stat_value)


def debug_character_calculation(character_data: Dict[str, Any], level: int, result: Dict[str, float]):
    """调试角色计算"""
    stats_data = character_data.get("Stats", {})
    print(f"=== 角色 {character_data.get('Name', '未知')} 等级 {level} 计算详情 ===")
    print(f"基础攻击力: {stats_data.get('Attack', 0)}")
    print(f"攻击成长: {stats_data.get('AttackGrowth', 0)}")
    print(f"等级段: {get_level_segment(level)}")
    print(f"ExtraLevel段: {get_extra_level_segment(level)}")
    print(f"最终攻击力: {result['base_atk']:.1f}")
    print(f"暴击率: {stats_data.get('Crit', 500)} -> {result['base_crit_rate']:.1%}")
    print(f"暴击伤害: {stats_data.get('CritDamage', 5000)} -> {result['base_crit_dmg']:.1%}")
    print("================================")