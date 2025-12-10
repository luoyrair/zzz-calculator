# src/core/models/gear.py
"""驱动盘业务模型 - 完整实现"""
import re
from dataclasses import dataclass, field
from typing import List

from .character import BaseStats


@dataclass
class GearSubAttribute:
    """驱动盘副属性"""
    gear_key: str
    value: float = 0.0
    is_locked: bool = False


@dataclass
class GearPiece:
    """单个驱动盘"""
    slot_index: int
    level: int = 0
    main_gear_key: str = ""
    main_value: float = 0.0
    sub_attributes: List[GearSubAttribute] = field(default_factory=list)

    def __post_init__(self):
        """确保列表不为空"""
        if self.sub_attributes is None:
            self.sub_attributes = []


@dataclass
class GearSetEffect:
    """驱动盘套装效果"""
    set_id: int
    name: str
    desc2: str = ""
    desc4: str = ""
    two_piece_bonus: BaseStats = field(default_factory=BaseStats)
    four_piece_bonus: BaseStats = field(default_factory=BaseStats)

    def __post_init__(self):
        """初始化时解析效果"""
        if not self.two_piece_bonus:
            self.two_piece_bonus = BaseStats()
        if not self.four_piece_bonus:
            self.four_piece_bonus = BaseStats()
        self._parse_two_piece_bonus()

    @classmethod
    def from_json_data(cls, set_id: int, json_data: dict) -> 'GearSetEffect':
        """从JSON数据创建套装效果"""
        return cls(
            set_id=set_id,
            name=json_data.get("name", ""),
            desc2=json_data.get("desc2", ""),
            desc4=json_data.get("desc4", "")
        )

    def _parse_two_piece_bonus(self):
        """解析二件套效果中的基础属性加成"""
        if not self.desc2:
            return

        desc = self.desc2
        print(f"[GearSet] 解析套装效果: {desc}")

        # 百分比加成解析
        attribute_rules = [
            (r'攻击力\+(\d+)%', 'ATK', True, 0.01),  # 除以100
            (r'生命值\+(\d+)%', 'HP', True, 0.01),
            (r'防御力\+(\d+)%', 'DEF', True, 0.01),
            (r'暴击率\+(\d+)%', 'CRIT_Rate', True, 0.01),
            (r'暴击伤害\+(\d+)%', 'CRIT_DMG', True, 0.01),
            (r'物理伤害\+(\d+)%', 'Physical_DMG_Bonus', True, 0.01),
            (r'火属性伤害\+(\d+)%', 'Fire_DMG_Bonus', True, 0.01),
            (r'冰属性伤害\+(\d+)%', 'Ice_DMG_Bonus', True, 0.01),
            (r'电属性伤害\+(\d+)%', 'Electric_DMG_Bonus', True, 0.01),
            (r'以太伤害\+(\d+)%', 'Ether_DMG_Bonus', True, 0.01),
            (r'异常精通\+(\d+)点', 'Anomaly_Proficiency', False, 1),  # 固定值
            (r'异常掌控\+(\d+)%', 'Anomaly_Mastery', True, 0.01),
            (r'穿透率\+(\d+)%', 'PEN_Ratio', True, 0.01),
            (r'能量自动回复\+(\d+)%', 'Energy_Regen', True, 0.01),
            (r'冲击力\+(\d+)%', 'Impact', True, 0.01),
        ]

        for pattern, attr_name, is_percentage, factor in attribute_rules:
            match = re.search(pattern, desc)
            if match:
                try:
                    value = float(match.group(1)) * factor

                    # 确保属性存在
                    if hasattr(self.two_piece_bonus, attr_name):
                        current = getattr(self.two_piece_bonus, attr_name)
                        setattr(self.two_piece_bonus, attr_name, current + value)

                        if is_percentage:
                            print(f"[GearSet] 套装加成: {attr_name} + {value:.2%}")
                        else:
                            print(f"[GearSet] 套装加成: {attr_name} + {value:.0f}")

                except (ValueError, AttributeError) as e:
                    print(f"[GearSet] 解析套装加成失败: {e}")
                    continue


@dataclass
class GearSetSelection:
    """套装组合选择"""
    combination_type: str  # "4+2" 或 "2+2+2"
    set_ids: List[int]

    def __post_init__(self):
        """确保列表不为空"""
        if self.set_ids is None:
            self.set_ids = []