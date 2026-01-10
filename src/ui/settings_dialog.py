"""
设置对话框 - 添加显示规则选项
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton, QCheckBox,
    QPushButton, QButtonGroup, QFormLayout
)

from src.config.settings import settings_manager, AppSettings


class SettingsDialog(QDialog):
    """设置对话框 - 添加显示规则选项"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.current_settings = self.settings_manager.get_settings()

        self._init_ui()
        self._load_current_settings()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setMinimumSize(500, 450)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # 自动选择设置组
        self._create_auto_select_group(main_layout)

        # 显示设置组
        self._create_display_group(main_layout)

        # 等级约束设置组
        self._create_level_constraints_group(main_layout)

        # 按钮区域
        self._create_buttons_area(main_layout)

    def _create_level_constraints_group(self, parent_layout):
        """创建等级约束设置组"""
        group = QGroupBox("角色等级约束设置")
        group_layout = QVBoxLayout(group)

        # 等级变化约束模式
        level_group = QGroupBox("等级变化时，如何设置突破等级：")
        level_group_layout = QVBoxLayout(level_group)

        self.level_mode_group = QButtonGroup(self)

        # 模式1：默认模式
        mode1 = QRadioButton("模式1：突破等级 = 等级最小值≤当前等级的最大等级最小值对应的突破等级")
        mode1.setToolTip("例如：等级=50 → 突破等级=5 (因为50>40且≤50)")
        self.level_mode_group.addButton(mode1, 1)
        level_group_layout.addWidget(mode1)

        # 模式2
        mode2 = QRadioButton("模式2：突破等级 = 等级最大值≥当前等级且当前等级>等级最大值的等级最小值的等级最大值对应的突破等级")
        mode2.setToolTip("更保守的模式，需要等级达到当前突破等级的上限才会升级突破")
        self.level_mode_group.addButton(mode2, 2)
        level_group_layout.addWidget(mode2)

        # 模式3
        mode3 = QRadioButton("模式3：渐进模式（等级达到当前突破上限时手动升级突破）")
        mode3.setToolTip("等级达到当前突破上限时不会自动升级突破，需要手动升级突破等级")
        self.level_mode_group.addButton(mode3, 3)
        level_group_layout.addWidget(mode3)

        group_layout.addWidget(level_group)

        # 突破等级变化约束模式
        breakthrough_group = QGroupBox("突破等级变化时，如何设置等级：")
        breakthrough_group_layout = QVBoxLayout(breakthrough_group)

        self.breakthrough_mode_group = QButtonGroup(self)

        # 模式1：默认模式
        bmode1 = QRadioButton("模式1：等级 = 突破等级的等级最大值")
        bmode1.setToolTip("例如：突破等级=5 → 等级=50")
        self.breakthrough_mode_group.addButton(bmode1, 1)
        breakthrough_group_layout.addWidget(bmode1)

        # 模式2
        bmode2 = QRadioButton("模式2：等级 = 突破等级的等级最小值")
        bmode2.setToolTip("例如：突破等级=5 → 等级=40")
        self.breakthrough_mode_group.addButton(bmode2, 2)
        breakthrough_group_layout.addWidget(bmode2)

        group_layout.addWidget(breakthrough_group)
        parent_layout.addWidget(group)

    def _create_auto_select_group(self, parent_layout):
        """创建自动选择设置组"""
        group = QGroupBox("自动选择设置")
        group_layout = QFormLayout(group)

        # 自动选择专属音擎
        self.auto_select_weapon_check = QCheckBox("选择角色时自动选择专属音擎")
        self.auto_select_weapon_check.setToolTip(
            "启用后，选择角色时会自动选择对应的专属音擎\n"
            "音擎ID格式：1{稀有度}{角色ID//10}"
        )
        group_layout.addRow(self.auto_select_weapon_check)

        # 使用原始推荐数据
        self.use_recommendations_check = QCheckBox("使用原始推荐数据设置角色的推荐数据")
        self.use_recommendations_check.setToolTip("启用后，将使用数据文件中的推荐数据")
        group_layout.addRow(self.use_recommendations_check)

        parent_layout.addWidget(group)

    def _create_display_group(self, parent_layout):
        """创建显示设置组"""
        group = QGroupBox("显示设置")
        group_layout = QVBoxLayout(group)

        # 角色属性显示模式
        display_group = QGroupBox("角色属性显示模式：")
        display_group_layout = QVBoxLayout(display_group)

        self.display_mode_group = QButtonGroup(self)

        # 模式1：显示角色面板属性
        display_mode1 = QRadioButton("显示角色面板属性")
        display_mode1.setToolTip("显示角色基础属性 + 武器基础属性 + 驱动盘属性\n不包含音擎天赋属性")
        self.display_mode_group.addButton(display_mode1, 1)
        display_group_layout.addWidget(display_mode1)

        # 模式2：显示角色局内属性
        display_mode2 = QRadioButton("显示角色局内属性")
        display_mode2.setToolTip("显示角色面板属性 + 音擎天赋属性")
        self.display_mode_group.addButton(display_mode2, 2)
        display_group_layout.addWidget(display_mode2)

        group_layout.addWidget(display_group)

        # 基础属性显示选项
        self.show_basic_section_check: QCheckBox = QCheckBox("显示角色基础属性")
        self.show_basic_section_check.setToolTip(
            "启用后，左侧面板将显示角色基础属性区域"
        )
        group_layout.addWidget(self.show_basic_section_check)

        # 基础属性内容显示选项
        basic_content_group = QGroupBox("基础属性区域显示内容：")
        basic_content_layout = QVBoxLayout(basic_content_group)

        self.basic_content_group = QButtonGroup(self)

        # 模式1：显示角色基础属性
        basic_mode1 = QRadioButton("显示角色基础属性")
        basic_mode1.setToolTip("根据角色类型显示对应的属性")
        self.basic_content_group.addButton(basic_mode1, 1)
        basic_content_layout.addWidget(basic_mode1)

        # 模式2：显示所有属性
        basic_mode2 = QRadioButton("显示所有属性")
        basic_mode2.setToolTip("显示所有属性")
        self.basic_content_group.addButton(basic_mode2, 2)
        basic_content_layout.addWidget(basic_mode2)

        group_layout.addWidget(basic_content_group)

        # 连接信号：当基础属性区域显示状态改变时，更新内容选项的可用状态
        self.show_basic_section_check.toggled.connect(
            lambda enabled: self._update_basic_content_group_state(enabled)
        )

        parent_layout.addWidget(group)

    def _create_buttons_area(self, parent_layout):
        """创建按钮区域"""
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        # 确定按钮
        ok_button: QPushButton = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        # 取消按钮
        cancel_button: QPushButton = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        # 应用按钮
        apply_button: QPushButton = QPushButton("应用")
        apply_button.clicked.connect(self._apply_settings)
        buttons_layout.addWidget(apply_button)

        # 恢复默认按钮
        default_button: QPushButton = QPushButton("恢复默认")
        default_button.clicked.connect(self._restore_defaults)
        buttons_layout.addWidget(default_button)

        parent_layout.addLayout(buttons_layout)

    def _update_basic_content_group_state(self, enabled):
        """更新基础属性内容选项组的状态"""
        basic_content_group_widget = self.findChild(QGroupBox, "基础属性区域显示内容：")
        if basic_content_group_widget:
            basic_content_group_widget.setEnabled(enabled)
            for button in self.basic_content_group.buttons():
                button.setEnabled(enabled)

    def _load_current_settings(self):
        """加载当前设置到UI"""
        # 等级约束模式
        level_mode = self.current_settings.level_constraints.character_level_constraint_mode
        if 1 <= level_mode <= 3:
            self.level_mode_group.button(level_mode).setChecked(True)

        # 突破约束模式
        breakthrough_mode = self.current_settings.level_constraints.breakthrough_constraint_mode
        if 1 <= breakthrough_mode <= 2:
            self.breakthrough_mode_group.button(breakthrough_mode).setChecked(True)

        # 自动选择设置
        self.auto_select_weapon_check.setChecked(
            self.current_settings.auto_select.auto_select_weapon
        )
        self.use_recommendations_check.setChecked(
            self.current_settings.auto_select.use_original_recommendations
        )

        # 显示模式
        display_mode = self.current_settings.display.character_attribute_display_mode
        if 1 <= display_mode <= 2:
            self.display_mode_group.button(display_mode).setChecked(True)

        # 基础属性区域显示选项
        self.show_basic_section_check.setChecked(
            self.current_settings.display.show_basic_attributes_section
        )

        # 基础属性内容显示选项
        basic_content_mode = self.current_settings.display.basic_attributes_display_mode
        if 1 <= basic_content_mode <= 2:
            self.basic_content_group.button(basic_content_mode).setChecked(True)

        # 根据基础属性区域显示状态设置内容选项的可用状态
        self._update_basic_content_group_state(
            self.current_settings.display.show_basic_attributes_section
        )

    def _apply_settings(self):
        """应用设置"""
        self._save_settings()

    def _restore_defaults(self):
        """恢复默认设置"""
        self.current_settings = AppSettings()
        self._load_current_settings()

    def _save_settings(self):
        """保存设置到管理器"""
        from src.config.settings import AppSettings

        # 创建新的设置对象
        new_settings = AppSettings()

        # 获取等级约束模式
        checked_button = self.level_mode_group.checkedButton()
        if checked_button:
            level_mode = self.level_mode_group.id(checked_button)
            new_settings.level_constraints.character_level_constraint_mode = level_mode

        # 获取突破约束模式
        checked_button = self.breakthrough_mode_group.checkedButton()
        if checked_button:
            breakthrough_mode = self.breakthrough_mode_group.id(checked_button)
            new_settings.level_constraints.breakthrough_constraint_mode = breakthrough_mode

        # 获取自动选择设置
        new_settings.auto_select.auto_select_weapon = self.auto_select_weapon_check.isChecked()
        new_settings.auto_select.use_original_recommendations = self.use_recommendations_check.isChecked()

        # 获取显示模式
        checked_button = self.display_mode_group.checkedButton()
        if checked_button:
            display_mode = self.display_mode_group.id(checked_button)
            new_settings.display.character_attribute_display_mode = display_mode

        # 获取基础属性显示选项
        new_settings.display.show_basic_attributes_section = self.show_basic_section_check.isChecked()

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