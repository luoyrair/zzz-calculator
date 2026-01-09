"""
驱动盘相关工具函数
"""

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from src.core.attributes import gear_main_attribute


class GearUtils:
    """驱动盘工具类"""

    # 主属性列表（按位置分组）
    gear_main_attribute_list = [
        [gear_main_attribute[0]],  # 位置1
        [gear_main_attribute[2]],  # 位置2
        [gear_main_attribute[4]],  # 位置3
        [  # 位置4
            gear_main_attribute[1],
            gear_main_attribute[3],
            gear_main_attribute[5],
            gear_main_attribute[7],
            gear_main_attribute[8],
            gear_main_attribute[11],
        ],
        [  # 位置5
            gear_main_attribute[1],
            gear_main_attribute[3],
            gear_main_attribute[5],
            gear_main_attribute[9],
            gear_main_attribute[13],
            gear_main_attribute[14],
            gear_main_attribute[15],
            gear_main_attribute[16],
            gear_main_attribute[17],
        ],
        [  # 位置6
            gear_main_attribute[1],
            gear_main_attribute[3],
            gear_main_attribute[5],
            gear_main_attribute[10],
            gear_main_attribute[6],
            gear_main_attribute[11],
        ]
    ]

    @staticmethod
    def add_set_item_to_combo(combo, set_id, set_name, is_recommended=False):
        """添加套装项到组合框"""
        if is_recommended:
            display_text = f"{set_name}"
            combo.addItem(display_text, set_id)
            index = combo.count() - 1
            combo.setItemData(index, QColor("#FF4500"), Qt.ItemDataRole.ForegroundRole)
        else:
            combo.addItem(set_name, set_id)

    @staticmethod
    def add_sub_attr_item(combo, sub_attr, idx, is_recommended):
        """添加副属性项到组合框"""
        name = sub_attr.name + "%" if sub_attr.value_type == 2 else sub_attr.name

        if is_recommended:
            display_text = f"{name}"
            combo.addItem(display_text, idx)
            index = combo.count() - 1
            combo.setItemData(index, QColor("#FF4500"), Qt.ItemDataRole.ForegroundRole)
        else:
            combo.addItem(name, idx)

    @staticmethod
    def restore_combo_selection(combo, current_id):
        """恢复组合框的选择"""
        if current_id and current_id in [combo.itemData(i) for i in range(combo.count())]:
            combo.setCurrentIndex(combo.findData(current_id))
        else:
            combo.setCurrentIndex(0)

    @staticmethod
    def handle_sub_attribute_deselected(combo, enhance_spinbox, value_label):
        """处理副属性被取消选择"""
        enhance_spinbox.blockSignals(True)
        enhance_spinbox.setValue(0)
        enhance_spinbox.setEnabled(False)
        enhance_spinbox.blockSignals(False)

        value_label.setText("")
        combo.setStyleSheet("")

    @staticmethod
    def restore_sub_attr_selection(combo, current_id):
        """恢复副属性选择"""
        if current_id in [combo.itemData(i) for i in range(combo.count())]:
            combo.setCurrentIndex(combo.findData(current_id))
        else:
            combo.setCurrentIndex(0)

    @staticmethod
    def is_sub_attr_recommended(sub_attr, recommended_sub):
        """检查副属性是否为推荐属性"""
        if not recommended_sub or not hasattr(recommended_sub, 'name'):
            return False
        return (sub_attr.name == recommended_sub.name and
                sub_attr.value_type == recommended_sub.value_type)

    @staticmethod
    def get_position_name(position: int) -> str:
        """获取位置名称"""
        position_names = ["1号盘", "2号盘", "3号盘", "4号盘", "5号盘", "6号盘"]
        return position_names[position] if 0 <= position < len(position_names) else f"位置{position + 1}"

    @staticmethod
    def get_main_attributes_by_position(position: int) -> List:
        """根据位置获取主属性列表"""
        if 0 <= position < len(GearUtils.gear_main_attribute_list):
            return GearUtils.gear_main_attribute_list[position]
        return []

    @staticmethod
    def get_main_attribute_by_index(position: int, index: int):
        """根据位置和索引获取主属性"""
        main_attrs = GearUtils.get_main_attributes_by_position(position)
        if 0 <= index < len(main_attrs):
            return main_attrs[index]
        return None
