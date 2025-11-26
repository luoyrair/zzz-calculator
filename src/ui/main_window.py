# src/ui/main_window.py (简化版)
"""重构后的主窗口"""
import tkinter as tk
from tkinter import ttk

from src.core.models import GearDataManager
from src.core.service_factory import get_service_factory
from src.ui.character_panel import CharacterPanel
from src.ui.gear_slot import GearSlotWidget


class MainWindow:
    """主窗口 - 专注于窗口管理和组件协调"""

    def __init__(self, root):
        self.root = root
        self.root.title("绝区零驱动盘属性计算器")
        self.root.geometry("1400x900")

        # 通过服务工厂初始化核心组件
        service_factory = get_service_factory()

        self.data_model = GearDataManager()
        self.character_loader = service_factory.character_loader
        self.character_manager = service_factory.character_manager
        self.gear_calculator = service_factory.gear_calculator
        self.character_calculator = service_factory.character_calculator

        # UI变量
        self.selected_character = tk.StringVar()
        self.main_enhance_level = tk.IntVar(value=self.data_model.main_enhance_level)

        self.setup_ui()
        self.update_calculation()

    def setup_ui(self):
        """设置用户界面"""
        # 主布局
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)

        # 左侧面板
        self.character_panel = CharacterPanel(main_frame, self)
        self.character_panel.pack(side='left', fill='y', padx=(0, 10))

        # 右侧选项卡
        self.setup_right_panel(main_frame)

    def setup_right_panel(self, parent):
        """设置右侧面板"""
        notebook = ttk.Notebook(parent)
        notebook.pack(side='right', fill='both', expand=True)

        # 角色配置选项卡
        character_tab = CharacterConfigTab(notebook, self)
        notebook.add(character_tab, text="角色配置")

        # 驱动盘配置选项卡
        gear_tab = GearConfigTab(notebook, self)
        notebook.add(gear_tab, text="驱动盘配置")

    def update_calculation(self):
        """更新计算"""
        try:
            gear_data = self.data_model.get_gear_data_for_calculation()
            stats = self.data_model.character_stats

            result = self.gear_calculator.calculate_all_stats(
                gear_data,
                stats.base_hp,
                stats.base_atk,
                stats.base_def,
                stats.impact,
                stats.base_crit_rate,
                stats.base_crit_dmg,
                stats.anomaly_mastery,
                stats.anomaly_proficiency,
                stats.penetration,
                stats.energy_regen
            )

            self.character_panel.update_display(result)

        except Exception as e:
            self.character_panel.show_error(f"计算错误: {str(e)}")

    def update_gear_data(self, slot_number: int, attr_type: str, sub_index: int, attr_name: str, value: float):
        """更新驱动盘数据"""
        try:
            # 使用数据管理器更新数据
            self.data_model.update_gear_attribute(slot_number, attr_type, sub_index, attr_name, value)

            # 触发计算更新
            self.update_calculation()

        except Exception as e:
            print(f"更新驱动盘数据错误: {e}")


class CharacterConfigTab(ttk.Frame):
    """角色配置选项卡 - 单一职责"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 角色选择
        selection_frame = ttk.LabelFrame(self, text="角色选择", padding="10")
        selection_frame.pack(fill='x', pady=5)

        ttk.Label(selection_frame, text="选择角色:").pack(side='left')

        characters = self.main_window.character_manager.get_available_characters()
        character_names = ["请选择角色"] + [char["name"] for char in characters]

        self.character_var = tk.StringVar()
        character_combo = ttk.Combobox(selection_frame, textvariable=self.character_var,
                                       values=character_names, state="readonly")
        character_combo.pack(side='left', padx=10)
        character_combo.bind('<<ComboboxSelected>>', self.on_character_selected)

        # 角色配置
        self.setup_character_config()

    def setup_character_config(self):
        """设置角色配置区域"""
        # 实现配置UI...
        pass

    def on_character_selected(self, event):
        """角色选择事件"""
        character_name = self.character_var.get()
        if character_name and character_name != "请选择角色":
            self.main_window.character_panel.load_character(character_name)


class GearConfigTab(ttk.Frame):
    """驱动盘配置选项卡 - 单一职责"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        gears_frame = ttk.LabelFrame(self, text="驱动盘配置 (6个槽位)", padding="5")
        gears_frame.pack(fill='both', expand=True)

        # 创建6个驱动盘槽位
        self.gear_widgets = []
        for i in range(6):
            gear_widget = GearSlotWidget(gears_frame, i + 1, self.main_window)
            row = i // 3
            col = i % 3
            gear_widget.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            self.gear_widgets.append(gear_widget)