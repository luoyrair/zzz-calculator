from typing import List, Optional
from src.data.manager import data_manager
from src.models.character_attributes import CharacterAttributesModel
from src.models.gear_models import GearPiece, GearSetSelection
from src.calculators.character_calculator import CharacterAttributeCalculator
from src.calculators.gear_calculator import GearCalculator, GearSetManager
from src.parsers.weapon_parsers import WeaponConverter


class CalculationService:
    """计算服务 - 负责所有计算逻辑"""

    def __init__(self):
        self.character_calculator = CharacterAttributeCalculator()
        self.gear_calculator = GearCalculator()
        self.gear_set_manager: Optional[GearSetManager] = None

        # 初始化装备套装管理器
        self._init_gear_set_manager()

    def _init_gear_set_manager(self):
        """初始化装备套装管理器"""
        try:
            from src.config.manager import config_manager
            import json

            equipment_file = config_manager.file.equipment_file
            if equipment_file.exists():
                with open(equipment_file, 'r', encoding='utf-8') as f:
                    equipment_data = json.load(f)

                self.gear_set_manager = GearSetManager(equipment_data)
                self.gear_calculator.set_gear_set_manager(self.gear_set_manager)
        except Exception as e:
            print(f"初始化装备套装管理器失败: {e}")

    def calculate_character_base_stats(
            self,
            character_id: int,
            level: int,
            breakthrough_level: int,
            core_passive_level: int
    ) -> Optional[CharacterAttributesModel]:
        """计算角色基础属性"""
        character = data_manager.get_character(character_id)
        if not character or not character.file_path.exists():
            return None

        return self.character_calculator.calculate_character_attributes(
            str(character.file_path),
            level,
            breakthrough_level,
            core_passive_level
        )

    def calculate_character_with_weapon(
            self,
            character_id: int,
            character_level: int,
            breakthrough_level: int,
            core_passive_level: int,
            weapon_id: int,
            weapon_level: int
    ) -> Optional[CharacterAttributesModel]:
        """计算带音擎的角色属性"""
        # 计算基础属性
        base_stats = self.calculate_character_base_stats(
            character_id, character_level, breakthrough_level, core_passive_level
        )

        if not base_stats:
            return None

        # 应用音擎加成
        weapon = data_manager.get_weapon(weapon_id)
        if not weapon or not weapon.file_path.exists():
            return base_stats

        try:
            weapon_schema = WeaponConverter.load_from_file(weapon.file_path)
            weapon_schema.apply_to_character(base_stats, weapon_level)
            return base_stats
        except Exception as e:
            print(f"应用音擎失败: {e}")
            return base_stats

    def calculate_final_stats(
            self,
            base_stats: CharacterAttributesModel,
            gear_pieces: List[GearPiece],
            gear_set_selection: GearSetSelection,
            gear_enhance_level: int
    ):
        """计算最终属性（包含驱动盘）"""
        return self.gear_calculator.calculate_complete_stats(
            base_stats,
            gear_pieces,
            gear_set_selection,
            gear_enhance_level
        )

    def get_breakthrough_level(self, character_level: int) -> int:
        """根据等级计算突破阶段"""
        if character_level <= 10:
            return 1
        elif character_level <= 20:
            return 2
        elif character_level <= 30:
            return 3
        elif character_level <= 40:
            return 4
        elif character_level <= 50:
            return 5
        else:
            return 6


# 创建全局计算服务实例
calculation_service = CalculationService()