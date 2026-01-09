"""
右侧面板 - 适配新架构
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from src.ui.right_panels.character_tab import CharacterTab
from src.ui.right_panels.gear_tab import GearTab


class RightPanel(QWidget):
    """右侧面板 - 适配新架构"""

    def __init__(self, app_core):
        super().__init__()
        self.app_core = app_core

        # 跟踪角色是否已选择
        self.character_selected = False

        # 初始化UI
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 创建选项卡部件
        self.tab_widget = QTabWidget()

        # 创建并添加角色选项卡
        self.character_tab = CharacterTab(self.app_core)
        self.tab_widget.addTab(self.character_tab, "角色/音擎")

        # 创建并添加驱动盘选项卡（初始禁用）
        self.gear_tab = GearTab(self.app_core)
        gear_tab_index = self.tab_widget.addTab(self.gear_tab, "驱动盘配置")
        self.tab_widget.setTabEnabled(gear_tab_index, False)

        layout.addWidget(self.tab_widget)

    def _connect_signals(self):
        """连接信号"""
        # 监听角色变化，启用驱动盘选项卡
        self.app_core.character_changed.connect(self._on_character_changed)

    def _on_character_changed(self, character):
        """处理角色变化 - 启用驱动盘选项卡"""
        # 角色已选择
        self.character_selected = True

        # 找到驱动盘选项卡的索引
        gear_tab_index = 1  # 因为先添加了角色选项卡

        # 启用驱动盘选项卡
        if self.character_selected:
            self.tab_widget.setTabEnabled(gear_tab_index, True)
        else:
            self.tab_widget.setTabEnabled(gear_tab_index, False)

            # 如果当前在驱动盘选项卡，切换回角色选项卡
            if self.tab_widget.currentIndex() == gear_tab_index:
                self.tab_widget.setCurrentIndex(0)