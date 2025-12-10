# src/data/converter/character.py
"""角色数据转换器"""
from typing import List, Dict

from src.core.models.character import (
    CharacterSchema, GrowthCurve, BreakthroughStage, CorePassiveBonus, SheerForceConversion, AttributeType
)
from src.data.models.character import JsonCharacterData, JsonLevelData, JsonExtraLevelData


class CharacterSchemaConverter:
    """角色JSON数据转换器"""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def convert(self, json_data: JsonCharacterData) -> CharacterSchema:
        """将JSON数据转换为标准业务数据架构"""
        print(f"\n[Converter] 开始转换角色数据: {json_data.Name}(ID:{json_data.Id})")

        try:
            # 转换成长曲线
            print(f"[Converter] 转换成长曲线...")
            growth_curve = self._convert_growth_curve(json_data.Stats)

            # 转换突破阶段
            print(f"[Converter] 转换突破阶段...")
            breakthrough_stages = self._convert_breakthrough_stages(json_data.Level)

            # 转换核心技加成
            print(f"[Converter] 转换核心技加成...")
            core_passive_bonuses = self._convert_core_passive_bonuses(json_data.ExtraLevel)

            # 获取武器类型
            weapon_type = self._get_weapon_display(json_data.WeaponType)
            print(f"[Converter] 武器类型: {weapon_type}")

            # 转换贯穿力转换系数（只有命破角色才有）
            sheer_force_conversion = None
            if weapon_type == "命破":
                print(f"[Converter] 检测到命破角色，解析贯穿力转换系数...")
                sheer_force_conversion = self._convert_sheer_force_conversion(json_data)
                if sheer_force_conversion:
                    print(
                        f"[Converter]  贯穿力转换: HP→{sheer_force_conversion.hp_to_sheer_force}, ATK→{sheer_force_conversion.atk_to_sheer_force}")
                else:
                    print(f"[Converter]  未找到贯穿力转换系数")
            else:
                print(f"[Converter] 非命破角色，跳过贯穿力转换")

            print(f"[Converter] 转换完成:")
            print(f"[Converter]  突破阶段数: {len(breakthrough_stages)}")
            print(f"[Converter]  核心技加成数: {len(core_passive_bonuses)}")
            print(f"[Converter]  贯穿力转换: {'有' if sheer_force_conversion else '无'}")

            # 创建架构
            return CharacterSchema(
                character_id=json_data.Id,
                name=json_data.Name,
                code_name=json_data.CodeName,
                rarity=json_data.Rarity,
                weapon_type=weapon_type,
                element_type=self._get_element_display(json_data.ElementType),
                growth_curve=growth_curve,
                breakthrough_stages=breakthrough_stages,
                core_passive_bonuses=core_passive_bonuses,
                sheer_force_conversion=sheer_force_conversion
            )

        except Exception as e:
            print(f"[Converter] 转换角色数据时出错: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _convert_growth_curve(self, stats) -> GrowthCurve:
        """转换Stats字段为成长曲线"""
        print(f"[Converter]  解析成长曲线数据...")

        attack_growth = stats.AttackGrowth / 10000.0 if hasattr(stats, 'AttackGrowth') else 0
        hp_growth = stats.HpGrowth / 10000.0 if hasattr(stats, 'HpGrowth') else 0
        defence_growth = stats.DefenceGrowth / 10000.0 if hasattr(stats, 'DefenceGrowth') else 0

        print(f"[Converter]   基础HP: {stats.HpMax}, HP成长: {hp_growth:.4f}")
        print(f"[Converter]   基础ATK: {stats.Attack}, ATK成长: {attack_growth:.4f}")
        print(f"[Converter]   基础DEF: {stats.Defence}, DEF成长: {defence_growth:.4f}")

        return GrowthCurve(
            base_hp=stats.HpMax,
            hp_growth=hp_growth,
            base_atk=stats.Attack,
            atk_growth=attack_growth,
            base_def=stats.Defence,
            def_growth=defence_growth,
            impact=stats.BreakStun,
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
        print(f"[Converter]  解析{len(level_data)}个突破阶段...")

        for stage_str, level_info in level_data.items():
            try:
                stage = int(stage_str)
                if 1 <= stage <= 6:
                    hp_bonus = level_info.HpMax if hasattr(level_info, 'HpMax') else 0
                    atk_bonus = level_info.Attack if hasattr(level_info, 'Attack') else 0
                    def_bonus = level_info.Defence if hasattr(level_info, 'Defence') else 0

                    # 只有有实际加成的阶段才添加
                    if hp_bonus > 0 or atk_bonus > 0 or def_bonus > 0:
                        stages.append(BreakthroughStage(
                            stage=stage,
                            hp_bonus=hp_bonus,
                            atk_bonus=atk_bonus,
                            def_bonus=def_bonus
                        ))
                        print(f"[Converter]   突破阶段{stage}: HP+{hp_bonus}, ATK+{atk_bonus}, DEF+{def_bonus}")
                    else:
                        print(f"[Converter]   突破阶段{stage}: 无加成数据，跳过")

            except (ValueError, AttributeError) as e:
                print(f"[Converter]   解析突破阶段{stage_str}时出错: {e}")
                continue

        result = sorted(stages, key=lambda x: x.stage)
        print(f"[Converter]  成功解析{len(result)}个有效突破阶段")
        return result

    def _convert_core_passive_bonuses(self, extra_level_data: Dict[str, JsonExtraLevelData]) -> List[CorePassiveBonus]:
        """转换核心技加成数据"""
        bonuses = []
        print(f"[Converter]  解析核心技加成...")
        print(f"[Converter]  ExtraLevel字段: {list(extra_level_data.keys())}")

        for level_str, extra_data in extra_level_data.items():
            try:
                # ExtraLevel的键就是核心技等级
                level = int(level_str)
                print(f"[Converter]   解析核心技等级{level}...")

                # 解析Extra属性
                bonus_dict = {}
                if hasattr(extra_data, 'Extra') and extra_data.Extra:
                    for prop_id, prop_data in extra_data.Extra.items():
                        try:
                            # 根据属性ID转换为AttributeType
                            attribute_type = self._convert_prop_to_attribute_type(prop_data.Prop)
                            if attribute_type:
                                value = self._normalize_property_value(prop_data.Value, prop_data.Format)
                                bonus_dict[attribute_type] = value
                                print(
                                    f"[Converter]     属性{prop_data.Name}(ID:{prop_data.Prop}): {value} ({prop_data.Format})")
                        except Exception as e:
                            print(f"[Converter]     解析属性{prop_id}时出错: {e}")
                            continue
                else:
                    print(f"[Converter]     等级{level}: Extra字段为空")

                if bonus_dict:
                    bonuses.append(CorePassiveBonus(
                        level=level,
                        bonuses=bonus_dict
                    ))
                    print(f"[Converter]   核心技等级{level}: {len(bonus_dict)}个属性加成")
                else:
                    print(f"[Converter]   核心技等级{level}: 无属性加成")

            except (ValueError, AttributeError) as e:
                print(f"[Converter]   解析核心技等级{level_str}时出错: {e}")
                continue

        result = sorted(bonuses, key=lambda x: x.level)
        print(f"[Converter]  成功解析{len(result)}个核心技加成")

        # 详细输出解析结果
        for bonus in result:
            print(f"[Converter]   等级{bonus.level}:")
            for attr_type, value in bonus.bonuses.items():
                print(f"[Converter]     {attr_type.value}: {value}")

        return result

    def _convert_sheer_force_conversion(self, json_data: JsonCharacterData) -> SheerForceConversion:
        """转换贯穿力转换系数"""
        try:
            print(f"[Converter]  尝试从Passive描述中提取贯穿力转换系数...")

            # 从Passive描述中提取贯穿力转换系数
            if hasattr(json_data, 'Passive') and json_data.Passive:
                # 查找第一个Passive描述
                for level_key, level_data in json_data.Passive.get("Level", {}).items():
                    if "Desc" in level_data and level_data["Desc"]:

                        # 如果没找到完整模式，尝试查找ExtraProperty
                        if "ExtraProperty" in level_data:
                            print(f"[Converter]   尝试从ExtraProperty中提取转换系数...")
                            hp_value = 0
                            atk_value = 0

                            for prop_id, prop_data in level_data["ExtraProperty"].items():
                                target = prop_data.get("Target", 0)
                                value = prop_data.get("Value", 0)

                                if target == 123:  # 贯穿力转换的目标ID
                                    prop_id_int = int(prop_id)
                                    if prop_id_int == 111:  # HP
                                        hp_value = value / 10000.0  # 转换为小数
                                    elif prop_id_int == 121:  # ATK
                                        atk_value = value / 10000.0  # 转换为小数

                            if hp_value > 0 or atk_value > 0:
                                print(f"[Converter]   从ExtraProperty中提取到转换系数:")
                                print(f"[Converter]     HP→贯穿力: {hp_value}")
                                print(f"[Converter]     ATK→贯穿力: {atk_value}")

                                return SheerForceConversion(
                                    hp_to_sheer_force=hp_value,
                                    atk_to_sheer_force=atk_value
                                )

            # 如果没找到，使用默认值（从仪玄数据中可以看到是0.1和0.3）
            print(f"[Converter]   使用默认贯穿力转换系数: HP→0.1, ATK→0.3")
            return SheerForceConversion(
                hp_to_sheer_force=0.1,  # 每1点HP转换为0.1贯穿力
                atk_to_sheer_force=0.3  # 每1点ATK转换为0.1贯穿力
            )

        except Exception as e:
            print(f"[Converter]   提取贯穿力转换系数时出错: {e}")
            return None

    def _convert_prop_to_attribute_type(self, prop_id: int) -> AttributeType:
        """将属性ID转换为AttributeType枚举"""
        # 处理特殊ID（如31201, 12101）
        # 雅的数据中: 31201=异常精通, 12101=基础攻击力
        base_prop_id = prop_id // 100  # 取前3位

        print(f"[Converter]   转换属性ID: {prop_id} -> base: {base_prop_id}")

        # 根据游戏数据映射
        prop_mapping = {
            111: AttributeType.HP,  # 生命值
            121: AttributeType.ATK,  # 攻击力
            131: AttributeType.DEF,  # 防御力
            122: AttributeType.IMPACT,  # 冲击力
            201: AttributeType.CRIT_RATE,  # 暴击率
            211: AttributeType.CRIT_DMG,  # 暴击伤害
            314: AttributeType.ANOMALY_MASTERY,  # 异常掌控
            312: AttributeType.ANOMALY_PROFICIENCY,  # 异常精通
            231: AttributeType.PEN_RATIO,  # 穿透率
            232: AttributeType.PEN,  # 穿透
            305: AttributeType.ENERGY_REGEN,  # 能量回复
        }

        # 特别处理31201
        if prop_id == 31201:
            return AttributeType.ANOMALY_PROFICIENCY
        elif prop_id == 12101:
            return AttributeType.ATK

        attr_type = prop_mapping.get(base_prop_id)
        if attr_type:
            print(f"[Converter]   属性ID {prop_id} -> {attr_type.value}")
        else:
            print(f"[Converter]   未知属性ID: {prop_id} (base: {base_prop_id})")

        return attr_type

    def _normalize_property_value(self, value: int, format_str: str) -> float:
        """规范化属性值"""
        print(f"[Converter]   规范化属性值: {value}, 格式: {format_str}")

        if "percent" in format_str.lower() or "%" in format_str or "ratio" in format_str.lower():
            normalized = value / 10000.0  # 百分比值除以10000
            print(f"[Converter]     百分比值: {value} -> {normalized:.4f}")
            return normalized
        else:
            print(f"[Converter]     固定值: {value} -> {float(value)}")
            return float(value)

    def _get_weapon_display(self, weapon_data: Dict[str, str]) -> str:
        """获取武器显示名称"""
        if weapon_data:
            values = list(weapon_data.values())
            if values:
                return values[0]
        return "未知"

    def _get_element_display(self, element_data: Dict[str, str]) -> str:
        """获取元素显示名称"""
        if element_data:
            values = list(element_data.values())
            if values:
                return values[0]
        return "未知"