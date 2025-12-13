"""驱动盘槽位组件"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any

from src.config.manager import config_manager
from src.ui.widget.attribute_comboBox import AttributeComboBox
from src.models.gear_attributes import Attribute
from src.models.gear_models import GearPiece


class GearSlotWidget(ttk.LabelFrame):
    """单个驱动盘槽位组件"""

    def __init__(self, parent, slot_number: int, main_window):
        super().__init__(parent, text=f"驱动盘 {slot_number}")
        self.slot_number = slot_number - 1  # 转换为0-based索引
        self.main_window = main_window  # 直接使用 main_window 引用

        # 存储子组件引用
        self.sub_widgets: List[Dict[str, Any]] = []
        self.total_enhancement_limit = 5

        self.setup_ui()

    def setup_ui(self):
        """设置UI组件"""
        # 主属性区域
        self.setup_main_attribute_section()

        # 副属性区域
        self.setup_sub_attributes_section()

        # 配置网格权重
        self.columnconfigure(0, weight=1)

    def setup_main_attribute_section(self):
        """设置主属性区域"""
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="we", pady=(5, 10))
        main_frame.columnconfigure(1, weight=1)

        # 主属性标签
        ttk.Label(main_frame, text="主属性:").grid(
            row=0, column=0, padx=(0, 5), sticky="w"
        )

        # 主属性选择框
        self.main_attr_combo = AttributeComboBox(
            main_frame,
            width=15
        )
        self.main_attr_combo.attributes = config_manager.slot_config.get_slot_main_attribute(self.slot_number)
        self.main_attr_combo.grid(row=0, column=1, padx=(0, 10), sticky="we")
        self.main_attr_combo.bind('<<ComboboxSelected>>', self.on_main_attr_changed)

        # 主属性值显示
        self.main_value_label = ttk.Label(
            main_frame,
            text="值: 0",
            width=10,
            foreground="blue"
        )
        self.main_value_label.grid(row=0, column=2, padx=(0, 5))

    def setup_sub_attributes_section(self):
        """设置副属性区域"""
        for i in range(4):  # 4个副属性槽位
            self.setup_single_sub_attribute(i)

    def setup_single_sub_attribute(self, sub_index: int):
        """设置单个副属性组件"""
        sub_frame = ttk.Frame(self)
        sub_frame.grid(row=sub_index + 1, column=0, sticky="we", pady=2)
        sub_frame.columnconfigure(0, weight=1)

        # 副属性选择框
        sub_attr_combo = AttributeComboBox(
            sub_frame,
            width=15
        )
        # 使用新的工厂方法获取副属性实例
        sub_attr_combo.attributes = config_manager.slot_config.get_slot_sub_attribute()
        sub_attr_combo.grid(row=0, column=0, padx=(0, 5), sticky="we")

        # 强化次数标签
        ttk.Label(sub_frame, text="强化:").grid(
            row=0, column=1, padx=(5, 5)
        )

        # 强化次数输入
        sub_level_var = tk.IntVar(value=0)
        sub_level_spin = ttk.Spinbox(
            sub_frame,
            from_=0,
            to=5,
            textvariable=sub_level_var,
            width=3,
            command=lambda: self.on_sub_attr_changed(sub_index)
        )
        sub_level_spin.grid(row=0, column=2, padx=(0, 5))
        sub_level_spin.bind('<KeyRelease>', lambda e: self.on_sub_attr_changed(sub_index))

        # 副属性值显示
        sub_value_label = ttk.Label(
            sub_frame,
            text="0",
            width=8,
            foreground="green"
        )
        sub_value_label.grid(row=0, column=3, padx=(5, 0))

        # 存储控件引用
        widget_data = {
            "combo": sub_attr_combo,
            "spin": sub_level_spin,
            "spin_var": sub_level_var,
            "value_label": sub_value_label
        }
        self.sub_widgets.append(widget_data)

        # 绑定事件
        sub_attr_combo.bind('<<ComboboxSelected>>',
                            lambda e, idx=sub_index: self.on_sub_attr_changed(idx))

    def on_main_attr_changed(self, event=None):
        """主属性改变事件处理"""
        # 1. 更新主属性值显示
        self.update_main_attribute_value()

        # 2. 更新副属性下拉框的可选列表
        self.update_sub_attributes_availability()

    def on_sub_attr_changed(self, sub_index: int):
        """副属性改变事件处理"""
        if sub_index < 0 or sub_index >= len(self.sub_widgets):
            return

        widget = self.sub_widgets[sub_index]
        attr = widget["combo"].get_selected_attribute()

        if not attr:
            widget["value_label"].config(text="0")
            # 更新其他副属性的可选列表
            self.update_sub_attributes_availability()
            return  # 移除自动计算

        new_enhancement_count = widget["spin_var"].get()

        # 检查总强化次数限制
        current_total = self.calculate_total_enhancement()
        old_value = self.get_current_enhancement_count(sub_index)

        if current_total - old_value + new_enhancement_count > self.total_enhancement_limit:
            max_allowed = self.total_enhancement_limit - (current_total - old_value)
            if max_allowed < 0:
                max_allowed = 0
            widget["spin_var"].set(max_allowed)
            new_enhancement_count = max_allowed

        if new_enhancement_count >= 0:
            # 计算属性值
            value = attr.calculate_value_at_level(new_enhancement_count)

            # 更新显示
            display_value = self.format_attribute_value(attr, value)
            widget["value_label"].config(text=display_value)

            # 更新其他副属性的可选列表（因为当前副属性已选择）
            self.update_sub_attributes_availability()

    def calculate_total_enhancement(self) -> int:
        """计算当前总强化次数"""
        total = 0
        for widget in self.sub_widgets:
            total += widget["spin_var"].get()
        return total

    def get_current_enhancement_count(self, index: int) -> int:
        """获取指定副属性当前的强化次数"""
        if 0 <= index < len(self.sub_widgets):
            return self.sub_widgets[index]["spin_var"].get()
        return 0

    def update_main_attribute_value(self):
        """更新主属性值显示和计算"""
        attr = self.main_attr_combo.get_selected_attribute()

        if not attr:
            self.main_value_label.config(text="值: 0")
            return

        global_level = self.main_window.main_enhance_level.get()

        if attr:
            # 计算属性值
            value = attr.calculate_value_at_level(global_level)

            # 更新显示
            display_value = self.format_attribute_value(attr, value)
            self.main_value_label.config(text=f"值: {display_value}")

    def update_sub_attributes_availability(self):
        """更新所有副属性下拉框的可选列表"""
        current_main_attr = self.main_attr_combo.get_selected_attribute()

        # 获取所有已选择的副属性名称（包括当前正在处理的下拉框）
        selected_attr_names = []
        for widget in self.sub_widgets:
            attr = widget["combo"].get_selected_attribute()
            if attr:
                selected_attr_names.append(attr.name)

        # 获取所有可用的副属性
        all_sub_attributes = config_manager.slot_config.get_slot_sub_attribute()

        # 更新每个副属性下拉框
        for i, widget in enumerate(self.sub_widgets):
            current_attr = widget["combo"].get_selected_attribute()

            # 构建当前下拉框可用的属性列表
            available_attrs = []
            for attr in all_sub_attributes:
                # 1. 排除主属性（如果已选择主属性）
                if current_main_attr and attr.name == current_main_attr.name:
                    continue

                # 2. 排除其他副属性已选择的属性
                # 我们需要排除其他下拉框选择的属性，但不排除自己当前选择的
                is_selected_by_others = False
                for j, selected_name in enumerate(selected_attr_names):
                    # 如果是当前下拉框自己的选择，不排除
                    if i == j:
                        continue
                    if attr.name == selected_name:
                        is_selected_by_others = True
                        break

                if not is_selected_by_others:
                    available_attrs.append(attr)

            # 更新下拉框选项
            widget["combo"].attributes = available_attrs

            # 检查当前选择是否还在可用列表中
            if current_attr:
                current_in_available = any(
                    attr.name == current_attr.name for attr in available_attrs
                )
                if not current_in_available:
                    # 当前选择已不可用，清空选择
                    widget["combo"].set_selected_attribute(None)
                    widget["spin_var"].set(0)
                    widget["value_label"].config(text="0")

    def format_attribute_value(self, attr: Attribute, value: float) -> str:
        """格式化属性值显示"""
        if hasattr(attr, 'is_percentage_type') and callable(attr.is_percentage_type):
            is_percentage = attr.is_percentage_type()
        else:
            # 回退到基于名称的判断
            is_percentage = any(keyword in attr.name.lower() for keyword in
                              ['百分比', 'rate', 'ratio', 'bonus', '伤害加成'])

        if is_percentage:
            return f"{value:.1%}"
        else:
            # 如果是小数但非百分比，保留1位小数
            if value != int(value):
                return f"{value:.1f}"
            else:
                return f"{value:.0f}"

    def reset(self):
        """重置当前驱动盘配置"""
        # 重置主属性
        self.main_attr_combo.set_selected_attribute(None)
        self.main_value_label.config(text="值: 0")

        # 重置所有副属性
        for widget in self.sub_widgets:
            widget["combo"].set_selected_attribute(None)
            widget["spin_var"].set(0)
            widget["value_label"].config(text="0")

        # 恢复所有副属性的完整列表
        from src.config.manager import config_manager
        all_sub_attributes = config_manager.slot_config.get_slot_sub_attribute()
        for widget in self.sub_widgets:
            widget["combo"].attributes = all_sub_attributes

        # 触发重新计算
        self.main_window.recalculate_final_stats()

    def get_gear_piece(self) -> GearPiece:
        """获取当前配置对应的GearPiece对象 - 修复版本"""
        main_attr = self.main_attr_combo.get_selected_attribute()

        # 收集所有副属性（包含属性和强化等级）
        sub_attributes = []
        for i, widget in enumerate(self.sub_widgets):
            sub_attr = widget["combo"].get_selected_attribute()
            if sub_attr:
                # 这里sub_attr已经是独立的实例，可以直接修改
                sub_attr.enhancement_level = widget["spin_var"].get()
                sub_attributes.append(sub_attr)

        # 创建GearPiece对象
        gear_piece = GearPiece(
            slot_index=self.slot_number,
            level=self.main_window.main_enhance_level.get(),
            main_attribute=main_attr,
            sub_attributes=sub_attributes
        )

        # 添加调试信息
        print(f"[GearSlot] 获取驱动盘数据 - 槽位 {self.slot_number}:")
        print(f"  主属性: {main_attr.name if main_attr else '无'}")
        print(f"  强化等级: {self.main_window.main_enhance_level.get()}")
        for i, sub_attr in enumerate(sub_attributes):
            print(f"  副属性{i+1}: {sub_attr.name}, 强化等级: {sub_attr.enhancement_level}, 计算值: {sub_attr.calculate_value_at_enhancement_level()}")

        return gear_piece

    def _extract_value_from_label(self, label_text: str) -> float:
        """从标签文本中提取数值"""
        try:
            # 处理 "值: 123" 或 "12.3%" 格式
            if ":" in label_text:
                value_str = label_text.split(":")[1].strip()
            else:
                value_str = label_text

            if "%" in value_str:
                return float(value_str.replace("%", "")) / 100
            else:
                return float(value_str)
        except (ValueError, IndexError):
            return 0.0


class GearSlotManager:
    """驱动盘槽位管理器 - 适配新架构"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.slot_widgets: List[GearSlotWidget] = []

    def create_slots(self, parent, slot_count: int = 6):
        """创建指定数量的槽位"""
        self.slot_widgets.clear()

        for i in range(slot_count):
            slot_widget = GearSlotWidget(parent, i + 1, self.main_window)
            self.slot_widgets.append(slot_widget)

        return self.slot_widgets

    def get_all_gear_pieces(self) -> List[GearPiece]:
        """获取所有槽位的GearPiece对象"""
        return [slot.get_gear_piece() for slot in self.slot_widgets]

    def reset_all_slots(self):
        """重置所有槽位"""
        for slot_widget in self.slot_widgets:
            slot_widget.reset()

        self.main_window.recalculate_final_stats()