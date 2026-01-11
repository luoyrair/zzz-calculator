"""
设置对话框 - 各设置页面
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QRadioButton, QCheckBox,
    QButtonGroup, QFormLayout
)

from src.config.settings import AppSettings


class GeneralSettingsPage(QWidget):
    """通用设置页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 自动选择设置组
        self._create_auto_select_group(layout)

        layout.addStretch()

    def _create_auto_select_group(self, parent_layout):
        """创建自动选择设置组"""
        group = QGroupBox("自动选择设置")
        group_layout = QFormLayout(group)
        group_layout.setVerticalSpacing(10)
        group_layout.setHorizontalSpacing(20)

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

    def load_settings(self, settings: AppSettings):
        """加载设置"""
        self.auto_select_weapon_check.setChecked(
            settings.auto_select.auto_select_weapon
        )
        self.use_recommendations_check.setChecked(
            settings.auto_select.use_original_recommendations
        )

    def save_settings(self, settings: AppSettings):
        """保存设置"""
        settings.auto_select.auto_select_weapon = self.auto_select_weapon_check.isChecked()
        settings.auto_select.use_original_recommendations = self.use_recommendations_check.isChecked()


class DisplaySettingsPage(QWidget):
    """显示设置页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 角色属性显示模式
        self._create_display_mode_group(layout)

        # 基础属性显示设置
        self._create_basic_attributes_group(layout)

        layout.addStretch()

    def _create_display_mode_group(self, parent_layout):
        """创建显示模式设置组"""
        group = QGroupBox("角色属性显示模式")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)

        self.display_mode_group = QButtonGroup(self)

        # 模式1：显示角色面板属性
        display_mode1 = QRadioButton("显示角色面板属性")
        display_mode1.setToolTip("显示角色基础属性 + 武器基础属性 + 驱动盘属性\n不包含音擎天赋属性")
        self.display_mode_group.addButton(display_mode1, 1)
        group_layout.addWidget(display_mode1)

        # 模式2：显示角色局内属性
        display_mode2 = QRadioButton("显示角色局内属性")
        display_mode2.setToolTip("显示角色面板属性 + 音擎天赋属性")
        self.display_mode_group.addButton(display_mode2, 2)
        group_layout.addWidget(display_mode2)

        parent_layout.addWidget(group)

    def _create_basic_attributes_group(self, parent_layout):
        """创建基础属性显示设置组"""
        group = QGroupBox("属性显示设置")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(15)

        # 基础属性区域显示选项
        self.show_basic_section_check = QCheckBox("显示角色基础属性区域")
        self.show_basic_section_check.setToolTip(
            "启用后，左侧面板将显示角色基础属性区域\n"
            "当不显示时，基础属性内容设置仍然保存但暂时不生效"
        )
        group_layout.addWidget(self.show_basic_section_check)

        # 基础属性内容显示选项
        basic_content_group = QGroupBox("属性区域显示内容")
        # 重要：这里不设置禁用，让用户始终可以配置
        basic_content_group.setToolTip(
            "当基础属性区域显示时，控制显示哪些属性\n"
            "此设置始终保存，无论基础属性区域是否显示"
        )
        basic_content_layout = QVBoxLayout(basic_content_group)
        basic_content_layout.setSpacing(8)

        self.basic_content_group = QButtonGroup(self)

        # 模式1：显示角色基础属性
        basic_mode1 = QRadioButton("显示角色基础属性")
        basic_mode1.setToolTip("根据角色类型显示对应的基础属性（如命破角色显示贯穿力等）")
        self.basic_content_group.addButton(basic_mode1, 1)
        basic_content_layout.addWidget(basic_mode1)

        # 模式2：显示所有属性
        basic_mode2 = QRadioButton("显示所有属性")
        basic_mode2.setToolTip("显示所有可能的属性（包括不常用的属性）")
        self.basic_content_group.addButton(basic_mode2, 2)
        basic_content_layout.addWidget(basic_mode2)

        group_layout.addWidget(basic_content_group)
        parent_layout.addWidget(group)

    def load_settings(self, settings: AppSettings):
        """加载设置"""
        # 显示模式
        display_mode = settings.display.character_attribute_display_mode
        if 1 <= display_mode <= 2:
            self.display_mode_group.button(display_mode).setChecked(True)

        # 基础属性区域显示选项
        self.show_basic_section_check.setChecked(
            settings.display.show_basic_attributes_section
        )

        # 基础属性内容显示选项
        basic_content_mode = settings.display.basic_attributes_display_mode
        if 1 <= basic_content_mode <= 2:
            self.basic_content_group.button(basic_content_mode).setChecked(True)


    def save_settings(self, settings: AppSettings):
        """保存设置"""
        # 显示模式
        checked_button = self.display_mode_group.checkedButton()
        if checked_button:
            display_mode = self.display_mode_group.id(checked_button)
            settings.display.character_attribute_display_mode = display_mode

        # 基础属性显示选项
        settings.display.show_basic_attributes_section = self.show_basic_section_check.isChecked()

        # 基础属性内容显示选项
        checked_button = self.basic_content_group.checkedButton()
        if checked_button:
            basic_content_mode = self.basic_content_group.id(checked_button)
            settings.display.basic_attributes_display_mode = basic_content_mode


class ConstraintsSettingsPage(QWidget):
    """等级约束设置页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 等级变化约束模式
        self._create_level_constraint_group(layout)

        # 突破等级变化约束模式
        self._create_breakthrough_constraint_group(layout)

        layout.addStretch()

    def _create_level_constraint_group(self, parent_layout):
        """创建等级变化约束模式设置组"""
        group = QGroupBox("等级变化时的突破等级设置")
        group.setToolTip("当角色等级发生变化时，如何自动设置突破等级")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)

        self.level_mode_group = QButtonGroup(self)

        # 模式1：默认模式
        mode1 = QRadioButton("模式1：自动升级突破")
        mode1.setToolTip(
            "当等级超过当前突破上限时自动升级突破\n"
            "例如：等级=50 → 突破等级=5 (因为50>40且≤50)"
        )
        self.level_mode_group.addButton(mode1, 1)
        group_layout.addWidget(mode1)

        # 模式2：保守模式
        mode2 = QRadioButton("模式2：保守模式")
        mode2.setToolTip(
            "更保守的模式，需要等级达到当前突破等级的上限才会升级突破\n"
            "例如：等级=41 → 突破等级=4 (因为41>40但未达到50)"
        )
        self.level_mode_group.addButton(mode2, 2)
        group_layout.addWidget(mode2)

        # 模式3：手动模式（未实现）
        mode3 = QRadioButton("模式3：手动模式（未实现）")
        mode3.setToolTip("等级达到当前突破上限时不会自动升级突破，需要手动升级突破等级")
        mode3.setEnabled(False)  # 暂时禁用
        self.level_mode_group.addButton(mode3, 3)
        group_layout.addWidget(mode3)

        parent_layout.addWidget(group)

    def _create_breakthrough_constraint_group(self, parent_layout):
        """创建突破等级变化约束模式设置组"""
        group = QGroupBox("突破等级变化时的角色等级设置")
        group.setToolTip("当突破等级发生变化时，如何自动设置角色等级")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)

        self.breakthrough_mode_group = QButtonGroup(self)

        # 模式1：设置到最大值
        bmode1 = QRadioButton("模式1：设置到最大值")
        bmode1.setToolTip("将角色等级设置为该突破等级的最大值\n例如：突破等级=5 → 等级=50")
        self.breakthrough_mode_group.addButton(bmode1, 1)
        group_layout.addWidget(bmode1)

        # 模式2：设置到最小值
        bmode2 = QRadioButton("模式2：设置到最小值")
        bmode2.setToolTip("将角色等级设置为该突破等级的最小值\n例如：突破等级=5 → 等级=40")
        self.breakthrough_mode_group.addButton(bmode2, 2)
        group_layout.addWidget(bmode2)

        parent_layout.addWidget(group)

    def load_settings(self, settings: AppSettings):
        """加载设置"""
        # 等级约束模式
        level_mode = settings.level_constraints.character_level_constraint_mode
        if 1 <= level_mode <= 3:
            self.level_mode_group.button(level_mode).setChecked(True)

        # 突破约束模式
        breakthrough_mode = settings.level_constraints.breakthrough_constraint_mode
        if 1 <= breakthrough_mode <= 2:
            self.breakthrough_mode_group.button(breakthrough_mode).setChecked(True)

    def save_settings(self, settings: AppSettings):
        """保存设置"""
        # 等级约束模式
        checked_button = self.level_mode_group.checkedButton()
        if checked_button:
            level_mode = self.level_mode_group.id(checked_button)
            settings.level_constraints.character_level_constraint_mode = level_mode

        # 突破约束模式
        checked_button = self.breakthrough_mode_group.checkedButton()
        if checked_button:
            breakthrough_mode = self.breakthrough_mode_group.id(checked_button)
            settings.level_constraints.breakthrough_constraint_mode = breakthrough_mode