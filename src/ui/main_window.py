# src/ui/main_window.py
"""重构后的主窗口 - 优化布局和交互"""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional

from src.core.service_factory import get_service_factory
from src.core.character_models import BaseCharacterStats
from src.core.gear_models import GearPiece, GearSetSelection
from src.services.character_service import CharacterService
from src.ui.character_panel import CharacterPanel
from src.ui.gear_slot import GearSlotWidget, GearSlotManager


class MainWindow:
    """主窗口 - 优化版本"""

    def __init__(self, root):
        self.root = root
        self.root.title("绝区零驱动盘属性计算器 - 新架构")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # 初始化服务
        self.service_factory = get_service_factory()

        # 使用新的服务
        self.character_service: Optional[CharacterService] = None
        self.character_manager = self.service_factory.character_manager
        self.gear_calculator = self.service_factory.gear_calculator

        # 当前状态
        self.current_base_stats: Optional[BaseCharacterStats] = None
        self.gear_pieces: List[GearPiece] = [GearPiece(i) for i in range(6)]
        self.gear_set_selection = GearSetSelection("4+2", [1, 2])
        self.gear_widgets = []

        # UI变量
        self.character_level = tk.IntVar(value=60)
        self.extra_level = tk.IntVar(value=7)
        self.main_enhance_level = tk.IntVar(value=15)

        # 槽位管理器
        self.gear_slot_manager = GearSlotManager(self)

        self.setup_ui()
        self.initialize_application()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)

        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # 左侧角色面板
        self.setup_left_panel(main_frame)

        # 右侧配置面板
        self.setup_right_panel(main_frame)

    def setup_left_panel(self, parent):
        """设置左侧角色面板"""
        left_frame = ttk.Frame(parent)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # 角色面板
        self.character_panel = CharacterPanel(left_frame, self)
        self.character_panel.pack(fill='both', expand=True)

    def setup_right_panel(self, parent):
        """设置右侧配置面板"""
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # 创建选项卡
        notebook = ttk.Notebook(right_frame)
        notebook.grid(row=0, column=0, sticky="nsew")
        right_frame.rowconfigure(0, weight=1)

        # 角色配置选项卡
        self.character_tab = CharacterConfigTab(notebook, self)
        notebook.add(self.character_tab, text="角色配置")

        # 驱动盘配置选项卡
        gear_tab = GearConfigTab(notebook, self)
        notebook.add(gear_tab, text="驱动盘配置")

        # 状态栏
        self.setup_status_bar(right_frame)

    def setup_status_bar(self, parent):
        """设置状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=1, column=0, sticky="we", pady=(5, 0))

        self.status_label = ttk.Label(
            status_frame,
            text="就绪",
            relief="sunken",
            anchor="w"
        )
        self.status_label.pack(fill='x', padx=5, pady=2)

    def initialize_application(self):
        """初始化应用程序 - 适配新服务"""
        try:
            # 初始化配置
            from src.config import config_manager
            if not config_manager.initialize():
                self.show_status("配置初始化失败", "red")
                return

            # 初始化服务
            self.character_service = self.service_factory.character_service

            self.show_status("配置加载成功", "green")

            # 预加载第一个角色
            self.load_first_character()

        except Exception as e:
            self.show_status(f"初始化失败: {str(e)}", "red")
            import traceback
            traceback.print_exc()

    def load_first_character(self):
        """加载第一个可用角色 - 适配新服务"""
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

    def update_calculation(self):
        """更新计算 - 适配新服务"""
        try:
            if not self.current_base_stats:
                self.show_status("请先选择角色", "orange")
                return

            # 【新增调试点1】：检查驱动盘数据
            gear_pieces = self.get_all_gear_pieces()
            print(f"[DEBUG] 获取到 {len(gear_pieces)} 个驱动盘配置:")
            for i, piece in enumerate(gear_pieces):
                print(
                    f"  槽位{i}: 主属性={piece.main_gear_key}, 值={piece.main_value}, 副属性数={len(piece.sub_attributes)}")

            if not self.gear_calculator:
                print(f"[ERROR] gear_calculator 不存在！")
                self.show_status("计算器未初始化", "red")
                return

            print(f"[DEBUG] 准备调用 gear_calculator.calculate_complete_stats")  # 新增调试
            print(f"[DEBUG] gear_calculator 类型: {type(self.gear_calculator)}")  # 新增调试

            # 计算最终属性
            if self.character_panel.current_base_stats:
                # 【新增调试点2】：检查计算器输入
                print(f"[DEBUG] 传入基础属性 ATK: {self.character_panel.current_base_stats.ATK}")
                print(f"[DEBUG] 传入套装选择: {self.gear_set_selection}")

                final_stats = self.gear_calculator.calculate_complete_stats(
                    self.character_panel.current_base_stats,
                    gear_pieces,
                    self.gear_set_selection
                )

                # 【新增调试点3】：检查计算结果
                print(f"[DEBUG] 计算完成。最终属性 ATK: {final_stats.ATK}")
                print(f"[DEBUG] 装备加成 ATK: {getattr(final_stats.gear_bonuses, 'ATK', 0)}")

                # 更新显示
                self.character_panel.update_final_stats_display(final_stats)
                self.show_status("计算完成", "green")
        except Exception as e:
            error_msg = f"计算错误: {str(e)}"
            self.show_status(error_msg, "red")
            self.character_panel.show_error(error_msg)
            import traceback
            traceback.print_exc()

    def get_all_gear_pieces(self) -> List[GearPiece]:
        """获取所有驱动盘配置 - 保持不变"""
        if hasattr(self, 'gear_widgets'):
            return [widget.get_gear_piece() for widget in self.gear_widgets]
        return self.gear_pieces

    def set_current_base_stats(self, base_stats: BaseCharacterStats):
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
    """角色配置选项卡 - 优化版本"""

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
        """角色选择事件 - 适配新服务"""
        character_name = self.character_var.get()
        if character_name:
            character_id = self.main_window.character_manager.get_character_id_by_name(character_name)
            if character_id:
                self.current_character_id = character_id

                # 使用角色面板加载角色
                self.main_window.character_panel.load_character_by_name(character_name)
                self.main_window.show_status(f"已选择: {character_name}", "green")

    def _set_character_data(self, character_id: str):
        """设置角色数据到主窗口"""
        try:
            level = self.main_window.character_level.get()
            extra_level = self.main_window.extra_level.get()

            detailed_stats = self.main_window.character_calculator.get_character_detailed_stats(
                character_id, level, extra_level
            )

            if detailed_stats and "base_stats" in detailed_stats:
                self.main_window.current_base_stats = detailed_stats["base_stats"]
                self.main_window.current_character_data = detailed_stats

        except Exception as e:
            self.main_window.show_status(f"设置角色数据失败: {e}", "red")

    def on_config_changed(self, event):
        """配置改变事件 - 适配新服务"""
        if not self.current_character_id:
            return

        character_name = self.character_var.get()
        if character_name:
            # 重新加载角色以应用新的等级配置
            self.main_window.character_panel.load_character_by_name(character_name)
            self.main_window.show_status("配置已更新", "blue")


class GearConfigTab(ttk.Frame):
    """驱动盘配置选项卡 - 优化版本"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 增强等级设置
        self.setup_enhancement_settings(main_frame)

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