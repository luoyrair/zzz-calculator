# src/core/models.py
"""重构后的数据模型"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class Attribute:
    """属性数据"""
    name: str
    value: float
    display_value: str = ""

    def __post_init__(self):
        if not self.display_value:
            self.display_value = self._format_value()

    def _format_value(self) -> str:
        """格式化显示值"""
        if self.name.endswith('_PERCENT') or any(x in self.name for x in ['RATE', 'DMG']):
            return f"{self.value:.1%}"
        return f"{self.value:.0f}"


@dataclass
class GearSlot:
    """驱动盘槽位"""
    slot_index: int
    main_attr: Optional[Attribute] = None
    sub_attrs: List[Optional[Attribute]] = field(default_factory=lambda: [None] * 4)

    def update_main_attr(self, name: str, value: float):
        self.main_attr = Attribute(name, value)

    def update_sub_attr(self, index: int, name: str, value: float):
        if 0 <= index < 4:
            self.sub_attrs[index] = Attribute(name, value)

    def reset(self):
        self.main_attr = None
        self.sub_attrs = [None] * 4


@dataclass
class CharacterStats:
    """角色基础属性"""
    base_hp: float = 0.0
    base_atk: float = 0.0
    base_def: float = 0.0
    impact: int = 0
    base_crit_rate: float = 0.0
    base_crit_dmg: float = 0.0
    anomaly_mastery: int = 0
    anomaly_proficiency: int = 0
    penetration: float = 0.0
    energy_regen: int = 0


@dataclass
class CharacterConfig:
    """角色配置"""
    level: int = 60
    ascension: int = 6
    passive_level: int = 7
    character_id: str = ""


class GearDataManager:
    """驱动盘数据管理器"""

    def __init__(self):
        self.character_stats = CharacterStats()
        self.character_config = CharacterConfig()
        self.main_enhance_level = 15
        self.gear_slots: List[GearSlot] = [GearSlot(i) for i in range(6)]

    def update_gear_attribute(self, slot_index: int, attr_type: str,
                              sub_index: int, attr_name: str, value: float):
        """更新驱动盘属性"""
        if 0 <= slot_index < 6:
            if attr_type == "main":
                self.gear_slots[slot_index].update_main_attr(attr_name, value)
            else:
                self.gear_slots[slot_index].update_sub_attr(sub_index, attr_name, value)

    def update_character_config(self, level: int, ascension: int,
                                passive_level: int, character_id: str = ""):
        """更新角色配置"""
        self.character_config.level = level
        self.character_config.ascension = ascension
        self.character_config.passive_level = passive_level
        if character_id:
            self.character_config.character_id = character_id

    def get_gear_data_for_calculation(self) -> List[Dict[str, Any]]:
        """获取计算数据"""
        result = []
        for slot in self.gear_slots:
            slot_data = {
                "main_attr": None,
                "sub_attrs": [None, None, None, None]
            }

            if slot.main_attr:
                slot_data["main_attr"] = {
                    "name": slot.main_attr.name,
                    "value": slot.main_attr.value
                }

            for i, sub_attr in enumerate(slot.sub_attrs):
                if sub_attr:
                    slot_data["sub_attrs"][i] = {
                        "name": sub_attr.name,
                        "value": sub_attr.value
                    }

            result.append(slot_data)
        return result

    def reset_all(self):
        """重置所有数据"""
        self.character_stats = CharacterStats()
        self.character_config = CharacterConfig()
        self.main_enhance_level = 0
        for slot in self.gear_slots:
            slot.reset()


@dataclass
class CalculationResult:
    """计算结果"""
    hp: Dict[str, Any]  # 生命值相关
    atk: Dict[str, Any]  # 攻击力相关
    def_stat: Dict[str, Any]  # 防御力相关
    crit: Dict[str, Any]  # 暴击相关
    impact: Dict[str, Any]  # 冲击力相关
    penetration: Dict[str, Any]  # 穿透率相关
    anomaly: Dict[str, Any]  # 异常属性相关
    energy_regen: Dict[str, Any]  # 能量回复相关
    element_damage: Dict[str, float]  # 元素伤害加成

    @property
    def total_hp(self) -> float:
        return self.hp["final_hp"]

    @property
    def total_atk(self) -> float:
        return self.atk["final_atk"]

    @property
    def total_crit_rate(self) -> float:
        return self.crit["total_crit_rate"]

    @property
    def total_crit_dmg(self) -> float:
        return self.crit["total_crit_dmg"]