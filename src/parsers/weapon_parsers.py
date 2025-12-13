"""音擎数据转换器"""
import json
from typing import Dict, Any
from pathlib import Path

from src.models.attributes import AttributeType
from src.models.weapon_model import WeaponSchema, WeaponLevelData, WeaponStarData, WeaponTalent


class WeaponConverter:
    """音擎JSON数据转换器"""

    # 属性名称映射
    ATTR_NAME_MAP = {
        "基础攻击力": AttributeType.ATK,
        "攻击力": AttributeType.ATK,
        "暴击率": AttributeType.CRIT_RATE,
        "暴击伤害": AttributeType.CRIT_DMG,
        "异常精通": AttributeType.ANOMALY_PROFICIENCY,
        "生命值": AttributeType.HP,
        "防御力": AttributeType.DEF,
        "能量自动回复": AttributeType.ENERGY_REGEN,
        "穿透率": AttributeType.PEN_RATIO,
        "冲击力": AttributeType.IMPACT,
        "异常掌控": AttributeType.ANOMALY_MASTERY,
    }

    @classmethod
    def convert_from_json(cls, json_data: Dict[str, Any]) -> WeaponSchema:
        """从JSON数据转换"""
        # 基础信息
        weapon_id = json_data.get("Id", 0)
        name = json_data.get("Name", "")
        rarity = json_data.get("Rarity", 2)

        # 解析基础属性
        base_property = json_data.get("BaseProperty", {})
        base_attr_type = cls.ATTR_NAME_MAP.get(base_property.get("Name", "基础攻击力"), AttributeType.ATK)
        base_attr_value = float(base_property.get("Value", 0))

        # 解析随机属性
        rand_property = json_data.get("RandProperty", {})
        rand_attr_name = rand_property.get("Name", "")
        rand_attr_type = cls.ATTR_NAME_MAP.get(rand_attr_name, AttributeType.ATK)
        rand_attr_value = float(rand_property.get("Value", 0))

        # 判断是否为百分比
        rand_format = rand_property.get("Format", "")
        rand_is_percentage = "%" in rand_format

        # 转换百分比值：从万分比转换为小数
        if rand_is_percentage:
            rand_attr_value = rand_attr_value / 10000.0

        # 解析等级数据
        level_data = {}
        raw_level_data = json_data.get("Level", {})
        for level_str, level_info in raw_level_data.items():
            try:
                level = int(level_str)
                level_data[level] = WeaponLevelData(
                    level=level,
                    base_atk_rate=float(level_info.get("Rate", 0)),
                    random_attr_rate=float(level_info.get("Rate2", 10000))
                )
            except (ValueError, KeyError):
                continue

        # 解析突破数据
        star_data = {}
        raw_star_data = json_data.get("Stars", {})
        for star_str, star_info in raw_star_data.items():
            try:
                star = int(star_str)
                star_data[star] = WeaponStarData(
                    star=star,
                    base_atk_star_rate=float(star_info.get("StarRate", 0)),
                    random_attr_star_rate=float(star_info.get("RandRate", 0))
                )
            except (ValueError, KeyError):
                continue

        # 解析天赋
        talents = {}
        raw_talents = json_data.get("Talents", {})
        for star_str, talent_info in raw_talents.items():
            try:
                star = int(star_str)
                talents[star] = WeaponTalent(
                    star=star,
                    name=talent_info.get("Name", ""),
                    description=talent_info.get("Desc", "")
                )
            except (ValueError, KeyError):
                continue

        return WeaponSchema(
            weapon_id=weapon_id,
            name=name,
            rarity=rarity,
            base_attr_type=base_attr_type,
            base_attr_value=base_attr_value,
            random_attr_type=rand_attr_type,
            random_attr_value=rand_attr_value,
            random_attr_is_percentage=rand_is_percentage,
            level_data=level_data,
            star_data=star_data,
            talents=talents
        )

    @classmethod
    def load_from_file(cls, file_path: Path) -> WeaponSchema:
        """从文件加载并转换"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            return cls.convert_from_json(json_data)
        except Exception as e:
            raise ValueError(f"加载音擎文件失败 {file_path}: {e}")