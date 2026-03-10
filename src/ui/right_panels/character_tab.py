"""角色选项卡"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QFormLayout, QMessageBox
)

from src.config.constants import ColorConstants
from src.config.settings import settings_manager
from src.core.app import ApplicationCore
from src.ui.widgets.level_selector import LevelSelector, BreakthroughSelector, CorePassiveSelector
from src.ui.widgets.rarity_widget import RarityWidget
from src.ui.widgets.simple_combo import CharacterSelector, WeaponSelector
from src.utils.constraint_utils import ConstraintUtils
from src.utils.format_utils import FormatUtils
from src.utils.logger import get_logger


class CharacterTab(QWidget):
    """角色选择选项卡"""

    def __init__(self, app_core: ApplicationCore):
        super().__init__()
        self.logger = get_logger("ui.character_tab")
        self.logger.info("CharacterTab 初始化开始")
        self.app_core = app_core
        self.gear_tab = None

        # 获取状态管理器实例
        from src.core.state_manager import StateManager
        self.state = StateManager.instance()

        # 初始化设置管理器
        self.settings_manager = settings_manager
        self.constraint_utils = ConstraintUtils()

        # 初始化UI
        self._init_ui()
        self._connect_signals()

        # 初始状态：未选择角色时禁用音擎相关控件
        self._update_weapon_section_state(enabled=False)

        # 加载数据
        self._load_data_to_ui()
        self.logger.info("CharacterTab  初始化完成")

    def refresh_from_settings(self):
        """从设置刷新状态"""
        self.logger.debug("refresh_from_settings 被调用")

        # 刷新设置管理器（重新加载文件）
        self.settings_manager.refresh()

        current_state = self.state.get_state()

        # 如果当前有角色且启用了自动选择，但还没有音擎，尝试自动选择
        if current_state.current_character:
            current_weapon_id = self.weapon_combo.get_selected_data()
            self.logger.debug("当前角色: {current_state.current_character.name}, 当前武器ID: {current_weapon_id}")

            # 获取当前设置
            settings = self.settings_manager.get_settings()
            self.logger.debug("自动选择音擎设置: {settings.auto_select.auto_select_weapon}")

            if settings.auto_select.auto_select_weapon:
                if not current_weapon_id or current_weapon_id == -1:
                    self.logger.debug("启用了自动选择且当前没有音擎，尝试自动选择")
                    self._auto_select_character_weapon(current_state.current_character)
                else:
                    self.logger.debug("已有音擎选择，不自动选择")
            else:
                self.logger.debug("自动选择音擎已禁用")
        else:
            self.logger.debug("当前没有选择角色")

    # ========== 公共接口方法 ==========

    def set_gear_tab_reference(self, gear_tab):
        """设置对GearTab的引用"""
        self.gear_tab = gear_tab

    # ========== UI初始化方法 ==========

    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 角色选择区域
        self._create_character_section(main_layout)

        # 音擎选择区域
        self._create_weapon_section(main_layout)

        main_layout.addStretch()

    def _create_character_section(self, parent_layout):
        """创建角色选择区域"""
        character_group = QGroupBox("角色选择")
        character_group.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))

        group_layout = QVBoxLayout(character_group)
        group_layout.setSpacing(15)

        # 表单布局
        char_form_layout = QFormLayout()
        char_form_layout.setVerticalSpacing(12)
        char_form_layout.setHorizontalSpacing(20)

        # 角色下拉选择
        self.character_combo = CharacterSelector()
        self.character_combo.setFixedWidth(400)

        # 角色信息显示
        self.character_info_widget = self._create_character_info_widget()

        # 角色等级选择器
        level_widget = self._create_character_level_selectors()

        # 添加到布局
        char_form_layout.addRow("选择角色：", self.character_combo)
        char_form_layout.addRow("角色信息：", self.character_info_widget)
        char_form_layout.addRow("角色培养：", level_widget)

        group_layout.addLayout(char_form_layout)
        parent_layout.addWidget(character_group)

    def _create_character_info_widget(self):
        """创建角色信息显示部件"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        # 角色名称
        self.char_name_label = QLabel("未选择角色")
        self.char_name_label.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        self.char_name_label.setStyleSheet("color: #2c3e50;")

        # 稀有度显示
        self.char_rarity_widget = RarityWidget()

        # 详细信息标签
        self.char_weapon_label = QLabel("武器类型：")
        self.char_weapon_label.setFont(QFont("Microsoft YaHei", 10))

        self.char_element_label = QLabel("元素类型：")
        self.char_element_label.setFont(QFont("Microsoft YaHei", 10))

        # 布局
        layout.addWidget(self.char_name_label, 0, 0, 1, 1)
        layout.addWidget(self.char_rarity_widget, 0, 1, 1, 1, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.char_weapon_label, 1, 0, 1, 2)
        layout.addWidget(self.char_element_label, 2, 0, 1, 2)

        # 设置背景
        widget.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
        """)

        return widget

    def _create_character_level_selectors(self):
        """创建角色等级选择器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # 角色等级选择器 (1-60)
        self.character_level_selector = LevelSelector("角色等级", 1, 60)
        self.character_level_selector.set_value(60)
        self.character_level_selector.setEnabled(False)  # 初始禁用

        # 突破等级选择器 (1-6)
        self.breakthrough_selector = BreakthroughSelector(6)
        self.breakthrough_selector.set_value(6)
        self.breakthrough_selector.setEnabled(False)  # 初始禁用

        # 核心被动等级选择器 (1-7)
        self.core_passive_selector = CorePassiveSelector(7)
        self.core_passive_selector.set_value(7)
        self.core_passive_selector.setEnabled(False)  # 初始禁用

        layout.addWidget(self.character_level_selector)
        layout.addWidget(self.breakthrough_selector)
        layout.addWidget(self.core_passive_selector)
        layout.addStretch()

        return widget

    def _create_weapon_section(self, parent_layout):
        """创建音擎选择区域"""
        self.weapon_group = QGroupBox("音擎选择")
        self.weapon_group.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))

        group_layout = QVBoxLayout(self.weapon_group)
        group_layout.setSpacing(15)

        self.weapon_form_layout = QFormLayout()
        self.weapon_form_layout.setVerticalSpacing(12)
        self.weapon_form_layout.setHorizontalSpacing(20)

        # 音擎下拉选择
        self.weapon_combo = WeaponSelector()
        self.weapon_combo.setFixedWidth(400)

        # 音擎信息显示
        self.weapon_info_widget = self._create_weapon_info_widget()

        # 音擎等级选择器
        self.weapon_level_widget = self._create_weapon_level_selectors()

        self.weapon_form_layout.addRow("选择音擎：", self.weapon_combo)
        self.weapon_form_layout.addRow("音擎信息：", self.weapon_info_widget)
        self.weapon_form_layout.addRow("音擎培养：", self.weapon_level_widget)

        group_layout.addLayout(self.weapon_form_layout)
        parent_layout.addWidget(self.weapon_group)

    def _create_weapon_info_widget(self):
        """创建音擎信息显示部件"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        # 音擎名称
        self.weapon_name_label = QLabel("未选择音擎")
        self.weapon_name_label.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        self.weapon_name_label.setStyleSheet("color: #2c3e50;")

        # 稀有度显示
        self.weapon_rarity_widget = RarityWidget()

        # 详细信息标签
        self.weapon_type_label = QLabel("武器类型：")
        self.weapon_type_label.setFont(QFont("Microsoft YaHei", 10))

        self.weapon_attr_label = QLabel("主属性：")
        self.weapon_attr_label.setFont(QFont("Microsoft YaHei", 10))

        # 布局
        layout.addWidget(self.weapon_name_label, 0, 0, 1, 1)
        layout.addWidget(self.weapon_rarity_widget, 0, 1, 1, 1, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.weapon_type_label, 1, 0, 1, 2)
        layout.addWidget(self.weapon_attr_label, 2, 0, 1, 2)

        # 设置背景
        widget.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
        """)

        return widget

    def _create_weapon_level_selectors(self):
        """创建音擎等级选择器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # 音擎等级选择器 (1-60)
        self.weapon_level_selector = LevelSelector("音擎等级", 1, 60)
        self.weapon_level_selector.set_value(60)
        self.weapon_level_selector.setEnabled(False)  # 初始禁用

        # 突破等级选择器 (0-5)
        self.weapon_refinement_selector = LevelSelector("突破等级", 0, 5)
        self.weapon_refinement_selector.set_value(5)
        self.weapon_refinement_selector.setEnabled(False)  # 初始禁用

        # 天赋等级选择器 (1-5)
        self.weapon_talent_selector = LevelSelector("天赋等级", 1, 5)
        self.weapon_talent_selector.set_value(1)
        self.weapon_talent_selector.setEnabled(False)  # 初始禁用

        layout.addWidget(self.weapon_level_selector)
        layout.addWidget(self.weapon_refinement_selector)
        layout.addWidget(self.weapon_talent_selector)
        layout.addStretch()

        return widget

    # ========== 数据加载方法 ==========

    def _load_data_to_ui(self):
        """加载数据到UI"""
        # 填充角色下拉框
        characters = self.app_core.data_manager.get_all_characters()
        self.character_combo.populate_from_data(characters)

        # 填充武器下拉框
        weapons = self.app_core.data_manager.get_all_weapons()
        self.weapon_combo.populate_from_data(weapons)

    # ========== 信号连接方法 ==========

    def _connect_signals(self):
        """连接信号"""
        # 状态管理器信号
        self.state.character_changed.connect(self._on_state_character_changed)
        self.state.weapon_changed.connect(self._on_state_weapon_changed)
        self.state.character_cleared.connect(self._on_state_character_changed)
        self.state.weapon_cleared.connect(self._on_state_weapon_changed)

        # UI控件信号
        self.character_combo.currentIndexChanged.connect(self._on_character_changed)
        self.weapon_combo.currentIndexChanged.connect(self._on_weapon_changed)

        # 等级选择器信号
        self.character_level_selector.level_changed.connect(self._on_character_level_changed)
        self.breakthrough_selector.level_changed.connect(self._on_breakthrough_changed)
        self.core_passive_selector.level_changed.connect(self._on_core_passive_changed)
        self.weapon_level_selector.level_changed.connect(self._on_weapon_level_changed)
        self.weapon_refinement_selector.level_changed.connect(self._on_weapon_refinement_changed)
        self.weapon_talent_selector.level_changed.connect(self._on_weapon_talent_changed)

    # ========== 状态更新方法 ==========

    def _update_weapon_section_state(self, enabled: bool):
        """更新音擎区域的状态"""
        # 更新组合框状态
        self.weapon_combo.setEnabled(enabled)

        # 更新等级选择器状态
        self.weapon_level_selector.setEnabled(enabled)
        self.weapon_refinement_selector.setEnabled(enabled)
        self.weapon_talent_selector.setEnabled(enabled)

        # 更新组框标题颜色提示
        if enabled:
            self.weapon_group.setStyleSheet("QGroupBox { color: #2c3e50; }")
        else:
            self.weapon_group.setStyleSheet("QGroupBox { color: #95a5a6; }")

    def _update_character_level_selectors_state(self, enabled: bool):
        """更新角色等级选择器状态"""
        self.character_level_selector.setEnabled(enabled)
        self.breakthrough_selector.setEnabled(enabled)
        self.core_passive_selector.setEnabled(enabled)

    # ========== 角色相关事件处理方法 ==========

    def _on_state_character_changed(self, character):
        """处理角色状态变化"""
        if character:
            self._update_character_display(character)
            self._update_character_level_selectors_state(enabled=True)
            self._update_weapon_section_state(enabled=True)

        else:
            # 角色被清空
            self._reset_character_section()
            self._update_weapon_section_state(enabled=False)

    def _on_state_weapon_changed(self, weapon):
        """处理武器状态变化"""
        if weapon:
            self._update_weapon_display(weapon)
        else:
            self._reset_weapon_section()

    def _on_character_changed(self, index):
        """处理角色选择变化"""
        self.logger.debug(f"_on_character_changed 调用: index={index}")

        if index <= 0:
            # 选择了占位符项，重置状态
            self.logger.debug("选择了占位符项，重置状态")
            # 清空应用核心中的角色选择
            self.app_core.set_character(None)

            return

        character_id = self.character_combo.get_selected_data()
        self.logger.debug(f"选择的角色ID: {character_id}")

        if character_id:
            # 获取角色对象
            character = self.app_core.data_manager.get_character(character_id)
            if not character:
                self.logger.error(f"[ERROR CharacterTab] 未找到角色: {character_id} type: {type(character_id)}")
                return

            # 设置角色
            self.logger.debug("调用 app_core.set_character")
            self.app_core.set_character(
                character_id=character_id,
                level=self.character_level_selector.get_value(),
                breakthrough=self.breakthrough_selector.get_value(),
                core_passive=self.core_passive_selector.get_value()
            )

            # 检查是否需要自动选择专属音擎
            self._handle_auto_weapon_selection(character)
        else:
            self.logger.debug("未获取到有效的角色ID")

    def _handle_auto_weapon_selection(self, character):
        """处理自动武器选择逻辑"""
        # 获取当前设置
        settings = self.settings_manager.get_settings()
        auto_select_enabled = settings.auto_select.auto_select_weapon

        self.logger.debug(f"自动选择音擎设置: {auto_select_enabled}")

        if auto_select_enabled:
            # 如果启用了自动选择，尝试选择专属音擎
            current_weapon_id = self.weapon_combo.get_selected_data()
            self.logger.debug(f"当前武器ID: {current_weapon_id}")

            if not current_weapon_id or current_weapon_id == -1:
                self.logger.debug("当前没有选择武器，执行自动选择")
                self._auto_select_character_weapon(character)
            else:
                self.logger.debug("已有武器选择，跳过自动选择")
        else:
            self.logger.debug("自动选择音擎已禁用，跳过自动选择")

    def _should_auto_select_weapon(self) -> bool:
        """检查是否应该自动选择专属音擎"""
        settings = self.settings_manager.get_settings()
        auto_select = settings.auto_select.auto_select_weapon
        self.logger.debug(f"_should_auto_select_weapon: {auto_select}")
        return auto_select

    def _auto_select_character_weapon(self, character):
        """自动选择角色的专属音擎"""
        try:
            # 构造专属音擎ID: 1{稀有度}{角色ID//10}
            weapon_id_str = f"1{character.rarity}{character.id // 10}"
            weapon_id = int(weapon_id_str)

            self.logger.debug("尝试自动选择专属音擎: ID={weapon_id}")

            # 尝试获取音擎
            weapon = self.app_core.data_manager.get_weapon(weapon_id)
            if weapon:
                self.logger.debug("找到专属音擎: {weapon.name}")

                # 在组合框中查找并选择该音擎
                found = False
                for i in range(self.weapon_combo.count()):
                    if self.weapon_combo.itemData(i) == weapon_id:
                        self.logger.debug(f"在组合框中找到音擎，索引: {i}")
                        self.weapon_combo.setCurrentIndex(i)
                        found = True
                        break

                if found:
                    self.logger.debug("自动选择音擎成功")
                    # 选择武器后，应用核心会通过信号自动处理武器设置
                else:
                    self.logger.debug("音擎在列表中但未找到")
                    self._show_weapon_not_found_warning(weapon_id)
            else:
                self.logger.debug(f"未找到音擎: {weapon_id}")
                self._show_weapon_not_found_warning(weapon_id)

        except Exception as e:
            self.logger.error(f"自动选择音擎失败: {e}")
            import traceback
            traceback.print_exc()

    def _show_weapon_not_found_warning(self, weapon_id: int):
        """显示未找到音擎的警告"""
        QMessageBox.information(
            self,
            "自动选择音擎",
            f"未找到角色的专属音擎 (ID: {weapon_id})\n"
            "请检查使用的数据文件是否与计算器适配。"
        )

    def _clear_gear_tab_recommendations(self):
        """清除驱动盘选项卡的推荐标记"""
        if self.gear_tab:
            # 清除套装配置的推荐数据
            if hasattr(self.gear_tab, 'gear_set_config'):
                self.gear_tab.gear_set_config.recommend_data = None
                # 更新套装选择器颜色
                self.gear_tab.gear_set_config.update_set_combo_colors()

    def _reset_character_section(self):
        """重置角色区域到初始状态"""
        # 重置角色信息显示
        self.char_name_label.setText("未选择角色")
        self.char_rarity_widget.set_rarity(-1)
        self.char_weapon_label.setText("武器类型：")
        self.char_element_label.setText("元素类型：")

        # 禁用角色等级选择器
        self._update_character_level_selectors_state(enabled=False)

        # 重置音擎区域
        self._reset_weapon_section()

    def _reset_weapon_section(self):
        """重置音擎区域"""
        # 重置音擎选择器
        self.weapon_combo.setCurrentIndex(0)

        # 重置音擎信息显示
        self.weapon_name_label.setText("未选择音擎")
        self.weapon_rarity_widget.set_rarity(-1)
        self.weapon_type_label.setText("武器类型：")
        self.weapon_attr_label.setText("主属性：")

        # 重置音擎等级选择器
        self.weapon_level_selector.set_value(60)
        self.weapon_refinement_selector.set_value(5)
        self.weapon_talent_selector.set_value(1)

    def _on_character_level_changed(self, level):
        """处理角色等级变化"""
        self.logger.debug("_on_character_level_changed 调用: level={level}")

        # 根据等级更新突破等级范围
        self.logger.debug("更新突破等级范围")
        self._update_breakthrough_by_level(level)

        # 根据等级更新核心被动等级范围
        self.logger.debug("更新核心被动等级范围")
        self._update_core_passive_by_level(level)

        # 更新角色选择
        self.logger.debug("调用 _character_selection")
        self._character_selection()

    def _on_breakthrough_changed(self, breakthrough):
        """处理突破等级变化"""
        self.logger.debug("_on_breakthrough_changed 调用: breakthrough={breakthrough}")

        # 根据突破等级更新角色等级范围
        self.logger.debug("更新角色等级范围")
        self._update_level_by_breakthrough(breakthrough)

        # 更新角色选择
        self.logger.debug("调用 _character_selection")
        self._character_selection()

    def _on_core_passive_changed(self, core_passive):
        """处理核心被动变化"""
        self.logger.debug("_on_core_passive_changed 调用: core_passive={core_passive}")

        # 根据核心被动等级更新角色等级范围
        self.logger.debug("更新角色等级范围")
        self._update_level_by_core_passive(core_passive)

        # 更新角色选择
        self.logger.debug("调用 _character_selection")
        self._character_selection()

    def _character_selection(self):
        """处理角色等级变化"""
        self.logger.debug("_character_selection 调用")

        if self.character_combo.currentIndex() > 0:
            character_id = self.character_combo.get_selected_data()
            self.logger.debug("当前角色ID: {character_id}")

            if character_id:
                self.logger.debug("调用 app_core.set_character")
                self.app_core.set_character(
                    character_id=character_id,
                    level=self.character_level_selector.get_value(),
                    breakthrough=self.breakthrough_selector.get_value(),
                    core_passive=self.core_passive_selector.get_value()
                )
        else:
            self.logger.debug("未选择角色，跳过")

    # ========== 武器相关事件处理方法 ==========

    def _on_weapon_changed(self, index):
        """处理武器选择变化"""
        if index <= 0:
            self.app_core.set_weapon(None)
            return

        weapon_id = self.weapon_combo.get_selected_data()
        if weapon_id:
            self.app_core.set_weapon(
                weapon_id=weapon_id,
                level=self.weapon_level_selector.get_value(),
                refinement=self.weapon_refinement_selector.get_value(),
                talent=self.weapon_talent_selector.get_value()
            )

    def _on_weapon_level_changed(self, level):
        """处理音擎等级变化"""
        # 根据等级更新突破等级范围
        self._update_weapon_refinement_by_level(level)

        # 更新武器选择
        self._weapon_selection()

    def _on_weapon_refinement_changed(self, refinement):
        """处理精炼等级变化"""
        # 根据突破等级更新音擎等级范围
        self._update_weapon_level_by_refinement(refinement)

        # 更新武器选择
        self._weapon_selection()

    def _on_weapon_talent_changed(self, talent):
        """处理天赋等级变化"""
        self._weapon_selection()

    def _weapon_selection(self):
        """处理武器选择变化"""
        weapon_id = self.weapon_combo.get_selected_data()
        if weapon_id:
            self.app_core.set_weapon(
                weapon_id=weapon_id,
                level=self.weapon_level_selector.get_value(),
                refinement=self.weapon_refinement_selector.get_value(),
                talent=self.weapon_talent_selector.get_value(),
                flag=True
            )

    # ========== 应用核心事件处理方法 ==========

    def _on_app_character_changed(self, character):
        """处理应用核心的角色变化信号"""
        self.logger.debug("_on_app_character_changed 调用: character={character.name}")

        # 更新角色信息显示
        self._update_character_display(character)

        # 获取当前设置状态
        settings = self.settings_manager.get_settings()
        self.logger.debug("使用原始推荐数据设置: {settings.auto_select.use_original_recommendations}")

        # 根据设置决定是否更新驱动盘选项卡的推荐数据
        if settings.auto_select.use_original_recommendations:
            self.logger.debug("启用推荐数据，更新驱动盘选项卡")
        else:
            self.logger.debug("禁用推荐数据，不更新驱动盘选项卡")
            # 如果禁用了推荐数据，应该清除驱动盘选项卡的推荐标记
            self._clear_gear_tab_recommendations()

    def _on_app_weapon_changed(self, weapon):
        """处理应用核心的武器变化信号"""
        # 更新武器信息显示
        self._update_weapon_display(weapon)

    # ========== 等级约束方法 ==========

    def _update_breakthrough_by_level(self, level):
        """根据等级更新突破等级"""
        settings = self.settings_manager.get_settings()
        mode = settings.level_constraints.character_level_constraint_mode

        if mode == 3:
            # 模式3：渐进模式，需要特殊处理
            current_breakthrough = self.breakthrough_selector.get_value()
            min_level, max_level = self.constraint_utils.LEVEL_RANGES[current_breakthrough]

            if level > max_level:
                # 等级超过当前突破上限，升级突破
                new_breakthrough = self.constraint_utils.get_breakthrough_by_character_level(level, mode=1)
                if new_breakthrough > current_breakthrough:
                    self.breakthrough_selector.set_value(new_breakthrough)
            # 如果等级降低到低于当前突破的最小值，不自动降级突破
        else:
            # 模式1和模式2
            target_breakthrough = self.constraint_utils.get_breakthrough_by_character_level(level, mode)
            current_breakthrough = self.breakthrough_selector.get_value()

            if target_breakthrough != current_breakthrough:
                self.breakthrough_selector.set_value(target_breakthrough)

    def _update_level_by_breakthrough(self, breakthrough):
        """根据突破等级更新角色等级"""
        settings = self.settings_manager.get_settings()
        mode = settings.level_constraints.breakthrough_constraint_mode

        level_min, level_max = self.constraint_utils.get_character_level_range_by_breakthrough(breakthrough, mode)
        current_level = self.character_level_selector.get_value()

        # 更新等级选择器的范围
        self.character_level_selector.set_range(level_min, level_max)

        # 根据模式调整等级
        if mode == 1:
            # 模式1：设置为最大值
            if current_level != level_max:
                self.character_level_selector.set_value(level_max)
        elif mode == 2:
            # 模式2：设置为最小值
            if current_level != level_min:
                self.character_level_selector.set_value(level_min)
        else:
            # 其他模式：如果当前等级不在范围内，调整
            if current_level < level_min:
                self.character_level_selector.set_value(level_min)
            elif current_level > level_max:
                self.character_level_selector.set_value(level_max)

    def _update_core_passive_by_level(self, level):
        """根据等级更新核心被动等级"""
        target_core_passive = self.constraint_utils.get_core_passive_by_character_level(level)
        current_core_passive = self.core_passive_selector.get_value()

        if target_core_passive != current_core_passive:
            self.core_passive_selector.set_value(target_core_passive)

    def _update_level_by_core_passive(self, core_passive):
        """根据核心被动等级更新角色等级范围"""
        level_min, level_max = self.constraint_utils.get_character_level_range_by_core_passive(core_passive)
        current_level = self.character_level_selector.get_value()

        # 更新等级选择器的范围
        self.character_level_selector.set_range(level_min, level_max)

        # 如果当前等级不在范围内，调整为最小值
        if current_level < level_min:
            self.character_level_selector.set_value(level_min)

    def _update_weapon_refinement_by_level(self, level):
        """根据等级更新音擎突破等级"""
        target_refinement = self.constraint_utils.get_refinement_by_weapon_level(level)
        current_refinement = self.weapon_refinement_selector.get_value()

        if target_refinement != current_refinement:
            self.weapon_refinement_selector.set_value(target_refinement)

    def _update_weapon_level_by_refinement(self, refinement):
        """根据突破等级更新音擎等级范围"""
        level_min, level_max = self.constraint_utils.get_weapon_level_range_by_refinement(refinement)
        current_level = self.weapon_level_selector.get_value()

        # 更新等级选择器的范围
        self.weapon_level_selector.set_range(level_min, level_max)

        # 如果当前等级不在范围内，调整为最大值
        if current_level < level_min:
            self.weapon_level_selector.set_value(level_min)
        elif current_level > level_max:
            self.weapon_level_selector.set_value(level_max)

    # ========== UI显示更新方法 ==========

    def _update_character_display(self, character):
        """更新角色信息显示"""
        # 更新名称
        display_name = character.name
        self.char_name_label.setText(display_name)

        # 更新稀有度
        self.char_rarity_widget.set_rarity(character.rarity)

        # 更新武器类型
        self.char_weapon_label.setText(f"武器类型：{character.weapon_type}")

        # 更新元素类型（带颜色）
        element_type = character.element_type
        element_color = ColorConstants.ELEMENT_COLORS.get(element_type, "#808080")
        element_html = f"元素类型：<span style='color:{element_color}; font-weight:bold;'>{element_type}</span>"
        self.char_element_label.setText(element_html)

    def _update_weapon_display(self, weapon):
        """更新武器信息显示"""
        # 更新名称
        self.weapon_name_label.setText(weapon.name)

        # 更新稀有度
        self.weapon_rarity_widget.set_rarity(weapon.rarity)

        # 更新武器类型
        self.weapon_type_label.setText(f"武器类型：{weapon.weapon_type}")

        # 更新高级属性
        if weapon.actual_advanced_attribute:
            display_value = FormatUtils.format_attribute_display(
                weapon.actual_advanced_attribute.name,
                weapon.actual_advanced_attribute.base_value
            )
            self.weapon_attr_label.setText(f"高级属性：{weapon.actual_advanced_attribute.name} {display_value}")
