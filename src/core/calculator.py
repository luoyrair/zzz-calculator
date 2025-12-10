# src/core/calculator.py
"""驱动盘属性计算器 - 完全适配新架构"""
from dataclasses import fields
from typing import List, Optional, Dict

from src.core.models.character import CharacterBaseStats, FinalCharacterStats, BaseStats
from src.core.models.gear import GearPiece, GearSetSelection, GearSetEffect


class GearCalculator:
    """驱动盘属性计算器 - 新架构"""

    def __init__(self, gear_config):
        self.gear_config = gear_config
        self.gear_set_manager: Optional['GearSetManager'] = None
        self.cache: Dict[str, BaseStats] = {}

    def set_gear_set_manager(self, gear_set_manager: 'GearSetManager'):
        """设置套装效果管理器"""
        self.gear_set_manager = gear_set_manager

    def calculate_gear_bonuses(self, gear_pieces: List[GearPiece],
                               set_selection: GearSetSelection,
                               base_stats: CharacterBaseStats) -> BaseStats:
        """计算驱动盘提供的所有加成 - 修复百分比加成"""
        total_bonus = BaseStats()

        print(
            f"[Calculator] 计算装备加成，基础属性: HP={base_stats.HP:.0f}, ATK={base_stats.ATK:.0f}, DEF={base_stats.DEF:.0f}")

        # 计算单个驱动盘加成
        for gear_piece in gear_pieces:
            self._add_gear_piece_bonus(total_bonus, gear_piece, base_stats)

        # 计算套装效果
        if self.gear_set_manager:
            set_bonus = self.gear_set_manager.get_set_bonuses(set_selection)
            # 套装效果需要基于基础属性计算百分比加成
            self._apply_percentage_bonuses(total_bonus, set_bonus, base_stats)

        print(
            f"[Calculator] 总计装备加成: HP={total_bonus.HP:.0f}, ATK={total_bonus.ATK:.0f}, DEF={total_bonus.DEF:.0f}")
        return total_bonus

    def _add_gear_piece_bonus(self, total_bonus: BaseStats, gear_piece: GearPiece,
                              base_stats: CharacterBaseStats):
        """添加单个驱动盘的加成 - 修复百分比加成"""
        # 主属性加成
        if gear_piece.main_gear_key and gear_piece.main_value > 0:
            self._add_attribute_bonus(total_bonus, gear_piece.main_gear_key,
                                      gear_piece.main_value, base_stats)

        # 副属性加成
        for sub_attr in gear_piece.sub_attributes:
            if sub_attr.gear_key and sub_attr.value > 0:
                self._add_attribute_bonus(total_bonus, sub_attr.gear_key,
                                          sub_attr.value, base_stats)

    def _add_attribute_bonus(self, total_bonus: BaseStats, gear_key: str,
                             value: float, base_stats: CharacterBaseStats):
        """添加单个属性加成 - 修复百分比加成"""
        # 获取属性配置
        gear_attr = self.gear_config.attribute_config.get_gear_attribute(gear_key)
        if not gear_attr:
            print(f"[Calculator] 警告: 未找到属性配置: {gear_key}")
            return

        attr_type = gear_attr.get("attribute_type")
        value_type = gear_attr.get("value_type", "")

        print(f"[Calculator] 处理属性: {gear_key}, 类型={attr_type}, 值类型={value_type}, 原始值={value}")

        # 根据值类型处理加成
        if value_type in ["PERCENTAGE", "RATE_PERCENTAGE", "DMG_BONUS_PERCENTAGE"]:
            # 百分比加成：需要基于基础属性计算
            self._apply_percentage_bonus(total_bonus, attr_type, value, value_type, base_stats)
        else:
            # 固定值加成：直接添加
            self._apply_fixed_bonus(total_bonus, attr_type, value)

    def _apply_percentage_bonus(self, total_bonus: BaseStats, attr_type: str,
                                percentage: float, value_type: str, base_stats: CharacterBaseStats):
        """应用百分比加成 - 修复直接百分比加成"""
        print(f"[Calculator] 应用百分比加成: {attr_type}, 百分比={percentage:.4f}, 类型={value_type}")

        # 直接百分比属性（如暴击率、暴击伤害、穿透率、能量回复）
        direct_percentage_attrs = ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio", "Energy_Regen"]

        if attr_type in direct_percentage_attrs:
            # 直接加百分比值
            if hasattr(total_bonus, attr_type):
                current = getattr(total_bonus, attr_type)
                setattr(total_bonus, attr_type, current + percentage)
                print(
                    f"[Calculator] 直接百分比加成 {attr_type}: {current:.2%} + {percentage:.2%} = {current + percentage:.2%}")
            return

        # 基于基础属性的百分比加成
        attr_mapping = {
            "HP": "HP",
            "ATK": "ATK",
            "DEF": "DEF",
            "Impact": "Impact",
            "Anomaly_Mastery": "Anomaly_Mastery",
            "Anomaly_Proficiency": "Anomaly_Proficiency",
        }

        if attr_type in attr_mapping:
            attr_name = attr_mapping[attr_type]

            if hasattr(base_stats, attr_name):
                base_value = getattr(base_stats, attr_name)
                bonus_value = base_value * percentage

                if hasattr(total_bonus, attr_name):
                    current = getattr(total_bonus, attr_name)
                    setattr(total_bonus, attr_name, current + bonus_value)
                    print(
                        f"[Calculator] 基于基础属性百分比加成 {attr_name}: {base_value:.0f} * {percentage:.2%} = +{bonus_value:.0f}")
            else:
                print(f"[Calculator] 警告: 基础属性没有 {attr_name} 字段")

        elif attr_type in ["Physical_DMG_Bonus", "Fire_DMG_Bonus", "Ice_DMG_Bonus",
                           "Electric_DMG_Bonus", "Ether_DMG_Bonus"]:
            # 伤害加成属性暂时不添加到BaseStats
            print(f"[Calculator] 跳过伤害加成属性: {attr_type} ({percentage:.2%})")

    def _apply_fixed_bonus(self, total_bonus: BaseStats, attr_type: str, value: float):
        """应用固定值加成"""
        attr_mapping = {
            "HP": "HP",
            "ATK": "ATK",
            "DEF": "DEF",
            "Anomaly_Proficiency": "Anomaly_Proficiency",
            "PEN": "PEN",
        }

        if attr_type in attr_mapping:
            attr_name = attr_mapping[attr_type]
            if hasattr(total_bonus, attr_name):
                current = getattr(total_bonus, attr_name)
                setattr(total_bonus, attr_name, current + value)
                print(f"[Calculator] 固定值加成 {attr_name}: +{value:.0f} = {current + value:.0f}")

    def _apply_percentage_bonuses(self, total_bonus: BaseStats, set_bonus: BaseStats,
                                  base_stats: CharacterBaseStats):
        """应用套装效果的百分比加成"""
        print(f"[Calculator] 应用套装百分比加成")

        # 直接百分比属性
        direct_percentage_attrs = ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio", "Energy_Regen"]

        for attr_name in direct_percentage_attrs:
            if hasattr(set_bonus, attr_name):
                percentage = getattr(set_bonus, attr_name)
                if percentage != 0:
                    if hasattr(total_bonus, attr_name):
                        current = getattr(total_bonus, attr_name)
                        setattr(total_bonus, attr_name, current + percentage)
                        print(
                            f"[Calculator] 套装直接百分比加成 {attr_name}: {current:.2%} + {percentage:.2%} = {current + percentage:.2%}")

        # 基于基础属性的百分比属性
        base_percentage_attrs = ["HP", "ATK", "DEF", "Impact", "Anomaly_Mastery"]

        for attr_name in base_percentage_attrs:
            if hasattr(set_bonus, attr_name):
                percentage = getattr(set_bonus, attr_name)
                if percentage != 0 and hasattr(base_stats, attr_name):
                    base_value = getattr(base_stats, attr_name)
                    bonus_value = base_value * percentage

                    if hasattr(total_bonus, attr_name):
                        current = getattr(total_bonus, attr_name)
                        setattr(total_bonus, attr_name, current + bonus_value)
                        print(
                            f"[Calculator] 套装基于基础属性加成 {attr_name}: {base_value:.0f} * {percentage:.2%} = +{bonus_value:.0f}")

    def calculate_final_stats(self, base_stats: CharacterBaseStats,
                              gear_bonuses: BaseStats) -> FinalCharacterStats:
        """计算最终属性"""
        # 创建最终属性对象
        final_stats = FinalCharacterStats()

        # 复制基础属性
        for field_name in [f.name for f in fields(CharacterBaseStats)]:
            if field_name == 'gear_bonuses':
                continue
            if hasattr(base_stats, field_name) and hasattr(final_stats, field_name):
                value = getattr(base_stats, field_name)
                setattr(final_stats, field_name, value)

        # 设置装备加成
        final_stats.gear_bonuses = gear_bonuses

        # 应用装备加成
        final_stats.apply_gear_bonuses()

        print(f"[Calculator] 最终属性计算完成:")
        print(f"  基础HP: {base_stats.HP:.0f}, 加成HP: {gear_bonuses.HP:.0f}, 最终HP: {final_stats.HP:.0f}")
        print(f"  基础ATK: {base_stats.ATK:.0f}, 加成ATK: {gear_bonuses.ATK:.0f}, 最终ATK: {final_stats.ATK:.0f}")

        return final_stats

    def calculate_complete_stats(self, base_stats: CharacterBaseStats,
                                 gear_pieces: List[GearPiece],
                                 set_selection: GearSetSelection) -> FinalCharacterStats:
        """完整的属性计算流程"""
        print(f"\n[Calculator] 开始完整属性计算")
        print(f"[Calculator] 基础属性: HP={base_stats.HP:.0f}, ATK={base_stats.ATK:.0f}, DEF={base_stats.DEF:.0f}")

        # 1. 计算驱动盘加成
        gear_bonuses = self.calculate_gear_bonuses(gear_pieces, set_selection, base_stats)

        # 2. 计算最终属性
        final_stats = self.calculate_final_stats(base_stats, gear_bonuses)
        return final_stats


class GearSetManager:
    """套装效果管理器"""

    def __init__(self, equipment_data: dict):
        self.equipment_data = equipment_data
        self.set_effects: Dict[int, GearSetEffect] = {}
        self._load_set_effects()

    def _load_set_effects(self):
        """从JSON数据加载所有套装效果"""
        for set_id_str, data in self.equipment_data.items():
            try:
                set_id = int(set_id_str)
                effect = GearSetEffect.from_json_data(set_id, data)
                self.set_effects[set_id] = effect
            except (ValueError, KeyError):
                continue

    def get_set_bonuses(self, selection: GearSetSelection) -> BaseStats:
        """根据用户选择的套装组合获取加成"""
        bonuses = BaseStats()

        if not selection.set_ids:
            return bonuses

        if selection.combination_type == "4+2":
            # 4+2组合：一个4件套 + 一个2件套
            if len(selection.set_ids) >= 1:
                set1 = self.set_effects.get(selection.set_ids[0])
                if set1:
                    bonuses.merge(set1.two_piece_bonus)
                    bonuses.merge(set1.four_piece_bonus)

            if len(selection.set_ids) >= 2:
                set2 = self.set_effects.get(selection.set_ids[1])
                if set2:
                    bonuses.merge(set2.two_piece_bonus)

        elif selection.combination_type == "2+2+2":
            # 2+2+2组合：三个2件套
            for set_id in selection.set_ids:
                set_effect = self.set_effects.get(set_id)
                if set_effect:
                    bonuses.merge(set_effect.two_piece_bonus)

        return bonuses

    def get_available_sets(self) -> List[Dict[str, any]]:
        """获取所有可用的套装"""
        return [
            {
                "id": set_id,
                "name": effect.name,
                "desc2": effect.desc2,
                "bonus_display": self._get_bonus_display(effect)
            }
            for set_id, effect in sorted(self.set_effects.items())
        ]

    def _get_bonus_display(self, effect: GearSetEffect) -> str:
        """获取加成显示信息"""
        bonuses = []
        for field_name in [f.name for f in fields(BaseStats)]:
            value = getattr(effect.two_piece_bonus, field_name, 0)
            if value != 0:
                if field_name in ['CRIT_Rate', 'CRIT_DMG', 'PEN_Ratio',
                                  'Energy_Regen', 'Automatic_Adrenaline_Accumulation']:
                    bonuses.append(f"{field_name}+{value * 100:.0f}%")
                else:
                    bonuses.append(f"{field_name}+{value}")

        return ", ".join(bonuses) if bonuses else "无基础属性加成"
