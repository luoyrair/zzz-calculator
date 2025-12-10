# src/data/models/weapon.py
"""音擎JSON数据模型"""
import json
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class JsonWeaponData:
    """音擎JSON数据结构"""
    Id: int = 0
    Name: str = ""
    Rarity: int = 4
    WeaponType: Dict[str, str] = field(default_factory=dict)
    BaseProperty: Dict[str, Any] = field(default_factory=dict)
    RandProperty: Dict[str, Any] = field(default_factory=dict)
    Level: Dict[str, Dict[str, int]] = field(default_factory=dict)
    Stars: Dict[str, Dict[str, int]] = field(default_factory=dict)

    @classmethod
    def from_json_file(cls, file_path: str) -> 'JsonWeaponData':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            return cls.from_dict(raw_data)
        except Exception as e:
            print(f"加载音擎JSON文件失败 {file_path}: {e}")
            return cls()

    @classmethod
    def from_dict(cls, raw_data: dict) -> 'JsonWeaponData':
        return cls(
            Id=raw_data.get("Id", 0),
            Name=raw_data.get("Name", ""),
            Rarity=raw_data.get("Rarity", 4),
            WeaponType=raw_data.get("WeaponType", {}),
            BaseProperty=raw_data.get("BaseProperty", {}),
            RandProperty=raw_data.get("RandProperty", {}),
            Level=raw_data.get("Level", {}),
            Stars=raw_data.get("Stars", {})
        )