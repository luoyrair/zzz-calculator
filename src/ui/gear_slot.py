# src/ui/gear_slot.py
"""重构后的驱动盘槽位组件"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any

from src.config import config_manager


class GearSlotWidget(ttk.LabelFrame):
    """单个驱动盘槽位组件 - 单一职责：管理单个驱动盘配置"""

    def __init__(self, parent, slot_number: int, app):
        super().__init__(parent, text=f"驱动盘 {slot_number}")
        self.slot_number = slot_number - 1  # 转换为0-based索引
        self.app = app

        # 存储子组件引用
        self.sub_widgets: List[Dict[str, Any]] = []

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
        self.main_attr_var = tk.StringVar()
        main_attr_values = self.get_available_main_attributes()
        self.main_attr_combo = ttk.Combobox(
            main_frame,
            textvariable=self.main_attr_var,
            values=main_attr_values,
            state="readonly",
            width=15
        )
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
        sub_attr_var = tk.StringVar()
        sub_display_values = self.get_available_sub_attributes()
        sub_attr_combo = ttk.Combobox(
            sub_frame,
            textvariable=sub_attr_var,
            values=sub_display_values,
            state="readonly",
            width=15
        )
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
            "combo_var": sub_attr_var,
            "spin": sub_level_spin,
            "spin_var": sub_level_var,
            "value_label": sub_value_label
        }
        self.sub_widgets.append(widget_data)

        # 绑定事件
        sub_attr_combo.bind('<<ComboboxSelected>>',
                            lambda e, idx=sub_index: self.on_sub_attr_changed(idx))

    def get_available_main_attributes(self) -> List[str]:
        """获取可用的主属性列表（中文显示名称）"""
        slot_config = config_manager.gear.slot_config
        attribute_config = config_manager.gear.attribute_config

        # 获取当前槽位的主属性英文键
        english_keys = slot_config.get_main_attributes_for_slot(self.slot_number + 1)

        # 转换为中文显示名称
        return [attribute_config.get_display_name(key) for key in english_keys]

    def get_available_sub_attributes(self) -> List[str]:
        """获取可用的副属性列表（中文显示名称）"""
        attribute_config = config_manager.gear.attribute_config
        growth_config = config_manager.gear.growth_config

        # 获取所有副属性的英文键
        english_keys = list(growth_config.SUB_ATTR_GROWTH.keys())

        # 转换为中文显示名称
        return [attribute_config.get_display_name(key) for key in english_keys]

    def get_filtered_sub_attributes(self) -> List[str]:
        """获取过滤后的副属性列表（排除当前主属性）"""
        current_main_display = self.main_attr_var.get()
        if not current_main_display:
            return self.get_available_sub_attributes()

        # 获取当前主属性的英文键
        current_main_english = config_manager.gear.attribute_config.get_english_key_from_display(
            current_main_display
        )

        # 过滤掉与主属性相同的属性
        available_sub_attrs = []
        growth_config = config_manager.gear.growth_config
        attribute_config = config_manager.gear.attribute_config

        for eng_key in growth_config.SUB_ATTR_GROWTH.keys():
            if eng_key != current_main_english:
                available_sub_attrs.append(attribute_config.get_display_name(eng_key))

        return available_sub_attrs

    def on_main_attr_changed(self, event=None):
        """主属性改变事件处理"""
        # 更新主属性值显示
        self.update_main_attribute_value()

        # 更新副属性下拉框的可选列表
        self.update_sub_attributes_availability()

        # 通知应用更新数据
        self.notify_app_update()

    def on_sub_attr_changed(self, sub_index: int):
        """副属性改变事件处理"""
        if sub_index < 0 or sub_index >= len(self.sub_widgets):
            return

        widget = self.sub_widgets[sub_index]
        display_name = widget["combo_var"].get()

        if not display_name:
            # 清空选择
            widget["value_label"].config(text="0")
            self.update_gear_data("sub", sub_index, "", 0)
            return

        # 将中文显示名称转换回英文键
        attr_name = config_manager.gear.attribute_config.get_english_key_from_display(display_name)
        enhancement_count = widget["spin_var"].get()

        if attr_name and enhancement_count >= 0:
            # 计算属性值
            value = self.app.gear_calculator.calculate_sub_attribute(
                attr_name, enhancement_count
            )

            # 更新显示
            display_value = self.format_attribute_value(attr_name, value)
            widget["value_label"].config(text=display_value)

            # 更新数据
            self.update_gear_data("sub", sub_index, attr_name, value)

    def update_main_attribute_value(self):
        """更新主属性值显示和计算"""
        display_name = self.main_attr_var.get()

        if not display_name:
            self.main_value_label.config(text="值: 0")
            self.update_gear_data("main", 0, "", 0)
            return

        # 将中文显示名称转换回英文键
        attr_name = config_manager.gear.attribute_config.get_english_key_from_display(display_name)
        global_level = self.app.main_enhance_level.get()

        if attr_name:
            # 计算属性值
            value = self.app.gear_calculator.calculate_main_attribute(attr_name, global_level)

            # 更新显示
            display_value = self.format_attribute_value(attr_name, value)
            self.main_value_label.config(text=f"值: {display_value}")

            # 更新数据
            self.update_gear_data("main", 0, attr_name, value)

    def update_sub_attributes_availability(self):
        """更新所有副属性下拉框的可选列表"""
        available_values = self.get_filtered_sub_attributes()
        current_main_display = self.main_attr_var.get()

        if current_main_display:
            current_main_english = config_manager.gear.attribute_config.get_english_key_from_display(
                current_main_display
            )
        else:
            current_main_english = None

        for widget in self.sub_widgets:
            current_selection = widget["combo_var"].get()
            current_english = None

            if current_selection:
                current_english = config_manager.gear.attribute_config.get_english_key_from_display(
                    current_selection
                )

            # 更新下拉框的值
            widget["combo"]["values"] = available_values

            # 如果当前选择的副属性与主属性冲突，清空选择
            if current_english and current_english == current_main_english:
                widget["combo_var"].set("")
                widget["value_label"].config(text="0")

                # 更新数据
                sub_index = self.sub_widgets.index(widget)
                self.update_gear_data("sub", sub_index, "", 0)

    def update_gear_data(self, attr_type: str, sub_index: int, attr_name: str, value: float):
        """更新驱动盘数据"""
        # 确保空字符串被正确处理
        effective_attr_name = attr_name if attr_name else ""
        effective_value = value if attr_name else 0.0

        self.app.update_gear_data(
            self.slot_number, attr_type, sub_index, effective_attr_name, effective_value
        )

    def notify_app_update(self):
        """通知应用更新计算"""
        self.app.update_calculation()

    def format_attribute_value(self, attr_name: str, value: float) -> str:
        """格式化属性值显示"""
        if (attr_name.endswith('_PERCENT') or
                'RATE' in attr_name or
                'DMG' in attr_name or
                attr_name in ['CRIT_RATE', 'CRIT_DMG', 'PENETRATION', 'ENERGY_REGEN', 'ANOMALY_PROFICIENCY', 'IMPACT']):
            return f"{value:.1%}"
        else:
            return f"{value:.0f}"

    def reset(self):
        """重置当前驱动盘配置"""
        # 重置主属性
        self.main_attr_var.set("")
        self.main_value_label.config(text="值: 0")

        # 重置所有副属性
        for widget in self.sub_widgets:
            widget["combo_var"].set("")
            widget["spin_var"].set(0)
            widget["value_label"].config(text="0")

        # 更新数据
        self.update_gear_data("main", 0, "", 0)
        for i in range(4):
            self.update_gear_data("sub", i, "", 0)

        # 通知应用
        self.notify_app_update()

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        config = {
            "slot_number": self.slot_number + 1,
            "main_attribute": {
                "display_name": self.main_attr_var.get(),
                "english_name": config_manager.gear.attribute_config.get_english_key_from_display(
                    self.main_attr_var.get()
                ) if self.main_attr_var.get() else "",
                "value": self._extract_value_from_label(self.main_value_label.cget("text"))
            },
            "sub_attributes": []
        }

        for i, widget in enumerate(self.sub_widgets):
            sub_config = {
                "index": i,
                "display_name": widget["combo_var"].get(),
                "english_name": config_manager.gear.attribute_config.get_english_key_from_display(
                    widget["combo_var"].get()
                ) if widget["combo_var"].get() else "",
                "enhancement_level": widget["spin_var"].get(),
                "value": self._extract_value_from_label(widget["value_label"].cget("text"))
            }
            config["sub_attributes"].append(sub_config)

        return config

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

    def set_main_attribute(self, attr_display_name: str):
        """设置主属性（用于程序化设置）"""
        available_attrs = self.get_available_main_attributes()

        if attr_display_name in available_attrs:
            self.main_attr_var.set(attr_display_name)
            self.update_main_attribute_value()
        else:
            print(f"警告: 主属性 '{attr_display_name}' 在当前槽位不可用")

    def set_sub_attribute(self, sub_index: int, attr_display_name: str, enhancement_level: int = 0):
        """设置副属性（用于程序化设置）"""
        if sub_index < 0 or sub_index >= len(self.sub_widgets):
            return

        available_attrs = self.get_filtered_sub_attributes()

        if attr_display_name in available_attrs:
            widget = self.sub_widgets[sub_index]
            widget["combo_var"].set(attr_display_name)
            widget["spin_var"].set(enhancement_level)
            self.on_sub_attr_changed(sub_index)
        else:
            print(f"警告: 副属性 '{attr_display_name}' 在当前配置下不可用")


class GearSlotManager:
    """驱动盘槽位管理器 - 管理所有槽位的协调"""

    def __init__(self, app):
        self.app = app
        self.slot_widgets: List[GearSlotWidget] = []

    def create_slots(self, parent, slot_count: int = 6):
        """创建指定数量的槽位"""
        self.slot_widgets.clear()

        for i in range(slot_count):
            slot_widget = GearSlotWidget(parent, i + 1, self.app)
            self.slot_widgets.append(slot_widget)

        return self.slot_widgets

    def reset_all_slots(self):
        """重置所有槽位"""
        for slot_widget in self.slot_widgets:
            slot_widget.reset()

    def get_all_configs(self) -> List[Dict[str, Any]]:
        """获取所有槽位的配置"""
        return [slot.get_current_config() for slot in self.slot_widgets]

    def validate_configurations(self) -> Dict[str, Any]:
        """验证所有槽位配置的有效性"""
        errors = []
        warnings = []

        for i, slot in enumerate(self.slot_widgets):
            config = slot.get_current_config()

            # 检查主属性冲突
            main_attr = config["main_attribute"]["english_name"]
            if main_attr:
                for sub_attr in config["sub_attributes"]:
                    if sub_attr["english_name"] == main_attr:
                        errors.append(f"槽位 {i + 1}: 主属性与副属性冲突")

            # 检查无效的属性组合
            if not self._is_valid_slot_configuration(i + 1, config):
                warnings.append(f"槽位 {i + 1}: 属性组合可能无效")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _is_valid_slot_configuration(self, slot_number: int, config: Dict[str, Any]) -> bool:
        """检查槽位配置是否有效"""
        slot_config = config_manager.gear.slot_config
        available_main_attrs = slot_config.get_main_attributes_for_slot(slot_number)

        main_attr_english = config["main_attribute"]["english_name"]
        if main_attr_english and main_attr_english not in available_main_attrs:
            return False

        return True