"""角色选项卡"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QFormLayout
)

from src.core.app import ApplicationCore
from src.ui.widgets.level_selector import LevelSelector, BreakthroughSelector, CorePassiveSelector
from src.ui.widgets.rarity_widget import RarityWidget
from src.ui.widgets.simple_combo import CharacterSelector, WeaponSelector
from src.utils.constraint_utils import ConstraintUtils
from src.utils.format_utils import FormatUtils


class CharacterTab(QWidget):
    """角色选择选项卡"""

    def __init__(self, app_core: ApplicationCore):
        super().__init__()
        print("[DEBUG CharacterTab] 初始化开始")
        self.app_core = app_core
        self.gear_tab = None

        # 初始化UI
        self._init_ui()
        self._connect_signals()

        # 初始状态：未选择角色时禁用音擎相关控件
        self._update_weapon_section_state(enabled=False)

        # 加载数据
        self._load_data_to_ui()
        print("[DEBUG CharacterTab] 初始化完成")

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
        # 角色相关信号
        self.character_combo.currentIndexChanged.connect(self._on_character_changed)
        self.character_level_selector.level_changed.connect(self._on_character_level_changed)
        self.breakthrough_selector.level_changed.connect(self._on_breakthrough_changed)
        self.core_passive_selector.level_changed.connect(self._on_core_passive_changed)

        # 武器相关信号
        self.weapon_combo.currentIndexChanged.connect(self._on_weapon_changed)
        self.weapon_level_selector.level_changed.connect(self._on_weapon_level_changed)
        self.weapon_refinement_selector.level_changed.connect(self._on_weapon_refinement_changed)
        self.weapon_talent_selector.level_changed.connect(self._on_weapon_talent_changed)

        # 应用核心信号
        self.app_core.character_changed.connect(self._on_app_character_changed)
        self.app_core.weapon_changed.connect(self._on_app_weapon_changed)

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

    def _on_character_changed(self, index):
        """处理角色选择变化"""
        print(f"[DEBUG CharacterTab] _on_character_changed 调用: index={index}")

        if index <= 0:
            # 选择了占位符项，重置状态
            print("[DEBUG CharacterTab] 选择了占位符项，重置状态")
            self._reset_character_section()
            self._update_weapon_section_state(enabled=False)
            return

        character_id = self.character_combo.get_selected_data()
        print(f"[DEBUG CharacterTab] 选择的角色ID: {character_id}")

        if character_id:
            # 启用角色等级选择器
            self._update_character_level_selectors_state(enabled=True)

            # 启用音擎区域
            self._update_weapon_section_state(enabled=True)

            # 设置角色
            print("[DEBUG CharacterTab] 调用 app_core.set_character")
            self.app_core.set_character(
                character_id=character_id,
                level=self.character_level_selector.get_value(),
                breakthrough=self.breakthrough_selector.get_value(),
                core_passive=self.core_passive_selector.get_value()
            )
        else:
            print("[DEBUG CharacterTab] 未获取到有效的角色ID")

    def _reset_character_section(self):
        """重置角色区域到初始状态"""
        # 重置角色信息显示
        self.char_name_label.setText("未选择角色")
        self.char_rarity_widget.set_rarity(-1)
        self.char_weapon_label.setText("武器类型：")
        self.char_element_label.setText("元素类型：")

        # 禁用角色等级选择器
        self._update_character_level_selectors_state(enabled=False)

        # 清空应用核心中的角色
        if self.app_core.current_character:
            self.app_core.current_character = None
            self.app_core.calculate_and_update()

    def _on_character_level_changed(self, level):
        """处理角色等级变化"""
        print(f"[DEBUG CharacterTab] _on_character_level_changed 调用: level={level}")

        # 根据等级更新突破等级范围
        print("[DEBUG CharacterTab] 更新突破等级范围")
        self._update_breakthrough_by_level(level)

        # 根据等级更新核心被动等级范围
        print("[DEBUG CharacterTab] 更新核心被动等级范围")
        self._update_core_passive_by_level(level)

        # 更新角色选择
        print("[DEBUG CharacterTab] 调用 _character_selection")
        self._character_selection()

    def _on_breakthrough_changed(self, breakthrough):
        """处理突破等级变化"""
        print(f"[DEBUG CharacterTab] _on_breakthrough_changed 调用: breakthrough={breakthrough}")

        # 根据突破等级更新角色等级范围
        print("[DEBUG CharacterTab] 更新角色等级范围")
        self._update_level_by_breakthrough(breakthrough)

        # 更新角色选择
        print("[DEBUG CharacterTab] 调用 _character_selection")
        self._character_selection()

    def _on_core_passive_changed(self, core_passive):
        """处理核心被动变化"""
        print(f"[DEBUG CharacterTab] _on_core_passive_changed 调用: core_passive={core_passive}")

        # 根据核心被动等级更新角色等级范围
        print("[DEBUG CharacterTab] 更新角色等级范围")
        self._update_level_by_core_passive(core_passive)

        # 更新角色选择
        print("[DEBUG CharacterTab] 调用 _character_selection")
        self._character_selection()

    def _character_selection(self):
        """处理角色等级变化"""
        print("[DEBUG CharacterTab] _character_selection 调用")

        if self.character_combo.currentIndex() > 0:
            character_id = self.character_combo.get_selected_data()
            print(f"[DEBUG CharacterTab] 当前角色ID: {character_id}")

            if character_id:
                print("[DEBUG CharacterTab] 调用 app_core.set_character")
                self.app_core.set_character(
                    character_id=character_id,
                    level=self.character_level_selector.get_value(),
                    breakthrough=self.breakthrough_selector.get_value(),
                    core_passive=self.core_passive_selector.get_value()
                )
        else:
            print("[DEBUG CharacterTab] 未选择角色，跳过")

    # ========== 武器相关事件处理方法 ==========

    def _on_weapon_changed(self, index):
        """处理武器选择变化"""
        if index <= 0:
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
        print(f"[DEBUG CharacterTab] _on_app_character_changed 调用: character={character.name}")

        # 更新角色信息显示
        print("[DEBUG CharacterTab] 更新角色显示")
        self._update_character_display(character)

        # 更新驱动盘选项卡的推荐数据
        print("[DEBUG CharacterTab] 更新驱动盘选项卡推荐数据")
        self._update_gear_tab_recommendations(character)

    def _on_app_weapon_changed(self, weapon):
        """处理应用核心的武器变化信号"""
        # 更新武器信息显示
        self._update_weapon_display(weapon)

    # ========== 等级约束方法 ==========

    def _update_breakthrough_by_level(self, level):
        """根据等级更新突破等级"""
        target_breakthrough = ConstraintUtils.get_breakthrough_by_character_level(level)
        current_breakthrough = self.breakthrough_selector.get_value()

        if target_breakthrough != current_breakthrough:
            self.breakthrough_selector.set_value(target_breakthrough)

    def _update_level_by_breakthrough(self, breakthrough):
        """根据突破等级更新角色等级范围"""
        level_min, level_max = ConstraintUtils.get_character_level_range_by_breakthrough(breakthrough)
        current_level = self.character_level_selector.get_value()

        # 更新等级选择器的范围
        self.character_level_selector.set_range(level_min, level_max)

        # 如果当前等级不在范围内，调整为最大值
        if current_level < level_min:
            self.character_level_selector.set_value(level_min)
        elif current_level > level_max:
            self.character_level_selector.set_value(level_max)

    def _update_core_passive_by_level(self, level):
        """根据等级更新核心被动等级"""
        target_core_passive = ConstraintUtils.get_core_passive_by_character_level(level)
        current_core_passive = self.core_passive_selector.get_value()

        if target_core_passive != current_core_passive:
            self.core_passive_selector.set_value(target_core_passive)

    def _update_level_by_core_passive(self, core_passive):
        """根据核心被动等级更新角色等级范围"""
        level_min, level_max = ConstraintUtils.get_character_level_range_by_core_passive(core_passive)
        current_level = self.character_level_selector.get_value()

        # 更新等级选择器的范围
        self.character_level_selector.set_range(level_min, level_max)

        # 如果当前等级不在范围内，调整为最小值（因为核心被动要求最低等级）
        if current_level < level_min:
            self.character_level_selector.set_value(level_min)

    def _update_weapon_refinement_by_level(self, level):
        """根据等级更新音擎突破等级"""
        target_refinement = ConstraintUtils.get_refinement_by_weapon_level(level)
        current_refinement = self.weapon_refinement_selector.get_value()

        if target_refinement != current_refinement:
            self.weapon_refinement_selector.set_value(target_refinement)

    def _update_weapon_level_by_refinement(self, refinement):
        """根据突破等级更新音擎等级范围"""
        level_min, level_max = ConstraintUtils.get_weapon_level_range_by_refinement(refinement)
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
        element_color = FormatUtils.get_element_color(element_type)
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

    def _update_gear_tab_recommendations(self, character):
        """更新驱动盘选项卡的推荐数据"""
        if self.gear_tab and hasattr(character, 'recommend'):
            # 设置驱动盘套装的推荐数据
            if hasattr(self.gear_tab, 'gear_set_config'):
                self.gear_tab.gear_set_config.set_recommend_data(character.recommend)
                # 只在4+2模式下更新颜色
                if self.gear_tab.gear_set_config.mode_combo.currentText() == "4+2":
                    self.gear_tab.gear_set_config.update_set_combo_colors()

            # 设置每个驱动盘编辑器的推荐数据
            if hasattr(self.gear_tab, 'gear_editors'):
                for position, editor in self.gear_tab.gear_editors.items():
                    if hasattr(editor, 'set_recommend_data'):
                        editor.set_recommend_data(character.recommend)
                        # 重新填充主属性选项以显示推荐标记
                        editor.populate_main_attributes()
                        # 更新副属性颜色
                        editor.update_sub_combo_colors()