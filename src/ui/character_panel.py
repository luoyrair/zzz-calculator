# src/ui/character_panel.py
"""重构后的角色面板 - 完全适配新架构"""
from tkinter import ttk
from typing import Dict, Optional

from src import data_manager, calculation_service
from src.models.character_attributes import CharacterAttributes


class CharacterPanel(ttk.Frame):
    """角色面板 - 新架构实现"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window

        # 使用新的服务
        self.character_calculator = calculation_service.character_calculator
        self.gear_calculator = calculation_service.gear_calculator

        # 当前数据
        self.current_base_stats: Optional[CharacterAttributes] = None  # 修复类型注解
        self.current_final_stats = None
        self.base_stat_labels: Dict[str, ttk.Label] = {}
        self.final_stat_labels: Dict[str, ttk.Label] = {}

        # 配置固定高度
        self.base_stats_frame_height = 300  # 基础属性区域固定高度
        self.final_stats_frame_height = 300  # 最终属性区域固定高度

        self.setup_ui()

    def setup_ui(self):
        """设置UI组件"""
        # 角色信息区域
        self.setup_character_info()

        # 基础属性区域 - 固定高度，不滚动
        self.setup_base_stats()

        # 最终属性区域 - 固定高度，不滚动
        self.setup_final_stats()

    def setup_character_info(self):
        """设置角色信息区域"""
        info_frame = ttk.LabelFrame(self, text="当前角色", padding="10")
        info_frame.pack(fill='x', pady=(0, 10))

        # 角色名称
        self.character_name_label = ttk.Label(
            info_frame,
            text="未选择角色",
            font=("", 12, "bold"),
            foreground="blue"
        )
        self.character_name_label.pack(anchor='w', pady=(0, 5))

        # 详细信息框架
        detail_frame = ttk.Frame(info_frame)
        detail_frame.pack(fill='x', pady=5)

        # 稀有度
        self.rarity_label = ttk.Label(detail_frame, text="", foreground="purple")
        self.rarity_label.pack(side='left', padx=(0, 15))

        # 武器类型
        self.weapon_label = ttk.Label(detail_frame, text="", foreground="brown")
        self.weapon_label.pack(side='left', padx=(0, 15))

        # 元素类型
        self.element_label = ttk.Label(detail_frame, text="", foreground="green")
        self.element_label.pack(side='left')

    def setup_base_stats(self):
        """设置基础属性区域 - 固定高度，不滚动"""
        base_frame = ttk.LabelFrame(self, text="基础属性（角色自身）", padding="10")
        base_frame.pack(fill='x', pady=(0, 10))

        # 固定高度的容器框架
        self.base_container = ttk.Frame(base_frame)
        self.base_container.pack(fill='both', expand=True)

        # 设置固定高度
        self.base_container.configure(height=self.base_stats_frame_height)

        # 初始提示
        self.base_placeholder = ttk.Label(
            self.base_container,
            text="请选择角色以查看属性",
            foreground="gray"
        )
        self.base_placeholder.place(relx=0.5, rely=0.5, anchor='center')

    def setup_final_stats(self):
        """设置最终属性区域 - 固定高度，不滚动"""
        final_frame = ttk.LabelFrame(self, text="最终属性（含驱动盘加成）", padding="10")
        final_frame.pack(fill='both', expand=True)

        # 固定高度的容器框架
        self.final_container = ttk.Frame(final_frame)
        self.final_container.pack(fill='both', expand=True)

        # 设置固定高度
        self.final_container.configure(height=self.final_stats_frame_height)

        # 初始提示
        self.final_placeholder = ttk.Label(
            self.final_container,
            text="请配置驱动盘以查看最终属性",
            foreground="gray"
        )
        self.final_placeholder.place(relx=0.5, rely=0.5, anchor='center')

    def _calculate_breakthrough_level(self, level: int) -> int:
        """根据等级计算突破阶段"""
        if level <= 10:
            return 1
        elif level <= 20:
            return 2
        elif level <= 30:
            return 3
        elif level <= 40:
            return 4
        elif level <= 50:
            return 5
        else:
            return 6

    def update_with_character_data(self, base_stats):
        """更新角色数据"""
        # 存储基础数据
        self.current_base_stats = base_stats
        self.main_window.current_base_stats = base_stats

        # 更新角色信息显示
        self._update_character_info(base_stats)

        # 更新基础属性显示
        self._update_base_stats_display(base_stats)

        # 触发计算更新
        self.main_window.recalculate_final_stats()

    def _update_character_info(self, display_info):
        """更新角色信息显示 - 适配新数据格式"""
        character = data_manager.get_character(display_info.character_id)
        self.character_name_label.config(text=character.name)

        # 稀有度
        rarity = display_info.rarity
        from src.config.manager import config_manager
        rarity_color = config_manager.display_config.get_rarity_color(rarity)
        self.rarity_label.config(text=f"{rarity + 1}星", foreground=rarity_color)

        # 武器和元素
        self.weapon_label.config(text=f"特性: {display_info.weapon_type}")
        self.element_label.config(text=f"元素: {display_info.element_type}")

    def _update_base_stats_display(self, base_stats: CharacterAttributes):
        """更新基础属性显示 - 固定高度网格布局"""
        # 移除初始提示
        if self.base_placeholder:
            self.base_placeholder.destroy()
            self.base_placeholder = None

        # 清空现有标签
        for widget in self.base_container.winfo_children():
            widget.destroy()

        self.base_stat_labels.clear()

        if not base_stats:
            return

        # 定义显示顺序 - 使用 CharacterAttributes 的实际属性名
        display_order = [
            "hp", "attack", "defence", "impact",
            "crit_rate", "crit_dmg",
            "anomaly_mastery", "anomaly_proficiency",
            "pen_ratio", "energy_regen"
        ]

        # 属性显示名称映射
        display_names = {
            "hp": "生命值",
            "attack": "攻击力",
            "defence": "防御力",
            "impact": "冲击力",
            "crit_rate": "暴击率",
            "crit_dmg": "暴击伤害",
            "anomaly_mastery": "异常掌控",
            "anomaly_proficiency": "异常精通",
            "pen_ratio": "穿透率",
            "energy_regen": "能量自动回复"
        }

        # 确定列数（每行显示1个属性）
        columns = 1
        total_attrs = len(display_order)
        rows = (total_attrs + columns - 1) // columns  # 计算需要的行数

        # 配置网格权重
        for i in range(columns):
            self.base_container.columnconfigure(i, weight=1)
        for i in range(rows):
            self.base_container.rowconfigure(i, weight=1)

        # 创建属性网格
        for index, attr_key in enumerate(display_order):
            if not hasattr(base_stats, attr_key):
                continue

            value = getattr(base_stats, attr_key, 0)
            display_name = display_names.get(attr_key, attr_key)
            formatted_value = self._format_attribute_value(attr_key, value)

            # 计算行列位置
            row = index // columns
            col = index % columns

            # 创建属性框架
            attr_frame = ttk.Frame(self.base_container, padding="5")
            attr_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=2)

            # 属性名称和值并排显示
            name_label = ttk.Label(
                attr_frame,
                text=f"{display_name}:",
                font=("", 10),
                anchor='w'
            )
            name_label.pack(side='left', fill='x', expand=True)

            # 属性值（蓝色）
            value_label = ttk.Label(
                attr_frame,
                text=formatted_value,
                font=("", 10, "bold"),
                foreground="blue",
                anchor='e'
            )
            value_label.pack(side='right', fill='x')

            self.base_stat_labels[attr_key] = value_label

    def update_final_stats_display(self, final_stats):
        """更新最终属性显示（含装备加成）"""
        print(f"[CharacterPanel] 开始更新最终属性显示")
        print(f"[CharacterPanel] 收到最终属性类型: {type(final_stats)}")

        self.current_final_stats = final_stats

        # 移除初始提示
        if self.final_placeholder:
            self.final_placeholder.destroy()
            self.final_placeholder = None

        # 清空现有标签
        for widget in self.final_container.winfo_children():
            widget.destroy()

        self.final_stat_labels.clear()

        if not final_stats:
            ttk.Label(
                self.final_container,
                text="请配置驱动盘以查看最终属性",
                foreground="gray"
            ).place(relx=0.5, rely=0.5, anchor='center')
            return

        # 定义显示顺序
        display_order = [
            "hp", "attack", "defence", "impact",
            "crit_rate", "crit_dmg",
            "anomaly_mastery", "anomaly_proficiency",
            "pen_ratio", "energy_regen"
        ]

        # 属性显示名称映射
        display_names = {
            "hp": "生命值",
            "attack": "攻击力",
            "defence": "防御力",
            "impact": "冲击力",
            "crit_rate": "暴击率",
            "crit_dmg": "暴击伤害",
            "anomaly_mastery": "异常掌控",
            "anomaly_proficiency": "异常精通",
            "pen_ratio": "穿透率",
            "energy_regen": "能量自动回复"
        }

        # 确定列数（每行显示2个属性）
        columns = 1
        total_attrs = len(display_order)
        rows = (total_attrs + columns - 1) // columns

        # 配置网格权重
        for i in range(columns):
            self.final_container.columnconfigure(i, weight=1)
        for i in range(rows):
            self.final_container.rowconfigure(i, weight=1)

        # 创建属性网格
        for index, attr_key in enumerate(display_order):
            # 获取属性值 - 处理不同类型
            value = None
            if isinstance(final_stats, dict):
                value = final_stats.get(attr_key, 0)
            elif hasattr(final_stats, attr_key):
                value = getattr(final_stats, attr_key, 0)
            elif hasattr(final_stats, '__dict__'):
                value = final_stats.__dict__.get(attr_key, 0)

            if value is None:
                value = 0

            display_name = display_names.get(attr_key, attr_key)
            formatted_value = self._format_attribute_value(attr_key, value)

            # 计算行列位置
            row = index // columns
            col = index % columns

            # 创建属性框架
            attr_frame = ttk.Frame(self.final_container, padding="5")
            attr_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=2)

            # 属性名称和值并排显示
            name_label = ttk.Label(
                attr_frame,
                text=f"{display_name}:",
                font=("", 10),
                anchor='w'
            )
            name_label.pack(side='left', fill='x', expand=True)

            # 属性值（绿色）
            value_label = ttk.Label(
                attr_frame,
                text=formatted_value,
                font=("", 10, "bold"),
                foreground="green",
                anchor='e'
            )
            value_label.pack(side='right', fill='x')

            self.final_stat_labels[attr_key] = value_label

        print(f"[CharacterPanel] 最终属性显示更新完成")

    def _format_attribute_value(self, attr_key: str, value: float) -> str:
        """格式化属性值显示"""
        # 确保值是数字类型
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return str(value)

        if attr_key in ["crit_rate", "crit_dmg", "pen_ratio"]:
            # 百分比显示，转为百分比形式
            return f"{value * 100:.1f}%"
        elif attr_key == "energy_regen":
            # 能量回复，保留1位小数
            return f"{value}"
        else:
            # 其他数值类型，向下取整
            try:
                return f"{int(value)}"
            except (ValueError, TypeError):
                return str(value)

    def show_error(self, message: str):
        """显示错误信息"""
        self.character_name_label.config(text="错误", foreground="red")

        # 清空其他信息
        self.rarity_label.config(text="")
        self.weapon_label.config(text="")
        self.element_label.config(text="")

        # 清空属性显示
        for widget in self.base_container.winfo_children():
            widget.destroy()
        for widget in self.final_container.winfo_children():
            widget.destroy()

        # 在基础属性区域显示错误信息
        ttk.Label(
            self.base_container,
            text=f"错误: {message}",
            foreground="red"
        ).place(relx=0.5, rely=0.5, anchor='center')

        # 在最终属性区域显示错误信息
        ttk.Label(
            self.final_container,
            text=f"错误: {message}",
            foreground="red"
        ).place(relx=0.5, rely=0.5, anchor='center')