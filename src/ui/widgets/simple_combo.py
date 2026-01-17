"""
简化的下拉选择器，使用标准 QComboBox
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QComboBox

from src.utils.format_utils import FormatUtils


class CharacterSelector(QComboBox):
    """角色选择器 - 基于标准 QComboBox"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(280)
        self.setToolTip("点击选择角色")

        # 添加占位符项
        self.addItem("请选择角色...", -1)

    def populate_from_data(self, characters):
        """从角色数据填充下拉框"""
        self.blockSignals(True)

        try:
            # 清除现有项目，保留占位符
            current_data = self.currentData()
            self.clear()
            self.addItem("请选择角色...", -1)

            # 按稀有度排序（从高到低）
            characters.sort(key=lambda x: x.rarity, reverse=True)

            # 添加项目
            for char in characters:
                display_text = FormatUtils.format_character_info(
                    char.name, char.weapon_type, char.element_type
                )

                # 根据稀有度设置颜色
                rarity_color = FormatUtils.get_rarity_color(char.rarity + 1)

                self.addItem(display_text, char.id)
                index = self.count() - 1
                if rarity_color:
                    self.setItemData(index, QColor(rarity_color), Qt.ItemDataRole.ForegroundRole)

            # 恢复选择
            if current_data:
                idx = self.findData(current_data)
                if idx >= 0:
                    self.setCurrentIndex(idx)
                else:
                    self.setCurrentIndex(0)
            else:
                self.setCurrentIndex(0)

        finally:
            self.blockSignals(False)

    def get_selected_data(self):
        """获取当前选中的数据"""
        index = self.currentIndex()
        if index >= 0:
            data = self.itemData(index)
            # 如果是占位符项，返回 None
            return None if data in [None, -1] else data
        return None


class WeaponSelector(QComboBox):
    """音擎选择器 - 基于标准 QComboBox"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(280)
        self.setToolTip("点击选择音擎")

        # 添加占位符项
        self.addItem("请选择音擎...", -1)

    def populate_from_data(self, weapons):
        """从音擎数据填充下拉框"""
        self.blockSignals(True)

        try:
            # 清除现有项目，保留占位符
            current_data = self.currentData()
            self.clear()
            self.addItem("请选择音擎...", -1)

            # 按稀有度排序（从高到低）
            weapons.sort(key=lambda x: x.rarity, reverse=True)

            # 添加项目
            for weapon in weapons:
                # 构建显示文本
                if weapon.actual_advanced_attribute:
                    display_text = FormatUtils.format_weapon_info(
                        weapon.name,
                        weapon.weapon_type,
                        weapon.actual_advanced_attribute.name,
                        weapon.actual_advanced_attribute.base_value
                    )
                else:
                    display_text = f"{weapon.name} | {weapon.weapon_type}"

                # 根据稀有度设置颜色
                rarity_color = FormatUtils.get_rarity_color(weapon.rarity + 1)

                self.addItem(display_text, weapon.id)
                index = self.count() - 1
                if rarity_color:
                    self.setItemData(index, QColor(rarity_color), Qt.ItemDataRole.ForegroundRole)

            # 恢复选择
            if current_data:
                idx = self.findData(current_data)
                if idx >= 0:
                    self.setCurrentIndex(idx)
                else:
                    self.setCurrentIndex(0)
            else:
                self.setCurrentIndex(0)

        finally:
            self.blockSignals(False)

    def get_selected_data(self):
        """获取当前选中的数据"""
        index = self.currentIndex()
        if index >= 0:
            data = self.itemData(index)
            # 如果是占位符项，返回 None
            return None if data in [None, -1] else data
        return None