# src/ui/character_panel.py
"""重构后的角色面板 - 完全适配新架构"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

from src.core.character_models import FinalCharacterStats
from src.core.service_factory import get_service_factory
from src.services.character_service import CharacterService


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

        self.setup_ui()

    def setup_ui(self):
        """设置UI组件"""
        # 角色信息区域
        self.setup_character_info()

        # 基础属性区域
        self.setup_base_stats()

        # 最终属性区域（含装备加成）
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
        """设置基础属性区域"""
        base_frame = ttk.LabelFrame(self, text="基础属性（角色自身）", padding="10")
        base_frame.pack(fill='x', pady=(0, 10))

        # 创建滚动框架
        canvas = tk.Canvas(base_frame, height=300)
        scrollbar = ttk.Scrollbar(base_frame, orient="vertical", command=canvas.yview)
        self.scrollable_base_frame = ttk.Frame(canvas)

        self.scrollable_base_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_base_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 初始提示
        self.base_placeholder = ttk.Label(
            self.scrollable_base_frame,
            text="请选择角色以查看属性",
            foreground="gray"
        )
        self.base_placeholder.pack(pady=20)

    def setup_final_stats(self):
        """设置最终属性区域（含装备加成）"""
        final_frame = ttk.LabelFrame(self, text="最终属性（含驱动盘加成）", padding="10")
        final_frame.pack(fill='both', expand=True)

        # 创建滚动框架
        canvas = tk.Canvas(final_frame, height=300)
        scrollbar = ttk.Scrollbar(final_frame, orient="vertical", command=canvas.yview)
        self.scrollable_final_frame = ttk.Frame(canvas)

        self.scrollable_final_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_final_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 初始提示
        self.final_placeholder = ttk.Label(
            self.scrollable_final_frame,
            text="请配置驱动盘以查看最终属性",
            foreground="gray"
        )
        self.final_placeholder.pack(pady=30)

    def load_character_by_name(self, character_name: str):
        """通过角色名称加载角色 - 适配新服务"""
        try:
            print(f"开始加载角色: {character_name}")

            # 获取角色ID
            character_id = self.character_manager.get_character_id_by_name(character_name)
            if not character_id:
                self.show_error(f"未找到角色: {character_name}")
                print(f"未找到角色ID: {character_name}")
                return

            print(f"找到角色ID: {character_id}")

            # 获取服务实例
            self.character_service = self.service_factory.character_service

            # 使用新服务加载角色
            print(f"开始使用服务加载角色...")
            if not self.character_service.load_character_by_id(character_id):
                self.show_error(f"加载角色数据失败: {character_name}")
                print(f"服务加载失败: {character_name}")
                return

            # 获取等级配置
            level = self.main_window.character_level.get()
            extra_level = self.main_window.extra_level.get()

            print(f"等级配置: 等级={level}, 核心技={extra_level}")

            # 计算突破阶段 (根据等级确定)
            breakthrough_level = self._calculate_breakthrough_level(level)
            print(f"突破阶段: {breakthrough_level}")

            # 使用新服务计算属性
            print(f"开始计算属性...")
            base_stats = self.character_service.calculate_character_stats(
                level, breakthrough_level, extra_level
            )

            if not base_stats:
                self.show_error("计算角色属性失败")
                print(f"属性计算失败")
                return

            print(f"属性计算成功")

            # 更新UI
            self._update_with_character_data(character_id, base_stats)

            print(f"角色加载完成: {character_name}")

        except Exception as e:
            error_msg = f"加载角色失败: {str(e)}"
            self.show_error(error_msg)
            print(f"发生异常: {error_msg}")
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

    def _update_with_character_data(self, character_id: str, base_stats):
        """使用新服务的数据更新UI"""
        # 获取角色显示信息
        display_info = self.character_service.get_character_display_info()

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
        from src.config import config_manager
        rarity_color = config_manager.character.display_config.get_rarity_color(rarity)
        star_text = "★" * (rarity + 1)
        self.rarity_label.config(text=f"{star_text}", foreground=rarity_color)

        # 武器和元素
        self.weapon_label.config(text=f"特性: {display_info.get('weapon_type', '未知')}")
        self.element_label.config(text=f"元素: {display_info.get('element_type', '未知')}")

    def _update_base_stats_display(self, base_stats):
        """更新基础属性显示 - 适配新数据格式"""
        # 移除初始提示
        if self.base_placeholder:
            self.base_placeholder.destroy()
            self.base_placeholder = None

        # 清空现有标签
        for widget in self.scrollable_base_frame.winfo_children():
            widget.destroy()

        self.base_stat_labels.clear()

        # 获取显示顺序配置
        from src.config import config_manager
        output_config = config_manager.character.attribute_output_config

        # 使用新服务获取武器类型
        if self.character_service:
            display_info = self.character_service.get_character_display_info()
            weapon_type = display_info.get("weapon_type", "")
        else:
            weapon_type = ""

        # 获取输出顺序
        display_order = output_config.get_output_order(weapon_type)

        # 创建属性网格
        row = 0
        for attr_key in display_order:
            if not hasattr(base_stats, attr_key):
                continue

            value = getattr(base_stats, attr_key, 0)
            display_name = output_config.get_display_name(attr_key)
            formatted_value = self._format_attribute_value(attr_key, value)

            attr_frame = ttk.Frame(self.scrollable_base_frame)
            attr_frame.grid(row=row, column=0, sticky="we", pady=2)
            attr_frame.columnconfigure(1, weight=1)

            # 属性名称
            name_label = ttk.Label(
                attr_frame,
                text=f"{display_name}:",
                width=20,
                anchor='w'
            )
            name_label.grid(row=0, column=0, padx=(5, 10), sticky="w")

            # 属性值（蓝色）
            value_label = ttk.Label(
                attr_frame,
                text=formatted_value,
                foreground="blue",
                width=15,
                anchor='e'
            )
            value_label.grid(row=0, column=1, padx=(0, 5), sticky="e")

            self.base_stat_labels[attr_key] = value_label
            row += 1

    def update_final_stats_display(self, final_stats: FinalCharacterStats):
        """更新最终属性显示（含装备加成）"""
        self.current_final_stats = final_stats

        # 移除初始提示
        if self.final_placeholder:
            self.final_placeholder.destroy()
            self.final_placeholder = None

        # 清空现有标签
        for widget in self.scrollable_final_frame.winfo_children():
            widget.destroy()

        self.final_stat_labels.clear()

        if not final_stats:
            ttk.Label(
                self.scrollable_final_frame,
                text="请配置驱动盘以查看最终属性",
                foreground="gray"
            ).pack(pady=30)
            return

        # 获取属性显示顺序
        from src.config import config_manager
        output_config = config_manager.character.attribute_output_config

        # 使用基础属性来确定显示顺序
        if self.current_base_stats:
            weapon_type = "命破" if hasattr(self.current_base_stats,
                                            'Sheer_Force') and self.current_base_stats.Sheer_Force > 0 else "其他"
            display_order = output_config.get_output_order(weapon_type)
        else:
            display_order = output_config.DEFAULT_OUTPUT_ORDER

        # 创建属性网格
        row = 0
        for attr_key in display_order:
            if not hasattr(final_stats, attr_key):
                continue

            value = getattr(final_stats, attr_key, 0)
            display_name = output_config.get_display_name(attr_key)
            formatted_value = self._format_attribute_value(attr_key, value)

            attr_frame = ttk.Frame(self.scrollable_final_frame)
            attr_frame.grid(row=row, column=0, sticky="we", pady=2)
            attr_frame.columnconfigure(1, weight=1)

            # 属性名称
            name_label = ttk.Label(
                attr_frame,
                text=f"{display_name}:",
                width=20,
                anchor='w'
            )
            name_label.grid(row=0, column=0, padx=(5, 10), sticky="w")

            # 属性值（绿色）
            value_label = ttk.Label(
                attr_frame,
                text=formatted_value,
                foreground="green",
                width=15,
                anchor='e'
            )
            value_label.grid(row=0, column=1, padx=(0, 5), sticky="e")

            self.final_stat_labels[attr_key] = value_label
            row += 1

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
        for widget in self.scrollable_base_frame.winfo_children():
            widget.destroy()
        for widget in self.scrollable_final_frame.winfo_children():
            widget.destroy()

        # 显示错误信息
        ttk.Label(
            self.scrollable_base_frame,
            text=f"错误: {message}",
            foreground="red"
        ).pack(pady=20)

        ttk.Label(
            self.scrollable_final_frame,
            text=f"错误: {message}",
            foreground="red"
        ).pack(pady=20)