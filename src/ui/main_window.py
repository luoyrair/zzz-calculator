# src/ui/main_window.py
"""重构后的主窗口 - 优化布局和交互"""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional

from src import get_service_factory
from src.core.models.character import CharacterBaseStats
from src.core.models.gear import GearPiece, GearSetSelection
from src.services.character import CharacterService
from src.services.weapon import WeaponService
from .character_panel import CharacterPanel
from .gear_slot import GearSlotWidget, GearSlotManager
from src.core.calculator import GearSetManager


class MainWindow:
    """主窗口 - 优化版本"""

    def __init__(self, root):
        self.root = root
        self.root.title("绝区零驱动盘属性计算器 - 新架构")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.left_frame = ttk.Frame(self.main_frame)
        self.character_panel = CharacterPanel(self.left_frame, self)
        self.right_frame = ttk.Frame(self.main_frame)
        self.notebook = ttk.Notebook(self.right_frame)

        self.status_frame = ttk.Frame(self.right_frame)
        self.status_label = ttk.Label(
            self.status_frame,
            text="就绪",
            relief="sunken",
            anchor="w"
        )

        # 初始化服务
        self.service_factory = get_service_factory()

        # 使用新的服务
        self.character_service: Optional[CharacterService] = None
        self.weapon_service: Optional[WeaponService] = None
        self.character_manager = self.service_factory.character_manager
        self.gear_calculator = self.service_factory.gear_calculator

        # 当前状态
        self.current_base_stats: Optional[CharacterBaseStats] = None
        self.gear_pieces: List[GearPiece] = []
        self.gear_set_selection = GearSetSelection("4+2", [])
        self.gear_widgets = []

        # UI变量
        self.character_level = tk.IntVar(value=60)
        self.extra_level = tk.IntVar(value=7)
        self.main_enhance_level = tk.IntVar(value=15)

        # 槽位管理器
        self.gear_slot_manager = GearSlotManager(self)

        # 套装管理器
        self.gear_set_manager: Optional[GearSetManager] = None

        # 加载装备数据
        self.load_equipment_data()

        self.setup_ui()
        self.initialize_application()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        self.main_frame.pack(fill='both', expand=True)

        # 配置网格权重
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # 左侧角色面板
        self.setup_left_panel()

        # 右侧配置面板
        self.setup_right_panel()

    def setup_left_panel(self):
        """设置左侧角色面板"""
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(0, weight=1)

        # 角色面板
        self.character_panel.pack(fill='both', expand=True)

    def setup_right_panel(self):
        """设置右侧配置面板"""
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(1, weight=1)

        # 创建选项卡
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.right_frame.rowconfigure(0, weight=1)

        # 角色配置选项卡
        self.character_tab = CharacterConfigTab(self.notebook, self)
        self.notebook.add(self.character_tab, text="角色配置")

        # 驱动盘配置选项卡
        gear_tab = GearConfigTab(self.notebook, self)
        self.notebook.add(gear_tab, text="驱动盘配置")

        # 状态栏
        self.setup_status_bar()

    def setup_status_bar(self):
        """设置状态栏"""
        self.status_frame.grid(row=1, column=0, sticky="we", pady=(5, 0))
        self.status_label.pack(fill='x', padx=5, pady=2)

    def initialize_application(self):
        """初始化应用程序"""
        try:
            # 初始化配置
            from src import config_manager
            if not config_manager.initialize():
                self.show_status("配置初始化失败", "red")
                return

            # 初始化服务
            self.character_service = self.service_factory.character_service
            self.weapon_service = self.service_factory.weapon_service

            self.show_status("配置加载成功", "green")

            # 预加载第一个角色
            self.load_first_character()

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
                self.character_panel.load_character_by_name(first_character["name"])
                self.show_status(f"已加载角色: {first_character['name']}", "green")
            else:
                self.show_status("未找到可用角色", "orange")
        except Exception as e:
            self.show_status(f"加载角色失败: {str(e)}", "red")

    def load_equipment_data(self):
        """加载装备数据"""
        try:
            from src import config_manager
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
            else:
                print(f"[WARNING] 装备文件不存在: {equipment_file}")

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

            for i, piece in enumerate(gear_pieces):
                print(
                    f"[MainWindow]  驱动盘{i + 1}: 槽位={piece.slot_index}, 主属性={piece.main_gear_key}, 主值={piece.main_value}")
                for j, sub_attr in enumerate(piece.sub_attributes):
                    print(f"[MainWindow]    副属性{j + 1}: {sub_attr.gear_key}={sub_attr.value}")

            if not self.gear_calculator:
                print(f"[MainWindow] 错误: 计算器未初始化")
                self.show_status("计算器未初始化", "red")
                return

            # 计算最终属性
            print(f"[MainWindow] 开始计算最终属性...")
            final_stats = self.gear_calculator.calculate_complete_stats(
                self.current_base_stats,
                gear_pieces,
                self.gear_set_selection
            )

            # 输出计算结果
            print(f"[MainWindow] 计算完成，最终属性类型: {type(final_stats)}")
            if hasattr(final_stats, 'HP'):
                print(f"[MainWindow] 基础HP: {self.current_base_stats.HP}, 最终HP: {final_stats.HP}")
                print(
                    f"[MainWindow] 装备加成HP: {final_stats.gear_bonuses.HP if hasattr(final_stats, 'gear_bonuses') else 'N/A'}")

            # 更新显示
            print(f"[MainWindow] 调用character_panel.update_final_stats_display")
            self.character_panel.update_final_stats_display(final_stats)
            self.show_status("计算完成", "green")

        except Exception as e:
            error_msg = f"计算错误: {str(e)}"
            print(f"[MainWindow] 错误: {error_msg}")
            self.show_status(error_msg, "red")
            self.character_panel.show_error(error_msg)
            import traceback
            traceback.print_exc()

    def get_all_gear_pieces(self) -> List[GearPiece]:
        """获取所有驱动盘配置"""
        if hasattr(self, 'gear_widgets') and self.gear_widgets:
            return [widget.get_gear_piece() for widget in self.gear_widgets]
        return self.gear_pieces

    def set_current_base_stats(self, base_stats: CharacterBaseStats):
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
    """角色配置选项卡"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.current_character_id = ""
        self.character_var = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 角色选择区域
        self.setup_character_selection(main_frame)

        # 等级配置区域
        self.setup_level_configuration(main_frame)

    def setup_character_selection(self, parent):
        """设置角色选择区域"""
        selection_frame = ttk.LabelFrame(parent, text="角色选择", padding="15")
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

    def setup_level_configuration(self, parent):
        """设置等级配置区域"""
        level_frame = ttk.LabelFrame(parent, text="等级配置", padding="15")
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

    def on_character_selected(self, event):
        """角色选择事件"""
        character_name = self.character_var.get()
        if character_name:
            character_id = self.main_window.character_manager.get_character_id_by_name(character_name)
            if character_id:
                self.current_character_id = character_id

                # 使用角色面板加载角色
                self.main_window.character_panel.load_character_by_name(character_name)
                self.main_window.show_status(f"已选择: {character_name}", "green")

    def on_config_changed(self, event):
        """配置改变事件"""
        if not self.current_character_id:
            return

        character_name = self.character_var.get()
        if character_name:
            # 重新加载角色以应用新的等级配置
            self.main_window.character_panel.load_character_by_name(character_name)
            self.main_window.show_status("配置已更新", "blue")


class GearConfigTab(ttk.Frame):
    """驱动盘配置选项卡"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()
        self.all_sets_display = []  # 存储所有套装显示文本
        self.selected_sets = []  # 存储已选择的套装ID - 修复属性名
        self.all_sets_data = []  # 存储所有套装数据

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

        # 套装选择框架（动态创建）
        self.set_selection_frame = ttk.Frame(set_frame)
        self.set_selection_frame.grid(row=1, column=0, columnspan=6, sticky='we', pady=(10, 0))

        # 套装选择变量和下拉框
        self.set_vars = []
        self.set_combos = []

        # 套装效果预览
        self.set_preview_label = ttk.Label(
            set_frame,
            text="请选择组合类型",
            foreground="blue",
            wraplength=600
        )
        self.set_preview_label.grid(
            row=2, column=0, columnspan=6, sticky='w', pady=(10, 0)
        )

        # 初始创建4+2的套装选择
        self.create_set_selection_widgets("4+2")

    def create_set_selection_widgets(self, combination_type: str):
        """创建套装选择组件"""
        # 清除现有组件
        for widget in self.set_selection_frame.winfo_children():
            widget.destroy()

        self.set_vars = []
        self.set_combos = []

        # 根据组合类型确定需要的套装数量
        if combination_type == "4+2":
            set_count = 2
            labels = ["4件套:", "2件套:"]
        else:  # "2+2+2"
            set_count = 3
            labels = ["套装1:", "套装2:", "套装3:"]

        # 创建套装选择组件
        for i in range(set_count):
            # 标签
            ttk.Label(self.set_selection_frame, text=labels[i]).grid(
                row=0, column=i * 2, sticky='w', pady=5, padx=(0, 5)
            )

            # 变量
            set_var = tk.StringVar()
            self.set_vars.append(set_var)

            # 下拉框
            combo = ttk.Combobox(
                self.set_selection_frame,
                textvariable=set_var,
                state="readonly",
                width=25
            )
            combo.grid(row=0, column=i * 2 + 1, padx=(0, 10), pady=5, sticky='w')

            # 绑定事件，传递索引
            combo.bind('<<ComboboxSelected>>',
                       lambda e, idx=i: self.on_set_selected(idx))

            self.set_combos.append(combo)

        # 加载套装数据
        self.load_set_data_to_combos()

    def on_combination_type_changed(self, event=None):
        """组合类型改变事件"""
        combination_type = self.combination_type_var.get()
        print(f"[GearConfig] 组合类型改变: {combination_type}")

        # 重置选中的套装
        self.selected_sets = []

        # 重新创建套装选择组件
        self.create_set_selection_widgets(combination_type)

        # 更新计算
        self.update_gear_set_selection()
        self.update_set_preview()
        self.main_window.update_calculation()

    def on_set_selected(self, combo_index: int):
        """套装选择事件"""
        combo = self.set_combos[combo_index]
        display_text = combo.get()

        if not display_text:
            return

        try:
            # 解析套装ID
            set_id = int(display_text.split(' - ')[0])

            # 确保 selected_sets 列表足够长
            while len(self.selected_sets) <= combo_index:
                self.selected_sets.append(0)

            # 移除旧的选中（如果有）
            old_set_id = self.selected_sets[combo_index]
            if old_set_id != 0 and old_set_id != set_id:
                print(f"[GearConfig] 移除旧的套装选择: {old_set_id}")

            # 更新选中列表
            self.selected_sets[combo_index] = set_id

            print(f"[GearConfig] 选择了套装: {set_id} (位置{combo_index})")
            print(f"[GearConfig] 当前选中套装: {self.selected_sets}")

            # 更新其他下拉框的可用选项
            self.update_combo_lists()

            # 更新套装选择和预览
            self.update_gear_set_selection()
            self.update_set_preview()
            self.main_window.update_calculation()

        except (ValueError, IndexError) as e:
            print(f"[GearConfig] 解析套装ID失败: {e}")

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
                self.set_preview_label.config(text="套装数据未加载", foreground="red")
                return

            # 获取套装列表
            sets = self.main_window.gear_set_manager.get_available_sets()
            if not sets:
                self.set_preview_label.config(text="无可用套装数据", foreground="orange")
                return

            # 清空之前的缓存
            self.all_sets_display = []
            self.all_sets_data = []
            self.selected_sets = []  # 初始化选中的套装列表

            # 格式化显示文本
            for set_info in sets:
                display_text = f"{set_info['id']} - {set_info['name']}"
                if set_info['bonus_display'] != "无基础属性加成":
                    display_text += f" ({set_info['bonus_display']})"

                self.all_sets_display.append(display_text)
                self.all_sets_data.append({
                    'id': set_info['id'],
                    'display': display_text,
                    'data': set_info
                })

            print(f"[GearConfig] 加载了 {len(self.all_sets_data)} 个套装")

            # 初始更新所有下拉框
            self.update_combo_lists()

        except Exception as e:
            print(f"[GearConfig] 加载套装数据失败: {e}")
            self.set_preview_label.config(text=f"加载套装数据失败: {e}", foreground="red")

    def update_combo_lists(self):
        """更新所有下拉框的选项列表"""
        # 构建可用套装列表（排除已选择的）
        available_sets = []
        for set_data in self.all_sets_data:
            if set_data['id'] not in self.selected_sets:
                available_sets.append(set_data['display'])

        print(f"[GearConfig] 可用套装: {len(available_sets)} 个 (已选择: {len(self.selected_sets)} 个)")

        # 更新所有下拉框
        for i, combo in enumerate(self.set_combos):
            current_value = combo.get()
            combo['values'] = available_sets

            # 如果当前值不在可用列表中，清空它
            if current_value and current_value not in available_sets:
                print(f"[GearConfig] 清空下拉框 {i}: {current_value} 不再可用")
                combo.set("")

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
                            preview_text.append(f"  四件套: {effect.desc4}")
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