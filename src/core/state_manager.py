"""统一状态管理器 - 单一数据源"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from PyQt6.QtCore import QObject, pyqtSignal, QMutex


@dataclass
class AppState:
    """应用状态 - 所有UI组件共享的数据"""
    current_character: Optional[Any] = None
    current_weapon: Optional[Any] = None
    current_gear_sets: Dict[str, Any] = field(default_factory=dict)
    current_gear_pieces: Dict[int, Any] = field(default_factory=dict)

    # 推荐数据（只读，从角色中获取）
    @property
    def recommend_data(self):
        if self.current_character and hasattr(self.current_character, 'recommend'):
            return self.current_character.recommend
        return None


class StateManager(QObject):
    """状态管理器 - 使用类变量实现单例模式"""

    # 类变量 - 单例实例
    _instance = None
    _mutex = QMutex()  # 线程安全

    # 信号定义
    state_changed: pyqtSignal = pyqtSignal()
    character_changed: pyqtSignal = pyqtSignal(object)  # 使用object而不是Character避免循环导入
    character_cleared: pyqtSignal = pyqtSignal(object)
    weapon_changed: pyqtSignal = pyqtSignal(object)
    weapon_cleared: pyqtSignal = pyqtSignal(object)
    gear_sets_changed: pyqtSignal = pyqtSignal(list)
    gear_piece_changed: pyqtSignal = pyqtSignal(int, object)

    def __init__(self, parent=None):
        """初始化 - 确保只初始化一次"""
        super().__init__(parent)

        # 如果已经有实例，避免重复初始化
        if StateManager._instance is not None:
            return

        # 初始化状态
        self._state = AppState()

        # 设置单例实例
        StateManager._instance = self

    @classmethod
    def instance(cls, parent=None):
        """获取单例实例（类方法）"""
        cls._mutex.lock()
        try:
            if cls._instance is None:
                cls._instance = cls(parent)
            return cls._instance
        finally:
            cls._mutex.unlock()

    def get_state(self) -> AppState:
        """获取当前状态"""
        return self._state

    def update_character(self, character):
        """更新角色"""
        self._state.current_character = character
        if character:
            self.character_changed.emit(character)
        else:
            # 角色清空时发出空信号
            self.character_cleared.emit(None)
        self.state_changed.emit()

    def update_weapon(self, weapon):
        """更新武器"""
        self._state.current_weapon = weapon
        if weapon:
            self.weapon_changed.emit(weapon)
        else:
            self.weapon_changed.emit(None)
        self.state_changed.emit()

    def update_gear_sets(self, gear_sets):
        """更新驱动盘套装"""
        self._state.current_gear_sets = gear_sets
        self._state.current_character.gear_set_ids = gear_sets
        self.gear_sets_changed.emit(list(gear_sets.keys()))
        self.state_changed.emit()

    def update_gear_piece(self, position, gear_piece):
        """更新单个驱动盘"""
        self._state.current_gear_pieces[position] = gear_piece
        self.gear_piece_changed.emit(position, gear_piece)
        self.state_changed.emit()

    def clear_gear_sets(self):
        """清空驱动盘套装"""
        self._state.current_gear_sets.clear()
        self.gear_sets_changed.emit([])
        self.state_changed.emit()

    def clear_gear_pieces(self):
        """清空所有驱动盘"""
        self._state.current_gear_pieces.clear()
        self.state_changed.emit()

    def clear_all(self):
        """清空所有状态"""
        self._state.current_character = None
        self._state.current_weapon = None
        self._state.current_gear_sets.clear()
        self._state.current_gear_pieces.clear()

        # 发出清空信号
        self.character_cleared.emit(None)
        self.weapon_cleared.emit(None)
        self.gear_sets_changed.emit([])
        self.state_changed.emit()