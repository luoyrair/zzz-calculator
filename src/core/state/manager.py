"""
可注入的状态管理器实现
"""

from typing import Dict, List, Optional, Set, Any
from PyQt6.QtCore import QObject, pyqtSignal

from src.core.state.interfaces import StateManager as StateManagerInterface
from src.core.state.interfaces import AppState, StateObserver
from src.utils.logger import get_logger


class QtStateObserver(QObject):
    """Qt信号适配器 - 将状态变化转换为Qt信号
    注意：不能同时继承 StateObserver，因为 QObject 有自己的元类
    """

    # 定义信号
    state_changed: pyqtSignal = pyqtSignal(object)  # AppState
    character_changed: pyqtSignal = pyqtSignal(object)
    character_cleared: pyqtSignal = pyqtSignal()
    weapon_changed: pyqtSignal = pyqtSignal(object)
    weapon_cleared: pyqtSignal = pyqtSignal()
    gear_sets_changed: pyqtSignal = pyqtSignal(list)
    gear_piece_changed: pyqtSignal = pyqtSignal(int, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 保存观察者引用，用于手动转发
        self._observers: Set[StateObserver] = set()

    def register_observer(self, observer: StateObserver):
        """注册额外的观察者"""
        self._observers.add(observer)

    def unregister_observer(self, observer: StateObserver):
        """注销额外的观察者"""
        self._observers.discard(observer)

    # 实现 StateObserver 接口的方法，但作为普通方法
    def on_state_changed(self, state: AppState):
        """状态变化时的回调"""
        self.state_changed.emit(state)
        # 转发给注册的观察者
        for observer in self._observers:
            try:
                observer.on_state_changed(state)
            except Exception as e:
                pass  # 避免循环导入，简单处理

    def on_character_changed(self, character):
        """角色变化时的回调"""
        if character:
            self.character_changed.emit(character)
        else:
            self.character_cleared.emit()
        # 转发给注册的观察者
        for observer in self._observers:
            try:
                observer.on_character_changed(character)
            except Exception:
                pass

    def on_weapon_changed(self, weapon):
        """武器变化时的回调"""
        if weapon:
            self.weapon_changed.emit(weapon)
        else:
            self.weapon_cleared.emit()
        # 转发给注册的观察者
        for observer in self._observers:
            try:
                observer.on_weapon_changed(weapon)
            except Exception:
                pass

    def on_gear_sets_changed(self, set_ids: List[str]):
        """驱动盘套装变化时的回调"""
        self.gear_sets_changed.emit(set_ids)
        # 转发给注册的观察者
        for observer in self._observers:
            try:
                observer.on_gear_sets_changed(set_ids)
            except Exception:
                pass

    def on_gear_piece_changed(self, position: int, gear_piece):
        """单个驱动盘变化时的回调"""
        self.gear_piece_changed.emit(position, gear_piece)
        # 转发给注册的观察者
        for observer in self._observers:
            try:
                observer.on_gear_piece_changed(position, gear_piece)
            except Exception:
                pass


class ObservableStateManager(StateManagerInterface):
    """
    可观察的状态管理器实现
    支持依赖注入，不强制使用单例
    """

    def __init__(self, initial_state: Optional[AppState] = None):
        """
        初始化状态管理器

        Args:
            initial_state: 初始状态，如果不提供则创建空状态
        """
        self.logger = get_logger("core.state.manager")
        self._state = initial_state or AppState()
        self._observers: Set[StateObserver] = set()
        self.logger.debug("ObservableStateManager 初始化")

    # ========== 状态访问 ==========

    def get_state(self) -> AppState:
        """获取当前状态"""
        return self._state

    # ========== 状态更新 ==========

    def update_character(self, character) -> bool:
        """更新角色"""
        old_character = self._state.current_character
        if old_character is character:
            return False

        # 检查是否是同一个角色的不同实例
        if (old_character and character and
                old_character.id == character.id):
            # 相同ID，但可能是更新后的实例
            self._state.current_character = character
            self._notify_character_changed(character)
            self._notify_state_changed()
            return True

        # 完全不同的角色
        self._state.current_character = character
        self._notify_character_changed(character)
        self._notify_state_changed()
        return True

    def update_weapon(self, weapon) -> bool:
        """更新武器"""
        old_weapon = self._state.current_weapon
        if old_weapon is weapon:
            return False

        # 检查是否是同一个武器的不同实例
        if (old_weapon and weapon and
                old_weapon.id == weapon.id):
            self._state.current_weapon = weapon
            self._notify_weapon_changed(weapon)
            self._notify_state_changed()
            return True

        self._state.current_weapon = weapon
        self._notify_weapon_changed(weapon)
        self._notify_state_changed()
        return True

    def update_gear_sets(self, gear_sets: Dict[str, Any]) -> bool:
        """更新驱动盘套装"""
        # 检查是否有实际变化
        old_ids = set(self._state.current_gear_sets.keys())
        new_ids = set(gear_sets.keys())

        if old_ids == new_ids:
            # ID相同，但可能需要检查内容
            # 简化实现，认为ID相同就没变化
            return False

        self._state.current_gear_sets = gear_sets.copy()
        if self._state.current_character:
            self._state.current_character.gear_set_ids = list(gear_sets.keys())

        self._notify_gear_sets_changed(list(gear_sets.keys()))
        self._notify_state_changed()
        return True

    def update_gear_piece(self, position: int, gear_piece) -> bool:
        """更新单个驱动盘"""
        old_piece = self._state.current_gear_pieces.get(position)
        if old_piece is gear_piece:
            return False

        self._state.current_gear_pieces[position] = gear_piece

        # 更新角色对象的引用
        if self._state.current_character:
            if position not in self._state.current_character.gear_pieces:
                self._state.current_character.gear_pieces[position] = {}

            if gear_piece and gear_piece.main_attribute:
                self._state.current_character.gear_pieces[position]['main'] = gear_piece.main_attribute

            if gear_piece and gear_piece.sub_attributes:
                for slot, attr in gear_piece.sub_attributes.items():
                    self._state.current_character.gear_pieces[position]['subs'][slot] = attr

        self._notify_gear_piece_changed(position, gear_piece)
        self._notify_state_changed()
        return True

    # ========== 清空操作 ==========

    def clear_character(self):
        """清空角色"""
        if self._state.current_character is None:
            return

        self._state.current_character = None
        self._notify_character_changed(None)
        self._notify_state_changed()

    def clear_weapon(self):
        """清空武器"""
        if self._state.current_weapon is None:
            return

        self._state.current_weapon = None
        self._notify_weapon_changed(None)
        self._notify_state_changed()

    def clear_gear_sets(self):
        """清空驱动盘套装"""
        if not self._state.current_gear_sets:
            return

        self._state.current_gear_sets.clear()
        if self._state.current_character:
            self._state.current_character.gear_set_ids = []

        self._notify_gear_sets_changed([])
        self._notify_state_changed()

    def clear_gear_pieces(self):
        """清空所有驱动盘"""
        if not self._state.current_gear_pieces:
            return

        self._state.current_gear_pieces.clear()
        if self._state.current_character:
            self._state.current_character.gear_pieces.clear()

        self._notify_state_changed()

    def clear_all(self):
        """清空所有状态"""
        had_character = self._state.current_character is not None
        had_weapon = self._state.current_weapon is not None
        had_gear_sets = bool(self._state.current_gear_sets)
        had_gear_pieces = bool(self._state.current_gear_pieces)

        self._state.current_character = None
        self._state.current_weapon = None
        self._state.current_gear_sets.clear()
        self._state.current_gear_pieces.clear()

        if had_character:
            self._notify_character_changed(None)
        if had_weapon:
            self._notify_weapon_changed(None)
        if had_gear_sets:
            self._notify_gear_sets_changed([])
        if had_character or had_weapon or had_gear_sets or had_gear_pieces:
            self._notify_state_changed()

    # ========== 观察者管理 ==========

    def register_observer(self, observer: StateObserver):
        """注册观察者"""
        self._observers.add(observer)
        self.logger.debug(f"观察者注册: {observer.__class__.__name__}")

        # 特殊处理：如果是 QtStateObserver，注册到它自己
        if isinstance(observer, QtStateObserver):
            observer.register_observer(self)  # 双向注册

    def unregister_observer(self, observer: StateObserver):
        """注销观察者"""
        self._observers.discard(observer)
        self.logger.debug(f"观察者注销: {observer.__class__.__name__}")

    # ========== 内部通知方法 ==========

    def _notify_state_changed(self):
        """通知所有观察者状态已变化"""
        for observer in self._observers:
            try:
                observer.on_state_changed(self._state)
            except Exception as e:
                self.logger.error(f"通知观察者失败: {e}")

    def _notify_character_changed(self, character):
        """通知所有观察者角色已变化"""
        for observer in self._observers:
            try:
                observer.on_character_changed(character)
            except Exception as e:
                self.logger.error(f"通知观察者角色变化失败: {e}")

    def _notify_weapon_changed(self, weapon):
        """通知所有观察者武器已变化"""
        for observer in self._observers:
            try:
                observer.on_weapon_changed(weapon)
            except Exception as e:
                self.logger.error(f"通知观察者武器变化失败: {e}")

    def _notify_gear_sets_changed(self, set_ids: List[str]):
        """通知所有观察者套装已变化"""
        for observer in self._observers:
            try:
                observer.on_gear_sets_changed(set_ids)
            except Exception as e:
                self.logger.error(f"通知观察者套装变化失败: {e}")

    def _notify_gear_piece_changed(self, position: int, gear_piece):
        """通知所有观察者驱动盘已变化"""
        for observer in self._observers:
            try:
                observer.on_gear_piece_changed(position, gear_piece)
            except Exception as e:
                self.logger.error(f"通知观察者驱动盘变化失败: {e}")

    # ========== 工具方法 ==========

    def create_snapshot(self) -> AppState:
        """创建当前状态的快照（用于测试）"""
        return self._state.copy()

    def restore_snapshot(self, snapshot: AppState):
        """恢复状态快照（用于测试）"""
        self._state = snapshot
        self._notify_state_changed()