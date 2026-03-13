"""简化版应用核心"""

from typing import Union, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from src.config.settings import settings_manager
from src.utils.logger import get_logger
from .calculator import AttributeCalculator
from .interfaces import DataProvider
from .state.interfaces import StateManager
from .state.manager import QtStateObserver


class ApplicationCore(QObject):
    """应用核心 - 支持状态注入"""

    # 信号定义（保持兼容）
    base_attributes_updated: pyqtSignal = pyqtSignal(dict)
    character_attributes_updated: pyqtSignal = pyqtSignal(dict)

    def __init__(self,
                 data_provider: Optional[DataProvider] = None,
                 state_manager: Optional[StateManager] = None):
        """
        初始化应用核心

        Args:
            data_provider: 数据提供者
            state_manager: 状态管理器（如果不提供，创建新的实例）
        """
        super().__init__()
        self.logger = get_logger("core.app")
        self.logger.info("ApplicationCore 初始化开始")

        # 设置数据提供者
        if data_provider is None:
            from src.core.data_manager import SimpleDataManager
            self.data_provider = SimpleDataManager()
            self.data_provider.initialize()
        else:
            self.data_provider = data_provider

        # 设置状态管理器
        if state_manager is None:
            from src.core.state.manager import ObservableStateManager
            self.state_manager = ObservableStateManager()
        else:
            self.state_manager = state_manager

        # 创建计算器
        self.calculator = AttributeCalculator()

        # 创建Qt信号适配器（用于UI）
        self._qt_observer = QtStateObserver()
        self.state_manager.register_observer(self._qt_observer)

        # 连接状态管理器的信号到自己的信号
        self._qt_observer.character_changed.connect(self._on_state_character_changed)
        self._qt_observer.weapon_changed.connect(self._on_state_weapon_changed)

        self.logger.info("ApplicationCore 初始化完成")

    # ========== 暴露状态管理器的信号给UI ==========

    @property
    def state_changed(self):
        return self._qt_observer.state_changed

    @property
    def character_changed(self):
        return self._qt_observer.character_changed

    @property
    def weapon_changed(self):
        return self._qt_observer.weapon_changed

    @property
    def gear_sets_changed(self):
        return self._qt_observer.gear_sets_changed

    @property
    def gear_piece_changed(self):
        return self._qt_observer.gear_piece_changed

    @property
    def character_cleared(self):
        return self._qt_observer.character_cleared

    @property
    def weapon_cleared(self):
        return self._qt_observer.weapon_cleared

    # ========== 业务方法 ==========

    def set_character(self, character_id: Union[int, None], level: int = 60,
                      breakthrough: int = 6, core_passive: int = 7):
        """设置当前角色"""
        self.logger.debug(f"设置角色: id={character_id}")

        if character_id is None or character_id == -1:
            self.logger.info("清空角色选择")
            self.state_manager.clear_character()
            return

        character = self.data_provider.get_character(character_id)
        if not character:
            self.logger.error(f"未找到角色: {character_id}")
            return

        # 更新角色等级信息
        if character.level != level:
            character.level = level
        if character.breakthrough != breakthrough:
            character.breakthrough = breakthrough
        if character.core_passive != core_passive:
            character.core_passive = core_passive

        # 更新状态管理器
        self.state_manager.update_character(character)

        # 计算并更新属性
        self._calculate_and_update_all()

    def set_weapon(self, weapon_id: Union[int, None], level: int = 60,
                   refinement: int = 5, talent: int = 1, flag=None):
        """设置当前武器"""
        self.logger.debug(f"设置武器: id={weapon_id}")

        if weapon_id is None or weapon_id == -1:
            self.logger.info("清空音擎选择")
            self.state_manager.clear_weapon()
            return

        weapon = self.data_provider.get_weapon(weapon_id)
        if not weapon:
            self.logger.error(f"未找到武器: {weapon_id}")
            return

        # 更新武器等级信息
        if weapon.level != level:
            weapon.level = level
        if weapon.refinement != refinement:
            weapon.refinement = refinement
        if weapon.talent != talent:
            weapon.talent = talent

        if flag:
            self.logger.debug("设置武器数据计算标志为False")
            weapon.data_calculation_flag = False

        # 更新状态管理器
        self.state_manager.update_weapon(weapon)

        # 计算并更新属性
        self._calculate_and_update_all()

    def set_gear_sets(self, set_ids: list):
        """设置驱动盘套装"""
        self.logger.debug(f"设置驱动盘套装: {set_ids}")

        gear_sets = {}
        if set_ids:
            for set_id in set_ids:
                if not set_id:
                    continue
                gear_set = self.data_provider.get_gear_set(set_id)
                if gear_set:
                    gear_sets[set_id] = gear_set

        self.state_manager.update_gear_sets(gear_sets)
        self._calculate_and_update_all()

    def set_gear_piece(self, position: int, main_attribute=None, sub_attributes=None):
        """设置单个驱动盘"""
        self.logger.debug(f"设置驱动盘: position={position}")

        from src.core.models import GearPiece

        # 获取现有状态
        state = self.state_manager.get_state()

        if position in state.current_gear_pieces:
            gear_piece = state.current_gear_pieces[position]
        else:
            gear_piece = GearPiece(position=position)

        # 更新属性
        if main_attribute:
            gear_piece.main_attribute = main_attribute

        if sub_attributes:
            gear_piece.sub_attributes.update(sub_attributes)
            # 清理空值
            for slot, attr in list(gear_piece.sub_attributes.items()):
                if attr is None:
                    del gear_piece.sub_attributes[slot]

        self.state_manager.update_gear_piece(position, gear_piece)
        self._calculate_and_update_all()

    # ========== 内部方法 ==========

    def _on_state_character_changed(self, character):
        """处理状态管理器中的角色变化"""
        self.logger.debug(f"角色变化: {character.name if character else 'None'}")
        # 可以在这里添加额外的业务逻辑

    def _on_state_weapon_changed(self, weapon):
        """处理状态管理器中的武器变化"""
        self.logger.debug(f"武器变化: {weapon.name if weapon else 'None'}")

    def _calculate_and_update_all(self):
        """计算并更新所有属性"""
        state = self.state_manager.get_state()

        if not state.current_character:
            self.logger.warning("没有当前角色，跳过计算")
            return

        # 获取显示设置
        settings = settings_manager.get_settings()
        display_mode = settings.display.character_attribute_display_mode

        # 计算基础属性
        if state.current_weapon:
            base_attributes = self.calculator.calculate_with_weapon(
                state.current_character,
                state.current_weapon,
                include_talent=False
            )
        else:
            base_attributes = self.calculator.calculate_character_only(
                state.current_character
            )

        # 发送基础属性信号
        if settings.display.show_basic_attributes_section:
            self.base_attributes_updated.emit(base_attributes)

        # 计算完整属性
        has_gear = bool(state.current_gear_sets or state.current_gear_pieces)

        if has_gear or display_mode == 2:
            include_talent = (display_mode == 2)

            character_attributes = self.calculator.calculate(
                character=state.current_character,
                weapon=state.current_weapon,
                gear_sets=state.current_gear_sets,
                gear_pieces=state.current_gear_pieces,
                include_talent=include_talent
            )

            self.character_attributes_updated.emit(character_attributes)
        else:
            self.character_attributes_updated.emit(base_attributes.copy())

    def clear_all(self):
        """清空所有选择"""
        self.state_manager.clear_all()
        self.base_attributes_updated.emit({})
        self.character_attributes_updated.emit({})