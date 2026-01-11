"""
驱动盘配置选项卡 - 纯UI，通过Application中间层触发事件
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QSpinBox, QFrame, QSizePolicy
)

from src.config.settings import settings_manager
from src.core.attribute_factory import AttributeFactory
from src.utils.format_utils import FormatUtils
from src.utils.gear_utils import GearUtils
from src.utils.logger import get_logger


def get_sub_attribute_by_index(index: int):
    """根据索引获取副属性"""
    sub_attrs = GearUtils.get_sub_attributes()
    if 0 <= index < len(sub_attrs):
        return sub_attrs[index]
    return None


class GearSetConfigWidget(QWidget):
    """驱动盘套装配置部件 - 纯UI"""

    gear_set_changed: pyqtSignal = pyqtSignal(list)

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.logger = get_logger(f"ui.gear_set")
        self.data_manager = data_manager

        # 获取状态管理器实例
        from src.core.state_manager import StateManager
        self.state = StateManager.instance()

        # 状态变量
        self.set_options = []  # 存储所有套装选项 (id, name)
        self.updating = False  # 防止递归调用

        # 初始化
        self._init_ui()
        self._connect_signals()
        self.populate_set_options()

    # ========== 初始化方法 ==========

    def _init_ui(self):
        """初始化UI"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 套装模式选择区域
        self._create_mode_selection_area()

        # 初始创建4+2模式
        self._create_4plus2_mode()

    def _create_mode_selection_area(self):
        """创建套装模式选择区域"""
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("套装模式："))

        self.mode_combo: QComboBox = QComboBox()
        self.mode_combo.addItems(["4+2", "2+2+2"])
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        self.layout.addLayout(mode_layout)

    def _connect_signals(self):
        """连接信号"""
        # 状态管理器信号
        self.state.state_changed.connect(self._on_state_changed)

        # UI信号
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)

    # ========== 套装模式UI创建方法 ==========

    def _create_4plus2_mode(self):
        """创建4+2模式选择器 - 纯UI"""
        self._clear_set_selectors()
        self.layout.addSpacing(20)

        # 4件套选择器
        four_label = QLabel("4件套:")
        self.layout.addWidget(four_label)

        self.four_set_combo: QComboBox = QComboBox()
        self.four_set_combo.addItem("请选择套装", "")
        self.four_set_combo.setFixedWidth(150)
        self.four_set_combo.currentIndexChanged.connect(self._on_combo_changed)
        self.layout.addWidget(self.four_set_combo)

        self.layout.addSpacing(20)

        # 2件套选择器
        two_label = QLabel("2件套:")
        self.layout.addWidget(two_label)

        self.two_set_combo: QComboBox = QComboBox()
        self.two_set_combo.addItem("请选择套装", "")
        self.two_set_combo.setFixedWidth(150)
        self.two_set_combo.currentIndexChanged.connect(self._on_combo_changed)
        self.layout.addWidget(self.two_set_combo)

        self.layout.addStretch()

    def _create_2plus2plus2_mode(self):
        """创建2+2+2模式选择器 - 纯UI"""
        self._clear_set_selectors()

        # 创建3个2件套选择器
        self.two_set_combos = []
        for i in range(3):
            self.layout.addSpacing(20)

            label = QLabel(f"2件套{i + 1}:")
            self.layout.addWidget(label)

            set_combo: QComboBox = QComboBox()
            set_combo.addItem("请选择套装", "")
            set_combo.setFixedWidth(120)
            set_combo.currentIndexChanged.connect(self._on_combo_changed)
            self.layout.addWidget(set_combo)

            self.two_set_combos.append(set_combo)

        self.layout.addStretch()

    def _clear_set_selectors(self):
        """清空套装选择器"""
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                self.layout.removeItem(item)

    # ========== 数据填充方法 ==========

    def populate_set_options(self):
        """填充套装选项 - UI更新"""
        set_options = self.data_manager.get_equipment()

        # 保存套装选项
        if set_options:
            self.set_options = set_options
        else:
            self.set_options = []
            self.logger.warning("警告: 未获取到套装选项")
            return

        # 根据当前模式填充套装选项
        if self.mode_combo.currentText() == "4+2":
            self._populate_all_combos_with_recommendations()
        else:
            self._populate_all_combos_without_recommendations()

        self.logger.info(f"已填充套装选项: {len(self.set_options)}个")

    def _populate_all_combos_with_recommendations(self):
        """为所有组合框填充带推荐标记的选项（4+2模式）"""
        if not self.set_options:
            return

        if not hasattr(self, 'four_set_combo') or not hasattr(self, 'two_set_combo'):
            return

        self._populate_combo_with_colors(self.four_set_combo, is_four=True)
        self._populate_combo_with_colors(self.two_set_combo, is_four=False)

    def _populate_all_combos_without_recommendations(self):
        """为所有组合框填充不带推荐标记的选项（2+2+2模式）"""
        if not self.set_options:
            return

        for combo in self._get_all_set_combos():
            self._populate_combo_without_colors(combo)

    def _populate_combo_with_colors(self, combo, is_four=True, recommend_data=None):
        """为组合框填充带颜色的选项"""
        if not self.set_options:
            return

        combo.blockSignals(True)
        try:
            current_id = combo.currentData()
            combo.clear()
            combo.addItem("请选择套装", "")

            # 添加所有套装选项
            for set_id, set_name in self.set_options:
                is_recommended = False
                if recommend_data and hasattr(recommend_data, 'gear_set'):
                    gear_set_data = recommend_data.gear_set
                    if gear_set_data:
                        if is_four and hasattr(gear_set_data, 'Slot4'):
                            is_recommended = str(set_id) == str(gear_set_data.Slot4)
                        elif not is_four and hasattr(gear_set_data, 'Slot2'):
                            is_recommended = str(set_id) == str(gear_set_data.Slot2)

                if is_recommended:
                    display_text = f"{set_name}"
                    combo.addItem(display_text, set_id)
                    index = combo.count() - 1
                    combo.setItemData(index, QColor("#FF4500"), Qt.ItemDataRole.ForegroundRole)
                else:
                    combo.addItem(set_name, set_id)

            # 恢复选择
            GearUtils.restore_combo_selection(combo, current_id)

        finally:
            combo.blockSignals(False)

    def _populate_combo_without_colors(self, combo):
        """为组合框填充不带颜色的选项"""
        combo.blockSignals(True)

        try:
            current_id = combo.currentData()
            combo.clear()
            combo.addItem("请选择套装", "")

            # 添加所有套装选项
            for set_id, set_name in self.set_options:
                combo.addItem(set_name, set_id)

            # 恢复当前选择
            GearUtils.restore_combo_selection(combo, current_id)

        finally:
            combo.blockSignals(False)

    # ========== 事件处理方法 ==========

    def _on_state_changed(self):
        """状态变化时更新UI颜色"""
        self._update_set_combo_colors()


    def _on_mode_changed(self, index):
        """处理模式变化"""
        if self.updating:
            return

        self.updating = True
        try:
            mode_text = "4+2" if index == 0 else "2+2+2"
            self.logger.info(f"套装模式已更改为: {mode_text}")

            # 重新创建对应模式的UI
            if index == 0:
                self._create_4plus2_mode()
            else:
                self._create_2plus2plus2_mode()

            # 重新填充选项
            self._repopulate_after_mode_change(mode_text)

        finally:
            self.updating = False

        selected_sets = self.get_selected_sets()
        self.gear_set_changed.emit(selected_sets)

    def _repopulate_after_mode_change(self, mode_text):
        """模式变更后重新填充选项"""
        if mode_text == "4+2":
            self._populate_all_combos_with_recommendations()
        else:
            self._populate_all_combos_without_recommendations()

    def _on_combo_changed(self):
        """处理套装选择器变化"""
        if self.updating:
            return

        self.updating = True
        try:
            self._update_all_combo_options()
        finally:
            self.updating = False

        selected_sets = self.get_selected_sets()
        self.gear_set_changed.emit(selected_sets)

    # ========== 套装选项管理方法 ==========

    def _update_all_combo_options(self):
        """更新所有组合框的选项，排除已选择的套装"""
        if not self.set_options:
            return

        selected_ids = self._get_all_selected_set_ids()
        for combo in self._get_all_set_combos():
            self._populate_combo_options(combo, selected_ids)

    def _populate_combo_options(self, combo, selected_ids):
        """填充单个组合框的选项，排除其他组合框已选择的套装"""
        current_id = combo.currentData()
        combo.blockSignals(True)

        try:
            combo.clear()
            combo.addItem("请选择套装", "")

            # 添加所有可用的套装选项
            for set_id, set_name in self.set_options:
                if set_id in selected_ids and set_id != current_id:
                    continue

                is_recommended = self._is_set_recommended(combo, set_id)
                GearUtils.add_set_item_to_combo(combo, set_id, set_name, is_recommended)

            # 恢复当前选择
            GearUtils.restore_combo_selection(combo, current_id)

        finally:
            combo.blockSignals(False)

    def _is_set_recommended(self, combo, set_id):
        """检查套装是否为推荐套装"""
        # 直接从状态管理器获取当前状态
        current_state = self.state.get_state()

        # 获取推荐数据
        recommend_data = current_state.recommend_data

        if not recommend_data or not hasattr(recommend_data, 'gear_set'):
            return False

        gear_set_data = recommend_data.gear_set
        if not gear_set_data:
            return False

        if combo == getattr(self, 'four_set_combo', None) and hasattr(gear_set_data, 'Slot4'):
            return str(set_id) == str(gear_set_data.Slot4)
        elif combo == getattr(self, 'two_set_combo', None) and hasattr(gear_set_data, 'Slot2'):
            return str(set_id) == str(gear_set_data.Slot2)

        return False

    # ========== 推荐数据管理方法 ==========

    def _update_set_combo_colors(self):
        """更新套装组合框的颜色显示"""
        if self.mode_combo.currentText() != "4+2":
            return

        # 直接从状态管理器获取当前状态
        current_state = self.state.get_state()

        # 获取推荐数据
        recommend_data = current_state.recommend_data if current_state.current_character else None

        self.logger.debug(f"update_set_combo_colors: recommend_data={recommend_data}")

        if not recommend_data:
            # 如果没有推荐数据，清除所有颜色标记
            if hasattr(self, 'four_set_combo'):
                self.logger.debug(f"清除4件套组合框颜色")
                self._populate_combo_without_colors(self.four_set_combo)

            if hasattr(self, 'two_set_combo'):
                self.logger.debug(f"清除2件套组合框颜色")
                self._populate_combo_without_colors(self.two_set_combo)
            return

        # 有推荐数据，正常显示颜色
        if hasattr(self, 'four_set_combo'):
            self._populate_combo_with_colors(self.four_set_combo, is_four=True, recommend_data=recommend_data)
        if hasattr(self, 'two_set_combo'):
            self._populate_combo_with_colors(self.two_set_combo, is_four=False, recommend_data=recommend_data)

    def _get_recommended_set_id(self, is_four=True):
        """获取推荐套装ID"""
        # 直接从状态管理器获取当前状态
        current_state = self.state.get_state()

        # 获取推荐数据
        recommend_data = current_state.recommend_data

        if not recommend_data or not hasattr(recommend_data, 'gear_set'):
            return None

        gear_set_data = recommend_data.gear_set
        if not gear_set_data:
            return None

        if is_four and hasattr(gear_set_data, 'Slot4'):
            return str(gear_set_data.Slot4)
        elif not is_four and hasattr(gear_set_data, 'Slot2'):
            return str(gear_set_data.Slot2)

        return None

    # ========== 工具方法 ==========

    def _get_all_set_combos(self):
        """获取所有套装选择器组合框"""
        combos = []

        if self.mode_combo.currentText() == "4+2":
            if hasattr(self, 'four_set_combo'):
                combos.append(self.four_set_combo)
            if hasattr(self, 'two_set_combo'):
                combos.append(self.two_set_combo)
        else:
            if hasattr(self, 'two_set_combos'):
                combos.extend(self.two_set_combos)

        return combos

    def _get_all_selected_set_ids(self):
        """获取所有已选择的套装ID"""
        selected_ids = []
        for combo in self._get_all_set_combos():
            set_id = combo.currentData()
            if set_id:
                selected_ids.append(set_id)
        return selected_ids

    def get_selected_sets(self):
        """获取用户选择的套装列表"""
        selected = []
        for combo in self._get_all_set_combos():
            set_id = combo.currentData()
            if set_id:
                selected.append(set_id)
        return selected

    def reset_selections(self):
        """重置所有选择"""
        for combo in self._get_all_set_combos():
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.blockSignals(False)

        if self.mode_combo.currentText() == "4+2":
            self._populate_all_combos_with_recommendations()
        else:
            self._populate_all_combos_without_recommendations()


class GearPieceEditor(QFrame):
    """单个驱动盘编辑器 - 纯UI"""

    # 配置变化信号
    main_attribute_changed: pyqtSignal = pyqtSignal(int, int, int)  # 位置, 主属性, 强化等级
    sub_attributes_changed: pyqtSignal = pyqtSignal(int, int, int, int)  # 位置, 副属性索引, 副属性ID, 强化等级

    def __init__(self, position, parent=None):
        super().__init__(parent)
        self.logger = get_logger(f"ui.gear_editor_{position}")
        self.position = position

        # 获取状态管理器实例
        from src.core.state_manager import StateManager
        self.state = StateManager.instance()

        # 状态变量
        self.selected_subs = []
        self.updating = False
        self.global_enhance_level = 15

        # 初始化
        self._init_ui()
        self._connect_signals()

    # ========== 初始化方法 ==========

    def _init_ui(self):
        """一次性初始化所有UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(320)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # 创建主属性区域
        self._create_main_attribute_area()

        # 创建副属性区域（初始隐藏）
        self.sub_group = self._create_sub_attr_ui()
        self.sub_group.setVisible(False)
        self.layout.addWidget(self.sub_group)

        self.layout.addStretch()

        # 填充初始数据
        self.populate_main_attributes()

    def _create_main_attribute_area(self):
        """创建主属性选择区域"""
        position_name = GearUtils.get_position_name(self.position)

        main_group = QGroupBox(position_name)
        self.main_layout = QVBoxLayout(main_group)
        self.main_layout.setContentsMargins(8, 15, 8, 8)

        # 主属性选择行
        self.main_row = QHBoxLayout()
        self.main_row.setSpacing(5)

        # 标签
        main_label = QLabel("主属性:")
        self.main_row.addWidget(main_label)

        # 组合框
        self.main_combo: QComboBox = QComboBox()
        self.main_combo.addItem("请选择主属性", -1)
        self.main_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.main_row.addWidget(self.main_combo, 1)

        # 数值显示标签
        self.main_value_label = QLabel("")
        self.main_value_label.setFixedWidth(70)
        self.main_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.main_value_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.main_row.addWidget(self.main_value_label)

        self.main_layout.addLayout(self.main_row)
        self.layout.addWidget(main_group)

    def _create_sub_attr_ui(self):
        """创建副属性UI组件"""
        sub_group = QGroupBox("副属性")
        sub_group.setMaximumWidth(275)
        sub_layout = QVBoxLayout(sub_group)
        sub_layout.setContentsMargins(8, 15, 8, 8)
        sub_layout.setSpacing(3)

        # 初始化副属性控件列表
        self.sub_combos = []
        self.sub_enhance_spinboxes = []
        self.sub_value_labels = []

        # 创建4个副属性行
        for i in range(4):
            self._create_sub_attribute_row(i, sub_layout)

        # 统计标签
        self._create_stats_area(sub_layout)

        return sub_group

    def _create_sub_attribute_row(self, index, parent_layout):
        """创建单个副属性行"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)

        # 标签
        sub_label = QLabel(f"副属性{index + 1}:")
        row_layout.addWidget(sub_label)

        # 组合框
        combo = QComboBox()
        combo.addItem("请选择副属性", -1)
        combo.setProperty("sub_index", index)
        combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row_layout.addWidget(combo, 1)
        self.sub_combos.append(combo)

        # 数值显示标签
        value_label = QLabel("")
        value_label.setFixedWidth(30)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value_label.setStyleSheet("color: #3498db; font-weight: bold;")
        value_label.setProperty("sub_index", index)
        row_layout.addWidget(value_label)
        self.sub_value_labels.append(value_label)

        # 强化标签
        enhance_label = QLabel("强化:")
        enhance_label.setFixedWidth(30)
        row_layout.addWidget(enhance_label)

        # 强化微调框
        enhance_spinbox = QSpinBox()
        enhance_spinbox.setRange(0, 5)
        enhance_spinbox.setValue(0)
        enhance_spinbox.setFixedWidth(50)
        enhance_spinbox.setProperty("sub_index", index)
        enhance_spinbox.setEnabled(False)
        row_layout.addWidget(enhance_spinbox)
        self.sub_enhance_spinboxes.append(enhance_spinbox)

        parent_layout.addWidget(row_widget)

    def _create_stats_area(self, parent_layout):
        """创建统计区域"""
        stats_layout = QHBoxLayout()
        stats_layout.addStretch()

        self.enhance_stats_label = QLabel("总强化: 0")
        self.enhance_stats_label.setFont(QFont("Microsoft YaHei", 8))
        self.enhance_stats_label.setStyleSheet("color: #666666;")
        stats_layout.addWidget(self.enhance_stats_label)

        parent_layout.addLayout(stats_layout)

    def _connect_signals(self):
        """连接信号"""
        self.main_combo.currentIndexChanged.connect(self._on_main_attr_changed)
        self.state.character_changed.connect(self._on_state_character_changed)

        # 副属性组合框信号
        for i, combo in enumerate(self.sub_combos):
            combo.currentIndexChanged.connect(
                lambda idx, combo_obj=combo, idx_obj=i:
                self._on_sub_attr_changed_with_obj(idx, combo_obj, idx_obj)
            )

        # 副属性强化微调框信号
        for spinbox in self.sub_enhance_spinboxes:
            spinbox.valueChanged.connect(self._on_sub_enhance_changed)

    # ========== 主属性处理方法 ==========

    def _on_main_attr_changed(self, index):
        """处理主属性变化"""
        main_attr_idx = self.main_combo.currentData()

        if main_attr_idx is not None and main_attr_idx >= 0:
            self._handle_main_attribute_selected(main_attr_idx)
        else:
            self._handle_main_attribute_deselected()

    def _handle_main_attribute_selected(self, main_attr_idx):
        """处理主属性被选择"""
        if main_attr_idx < len(GearUtils.get_main_attributes_by_position(self.position)):
            # 发出信号
            self.main_attribute_changed.emit(self.position, main_attr_idx, self.global_enhance_level)

            # 更新UI
            self._update_main_value_display()
            self.sub_group.setVisible(True)
            self._clear_all_sub_selections()
            self._update_sub_attributes()
            self._update_main_combo_colors()

    def _handle_main_attribute_deselected(self):
        """处理主属性被取消选择"""
        self.sub_group.setVisible(False)
        self._clear_all_sub_selections()
        self.main_value_label.setText("")
        self.main_combo.setStyleSheet("")

    def _update_main_value_display(self):
        """更新主属性数值显示"""
        main_attr_idx = self.main_combo.currentData()

        if main_attr_idx is None or main_attr_idx < 0:
            self.main_value_label.setText("")
            return
        main_attr_name_list = GearUtils.get_main_attributes_by_position(self.position)
        main_attr_name, main_attr_value_type = main_attr_name_list[main_attr_idx]

        main_attr = AttributeFactory().gear_main(main_attr_name, main_attr_value_type, self.global_enhance_level)
        if not main_attr:
            return

        self.main_value_label.setText(
            FormatUtils.format_attribute_display(main_attr.name, main_attr.base_value)
        )

    def _emit_main_attribute_signal(self):
        """发出主属性变化信号"""
        main_attr_idx = self.main_combo.currentData()

        if main_attr_idx is not None and main_attr_idx >= 0:
            if main_attr_idx < len(GearUtils.get_main_attributes_by_position(self.position)):
                self.main_attribute_changed.emit(self.position, main_attr_idx, self.global_enhance_level)

    # ========== 副属性处理方法 ==========

    def _on_sub_attr_changed_with_obj(self, index, combo, sub_index):
        """处理副属性变化"""
        if self.updating:
            return

        selected_sub_id = combo.currentData()
        enhance_spinbox = self.sub_enhance_spinboxes[sub_index]
        value_label = self.sub_value_labels[sub_index]

        # 发送信号
        self.logger.debug(f"发射副属性信号: position={self.position}, sub_idx={sub_index}, attr_id={selected_sub_id}")
        self._send_sub_attributes_changed_signal(selected_sub_id, sub_index)

        if index <= 0 or selected_sub_id == -1:
            GearUtils.handle_sub_attribute_deselected(combo, enhance_spinbox, value_label)
        else:
            self._handle_sub_attribute_selected(enhance_spinbox, sub_index)

        # 更新UI状态
        self._rebuild_selected_subs()
        self._update_sub_attributes()
        self._update_enhance_stats()

    def _on_sub_enhance_changed(self, value):
        """处理副属性强化次数变化"""
        sender = self.sender()
        sub_index = sender.property("sub_index")

        self._update_sub_value_display(sub_index)
        self._update_enhance_stats()

        sub_attr_id = self.sub_combos[sub_index].currentData()
        self._send_sub_attributes_changed_signal(sub_attr_id, sub_index)

    def _send_sub_attributes_changed_signal(self, sub_attr_idx, sub_index):
        """发送副属性变化信号"""
        if sub_attr_idx is None or sub_attr_idx < 0:
            return

        enhance_spinbox = self.sub_enhance_spinboxes[sub_index]
        enhance_level = enhance_spinbox.value()

        self.sub_attributes_changed.emit(
            self.position,
            sub_index,
            sub_attr_idx,
            enhance_level
        )

    def _handle_sub_attribute_selected(self, enhance_spinbox, sub_index):
        """处理副属性被选择"""
        enhance_spinbox.setEnabled(True)
        self._update_sub_value_display(sub_index)
        self.update_sub_combo_colors()

    # ========== 数据填充方法 ==========

    def populate_main_attributes(self):
        """填充主属性选项 - 使用GearUtils，带推荐标记"""
        self.updating = True

        try:
            main_attr_name_list = GearUtils.get_main_attributes_by_position(self.position)
            current_data = self.main_combo.currentData()

            self.main_combo.clear()
            self.main_combo.addItem("请选择主属性", -1)

            # 直接从状态管理器获取当前状态
            current_state = self.state.get_state()
            recommend_data = current_state.recommend_data

            # 获取推荐主属性
            recommended_main = None
            if recommend_data and hasattr(recommend_data, 'gear_mian_attribute'):
                recommended_main = recommend_data.gear_mian_attribute.get(self.position)

            # 添加所有主属性
            for idx, (main_attr_name, value) in enumerate(main_attr_name_list):
                is_recommended = recommended_main and hasattr(recommended_main, 'name') and main_attr_name == recommended_main.name
                self._add_main_attr_item(main_attr_name, idx, is_recommended)

            # 恢复选择
            self._restore_main_attr_selection(current_data)

        finally:
            self.updating = False

    def _add_main_attr_item(self, main_attr_name, idx, is_recommended):
        """添加主属性项到组合框"""
        if is_recommended:
            display_text = f"{main_attr_name}"
            self.main_combo.addItem(display_text, idx)
            index = self.main_combo.count() - 1
            self.main_combo.setItemData(index, QColor("#FF4500"), Qt.ItemDataRole.ForegroundRole)
        else:
            self.main_combo.addItem(main_attr_name, idx)

    def _restore_main_attr_selection(self, current_data):
        """恢复主属性选择"""
        if current_data is not None:
            if current_data != -1:
                new_index = self.main_combo.findData(current_data)
                if new_index >= 0:
                    self.main_combo.setCurrentIndex(new_index)
            else:
                self.main_combo.setCurrentIndex(0)

    def _update_sub_attributes(self):
        """更新所有副属性组合框的选项"""
        if self.updating:
            return

        self.updating = True

        try:
            main_attrs = GearUtils.get_main_attributes_by_position(self.position)
            main_attr_idx = self.main_combo.currentData()

            # 没有选择主属性时显示所有副属性
            if main_attr_idx is None or main_attr_idx == -1:
                for combo in self.sub_combos:
                    self._populate_sub_combo(combo, GearUtils.get_sub_attributes(), [])
                return

            # 获取主属性对象
            if main_attr_idx < len(main_attrs):
                main, value_type = main_attrs[main_attr_idx]

                # 更新每个副属性组合框
                for i, combo in enumerate(self.sub_combos):
                    current_sub_id = combo.currentData()
                    other_selected = self._get_other_selected_sub_attributes(i)
                    available_subs = self._get_available_sub_attributes([main, value_type], other_selected)
                    self._populate_sub_combo(combo, available_subs, current_sub_id)

        finally:
            self.updating = False

    def _get_other_selected_sub_attributes(self, exclude_index):
        """获取其他组合框已选择的副属性"""
        other_selected = []
        sub_attrs = GearUtils.get_sub_attributes()

        for j, other_combo in enumerate(self.sub_combos):
            if j != exclude_index:
                other_sub_id = other_combo.currentData()
                if other_sub_id is not None and 0 <= other_sub_id < len(sub_attrs):
                    sub_attr_name, sub_attr_value_type = sub_attrs[other_sub_id]
                    other_selected.append((sub_attr_name, sub_attr_value_type))

        return other_selected

    @staticmethod
    def _get_available_sub_attributes(main_attr, selected_attrs):
        """获取可用的副属性列表"""
        available = []

        for sub_attr_name, sub_attr_value_type in GearUtils.get_sub_attributes():
            # 跳过主属性
            if (sub_attr_name == main_attr[0] and
                    main_attr[1] == sub_attr_value_type):
                continue

            # 跳过其他已选择的副属性
            skip = False
            for sa_name, sa_value_type in selected_attrs:
                if (sub_attr_name == sa_name and
                        sub_attr_value_type == sa_value_type):
                    skip = True
                    break

            if not skip:
                available.append((sub_attr_name, sub_attr_value_type))

        return available

    def _populate_sub_combo(self, combo, sub_attrs, current_id):
        """填充副属性组合框，带推荐标记"""
        combo.blockSignals(True)

        try:
            combo.clear()
            combo.addItem("请选择", -1)

            # 直接从状态管理器获取当前状态
            current_state = self.state.get_state()
            recommend_data = current_state.recommend_data

            # 获取推荐的副属性
            recommended_sub = None
            if recommend_data and hasattr(recommend_data, 'gear_sub_attribute'):
                recommended_sub = recommend_data.gear_sub_attribute

            for sub_attr_name, sub_attr_value_type in sub_attrs:
                try:
                    idx = GearUtils.get_sub_attributes().index((sub_attr_name, sub_attr_value_type))
                    is_recommended = GearUtils.is_sub_attr_recommended(sub_attr_name, sub_attr_value_type, recommended_sub)
                    GearUtils.add_sub_attr_item(combo, sub_attr_name, sub_attr_value_type, idx, is_recommended)
                except ValueError:
                    continue

            # 恢复选择
            GearUtils.restore_sub_attr_selection(combo, current_id)

        finally:
            combo.blockSignals(False)

    # ========== 显示更新方法 ==========

    def _update_sub_value_display(self, sub_index):
        """更新副属性数值显示"""
        combo = self.sub_combos[sub_index]
        sub_id = combo.currentData()

        if sub_id is None or sub_id < 0:
            self.sub_value_labels[sub_index].setText("")
            return

        sub_attr_name, sub_attr_value_type  = get_sub_attribute_by_index(sub_id)
        enhance_level = self.sub_enhance_spinboxes[sub_index].value()
        sub_attr = AttributeFactory.gear_sub(sub_attr_name, sub_attr_value_type, enhance_level)

        if not sub_attr:
            return

        value = sub_attr.base_value

        if sub_attr.value_type == 2:
            value = f"{value * 100}%"

        label = self.sub_value_labels[sub_index]
        label.setText(FormatUtils.format_attribute_display(sub_attr.name, value))

    def _update_enhance_stats(self):
        """更新强化次数统计"""
        total_used = sum(spinbox.value() for spinbox in self.sub_enhance_spinboxes)
        remaining = 5 - total_used

        # 更新统计标签
        self.enhance_stats_label.setText(f"总强化: {total_used}")

        # 设置颜色
        if remaining == 0:
            self.enhance_stats_label.setStyleSheet("color: green; font-weight: bold;")
        elif remaining > 0:
            self.enhance_stats_label.setStyleSheet("color: #666666;")
        else:
            self.enhance_stats_label.setStyleSheet("color: red; font-weight: bold;")

        # 更新微调框状态
        self._update_enhance_spinboxes_state(total_used)

    def _update_enhance_spinboxes_state(self, total_used):
        """更新强化微调框状态"""
        is_full = total_used >= 5

        for i, spinbox in enumerate(self.sub_enhance_spinboxes):
            has_sub_attr = (
                i < len(self.sub_combos) and
                self.sub_combos[i].currentData() not in [None, -1]
            )

            if not has_sub_attr:
                spinbox.setEnabled(False)
                if spinbox.value() != 0:
                    spinbox.blockSignals(True)
                    spinbox.setValue(0)
                    spinbox.blockSignals(False)
                continue

            if not is_full:
                spinbox.setEnabled(True)
                spinbox.setMaximum(5)
            else:
                spinbox.setEnabled(True)
                current_value = spinbox.value()
                spinbox.setMaximum(current_value)

    def _rebuild_selected_subs(self):
        """重新构建已选择的副属性列表"""
        self.selected_subs = []
        for combo in self.sub_combos:
            sub_id = combo.currentData()
            if sub_id is not None and sub_id >= 0:
                self.selected_subs.append(sub_id)

    # ========== 推荐数据管理方法 ==========

    def _on_state_character_changed(self, character):
        """处理角色变化 - 更新推荐显示"""
        self.logger.debug(f"角色变化: {character.name if character else 'None'}")
        self._update_attribute_colors()

    def _update_attribute_colors(self):
        """更新属性选择的颜色显示"""
        self.logger.debug(f"_update_attribute_colors")
        self._update_main_combo_colors()
        self.update_sub_combo_colors()

    def _update_main_combo_colors(self):
        """更新主属性组合框的颜色显示"""
        # 直接从状态管理器获取当前状态
        current_state = self.state.get_state()
        recommend_data = current_state.recommend_data

        # 检查设置：是否使用原始推荐数据
        settings = settings_manager.get_settings()
        if not settings.auto_select.use_original_recommendations:
            self.logger.debug(f"推荐数据已禁用，清除主属性颜色")
            # 清除所有颜色标记，恢复为黑色
            for i in range(self.main_combo.count()):
                self.main_combo.setItemData(i, QColor("#000000"), Qt.ItemDataRole.ForegroundRole)
            return

        if not recommend_data or not hasattr(recommend_data, 'gear_mian_attribute'):
            self.logger.debug(f"没有推荐数据，清除主属性颜色")
            # 清除所有颜色标记
            for i in range(self.main_combo.count()):
                self.main_combo.setItemData(i, QColor("#000000"), Qt.ItemDataRole.ForegroundRole)
            return

        recommended_main = recommend_data.gear_mian_attribute.get(self.position)
        if not recommended_main:
            self.logger.debug(f"该位置没有推荐主属性")
            # 清除所有颜色标记
            for i in range(self.main_combo.count()):
                self.main_combo.setItemData(i, QColor("#000000"), Qt.ItemDataRole.ForegroundRole)
            return

        self.logger.debug(f"推荐主属性: {recommended_main.name}")

        for i in range(self.main_combo.count()):
            data = self.main_combo.itemData(i)
            if data is not None and data >= 0:
                main_attr_name_list = GearUtils.get_main_attributes_by_position(self.position)
                if data < len(main_attr_name_list):
                    attr_name, value_type = main_attr_name_list[data]
                    is_recommended = attr_name == recommended_main.name

                    if is_recommended:
                        self.logger.debug(f"设置索引 {i} 为橙色")
                        self.main_combo.setItemData(i, QColor("#FF4500"), Qt.ItemDataRole.ForegroundRole)
                    else:
                        self.main_combo.setItemData(i, QColor("#000000"), Qt.ItemDataRole.ForegroundRole)

    def update_sub_combo_colors(self):
        """更新副属性组合框的颜色显示"""
        # 直接从状态管理器获取当前状态
        current_state = self.state.get_state()
        recommend_data = current_state.recommend_data

        # 检查设置：是否使用原始推荐数据
        settings = settings_manager.get_settings()
        if not settings.auto_select.use_original_recommendations:
            self.logger.debug(f"推荐数据已禁用，清除副属性颜色")
            # 清除所有颜色标记，恢复为黑色
            for combo in self.sub_combos:
                for i in range(combo.count()):
                    combo.setItemData(i, QColor("#000000"), Qt.ItemDataRole.ForegroundRole)
            return

        if not recommend_data or not hasattr(recommend_data, 'gear_sub_attribute'):
            self.logger.debug(f"没有推荐数据，清除副属性颜色")
            # 清除所有颜色标记
            for combo in self.sub_combos:
                for i in range(combo.count()):
                    combo.setItemData(i, QColor("#000000"), Qt.ItemDataRole.ForegroundRole)
            return

        recommended_sub = recommend_data.gear_sub_attribute
        if not recommended_sub:
            self.logger.debug(f"没有推荐副属性")
            # 清除所有颜色标记
            for combo in self.sub_combos:
                for i in range(combo.count()):
                    combo.setItemData(i, QColor("#000000"), Qt.ItemDataRole.ForegroundRole)
            return

        self.logger.debug(f"推荐副属性: {recommended_sub.name}")

        for combo in self.sub_combos:
            for i in range(combo.count()):
                data = combo.itemData(i)
                if data is not None and data >= 0:
                    sub_attr_name, sub_attr_value_type = get_sub_attribute_by_index(data)
                    if sub_attr_name == recommended_sub.name and sub_attr_value_type == recommended_sub.value_type:
                        self.logger.debug(f"设置副属性组合框索引 {i} 为橙色")
                        combo.setItemData(i, QColor("#FF4500"), Qt.ItemDataRole.ForegroundRole)
                    else:
                        combo.setItemData(i, QColor("#000000"), Qt.ItemDataRole.ForegroundRole)

    # ========== 配置管理方法 ==========

    def set_global_enhance_level(self, level):
        """设置全局强化等级并触发相关更新"""
        old_level = self.global_enhance_level
        self.global_enhance_level = level

        if old_level != level and self.main_combo.currentData() >= 0:
            self._emit_main_attribute_signal()
            self._update_main_value_display()

    def _clear_all_sub_selections(self):
        """清空所有副属性选择"""
        self.selected_subs = []

        for combo in self.sub_combos:
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.blockSignals(False)

        for spinbox in self.sub_enhance_spinboxes:
            spinbox.blockSignals(True)
            spinbox.setValue(0)
            spinbox.setEnabled(False)
            spinbox.blockSignals(False)

        for label in self.sub_value_labels:
            label.setText("")

        self._update_enhance_stats()

    def clear_all(self):
        """清空所有选择"""
        self.main_combo.blockSignals(True)
        self.main_combo.setCurrentIndex(0)
        self.main_combo.blockSignals(False)

        self.main_value_label.setText("")
        self._clear_all_sub_selections()
