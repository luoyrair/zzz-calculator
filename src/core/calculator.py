"""统一属性计算器"""
from typing import Dict, Optional

from src.utils.calculation_utils import CalculationUtils
from src.utils.logger import get_logger
from .models import Character, Weapon, GearSet, GearPiece


class AttributeCalculator:
    """简化版属性计算器"""

    def __init__(self, data_manager):
        self.logger = get_logger("core.calculator")
        self.logger.info("AttributeCalculator 初始化开始")
        self.data_manager = data_manager

        # 初始化缓存
        self._calculate_cache = {}  # 主计算缓存
        self._calculate_character_cache = {}  # 仅角色计算缓存
        self._calculate_with_weapon_cache = {}  # 角色+武器计算缓存（不含天赋）
        self._calculate_with_weapon_talent_cache = {}  # 角色+武器+天赋计算缓存
        self.logger.debug(
            f"缓存初始化完成: "
            f"calculate={len(self._calculate_cache)}, "
            f"character={len(self._calculate_character_cache)}, "
            f"with_weapon={len(self._calculate_with_weapon_cache)}, "
            f"with_weapon_talent={len(self._calculate_with_weapon_talent_cache)}")
        self.logger.info("AttributeCalculator 初始化完成")

    # ========== 公共计算方法 ==========

    def calculate(self, character: Character,
                  weapon: Optional[Weapon] = None,
                  gear_sets: Dict[str, GearSet] = None,
                  gear_pieces: Dict[int, GearPiece] = None,
                  include_talent: bool = True) -> Dict[str, float]:
        """
        综合计算：角色 + 武器 + 套装 + 驱动盘

        Args:
            character: 角色模型实例
            weapon: 武器模型实例
            gear_sets: 字典存储的驱动盘套装实例
            gear_pieces: 字典存储的驱动盘实例
            include_talent: 是否包含音擎天赋属性
        """
        self.logger.debug(f"开始计算 (include_talent={include_talent}):")
        self.logger.debug(f"  - 角色: {character.name if character else 'None'}")
        self.logger.debug(f"  - 武器: {weapon.name if weapon else 'None'}")
        self.logger.debug(f"  - 套装数量: {len(gear_sets) if gear_sets else 0}")
        self.logger.debug(f"  - 驱动盘数量: {len(gear_pieces) if gear_pieces else 0}")

        # 检查缓存
        cache_key = CalculationUtils.get_cache_key(character, weapon, gear_sets, gear_pieces, include_talent)
        self.logger.debug(f"缓存键: {cache_key}")
        if cache_key in self._calculate_cache:
            self.logger.debug(f"使用缓存结果")
            return self._calculate_cache[cache_key].copy()

        # 计算角色和武器基础属性（不包含天赋）
        (
            character_base,
            result, percentage_bonuses, flat_bonuses,
            weapon_base_attack
        ) = self._calculate_character_with_weapon(character, weapon, include_talent=False)

        self.logger.debug(f"计算角色和武器基础属性 {character_base}")

        # 如果包含天赋属性，添加天赋属性
        if include_talent and weapon and weapon.talent_attributes:
            self.logger.debug(f"包含天赋属性，天赋等级: {weapon.talent}")
            if 0 <= weapon.talent - 1 < len(weapon.talent_attributes):
                talent_attr = weapon.talent_attributes[weapon.talent - 1]
                self.logger.debug(f"天赋属性: {talent_attr.name}={talent_attr.base_value}")
                percentage_bonuses, flat_bonuses = CalculationUtils.add_attribute_to_dicts(
                    talent_attr, percentage_bonuses, flat_bonuses
                )

        # 处理套装效果
        if gear_sets:
            for gear_set in gear_sets.values():
                if gear_set.effect_2:
                    percentage_bonuses, flat_bonuses = CalculationUtils.add_attribute_to_dicts(
                        gear_set.effect_2, percentage_bonuses, flat_bonuses
                    )
                self.logger.debug(f"处理套装效果后 percentage_bonuses: {percentage_bonuses}, flat_bonuses: {flat_bonuses}")

        # 处理驱动盘属性
        if gear_pieces:
            for gear_piece in gear_pieces.values():
                for attr in gear_piece.get_all_attributes():
                    percentage_bonuses, flat_bonuses = CalculationUtils.add_attribute_to_dicts(
                        attr, percentage_bonuses, flat_bonuses
                    )
        self.logger.debug(f"处理驱动盘属性后 百分比加成 {percentage_bonuses}，固定值加成 {flat_bonuses}")

        if character.core_passive - 1 >= 0:
            if character.weapon_type == "命破":
                passive_data = character.get_passive_data()
            else:
                passive_data = None
        else:
            passive_data = None

        # 计算最终属性值
        result = CalculationUtils.calculate_final_attributes(
            character_base, result, percentage_bonuses, flat_bonuses, weapon_base_attack, passive_data
        )
        self.logger.debug(f"final - result {result}")

        # 缓存结果
        CalculationUtils().cache_result(cache_key, result, self._calculate_cache)

        return result

    def calculate_character_only(self, character: Character) -> Dict[str, float]:
        """计算仅角色的基础属性"""
        cache_key = CalculationUtils.get_cache_key(character)
        if cache_key in self._calculate_character_cache:
            self.logger.debug(f"calculate_character_only 使用缓存")
            return self._calculate_character_cache[cache_key].copy()

        character_base = character.get_base_attributes()
        self.logger.debug(f"calculate_character_only character_base={character_base}")

        # 缓存结果
        CalculationUtils().cache_result(cache_key, character_base, self._calculate_character_cache)

        return character_base

    def calculate_with_weapon(self, character: Character, weapon: Weapon, include_talent: bool = False) -> Dict[
        str, float]:
        """计算角色 + 武器的属性

        Args:
            character: 角色模型实例
            weapon: 武器模型实例
            include_talent: 是否包含音擎天赋属性
        """
        self.logger.debug(f"calculate_with_weapon 开始: character={character.name}, weapon={weapon}, include_talent={include_talent}")

        # 根据是否包含天赋属性选择不同的缓存
        if include_talent:
            cache_dict = self._calculate_with_weapon_talent_cache
        else:
            cache_dict = self._calculate_with_weapon_cache

        cache_key = CalculationUtils.get_cache_key(character, weapon, include_talent=include_talent)
        self.logger.debug(f"缓存键: {cache_key}")

        if cache_key in cache_dict:
            self.logger.debug(f"使用缓存结果")
            return cache_dict[cache_key].copy()
        (
            character_base,
            result, percentage_bonuses, flat_bonuses,
            weapon_base_attack
        ) = self._calculate_character_with_weapon(character, weapon, include_talent)

        if character.core_passive - 1 >= 0:
            if character.weapon_type == "命破":
                passive_data = character.get_passive_data()
                self.logger.debug(f"有被动数据: {passive_data}")
            else:
                passive_data = None
        else:
            passive_data = None

        # 计算最终属性值
        result = CalculationUtils.calculate_final_attributes(
            character_base, result, percentage_bonuses, flat_bonuses, weapon_base_attack, passive_data
        )
        self.logger.debug(f"计算结果: {result}")

        # 缓存结果
        CalculationUtils().cache_result(cache_key, result, cache_dict)
        self.logger.debug(f"缓存大小: {len(cache_dict)}")

        return result

    # ========== 内部计算方法 ==========

    def _calculate_character_with_weapon(self, character: Character, weapon: Weapon, include_talent: bool = False):
        """
        计算角色和武器的属性（内部方法）
        返回：(character_base, result, percentage_bonuses, flat_bonuses, weapon_base_attack)
        """
        self.logger.debug(f"_calculate_character_with_weapon 开始: character={character.name}, weapon={weapon}, include_talent={include_talent}")

        # 1. 获取角色基础属性
        self.logger.debug(f"获取角色基础属性")
        character_base = character.get_base_attributes()
        self.logger.debug(f"角色基础属性: {character_base}")

        # 2. 初始化结果和加成集合
        result = {}
        percentage_bonuses = {}  # 属性名 -> 总百分比加成
        flat_bonuses = {}  # 属性名 -> 固定值加成

        # 3. 处理武器属性
        weapon_base_attack = 0
        if weapon:
            self.logger.debug(f"处理武器属性: {weapon.name}")
            weapon.set_actual_attributes(self.data_manager)

            # 获取武器属性（基础攻击力和高级属性）
            weapon_attrs = weapon.get_attributes()

            # 根据是否包含天赋决定要处理的属性数量
            if include_talent:
                attrs_to_process = weapon_attrs  # 包含所有属性（包括天赋）
            else:
                attrs_to_process = weapon_attrs[:2]  # 只包含基础攻击力和高级属性，不包含天赋

            for attr in attrs_to_process:
                self.logger.debug(f"处理武器属性: {attr.name}={attr.base_value}")
                weapon_base_attack = CalculationUtils().process_attribute(attr, percentage_bonuses,
                                                                          flat_bonuses, weapon_base_attack)

        self.logger.debug(f"武器基础攻击: {weapon_base_attack}")
        self.logger.debug(f"百分比加成: {percentage_bonuses}")
        self.logger.debug(f"固定值加成: {flat_bonuses}")

        return character_base, result, percentage_bonuses, flat_bonuses, weapon_base_attack

    # ========== 缓存管理方法 ==========

    def clear_cache(self):
        """清空所有缓存"""
        self._calculate_cache.clear()
        self._calculate_character_cache.clear()
        self._calculate_with_weapon_cache.clear()
        self._calculate_with_weapon_talent_cache.clear()

    def clear_specific_cache(self, cache_type: str = "all"):
        """
        清除指定类型的缓存

        Args:
            cache_type: "all" - 所有缓存
                       "character" - 仅角色缓存
                       "weapon" - 角色+武器缓存
                       "full" - 完整计算缓存
        """
        if cache_type == "all":
            self.clear_cache()
        elif cache_type == "character":
            self._calculate_character_cache.clear()
        elif cache_type == "weapon":
            self._calculate_with_weapon_cache.clear()
        elif cache_type == "full":
            self._calculate_cache.clear()

    def get_cache_info(self) -> Dict[str, int]:
        """获取缓存信息"""
        return {
            "full_calculation": len(self._calculate_cache),
            "character_only": len(self._calculate_character_cache),
            "character_with_weapon": len(self._calculate_with_weapon_cache),
            "total": len(self._calculate_cache) +
                    len(self._calculate_character_cache) +
                    len(self._calculate_with_weapon_cache)
        }