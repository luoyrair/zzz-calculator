"""音擎选择下拉框组件"""
from tkinter import ttk
from typing import List, Dict, Optional

from src.data.manager import data_manager


class WeaponComboBox(ttk.Combobox):
    """音擎选择下拉框"""

    def __init__(self, parent, width=25, on_selected_callback=None, **kwargs):
        super().__init__(parent, width=width, state="readonly", **kwargs)

        # 回调函数
        self.on_selected_callback = on_selected_callback

        # 数据存储
        self.weapons: List[Dict[str, any]] = []
        self.selected_weapon_id: Optional[int] = None

        # 加载音擎数据
        self.load_weapons()

        # 绑定事件
        self.bind('<<ComboboxSelected>>', self._on_selected)

    def load_weapons(self):
        """加载音擎数据"""
        try:
            # 从数据管理器获取所有音擎
            weapon_infos = data_manager.get_all_weapons()

            # 转换为字典格式
            self.weapons = []
            for weapon in weapon_infos:
                self.weapons.append({
                    'id': weapon.id,
                    'name': weapon.name,
                    'rarity': weapon.rarity + 1
                })

            # 按稀有度排序（稀有度高的在前）
            self.weapons.sort(key=lambda x: x['rarity'], reverse=True)

            # 生成显示文本
            display_texts = []
            for weapon in self.weapons:
                # 根据稀有度添加星号
                stars = "★" * weapon['rarity']
                display_texts.append(f"{weapon['name']} ({stars})")

            # 设置下拉框选项
            self['values'] = display_texts

        except Exception as e:
            print(f"加载音擎数据失败: {e}")
            self['values'] = ["加载失败"]

    def get_selected_weapon_id(self) -> Optional[int]:
        """获取选中的音擎ID"""
        return self.selected_weapon_id

    def get_selected_weapon_data(self) -> Optional[Dict[str, any]]:
        """获取选中的音擎数据"""
        if self.selected_weapon_id is None:
            return None

        for weapon in self.weapons:
            if weapon['id'] == self.selected_weapon_id:
                return weapon

        return None

    def set_selected_weapon_id(self, weapon_id: int):
        """设置选中的音擎ID"""
        self.selected_weapon_id = weapon_id

        # 更新显示
        for i, weapon in enumerate(self.weapons):
            if weapon['id'] == weapon_id:
                stars = "★" * weapon['rarity']
                display_text = f"{weapon['name']} ({stars})"
                self.set(display_text)
                break

    def _on_selected(self, event):
        """选择事件处理"""
        selected_index = self.current()

        if 0 <= selected_index < len(self.weapons):
            old_id = self.selected_weapon_id
            new_id = self.weapons[selected_index]['id']

            self.selected_weapon_id = new_id

            # 调用回调函数
            if self.on_selected_callback:
                self.on_selected_callback(self, old_id, new_id)

    def clear_selection(self):
        """清空选择"""
        self.selected_weapon_id = None
        self.set("")