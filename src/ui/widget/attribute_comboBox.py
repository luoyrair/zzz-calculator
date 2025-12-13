import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable

from src.models.gear_attributes import Attribute


class AttributeComboBox(ttk.Combobox):
    """支持 Attribute 类型列表的 Combobox"""

    def __init__(self, master=None, **kwargs):
        # 初始化父类
        super().__init__(master, **kwargs)

        # 存储 Attribute 列表
        self._attributes: List[Attribute] = []

        # 自定义显示文本的映射函数
        self._display_func: Optional[Callable[[Attribute], str]] = lambda attr: attr.name

        # 绑定事件，用于处理选择
        # self.bind('<<ComboboxSelected>>', self._on_select)

    @property
    def attributes(self) -> List[Attribute]:
        """获取 Attribute 列表"""
        return self._attributes

    @attributes.setter
    def attributes(self, value: List[Attribute]):
        """设置 Attribute 列表"""
        if not isinstance(value, list):
            raise TypeError(f"attributes must be a list, got {type(value).__name__}")

        self._attributes = value

        # 更新显示文本
        if self._display_func:
            display_texts = [self._display_func(attr) for attr in value]
        else:
            # 默认显示 Attribute 的 name
            display_texts = [getattr(attr, 'name', str(attr)) for attr in value]

        # 设置 Combobox 的 values
        super().configure(values=display_texts)

    @property
    def display_func(self) -> Optional[Callable[[Attribute], str]]:
        """获取显示文本函数"""
        return self._display_func

    @display_func.setter
    def display_func(self, func: Callable[[Attribute], str]):
        """设置显示文本函数"""
        self._display_func = func
        # 重新应用显示函数
        if self._attributes:
            self.attributes = self._attributes

    def get_selected_attribute(self) -> Optional[Attribute]:
        """获取当前选择的 Attribute 对象"""
        try:
            index = self.current()
            if 0 <= index < len(self._attributes):
                return self._attributes[index]
        except tk.TclError:
            pass
        return None

    def set_selected_attribute(self, attribute: Attribute):
        """通过 Attribute 对象设置选择"""
        if attribute in self._attributes:
            index = self._attributes.index(attribute)
            self.current(index)
        else:
            self.current()  # 清除选择

    def _on_select(self, event=None):
        """选择事件处理"""
        # 可以在这里添加自定义的选择处理逻辑
        pass

    # 重写 configure 方法以处理 values 参数
    def configure(self, cnf=None, **kwargs):
        if 'values' in kwargs:
            values = kwargs.pop('values')
            if isinstance(values, list):
                # 检查是否是 Attribute 列表
                if all(isinstance(v, Attribute) for v in values):
                    self.attributes = values
                else:
                    # 普通文本列表
                    self._attributes = []
                    super().configure(values=values)
        return super().configure(cnf, **kwargs)

    # 重写 cget 方法以获取正确的 values
    def cget(self, key):
        if key == 'values':
            if self._attributes:
                # 返回 Attribute 列表
                return self._attributes
            else:
                return super().cget(key)
        return super().cget(key)

    # 重写 __setitem__ 和 __getitem__ 方法
    def __setitem__(self, key, value):
        if key == 'values':
            self.configure(values=value)
        else:
            super().__setitem__(key, value)

    def __getitem__(self, key):
        if key == 'values':
            return self.attributes
        return super().__getitem__(key)
