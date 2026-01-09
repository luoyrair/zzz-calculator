"""
等级和突破等级选择器
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QSpinBox
)


class LevelSelector(QWidget):
    """等级选择器"""

    level_changed: pyqtSignal = pyqtSignal(int)

    def __init__(self, title="等级", min_level=1, max_level=60, parent=None):
        super().__init__(parent)

        self.min_level = min_level
        self.max_level = max_level

        self._init_ui(title)
        self._connect_signals()

    def _init_ui(self, title):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标签
        self.label = QLabel(title)
        self.label.setFont(QFont("Microsoft YaHei", 9))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # 微调框
        self.spinbox: QSpinBox = QSpinBox()
        self.spinbox.setMinimum(self.min_level)
        self.spinbox.setMaximum(self.max_level)
        self.spinbox.setValue(self.max_level)  # 默认满级
        self.spinbox.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(self.spinbox)

    def _connect_signals(self):
        """连接信号"""
        self.spinbox.valueChanged.connect(self.level_changed.emit)

    def get_value(self) -> int:
        """获取当前值"""
        return self.spinbox.value()

    def set_value(self, value: int):
        """设置值"""
        self.spinbox.setValue(value)

    def set_range(self, min_val: int, max_val: int):
        """设置范围"""
        self.min_level = min_val
        self.max_level = max_val
        self.spinbox.setMinimum(min_val)
        self.spinbox.setMaximum(max_val)


class BreakthroughSelector(LevelSelector):
    """突破等级选择器"""

    def __init__(self, max_breakthrough=6, parent=None):
        super().__init__("突破等级", 1, max_breakthrough, parent)

    def get_breakthrough_level(self) -> int:
        """获取突破等级"""
        return self.get_value()


class CorePassiveSelector(LevelSelector):
    """核心被动等级选择器"""

    def __init__(self, max_core_passive=7, parent=None):
        super().__init__("核心被动", 1, max_core_passive, parent)

    def get_core_passive_level(self) -> int:
        """获取核心被动等级"""
        return self.get_value()