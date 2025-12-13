from src.models.gear_attributes import GearMainAttributes, GearSubAttributes


class SlotConfig:
    """槽位配置"""

    def __init__(self):
        self.slot_main_attributes = {
            0: [GearMainAttributes.hp_numeric],
            1: [GearMainAttributes.attack_numeric],
            2: [GearMainAttributes.defence_numeric],
            3: [
                GearMainAttributes.hp_percentage,
                GearMainAttributes.attack_percentage,
                GearMainAttributes.defence_percentage,
                GearMainAttributes.crit_rate,
                GearMainAttributes.crit_dmg,
                GearMainAttributes.anomaly_proficiency
            ],
            4: [
                GearMainAttributes.hp_percentage,
                GearMainAttributes.attack_percentage,
                GearMainAttributes.defence_percentage,
                GearMainAttributes.pen_ratio,
                GearMainAttributes.physical_dmg_bonus,
                GearMainAttributes.fire_dmg_bonus,
                GearMainAttributes.ice_dmg_bonus,
                GearMainAttributes.electric_dmg_bonus,
                GearMainAttributes.ether_dmg_bonus
            ],
            5: [
                GearMainAttributes.hp_percentage,
                GearMainAttributes.attack_percentage,
                GearMainAttributes.defence_percentage,
                GearMainAttributes.anomaly_mastery,
                GearMainAttributes.impact,
                GearMainAttributes.energy_regen
            ]
        }

        self.slot_sub_attributes = [
            GearSubAttributes.hp_numeric,
            GearSubAttributes.hp_percentage,
            GearSubAttributes.attack_numeric,
            GearSubAttributes.attack_percentage,
            GearSubAttributes.defence_numeric,
            GearSubAttributes.defence_percentage,
            GearSubAttributes.crit_rate,
            GearSubAttributes.crit_dmg,
            GearSubAttributes.anomaly_proficiency,
            GearSubAttributes.pen,
        ]

    def get_slot_main_attribute(self, slot_id: int):
        """获取指定槽位的主属性名称列表"""
        if slot_id not in self.slot_main_attributes:
            return []
        return self.slot_main_attributes[slot_id]

    def get_slot_sub_attribute(self):
        """获取指定槽位的主属性名称列表"""
        return self.slot_sub_attributes