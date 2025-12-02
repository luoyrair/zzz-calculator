# src/core/calculator.py
"""驱动盘属性计算器 - 完全适配新架构"""
from dataclasses import fields
from typing import List, Optional

from src.core.attribute_calculator import AttributeCalculator
from src.core.character_models import BaseCharacterStats, FinalCharacterStats
from src.core.gear_models import GearPiece, GearBonuses, GearSetSelection, GearSetManager


class GearCalculator:
    """驱动盘属性计算器 - 新架构"""

    def __init__(self, gear_config):
        self.gear_config = gear_config
        self.gear_set_manager: Optional[GearSetManager] = None
        self.attribute_calculator: Optional[AttributeCalculator] = AttributeCalculator(self.gear_config)

        print(f"[DEBUG] GearCalculator 初始化完成")  # 新增调试
        print(f"[DEBUG] gear_set_manager: {self.gear_set_manager}")  # 新增调试
        print(f"[DEBUG] attribute_calculator: {self.attribute_calculator}")  # 新增调试

    def set_gear_set_manager(self, gear_set_manager: GearSetManager):
        """设置套装效果管理器"""
        self.gear_set_manager = gear_set_manager

    def calculate_main_attribute(self, attr_name: str, level: int) -> float:
        """计算主属性值"""
        # 使用配置中的属性映射
        mapped_attr_name = self.gear_config.attribute_config.get_character_data_key(attr_name)

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

    def calculate_gear_bonuses(self, gear_pieces: List[GearPiece],
                               set_selection: GearSetSelection,
                               base_stats: BaseCharacterStats) -> GearBonuses:
        """计算驱动盘提供的所有加成"""
        print(f"[DEBUG] calculate_gear_bonuses 被调用")
        print(f"[DEBUG] gear_pieces 数量: {len(gear_pieces)}")

        # 确保 attribute_calculator 存在
        if not self.attribute_calculator:
            print(f"[ERROR] attribute_calculator 未初始化！")
            self.attribute_calculator = AttributeCalculator(self.gear_config)

        gear_bonuses = GearBonuses(self.attribute_calculator)
        print(f"[DEBUG] 创建 GearBonuses 实例")

        # 【关键修复】：无论有没有 gear_set_manager，都要计算单个驱动盘属性
        # 先计算单个驱动盘的属性加成
        print(f"[DEBUG] 开始计算单个驱动盘属性加成")
        gear_bonuses.calculate_individual_pieces(gear_pieces, base_stats)

        # 然后计算套装效果（如果有）
        if self.gear_set_manager:
            print(f"[DEBUG] 调用 calculate_set_bonuses")
            set_bonuses = self.gear_set_manager.get_set_bonuses(set_selection)
            gear_bonuses.merge(set_bonuses)
        else:
            print(f"[WARNING] gear_set_manager 未设置，跳过套装效果计算")

        print(f"[DEBUG] 计算完成，总加成 HP: {gear_bonuses.HP}, ATK: {gear_bonuses.ATK}")
        return gear_bonuses

    def calculate_final_stats(self, base_stats: BaseCharacterStats,
                              gear_bonuses: GearBonuses) -> FinalCharacterStats:
        """计算最终属性 - 返回FinalCharacterStats"""
        # 创建FinalCharacterStats对象，继承基础属性
        final_stats = FinalCharacterStats()

        # 复制基础属性到最终属性
        self._copy_base_stats(base_stats, final_stats)

        # 设置装备加成
        final_stats.gear_bonuses = gear_bonuses

        # 【确保这行代码存在并执行】：应用装备加成到最终属性
        final_stats.apply_gear_bonuses()

        print(f"[DEBUG] 应用加成前 ATK: {base_stats.ATK}")
        print(f"[DEBUG] 应用加成后 ATK: {final_stats.ATK}")
        return final_stats

    def _copy_base_stats(self, source: BaseCharacterStats, target: FinalCharacterStats):
        """复制基础属性到目标对象"""
        # 获取所有字段名
        base_fields = {f.name for f in fields(BaseCharacterStats)}

        # 复制基础属性
        for field_name in base_fields:
            if hasattr(source, field_name) and hasattr(target, field_name):
                value = getattr(source, field_name)
                setattr(target, field_name, value)

    def calculate_complete_stats(self, base_stats: BaseCharacterStats,
                                 gear_pieces: List[GearPiece],
                                 set_selection: GearSetSelection) -> FinalCharacterStats:
        """完整的属性计算流程"""
        print(f"[DEBUG] 开始完整计算...")
        # 1. 计算驱动盘加成
        gear_bonuses = self.calculate_gear_bonuses(gear_pieces, set_selection, base_stats)
        print(f"[DEBUG] 计算出的总装备加成:")
        print(f"  ATK: {gear_bonuses.ATK}")
        print(f"  HP: {gear_bonuses.HP}")
        print(f"  CRIT_Rate: {gear_bonuses.CRIT_Rate}")

        # 2. 计算最终属性
        final_stats = self.calculate_final_stats(base_stats, gear_bonuses)
        return final_stats