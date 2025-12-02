# src/ui/gear_slot.py
"""驱动盘槽位组件 - 适配新架构"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any

from src.config import config_manager
from src.core.gear_models import GearPiece, GearSubAttribute


class GearSlotWidget(ttk.LabelFrame):
    """单个驱动盘槽位组件 - 新架构"""

    def __init__(self, parent, slot_number: int, app):
        super().__init__(parent, text=f"驱动盘 {slot_number}")
        self.slot_number = slot_number - 1  # 转换为0-based索引
        self.app = app

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

        # 获取当前槽位的主属性gear_key
        gear_keys = slot_config.get_main_attributes_for_slot(self.slot_number + 1)

        # 转换为中文显示名称
        return [attribute_config.get_display_name(key) for key in gear_keys]

    def get_available_sub_attributes(self) -> List[str]:
        """获取可用的副属性列表（中文显示名称）"""
        attribute_config = config_manager.gear.attribute_config
        growth_config = config_manager.gear.growth_config

        # 获取所有副属性的gear_key
        gear_keys = list(growth_config.sub_attr_growth.keys())

        # 转换为中文显示名称
        return [attribute_config.get_display_name(key) for key in gear_keys]

    def get_filtered_sub_attributes(self) -> List[str]:
        """获取过滤后的副属性列表（排除当前主属性）"""
        current_main_display = self.main_attr_var.get()
        if not current_main_display:
            return self.get_available_sub_attributes()

        # 获取当前主属性的gear_key
        current_main_gear_key = config_manager.gear.attribute_config.get_gear_key_by_display(
            current_main_display
        )

        # 过滤掉与主属性相同的属性
        available_sub_attrs = []
        growth_config = config_manager.gear.growth_config
        attribute_config = config_manager.gear.attribute_config

        for gear_key in growth_config.sub_attr_growth.keys():
            if gear_key != current_main_gear_key:
                available_sub_attrs.append(attribute_config.get_display_name(gear_key))

        return available_sub_attrs

    def on_main_attr_changed(self, event=None):
        """主属性改变事件处理"""
        print(f"[DEBUG] 槽位 {self.slot_number + 1} 主属性改变事件触发")  # 调试

        # 1. 更新主属性值显示
        self.update_main_attribute_value()

        # 2. 更新副属性下拉框的可选列表
        self.update_sub_attributes_availability()

        # 3. 【关键修复】立即更新驱动盘数据，并通知应用
        self.update_gear_data()

        # 4. 通知应用更新最终计算
        self.notify_app_update()

    def on_sub_attr_changed(self, sub_index: int):
        """副属性改变事件处理"""
        if sub_index < 0 or sub_index >= len(self.sub_widgets):
            return

        widget = self.sub_widgets[sub_index]
        display_name = widget["combo_var"].get()

        if not display_name:
            widget["value_label"].config(text="0")
            self.update_gear_data()
            return

        # 将中文显示名称转换回gear_key
        gear_key = config_manager.gear.attribute_config.get_gear_key_by_display(display_name)
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

        if gear_key and new_enhancement_count >= 0:
            # 计算属性值 - 直接使用GrowthConfig
            value = self.calculate_sub_attribute_value(gear_key, new_enhancement_count)

            # 更新显示
            display_value = self.format_attribute_value(gear_key, value)
            widget["value_label"].config(text=display_value)

            # 更新数据
            self.update_gear_data()

    def calculate_main_attribute_value(self, gear_key: str, level: int) -> float:
        """计算主属性值 - 使用GrowthConfig"""
        growth_config = config_manager.gear.growth_config
        growth_data = growth_config.get_main_attribute_growth(gear_key)

        if not growth_data:
            return 0.0

        base_value = growth_data.get("base", 0)
        growth_rate = growth_data.get("growth", 0)

        return base_value + growth_rate * level

    def calculate_sub_attribute_value(self, gear_key: str, enhancement_count: int) -> float:
        """计算副属性值 - 使用GrowthConfig"""
        growth_config = config_manager.gear.growth_config
        growth_data = growth_config.get_sub_attribute_growth(gear_key)

        if not growth_data:
            return 0.0

        base_value = growth_data.get("base", 0)
        growth_rate = growth_data.get("growth", 0)

        return base_value + growth_rate * enhancement_count

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
        display_name = self.main_attr_var.get()
        print(f"[DEBUG] update_main_attribute_value: 显示名称='{display_name}'")  # 调试

        if not display_name:
            self.main_value_label.config(text="值: 0")
            print(f"[DEBUG] 显示名称为空，重置值显示")  # 调试
            self.update_gear_data()
            return

        # 将中文显示名称转换回gear_key
        gear_key = config_manager.gear.attribute_config.get_gear_key_by_display(display_name)
        global_level = self.app.main_enhance_level.get()

        print(f"[DEBUG] 转换结果: 显示名='{display_name}' -> gear_key='{gear_key}'")  # 调试
        print(f"[DEBUG] 全局强化等级: {global_level}")  # 调试

        if gear_key:
            # 计算属性值
            value = self.calculate_main_attribute_value(gear_key, global_level)

            # 更新显示
            display_value = self.format_attribute_value(gear_key, value)
            self.main_value_label.config(text=f"值: {display_value}")

            print(f"[DEBUG] 计算属性值: {value} -> 显示格式: {display_value}")  # 调试

            # 更新数据
            self.update_gear_data()
        else:
            print(f"[ERROR] 无法找到显示名 '{display_name}' 对应的gear_key")
            self.main_value_label.config(text="值: 0")
            self.update_gear_data()

    def update_sub_attributes_availability(self):
        """更新所有副属性下拉框的可选列表"""
        available_values = self.get_filtered_sub_attributes()
        current_main_display = self.main_attr_var.get()

        if current_main_display:
            current_main_gear_key = config_manager.gear.attribute_config.get_gear_key_by_display(
                current_main_display
            )
        else:
            current_main_gear_key = None

        for widget in self.sub_widgets:
            current_selection = widget["combo_var"].get()
            current_gear_key = None

            if current_selection:
                current_gear_key = config_manager.gear.attribute_config.get_gear_key_by_display(
                    current_selection
                )

            # 更新下拉框的值
            widget["combo"]["values"] = available_values

            # 如果当前选择的副属性与主属性冲突，清空选择
            if current_gear_key and current_gear_key == current_main_gear_key:
                widget["combo_var"].set("")
                widget["value_label"].config(text="0")
                self.update_gear_data()

    def update_gear_data(self):
        """更新驱动盘数据"""
        self.app.update_gear_data()

    def notify_app_update(self):
        """通知应用更新计算"""
        self.app.update_calculation()

    def format_attribute_value(self, gear_key: str, value: float) -> str:
        """格式化属性值显示"""
        gear_attr = config_manager.gear.attribute_config.get_gear_attribute(gear_key)
        if not gear_attr:
            return f"{value:.0f}"

        # 根据属性值类型格式化显示
        from src.config.gear_config import AttributeValueType
        if gear_attr.value_type in [
            AttributeValueType.PERCENTAGE,
            AttributeValueType.RATE_PERCENTAGE,
            AttributeValueType.DMG_BONUS_PERCENTAGE
        ]:
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
        self.update_gear_data()

    def get_gear_piece(self) -> GearPiece:
        """获取当前配置对应的GearPiece对象"""
        main_attr_display = self.main_attr_var.get()
        print(f"[DEBUG] get_gear_piece 调用:")  # 调试
        print(f"  槽位: {self.slot_number + 1}")  # 调试
        print(f"  主属性显示名: '{main_attr_display}'")  # 调试

        main_gear_key = config_manager.gear.attribute_config.get_gear_key_by_display(main_attr_display)
        print(f"  转换的gear_key: '{main_gear_key}'")  # 调试

        main_value = self._extract_value_from_label(self.main_value_label.cget("text"))
        print(f"  标签文本: '{self.main_value_label.cget('text')}'")  # 调试
        print(f"  提取的数值: {main_value}")  # 调试

        sub_attributes = []
        for i, widget in enumerate(self.sub_widgets):
            sub_display = widget["combo_var"].get()
            if sub_display:
                sub_gear_key = config_manager.gear.attribute_config.get_gear_key_by_display(sub_display)
                sub_value = self._extract_value_from_label(widget["value_label"].cget("text"))
                sub_attributes.append(GearSubAttribute(
                    gear_key=sub_gear_key,
                    value=sub_value,
                    is_locked=False
                ))
                print(f"  副属性{i}: 显示名='{sub_display}', gear_key='{sub_gear_key}', 值={sub_value}")  # 调试

        gear_piece = GearPiece(
            slot_index=self.slot_number,
            level=self.app.main_enhance_level.get(),
            main_gear_key=main_gear_key,
            main_value=main_value,
            sub_attributes=sub_attributes
        )

        print(
            f"  生成的GearPiece: main_gear_key='{gear_piece.main_gear_key}', main_value={gear_piece.main_value}")  # 调试
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
    """驱动盘槽位管理器 - 新架构"""

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

    def get_all_gear_pieces(self) -> List[GearPiece]:
        """获取所有槽位的GearPiece对象"""
        return [slot.get_gear_piece() for slot in self.slot_widgets]

    def reset_all_slots(self):
        """重置所有槽位"""
        for slot_widget in self.slot_widgets:
            slot_widget.reset()

    def validate_configurations(self) -> Dict[str, Any]:
        """验证所有槽位配置的有效性"""
        errors = []
        warnings = []

        for i, slot in enumerate(self.slot_widgets):
            gear_piece = slot.get_gear_piece()

            # 检查主属性冲突
            main_gear_key = gear_piece.main_gear_key
            if main_gear_key:
                for sub_attr in gear_piece.sub_attributes:
                    if sub_attr.gear_key == main_gear_key:
                        errors.append(f"槽位 {i + 1}: 主属性与副属性冲突")

            # 检查无效的属性组合
            if not self._is_valid_slot_configuration(i + 1, gear_piece):
                warnings.append(f"槽位 {i + 1}: 属性组合可能无效")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _is_valid_slot_configuration(self, slot_number: int, gear_piece: GearPiece) -> bool:
        """检查槽位配置是否有效"""
        slot_config = config_manager.gear.slot_config
        available_main_attrs = slot_config.get_main_attributes_for_slot(slot_number)

        main_gear_key = gear_piece.main_gear_key
        if main_gear_key and main_gear_key not in available_main_attrs:
            return False

        return True