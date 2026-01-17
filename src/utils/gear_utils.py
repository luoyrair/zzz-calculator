"""
驱动盘相关工具函数
"""
from typing import List, Tuple


class GearUtils:
    """驱动盘工具类"""

    @staticmethod
    def get_main_attributes_by_position(position: int) -> List[Tuple[str, int]]:
        """根据位置获取主属性名称列表"""
        # 位置0-5的主属性
        position_main_attrs = {
            0: [("生命值", 1)],  # 位置1
            1: [("攻击力", 1)],  # 位置2
            2: [("防御力", 1)],  # 位置3
            3: [  # 位置4
                ("生命值", 2), ("攻击力", 2), ("防御力", 2),
                ("暴击率", 2), ("暴击伤害", 2), ("异常精通", 1)
            ],
            4: [  # 位置5
                ("生命值", 2), ("攻击力", 2), ("防御力", 2), ("穿透率", 2),
                ("物理伤害加成", 2), ("火属性伤害加成", 2), ("冰属性伤害加成", 2),
                ("电属性伤害加成", 2), ("以太伤害加成", 2)
            ],
            5: [  # 位置6
                ("生命值", 2), ("攻击力", 2), ("防御力", 2),
                ("能量自动回复", 2), ("冲击力", 2), ("异常掌控", 2)
            ]
        }
        return position_main_attrs.get(position, [])

    @staticmethod
    def get_sub_attributes() -> List[Tuple[str, int]]:
        """获取副属性列表（名称和类型）"""
        return [
            ("生命值", 1),  # 数值型
            ("生命值", 2),  # 百分比型
            ("攻击力", 1),  # 数值型
            ("攻击力", 2),  # 百分比型
            ("防御力", 1),  # 数值型
            ("防御力", 2),  # 百分比型
            ("暴击率", 2),  # 百分比型
            ("暴击伤害", 2),  # 百分比型
            ("异常精通", 1),  # 数值型
            ("穿透值", 1),  # 数值型
        ]

    @staticmethod
    def get_position_name(position: int) -> str:
        """获取位置名称"""
        position_names = ["1号盘", "2号盘", "3号盘", "4号盘", "5号盘", "6号盘"]
        return position_names[position] if 0 <= position < len(position_names) else f"位置{position + 1}"

    # ========== UI相关工具方法 ==========

    @staticmethod
    def restore_combo_selection(combo, current_id):
        """恢复组合框的选择"""
        if current_id and current_id in [combo.itemData(i) for i in range(combo.count())]:
            combo.setCurrentIndex(combo.findData(current_id))
        else:
            combo.setCurrentIndex(0)

    @staticmethod
    def is_sub_attr_recommended(sub_attr_name, sub_attr_value_type, recommended_sub):
        """检查副属性是否为推荐属性"""
        if not recommended_sub or not hasattr(recommended_sub, 'name'):
            return False
        return (sub_attr_name == recommended_sub.name and
                sub_attr_value_type == recommended_sub.value_type)