"""更新左侧面板 - 适配新架构"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QGroupBox,
    QFormLayout
)

from src.config.constants import ColorConstants
from src.utils.format_utils import FormatUtils
from src.ui.widgets.attribute_display import AttributeDisplay


class LeftPanel(QWidget):
    """左侧面板 - 适配新架构"""

    def __init__(self, app_core):
        super().__init__()
        self.app_core = app_core
        self.current_character = None  # 存储当前角色
        self.recommend_data = None     # 存储角色推荐数据

        self._init_placeholder_data()
        self._init_ui()
        self._connect_signals()

    def _init_placeholder_data(self):
        """初始化占位数据"""
        basic_placeholder_data = [
            ("生命值", "0"),
            ("攻击力", "0"),
            ("防御力", "0"),
            ("冲击力", "0"),
            ("暴击率", "0.0%"),
            ("暴击伤害", "0.0%"),
            ("异常掌控", "0"),
            ("异常精通", "0"),
            ("穿透率", "0.0%"),
            ("穿透值", "0"),
            ("能量自动回复", "0.0"),
            ("闪能自动积蓄", "0.0"),
            ("贯穿力", "0"),
            ("物理伤害加成", "0.0%"),
            ("火属性伤害加成", "0.0%"),
            ("冰属性伤害加成", "0.0%"),
            ("电属性伤害加成", "0.0%"),
            ("以太伤害加成", "0.0%"),
            ("贯穿伤害加成", "0.0%"),
        ]
        # 格式：(name, value, name_color, value_color)
        self.basic_placeholder_data = [(name, value, ColorConstants.BASIC_COLOR, ColorConstants.BASIC_ATTRIBUTE_COLOR)
                                       for name, value in basic_placeholder_data]
        self.character_placeholder_data = [(name, value, ColorConstants.BASIC_COLOR, ColorConstants.CHARACTER_ATTRIBUTE_COLOR)
                                           for name, value in basic_placeholder_data]

    def _init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # 上区域：角色基础属性
        self.basic_stats_widget = self._create_basic_stats_widget()

        # 下区域：角色面板属性
        self.character_stats_widget = self._create_character_stats_widget()

        splitter.addWidget(self.basic_stats_widget)
        splitter.addWidget(self.character_stats_widget)
        splitter.setSizes([300, 300])

        main_layout.addWidget(splitter)

    def _create_basic_stats_widget(self):
        """创建角色基础属性部件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        group_box = QGroupBox("角色基础属性")
        group_box.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))

        group_layout = QFormLayout()
        group_layout.setVerticalSpacing(8)
        group_layout.setHorizontalSpacing(15)

        self.basic_stats = AttributeDisplay()
        self.basic_stats.set_attributes(self.basic_placeholder_data)

        group_layout.addRow(self.basic_stats)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        return widget

    def _create_character_stats_widget(self):
        """创建角色属性部件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        group_box = QGroupBox("角色面板属性")
        group_box.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))

        group_layout = QFormLayout()
        group_layout.setVerticalSpacing(8)
        group_layout.setHorizontalSpacing(15)

        self.character_stats = AttributeDisplay()
        self.character_stats.set_attributes(self.character_placeholder_data)

        group_layout.addRow(self.character_stats)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        return widget

    def _connect_signals(self):
        """连接信号"""
        self.app_core.base_attributes_updated.connect(self._on_basic_attributes_updated)
        self.app_core.character_attributes_updated.connect(self._on_character_attributes_updated)
        self.app_core.character_changed.connect(self.on_character_changed)

    def on_character_changed(self, character):
        """处理角色变化 - 更新推荐数据"""
        self.current_character = character
        if hasattr(character, 'recommend'):
            self.recommend_data = character.recommend
        else:
            self.recommend_data = None

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
        print("LeftPanel -> basic_attributes", attributes)
        if not attributes:
            return

        # 格式化属性数据
        basic_stats = self._format_stats_with_recommendation(attributes, ColorConstants.BASIC_ATTRIBUTE_COLOR)

        # 更新显示
        self.update_basic_stats(basic_stats)

    def _on_character_attributes_updated(self, attributes: dict):
        """处理角色属性更新信号"""
        print("character_attributes", attributes)
        if not attributes:
            return

        # 格式化属性数据
        character_stats = self._format_stats_with_recommendation(attributes, ColorConstants.CHARACTER_ATTRIBUTE_COLOR)

        # 更新显示
        self.update_character_stats(character_stats)

    def _format_stats_with_recommendation(self, attributes: dict, base_color: str):
        """格式化属性数据，标记推荐属性（只标记属性名）"""
        formatted = []

        for name, value in attributes.items():
            formatted_value = FormatUtils.format_attribute_display(name, value)

            # 检查是否为推荐属性
            is_recommended = False
            if self.recommend_data:
                is_recommended = FormatUtils.is_recommended_attribute(name, self.recommend_data)

            # 如果为推荐属性，属性名使用橙色，否则使用基础颜色
            if is_recommended:
                # 属性名用橙色，属性值用基础颜色
                formatted.append((name, formatted_value, ColorConstants.RECOMMENDED_COLOR, base_color))
            else:
                # 属性名和属性值都用基础颜色
                formatted.append((name, formatted_value, ColorConstants.BASIC_COLOR, base_color))

        return formatted

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