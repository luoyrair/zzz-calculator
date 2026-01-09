"""
属性显示控件
用于显示属性名称和值
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel


class AttributeDisplay(QWidget):
    """属性显示控件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.attribute_labels = {}  # 存储属性标签

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(8)

    def set_attributes(self, attributes):
        """
        设置属性列表

        Args:
            attributes: list of (name, value, name_color, value_color) tuples
                       or (name, value, color) tuples for backward compatibility
        """
        # 清空现有标签
        for label in self.attribute_labels.values():
            label[0].deleteLater()
            label[1].deleteLater()
        self.attribute_labels.clear()

        # 添加属性标签
        for i, attr_data in enumerate(attributes):
            # 支持新格式 (name, value, name_color, value_color)
            # 也支持旧格式 (name, value, color)
            if len(attr_data) == 4:
                name, value, name_color, value_color = attr_data
            else:
                name, value, color = attr_data
                name_color = color
                value_color = color

            row = i // 1  # 每行显示1个属性
            col = (i % 1) * 2  # 每列占2个网格

            # 创建属性名称标签
            name_label = QLabel(name)
            name_label.setFont(QFont("Microsoft YaHei", 9))
            name_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if name_color:
                # 只设置颜色，保持原有字体
                name_label.setStyleSheet(f"color: {name_color};")
            else:
                name_label.setStyleSheet("color: black;")

            # 创建属性值标签
            value_label = QLabel(value)
            value_label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))  # 值保持加粗
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            if value_color:
                value_label.setStyleSheet(f"color: {value_color};")
            else:
                value_label.setStyleSheet("color: black;")

            # 添加到布局
            self.layout.addWidget(name_label, row, col)
            self.layout.addWidget(value_label, row, col + 1)

            # 保存引用
            self.attribute_labels[name] = (name_label, value_label)

    def update_attributes(self, attributes):
        """更新属性值（使用QPalette设置颜色）"""
        for name, value, name_color, value_color in attributes:
            if name in self.attribute_labels:
                name_label, value_label = self.attribute_labels[name]

                # 更新值
                value_label.setText(str(value))

                # 设置属性名颜色
                if name_color:
                    # 使用样式表设置颜色，因为QPalette在某些情况下可能不生效
                    name_label.setStyleSheet(f"color: {name_color};")

                # 设置属性值颜色
                if value_color:
                    value_label.setStyleSheet(f"color: {value_color};")

    def get_attribute_value(self, name):
        """获取属性值"""
        if name in self.attribute_labels:
            return self.attribute_labels[name][1].text()
        return None