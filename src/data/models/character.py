# src/data/models/character.py
"""角色JSON数据模型"""
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class JsonStats:
    """JSON中的Stats字段 - 基于实际数据"""
    HpMax: int = 0
    HpGrowth: int = 0
    Attack: int = 0
    AttackGrowth: int = 0
    Defence: int = 0
    DefenceGrowth: int = 0
    Crit: int = 0
    CritDamage: int = 0
    ElementAbnormalPower: int = 0
    ElementMystery: int = 0
    PenRate: int = 0
    PenDelta: int = 0
    SpRecover: int = 0
    SpBarPoint: int = 0
    RpRecover: int = 0
    RpMax: int = 0
    Armor: int = 0
    ArmorGrowth: int = 0
    MoveSpeed: int = 0
    MoveSpeedGrowth: int = 0
    BreakStun: int = 0
    CritDmgRes: int = 0
    CritRes: int = 0
    Endurance: int = 0
    Rbl: int = 0
    RblCorrectionFactor: int = 0
    RblProbability: int = 0
    Shield: int = 0
    ShieldGrowth: int = 0
    Stun: int = 0
    Tags: List[str] = field(default_factory=list)
    AvatarPieceId: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> 'JsonStats':
        """从字典创建实例"""
        # 创建默认实例
        instance = cls()

        # 动态设置属性
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        return instance


@dataclass
class JsonLevelData:
    """JSON中的Level字段数据"""
    HpMax: int = 0
    Attack: int = 0
    Defence: int = 0
    LevelMax: int = 0
    LevelMin: int = 0

@dataclass
class JsonExtraProperty:
    """ExtraLevel中的Extra属性"""
    Prop: int = 0
    Name: str = ""
    Format: str = ""
    Value: int = 0

@dataclass
class JsonExtraLevelData:
    """ExtraLevel数据"""
    MaxLevel: int = 0
    Extra: Dict[str, JsonExtraProperty] = field(default_factory=dict)

@dataclass
class JsonPassiveExtraProperty:
    """Passive中的ExtraProperty详细结构"""
    Target: int = 0
    Value: int = 0
    Type: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> 'JsonPassiveExtraProperty':
        return cls(
            Target=data.get("Target", 0),
            Value=data.get("Value", 0),
            Type=data.get("Type", "")
        )

@dataclass
class JsonPassiveLevel:
    """Passive中的Level数据"""
    Level: int = 0
    Id: int = 0
    Name: List[str] = field(default_factory=list)
    Desc: List[str] = field(default_factory=list)
    ExtraProperty: Dict[str, JsonPassiveExtraProperty] = field(default_factory=dict)

@dataclass
class JsonCharacterData:
    """完整的JSON角色数据结构"""
    Id: int = 0
    Name: str = ""
    CodeName: str = ""
    Rarity: int = 4
    WeaponType: Dict[str, str] = field(default_factory=dict)
    ElementType: Dict[str, str] = field(default_factory=dict)
    SpecialElementType: Dict[str, Any] = field(default_factory=dict)
    HitType: Dict[str, str] = field(default_factory=dict)
    Camp: Dict[str, str] = field(default_factory=dict)
    Gender: int = 0

    Stats: JsonStats = field(default_factory=JsonStats)
    Level: Dict[str, JsonLevelData] = field(default_factory=dict)
    ExtraLevel: Dict[str, JsonExtraLevelData] = field(default_factory=dict)

    Passive: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json_file(cls, file_path: str) -> 'JsonCharacterData':
        """从JSON文件加载并解析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            return cls.from_dict(raw_data)

        except Exception as e:
            print(f"加载JSON文件失败 {file_path}: {e}")
            return cls()

    @classmethod
    def from_dict(cls, raw_data: dict) -> 'JsonCharacterData':
        """从字典创建实例"""
        # 处理Stats字段
        stats = JsonStats.from_dict(raw_data.get("Stats", {}))

        # 处理Level字段
        level = {}
        for level_key, level_data in raw_data.get("Level", {}).items():
            try:
                # 确保我们创建的是 JsonLevelData 对象
                level[level_key] = JsonLevelData(
                    HpMax=level_data.get("HpMax", 0),
                    Attack=level_data.get("Attack", 0),
                    Defence=level_data.get("Defence", 0),
                    LevelMax=level_data.get("LevelMax", 0),
                    LevelMin=level_data.get("LevelMin", 0)
                )
            except Exception as e:
                print(f"[JsonCharacterData] 解析Level字段{level_key}时出错: {e}")
                # 创建默认对象
                level[level_key] = JsonLevelData()

        # 处理ExtraLevel字段
        extra_level = {}
        for level_key, level_data in raw_data.get("ExtraLevel", {}).items():
            extra_data = {}
            for prop_id, prop_data in level_data.get("Extra", {}).items():
                extra_data[prop_id] = JsonExtraProperty(
                    Prop=prop_data.get("Prop", 0),
                    Name=prop_data.get("Name", ""),
                    Format=prop_data.get("Format", ""),
                    Value=prop_data.get("Value", 0)
                )

            extra_level[level_key] = JsonExtraLevelData(
                MaxLevel=level_data.get("MaxLevel", 0),
                Extra=extra_data
            )

        # 处理Passive字段
        passive_data = raw_data.get("Passive", {})
        passive_levels = {}

        if "Level" in passive_data:
            for level_key, level_info in passive_data["Level"].items():
                extra_property = {}
                if "ExtraProperty" in level_info:
                    for prop_id, prop_data in level_info["ExtraProperty"].items():
                        extra_property[prop_id] = JsonPassiveExtraProperty.from_dict(prop_data)

                passive_levels[level_key] = JsonPassiveLevel(
                    Level=level_info.get("Level", 0),
                    Id=level_info.get("Id", 0),
                    Name=level_info.get("Name", []),
                    Desc=level_info.get("Desc", []),
                    ExtraProperty=extra_property
                )

        passive_data_with_levels = {"Level": passive_levels}
        if "Materials" in passive_data:
            pass

        # 暂时不处理FairyRecommend字段

        return cls(
            Id=raw_data.get("Id", 0),
            Name=raw_data.get("Name", ""),
            CodeName=raw_data.get("CodeName", ""),
            Rarity=raw_data.get("Rarity", 4),
            WeaponType=raw_data.get("WeaponType", {}),
            ElementType=raw_data.get("ElementType", {}),
            SpecialElementType=raw_data.get("SpecialElementType", {}),
            HitType=raw_data.get("HitType", {}),
            Camp=raw_data.get("Camp", {}),
            Gender=raw_data.get("Gender", 0),
            Stats=stats,
            Level=level,
            ExtraLevel=extra_level,
            Passive=passive_data_with_levels
        )