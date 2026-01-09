"""
主窗口模块 - 适配新架构
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter, QStatusBar
)

from src.config.constants import AppConstants
from src.ui.left_panel import LeftPanel
from src.ui.right_panel import RightPanel


class MainWindow(QMainWindow):
    """主窗口 - 适配新架构"""

    def __init__(self, app_core):
        super().__init__()

        print("初始化主窗口...")
        self.app_core = app_core

        try:
            self._init_ui()
            self._setup_window()
            self._connect_signals()
            print("✓ 主窗口初始化完成")
        except Exception as e:
            print(f"✗ 主窗口初始化失败: {e}")
            import traceback
            traceback.print_exc()

    def _init_ui(self):
        """初始化UI"""
        # 设置窗口标题
        self.setWindowTitle(f"{AppConstants.APP_NAME} v{AppConstants.VERSION}")

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 创建分割器（左右面板）
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # 创建左侧面板
        self.left_panel = LeftPanel(self.app_core)

        # 创建右侧面板
        self.right_panel = RightPanel(self.app_core)

        # 添加到分割器
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)

        # 设置分割器比例 (4:6)
        self.splitter.setSizes([300, 700])

        # 添加到主布局
        main_layout.addWidget(self.splitter)

        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def _setup_window(self):
        """设置窗口属性"""
        # 设置窗口尺寸
        self.resize(1400, 960)

        # 设置最小尺寸
        self.setMinimumSize(1000, 600)

        # 居中显示
        self.center_window()

    def _connect_signals(self):
        """连接信号"""
        # 连接应用核心的信号到状态栏更新
        self.app_core.character_changed.connect(self._on_character_changed)
        self.app_core.weapon_changed.connect(self._on_weapon_changed)
        self.app_core.gear_set_changed.connect(self._on_gear_set_changed)
        self.app_core.gear_piece_changed.connect(self._on_gear_piece_changed)

        # 连接角色选项卡和驱动盘选项卡
        if hasattr(self.right_panel, 'character_tab') and hasattr(self.right_panel, 'gear_tab'):
            self.right_panel.character_tab.set_gear_tab_reference(self.right_panel.gear_tab)

    def _on_character_changed(self, character):
        """处理角色变化"""
        self.status_bar.showMessage(f"角色已选择: {character.name}")

        # 更新左侧面板的角色数据
        if hasattr(self.left_panel, '_on_character_changed'):
            self.left_panel.on_character_changed(character)

    def _on_weapon_changed(self, weapon):
        """处理武器变化"""
        self.status_bar.showMessage(f"音擎已选择: {weapon.name}")

    def _on_gear_set_changed(self, set_ids):
        """处理套装变化"""
        self.status_bar.showMessage(f"驱动盘套装已更新: {set_ids}")

    def _on_gear_piece_changed(self, position):
        """处理驱动盘变化"""
        pos_name = ["1号盘", "2号盘", "3号盘", "4号盘", "5号盘", "6号盘"][position]
        self.status_bar.showMessage(f"{pos_name} 属性已更新")

    def center_window(self):
        """窗口居中"""
        screen_geometry = self.screen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def closeEvent(self, event):
        """关闭事件处理"""
        # 可以在这里保存设置或执行清理操作
        event.accept()