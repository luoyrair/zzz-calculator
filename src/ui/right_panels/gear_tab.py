"""
驱动盘配置选项卡
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QSpinBox, QPushButton, QMessageBox
)

from src.core.attribute_factory import AttributeFactory
from src.ui.widgets.gear_widgets import (
    GearSetConfigWidget, GearPieceEditor, get_sub_attribute_by_index,
)
from src.utils.gear_utils import GearUtils
from src.utils.logger import get_logger


class GearTab(QWidget):
    """驱动盘配置选项卡"""

    def __init__(self, app_core):
        super().__init__()
        self.logger = get_logger("ui.gear_tab")
        self.app_core = app_core

        # 存储驱动盘编辑器
        self.gear_editors = {}

        # 初始化
        self._init_ui()
        self._init_enhance()
        self._connect_signals()

    # ========== 初始化方法 ==========

    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # 创建顶部面板
        self._create_top_panel(main_layout)

        # 创建驱动盘编辑区域
        self._create_gear_editors_area(main_layout)

        # 创建操作按钮区域
        self._create_action_buttons(main_layout)

        # 添加弹性空间
        main_layout.addStretch()

    def _create_top_panel(self, parent_layout):
        """创建顶部面板：套装配置和全局强化等级"""
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)

        # 驱动盘套装配置
        self.gear_set_config = GearSetConfigWidget(self.app_core.data_manager)
        top_layout.addWidget(self.gear_set_config, 0)

        # 全局强化等级设置
        self._create_enhance_widget(top_layout)

        parent_layout.addWidget(top_panel)

    def _create_enhance_widget(self, parent_layout):
        """创建强化等级设置部件"""
        enhance_widget = QWidget()
        enhance_layout = QVBoxLayout(enhance_widget)
        enhance_layout.setContentsMargins(5, 5, 5, 5)
        enhance_layout.setSpacing(5)

        # 创建强化等级微调框
        self.global_enhance_spinbox: QSpinBox = QSpinBox()
        self.global_enhance_spinbox.setRange(0, 15)
        self.global_enhance_spinbox.setValue(15)

        # 水平布局：标签 + 微调框
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("驱动盘强化等级:"))
        level_layout.addWidget(self.global_enhance_spinbox)
        level_layout.addStretch()

        enhance_layout.addLayout(level_layout)
        enhance_layout.addStretch()
        parent_layout.addWidget(enhance_widget, 0)

    def _create_gear_editors_area(self, parent_layout):
        """创建驱动盘编辑区域"""
        gears_group = QGroupBox("驱动盘配置")
        gears_layout = QGridLayout(gears_group)
        gears_layout.setHorizontalSpacing(15)
        gears_layout.setVerticalSpacing(15)

        # 创建6个驱动盘编辑器（3列×2行）
        for i in range(6):
            editor = GearPieceEditor(i)
            self.gear_editors[i] = editor

            row = i // 3  # 行索引 (0, 0, 0, 1, 1, 1)
            col = i % 3   # 列索引 (0, 1, 2, 0, 1, 2)
            gears_layout.addWidget(editor, row, col)

        parent_layout.addWidget(gears_group)

    def _create_action_buttons(self, parent_layout):
        """创建操作按钮区域"""
        buttons_layout = QHBoxLayout()

        # 清空配置按钮
        self.clear_button: QPushButton = QPushButton("清空配置")
        self.clear_button.clicked.connect(self._on_clear_config)
        buttons_layout.addWidget(self.clear_button)

        # 加载预设按钮
        self.load_preset_button: QPushButton = QPushButton("加载预设")
        self.load_preset_button.clicked.connect(self._on_load_preset)
        buttons_layout.addWidget(self.load_preset_button)

        buttons_layout.addStretch()
        parent_layout.addLayout(buttons_layout)

    def _init_enhance(self):
        """初始化强化等级设置"""
        enhance_level = self.global_enhance_spinbox.value()
        for editor in self.gear_editors.values():
            editor.global_enhance_level = enhance_level

    def _connect_signals(self):
        """连接所有信号"""
        # 全局强化等级信号
        self.global_enhance_spinbox.valueChanged.connect(self._on_global_enhance_changed)

        # 套装配置信号
        self.gear_set_config.gear_set_changed.connect(self._on_gear_set_changed)

        # 驱动盘编辑器信号
        self._connect_gear_editor_signals()

    def _connect_gear_editor_signals(self):
        """连接驱动盘编辑器的所有信号"""
        for position, editor in self.gear_editors.items():
            # 主属性变化信号
            editor.main_attribute_changed.connect(
                lambda pos=position, main_attr_idx=None, level=None:
                self._on_main_attribute_changed(pos, main_attr_idx, level)
            )

            # 副属性变化信号
            editor.sub_attributes_changed.connect(
                lambda pos=position, sub_idx=None, sub_attr_idx=None, enhance_level=None:
                self._on_sub_attributes_changed(pos, sub_idx, sub_attr_idx, enhance_level)
            )

    # ========== 事件处理方法 ==========

    def _on_gear_set_changed(self, set_ids):
        """处理套装配置变化"""
        self.app_core.set_gear_sets(set_ids)

    def _on_global_enhance_changed(self, value):
        """处理全局强化等级变化"""
        for editor in self.gear_editors.values():
            editor.set_global_enhance_level(value)

    def _on_main_attribute_changed(self, position, main_attr_idx, level):
        """处理驱动盘主属性变化"""
        main_attrs = GearUtils.get_main_attributes_by_position(position)

        if not (0 <= main_attr_idx < len(main_attrs)):
            return

        main_attr_name, main_attr_value_type = main_attrs[main_attr_idx]

        main_attr = AttributeFactory().gear_main(main_attr_name, main_attr_value_type, level)

        self.app_core.set_gear_piece(
            position=position,
            main_attribute=main_attr,
            sub_attributes=None
        )

    def _on_sub_attributes_changed(self, position, sub_idx, sub_attr_idx, enhance_level):
        """处理驱动盘副属性变化"""
        sub_attr = get_sub_attribute_by_index(sub_attr_idx)

        name, value_type = sub_attr

        sub_attr = AttributeFactory.gear_sub(name,value_type,enhance_level)

        if not sub_attr:
            return

        sub_attributes = {sub_idx: sub_attr}
        self.app_core.set_gear_piece(
            position=position,
            main_attribute=None,
            sub_attributes=sub_attributes
        )

    # ========== 操作按钮方法 ==========

    def _on_clear_config(self):
        """清空所有配置"""
        self._reset_gear_set_config()
        self._reset_enhance_level()
        self._reset_all_gear_editors()

    def _reset_gear_set_config(self):
        """重置套装配置"""
        self.gear_set_config.mode_combo.setCurrentIndex(0)

    def _reset_enhance_level(self):
        """重置强化等级"""
        self.global_enhance_spinbox.setValue(15)

    def _reset_all_gear_editors(self):
        """重置所有驱动盘编辑器"""
        for editor in self.gear_editors.values():
            editor.clear_all()

    def _on_load_preset(self):
        """加载预设配置"""
        QMessageBox.information(
            self,
            "加载预设",
            "加载预设功能将在后续版本中实现"
        )

    # ========== 公共接口方法 ==========

    def update_all_gear_editors(self):
        """更新所有驱动盘编辑器"""
        for editor in self.gear_editors.values():
            editor.update_display()

    def get_gear_editor(self, position: int) -> GearPieceEditor:
        """获取指定位置的驱动盘编辑器"""
        return self.gear_editors.get(position)

    def get_global_enhance_level(self) -> int:
        """获取全局强化等级"""
        return self.global_enhance_spinbox.value()

    def set_global_enhance_level(self, level: int):
        """设置全局强化等级"""
        if 0 <= level <= 15:
            self.global_enhance_spinbox.setValue(level)
