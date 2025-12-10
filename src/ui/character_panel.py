# src/ui/character_panel.py
"""重构后的角色面板 - 完全适配新架构"""
from tkinter import ttk
from typing import Dict, Any, Optional

from src import get_service_factory
from src.core.models.character import FinalCharacterStats
from src.services.character import CharacterService


class CharacterPanel(ttk.Frame):
    """角色面板 - 新架构实现"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.service_factory = get_service_factory()

        # 使用新的服务
        self.character_service: Optional[CharacterService] = None
        self.character_manager = self.service_factory.character_manager

        # 当前数据
        self.current_base_stats = None
        self.current_final_stats = None
        self.base_stat_labels: Dict[str, ttk.Label] = {}
        self.final_stat_labels: Dict[str, ttk.Label] = {}

        # 配置固定高度
        self.base_stats_frame_height = 300  # 基础属性区域固定高度
        self.final_stats_frame_height = 350  # 最终属性区域固定高度

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

    def load_character_by_name(self, character_name: str):
        """通过角色名称加载角色 - 适配新服务"""
        try:
            # 获取角色ID
            character_id = self.character_manager.get_character_id_by_name(character_name)
            if not character_id:
                self.show_error(f"未找到角色: {character_name}")
                return

            # 获取服务实例
            self.character_service = self.service_factory.character_service

            # 使用新服务加载角色
            if not self.character_service.load_character_by_id(character_id):
                self.show_error(f"加载角色数据失败: {character_name}")
                return

            # 获取角色构建器
            builder = self.character_service.get_character_builder(character_id)
            if not builder:
                self.show_error(f"获取角色构建器失败: {character_name}")
                return

            # 获取等级配置
            level = self.main_window.character_level.get()
            extra_level = self.main_window.extra_level.get()

            # 计算突破阶段 (根据等级确定)
            breakthrough_level = self._calculate_breakthrough_level(level)

            # 使用构建器计算属性
            base_stats = builder.build_base_stats(
                level, breakthrough_level, extra_level
            )

            if not base_stats:
                self.show_error("计算角色属性失败")
                return

            # 更新UI
            self._update_with_character_data(character_id, base_stats, builder)

        except Exception as e:
            error_msg = f"加载角色失败: {str(e)}"
            self.show_error(error_msg)
            import traceback
            traceback.print_exc()

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

    def _update_with_character_data(self, character_id: str, base_stats, builder):
        """使用新服务的数据更新UI"""
        # 获取角色显示信息
        display_info = builder.get_display_info()

        # 存储基础数据
        self.current_base_stats = base_stats
        self.main_window.set_current_base_stats(base_stats)

        # 更新角色信息显示
        self._update_character_info(display_info)

        # 更新基础属性显示
        self._update_base_stats_display(base_stats)

        # 触发计算更新
        self.main_window.update_calculation()

    def _update_character_info(self, display_info: Dict[str, Any]):
        """更新角色信息显示 - 适配新数据格式"""
        self.character_name_label.config(text=display_info.get("name", "未知角色"))

        # 稀有度
        rarity = display_info.get("rarity", 4)
        from src import config_manager
        rarity_color = config_manager.character.display_config.get_rarity_color(rarity)
        star_text = "★" * (rarity + 1)
        self.rarity_label.config(text=f"{star_text}", foreground=rarity_color)

        # 武器和元素
        self.weapon_label.config(text=f"特性: {display_info.get('weapon_type', '未知')}")
        self.element_label.config(text=f"元素: {display_info.get('element_type', '未知')}")

    def _update_base_stats_display(self, base_stats):
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

        # 获取显示顺序配置
        from src import config_manager
        output_config = config_manager.character.attribute_output_config

        # 使用新服务获取武器类型
        if self.character_service:
            display_info = self.character_service.get_character_display_info()
            weapon_type = display_info.get("weapon_type", "")
        else:
            weapon_type = ""

        # 获取输出顺序
        display_order = output_config.get_output_order(weapon_type)

        # 确定列数（每行显示2个属性）
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
            display_name = output_config.get_display_name(attr_key)
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

    def update_final_stats_display(self, final_stats: FinalCharacterStats):
        """更新最终属性显示（含装备加成） - 固定高度网格布局"""
        print(f"[CharacterPanel] 开始更新最终属性显示")
        print(f"[CharacterPanel] 收到最终属性: {type(final_stats)}")

        self.current_final_stats = final_stats

        # 移除初始提示
        if self.final_placeholder:
            print(f"[CharacterPanel] 移除初始提示")
            self.final_placeholder.destroy()
            self.final_placeholder = None

        # 清空现有标签
        print(f"[CharacterPanel] 清空现有标签")
        for widget in self.final_container.winfo_children():
            widget.destroy()

        self.final_stat_labels.clear()

        if not final_stats:
            print(f"[CharacterPanel] 最终属性为空，显示提示")
            ttk.Label(
                self.final_container,
                text="请配置驱动盘以查看最终属性",
                foreground="gray"
            ).place(relx=0.5, rely=0.5, anchor='center')
            return

        # 获取属性显示顺序
        from src import config_manager
        output_config = config_manager.character.attribute_output_config

        # 使用基础属性来确定显示顺序
        if self.current_base_stats:
            weapon_type = "命破" if hasattr(self.current_base_stats,
                                            'Sheer_Force') and self.current_base_stats.Sheer_Force > 0 else "其他"
            display_order = output_config.get_output_order(weapon_type)
        else:
            display_order = output_config.DEFAULT_OUTPUT_ORDER

        # 确定列数（每行显示2个属性）
        columns = 1
        total_attrs = len(display_order)
        rows = (total_attrs + columns - 1) // columns  # 计算需要的行数

        # 配置网格权重
        for i in range(columns):
            self.final_container.columnconfigure(i, weight=1)
        for i in range(rows):
            self.final_container.rowconfigure(i, weight=1)

        # 创建属性网格
        print(f"[CharacterPanel] 创建属性网格，共{total_attrs}个属性")
        for index, attr_key in enumerate(display_order):
            if not hasattr(final_stats, attr_key):
                print(f"[CharacterPanel] 警告: 最终属性没有 {attr_key} 字段")
                continue

            value = getattr(final_stats, attr_key, 0)
            display_name = output_config.get_display_name(attr_key)
            formatted_value = self._format_attribute_value(attr_key, value)

            # 计算行列位置
            row = index // columns
            col = index % columns

            print(f"[CharacterPanel]  属性 {display_name}: 值={value}, 格式={formatted_value}, 位置=({row},{col})")

            # 创建属性框架
            attr_frame = ttk.Frame(self.final_container, padding="5")
            attr_frame.grid(row=row, column=col, sticky="nsew")

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
        if attr_key in ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio"]:
            return f"{value:.1%}"
        elif attr_key in ["HP", "ATK", "DEF", "Impact",
                          "Anomaly_Mastery", "Anomaly_Proficiency", "Sheer_Force"]:
            return f"{value:,.0f}"
        elif attr_key in ["Energy_Regen", "Automatic_Adrenaline_Accumulation"]:
            return f"{value:.1f}"
        else:
            return f"{value:.2f}"

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