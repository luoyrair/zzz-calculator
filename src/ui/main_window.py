# src/ui/main_window.py
"""重构后的主窗口 - 优化布局和交互"""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional

from src.models.gear_models import GearPiece, GearSetSelection
from src.manager.character_manager import CharacterManager
from .character_panel import CharacterPanel
from .gear_slot import GearSlotWidget, GearSlotManager
from .widget.gear_set_combo import GearSetComboBox
from ..calculators.gear_calculator import GearSetManager, GearCalculator
from ..manager.weapon_manager import WeaponManager
from ..models.character_attributes import CharacterAttributesModel


class MainWindow:
    """主窗口 - 优化版本"""

    def __init__(self, root):
        self.root = root
        self.root.title("绝区零驱动盘属性计算器")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill='both', expand=True)

        # 配置网格权重
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # 左侧角色面板
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(0, weight=1)

        self.character_panel = CharacterPanel(self.left_frame, self)
        self.character_panel.pack(fill='both', expand=True)

        # 右侧配置面板
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(1, weight=1)

        # 创建选项卡
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.right_frame.rowconfigure(0, weight=1)

        # 状态栏
        self.status_frame = ttk.Frame(self.right_frame)
        self.status_frame.grid(row=1, column=0, sticky="we", pady=(5, 0))
        self.status_label = ttk.Label(
            self.status_frame,
            text="就绪",
            relief="sunken",
            anchor="w"
        )
        self.status_label.pack(fill='x', padx=5, pady=2)

        # 初始化管理器
        self.character_manager = CharacterManager()
        self.weapon_manager = WeaponManager()
        self.gear_calculator = GearCalculator()  # 直接创建计算器

        # 当前状态
        self.current_base_stats: Optional[CharacterAttributesModel] = None  # 修正类型
        self.gear_pieces: List[GearPiece] = []
        self.gear_set_selection = GearSetSelection("4+2", [])
        self.gear_widgets = []

        # UI变量
        self.character_level = tk.IntVar(value=60)
        self.extra_level = tk.IntVar(value=7)
        self.main_enhance_level = tk.IntVar(value=15)
        self.weapon_level = tk.IntVar(value=60)

        # 槽位管理器
        self.gear_slot_manager = GearSlotManager(self)

        # 套装管理器
        self.gear_set_manager: Optional[GearSetManager] = None

        # 创建选项卡
        self.character_tab = CharacterConfigTab(self.notebook, self)
        self.notebook.add(self.character_tab, text="基础配置")

        # 加载装备数据
        self.load_equipment_data()

        gear_tab = GearConfigTab(self.notebook, self)
        self.notebook.add(gear_tab, text="驱动盘配置")

        self.initialize_application()

    def initialize_application(self):
        """初始化应用程序"""
        try:
            from src.config.manager import config_manager
            self.show_status("配置加载成功", "green")

            # 预加载第一个角色
            self.load_first_character()
            self.load_first_weapon()

        except Exception as e:
            self.show_status(f"初始化失败: {str(e)}", "red")
            import traceback
            traceback.print_exc()

    def load_first_character(self):
        """加载第一个可用角色"""
        try:
            characters = self.character_manager.get_available_characters()
            if characters:
                first_character = characters[0]
                self.character_tab.character_var.set(first_character["name"])
                self.character_tab.current_character_id = first_character["id"]
                self.character_panel.load_character_by_name(first_character["name"])
                self.show_status(f"已加载角色: {first_character['name']}", "green")
            else:
                self.show_status("未找到可用角色", "orange")
        except Exception as e:
            self.show_status(f"加载角色失败: {str(e)}", "red")

    def load_first_weapon(self):
        """加载第一个可用音擎"""
        try:
            character_id = self.character_tab.current_character_id
            if character_id and self.current_base_stats:
                weapon_id = int(f"1{self.current_base_stats.rarity}{character_id//10}")
                weapon_name = self.weapon_manager.get_weapon_name_by_id(weapon_id)
                self.character_tab.weapon_var.set(weapon_name)
                self.character_tab.current_weapon_id = weapon_id
                self.character_tab.apply_weapon_to_character()
                self.weapon_manager.apply_weapon_to_character(self.current_base_stats, weapon_id, 60)
                self.show_status(f"已加载音擎: {weapon_name}", "green")
            else:
                self.show_status("未找到可用音擎", "orange")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_status(f"加载音擎失败: {str(e)}", "red")

    def load_equipment_data(self):
        """加载装备数据"""
        try:
            from src.config.manager import config_manager
            import json

            equipment_file = config_manager.file.equipment_file

            if equipment_file.exists():
                with open(equipment_file, 'r', encoding='utf-8') as f:
                    equipment_data = json.load(f)

                # 创建套装管理器
                self.gear_set_manager = GearSetManager(equipment_data)

                # 设置到计算器中
                if self.gear_calculator:
                    self.gear_calculator.set_gear_set_manager(self.gear_set_manager)

                print(f"[INFO] 加载了 {len(equipment_data)} 个套装效果")
                self.show_status("装备数据加载成功", "green")
            else:
                print(f"[WARNING] 装备文件不存在: {equipment_file}")
                self.show_status("装备文件不存在", "orange")

        except Exception as e:
            print(f"[ERROR] 加载装备数据失败: {e}")
            import traceback
            traceback.print_exc()
            self.show_status("装备数据加载失败", "red")

    def update_calculation(self):
        """更新计算"""
        print(f"\n[MainWindow] 开始更新计算")
        try:
            if not self.current_base_stats:
                print(f"[MainWindow] 警告: 当前基础属性为空")
                self.show_status("请先选择角色", "orange")
                return

            # 获取驱动盘数据
            gear_pieces = self.get_all_gear_pieces()
            print(f"[MainWindow] 获取到 {len(gear_pieces)} 个驱动盘")

            if not self.gear_calculator:
                print(f"[MainWindow] 错误: 计算器未初始化")
                self.show_status("计算器未初始化", "red")
                return

            # 计算最终属性
            print(f"[MainWindow] 开始计算最终属性...")

            # 获取强化等级（从UI变量）
            level = self.main_enhance_level.get()

            # 调用计算器的完整计算
            final_stats = self.gear_calculator.calculate_complete_stats(
                self.current_base_stats,
                gear_pieces,
                self.gear_set_selection,
                level  # 添加强化等级参数
            )

            if not final_stats:
                print(f"[MainWindow] 错误: 计算返回空结果")
                self.show_status("计算返回空结果", "red")
                return

            # 输出计算结果
            print(f"[MainWindow] 计算完成，最终属性类型: {type(final_stats)}")

            # 将最终属性转换为字典格式以便显示
            if hasattr(final_stats, '__dict__'):
                display_stats = {}
                for key, value in final_stats.__dict__.items():
                    if not key.startswith('_'):
                        # 转换属性名为小写以匹配显示
                        display_stats[key.lower()] = value
            else:
                # 如果是其他类型，尝试直接传递
                display_stats = final_stats

            # 更新显示
            print(f"[MainWindow] 调用character_panel.update_final_stats_display")
            self.character_panel.update_final_stats_display(display_stats)
            self.show_status("计算完成", "green")

        except Exception as e:
            error_msg = f"计算错误: {str(e)}"
            print(f"[MainWindow] 错误: {error_msg}")
            self.show_status(error_msg, "red")
            import traceback
            traceback.print_exc()

    def get_all_gear_pieces(self) -> List[GearPiece]:
        """获取所有驱动盘配置"""
        if hasattr(self, 'gear_widgets') and self.gear_widgets:
            return [widget.get_gear_piece() for widget in self.gear_widgets]
        return self.gear_pieces

    def set_current_base_stats(self, base_stats: CharacterAttributesModel):
        """设置当前基础属性"""
        self.current_base_stats = base_stats
        # 同时更新到角色面板
        if hasattr(self, 'character_panel'):
            self.character_panel.current_base_stats = base_stats

    def update_gear_data(self):
        """更新驱动盘数据"""
        self.update_calculation()

    def show_status(self, message: str, color: str = "black"):
        """显示状态信息"""
        self.status_label.config(text=message, foreground=color)


class CharacterConfigTab(ttk.Frame):
    """角色配置选项卡 - 简化版"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.current_character_id = 0
        self.current_weapon_id = 0
        self.t = False
        self.character_var = tk.StringVar()
        self.weapon_var = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 角色选择区域
        selection_frame = ttk.LabelFrame(main_frame, text="角色选择", padding="15")
        selection_frame.pack(fill='x', pady=(0, 15))

        ttk.Label(selection_frame, text="选择角色:").grid(
            row=0, column=0, sticky='w', pady=5
        )

        # 获取角色列表
        characters = self.main_window.character_manager.get_available_characters()
        character_names = [char["name"] for char in characters]

        self.character_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.character_var,
            values=character_names,
            state="readonly",
            width=20
        )
        self.character_combo.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        self.character_combo.bind('<<ComboboxSelected>>', self.on_character_selected)

        # 角色数量显示
        ttk.Label(
            selection_frame,
            text=f"共 {len(character_names)} 个角色",
            foreground="gray"
        ).grid(row=0, column=2, padx=(20, 0), pady=5, sticky='w')

        # 等级配置区域
        level_frame = ttk.LabelFrame(main_frame, text="等级配置", padding="15")
        level_frame.pack(fill='x', pady=(0, 15))

        # 角色等级
        ttk.Label(level_frame, text="角色等级:").grid(
            row=0, column=0, sticky='w', pady=8
        )
        levels = list(range(1, 61))
        level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.main_window.character_level,
            values=levels,
            state="readonly",
            width=8
        )
        level_combo.grid(row=0, column=1, padx=(10, 30), pady=8, sticky='w')
        level_combo.bind('<<ComboboxSelected>>', self.on_config_changed)

        # 核心技等级
        ttk.Label(level_frame, text="核心技等级:").grid(
            row=0, column=2, sticky='w', pady=8
        )
        extra_levels = list(range(1, 8))
        extra_combo = ttk.Combobox(
            level_frame,
            textvariable=self.main_window.extra_level,
            values=extra_levels,
            state="readonly",
            width=8
        )
        extra_combo.grid(row=0, column=3, padx=10, pady=8, sticky='w')
        extra_combo.bind('<<ComboboxSelected>>', self.on_config_changed)

        weapon_frame = ttk.LabelFrame(main_frame, text="音擎配置", padding="15")
        weapon_frame.pack(fill='x', pady=(0, 15))

        ttk.Label(weapon_frame, text="选择音擎:").grid(
            row=0, column=0, sticky='w', pady=8
        )

        # 获取音擎列表
        weapons = self.main_window.weapon_manager.get_available_weapons()
        weapon_names = [char["name"] for char in weapons]

        self.weapon_combo = ttk.Combobox(
            weapon_frame,
            textvariable=self.weapon_var,
            values=weapon_names,
            state="readonly",
            width=20
        )
        self.weapon_combo.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        self.weapon_combo.bind('<<ComboboxSelected>>', self.on_weapon_selected)

        # 音擎等级（与角色等级分开）
        ttk.Label(weapon_frame, text="音擎等级:").grid(
            row=0, column=2, sticky='w', pady=8, padx=(20, 5)
        )

        weapon_levels = list(range(1, 61))
        self.weapon_level_combo = ttk.Combobox(
            weapon_frame,
            textvariable=self.main_window.weapon_level,
            values=weapon_levels,
            state="readonly",
            width=8
        )
        self.weapon_level_combo.grid(row=0, column=3, pady=8, sticky='w')
        self.weapon_level_combo.bind('<<ComboboxSelected>>', self.on_weapon_config_changed)

    def on_character_selected(self, event):
        """角色选择事件"""
        character_name = self.character_var.get()
        if character_name:
            character_id = self.main_window.character_manager.get_character_id_by_name(character_name)
            if character_id:
                self.current_character_id = character_id
                self.main_window.character_panel.load_character_by_name(character_name)
                weapon_id = int(f"1{self.main_window.current_base_stats.rarity}{character_id // 10}")
                weapon_name = self.main_window.weapon_manager.get_weapon_name_by_id(weapon_id)
                self.current_weapon_id = weapon_id
                self.weapon_var.set(weapon_name)
                self.apply_weapon_to_character()
                self.main_window.show_status(f"已选择: {character_name}", "green")

    def on_weapon_selected(self, event):
        """音擎选择事件"""
        weapon_name = self.weapon_var.get()
        if weapon_name:
            weapon_id = self.main_window.weapon_manager.get_weapon_id_by_name(weapon_name)
            if weapon_id:
                self.current_weapon_id = weapon_id
                self.apply_weapon_to_character()
                self.main_window.show_status(f"已选择音擎: {weapon_name}", "green")

    def on_config_changed(self, event):
        """配置改变事件"""
        if not self.current_character_id:
            return

        character_name = self.character_var.get()
        if character_name:
            try:
                self.main_window.character_panel.load_character_by_name(character_name)

                self.main_window.show_status("配置已更新", "blue")

            except Exception as e:
                self.main_window.show_status(f"配置更新失败: {str(e)}", "red")

    def on_weapon_config_changed(self, event):
        """音擎配置改变事件"""
        if self.current_weapon_id:
            self.apply_weapon_to_character()
            self.main_window.show_status("音擎配置已更新", "blue")

    def apply_weapon_to_character(self):
        """应用音擎属性到角色"""
        if not self.current_weapon_id:
            return

        if not self.main_window.current_base_stats:
            return

        if not self.t:
            try:
                level = self.main_window.weapon_level.get()

                # 获取角色当前的基础属性（复制一份）
                from copy import deepcopy
                base_stats_before = deepcopy(self.main_window.current_base_stats)

                # 应用音擎属性
                success = self.main_window.weapon_manager.apply_weapon_to_character(
                    self.main_window.current_base_stats,
                    self.current_weapon_id,
                    level
                )
                print(f"success:{success}")

                if success:
                    # 计算音擎带来的攻击力加成
                    attack_before = base_stats_before.attack
                    attack_after = self.main_window.current_base_stats.attack
                    weapon_attack_gain = attack_after - attack_before

                    print(f"[Weapon] 音擎攻击力加成: +{weapon_attack_gain:.0f}")

                    # 更新角色面板显示
                    self.main_window.character_panel.update_with_character_data(
                        self.main_window.current_base_stats
                    )

                    # 触发重新计算（包含驱动盘）
                    self.main_window.update_calculation()

                    self.main_window.show_status(f"音擎属性已应用 (+{weapon_attack_gain:.0f}攻击)", "green")
                    self.t = True
                else:
                    self.main_window.show_status("应用音擎属性失败", "red")

            except Exception as e:
                import traceback
                traceback.print_exc()
                self.main_window.show_status(f"应用音擎属性失败: {str(e)}", "red")
        else:
            print("不能重复计算音擎加成")


class GearConfigTab(ttk.Frame):
    """驱动盘配置选项卡"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.all_sets_display = []  # 存储所有套装显示文本
        self.selected_sets = []  # 存储已选择的套装ID - 修复属性名
        self.all_sets_data = []  # 存储所有套装数据
        self.setup_ui()

        self.load_set_data_to_combos()

    def setup_ui(self):
        """设置UI"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 强化设置
        self.setup_enhancement_settings(main_frame)

        # 套装选择
        self.setup_set_selection(main_frame)

        # 驱动盘槽位
        self.setup_gear_slots(main_frame)

    def setup_enhancement_settings(self, parent):
        """设置增强等级区域"""
        enhance_frame = ttk.LabelFrame(parent, text="驱动盘强化设置", padding="15")
        enhance_frame.pack(fill='x', pady=(0, 15))

        ttk.Label(enhance_frame, text="主属性强化等级:").grid(
            row=0, column=0, sticky='w', pady=5
        )

        levels = list(range(0, 16))
        enhance_combo = ttk.Combobox(
            enhance_frame,
            textvariable=self.main_window.main_enhance_level,
            values=levels,
            state="readonly",
            width=10
        )
        enhance_combo.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        enhance_combo.bind('<<ComboboxSelected>>', self.on_enhance_level_changed)

        # 重置按钮
        reset_btn = ttk.Button(
            enhance_frame,
            text="重置所有驱动盘",
            command=self.reset_all_gears
        )
        reset_btn.grid(row=0, column=2, padx=(30, 0), pady=5, sticky='w')

    def setup_set_selection(self, parent):
        """设置套装选择区域"""
        set_frame = ttk.LabelFrame(parent, text="套装效果选择", padding="15")
        set_frame.pack(fill='x', pady=(0, 15))

        # 组合类型选择
        ttk.Label(set_frame, text="组合类型:").grid(
            row=0, column=0, sticky='w', pady=5
        )

        self.combination_type_var = tk.StringVar(value="4+2")
        type_combo = ttk.Combobox(
            set_frame,
            textvariable=self.combination_type_var,
            values=["4+2", "2+2+2"],
            state="readonly",
            width=8
        )
        type_combo.grid(row=0, column=1, padx=(10, 30), pady=5, sticky='w')
        type_combo.bind('<<ComboboxSelected>>', self.on_combination_type_changed)

        # 套装选择框架
        self.set_selection_frame = ttk.Frame(set_frame)
        self.set_selection_frame.grid(row=1, column=0, columnspan=6, sticky='we', pady=(10, 0))

        # 使用新的 GearSetComboBox
        self.set_combos: List[GearSetComboBox] = []

        # 初始创建
        self.create_set_selection_widgets("4+2")

        # 套装效果预览
        self.set_preview_label = ttk.Label(
            set_frame,
            text="请选择套装",
            foreground="blue",
            wraplength=600
        )
        self.set_preview_label.grid(
            row=2, column=0, columnspan=6, sticky='w', pady=(10, 0)
        )

    def create_set_selection_widgets(self, combination_type: str):
        """创建套装选择组件 - 使用 GearSetComboBox"""
        # 清除现有组件
        for widget in self.set_selection_frame.winfo_children():
            widget.destroy()

        self.set_combos = []

        # 根据组合类型确定需要的套装数量
        if combination_type == "4+2":
            set_count = 2
            labels = ["4件套:", "2件套:"]
            # 调整 selected_sets 长度
            self.selected_sets = self.selected_sets[:2] if len(self.selected_sets) >= 2 else [0, 0]
            if len(self.selected_sets) < 2:
                self.selected_sets = self.selected_sets + [0] * (2 - len(self.selected_sets))
        else:  # "2+2+2"
            set_count = 3
            labels = ["套装1:", "套装2:", "套装3:"]
            # 调整 selected_sets 长度
            self.selected_sets = self.selected_sets[:3] if len(self.selected_sets) >= 3 else [0, 0, 0]
            if len(self.selected_sets) < 3:
                self.selected_sets = self.selected_sets + [0] * (3 - len(self.selected_sets))

        print(f"[create_set_selection_widgets] 创建 {set_count} 个下拉框, selected_sets: {self.selected_sets}")

        # 创建套装选择组件
        for i in range(set_count):
            # 标签
            ttk.Label(self.set_selection_frame, text=labels[i]).grid(
                row=0, column=i * 2, sticky='w', pady=5, padx=(0, 5)
            )

            # 使用新的 GearSetComboBox
            combo = GearSetComboBox(
                self.set_selection_frame,
                width=25,
                on_selected_callback=lambda c, old, new, idx=i: self.on_set_selected(idx, old, new)
            )
            combo.grid(row=0, column=i * 2 + 1, padx=(0, 10), pady=5, sticky='w')

            self.set_combos.append(combo)

        # 如果数据已加载，立即更新下拉框
        if hasattr(self, 'all_sets_data') and self.all_sets_data:
            self.update_combo_lists()

    def on_combination_type_changed(self, event=None):
        """组合类型改变事件"""
        combination_type = self.combination_type_var.get()
        print(f"[GearConfig] 组合类型改变: {combination_type}")

        # 重新创建套装选择组件（会处理 selected_sets 长度调整）
        self.create_set_selection_widgets(combination_type)

        # 确保数据已加载
        if hasattr(self, 'all_sets_data') and self.all_sets_data:
            self.update_combo_lists()

        # 更新计算
        self.update_gear_set_selection()
        self.update_set_preview()
        self.main_window.update_calculation()

    def on_set_selected(self, combo_index: int, old_set_id: Optional[int], new_set_id: Optional[int]):
        """套装选择事件 - 适配 GearSetComboBox"""
        print(f"[DEBUG] on_set_selected - combo_index: {combo_index}, old: {old_set_id}, new: {new_set_id}")

        if not hasattr(self, 'set_combos') or combo_index >= len(self.set_combos):
            print(f"[DEBUG] 错误: set_combos 不存在或索引越界")
            return

        combo = self.set_combos[combo_index]

        # 处理清空选择的情况
        if new_set_id is None:
            print(f"[DEBUG] 清空选择: 位置 {combo_index}")

            # 更新 selected_sets
            if combo_index < len(self.selected_sets):
                self.selected_sets[combo_index] = 0

            # 更新其他下拉框
            self.update_combo_lists()

            # 更新套装选择和预览
            self.update_gear_set_selection()
            self.update_set_preview()
            self.main_window.update_calculation()
            return

        # 检查是否已经选择了这个套装（在不同位置）
        for i, selected_id in enumerate(self.selected_sets):
            if i != combo_index and selected_id == new_set_id:
                print(f"[DEBUG] 错误: 套装 {new_set_id} 已在位置 {i} 被选择")

                # 恢复到之前的选择
                old_set_id_in_list = self.selected_sets[combo_index] if combo_index < len(self.selected_sets) else 0
                if old_set_id_in_list != 0:
                    # 使用 GearSetComboBox 的方法设置回原来的选择
                    combo.set_selected_set_id(old_set_id_in_list)
                else:
                    combo.clear_selection()

                # 显示提示（可选）
                # import tkinter.messagebox as messagebox
                # messagebox.showwarning("重复选择", "该套装已被其他位置选择，请选择其他套装。")
                return

        # 确保 selected_sets 列表足够长
        while len(self.selected_sets) <= combo_index:
            self.selected_sets.append(0)
            print(f"[DEBUG] 扩展 selected_sets 到长度 {len(self.selected_sets)}")

        # 更新选中列表
        old_set_id_in_list = self.selected_sets[combo_index]
        self.selected_sets[combo_index] = new_set_id

        print(f"[DEBUG] 更新后 selected_sets: {self.selected_sets}")

        # 更新其他下拉框的可用选项
        self.update_combo_lists()

        # 更新套装选择和预览
        self.update_gear_set_selection()
        self.update_set_preview()
        self.main_window.update_calculation()

    def on_set_changed(self, combo_index: int):
        """套装更改事件（如手动清空）"""
        combo = self.set_combos[combo_index]
        display_text = combo.get()

        if not display_text:
            # 清空了选择
            if combo_index < len(self.selected_sets):
                old_set_id = self.selected_sets[combo_index]
                if old_set_id != 0:
                    print(f"[GearConfig] 清空套装选择: {old_set_id}")
                    self.selected_sets[combo_index] = 0

                    # 更新下拉框列表
                    self.update_combo_lists()

                    # 更新套装选择和预览
                    self.update_gear_set_selection()
                    self.update_set_preview()
                    self.main_window.update_calculation()

    def load_set_data_to_combos(self):
        """加载套装数据到下拉框"""
        try:
            # 检查是否有套装管理器
            if not self.main_window.gear_set_manager:
                print("[load_set_data_to_combos] 警告: gear_set_manager 未加载")
                return

            # 获取套装列表
            sets = self.main_window.gear_set_manager.get_available_sets()
            if not sets:
                print("[load_set_data_to_combos] 警告: 无可用套装数据")
                return

            # 转换为需要的格式
            self.all_sets_data = []
            for set_info in sets:
                self.all_sets_data.append({
                    'id': set_info['id'],
                    'name': set_info['name'],
                    'bonus_display': set_info['bonus_display'],
                    'data': set_info  # 保留原始数据
                })

            print(f"[load_set_data_to_combos] 加载了 {len(self.all_sets_data)} 个套装")
            print(f"[load_set_data_to_combos] 当前 selected_sets: {self.selected_sets}")

            # 如果下拉框已创建，更新它们
            if hasattr(self, 'set_combos') and self.set_combos:
                self.update_combo_lists()

        except Exception as e:
            print(f"[GearConfig] 加载套装数据失败: {e}")
            import traceback
            traceback.print_exc()

    def update_combo_lists(self):
        """更新所有下拉框的选项列表"""
        if not hasattr(self, 'all_sets_data') or not self.all_sets_data:
            print("[update_combo_lists] 警告: 套装数据未加载")
            return

        # 确保 selected_sets 存在
        if not hasattr(self, 'selected_sets') or self.selected_sets is None:
            self.selected_sets = []

        # 过滤有效的已选套装ID（非0值）
        selected_set_ids = [sid for sid in self.selected_sets if sid != 0]
        print(f"[update_combo_lists] 当前已选套装ID: {selected_set_ids}")

        # 更新每个下拉框
        for i, combo in enumerate(self.set_combos):
            # 构建这个下拉框的可用套装列表
            available_sets = []

            for set_data in self.all_sets_data:
                set_id = set_data['id']

                # 检查是否被其他下拉框选中
                is_selected_by_others = False
                for j, selected_id in enumerate(selected_set_ids):
                    # 跳过当前下拉框自己的选择
                    if j != i and selected_id == set_id:
                        is_selected_by_others = True
                        break

                if not is_selected_by_others:
                    available_sets.append(set_data)

            # 设置可用套装到下拉框
            combo.set_available_sets(available_sets)

            # 设置选中的套装（如果当前下拉框有选择）
            if i < len(self.selected_sets):
                set_id = self.selected_sets[i]
                combo.set_selected_set_id(set_id if set_id != 0 else None)

    def update_gear_set_selection(self):
        """更新套装选择"""
        combination_type = self.combination_type_var.get()
        set_ids = []

        # 只添加非0的套装ID
        for set_id in self.selected_sets:
            if set_id != 0:
                set_ids.append(set_id)

        print(f"[GearConfig] 更新套装选择: {combination_type}, IDs: {set_ids}")

        self.main_window.gear_set_selection = GearSetSelection(
            combination_type=combination_type,
            set_ids=set_ids
        )

    def update_set_preview(self):
        """更新套装效果预览"""
        if not self.main_window.gear_set_manager:
            return

        combination_type = self.combination_type_var.get()
        preview_text = []

        # 根据组合类型确定显示的数量
        if combination_type == "4+2":
            max_sets = 2
        else:  # "2+2+2"
            max_sets = 3

        for i in range(max_sets):
            if i < len(self.selected_sets) and self.selected_sets[i] != 0:
                set_id = self.selected_sets[i]
                effect = self.main_window.gear_set_manager.set_effects.get(set_id)
                if effect:
                    if combination_type == "4+2":
                        if i == 0:
                            preview_text.append(f"4件套: {effect.name}")
                            preview_text.append(f"  二件套: {effect.desc2}")
                        else:
                            preview_text.append(f"2件套: {effect.name}")
                            preview_text.append(f"  二件套: {effect.desc2}")
                    else:
                        preview_text.append(f"套装{i + 1}: {effect.name}")
                        preview_text.append(f"  二件套: {effect.desc2}")

        if preview_text:
            self.set_preview_label.config(text="\n".join(preview_text))
        else:
            self.set_preview_label.config(text="请选择套装")

    def setup_gear_slots(self, parent):
        """设置驱动盘槽位"""
        gears_frame = ttk.LabelFrame(parent, text="驱动盘配置 (6个槽位)", padding="10")
        gears_frame.pack(fill='both', expand=True)

        # 创建3x2网格布局
        for i in range(3):
            gears_frame.columnconfigure(i, weight=1)
        for i in range(2):
            gears_frame.rowconfigure(i, weight=1)

        self.gear_widgets = []
        for i in range(6):
            gear_widget = GearSlotWidget(gears_frame, i + 1, self.main_window)
            row = i // 3
            col = i % 3
            gear_widget.grid(
                row=row, column=col,
                padx=5, pady=5,
                sticky="nsew"
            )
            self.gear_widgets.append(gear_widget)

        self.main_window.gear_widgets = self.gear_widgets

    def on_enhance_level_changed(self, event):
        """强化等级改变事件"""
        new_level = self.main_window.main_enhance_level.get()

        for gear_widget in self.gear_widgets:
            gear_widget.update_main_attribute_value()

        self.main_window.update_calculation()
        self.main_window.show_status(f"强化等级已更新: {new_level}", "blue")

    def reset_all_gears(self):
        """重置所有驱动盘"""
        for gear_widget in self.gear_widgets:
            gear_widget.reset()

        self.main_window.update_calculation()
        self.main_window.show_status("已重置所有驱动盘", "blue")

    def get_set_display_by_id(self, set_id: int) -> Optional[str]:
        """根据套装ID获取显示文本"""
        if not hasattr(self, 'all_sets_data') or not self.all_sets_data:
            print(f"[get_set_display_by_id] 警告: all_sets_data 为空")
            return None

        for set_data in self.all_sets_data:
            if set_data['id'] == set_id:
                return set_data['display']

        print(f"[get_set_display_by_id] 警告: 未找到套装 {set_id}")
        return None