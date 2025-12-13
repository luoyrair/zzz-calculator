"""主窗口 - 协调各个组件"""
import tkinter as tk
from tkinter import ttk
from typing import Optional

from src.services.calculation_service import calculation_service
from src.models.character_attributes import CharacterAttributesModel
from src.models.gear_models import GearSetSelection
from .character_panel import CharacterPanel
from .tabs.character_config_tab import CharacterConfigTab
from .tabs.gear_config_tab import GearConfigTab
from ..services.gear_export_service import GearExportService


class MainWindow:
    """主窗口 - 只负责协调和集成"""

    def __init__(self, root):
        self.root = root
        self.root.title("绝区零驱动盘属性计算器")
        self.root.geometry("1400x900")

        self.calculation_service = calculation_service
        self.export_service = GearExportService(self)

        # 当前状态
        self.current_character_id: int = 0
        self.current_weapon_id: int = 0
        self.current_base_stats: Optional[CharacterAttributesModel] = None

        # UI变量
        self.character_level = tk.IntVar(value=60)
        self.weapon_level = tk.IntVar(value=60)
        self.extra_level = tk.IntVar(value=7)
        self.main_enhance_level = tk.IntVar(value=15)

        # 驱动盘数据
        self.gear_set_selection = GearSetSelection("4+2", [])

        # 设置UI
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局"""
        self._setup_keyboard_shortcuts()
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)

        # 使用简单的左右框架布局，不使用PanedWindow
        # 左侧框架 - 固定宽度
        left_frame = ttk.Frame(main_frame, width=380)
        left_frame.pack(side='left', fill='y')
        left_frame.pack_propagate(False)  # 禁止自动调整大小

        # 创建CharacterPanel
        self.character_panel = CharacterPanel(left_frame, self)
        self.character_panel.pack(fill='both', expand=True, padx=5, pady=5)

        # 右侧框架 - 占据剩余空间
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)

        # 设置右侧面板
        self.setup_right_panel(right_frame)

        # 状态栏
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side='bottom', fill='x')
        self.status_label = ttk.Label(
            self.status_bar,
            text="就绪",
            relief="sunken",
            anchor="w"
        )
        self.status_label.pack(fill='x', padx=5, pady=2)

    def setup_right_panel(self, container):
        """设置右侧面板"""
        # 创建选项卡
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # 基础配置选项卡
        self.character_tab = CharacterConfigTab(self.notebook, self)
        self.notebook.add(self.character_tab, text="基础配置")

        # 驱动盘配置选项卡
        self.gear_tab = GearConfigTab(self.notebook, self)
        self.notebook.add(self.gear_tab, text="驱动盘配置")

    def load_character(self, character_id: int):
        """加载指定角色"""
        from src.data.manager import data_manager

        character = data_manager.get_character(character_id)
        if not character:
            self.update_status(f"角色 {character_id} 不存在", "red")
            return

        self.current_character_id = character_id

        # 计算角色基础属性
        level = self.character_level.get()
        breakthrough = calculation_service.get_breakthrough_level(level)

        base_stats = calculation_service.calculate_character_base_stats(
            character_id, level, breakthrough, self.extra_level.get()
        )

        if not base_stats:
            self.update_status("计算角色属性失败", "red")
            return

        self.current_base_stats = base_stats

        # 更新UI
        self.character_panel.update_with_character_data(base_stats)

        self.update_status(f"已加载角色: {character.name}", "green")

    def load_weapon(self, weapon_id: int):
        """加载音擎"""
        if not self.current_base_stats:
            return

        from src.data.manager import data_manager
        weapon = data_manager.get_weapon(weapon_id)
        if not weapon:
            return

        self.current_weapon_id = weapon_id

        # 应用音擎属性
        weapon_level = self.weapon_level.get()

        final_stats = calculation_service.calculate_character_with_weapon(
            self.current_character_id,
            self.character_level.get(),
            calculation_service.get_breakthrough_level(self.character_level.get()),
            self.extra_level.get(),
            weapon_id,
            weapon_level
        )

        if final_stats:
            self.current_base_stats = final_stats
            self.character_panel.update_with_character_data(final_stats)
            # self.recalculate_final_stats()

            self.update_status(f"已应用音擎: {weapon.name}", "green")

    def recalculate_final_stats(self):
        """重新计算最终属性"""
        if not self.current_base_stats:
            return

        # 获取当前驱动盘配置
        gear_pieces = self.get_current_gear_pieces()

        # 计算最终属性
        final_stats = calculation_service.calculate_final_stats(
            self.current_base_stats,
            gear_pieces,
            self.gear_set_selection,
            self.main_enhance_level.get()
        )

        if final_stats:
            self.character_panel.update_final_stats_display(final_stats)

    def get_current_gear_pieces(self):
        """获取当前驱动盘配置"""
        if hasattr(self, 'gear_tab') and hasattr(self.gear_tab, 'gear_slot_manager'):
            return self.gear_tab.gear_slot_manager.get_all_gear_pieces()
        return []

    def update_status(self, message: str, color: str = "black"):
        """更新状态信息"""
        self.status_label.config(text=message, foreground=color)

    def _setup_keyboard_shortcuts(self):
        """设置键盘快捷键"""
        # 导出导入快捷键
        self.root.bind('<Control-s>', lambda e: self.export_service.export_to_file())
        self.root.bind('<Control-o>', lambda e: self.export_service.import_from_file())
        self.root.bind('<Control-c>', lambda e: self.export_service.copy_as_json())
        self.root.bind('<Control-v>', lambda e: self.export_service.paste_from_clipboard())
        self.root.bind('<Control-p>', lambda e: self.export_service.preset_manager.save_as_preset())
        self.root.bind('<Control-m>', lambda e: self.export_service.preset_manager.show_preset_manager())

        # 计算快捷键
        self.root.bind('<F5>', lambda e: self.recalculate_final_stats())