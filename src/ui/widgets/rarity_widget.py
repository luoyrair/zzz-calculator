"""
稀有度显示控件
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

from src.config.constants import ColorConstants


class RarityWidget(QWidget):
    """稀有度显示控件"""

    RARITY_NAMES = {
        1: "★",
        2: "★★",
        3: "★★★",
        4: "★★★★",
        5: "★★★★★"
    }

    def __init__(self, rarity: int = -1, parent=None):
        super().__init__(parent)
        self.rarity = rarity
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setFixedHeight(20)

        # 创建标签显示星级
        self.star_label = QLabel(self.RARITY_NAMES.get(self.rarity + 1, ""))
        self.star_label.setFont(QFont("Microsoft YaHei", 10))

        # 设置颜色
        color = ColorConstants.RARITY_COLORS.get(self.rarity + 1, "#808080")
        self.star_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.star_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.star_label)

    def set_rarity(self, rarity: int):
        """设置稀有度"""
        self.rarity = rarity
        color = ColorConstants.RARITY_COLORS.get(rarity + 1, "#808080")
        self.star_label.setText(self.RARITY_NAMES.get(rarity + 1, ""))
        self.star_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def get_rarity(self) -> int:
        """获取稀有度"""
        return self.rarity