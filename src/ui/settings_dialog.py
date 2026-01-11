"""
主设置对话框
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSplitter, QWidget, QStackedWidget
from PyQt6.QtCore import Qt

from src.config.settings import settings_manager, AppSettings
from src.ui.settings.settings_navigation import NavigationList
from src.ui.settings.settings_pages import (
    GeneralSettingsPage,
    DisplaySettingsPage,
    ConstraintsSettingsPage
)


class SettingsDialog(QDialog):
    """主设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.current_settings = self.settings_manager.get_settings()

        self._init_ui()
        self._connect_signals()
        self._load_current_settings()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setMinimumSize(700, 550)
        self.resize(800, 600)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建分割器（左侧导航 + 右侧内容）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # 左侧导航栏
        self.navigation_list = NavigationList()
        self.navigation_list.add_navigation_item("📊 通用设置")
        self.navigation_list.add_navigation_item("👁️ 显示设置")
        self.navigation_list.add_navigation_item("⚙️ 等级约束")
        splitter.addWidget(self.navigation_list)

        # 右侧内容区域
        self.content_stack = QStackedWidget()

        # 创建各个设置页面
        self.general_page = GeneralSettingsPage()
        self.display_page = DisplaySettingsPage()
        self.constraints_page = ConstraintsSettingsPage()

        self.content_stack.addWidget(self.general_page)
        self.content_stack.addWidget(self.display_page)
        self.content_stack.addWidget(self.constraints_page)

        splitter.addWidget(self.content_stack)

        # 设置分割器比例
        splitter.setSizes([200, 600])

        main_layout.addWidget(splitter)

        # 按钮区域（底部）
        self._create_buttons_area(main_layout)

    def _connect_signals(self):
        """连接信号"""
        self.navigation_list.current_page_changed.connect(self._on_page_changed)

    def _on_page_changed(self, index: int):
        """处理页面切换"""
        if 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)

    def _create_buttons_area(self, parent_layout):
        """创建按钮区域"""
        buttons_widget = QWidget()
        buttons_widget.setStyleSheet("background-color: #f5f5f5; border-top: 1px solid #e0e0e0;")

        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(20, 15, 20, 15)
        buttons_layout.setSpacing(15)

        # 恢复默认按钮
        default_button: QPushButton = QPushButton("恢复默认")
        default_button.setMinimumWidth(100)
        default_button.clicked.connect(self._restore_defaults)
        buttons_layout.addWidget(default_button)

        buttons_layout.addStretch()

        # 取消按钮
        cancel_button: QPushButton = QPushButton("取消")
        cancel_button.setMinimumWidth(80)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        # 应用按钮
        apply_button: QPushButton = QPushButton("应用")
        apply_button.setMinimumWidth(80)
        apply_button.setStyleSheet("background-color: #3498db; color: white;")
        apply_button.clicked.connect(self._apply_settings)
        buttons_layout.addWidget(apply_button)

        # 确定按钮
        ok_button: QPushButton = QPushButton("确定")
        ok_button.setMinimumWidth(80)
        ok_button.setDefault(True)
        ok_button.setStyleSheet("background-color: #2ecc71; color: white;")
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        parent_layout.addWidget(buttons_widget)

    def _load_current_settings(self):
        """加载当前设置到各个页面"""
        # 通用设置
        self.general_page.load_settings(self.current_settings)

        # 显示设置
        self.display_page.load_settings(self.current_settings)

        # 等级约束设置
        self.constraints_page.load_settings(self.current_settings)

        # 默认选择第一个页面
        self.navigation_list.set_current_page(0)

    def _apply_settings(self):
        """应用设置"""
        self._save_settings()

    def _restore_defaults(self):
        """恢复默认设置"""
        self.current_settings = AppSettings()
        self._load_current_settings()

    def _save_settings(self):
        """保存设置到管理器"""
        # 创建新的设置对象
        new_settings = AppSettings()

        # 保存各个页面的设置
        self.general_page.save_settings(new_settings)
        self.display_page.save_settings(new_settings)
        self.constraints_page.save_settings(new_settings)

        # 保存到管理器
        self.settings_manager.update_settings(new_settings)

        # 更新当前设置引用
        self.current_settings = new_settings

    def accept(self):
        """确定按钮点击事件"""
        self._save_settings()
        super().accept()

    def get_settings(self) -> AppSettings:
        """获取当前设置"""
        return self.current_settings
