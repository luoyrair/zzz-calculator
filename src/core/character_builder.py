# src/core/character_builder.py
"""角色属性构建器 - 单一职责：构建角色属性"""
from src.core.character_models import BaseCharacterStats, CharacterData
from src.core.character_schema import CharacterSchema


class CharacterBuilder:
    """角色属性构建器"""

    def __init__(self, schema: CharacterSchema):
        self.schema = schema

    def build_base_stats(self, level: int, breakthrough_level: int,
                         core_passive_level: int) -> BaseCharacterStats:
        """构建基础属性"""
        stats = BaseCharacterStats()
        stats.Level = level
        stats.BreakthroughLevel = breakthrough_level
        stats.CorePassiveLevel = core_passive_level

        try:
            print(f"\n{'=' * 50}")
            print(f"{self.schema.name} 属性计算")
            print(f"{'=' * 50}")
            print(f"配置: 等级={level}, 突破阶段={breakthrough_level}, 核心技等级={core_passive_level}")

            # 0. 打印基础信息
            curve = self.schema.growth_curve
            print(f"\n[基础数据]")
            print(f"  基础值: HP={curve.base_hp}, ATK={curve.base_atk}, DEF={curve.base_def}")
            print(f"  每级成长: HP={curve.hp_growth:.4f}, ATK={curve.atk_growth:.4f}, DEF={curve.def_growth:.4f}")

            # 1. 计算成长属性
            growth_stats = self._calculate_growth_stats(level)
            print(f"\n[1. 成长计算] (等级{level})")
            print(f"  HP: {curve.base_hp} + ({level}-1)×{curve.hp_growth:.4f} = {growth_stats.HP:.0f}")
            print(f"  ATK: {curve.base_atk} + ({level}-1)×{curve.atk_growth:.4f} = {growth_stats.ATK:.0f}")
            print(f"  DEF: {curve.base_def} + ({level}-1)×{curve.def_growth:.4f} = {growth_stats.DEF:.0f}")
            stats.merge(growth_stats)

            # 2. 应用突破加成
            breakthrough_stats = self._calculate_breakthrough_stats(breakthrough_level)
            print(f"\n[2. 突破加成] (阶段{breakthrough_level})")
            if breakthrough_stats.HP > 0 or breakthrough_stats.ATK > 0 or breakthrough_stats.DEF > 0:
                print(f"  HP: +{breakthrough_stats.HP:.0f}")
                print(f"  ATK: +{breakthrough_stats.ATK:.0f}")
                print(f"  DEF: +{breakthrough_stats.DEF:.0f}")
                print(f"  突破后属性: HP={stats.HP:.0f}, ATK={stats.ATK:.0f}, DEF={stats.DEF:.0f}")
            else:
                print(f"  无突破加成")
            stats.merge(breakthrough_stats)

            # 3. 设置其他属性
            stats.Anomaly_Mastery = self.schema.growth_curve.anomaly_mastery
            stats.Anomaly_Proficiency = self.schema.growth_curve.anomaly_proficiency
            stats.PEN_Ratio = self.schema.growth_curve.pen_ratio
            stats.PEN = self.schema.growth_curve.pen_value
            stats.Energy_Regen = self.schema.growth_curve.energy_regen
            stats.Automatic_Adrenaline_Accumulation = self.schema.growth_curve.adrenaline_accumulation

            # 4. 计算贯穿力
            if self.schema.sheer_force_conversion:
                stats.Sheer_Force = self._calculate_sheer_force(stats)
                print(f"\n[4. 贯穿力计算]")
                print(f"  贯穿力: {stats.Sheer_Force:.0f}")
            else:
                stats.Sheer_Force = 0.0
                print(f"\n[4. 贯穿力计算]")
                print(f"  该角色无贯穿力")

            # 5. 应用核心技加成
            core_passive_stats = self._calculate_core_passive_stats(core_passive_level)
            print(f"\n[3. 核心技加成] (等级{core_passive_level})")
            if core_passive_stats.HP > 0 or core_passive_stats.ATK > 0 or core_passive_stats.DEF > 0:
                print(f"  HP: +{core_passive_stats.HP:.0f}")
                print(f"  ATK: +{core_passive_stats.ATK:.0f}")
                print(f"  DEF: +{core_passive_stats.DEF:.0f}")
                print(f"  核心技后属性: HP={stats.HP:.0f}, ATK={stats.ATK:.0f}, DEF={stats.DEF:.0f}")
            else:
                print(f"  无核心技加成 (等级1)")
            stats.merge(core_passive_stats)

            print(f"\n{'=' * 50}")
            print(f"最终基础属性 (不含驱动盘):")
            print(f"{'=' * 50}")
            print(f"  HP: {stats.HP:.0f}")
            print(f"  ATK: {stats.ATK:.0f}")
            print(f"  DEF: {stats.DEF:.0f}")
            print(f"  暴击率: {stats.CRIT_Rate:.1%}")
            print(f"  暴击伤害: {stats.CRIT_DMG:.1%}")
            print(f"  异常精通: {stats.Anomaly_Proficiency:.0f}")
            print(f"  异常掌控: {stats.Anomaly_Mastery:.0f}")

            return stats

        except Exception as e:
            print(f"构建角色属性失败: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_stats()

    def _calculate_growth_stats(self, level: int) -> CharacterData:
        """计算成长属性"""
        curve = self.schema.growth_curve

        # 成长值计算：基础值 + (等级-1) * 成长率
        hp = curve.base_hp + (level - 1) * curve.hp_growth
        atk = curve.base_atk + (level - 1) * curve.atk_growth
        def_val = curve.base_def + (level - 1) * curve.def_growth

        return CharacterData(
            HP=hp,
            ATK=atk,
            DEF=def_val,
            Impact= curve.impact,
            CRIT_Rate=curve.base_crit_rate,
            CRIT_DMG=curve.base_crit_dmg,
            Anomaly_Mastery=curve.anomaly_mastery,
            Anomaly_Proficiency=curve.anomaly_proficiency,
            PEN_Ratio=curve.pen_ratio,
            PEN=curve.pen_value,
            Energy_Regen=curve.energy_regen,
            Automatic_Adrenaline_Accumulation=curve.adrenaline_accumulation
        )

    def _calculate_breakthrough_stats(self, breakthrough_level: int) -> CharacterData:
        """计算突破加成"""
        result = CharacterData()

        if breakthrough_level <= 0:
            return result

        # 累加所有<=突破阶段的加成
        for stage in self.schema.breakthrough_stages:
            if stage.stage == breakthrough_level:
                result.HP += stage.hp_bonus
                result.ATK += stage.atk_bonus
                result.DEF += stage.def_bonus

        return result

    def _calculate_core_passive_stats(self, core_passive_level: int) -> CharacterData:
        """计算核心技加成"""
        result = CharacterData()

        if core_passive_level <= 1:  # 核心技等级1没有加成
            print(f"核心技等级{core_passive_level}: 无加成 (等级1没有ExtraLevel加成)")
            return result

        print(f"计算核心技加成: 当前等级={core_passive_level}")

        # ExtraLevel中的等级 = 核心技等级 - 1
        json_level = core_passive_level - 1

        # 只应用当前核心技等级对应的加成，而不是累加所有<=等级的加成
        found_bonus = False
        for bonus in self.schema.core_passive_bonuses:
            if bonus.level == json_level:  # 只匹配当前等级
                for attr_type, value in bonus.bonuses.items():
                    attr_name = attr_type.value
                    if hasattr(result, attr_name):
                        setattr(result, attr_name, value)
                        print(f"  应用 {attr_name}: +{value}")
                found_bonus = True
                break

        if not found_bonus:
            print(f"  警告: 未找到核心技等级{core_passive_level}的加成数据")

        print(f"当前核心技等级加成: HP={result.HP:.0f}, ATK={result.ATK:.0f}, DEF={result.DEF:.0f}")
        return result

    def _calculate_sheer_force(self, base_stats: BaseCharacterStats) -> float:
        """计算贯穿力"""
        if not self.schema.sheer_force_conversion:
            return 0.0

        conversion = self.schema.sheer_force_conversion

        # 计算贯穿力
        sheer_force = (
                base_stats.HP * conversion.hp_to_sheer_force +
                base_stats.ATK * conversion.atk_to_sheer_force
        )

        print(f"计算贯穿力:")
        print(
            f"  HP: {base_stats.HP:.0f} * {conversion.hp_to_sheer_force:.3%} = {base_stats.HP * conversion.hp_to_sheer_force:.0f}")
        print(
            f"  ATK: {base_stats.ATK:.0f} * {conversion.atk_to_sheer_force:.3%} = {base_stats.ATK * conversion.atk_to_sheer_force:.0f}")
        print(f"  总贯穿力: {sheer_force:.0f}")

        return sheer_force

    def get_display_info(self) -> dict:
        """获取显示信息"""
        return {
            "id": self.schema.character_id,
            "name": self.schema.name,
            "code_name": self.schema.code_name,
            "rarity": self.schema.rarity,
            "weapon_type": self.schema.weapon_type,
            "element_type": self.schema.element_type
        }

    def _get_default_stats(self) -> BaseCharacterStats:
        """获取默认属性"""
        return BaseCharacterStats(
            HP=1000,
            ATK=100,
            DEF=50,
            CRIT_Rate=0.05,
            CRIT_DMG=0.50,
            Anomaly_Mastery=0,
            Anomaly_Proficiency=0,
            PEN_Ratio=0.0,
            PEN=0,
            Energy_Regen=0,
            Automatic_Adrenaline_Accumulation=0
        )