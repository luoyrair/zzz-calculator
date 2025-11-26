# src/core/calculator.py
"""简化版属性计算器"""
from typing import Dict, Any, List
from .models import CalculationResult


class GearCalculator:
    """驱动盘属性计算器 - 单一职责：基础属性计算"""

    def __init__(self, gear_config):
        self.gear_config = gear_config

    def calculate_main_attribute(self, attr_name: str, level: int) -> float:
        """计算主属性值 - 使用AttributeConfig中的映射"""
        # 使用配置中的属性映射
        mapped_attr_name = self.gear_config.attribute_config.ATTRIBUTE_MAPPING.get(attr_name, attr_name)

        growth_data = self.gear_config.growth_config.get_main_attribute_growth(mapped_attr_name)
        if not growth_data:
            return 0.0

        base_value = growth_data.get("base", 0)
        growth_rate = growth_data.get("growth", 0)

        return base_value + growth_rate * level

    def calculate_sub_attribute(self, attr_name: str, enhancement_count: int) -> float:
        """计算副属性值"""
        growth_data = self.gear_config.growth_config.get_sub_attribute_growth(attr_name)
        if not growth_data:
            return 0.0

        base_value = growth_data.get("base", 0)
        growth_rate = growth_data.get("growth", 0)

        return base_value + growth_rate * enhancement_count

    def _sum_attribute_values(self, gear_data: List[Dict[str, Any]],
                              target_attrs: List[str]) -> Dict[str, float]:
        """汇总指定属性的值"""
        result = {"flat": 0.0, "percent": 0.0}

        for gear in gear_data:
            # 主属性
            main_attr = gear.get("main_attr")
            if main_attr and main_attr.get("name") in target_attrs:
                value = main_attr.get("value", 0)
                if main_attr["name"].endswith('_PERCENT'):
                    result["percent"] += value
                else:
                    result["flat"] += value

            # 副属性
            for sub_attr in gear.get("sub_attrs", []):
                if sub_attr and sub_attr.get("name") in target_attrs:
                    value = sub_attr.get("value", 0)
                    if sub_attr["name"].endswith('_PERCENT'):
                        result["percent"] += value
                    else:
                        result["flat"] += value

        return result

    def calculate_hp_stats(self, base_hp: float, gear_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算生命值相关属性"""
        hp_attrs = ["HP", "HP_PERCENT"]
        hp_values = self._sum_attribute_values(gear_data, hp_attrs)

        final_hp = base_hp * (1 + hp_values["percent"]) + hp_values["flat"]

        return {
            "base_hp": base_hp,
            "total_flat_hp": hp_values["flat"],
            "total_hp_percent": hp_values["percent"],
            "final_hp": final_hp,
            "increase_percent": (final_hp / base_hp - 1) if base_hp > 0 else 0
        }

    def calculate_atk_stats(self, base_atk: float, gear_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算攻击力相关属性"""
        atk_attrs = ["ATK", "ATK_PERCENT"]
        atk_values = self._sum_attribute_values(gear_data, atk_attrs)

        final_atk = base_atk * (1 + atk_values["percent"]) + atk_values["flat"]

        return {
            "base_atk": base_atk,
            "total_flat_atk": atk_values["flat"],
            "total_atk_percent": atk_values["percent"],
            "final_atk": final_atk,
            "increase_percent": (final_atk / base_atk - 1) if base_atk > 0 else 0
        }

    def calculate_def_stats(self, base_def: float, gear_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算防御力相关属性"""
        def_attrs = ["DEF", "DEF_PERCENT"]
        def_values = self._sum_attribute_values(gear_data, def_attrs)

        final_def = base_def * (1 + def_values["percent"]) + def_values["flat"]

        return {
            "base_def": base_def,
            "total_flat_def": def_values["flat"],
            "total_def_percent": def_values["percent"],
            "final_def": final_def,
            "increase_percent": (final_def / base_def - 1) if base_def > 0 else 0
        }

    def calculate_crit_stats(self, base_crit_rate: float, base_crit_dmg: float,
                             gear_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算暴击相关属性"""
        crit_rate_total = base_crit_rate
        crit_dmg_total = base_crit_dmg

        for gear in gear_data:
            # 主属性
            main_attr = gear.get("main_attr")
            if main_attr:
                attr_name = main_attr.get("name")
                value = main_attr.get("value", 0)
                if attr_name == "CRIT_RATE":
                    crit_rate_total += value
                elif attr_name == "CRIT_DMG":
                    crit_dmg_total += value

            # 副属性
            for sub_attr in gear.get("sub_attrs", []):
                if sub_attr:
                    attr_name = sub_attr.get("name")
                    value = sub_attr.get("value", 0)
                    if attr_name == "CRIT_RATE":
                        crit_rate_total += value
                    elif attr_name == "CRIT_DMG":
                        crit_dmg_total += value

        # 限制暴击率在合理范围内
        crit_rate_total = max(0, min(crit_rate_total, 1.0))

        return {
            "base_crit_rate": base_crit_rate,
            "base_crit_dmg": base_crit_dmg,
            "total_crit_rate": crit_rate_total,
            "total_crit_dmg": crit_dmg_total,
            "crit_rate_added": crit_rate_total - base_crit_rate,
            "crit_dmg_added": crit_dmg_total - base_crit_dmg
        }

    def calculate_impact_stats(self, base_impact: int, gear_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算冲击力相关属性 - 修正版本"""
        impact_percent_total = 0.0

        # 冲击力只有主属性且是百分比加成
        for gear in gear_data:
            main_attr = gear.get("main_attr")
            if main_attr and main_attr.get("name") == "IMPACT":
                impact_percent_total += main_attr.get("value", 0)

        # 冲击力加成 = 基础冲击力 * (1 + 百分比加成)
        final_impact = base_impact * (1 + impact_percent_total)

        return {
            "base_impact": base_impact,
            "final_impact": final_impact,
            "impact_percent": impact_percent_total,
            "impact_added": final_impact - base_impact
        }

    def calculate_penetration_stats(self, base_penetration: float, gear_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算穿透率相关属性 - 修正版本"""
        penetration_rate_total = 0.0
        penetration_value_total = 0.0

        for gear in gear_data:
            # 主属性 - 穿透率
            main_attr = gear.get("main_attr")
            if main_attr:
                attr_name = main_attr.get("name")
                value = main_attr.get("value", 0)
                if attr_name == "PENETRATION":
                    penetration_rate_total += value

            # 副属性 - 穿透值（独立属性）
            for sub_attr in gear.get("sub_attrs", []):
                if sub_attr:
                    attr_name = sub_attr.get("name")
                    value = sub_attr.get("value", 0)
                    if attr_name == "PENETRATION_VALUE":
                        penetration_value_total += value

        # 冲击力加成 = 基础冲击力 * (1 + 百分比加成)
        final_penetration = base_penetration * (1 + penetration_rate_total)

        # 穿透值和穿透率是两个独立的属性，不需要转换
        return {
            "base_penetration": base_penetration,
            "final_penetration": final_penetration,
            "penetration_added": final_penetration - base_penetration,
            "penetration_value": penetration_value_total
        }

    def calculate_anomaly_stats(self, base_mastery: int, base_proficiency: int,
                                gear_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算异常属性相关 - 修正版本"""
        mastery_percent_total = 0.0
        proficiency_flat_total = 0

        for gear in gear_data:
            # 主属性
            main_attr = gear.get("main_attr")
            if main_attr:
                attr_name = main_attr.get("name")
                value = main_attr.get("value", 0)
                if attr_name == "ANOMALY_MASTERY":
                    # 异常精通是数值加成（int）
                    proficiency_flat_total += int(value)
                elif attr_name == "ANOMALY_PROFICIENCY":
                    # 异常掌控是百分比加成且只有主属性
                    mastery_percent_total += value

            # 副属性 - 只有异常精通有副属性
            for sub_attr in gear.get("sub_attrs", []):
                if sub_attr:
                    attr_name = sub_attr.get("name")
                    value = sub_attr.get("value", 0)
                    if attr_name == "ANOMALY_MASTERY":
                        proficiency_flat_total += int(value)

        # 异常掌控 = 基础异常掌控 * (1 + 百分比加成)
        final_mastery = base_mastery * (1 + mastery_percent_total)
        # 异常精通 = 基础异常精通 + 固定值加成
        final_proficiency = base_proficiency + proficiency_flat_total

        return {
            "base_anomaly_mastery": base_mastery,
            "base_anomaly_proficiency": base_proficiency,
            "final_mastery": final_mastery,
            "final_proficiency": final_proficiency,
            "anomaly_mastery_percent": mastery_percent_total,
            "anomaly_proficiency_flat": proficiency_flat_total,
            "anomaly_mastery_added": final_mastery - base_mastery,
            "anomaly_proficiency_added": final_proficiency - base_proficiency
        }

    def calculate_energy_regen_stats(self, base_energy_regen: int, gear_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算能量回复相关属性 - 修正版本"""
        energy_regen_percent_total = 0.0

        # 能量回复只有主属性且是百分比加成
        for gear in gear_data:
            main_attr = gear.get("main_attr")
            if main_attr and main_attr.get("name") == "ENERGY_REGEN":
                energy_regen_percent_total += main_attr.get("value", 0)

        # 能量回复加成 = 基础能量回复 * (1 + 百分比加成)
        final_energy_regen = base_energy_regen * (1 + energy_regen_percent_total)

        return {
            "base_energy_regen": base_energy_regen,
            "final_energy_regen": final_energy_regen,
            "energy_regen_percent": energy_regen_percent_total,
            "energy_regen_added": final_energy_regen - base_energy_regen
        }

    def calculate_element_damage_stats(self, gear_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算元素伤害加成 - 修正版本"""
        element_damage = {
            "PHYSICAL_DMG": 0.0,
            "FIRE_DMG": 0.0,
            "ICE_DMG": 0.0,
            "ELECTRIC_DMG": 0.0,
            "ETHER_DMG": 0.0
        }

        for gear in gear_data:
            # 主属性
            main_attr = gear.get("main_attr")
            if main_attr:
                attr_name = main_attr.get("name")
                value = main_attr.get("value", 0)
                if attr_name in element_damage:
                    element_damage[attr_name] += value

        return element_damage

    def calculate_all_stats(self, gear_data: List[Dict[str, Any]],
                          base_hp: float, base_atk: float, base_def: float,
                          impact: int, base_crit_rate: float, base_crit_dmg: float,
                          anomaly_mastery: int, anomaly_proficiency: int,
                          penetration: float, energy_regen: int) -> CalculationResult:
        """计算所有属性"""
        # 确保基础值有效
        base_hp = max(1.0, base_hp)
        base_atk = max(1.0, base_atk)
        base_def = max(1.0, base_def)
        impact = max(0, impact)
        base_crit_rate = max(0.0, base_crit_rate)
        base_crit_dmg = max(0.0, base_crit_dmg)
        anomaly_mastery = max(0, anomaly_mastery)
        anomaly_proficiency = max(0, anomaly_proficiency)
        penetration = max(0.0, penetration)
        energy_regen = max(0, energy_regen)

        # 计算各项属性
        hp_result = self.calculate_hp_stats(base_hp, gear_data)
        atk_result = self.calculate_atk_stats(base_atk, gear_data)
        def_result = self.calculate_def_stats(base_def, gear_data)
        crit_result = self.calculate_crit_stats(base_crit_rate, base_crit_dmg, gear_data)
        impact_result = self.calculate_impact_stats(impact, gear_data)
        penetration_result = self.calculate_penetration_stats(penetration, gear_data)
        anomaly_result = self.calculate_anomaly_stats(anomaly_mastery, anomaly_proficiency, gear_data)
        energy_regen_result = self.calculate_energy_regen_stats(energy_regen, gear_data)
        element_damage_result = self.calculate_element_damage_stats(gear_data)

        return CalculationResult(
            hp=hp_result,
            atk=atk_result,
            def_stat=def_result,
            crit=crit_result,
            impact=impact_result,
            penetration=penetration_result,
            anomaly=anomaly_result,
            energy_regen=energy_regen_result,
            element_damage=element_damage_result
        )