# src/ui/character_panel.py
"""重构后的角色面板 - 使用服务工厂"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional

from src.core.service_factory import get_service_factory
from src.services.calculation_service import CalculationService


class CharacterPanel(ttk.Frame):
    """角色面板 - 单一职责：显示角色信息和属性"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window

        # 通过服务工厂获取服务实例
        self.service_factory = get_service_factory()
        self.character_loader = self.service_factory.character_loader
        self.character_manager = self.service_factory.character_manager
        self.character_calculator = self.service_factory.character_calculator
        self.calculation_service = CalculationService()

        # 当前角色状态
        self.current_character_id = tk.StringVar(value="")
        self.current_character_data: Optional[Dict[str, Any]] = None

        # UI变量 - 基础属性
        self.base_hp = tk.StringVar(value="0")
        self.base_atk = tk.StringVar(value="0")
        self.base_crit_rate = tk.StringVar(value="0.0%")
        self.base_crit_dmg = tk.StringVar(value="0.0%")

        # UI变量 - 计算结果
        self.final_hp = tk.StringVar(value="0")
        self.final_atk = tk.StringVar(value="0")
        self.final_def = tk.StringVar(value="0")
        self.final_crit_rate = tk.StringVar(value="0%")
        self.final_crit_dmg = tk.StringVar(value="0%")
        self.final_impact = tk.StringVar(value="0")
        self.final_penetration = tk.StringVar(value="0%")
        self.final_anomaly_mastery = tk.StringVar(value="0")
        self.final_anomaly_proficiency = tk.StringVar(value="0")
        self.final_energy_regen = tk.StringVar(value="0")

        self.setup_ui()

    def setup_ui(self):
        """设置UI组件"""
        # 角色信息区域
        self.setup_character_info()

        # 基础属性显示区域
        self.setup_base_stats()

        # 计算结果区域
        self.setup_calculation_results()

    def setup_character_info(self):
        """设置角色信息区域"""
        info_frame = ttk.LabelFrame(self, text="当前角色", padding="5")
        info_frame.pack(fill='x', pady=(0, 10))

        # 角色名称
        self.character_name_label = ttk.Label(
            info_frame,
            text="未选择角色",
            font=("", 10, "bold"),
            foreground="blue"
        )
        self.character_name_label.pack(pady=5)

        # 角色详细信息
        detail_frame = ttk.Frame(info_frame)
        detail_frame.pack(fill='x', pady=(5, 0))

        self.rarity_label = ttk.Label(detail_frame, text="", foreground="gray")
        self.rarity_label.pack(side='left', padx=(0, 10))

        self.weapon_label = ttk.Label(detail_frame, text="", foreground="gray")
        self.weapon_label.pack(side='left', padx=(0, 10))

        self.element_label = ttk.Label(detail_frame, text="", foreground="gray")
        self.element_label.pack(side='left')

    def setup_base_stats(self):
        """设置基础属性显示区域"""
        attr_frame = ttk.LabelFrame(self, text="基础属性", padding="5")
        attr_frame.pack(fill='x', pady=(0, 10))

        # 创建属性显示网格
        self.attr_labels = {}
        attributes = [
            ("生命值:", "base_hp", "0"),
            ("攻击力:", "base_atk", "0"),
            ("防御力:", "base_def", "0"),
            ("暴击率:", "base_crit_rate", "0%"),
            ("暴击伤害:", "base_crit_dmg", "0%"),
            ("冲击力:", "impact", "0"),
            ("异常掌控:", "anomaly_mastery", "0"),
            ("异常精通:", "anomaly_proficiency", "0"),
            ("穿透率:", "penetration", "0%"),
            ("能量自动回复:", "energy_regen", "0")
        ]

        for i, (label_text, attr_key, default_value) in enumerate(attributes):
            # 标签
            ttk.Label(attr_frame, text=label_text).grid(
                row=i, column=0, sticky=tk.W, pady=2, padx=(5, 0)
            )

            # 值显示
            value_label = ttk.Label(
                attr_frame,
                text=default_value,
                foreground="blue",
                width=12,
                anchor='e'
            )
            value_label.grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 5))
            self.attr_labels[attr_key] = value_label

    def setup_calculation_results(self):
        """设置计算结果区域"""
        result_frame = ttk.LabelFrame(self, text="装备加成详情", padding="5")
        result_frame.pack(fill='both', expand=True)

        # 创建计算结果属性显示网格
        result_attributes = [
            ("生命值:", self.final_hp),
            ("攻击力:", self.final_atk),
            ("防御力:", self.final_def),
            ("暴击率:", self.final_crit_rate),
            ("暴击伤害:", self.final_crit_dmg),
            ("冲击力:", self.final_impact),
            ("异常掌控:", self.final_anomaly_mastery),
            ("异常精通:", self.final_anomaly_proficiency),
            ("穿透率:", self.final_penetration),
            ("能量自动回复:", self.final_energy_regen)
        ]

        for i, (label_text, value_var) in enumerate(result_attributes):
            # 标签
            ttk.Label(result_frame, text=label_text).grid(
                row=i, column=0, sticky=tk.W, pady=2, padx=(5, 0)
            )

            # 值显示
            value_label = ttk.Label(
                result_frame,
                textvariable=value_var,
                foreground="green",
                width=15,
                anchor='e'
            )
            value_label.grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 5))

        # 初始提示文本
        self._set_initial_values()

    def load_character(self, character_name: str):
        """加载角色数据"""
        self._set_loading_state()

        try:
            character_id = self.character_manager.get_character_id_by_name(character_name)
            if not character_id:
                self._handle_load_error(f"未找到角色: {character_name}")
                return

            # 统一使用同步加载确保数据一致性
            character_data = self.character_loader.load_character(character_id)
            if not character_data:
                self._handle_load_error(f"角色数据加载失败: {character_name}")
                return

            display_info = self.character_calculator.get_character_display_info(character_id)
            self._update_ui_with_character_data(character_id, character_data, display_info)

        except Exception as e:
            self._handle_load_error(f"加载角色失败: {str(e)}")

    def update_base_stats_display(self, base_stats: Dict[str, float]):
        """更新基础属性显示"""
        try:
            # 更新标签显示
            self.attr_labels["base_hp"].config(text=f"{base_stats['base_hp']:,.0f}")
            self.attr_labels["base_atk"].config(text=f"{base_stats['base_atk']:,.0f}")
            self.attr_labels["base_def"].config(text=f"{base_stats['base_def']:,.0f}")
            self.attr_labels["base_crit_rate"].config(text=f"{base_stats['base_crit_rate']:.1%}")
            self.attr_labels["base_crit_dmg"].config(text=f"{base_stats['base_crit_dmg']:.1%}")
            self.attr_labels["impact"].config(text=f"{base_stats['impact']:,.0f}")
            self.attr_labels["penetration"].config(text=f"{base_stats['penetration']:.1%}")
            self.attr_labels["anomaly_mastery"].config(text=f"{base_stats['anomaly_mastery']:,.0f}")
            self.attr_labels["anomaly_proficiency"].config(text=f"{base_stats['anomaly_proficiency']:,.0f}")
            self.attr_labels["energy_regen"].config(text=f"{base_stats['energy_regen']:,.1f}")

            # 更新UI变量
            self.base_hp.set(str(int(base_stats["base_hp"])))
            self.base_atk.set(str(int(base_stats["base_atk"])))
            self.base_crit_rate.set(f"{base_stats['base_crit_rate']:.1%}")
            self.base_crit_dmg.set(f"{base_stats['base_crit_dmg']:.1%}")

        except Exception as e:
            print(f"更新基础属性显示失败: {e}")

    def update_display(self, calculation_result):
        """更新计算结果显示"""
        try:
            # 更新计算结果UI变量
            self._update_result_variables(calculation_result)

        except Exception as e:
            print(f"更新计算结果失败: {e}")
            self.show_error(f"显示计算结果失败: {str(e)}")

    def _update_result_variables(self, result):
        """更新计算结果UI变量"""
        try:
            # 更新最终属性值
            self.final_hp.set(f"{result.hp['final_hp']:,.0f}")
            self.final_atk.set(f"{result.atk['final_atk']:,.0f}")
            self.final_def.set(f"{result.def_stat['final_def']:,.0f}")
            self.final_crit_rate.set(f"{result.crit['total_crit_rate']:.1%}")
            self.final_crit_dmg.set(f"{result.crit['total_crit_dmg']:.1%}")
            self.final_impact.set(f"{result.impact['final_impact']:,.0f}")
            self.final_penetration.set(f"{result.penetration['final_penetration']:.1%}")
            self.final_anomaly_mastery.set(f"{result.anomaly['final_mastery']:,.0f}")
            self.final_anomaly_proficiency.set(f"{result.anomaly['final_proficiency']:,.0f}")
            self.final_energy_regen.set(f"{result.energy_regen['final_energy_regen']:,.1f}")

        except Exception as e:
            print(f"更新结果变量失败: {e}")

    def show_error(self, message: str):
        """显示错误信息"""
        self.character_name_label.config(text="错误", foreground="red")
        self._set_error_values(message)

    def _update_ui_with_character_data(self, character_id: str,
                                       character_data: Dict[str, Any],
                                       display_info: Dict[str, str]):
        """使用角色数据更新UI"""

        try:
            # 更新角色信息显示
            self._update_character_info(display_info)

            # 设置当前角色ID
            self.current_character_id.set(character_id)
            self.current_character_data = character_data

            # 获取主窗口的配置
            level = getattr(self.main_window, 'character_level', tk.IntVar(value=60)).get()
            passive_level = getattr(self.main_window, 'passive_level', tk.IntVar(value=7)).get()

            # 计算角色基础属性
            base_stats = self.character_calculator.get_character_base_stats(
                character_id, level, passive_level
            )

            self.update_base_stats_display(base_stats)

            # 更新主窗口的数据模型
            self._update_main_window_data(base_stats)

            # 触发计算更新
            self.main_window.update_calculation()

        except Exception as e:
            print(f"更新UI失败: {e}")
            self.show_error(f"更新界面失败: {str(e)}")

    def _update_character_info(self, display_info: Dict[str, str]):
        """更新角色信息显示"""
        self.character_name_label.config(text=display_info["name"])

        # 稀有度显示
        rarity = int(display_info["rarity"])
        from src.config import config_manager
        rarity_color = config_manager.character.display_config.get_rarity_color(rarity)
        self.rarity_label.config(
            text=f"{rarity + 1}星",
            foreground=rarity_color
        )

        # 武器类型
        self.weapon_label.config(text=display_info["weapon_type"])

        # 元素类型
        self.element_label.config(text=display_info["element_type"])

    def _update_main_window_data(self, base_stats: Dict[str, float]):
        """更新主窗口数据模型"""
        try:
            # 更新数据模型的角色属性
            self.main_window.data_model.character_stats.base_hp = base_stats["base_hp"]
            self.main_window.data_model.character_stats.base_atk = base_stats["base_atk"]
            self.main_window.data_model.character_stats.base_def = base_stats["base_def"]
            self.main_window.data_model.character_stats.impact = base_stats["impact"]
            self.main_window.data_model.character_stats.base_crit_rate = base_stats["base_crit_rate"]
            self.main_window.data_model.character_stats.base_crit_dmg = base_stats["base_crit_dmg"]
            self.main_window.data_model.character_stats.anomaly_mastery = base_stats["anomaly_mastery"]
            self.main_window.data_model.character_stats.anomaly_proficiency = base_stats["anomaly_proficiency"]
            self.main_window.data_model.character_stats.penetration = base_stats["penetration"]
            self.main_window.data_model.character_stats.energy_regen = base_stats["energy_regen"]

        except Exception as e:
            print(f"更新主窗口数据失败: {e}")

    def _set_loading_state(self):
        """设置加载状态"""
        self.character_name_label.config(text="加载中...", foreground="orange")
        self._set_loading_values()

    def _handle_load_error(self, error_message: str):
        """处理加载错误"""
        self.show_error(error_message)

    def _set_initial_values(self):
        """设置初始值"""
        self.final_hp.set("请选择角色")
        self.final_atk.set("并配置驱动盘")
        self.final_def.set("以查看计算结果")
        self.final_crit_rate.set("")
        self.final_crit_dmg.set("")
        self.final_impact.set("")
        self.final_penetration.set("")
        self.final_anomaly_mastery.set("")
        self.final_anomaly_proficiency.set("")
        self.final_energy_regen.set("")

    def _set_loading_values(self):
        """设置加载中的值"""
        self.final_hp.set("加载中...")
        self.final_atk.set("")
        self.final_def.set("")
        self.final_crit_rate.set("")
        self.final_crit_dmg.set("")
        self.final_impact.set("")
        self.final_penetration.set("")
        self.final_anomaly_mastery.set("")
        self.final_anomaly_proficiency.set("")
        self.final_energy_regen.set("")

    def _set_error_values(self, message: str):
        """设置错误状态的值"""
        self.final_hp.set(f"错误: {message}")
        self.final_atk.set("")
        self.final_def.set("")
        self.final_crit_rate.set("")
        self.final_crit_dmg.set("")
        self.final_impact.set("")
        self.final_penetration.set("")
        self.final_anomaly_mastery.set("")
        self.final_anomaly_proficiency.set("")
        self.final_energy_regen.set("")

    def _safe_calc_increase(self, final_value: float, base_value: float) -> float:
        """安全计算提升百分比"""
        if base_value == 0:
            return 0.0
        return final_value / base_value - 1