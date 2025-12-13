"""驱动盘配置选项卡 - 单一职责"""
import tkinter as tk
from tkinter import ttk

from src.ui.gear_slot import GearSlotManager, GearSlotWidget
from src.ui.widget.gear_set_combo import GearSetComboBox


class GearConfigTab(ttk.Frame):
    """驱动盘配置选项卡 - 只负责驱动盘配置"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window

        # 驱动盘槽位管理器
        self.gear_slot_manager = GearSlotManager(self.main_window)

        # 套装相关
        self.selected_sets = []
        self.combination_type_var = tk.StringVar(value="4+2")

        # 初始化UI
        self.setup_ui()

        # 加载套装数据
        self.load_set_data()

    def setup_ui(self):
        """设置UI - 移除滚动功能"""
        # 主框架，使用pack布局
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 设置左侧内容
        self.setup_enhancement_settings(main_frame)
        self.setup_set_selection(main_frame)

        # 设置右侧内容
        self.setup_gear_slots(main_frame)

        # 底部：计算按钮
        self.setup_calculation_button(main_frame)

    def setup_enhancement_settings(self, parent):
        """设置增强等级区域"""
        enhance_frame = ttk.LabelFrame(parent, text="驱动盘强化设置", padding="15")
        enhance_frame.pack(fill='x', pady=(0, 15))

        # 主属性强化等级
        ttk.Label(enhance_frame, text="主属性强化等级:").grid(
            row=0, column=0, sticky='w', pady=5
        )

        levels = list(range(0, 16))
        self.enhance_combo = ttk.Combobox(
            enhance_frame,
            textvariable=self.main_window.main_enhance_level,
            values=levels,
            state="readonly",
            width=10
        )
        self.enhance_combo.grid(row=0, column=1, padx=10, pady=5, sticky='w')

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

        self.type_combo = ttk.Combobox(
            set_frame,
            textvariable=self.combination_type_var,
            values=["4+2", "2+2+2"],
            state="readonly",
            width=8
        )
        self.type_combo.grid(row=0, column=1, padx=(10, 30), pady=5, sticky='w')
        self.type_combo.bind('<<ComboboxSelected>>', self.on_combination_type_changed)

        # 套装选择框架
        self.set_selection_frame = ttk.Frame(set_frame)
        self.set_selection_frame.grid(row=1, column=0, columnspan=6, sticky='we', pady=(10, 0))

        # 使用 GearSetComboBox
        self.set_combos = []

        # 初始创建
        self.create_set_selection_widgets("4+2")

        # 套装效果预览
        self.set_preview_label = ttk.Label(
            set_frame,
            text="请选择套装",
            foreground="blue",
            wraplength=250
        )
        self.set_preview_label.grid(
            row=2, column=0, columnspan=6, sticky='w', pady=(10, 0)
        )

    def create_set_selection_widgets(self, combination_type: str):
        """创建套装选择组件"""
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

        # 创建套装选择组件
        for i in range(set_count):
            # 标签
            ttk.Label(self.set_selection_frame, text=labels[i]).grid(
                row=0, column=i * 2, sticky='w', pady=5, padx=(0, 5)
            )

            # 使用 GearSetComboBox
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

    def load_set_data(self):
        """加载套装数据"""
        from src.services.calculation_service import calculation_service

        if not hasattr(calculation_service, 'gear_set_manager'):
            print("[GearConfigTab] 警告: gear_set_manager 未初始化")
            return

        # 从计算服务获取套装管理器
        gear_set_manager = calculation_service.gear_set_manager
        if not gear_set_manager:
            print("[GearConfigTab] 警告: gear_set_manager 未加载")
            return

        # 获取所有套装数据
        self.all_sets_data = []
        available_sets = gear_set_manager.get_available_sets()

        for set_info in available_sets:
            self.all_sets_data.append({
                'id': set_info['id'],
                'name': set_info['name'],
                'bonus_display': set_info['bonus_display'],
                'data': set_info
            })

        print(f"[GearConfigTab] 加载了 {len(self.all_sets_data)} 个套装")

        # 更新下拉框列表
        if hasattr(self, 'set_combos'):
            self.update_combo_lists()

    def update_combo_lists(self):
        """更新所有下拉框的选项列表"""
        if not hasattr(self, 'all_sets_data') or not self.all_sets_data:
            print("[GearConfigTab] 警告: 套装数据未加载")
            return

        # 确保 selected_sets 存在
        if not hasattr(self, 'selected_sets') or self.selected_sets is None:
            self.selected_sets = []

        # 过滤有效的已选套装ID（非0值）
        selected_set_ids = [sid for sid in self.selected_sets if sid != 0]

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

    def on_set_selected(self, combo_index: int, old_set_id, new_set_id):
        """套装选择事件"""
        if not hasattr(self, 'set_combos') or combo_index >= len(self.set_combos):
            return

        combo = self.set_combos[combo_index]

        # 处理清空选择的情况
        if new_set_id is None:
            # 更新 selected_sets
            if combo_index < len(self.selected_sets):
                self.selected_sets[combo_index] = 0

            # 更新其他下拉框
            self.update_combo_lists()

            # 更新套装选择和预览
            self.update_gear_set_selection()
            self.update_set_preview()
            return  # 移除自动计算调用

        # 检查是否已经选择了这个套装（在不同位置）
        for i, selected_id in enumerate(self.selected_sets):
            if i != combo_index and selected_id == new_set_id:
                # 恢复到之前的选择
                old_set_id_in_list = self.selected_sets[combo_index] if combo_index < len(self.selected_sets) else 0
                if old_set_id_in_list != 0:
                    combo.set_selected_set_id(old_set_id_in_list)
                else:
                    combo.clear_selection()
                return

        # 确保 selected_sets 列表足够长
        while len(self.selected_sets) <= combo_index:
            self.selected_sets.append(0)

        # 更新选中列表
        self.selected_sets[combo_index] = new_set_id

        # 更新其他下拉框的可用选项
        self.update_combo_lists()

        # 更新套装选择和预览
        self.update_gear_set_selection()
        self.update_set_preview()

    def update_gear_set_selection(self):
        """更新套装选择"""
        from src.models.gear_models import GearSetSelection

        combination_type = self.combination_type_var.get()
        set_ids = []

        # 只添加非0的套装ID
        for set_id in self.selected_sets:
            if set_id != 0:
                set_ids.append(set_id)

        self.main_window.gear_set_selection = GearSetSelection(
            combination_type=combination_type,
            set_ids=set_ids
        )

    def update_set_preview(self):
        """更新套装效果预览"""
        from src.services.calculation_service import calculation_service

        # 从计算服务获取套装管理器
        gear_set_manager = calculation_service.gear_set_manager
        if not gear_set_manager:
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
                effect = gear_set_manager.set_effects.get(set_id)
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

    def on_combination_type_changed(self, event=None):
        """组合类型改变事件"""
        combination_type = self.combination_type_var.get()

        # 重新创建套装选择组件
        self.create_set_selection_widgets(combination_type)

        # 确保数据已加载
        if hasattr(self, 'all_sets_data') and self.all_sets_data:
            self.update_combo_lists()

        # 更新计算
        self.update_gear_set_selection()
        self.update_set_preview()

    def setup_gear_slots(self, parent):
        """设置驱动盘槽位"""
        gears_frame = ttk.LabelFrame(parent, text="驱动盘配置 (6个槽位)", padding="10")
        gears_frame.pack(fill='both', expand=True, pady=(0, 10))

        # 创建3x2网格布局
        for i in range(3):
            gears_frame.columnconfigure(i, weight=1)
        for i in range(2):
            gears_frame.rowconfigure(i, weight=1)

        # 创建槽位小部件
        gear_widgets = []
        for i in range(6):
            gear_widget = GearSlotWidget(gears_frame, i + 1, self.main_window)
            row = i // 3
            col = i % 3
            gear_widget.grid(
                row=row, column=col,
                padx=5, pady=5,
                sticky="nsew"
            )
            gear_widgets.append(gear_widget)

        # 更新管理器中的部件引用
        self.gear_slot_manager.slot_widgets = gear_widgets

    def setup_calculation_button(self, parent):
        """设置计算按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=(10, 0))

        # 计算按钮
        self.calculate_button = ttk.Button(
            button_frame,
            text="计算最终属性",
            command=self.calculate_final_stats,
            style="Accent.TButton"
        )
        self.calculate_button.pack(pady=10)

    def calculate_final_stats(self):
        """计算最终属性"""
        try:
            # 获取当前驱动盘配置
            gear_pieces = self.gear_slot_manager.get_all_gear_pieces()

            # 获取当前角色基础属性
            if not self.main_window.current_base_stats:
                self.main_window.update_status("请先选择角色", "red")
                return

            # 更新状态
            self.main_window.update_status("正在计算最终属性...", "blue")

            # 计算最终属性
            final_stats = self.main_window.calculation_service.calculate_final_stats(
                self.main_window.current_base_stats,
                gear_pieces,
                self.main_window.gear_set_selection,
                self.main_window.main_enhance_level.get()
            )

            if final_stats:
                # 更新显示
                self.main_window.character_panel.update_final_stats_display(final_stats)
                self.main_window.update_status("计算完成", "green")
            else:
                self.main_window.update_status("计算失败", "red")

        except Exception as e:
            self.main_window.update_status(f"计算错误: {str(e)}", "red")
            print(f"[GearConfigTab] 计算错误: {e}")

    def reset_all_gears(self):
        """重置所有驱动盘"""
        if hasattr(self.gear_slot_manager, 'slot_widgets'):
            for gear_widget in self.gear_slot_manager.slot_widgets:
                gear_widget.reset()

        self.main_window.recalculate_final_stats()
        self.main_window.update_status("已重置所有驱动盘", "blue")