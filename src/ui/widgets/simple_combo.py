"""
简化但功能完整的下拉选择器
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QComboBox

from src.utils.format_utils import FormatUtils


class EnhancedSimpleComboBox(QComboBox):
    """增强的简化组合框 - 保持标准QComboBox的点击行为"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(280)

    def add_colored_item(self, text: str, color: str = None, data=None, font_size: int = None):
        """添加带颜色的项目

        Args:
            text: 显示文本
            color: 颜色代码（如"#FF0000"）
            data: 关联数据
            font_size: 字体大小
        """
        # 如果第一个是占位符项，先移除它
        if self.count() == 1 and self.itemData(0) is None:
            self.removeItem(0)

        self.addItem(text, data)

        index = self.count() - 1

        # 设置文本颜色
        if color:
            self.setItemData(index, QColor(color), Qt.ItemDataRole.ForegroundRole)

        # 设置字体大小
        if font_size:
            font = QFont("Microsoft YaHei", font_size)
            self.setItemData(index, font, Qt.ItemDataRole.FontRole)

    def set_placeholder_text(self, text: str):
        """设置占位符文本"""
        # 方法1：如果使用可编辑模式
        line_edit = self.lineEdit()
        if line_edit:
            line_edit.setPlaceholderText(text)
        # 方法2：如果使用占位符项
        elif self.count() > 0 and self.itemData(0) is None:
            self.setItemText(0, text)

    def get_selected_data(self):
        """获取当前选中的数据"""
        index = self.currentIndex()
        if index >= 0:
            data = self.itemData(index)
            # 如果是占位符项，返回None
            return None if data is None else data
        return None

    def set_current_by_data(self, data):
        """根据数据设置当前项"""
        for i in range(self.count()):
            if self.itemData(i) == data:
                self.setCurrentIndex(i)
                return True
        # 如果没找到，选择占位符项
        if self.count() > 0 and self.itemData(0) is None:
            self.setCurrentIndex(0)
        return False


class CharacterSelector(EnhancedSimpleComboBox):
    """角色选择器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_placeholder_text("选择角色...")
        self.setToolTip("点击选择角色")

    def populate_from_data(self, characters):
        """从角色数据填充下拉框

        Args:
            characters: CharacterInfo对象列表
        """
        self.blockSignals(True)

        try:
            self.clear()

            # 添加占位符项
            self.addItem("请选择角色...", -1)

            # 按稀有度排序（从高到低）
            characters.sort(key=lambda x: x.rarity + 1, reverse=True)

            # 添加项目
            for char in characters:
                # 使用FormatUtils格式化显示文本
                display_text = FormatUtils.format_character_info(
                    char.name, char.weapon_type, char.element_type
                )

                # 根据稀有度设置颜色
                rarity_color = FormatUtils.get_rarity_color(char.rarity + 1)

                self.add_colored_item(display_text, rarity_color, char.id)

            # 设置默认选择占位符项
            self.setCurrentIndex(0)
        finally:
            self.blockSignals(False)


class WeaponSelector(EnhancedSimpleComboBox):
    """音擎选择器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_placeholder_text("选择音擎...")
        self.setToolTip("点击选择音擎")

    def populate_from_data(self, weapons):
        """从音擎数据填充下拉框

        Args:
            weapons: WeaponInfo对象列表
        """
        self.blockSignals(True)

        try:
            self.clear()

            # 添加占位符项
            self.addItem("请选择音擎...", -1)

            # 按稀有度排序（从高到低）
            weapons.sort(key=lambda x: x.rarity + 1, reverse=True)

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

                self.add_colored_item(display_text, rarity_color, weapon.id)

            # 设置默认选择占位符项
            self.setCurrentIndex(0)
        finally:
            self.blockSignals(False)
