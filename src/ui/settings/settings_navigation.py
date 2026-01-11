"""
设置对话框导航栏
"""

from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal


class NavigationList(QListWidget):
    """左侧导航列表"""

    current_page_changed: pyqtSignal = pyqtSignal(int)  # 发送页面索引变化信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setMaximumWidth(180)
        self.setMinimumWidth(150)

        # 设置样式
        self.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #f5f5f5;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                border-left: 4px solid #2980b9;
            }
            QListWidget::item:hover:!selected {
                background-color: #e3f2fd;
            }
        """)

    def add_navigation_item(self, text: str, icon: str = ""):
        """添加导航项"""
        item = QListWidgetItem(text)
        if icon:
            # 可以在这里添加图标
            pass
        self.addItem(item)

    def set_current_page(self, index: int):
        """设置当前页面"""
        if 0 <= index < self.count():
            self.setCurrentRow(index)

    def currentChanged(self, current, previous):
        """当前项变化时发送信号"""
        super().currentChanged(current, previous)
        if current:
            self.current_page_changed.emit(current.row())