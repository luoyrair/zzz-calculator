# src/core/calculator.py
from dataclasses import fields
from typing import List, Optional, Dict

from src.models.attributes import GearAttributeValueType
from src.models.character_attributes import CharacterAttributes
from src.models.base_stats import BaseStats, FinalCharacterStats
from src.models.gear_models import GearPiece, GearSetSelection, GearSetEffect


class GearCalculator:
    """驱动盘属性计算器"""

    def __init__(self):
        self.gear_set_manager: Optional['GearSetManager'] = None

    def set_gear_set_manager(self, gear_set_manager: 'GearSetManager'):
        """设置套装效果管理器"""
        self.gear_set_manager = gear_set_manager

    def calculate_gear_bonuses(self, gear_pieces: List[GearPiece],
                               set_selection: GearSetSelection,
                               base_stats: CharacterAttributes, character_level) -> BaseStats:
        """计算驱动盘提供的所有加成 - 统一属性分类"""
        total_bonus = BaseStats()

        # 调试：输出接收到的驱动盘数据
        print(f"\n[GearCalculator] 接收到 {len(gear_pieces)} 个驱动盘")
        for i, gear_piece in enumerate(gear_pieces):
            print(f"[GearCalculator] 驱动盘 {i + 1} (槽位{gear_piece.slot_index}):")
            if gear_piece.main_attribute:
                print(f"主属性: {gear_piece.main_attribute.name}, 等级: {gear_piece.level}")
            print(f"副属性数量: {len(gear_piece.sub_attributes)}")
            for j, sub_attr in enumerate(gear_piece.sub_attributes):
                print(
                    f"副属性{j + 1}: {sub_attr.name}, 强化等级: {sub_attr.enhancement_level}, 计算值: {sub_attr.calculate_value_at_enhancement_level()}")

        # 计算单个驱动盘加成
        for gear_piece in gear_pieces:
            print(f'驱动盘槽位：{gear_piece.slot_index}')
            self._add_gear_piece_bonus(total_bonus, gear_piece, base_stats, character_level)

        # 计算套装效果
        if self.gear_set_manager:
            set_bonus = self.gear_set_manager.get_set_bonuses(set_selection)
            # 套装效果需要正确分类
            self._apply_set_bonuses(total_bonus, set_bonus, base_stats)

        return total_bonus

    def _add_gear_piece_bonus(self, total_bonus: BaseStats, gear_piece: GearPiece,
                              base_stats: CharacterAttributes, character_level):
        """添加单个驱动盘的加成"""
        # 主属性加成
        if gear_piece.main_attribute:
            self._add_attribute_bonus(total_bonus, gear_piece.main_attribute, base_stats, character_level)

        # 副属性加成
        for sub_attr in gear_piece.sub_attributes:
            if sub_attr:
                self._add_attribute_bonus(total_bonus, sub_attr, base_stats)

    def _add_attribute_bonus(self, total_bonus: BaseStats, attr, base_stats: CharacterAttributes, level=None):
        """统一处理属性加成 - 修复后的版本"""
        attr_type = attr.attribute_type.value
        value_type = attr.attribute_value_type

        # 根据是否有level参数决定计算方式
        if level is not None:
            value = attr.calculate_value_at_level(level)
            print(f"驱动盘等级: {level}")
        else:
            value = attr.calculate_value_at_enhancement_level()

        print(f"[Calculator] 处理属性: {attr.name}, 类型={attr_type}, 值类型={value_type}, 值={value}")

        # 统一属性分类处理
        if self._is_direct_percentage_attr(attr_type, value_type):
            # 直接百分比属性：暴击率、暴击伤害、穿透率
            # 这些值已经是百分比（如0.06表示6%），直接相加
            if hasattr(total_bonus, attr_type):
                current = getattr(total_bonus, attr_type)
                setattr(total_bonus, attr_type, current + value)
                print(f"[Calculator] 直接百分比加成 {attr_type}: {current:.2%} + {value:.2%} = {current + value:.2%}")

        elif self._is_base_percentage_attr(attr_type, value_type):
            # 基于基础属性的百分比：HP%、ATK%、DEF%、异常精通、穿透力
            # 需要乘以基础值
            if hasattr(base_stats, attr_type):
                base_value = getattr(base_stats, attr_type)
                bonus_value = base_value * value

                if hasattr(total_bonus, attr_type):
                    current = getattr(total_bonus, attr_type)
                    setattr(total_bonus, attr_type, current + bonus_value)
                    print(
                        f"[Calculator] 基于基础属性百分比加成 {attr_type}: {base_value:.0f} * {value:.2%} = +{bonus_value:.0f}")
            else:
                print(f"[Calculator] 警告: 基础属性没有 {attr_type} 字段")

        elif self._is_fixed_value_attr(value_type):
            # 固定值属性：直接相加
            if hasattr(total_bonus, attr_type):
                current = getattr(total_bonus, attr_type)
                setattr(total_bonus, attr_type, current + value)
                print(f"[Calculator] 固定值加成 {attr_type}: +{value:.0f} = {current + value:.0f}")

        elif self._is_damage_bonus_attr(value_type):
            # 伤害加成属性：直接百分比相加
            if hasattr(total_bonus, attr_type):
                current = getattr(total_bonus, attr_type)
                setattr(total_bonus, attr_type, current + value)
                print(f"[Calculator] 伤害加成 {attr_type}: {current:.2%} + {value:.2%} = {current + value:.2%}")

        else:
            print(f"[Calculator] 未处理的属性类型: {attr_type}, 值类型: {value_type}")

    def _is_direct_percentage_attr(self, attr_type: str, value_type) -> bool:
        """判断是否为直接百分比属性"""
        direct_percentage_attrs = ["crit_rate", "crit_dmg", "pen_ratio", "energy_regen"]

        # 这些属性无论值类型如何，都应该作为直接百分比处理
        if attr_type in direct_percentage_attrs:
            return True

        # 或者值类型是RATE_PERCENTAGE
        return value_type == GearAttributeValueType.RATE_PERCENTAGE

    def _is_base_percentage_attr(self, attr_type: str, value_type) -> bool:
        """判断是否为基于基础属性的百分比"""
        base_percentage_attrs = ["hp", "attack", "defence", "impact", "anomaly_mastery", "pen"]

        if attr_type in base_percentage_attrs and value_type == GearAttributeValueType.PERCENTAGE:
            return True

        return False

    def _is_fixed_value_attr(self, value_type) -> bool:
        """判断是否为固定值属性"""
        return value_type == GearAttributeValueType.NUMERIC_VALUE

    def _is_damage_bonus_attr(self, value_type) -> bool:
        """判断是否为伤害加成属性"""
        return value_type == GearAttributeValueType.DMG_BONUS_PERCENTAGE

    def _apply_set_bonuses(self, total_bonus: BaseStats, set_bonus: BaseStats,
                           base_stats: CharacterAttributes):
        """应用套装效果的加成"""
        print(f"[Calculator] 应用套装加成")

        # 应用所有套装加成属性
        for field_name in [f.name for f in fields(BaseStats)]:
            if hasattr(set_bonus, field_name):
                bonus_value = getattr(set_bonus, field_name)

                if bonus_value != 0:
                    # 根据属性类型应用正确的加成
                    if self._is_set_direct_percentage_attr(field_name):
                        # 直接百分比属性
                        if hasattr(total_bonus, field_name):
                            current = getattr(total_bonus, field_name)
                            setattr(total_bonus, field_name, current + bonus_value)
                            print(
                                f"[Calculator] 套装直接百分比加成 {field_name}: {current:.2%} + {bonus_value:.2%} = {current + bonus_value:.2%}")

                    elif self._is_set_base_percentage_attr(field_name):
                        # 基于基础属性的百分比
                        if hasattr(base_stats, field_name):
                            base_value = getattr(base_stats, field_name)
                            actual_bonus = base_value * bonus_value

                            if hasattr(total_bonus, field_name):
                                current = getattr(total_bonus, field_name)
                                setattr(total_bonus, field_name, current + actual_bonus)
                                print(
                                    f"[Calculator] 套装基于基础属性加成 {field_name}: {base_value:.0f} * {bonus_value:.2%} = +{actual_bonus:.0f}")

                    else:
                        # 固定值属性
                        if hasattr(total_bonus, field_name):
                            current = getattr(total_bonus, field_name)
                            setattr(total_bonus, field_name, current + bonus_value)
                            print(
                                f"[Calculator] 套装固定值加成 {field_name}: +{bonus_value:.0f} = {current + bonus_value:.0f}")

    def _is_set_direct_percentage_attr(self, field_name: str) -> bool:
        """判断套装加成中的直接百分比属性"""
        direct_percentage_attrs = ["crit_rate", "crit_dmg", "pen_ratio", "energy_regen",
                                   "physical_dmg_bonus", "fire_dmg_bonus", "ice_dmg_bonus",
                                   "electric_dmg_bonus", "ether_dmg_bonus"]
        return field_name in direct_percentage_attrs

    def _is_set_base_percentage_attr(self, field_name: str) -> bool:
        """判断套装加成中的基础百分比属性"""
        base_percentage_attrs = ["hp", "attack", "defence", "impact", "anomaly_mastery"]
        return field_name in base_percentage_attrs

    def calculate_final_stats(self, base_stats: CharacterAttributes,
                              gear_bonuses: BaseStats) -> FinalCharacterStats:
        """计算最终属性"""
        # 创建最终属性对象
        final_stats = FinalCharacterStats()

        # 复制基础属性
        for field_name in [f.name for f in fields(base_stats)]:
            if field_name == 'gear_bonuses':
                continue
            if hasattr(base_stats, field_name) and hasattr(final_stats, field_name):
                value = getattr(base_stats, field_name)
                setattr(final_stats, field_name, value)

        # 设置装备加成
        final_stats.gear_bonuses = gear_bonuses

        # 应用装备加成
        final_stats.apply_gear_bonuses()

        return final_stats

    def calculate_complete_stats(self, base_stats: CharacterAttributes,
                                 gear_pieces: List[GearPiece],
                                 set_selection: GearSetSelection, level) -> FinalCharacterStats:
        """完整的属性计算流程"""
        print(f"\n[Calculator] 开始完整属性计算")
        print(f"[Calculator] 基础属性: HP={base_stats.hp}, ATK={base_stats.attack}, DEF={base_stats.defence}")

        # 1. 计算驱动盘加成
        gear_bonuses = self.calculate_gear_bonuses(gear_pieces, set_selection, base_stats, level)

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