# src/core/gear_models.py
"""驱动盘业务模型 - 专注业务逻辑和计算"""
import re
from dataclasses import dataclass, field
from typing import Dict, List

from src.core.attribute_calculator import AttributeCalculator
from src.core.character_models import BaseCharacterStats, CharacterData


@dataclass
class GearSubAttribute:
    """驱动盘副属性"""
    gear_key: str  # 使用gear_key而不是attribute_type
    value: float = 0.0
    is_locked: bool = False


@dataclass
class GearPiece:
    """单个驱动盘"""
    slot_index: int
    level: int = 0
    main_gear_key: str = ""  # 使用gear_key
    main_value: float = 0.0
    sub_attributes: List[GearSubAttribute] = field(default_factory=list)


@dataclass
class GearSetEffect:
    """驱动盘套装效果"""
    set_id: int
    name: str
    two_piece_bonus: CharacterData = field(default_factory=CharacterData)
    four_piece_bonus: CharacterData = field(default_factory=CharacterData)

    @classmethod
    def from_json_data(cls, set_id: int, json_data: dict) -> 'GearSetEffect':
        effect = cls(set_id=set_id, name=json_data["name"])
        effect.two_piece_bonus = cls._parse_set_bonus(json_data["desc2"])
        effect.four_piece_bonus = cls._parse_set_bonus(json_data["desc4"])
        return effect

    @staticmethod
    def _parse_set_bonus(desc: str) -> CharacterData:
        """解析套装效果描述"""
        bonus = CharacterData()

        # 简化的解析逻辑，实际应该更复杂
        percentage_match = re.search(r'\+(\d+)%', desc)
        if percentage_match:
            value = float(percentage_match.group(1)) / 100

            if "物理伤害" in desc:
                bonus.Physical_DMG_Bonus = value
            elif "火属性伤害" in desc:
                bonus.Fire_DMG_Bonus = value
            elif "冰属性伤害" in desc:
                bonus.Ice_DMG_Bonus = value
            elif "电属性伤害" in desc:
                bonus.Electric_DMG_Bonus = value
            elif "以太伤害" in desc:
                bonus.Ether_DMG_Bonus = value
            elif "暴击率" in desc:
                bonus.CRIT_Rate = value
            elif "暴击伤害" in desc:
                bonus.CRIT_DMG = value
            elif "穿透率" in desc:
                bonus.PEN_Ratio = value
            elif "能量回复" in desc:
                bonus.Energy_Regen = value

        return bonus


@dataclass
class GearSetSelection:
    """用户选择的套装组合"""
    combination_type: str  # "4+2" 或 "2+2+2"
    set_ids: List[int]


class GearBonuses(CharacterData):
    """驱动盘提供的所有属性加成"""

    def __init__(self, attribute_calculator: AttributeCalculator):
        super().__init__()
        self.attribute_calculator = attribute_calculator
        print(f"[DEBUG] GearBonuses 初始化，attribute_calculator: {self.attribute_calculator}")

    def calculate_from_gear_set(self, gear_pieces: List[GearPiece],
                                set_selection: GearSetSelection,
                                set_manager: 'GearSetManager',
                                base_stats: BaseCharacterStats):
        """计算驱动盘加成（兼容旧版本）"""
        self.reset()

        # 计算单个驱动盘加成
        self.calculate_individual_pieces(gear_pieces, base_stats)

        # 计算套装效果
        set_bonuses = set_manager.get_set_bonuses(set_selection)
        self.merge(set_bonuses)

    def calculate_individual_pieces(self, gear_pieces: List[GearPiece], base_stats: BaseCharacterStats):
        """计算单个驱动盘的属性加成（不含套装效果）"""
        print(f"[DEBUG] GearBonuses.calculate_individual_pieces 开始")

        for gear_piece in gear_pieces:
            print(f"[DEBUG] 处理槽位 {gear_piece.slot_index}")
            self._add_gear_piece_bonuses(gear_piece, base_stats)

        print(f"[DEBUG] 单个驱动盘计算完成: HP={self.HP}, ATK={self.ATK}")

    def _add_gear_piece_bonuses(self, gear_piece: GearPiece, base_stats: BaseCharacterStats):
        """添加单个驱动盘的加成"""
        print(f"[DEBUG] _add_gear_piece_bonuses: 处理槽位{gear_piece.slot_index}")
        # 主属性加成
        if gear_piece.main_gear_key and gear_piece.main_value > 0:
            print(f"[DEBUG]  主属性: {gear_piece.main_gear_key}={gear_piece.main_value}")
            main_bonus = self.attribute_calculator.calculate_gear_attribute_contribution(
                gear_piece.main_gear_key, gear_piece.main_value, base_stats
            )
            print(f"[DEBUG]  主属性加成结果: HP={main_bonus.HP}, ATK={main_bonus.ATK}")
            self.merge(main_bonus)
            print(f"[DEBUG]  合并后总加成: HP={self.HP}, ATK={self.ATK}")

        # 副属性加成
        for sub_attr in gear_piece.sub_attributes:
            if sub_attr.gear_key and sub_attr.value > 0:
                sub_bonus = self.attribute_calculator.calculate_gear_attribute_contribution(
                    sub_attr.gear_key, sub_attr.value, base_stats
                )
                self.merge(sub_bonus)


class GearSetManager:
    """套装效果管理器"""

    def __init__(self, equipment_data: dict):
        self.equipment_data = equipment_data
        self.set_effects: Dict[int, GearSetEffect] = {}
        self._load_set_effects()

    def _load_set_effects(self):
        """从JSON数据加载所有套装效果"""
        for set_id, data in self.equipment_data.items():
            self.set_effects[int(set_id)] = GearSetEffect.from_json_data(int(set_id), data)

    def get_set_bonuses(self, selection: GearSetSelection) -> CharacterData:
        """根据用户选择的套装组合获取加成"""
        bonuses = CharacterData()

        if selection.combination_type == "4+2":
            set1 = self.set_effects.get(selection.set_ids[0])
            set2 = self.set_effects.get(selection.set_ids[1])

            if set1:
                bonuses.merge(set1.four_piece_bonus)
                bonuses.merge(set1.two_piece_bonus)
            if set2:
                bonuses.merge(set2.two_piece_bonus)

        elif selection.combination_type == "2+2+2":
            for set_id in selection.set_ids:
                set_effect = self.set_effects.get(set_id)
                if set_effect:
                    bonuses.merge(set_effect.two_piece_bonus)

        return bonuses