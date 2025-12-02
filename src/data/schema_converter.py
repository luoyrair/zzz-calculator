# src/data/schema_converter.py
"""JSON数据到业务数据的转换器"""
from typing import Optional, List, Dict, Any
from src.data.json_models import JsonCharacterData, JsonLevelData
from src.core.character_schema import (
    CharacterSchema, GrowthCurve, BreakthroughStage,
    CorePassiveBonus, SheerForceConversion, AttributeType
)


class SchemaConverter:
    """数据架构转换器"""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def convert(self, json_data: JsonCharacterData) -> CharacterSchema:
        """将JSON数据转换为标准业务数据架构"""

        print(f"开始转换角色数据: {json_data.Name} (ID: {json_data.Id})")

        # 1. 转换成长曲线
        growth_curve = self._convert_growth_curve(json_data.Stats)

        # 2. 转换突破阶段
        breakthrough_stages = self._convert_breakthrough_stages(json_data.Level)
        print(f"突破阶段数量: {len(breakthrough_stages)}")

        # 3. 转换核心技加成
        core_passive_bonuses = self._convert_core_passive_bonuses(json_data.ExtraLevel)
        print(f"核心技加成数量: {len(core_passive_bonuses)}")

        # 4. 转换贯穿力系数
        print("正在提取贯穿力转换系数...")
        sheer_force_conversion = self._extract_sheer_force_conversion(json_data.Passive)

        if sheer_force_conversion:
            print(
                f"贯穿力转换系数: HP={sheer_force_conversion.hp_to_sheer_force:.3%}, ATK={sheer_force_conversion.atk_to_sheer_force:.3%}")
        else:
            print("该角色没有贯穿力转换系数")

        # 5. 获取显示信息
        weapon_type = self._get_weapon_display(json_data.WeaponType)
        element_type = self._get_element_display(json_data.ElementType)

        # 6. 提取被动技能数据
        passive_abilities = self._extract_passive_abilities(json_data.Passive)
        print(f"被动技能数量: {len(passive_abilities)}")

        print("角色数据转换完成")

        return CharacterSchema(
            character_id=json_data.Id,
            name=json_data.Name,
            code_name=json_data.CodeName,
            rarity=json_data.Rarity,
            weapon_type=weapon_type,
            element_type=element_type,
            special_element_type=self._get_special_element_display(json_data.SpecialElementType),
            growth_curve=growth_curve,
            breakthrough_stages=breakthrough_stages,
            core_passive_bonuses=core_passive_bonuses,
            sheer_force_conversion=sheer_force_conversion,
            passive_abilities=passive_abilities
        )

    def _convert_growth_curve(self, stats) -> GrowthCurve:
        """转换Stats字段为成长曲线"""
        # 注意：AttackGrowth是整数，需要除以10000得到每级成长值
        # 公式：属性值 = 基础值 + (等级-1) * 成长值/10000

        attack_growth = stats.AttackGrowth / 10000.0 if hasattr(stats, 'AttackGrowth') else 0
        hp_growth = stats.HpGrowth / 10000.0 if hasattr(stats, 'HpGrowth') else 0
        defence_growth = stats.DefenceGrowth / 10000.0 if hasattr(stats, 'DefenceGrowth') else 0

        print(f"成长值转换 - 基础值: HP={stats.HpMax}, ATK={stats.Attack}, DEF={stats.Defence}")
        print(f"成长值转换 - 每级成长: HP={hp_growth:.4f}, ATK={attack_growth:.4f}, DEF={defence_growth:.4f}")
        print(
            f"成长值转换 - 60级计算: HP={stats.HpMax + 59 * hp_growth:.0f}, ATK={stats.Attack + 59 * attack_growth:.0f}, DEF={stats.Defence + 59 * defence_growth:.0f}")

        return GrowthCurve(
            base_hp=stats.HpMax,
            hp_growth=hp_growth,
            base_atk=stats.Attack,
            atk_growth=attack_growth,
            base_def=stats.Defence,
            def_growth=defence_growth,
            impact = stats.BreakStun,
            base_crit_rate=stats.Crit / 10000.0,
            base_crit_dmg=stats.CritDamage / 10000.0,
            anomaly_mastery=stats.ElementAbnormalPower,
            anomaly_proficiency=stats.ElementMystery,
            pen_ratio=stats.PenRate / 100.0,
            pen_value=stats.PenDelta,
            energy_regen=stats.SpRecover / 100.0,
            adrenaline_accumulation=stats.RpRecover / 100.0
        )

    def _convert_breakthrough_stages(self, level_data: Dict[str, JsonLevelData]) -> List[BreakthroughStage]:
        """转换突破阶段数据"""
        stages = []

        for stage_str, level_info in level_data.items():
            try:
                stage = int(stage_str)
                # 只有阶段1-6有属性加成
                if 1 <= stage <= 6:
                    stages.append(BreakthroughStage(
                        stage=stage,
                        hp_bonus=level_info.HpMax,
                        atk_bonus=level_info.Attack,
                        def_bonus=level_info.Defence
                    ))
            except (ValueError, AttributeError):
                continue

        return sorted(stages, key=lambda x: x.stage)

    def _convert_core_passive_bonuses(self, extra_level_data) -> List[CorePassiveBonus]:
        """转换核心技加成数据"""
        bonuses = []

        # 属性ID到AttributeType的映射
        prop_mapping = {
            11101: AttributeType.HP,  # 基础生命值
            11102: AttributeType.HP,  # 生命值百分比
            12101: AttributeType.ATK,  # 基础攻击力
            12102: AttributeType.ATK,  # 攻击力百分比
            12201: AttributeType.IMPACT,  # 冲击力
            20101: AttributeType.CRIT_RATE,  # 暴击率
            20103: AttributeType.CRIT_RATE,  # 暴击率（百分比）
            21101: AttributeType.CRIT_DMG,  # 暴击伤害
            21103: AttributeType.CRIT_DMG,  # 暴击伤害（百分比）
            23101: AttributeType.PEN_RATIO,  # 穿透率
            31201: AttributeType.ANOMALY_PROFICIENCY,  # 异常精通
            30501: AttributeType.ENERGY_REGEN,  # 能量回复
            31401: AttributeType.ANOMALY_MASTERY,  # 异常掌控
        }

        for level_str, level_info in extra_level_data.items():
            try:
                # ExtraLevel中的等级 = 核心技等级 - 1
                # 所以等级1对应核心技等级2
                json_level = int(level_str)
                core_passive_level = json_level + 1  # 转换为实际的核心技等级

                bonus_dict = {}

                for prop_id, prop_info in level_info.Extra.items():
                    # 转换为整数
                    try:
                        prop_id_int = int(prop_id)
                    except ValueError:
                        continue

                    attr_type = prop_mapping.get(prop_id_int)
                    if attr_type and hasattr(prop_info, 'Value'):
                        value = prop_info.Value

                        # 根据属性类型处理值
                        if attr_type == AttributeType.ATK:
                            # 基础攻击力：固定值
                            bonus_dict[attr_type] = value
                            print(f"核心技等级{core_passive_level}: 基础攻击力+{value}")
                        elif attr_type == AttributeType.ANOMALY_PROFICIENCY:
                            # 异常精通：固定值
                            bonus_dict[attr_type] = value
                        else:
                            # 其他属性：除以10000转换为小数百分比
                            bonus_dict[attr_type] = value / 10000.0

                if bonus_dict:
                    bonuses.append(CorePassiveBonus(
                        level=core_passive_level,  # 存储实际的核心技等级
                        bonuses=bonus_dict
                    ))
                    print(f"创建核心技加成: 等级={core_passive_level}, 加成={bonus_dict}")

            except (ValueError, AttributeError) as e:
                print(f"转换核心技加成失败: level_str={level_str}, 错误={e}")
                continue

        # 按等级排序
        sorted_bonuses = sorted(bonuses, key=lambda x: x.level)
        print(f"核心技加成总数: {len(sorted_bonuses)}")
        return sorted_bonuses

    def _extract_sheer_force_conversion(self, passive_data) -> Optional[SheerForceConversion]:
        """从被动数据中提取贯穿力转换系数"""
        try:
            # 检查Passive数据是否存在
            if not passive_data or "Level" not in passive_data:
                return None

            level_data = passive_data["Level"]
            if not level_data:
                return None

            # 使用第一个有效的被动等级数据
            for level_key, passive_info in level_data.items():
                if not hasattr(passive_info, 'ExtraProperty') or not passive_info.ExtraProperty:
                    continue

                extra_property = passive_info.ExtraProperty
                hp_to_pen = 0.0
                atk_to_pen = 0.0

                # 遍历ExtraProperty中的所有属性
                for prop_id_str, prop_data in extra_property.items():
                    try:
                        prop_id = int(prop_id_str)
                        target = prop_data.Target
                        value = prop_data.Value

                        # 检查是否是贯穿力转换属性 (Target == 123)
                        if target == 123:  # 贯穿力目标ID
                            if prop_id == 121:  # 攻击力转贯穿力
                                atk_to_pen = value / 10000.0  # 转换为小数
                                print(f"找到攻击力转贯穿力系数: {value} -> {atk_to_pen:.2%}")
                            elif prop_id == 111:  # 生命值转贯穿力
                                hp_to_pen = value / 10000.0  # 转换为小数
                                print(f"找到生命值转贯穿力系数: {value} -> {hp_to_pen:.2%}")

                    except (ValueError, AttributeError) as e:
                        print(f"解析贯穿力系数时出错: prop_id={prop_id_str}, 错误={e}")
                        continue

                # 如果找到了转换系数，返回结果
                if hp_to_pen > 0 or atk_to_pen > 0:
                    print(f"生成贯穿力转换系数: HP->{hp_to_pen:.2%}, ATK->{atk_to_pen:.2%}")
                    return SheerForceConversion(
                        hp_to_sheer_force=hp_to_pen,
                        atk_to_sheer_force=atk_to_pen
                    )

            # 没有找到贯穿力转换系数
            print("未找到贯穿力转换系数")
            return None

        except Exception as e:
            print(f"提取贯穿力转换系数时出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _get_weapon_display(self, weapon_data: Dict[str, str]) -> str:
        """获取武器显示名称"""
        display_config = self.config_manager.character.display_config

        # 提取武器类型值
        if weapon_data:
            values = list(weapon_data.values())
            if values:
                return display_config.get_weapon_display({"value": values[0]})

        return "未知"

    def _get_element_display(self, element_data: Dict[str, str]) -> str:
        """获取元素显示名称"""
        display_config = self.config_manager.character.display_config

        # 提取元素类型值
        if element_data:
            values = list(element_data.values())
            if values:
                return display_config.get_element_display({"value": values[0]})

        return "未知"

    def _get_special_element_display(self, special_element_data) -> str:
        """获取特殊元素显示名称"""
        if not special_element_data:
            return ""

        # 从字典中提取值
        if isinstance(special_element_data, dict):
            values = list(special_element_data.values())
            return values[0] if values else ""

        return str(special_element_data)

    def _extract_passive_abilities(self, passive_data) -> Dict[str, Any]:
        """提取被动技能数据"""
        # 对于当前版本，我们不需要被动技能数据
        # 返回空字典避免错误
        return {}