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

    def get_slot_main_attribute(self, slot_id: int):
        """获取指定槽位的主属性列表"""
        if slot_id not in self.slot_main_attributes:
            return []
        return self.slot_main_attributes[slot_id]

    def get_slot_sub_attribute(self):
        """获取所有副属性"""
        return GearSubAttributes.get_all_sub_attributes()