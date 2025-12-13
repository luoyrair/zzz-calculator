from src.models.character_attributes import CharacterAttributesModel
from src.parsers.character_parser import load_character_data


class CharacterAttributeCalculator:
    """角色属性计算器"""

    def __init__(self):
        print("CharacterAttributeCalculator initialized")

    def calculate_character_attributes(
            self,
            json_file_path: str,
            character_level: int,
            breakthrough_level: int,
            core_passive_level: int
    ) -> CharacterAttributesModel:
        """计算角色属性"""
        parsed_data = load_character_data(json_file_path)
        if not parsed_data:
            raise ValueError(f"无法加载角色数据: {json_file_path}")

        attributes = CharacterAttributesModel()

        attributes.character_id = parsed_data.character_id
        attributes.rarity = parsed_data.rarity
        attributes.weapon_type = parsed_data.weapon_type
        attributes.element_type = parsed_data.element_type

        # 计算基础属性
        self._calculate_base_attributes(attributes, parsed_data, character_level, breakthrough_level)

        # 应用额外属性
        self._apply_extra_attributes(attributes, parsed_data, core_passive_level)

        return attributes

    def _calculate_base_attributes(
            self,
            attributes: CharacterAttributesModel,
            parsed_data,
            character_level: int,
            breakthrough_level: int
    ):
        """计算基础属性"""
        print(f"[CharacterCalculator] 开始计算基础属性:")
        print(f"  角色等级: {character_level}")
        print(f"  突破等级: {breakthrough_level}")
        # HP
        attributes.hp = (
                parsed_data.stats.hp.growing_attribute.calculate_value_at_level(character_level) +
                parsed_data.level[breakthrough_level].hp_max.base_attribute.base
        )

        # 攻击力
        attributes.attack = (
                parsed_data.stats.attack.growing_attribute.calculate_value_at_level(character_level) +
                parsed_data.level[breakthrough_level].attack.base_attribute.base
        )

        # 防御力
        attributes.defence = (
                parsed_data.stats.defence.growing_attribute.calculate_value_at_level(character_level) +
                parsed_data.level[breakthrough_level].defence.base_attribute.base
        )
        print(f"  HP成长: base={parsed_data.stats.hp.growing_attribute.base}, growth={parsed_data.stats.hp.growing_attribute.growth}")
        print(f"  ATK成长: base={parsed_data.stats.attack.growing_attribute.base}, growth={parsed_data.stats.attack.growing_attribute.growth}")
        print(f"  DEF成长: base={parsed_data.stats.defence.growing_attribute.base}, growth={parsed_data.stats.defence.growing_attribute.growth}")

        # 其他固定属性
        attributes.impact = parsed_data.stats.impact.base_attribute.base
        attributes.crit_rate = parsed_data.stats.crit_rate.base_attribute.base / 10000
        attributes.crit_dmg = parsed_data.stats.crit_dmg.base_attribute.base / 10000
        attributes.anomaly_mastery = parsed_data.stats.anomaly_mastery.base_attribute.base
        attributes.anomaly_proficiency = parsed_data.stats.anomaly_proficiency.base_attribute.base
        attributes.pen_ratio = parsed_data.stats.pen_ratio.base_attribute.base
        attributes.pen = parsed_data.stats.pen.base_attribute.base
        attributes.energy_regen = parsed_data.stats.energy_regen.base_attribute.base / 100
        attributes.energy_limit = parsed_data.stats.energy_limit.base_attribute.base
        attributes.automatic_adrenaline_accumulation = (
                parsed_data.stats.automatic_adrenaline_accumulation.base_attribute.base / 100
        )
        attributes.max_adrenaline = parsed_data.stats.max_adrenaline.base_attribute.base

    def _apply_extra_attributes(
            self,
            attributes: CharacterAttributesModel,
            parsed_data,
            core_passive_level: int
    ):
        """应用额外属性（突破、被动等）"""
        if core_passive_level <= 1:
            return

        extra_level_key = core_passive_level - 1
        if extra_level_key in parsed_data.extra:
            for extra_attr in parsed_data.extra[extra_level_key].extra:
                current_value = getattr(attributes, extra_attr.attribute_type, 0.0)
                new_value = current_value + extra_attr.base_attribute.base
                setattr(attributes, extra_attr.attribute_type, new_value)