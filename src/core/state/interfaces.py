"""
状态管理接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class AppState:
    """应用状态数据对象 - 纯数据容器"""
    current_character: Optional[Any] = None  # Character 对象
    current_weapon: Optional[Any] = None  # Weapon 对象
    current_gear_sets: Dict[str, Any] = field(default_factory=dict)  # set_id -> GearSet
    current_gear_pieces: Dict[int, Any] = field(default_factory=dict)  # position -> GearPiece

    @property
    def recommend_data(self):
        """获取推荐数据（只读）"""
        if self.current_character and hasattr(self.current_character, 'recommend'):
            return self.current_character.recommend
        return None

    def copy(self) -> 'AppState':
        """创建状态的深拷贝（用于测试）"""
        import copy
        return copy.deepcopy(self)


class StateObserver(ABC):
    """状态观察者接口"""

    @abstractmethod
    def on_state_changed(self, state: AppState):
        """状态变化时的回调"""
        pass

    @abstractmethod
    def on_character_changed(self, character):
        """角色变化时的回调"""
        pass

    @abstractmethod
    def on_weapon_changed(self, weapon):
        """武器变化时的回调"""
        pass

    @abstractmethod
    def on_gear_sets_changed(self, set_ids: List[str]):
        """驱动盘套装变化时的回调"""
        pass

    @abstractmethod
    def on_gear_piece_changed(self, position: int, gear_piece):
        """单个驱动盘变化时的回调"""
        pass


class StateManager(ABC):
    """状态管理器接口"""

    @abstractmethod
    def get_state(self) -> AppState:
        """获取当前状态"""
        pass

    @abstractmethod
    def update_character(self, character) -> bool:
        """更新角色，返回是否真的有变化"""
        pass

    @abstractmethod
    def update_weapon(self, weapon) -> bool:
        """更新武器，返回是否真的有变化"""
        pass

    @abstractmethod
    def update_gear_sets(self, gear_sets: Dict[str, Any]) -> bool:
        """更新驱动盘套装，返回是否真的有变化"""
        pass

    @abstractmethod
    def update_gear_piece(self, position: int, gear_piece) -> bool:
        """更新单个驱动盘，返回是否真的有变化"""
        pass

    @abstractmethod
    def clear_character(self):
        """清空角色"""
        pass

    @abstractmethod
    def clear_weapon(self):
        """清空武器"""
        pass

    @abstractmethod
    def clear_gear_sets(self):
        """清空驱动盘套装"""
        pass

    @abstractmethod
    def clear_gear_pieces(self):
        """清空所有驱动盘"""
        pass

    @abstractmethod
    def clear_all(self):
        """清空所有状态"""
        pass

    @abstractmethod
    def register_observer(self, observer: StateObserver):
        """注册观察者"""
        pass

    @abstractmethod
    def unregister_observer(self, observer: StateObserver):
        """注销观察者"""
        pass