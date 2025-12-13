from tkinter import ttk
from typing import List, Dict, Any, Optional


class GearSetComboBox(ttk.Combobox):
    """套装选择下拉框 - 显示纯名称格式"""

    def __init__(self, parent, width=25, on_selected_callback=None, **kwargs):
        super().__init__(parent, width=width, state="readonly", **kwargs)

        # 回调函数
        self.on_selected_callback = on_selected_callback

        # 数据存储
        self.all_sets: List[Dict[str, Any]] = []  # 所有套装数据
        self.available_sets: List[Dict[str, Any]] = []  # 当前可用套装
        self.selected_set_id: Optional[int] = None  # 当前选中的套装ID

        # 映射：显示文本 -> 套装ID
        self.display_to_id: Dict[str, int] = {}

        # 绑定事件
        self.bind('<<ComboboxSelected>>', self._on_combobox_selected)

        # 初始化显示
        self._update_display()

    def set_all_sets(self, all_sets: List[Dict[str, Any]]):
        """设置所有套装数据"""
        self.all_sets = all_sets
        self._update_display()

    def set_available_sets(self, available_sets: List[Dict[str, Any]]):
        """设置可用套装数据"""
        self.available_sets = available_sets
        self._update_display()

    def set_selected_set_id(self, set_id: Optional[int]):
        """设置选中的套装ID"""
        self.selected_set_id = set_id
        self._update_display()

    def get_selected_set_id(self) -> Optional[int]:
        """获取选中的套装ID"""
        return self.selected_set_id

    def get_selected_set_data(self) -> Optional[Dict[str, Any]]:
        """获取选中的套装数据"""
        if self.selected_set_id is None:
            return None

        for set_data in self.all_sets:
            if set_data['id'] == self.selected_set_id:
                return set_data

        return None

    def _format_bonus_display(self, bonus_display: str) -> str:
        """格式化加成显示文本"""
        if not bonus_display or bonus_display == "无基础属性加成":
            return ""

        # 将英文属性名转换为中文
        bonus_mapping = {
            'crit_rate': '暴击率',
            'crit_dmg': '暴击伤害',
            'pen_ratio': '穿透率',
            'attack': '攻击力',
            'defence': '防御力',
            'hp': '生命值',
            'impact': '冲击力',
            'anomaly_mastery': '异常掌控',
            'anomaly_proficiency': '异常精通',
            'energy_regen': '能量回复',
            'physical_dmg_bonus': '物理伤害',
            'fire_dmg_bonus': '火属性伤害',
            'ice_dmg_bonus': '冰属性伤害',
            'electric_dmg_bonus': '电属性伤害',
            'ether_dmg_bonus': '以太伤害'
        }

        # 解析加成值
        parts = bonus_display.split('+')
        if len(parts) >= 2:
            attr_name = parts[0]
            attr_value = parts[1]

            # 转换属性名
            chinese_name = bonus_mapping.get(attr_name, attr_name)

            # 转换数值格式
            try:
                value = float(attr_value)
                if value < 1:  # 可能是百分比
                    return f"{chinese_name}+{value * 100:.0f}%"
                else:
                    return f"{chinese_name}+{int(value)}"
            except ValueError:
                return f"{chinese_name}+{attr_value}"

        return bonus_display

    def _format_set_display(self, set_data: Dict[str, Any]) -> str:
        """格式化套装显示文本 - 只显示名称和中文加成"""
        name = set_data.get('name', '未知套装')
        bonus_display = set_data.get('bonus_display', '')

        # 格式化加成显示
        return name

    def _update_display(self):
        """更新下拉框显示"""
        # 清空映射
        self.display_to_id.clear()

        # 生成显示文本
        display_values = []

        # 如果有选中的套装，确保它在显示列表中
        if self.selected_set_id is not None:
            for set_data in self.all_sets:
                if set_data['id'] == self.selected_set_id:
                    display_text = set_data.get('name', '未知套装')
                    display_values.append(display_text)
                    self.display_to_id[display_text] = set_data['id']
                    break

        # 添加可用套装
        for set_data in self.available_sets:
            if set_data['id'] not in self.display_to_id.values():  # 避免重复
                display_text = set_data.get('name', '未知套装')
                display_values.append(display_text)
                self.display_to_id[display_text] = set_data['id']

        # 设置下拉框值
        self['values'] = display_values

        # 设置当前显示的值
        if self.selected_set_id is not None:
            # 查找对应的显示文本
            for display_text, set_id in self.display_to_id.items():
                if set_id == self.selected_set_id:
                    self.set(display_text)
                    return

        # 没有选中或找不到对应显示文本
        self.set("")

    def _on_combobox_selected(self, event):
        """下拉框选择事件"""
        display_text = self.get()

        if not display_text:
            # 清空了选择
            old_set_id = self.selected_set_id
            self.selected_set_id = None

            if self.on_selected_callback:
                self.on_selected_callback(self, old_set_id, None)
            return

        # 从显示文本获取套装ID
        set_id = self.display_to_id.get(display_text)

        if set_id is not None and set_id != self.selected_set_id:
            old_set_id = self.selected_set_id
            self.selected_set_id = set_id

            if self.on_selected_callback:
                self.on_selected_callback(self, old_set_id, set_id)

    def clear_selection(self):
        """清空选择"""
        self.selected_set_id = None
        self.set("")

        if self.on_selected_callback:
            self.on_selected_callback(self, None, None)