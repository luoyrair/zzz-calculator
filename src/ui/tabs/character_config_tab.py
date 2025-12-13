"""角色配置选项卡 - 单一职责"""
import tkinter as tk
from tkinter import ttk

from src.data.manager import data_manager
from src.ui.widget.weapon_combo import WeaponComboBox
from src.ui.widget.weapon_info_display import WeaponInfoDisplay


class CharacterConfigTab(ttk.Frame):
    """角色配置选项卡 - 只负责角色和音擎配置"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        """设置UI布局 - 移除滚动"""
        # 使用简单pack布局，不使用Canvas滚动
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 角色选择区域
        self.setup_character_section(main_frame)

        # 音擎选择区域
        self.setup_weapon_section(main_frame)

        # 等级设置区域
        self.setup_level_settings(main_frame)

    def setup_character_section(self, parent):
        """设置角色选择区域"""
        char_frame = ttk.LabelFrame(parent, text="角色选择", padding="15")
        char_frame.pack(fill='x', pady=(0, 15))

        # 角色选择标签
        ttk.Label(char_frame, text="选择角色:").pack(anchor='w', pady=(0, 5))

        # 角色下拉框
        self.character_var = tk.StringVar()
        character_names = [char.name for char in data_manager.get_all_characters()]
        self.character_combo = ttk.Combobox(
            char_frame,
            textvariable=self.character_var,
            values=character_names,
            state="readonly"
        )
        self.character_combo.pack(fill='x', pady=5)
        self.character_combo.bind('<<ComboboxSelected>>', self.on_character_selected)

        # 角色信息预览
        self.char_info_label = ttk.Label(
            char_frame,
            text="请选择角色",
            foreground="blue",
            wraplength=400
        )
        self.char_info_label.pack(fill='x', pady=(10, 0))

    def setup_weapon_section(self, parent):
        """设置音擎选择区域"""
        weapon_frame = ttk.LabelFrame(parent, text="音擎选择", padding="15")
        weapon_frame.pack(fill='x', pady=(0, 15))

        # 音擎选择标签
        ttk.Label(weapon_frame, text="选择音擎:").pack(anchor='w', pady=(0, 5))

        # 音擎下拉框
        self.weapon_combo = WeaponComboBox(
            weapon_frame,
            width=30,
            on_selected_callback=self.on_weapon_selected
        )
        self.weapon_combo.pack(fill='x', pady=5)

        # 音擎等级
        level_frame = ttk.Frame(weapon_frame)
        level_frame.pack(fill='x', pady=10)

        ttk.Label(level_frame, text="音擎等级:").pack(side='left', padx=(0, 10))

        self.weapon_level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.main_window.weapon_level,
            values=list(range(1, 61)),
            state="readonly",
            width=10
        )
        self.weapon_level_combo.pack(side='left')
        self.weapon_level_combo.bind('<<ComboboxSelected>>', self.on_weapon_level_changed)

        # 音擎信息显示
        self.weapon_info_display = WeaponInfoDisplay(weapon_frame)
        self.weapon_info_display.pack(fill='x', pady=(15, 0))

    def setup_level_settings(self, parent):
        """设置等级配置区域"""
        level_frame = ttk.LabelFrame(parent, text="等级配置", padding="15")
        level_frame.pack(fill='x')

        # 使用网格布局
        ttk.Label(level_frame, text="角色等级:").grid(row=0, column=0, sticky='w', pady=5)
        self.character_level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.main_window.character_level,
            values=list(range(1, 61)),
            state="readonly",
            width=10
        )
        self.character_level_combo.grid(row=0, column=1, padx=(5, 20), pady=5, sticky='w')
        self.character_level_combo.bind('<<ComboboxSelected>>', self.on_character_level_changed)

        # 额外等级（核心被动等级）
        ttk.Label(level_frame, text="核心被动等级:").grid(row=0, column=2, sticky='w', pady=5)
        self.extra_level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.main_window.extra_level,
            values=list(range(1, 8)),
            state="readonly",
            width=10
        )
        self.extra_level_combo.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.extra_level_combo.bind('<<ComboboxSelected>>', self.on_extra_level_changed)

    def on_character_selected(self, event):
        """角色选择事件"""
        character_name = self.character_var.get()
        if not character_name:
            return

        character = data_manager.get_character_by_name(character_name)
        if character:
            # 更新角色信息预览
            self.char_info_label.config(
                text=f"{character.name} | {character.weapon_type} | {character.element_type}"
            )

            # 调用主窗口加载角色
            self.main_window.load_character(character.id)

    def on_weapon_selected(self, combo, old_id, new_id):
        """音擎选择事件"""
        if new_id:
            # 获取音擎等级
            weapon_level = self.main_window.weapon_level.get()

            # 更新音擎信息显示
            self.weapon_info_display.load_weapon(new_id, weapon_level)

            # 调用主窗口加载音擎
            self.main_window.load_weapon(new_id)

            # 更新状态
            weapon_data = self.weapon_combo.get_selected_weapon_data()
            if weapon_data:
                self.main_window.update_status(f"已选择音擎: {weapon_data['name']}", "green")

    def on_weapon_level_changed(self, event):
        """音擎等级改变事件"""
        selected_id = self.weapon_combo.get_selected_weapon_id()
        if selected_id:
            # 更新音擎信息显示
            weapon_level = self.main_window.weapon_level.get()
            self.weapon_info_display.load_weapon(selected_id, weapon_level)

            # 重新计算
            self.main_window.load_weapon(selected_id)

            self.main_window.update_status(f"音擎等级已更新: {weapon_level}", "blue")

    def on_character_level_changed(self, event):
        """角色等级改变事件"""
        new_level = self.main_window.character_level.get()

        # 重新加载当前角色
        if self.main_window.current_character_id:
            self.main_window.load_character(self.main_window.current_character_id)

        self.main_window.update_status(f"角色等级已更新: {new_level}", "blue")

    def on_extra_level_changed(self, event):
        """额外等级改变事件"""
        new_level = self.main_window.extra_level.get()

        # 重新加载当前角色
        if self.main_window.current_character_id:
            self.main_window.load_character(self.main_window.current_character_id)

        self.main_window.update_status(f"核心被动等级已更新: {new_level}", "blue")

    def initialize(self):
        """初始化选项卡"""
        # 尝试加载第一个角色
        characters = data_manager.get_all_characters()
        if characters:
            self.character_var.set(characters[0].name)
            self.on_character_selected(None)

        # 尝试加载第一个音擎
        weapons = data_manager.get_all_weapons()
        if weapons:
            self.weapon_combo.set_selected_weapon_id(weapons[0].id)
            self.weapon_info_display.load_weapon(weapons[0].id, self.main_window.weapon_level.get())