# src/data/converter/weapon.py
"""音擎数据转换器"""
from typing import Dict
from ...core.models.weapon import (
    WeaponSchema, WeaponProperty, WeaponLevelData,
    WeaponStarData, WeaponTalent
)
from ..models.weapon import JsonWeaponData


class WeaponSchemaConverter:
    """音擎JSON到标准架构的转换器"""

    @staticmethod
    def convert(json_data: JsonWeaponData) -> WeaponSchema:
        # 解析基础属性
        base_property = WeaponProperty(
            name=json_data.BaseProperty.get("Name", ""),
            display_name=json_data.BaseProperty.get("Name2", ""),
            format=json_data.BaseProperty.get("Format", ""),
            base_value=float(json_data.BaseProperty.get("Value", 0)),
            is_percentage=False
        )

        # 解析随机属性
        rand_property = WeaponProperty(
            name=json_data.RandProperty.get("Name", ""),
            display_name=json_data.RandProperty.get("Name2", ""),
            format=json_data.RandProperty.get("Format", ""),
            base_value=float(json_data.RandProperty.get("Value", 0)),
            is_percentage=json_data.RandProperty.get("Name") != "异常精通"
        )

        # 解析等级数据
        level_data = {}
        for level_str, level_info in json_data.Level.items():
            try:
                level = int(level_str)
                level_data[level] = WeaponLevelData(
                    rate=level_info.get("Rate", 0),
                    rate2=level_info.get("Rate2", 10000)
                )
            except (ValueError, KeyError):
                continue

        # 解析星阶数据
        star_data = {}
        for star_str, star_info in json_data.Stars.items():
            try:
                star = int(star_str)
                star_data[star] = WeaponStarData(
                    star_rate=star_info.get("StarRate", 0),
                    rand_rate=star_info.get("RandRate", 0)
                )
            except (ValueError, KeyError):
                continue

        # 获取武器类型
        weapon_type = "未知"
        if json_data.WeaponType:
            weapon_type = list(json_data.WeaponType.values())[0]

        return WeaponSchema(
            weapon_id=json_data.Id,
            name=json_data.Name,
            rarity=json_data.Rarity,
            weapon_type=weapon_type,
            base_property=base_property,
            rand_property=rand_property,
            level_data=level_data,
            star_data=star_data,
            talents={}  # 简化版本
        )