# src/core/calculation/flow.py
"""计算流程管理器"""
from src.core.models.character import CharacterSchema


class AttackCalculationFlow:
    """攻击力计算流程"""

    def __init__(self, character_schema: CharacterSchema, weapon_service=None):
        self.character_schema = character_schema
        self.weapon_service = weapon_service
        self.weapon_atk_fixed = 0.0
        self.weapon_atk_percent = 0.0
        self.weapon_crit_rate = 0.0
        self.weapon_crit_dmg = 0.0
        self.weapon_other_attrs = {}

        print(f"[AttackFlow] 攻击计算流程初始化完成")
        print(f"[AttackFlow] 角色: {character_schema.name}")

    def set_weapon(self, weapon_id: int, level: int, stars: int = None):
        """设置音擎"""
        print(f"\n[AttackFlow] 开始设置音擎:")
        print(f"[AttackFlow]   武器ID: {weapon_id}")
        print(f"[AttackFlow]   等级: {level}")
        print(f"[AttackFlow]   星阶: {stars if stars else '自动计算'}")

        if not self.weapon_service:
            print(f"[AttackFlow] 警告: 武器服务未提供")
            return self

        weapon_attrs = self.weapon_service.get_weapon_attributes_for_character(
            weapon_id, level, stars
        )

        print(f"[AttackFlow] 获取到的武器属性: {weapon_attrs}")

        self.weapon_atk_fixed = weapon_attrs.get('ATK_FIXED', 0.0)
        self.weapon_atk_percent = weapon_attrs.get('ATK_PERCENT', 0.0)
        self.weapon_crit_rate = weapon_attrs.get('CRIT_Rate', 0.0)
        self.weapon_crit_dmg = weapon_attrs.get('CRIT_DMG', 0.0)

        for key, value in weapon_attrs.items():
            if key not in ['ATK_FIXED', 'ATK_PERCENT']:
                self.weapon_other_attrs[key] = value

        print(f"[AttackFlow] 音擎属性解析完成:")
        print(f"[AttackFlow]   固定攻击力: {self.weapon_atk_fixed:.0f}")
        if self.weapon_atk_percent > 0:
            print(f"[AttackFlow]   百分比攻击力: {self.weapon_atk_percent * 100:.1f}%")
        if self.weapon_crit_rate > 0:
            print(f"[AttackFlow]   暴击率加成: {self.weapon_crit_rate * 100:.1f}%")
        if self.weapon_crit_dmg > 0:
            print(f"[AttackFlow]   暴击伤害加成: {self.weapon_crit_dmg * 100:.1f}%")

        if self.weapon_other_attrs:
            print(f"[AttackFlow]   其他属性: {self.weapon_other_attrs}")

        print(f"[AttackFlow] 音擎设置完成")
        return self

    def calculate_base_attack(self, level: int) -> float:
        """计算基础攻击力"""
        print(f"\n[AttackFlow] 计算基础攻击力:")
        print(f"[AttackFlow]   等级: {level}")

        curve = self.character_schema.growth_curve
        character_base_atk = curve.base_atk + (level - 1) * curve.atk_growth
        base_attack = character_base_atk + self.weapon_atk_fixed

        print(f"[AttackFlow]   角色基础攻击力: {curve.base_atk:.0f}")
        print(f"[AttackFlow]   等级成长加成: {(level - 1) * curve.atk_growth:.0f}")
        print(f"[AttackFlow]   角色最终攻击力: {character_base_atk:.0f}")
        print(f"[AttackFlow]   武器固定攻击力: {self.weapon_atk_fixed:.0f}")
        print(f"[AttackFlow]   基础攻击力: {character_base_atk:.0f} + {self.weapon_atk_fixed:.0f} = {base_attack:.0f}")

        return base_attack

    def calculate_final_attack(self, level: int, breakthrough_level: int,
                               core_passive_level: int) -> float:
        """计算最终攻击力"""
        print(f"\n[AttackFlow] 开始计算最终攻击力:")
        print(f"[AttackFlow]   等级: {level}, 突破: {breakthrough_level}, 核心技: {core_passive_level}")

        # 1. 计算基础攻击力
        base_atk = self.calculate_base_attack(level)

        # 2. 应用音擎百分比加成
        if self.weapon_atk_percent > 0:
            bonus = base_atk * self.weapon_atk_percent
            base_atk += bonus
            print(
                f"[AttackFlow]   武器百分比加成: {base_atk * self.weapon_atk_percent:.0f} ({self.weapon_atk_percent * 100:.1f}%)")

        # 3. 应用突破加成
        breakthrough_bonus = 0.0
        if breakthrough_level > 0:
            for stage in self.character_schema.breakthrough_stages:
                if stage.stage == breakthrough_level:
                    breakthrough_bonus = stage.atk_bonus
                    base_atk += breakthrough_bonus
                    print(f"[AttackFlow]   突破加成: +{breakthrough_bonus:.0f}")
                    break

        # 4. 应用核心技加成
        core_passive_bonus = 0.0
        if core_passive_level > 1:
            for passive_bonus in self.character_schema.core_passive_bonuses:
                if passive_bonus.level == core_passive_level:
                    for attr_type, value in passive_bonus.bonuses.items():
                        if attr_type.value == "ATK":
                            core_passive_bonus = value
                            base_atk += core_passive_bonus
                            print(f"[AttackFlow]   核心技加成: +{core_passive_bonus:.0f}")
                            break
                    break

        print(f"[AttackFlow] 最终攻击力计算完成:")
        print(f"[AttackFlow]   基础攻击力: {base_atk - breakthrough_bonus - core_passive_bonus:.0f}")
        if breakthrough_bonus > 0:
            print(f"[AttackFlow]   +突破加成: {breakthrough_bonus:.0f}")
        if core_passive_bonus > 0:
            print(f"[AttackFlow]   +核心技加成: {core_passive_bonus:.0f}")
        print(f"[AttackFlow]   =最终攻击力: {base_atk:.0f}")

        return base_atk

    def get_weapon_bonuses(self):
        """获取音擎提供的所有属性加成"""
        bonuses = self.weapon_other_attrs.copy()
        bonuses.update({
            'CRIT_Rate': self.weapon_crit_rate,
            'CRIT_DMG': self.weapon_crit_dmg
        })

        print(f"[AttackFlow] 获取武器所有加成: {bonuses}")
        return bonuses


class HpDefCalculationFlow:
    """HP和DEF计算流程"""

    def __init__(self, character_schema: CharacterSchema):
        self.character_schema = character_schema
        print(f"[HpDefFlow] HP/DEF计算流程初始化完成")
        print(f"[HpDefFlow] 角色: {character_schema.name}")

    def calculate_final_hp(self, level: int, breakthrough_level: int,
                           core_passive_level: int) -> float:
        """计算最终HP"""
        print(f"\n[HpDefFlow] 开始计算最终HP:")
        print(f"[HpDefFlow]   等级: {level}, 突破: {breakthrough_level}, 核心技: {core_passive_level}")

        curve = self.character_schema.growth_curve

        # 基础HP
        base_hp = curve.base_hp + (level - 1) * curve.hp_growth
        print(f"[HpDefFlow]   角色基础HP: {curve.base_hp:.0f}")
        print(f"[HpDefFlow]   等级成长加成: {(level - 1) * curve.hp_growth:.0f}")
        print(f"[HpDefFlow]   基础HP: {base_hp:.0f}")

        # 突破加成
        breakthrough_bonus = 0.0
        if breakthrough_level > 0:
            for stage in self.character_schema.breakthrough_stages:
                if stage.stage == breakthrough_level:
                    breakthrough_bonus = stage.hp_bonus
                    print(f"[HpDefFlow]   突破HP加成: +{breakthrough_bonus:.0f}")
                    break

        # 核心技加成
        core_passive_bonus = 0.0
        if core_passive_level > 1:
            for passive_bonus in self.character_schema.core_passive_bonuses:
                if passive_bonus.level == core_passive_level:
                    for attr_type, value in passive_bonus.bonuses.items():
                        if attr_type.value == "HP":
                            core_passive_bonus = value
                            print(f"[HpDefFlow]   核心技HP加成: +{core_passive_bonus:.0f}")
                            break
                    break

        final_hp = base_hp + breakthrough_bonus + core_passive_bonus

        print(f"[HpDefFlow] HP计算完成:")
        print(f"[HpDefFlow]   基础HP: {base_hp:.0f}")
        if breakthrough_bonus > 0:
            print(f"[HpDefFlow]   +突破加成: {breakthrough_bonus:.0f}")
        if core_passive_bonus > 0:
            print(f"[HpDefFlow]   +核心技加成: {core_passive_bonus:.0f}")
        print(f"[HpDefFlow]   =最终HP: {final_hp:.0f}")
        return final_hp

    def calculate_final_def(self, level: int, breakthrough_level: int,
                            core_passive_level: int) -> float:
        """计算最终DEF"""
        print(f"\n[HpDefFlow] 开始计算最终DEF:")
        print(f"[HpDefFlow]   等级: {level}, 突破: {breakthrough_level}, 核心技: {core_passive_level}")

        curve = self.character_schema.growth_curve

        # 基础DEF
        base_def = curve.base_def + (level - 1) * curve.def_growth
        print(f"[HpDefFlow]   角色基础DEF: {curve.base_def:.0f}")
        print(f"[HpDefFlow]   等级成长加成: {(level - 1) * curve.def_growth:.0f}")
        print(f"[HpDefFlow]   基础DEF: {base_def:.0f}")

        # 突破加成
        breakthrough_bonus = 0.0
        if breakthrough_level > 0:
            for stage in self.character_schema.breakthrough_stages:
                if stage.stage == breakthrough_level:
                    breakthrough_bonus = stage.def_bonus
                    print(f"[HpDefFlow]   突破DEF加成: +{breakthrough_bonus:.0f}")
                    break

        # 核心技加成
        core_passive_bonus = 0.0
        if core_passive_level > 1:
            for passive_bonus in self.character_schema.core_passive_bonuses:
                if passive_bonus.level == core_passive_level:
                    for attr_type, value in passive_bonus.bonuses.items():
                        if attr_type.value == "DEF":
                            core_passive_bonus = value
                            print(f"[HpDefFlow]   核心技DEF加成: +{core_passive_bonus:.0f}")
                            break
                    break

        final_def = base_def + breakthrough_bonus + core_passive_bonus

        print(f"[HpDefFlow] DEF计算完成:")
        print(f"[HpDefFlow]   基础DEF: {base_def:.0f}")
        if breakthrough_bonus > 0:
            print(f"[HpDefFlow]   +突破加成: {breakthrough_bonus:.0f}")
        if core_passive_bonus > 0:
            print(f"[HpDefFlow]   +核心技加成: {core_passive_bonus:.0f}")
        print(f"[HpDefFlow]   =最终DEF: {final_def:.0f}")
        return final_def