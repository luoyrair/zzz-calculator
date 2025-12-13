"""音擎信息显示组件"""
import tkinter as tk
from tkinter import ttk

from src.data.manager import data_manager
from src.parsers.weapon_parsers import WeaponConverter


class WeaponInfoDisplay(ttk.Frame):
    """音擎信息显示组件"""

    def __init__(self, parent):
        super().__init__(parent)

        # 当前音擎数据
        self.current_weapon_schema = None

        # 设置UI
        self.setup_ui()

    def setup_ui(self):
        """设置UI组件"""
        # 基本信息区域
        info_frame = ttk.LabelFrame(self, text="音擎信息", padding="10")
        info_frame.pack(fill='x', padx=5, pady=5)

        # 名称和稀有度
        self.name_frame = ttk.Frame(info_frame)
        self.name_frame.pack(fill='x', pady=(0, 5))

        self.name_label = ttk.Label(
            self.name_frame,
            text="未选择音擎",
            font=("", 11, "bold"),
            foreground="blue"
        )
        self.name_label.pack(side='left', padx=(0, 10))

        self.rarity_label = ttk.Label(
            self.name_frame,
            text="",
            font=("", 11, "bold"),
            foreground="orange"
        )
        self.rarity_label.pack(side='left')

        # 属性区域
        self.stats_frame = ttk.Frame(info_frame)
        self.stats_frame.pack(fill='x')

        # 基础攻击力
        self.base_atk_label = ttk.Label(
            self.stats_frame,
            text="基础攻击力: 0"
        )
        self.base_atk_label.pack(anchor='w', pady=2)

        # 随机属性
        self.random_attr_label = ttk.Label(
            self.stats_frame,
            text="随机属性: 无"
        )
        self.random_attr_label.pack(anchor='w', pady=2)

        # 天赋区域
        talent_frame = ttk.LabelFrame(self, text="天赋效果", padding="10")
        talent_frame.pack(fill='x', padx=5, pady=5)

        # 天赋描述（支持多行显示）
        self.talent_text = tk.Text(
            talent_frame,
            height=4,
            width=40,
            wrap='word',
            font=("", 9),
            bg='#f5f5f5',
            relief='flat'
        )
        self.talent_text.pack(fill='both', expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(talent_frame)
        scrollbar.pack(side='right', fill='y')

        self.talent_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.talent_text.yview)

        # 初始状态
        self.talent_text.insert('1.0', "请选择音擎以查看天赋效果")
        self.talent_text.config(state='disabled')

    def load_weapon(self, weapon_id: int, weapon_level: int = 60):
        """加载音擎信息"""
        try:
            # 获取音擎信息
            weapon = data_manager.get_weapon(weapon_id)
            if not weapon or not weapon.file_path.exists():
                self.show_no_weapon()
                return

            # 加载音擎数据
            self.current_weapon_schema = WeaponConverter.load_from_file(weapon.file_path)

            # 更新基本信息
            self.update_basic_info(weapon)

            # 更新属性信息
            self.update_stats(weapon_level)

            # 更新天赋信息
            self.update_talent()

        except Exception as e:
            print(f"加载音擎信息失败: {e}")
            self.show_error(f"加载失败: {str(e)}")

    def update_basic_info(self, weapon_info):
        """更新基本信息"""
        # 名称
        self.name_label.config(text=weapon_info.name)

        # 稀有度
        rarity = weapon_info.rarity
        stars = "★" * rarity
        self.rarity_label.config(text=stars)

    def update_stats(self, weapon_level: int):
        """更新属性信息"""
        if not self.current_weapon_schema:
            return

        try:
            # 计算最终属性值
            base_atk, random_attr = self.current_weapon_schema.calculate_final_values(weapon_level)

            # 更新基础攻击力
            self.base_atk_label.config(text=f"基础攻击力: {int(base_atk)}")

            # 更新随机属性
            random_attr_type = self.current_weapon_schema.random_attr_type.value
            attr_name_mapping = {
                "attack": "攻击力",
                "crit_rate": "暴击率",
                "crit_dmg": "暴击伤害",
                "anomaly_proficiency": "异常精通",
                "hp": "生命值",
                "defence": "防御力",
                "energy_regen": "能量回复",
                "pen_ratio": "穿透率",
                "impact": "冲击力",
                "anomaly_mastery": "异常掌控"
            }

            attr_display_name = attr_name_mapping.get(random_attr_type, random_attr_type)

            if self.current_weapon_schema.random_attr_is_percentage:
                # 百分比属性
                display_value = f"{random_attr:.1%}"
            else:
                # 数值属性
                display_value = f"{int(random_attr)}"

            self.random_attr_label.config(
                text=f"{attr_display_name}: {display_value}"
            )

        except Exception as e:
            print(f"更新属性信息失败: {e}")
            self.random_attr_label.config(text=f"随机属性: 计算失败")

    def update_talent(self):
        """更新天赋信息"""
        if not self.current_weapon_schema:
            return

        # 清空文本
        self.talent_text.config(state='normal')
        self.talent_text.delete('1.0', tk.END)

        try:
            # 获取天赋描述（如果有的话）
            talents = self.current_weapon_schema.talents

            if talents:
                # 获取最高星级的天赋
                max_star = max(talents.keys())
                talent = talents.get(max_star)

                if talent:
                    # 插入天赋信息
                    self.talent_text.insert('1.0', f"{talent.name}\n\n")
                    self.talent_text.insert(tk.END, talent.description)
                else:
                    self.talent_text.insert('1.0', "无天赋信息")
            else:
                self.talent_text.insert('1.0', "无天赋信息")

        except Exception as e:
            print(f"更新天赋信息失败: {e}")
            self.talent_text.insert('1.0', f"加载天赋失败: {str(e)}")

        # 禁用编辑
        self.talent_text.config(state='disabled')

    def show_no_weapon(self):
        """显示无音擎状态"""
        self.name_label.config(text="未选择音擎", foreground="gray")
        self.rarity_label.config(text="")
        self.base_atk_label.config(text="基础攻击力: 0")
        self.random_attr_label.config(text="随机属性: 无")

        self.talent_text.config(state='normal')
        self.talent_text.delete('1.0', tk.END)
        self.talent_text.insert('1.0', "请选择音擎以查看天赋效果")
        self.talent_text.config(state='disabled')

        self.current_weapon_schema = None

    def show_error(self, message: str):
        """显示错误信息"""
        self.name_label.config(text="错误", foreground="red")
        self.rarity_label.config(text="")
        self.base_atk_label.config(text=f"错误: {message}")
        self.random_attr_label.config(text="")

        self.talent_text.config(state='normal')
        self.talent_text.delete('1.0', tk.END)
        self.talent_text.insert('1.0', f"加载失败: {message}")
        self.talent_text.config(state='disabled')