"""更新左侧面板 - 适配新架构"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QGroupBox,
    QFormLayout, QLabel
)

from src.config.constants import ColorConstants
from src.config.settings import settings_manager
from src.ui.widgets.attribute_display import AttributeDisplay
from src.utils.format_utils import FormatUtils
from src.utils.logger import get_logger


def _create_placeholder_label():
    """创建占位符标签（工具函数）"""
    placeholder_label = QLabel("请选择角色查看属性")
    placeholder_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
    placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder_label.setStyleSheet("color: #95a5a6;")
    placeholder_label.setVisible(True)  # 初始显示

    return placeholder_label


def _create_stats_widget_with_placeholder(title: str):
    """创建带占位符的属性显示部件（工具函数）

    Args:
        title: 分组框标题

    Returns:
        tuple: (widget, group_box, placeholder_label, stats_display)
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(5, 5, 5, 5)

    # 创建分组框
    group_box = QGroupBox(title)
    group_box.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))

    group_layout = QFormLayout()
    group_layout.setVerticalSpacing(8)
    group_layout.setHorizontalSpacing(15)

    # 创建占位符标签
    placeholder_label = _create_placeholder_label()

    # 创建属性显示组件
    stats_display = AttributeDisplay()
    stats_display.set_attributes([])
    stats_display.setVisible(False)  # 初始隐藏

    group_layout.addRow(placeholder_label)
    group_layout.addRow(stats_display)
    group_box.setLayout(group_layout)
    layout.addWidget(group_box)

    return widget, group_box, placeholder_label, stats_display


class LeftPanel(QWidget):
    """左侧面板 - 适配新架构"""

    def __init__(self, app_core):
        super().__init__()
        self.logger = get_logger("ui.left_panel")
        self.app_core = app_core

        # 获取状态管理器实例
        from src.core.state_manager import StateManager
        self.state = StateManager.instance()

        self._init_ui()
        self._connect_signals()

        # 初始根据设置显示/隐藏基础属性区域
        self._update_ui_visibility()

    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        self.splitter = QSplitter(Qt.Orientation.Vertical)

        # 上区域：角色基础属性
        self.basic_stats_widget = self._create_basic_stats_widget()

        # 下区域：角色面板属性
        self.character_stats_widget = self._create_character_stats_widget()

        self.splitter.addWidget(self.basic_stats_widget)
        self.splitter.addWidget(self.character_stats_widget)
        self.splitter.setSizes([300, 300])

        main_layout.addWidget(self.splitter)

    def _create_basic_stats_widget(self):
        """创建角色基础属性部件"""
        widget, group_box, placeholder_label, stats_display = _create_stats_widget_with_placeholder("角色基础属性")

        # 保存引用
        self.basic_group_box = group_box
        self.basic_placeholder_label = placeholder_label
        self.basic_stats = stats_display

        return widget

    def _create_character_stats_widget(self):
        """创建角色属性部件"""
        widget, group_box, placeholder_label, stats_display = _create_stats_widget_with_placeholder("角色面板属性")

        # 保存引用
        self.character_group_box = group_box
        self.character_placeholder_label = placeholder_label
        self.character_stats = stats_display

        return widget

    def _connect_signals(self):
        """连接信号"""
        self.app_core.base_attributes_updated.connect(self._on_basic_attributes_updated)
        self.app_core.character_attributes_updated.connect(self._on_character_attributes_updated)

        # 状态管理器信号
        self.state.character_changed.connect(self._on_state_character_changed)
        self.state.character_cleared.connect(self.on_character_cleared)

    def _on_state_character_changed(self, character):
        """处理状态管理器的角色变化信号"""
        self.logger.debug(f"_on_state_character_changed: character={character.name if character else 'None'}")

        if character:
            # 有角色时隐藏占位符，显示属性区域
            self._set_widget_visibility(False, True)

            # ★★★ 关键：在这里初始化标签 ★★★
            self.logger.debug(f"初始化角色属性标签")

            # 获取显示设置
            settings = settings_manager.get_settings()
            display_mode = settings.display.character_attribute_display_mode

            # 生成占位数据
            basic_data, character_data = self.generate_placeholder_data(character)

            if display_mode == 1:
                # 面板属性：使用 character_data
                self.logger.debug(f"使用面板属性模式，初始化 {len(character_data)} 个标签")
                self.character_stats.set_attributes(character_data)
            else:
                # 局内属性：可能需要不同的属性集
                self.logger.debug(f"使用局内属性模式，初始化 {len(character_data)} 个标签")
                self.character_stats.set_attributes(character_data)

            self.logger.debug(f"标签初始化完成")

            # 更新标题
            self._update_groupbox_titles()
        else:
            # 无角色时重置为占位符
            self.on_character_cleared()

    def on_character_changed(self, character):
        """处理角色变化 - 更新推荐数据"""
        self.logger.debug(f"on_character_changed 被调用: character={character.name if character else 'None'}")

        current_state = self.state.get_state()

        if current_state.current_character:
            self.logger.debug(f"角色已选择: {current_state.current_character.name}")
            # 有角色时隐藏占位符标签，显示属性显示区域
            self._set_widget_visibility(False, True)

            # 更新分组框标题
            self._update_groupbox_titles()
        else:
            self.logger.debug(f"角色被清空或选择了占位符")
            # 没有角色时显示占位符标签，隐藏属性显示区域
            self._set_widget_visibility(True, False)

            self.basic_stats.set_attributes([])
            self.character_stats.set_attributes([])

            # 重置分组框标题
            self.basic_group_box.setTitle("角色基础属性")
            self.character_group_box.setTitle("角色面板属性")

    def on_character_cleared(self):
        """处理角色被清空"""
        self.logger.debug(f"on_character_cleared 被调用")

        # 显示占位符标签，隐藏属性显示区域
        self._set_widget_visibility(True, False)

        # 清空属性显示
        self.basic_stats.set_attributes([])
        self.character_stats.set_attributes([])

        # 重置分组框标题
        self.basic_group_box.setTitle("角色基础属性")
        self.character_group_box.setTitle("角色面板属性")

        self.logger.debug(f"已重置为占位符状态")

    def _set_widget_visibility(self, show_placeholder: bool, show_stats: bool):
        """设置部件可见性（工具函数）

        Args:
            show_placeholder: 是否显示占位符标签
            show_stats: 是否显示属性显示区域
        """
        self.logger.debug(f"设置部件可见性: show_placeholder={show_placeholder}, show_stats={show_stats}")
        self.basic_placeholder_label.setVisible(show_placeholder)
        self.basic_stats.setVisible(show_stats)
        self.character_placeholder_label.setVisible(show_placeholder)
        self.character_stats.setVisible(show_stats)

    def update_basic_stats(self, stats_dict):
        """更新角色基础属性显示"""
        if stats_dict:
            stats_data = self._convert_stats_to_display_format(stats_dict)
            if stats_data:
                self.basic_stats.update_attributes(stats_data)

    def update_character_stats(self, stats_dict):
        """更新角色属性显示"""
        if stats_dict:
            stats_data = self._convert_stats_to_display_format(stats_dict)
            if stats_data:
                self.character_stats.update_attributes(stats_data)

    def _on_basic_attributes_updated(self, attributes: dict):
        """处理基础属性更新信号"""
        self.logger.debug(f"basic_attributes_updated: {len(attributes)} 个属性")

        # 只有基础属性区域显示时才更新
        settings = settings_manager.get_settings()
        if not settings.display.show_basic_attributes_section:
            self.logger.debug(f"基础属性区域已隐藏，跳过更新")
            return

        if not attributes:
            # 清空显示
            self.logger.debug(f"清空基础属性显示")
            self.basic_stats.set_attributes([])
            return

        # 格式化属性数据
        basic_stats = FormatUtils().format_stats_with_recommendation(attributes, ColorConstants.BASIC_ATTRIBUTE_COLOR)

        # 更新显示
        self.update_basic_stats(basic_stats)

    def _on_character_attributes_updated(self, attributes: dict):
        """处理角色属性更新信号"""
        self.logger.debug(f"character_attributes_updated: {len(attributes)} 个属性")

        if not attributes:
            # 清空显示
            self.logger.debug(f"清空角色属性显示")
            self.character_stats.set_attributes([])
            return

        # 格式化属性数据
        character_stats = FormatUtils().format_stats_with_recommendation(
            attributes, ColorConstants.CHARACTER_ATTRIBUTE_COLOR
        )
        self.logger.debug(f"character_stats: {character_stats}")

        # 更新显示
        self.update_character_stats(character_stats)

    def _update_groupbox_titles(self):
        """根据设置更新分组框标题"""
        settings = settings_manager.get_settings()
        display_mode = settings.display.character_attribute_display_mode

        if display_mode == 1:
            # 显示角色面板属性
            self.character_group_box.setTitle("角色面板属性")
            self.logger.debug(f"更新标题: 角色面板属性")
        else:
            # 显示角色局内属性
            self.character_group_box.setTitle("角色局内属性")
            self.logger.debug(f"更新标题: 角色局内属性")

    def _update_ui_visibility(self):
        """根据设置更新UI可见性"""
        settings = settings_manager.get_settings()
        show_basic = settings.display.show_basic_attributes_section

        self.logger.debug(f"更新UI可见性: show_basic={show_basic}")

        if show_basic:
            # 显示基础属性区域
            self.basic_stats_widget.setVisible(True)

            # 获取当前状态
            current_state = self.state.get_state()
            has_character = current_state.current_character is not None

            if has_character:
                # 有角色时显示属性，隐藏占位符
                self._set_widget_visibility(False, True)
            else:
                # 无角色时显示占位符
                self._set_widget_visibility(True, False)

            # 调整分割器比例
            self.splitter.setSizes([300, 300])  # 基础属性区域较小
        else:
            # 隐藏基础属性区域
            self.basic_stats_widget.setVisible(False)

            # 更新可见性
            current_state = self.state.get_state()
            has_character = current_state.current_character is not None

            if has_character:
                # 有角色时只显示角色属性区域
                self.character_stats_widget.setVisible(True)
                self.character_placeholder_label.setVisible(False)
                self.character_stats.setVisible(True)
            else:
                # 无角色时显示占位符
                self.character_stats_widget.setVisible(True)
                self.character_placeholder_label.setVisible(True)
                self.character_stats.setVisible(False)

    @staticmethod
    def _convert_stats_to_display_format(stats_dict):
        """将统计字典转换为显示格式（支持属性名和属性值分别设置颜色）"""
        stats_data = []
        if stats_dict:
            # stats_dict 是 (name, value, name_color, value_color) 元组
            for name, value, name_color, value_color in stats_dict:
                if isinstance(value, float):
                    if name in ['穿透率', '物理伤害加成', '火属性伤害加成', '冰属性伤害加成', '电属性伤害加成',
                                '以太伤害加成']:
                        display_value = f"{value:.1f}%"
                    elif name == '能量自动回复':
                        display_value = f"{value}"
                    else:
                        display_value = value
                else:
                    display_value = str(value)

                # 返回 (name, value, name_color, value_color)
                stats_data.append((name, display_value, name_color, value_color))

        return stats_data

    def generate_placeholder_data(self, character=None):
        """动态生成占位数据（按需调用）"""

        # 获取显示设置
        settings = settings_manager.get_settings()
        basic_content_mode = settings.display.basic_attributes_display_mode

        self.logger.debug(f"基础属性内容模式: {basic_content_mode} (1=角色基础属性, 2=所有属性)")

        # 1. 基础属性（所有角色都有的）
        basic_attrs = [
            ("生命值", "0"),
            ("攻击力", "0"),
            ("防御力", "0"),
            ("冲击力", "0"),
            ("暴击率", "0.0%"),
            ("暴击伤害", "0.0%"),
            ("异常掌控", "0"),
            ("异常精通", "0"),
        ]

        if basic_content_mode == 2:
            # 模式2：显示所有属性
            basic_attrs.extend([
                ("穿透率", "0.0%"),
                ("穿透值", "0"),
                ("能量自动回复", "0.0"),
                ("物理伤害加成", "0.0%"),
                ("火属性伤害加成", "0.0%"),
                ("冰属性伤害加成", "0.0%"),
                ("电属性伤害加成", "0.0%"),
                ("以太伤害加成", "0.0%"),
                ("贯穿力", "0"),
                ("闪能自动积蓄", "0.0"),
                ("贯穿伤害加成", "0.0%"),
            ])
        elif character and basic_content_mode == 1:
            # 模式1：显示角色基础属性，根据角色类型添加特定属性
            if character.weapon_type == "命破":
                # 命破角色：加上贯穿力、闪能自动积蓄、对应的属性伤害加成
                basic_attrs.extend([("贯穿力", "0"), ("闪能自动积蓄", "0.0"), ])
            else:
                # 非命破角色：加上穿透率、能量自动回复、穿透值、对应的属性伤害加成
                basic_attrs.extend([("穿透率", "0.0%"), ("能量自动回复", "0.0"), ("穿透值", "0"), ])

            # 添加对应的属性伤害加成
            basic_attrs.append((f"{character.element_type}伤害加成", "0.0%"))
        else:
            # 没有角色或模式1但没有角色时，显示基础属性
            pass

        # 格式：(name, value, name_color, value_color)
        basic_data = [
            (name, value, ColorConstants.BASIC_COLOR, ColorConstants.BASIC_ATTRIBUTE_COLOR)
            for name, value in basic_attrs
        ]

        character_data = [
            (name, value, ColorConstants.BASIC_COLOR, ColorConstants.CHARACTER_ATTRIBUTE_COLOR)
            for name, value in basic_attrs
        ]

        self.logger.debug(f"生成占位数据: {len(basic_attrs)} 个属性")
        self.logger.debug(f"角色类型: {character.weapon_type if character else '无'}, 元素类型: {character.element_type if character else '无'}")

        return basic_data, character_data

    def reset_to_placeholder(self):
        """重置为占位数据"""
        self.logger.debug(f"reset_to_placeholder 被调用")

        # 显示占位符标签，隐藏属性显示区域
        self._set_widget_visibility(True, False)

        # 清空属性显示（使用空列表，因为占位符标签会显示）
        self.basic_stats.set_attributes([])
        self.character_stats.set_attributes([])

        # 重置分组框标题
        self.basic_group_box.setTitle("角色基础属性")
        self.character_group_box.setTitle("角色面板属性")