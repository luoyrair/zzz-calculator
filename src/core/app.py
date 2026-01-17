"""简化版应用核心"""

from typing import Union

from PyQt6.QtCore import QObject, pyqtSignal

from src.config.settings import settings_manager
from src.utils.logger import get_logger
from .calculator import AttributeCalculator
from .data_manager import SimpleDataManager
from .models import GearPiece


class ApplicationCore(QObject):
    """应用核心 - 连接UI和数据层"""

    # 信号定义
    base_attributes_updated: pyqtSignal = pyqtSignal(dict)  # 基础属性更新信号
    character_attributes_updated: pyqtSignal = pyqtSignal(dict)  # 角色属性更新信号

    def __init__(self):
        super().__init__()
        self.logger = get_logger("core.app")
        self.logger.info("ApplicationCore 初始化开始")
        self.data_manager = SimpleDataManager()
        self.calculator = AttributeCalculator(self.data_manager)

        # 获取状态管理器实例
        from src.core.state_manager import StateManager
        self.state = StateManager.instance()

        # 加载数据
        self._load_data()
        self.logger.info("ApplicationCore 初始化完成")

    def _load_data(self):
        """加载数据"""
        self.logger.info("开始加载数据")
        if not self.data_manager.load_all():
            self.logger.error("数据加载失败")
        else:
            self.logger.info("数据加载成功")

    def set_character(self, character_id: Union[int, None], level: int = 60,
                      breakthrough: int = 6, core_passive: int = 7):
        """设置当前角色"""
        self.logger.debug(f"设置角色: id={character_id}, level={level}, breakthrough={breakthrough}, core_passive={core_passive}")

        if character_id is None or character_id == -1:
            self.logger.info("清空角色选择")
            self.state.clear_all()
            return

        character = self.data_manager.get_character(character_id)
        if not character:
            self.logger.error(f"未找到角色: {character_id}")
            return

        self.logger.info(f"找到角色: {character.name} (ID: {character.id})")

        # 更新角色信息
        if character.level != level:
            self.logger.debug(f"更新角色等级: {character.level} -> {level}")
            character.level = level
        if character.breakthrough != breakthrough:
            self.logger.debug(f"更新角色突破等级: {character.breakthrough} -> {breakthrough}")
            character.breakthrough = breakthrough
        if character.core_passive != core_passive:
            self.logger.debug(f"更新角色核心被动: {character.core_passive} -> {core_passive}")
            character.core_passive = core_passive

        # 更新状态管理器
        self.state.update_character(character)
        self.logger.info(f"设置当前角色: {character.name}")

        # 更新角色对象中的武器ID
        if self.state.get_state().current_weapon:
            if character.weapon_id != self.state.get_state().current_weapon.id:
                self.logger.debug(f"更新角色武器ID: {character.weapon_id} -> {self.state.get_state().current_weapon.id}")
                character.weapon_id = self.state.get_state().current_weapon.id

        # 角色变化时：计算并更新所有属性
        self.logger.debug("开始计算属性")
        self._calculate_and_update_all()

    def set_weapon(self, weapon_id: Union[int, None], level: int = 60,
                   refinement: int = 5, talent: int = 1, flag=None):
        """设置当前武器"""
        self.logger.debug(f"设置武器: id={weapon_id}, level={level}, refinement={refinement}, talent={talent}")

        if weapon_id is None or weapon_id == -1:
            self.logger.info("清空音擎选择")
            return

        weapon = self.data_manager.get_weapon(weapon_id)
        if not weapon:
            self.logger.error(f"未找到武器: {weapon_id}")
            return

        self.logger.info(f"找到武器: {weapon.name} (ID: {weapon.id})")

        # 更新武器信息
        if weapon.level != level:
            self.logger.debug(f"更新武器等级: {weapon.level} -> {level}")
            weapon.level = level
        if weapon.refinement != refinement:
            self.logger.debug(f"更新武器突破等级: {weapon.refinement} -> {refinement}")
            weapon.refinement = refinement
        if weapon.talent != talent:
            self.logger.debug(f"更新武器天赋等级: {weapon.talent} -> {talent}")
            weapon.talent = talent

        if flag:
            self.logger.debug("设置武器数据计算标志为False")
            weapon.data_calculation_flag = False

        # 更新状态管理器
        self.state.update_weapon(weapon)
        self.logger.info(f"设置当前武器: {weapon.name}")

        # 更新角色对象中的武器ID
        current_state = self.state.get_state()
        if current_state.current_character:
            if current_state.current_character.weapon_id != weapon.id:
                self.logger.debug(f"更新角色武器ID: {current_state.current_character.weapon_id} -> {weapon.id}")
                current_state.current_character.weapon_id = weapon.id

        # 武器变化时：计算并更新所有属性
        self.logger.debug("开始计算属性")
        self._calculate_and_update_all()

    def set_gear_sets(self, set_ids: list):
        """设置驱动盘套装"""
        self.logger.debug(f"设置驱动盘套装: set_ids={set_ids}")

        self.state.clear_gear_sets()

        # 加载新套装
        gear_sets = {}
        if set_ids:
            for set_id in set_ids:
                if not set_id:  # 跳过空ID
                    continue
                gear_set = self.data_manager.get_gear_set(set_id)
                if gear_set:
                    self.logger.info(f"找到驱动盘套装: {gear_set.name} (ID: {set_id})")
                    gear_sets[set_id] = gear_set
                else:
                    self.logger.warning(f"未找到驱动盘套装: ID={set_id}")

        # 更新状态管理器
        self.state.update_gear_sets(gear_sets)

        # 驱动盘变化时：只计算完整属性
        self.logger.debug("开始计算属性")
        self._calculate_and_update_all()

    def set_gear_piece(self, position: int, main_attribute=None, sub_attributes=None):
        """设置单个驱动盘 - 合并更新而非覆盖"""
        self.logger.debug(f"设置驱动盘: position={position}, main_attribute={main_attribute}, sub_attributes={sub_attributes}")

        # 获取现有的驱动盘（如果有）
        current_state = self.state.get_state()
        if position in current_state.current_gear_pieces:
            gear_piece = current_state.current_gear_pieces[position]
            self.logger.debug(f"找到驱动盘: position: {position}")
        else:
            gear_piece = GearPiece(position=position)
            self.logger.debug(f"创建驱动盘: position: {position}")

        # 只更新提供的属性，不覆盖未提供的
        if main_attribute:
            gear_piece.main_attribute = main_attribute

        if sub_attributes:
            # 更新指定的副属性，保留其他的
            gear_piece.sub_attributes.update(sub_attributes)
            # 如果传入空字典，表示清除该副属性
            for slot, attr in list(gear_piece.sub_attributes.items()):
                if attr is None:
                    del gear_piece.sub_attributes[slot]

        # 更新状态管理器
        self.state.update_gear_piece(position, gear_piece)

        # 更新角色对象
        current_state = self.state.get_state()
        if current_state.current_character:
            if position not in current_state.current_character.gear_pieces:
                current_state.current_character.gear_pieces[position] = {'main': None, 'subs': {}}

            if main_attribute:
                current_state.current_character.gear_pieces[position]['main'] = main_attribute

            if sub_attributes:
                for slot, attr in sub_attributes.items():
                    if attr:
                        current_state.current_character.gear_pieces[position]['subs'][slot] = attr
                    elif slot in current_state.current_character.gear_pieces[position]['subs']:
                        del current_state.current_character.gear_pieces[position]['subs'][slot]

        # 驱动盘变化时：只计算完整属性
        self.logger.debug("开始计算属性")
        self._calculate_and_update_character_only()

    def _calculate_and_update_all(self):
        """计算并更新所有属性（角色/武器变化时调用）"""
        current_state = self.state.get_state()
        if not current_state.current_character:
            self.logger.warning("没有当前角色，跳过计算")
            return

        # 获取显示设置
        settings = settings_manager.get_settings()
        display_mode = settings.display.character_attribute_display_mode

        self.logger.debug(f"显示模式: {display_mode} (1=面板属性, 2=局内属性)")
        self.logger.debug(f"显示基础属性区域: {settings.display.show_basic_attributes_section}")

        # 1. 计算基础属性（仅角色+武器基础属性）
        current_state = self.state.get_state()
        if current_state.current_weapon:
            self.logger.debug(f"计算带武器的属性，武器: {current_state.current_weapon.name}")
            base_attributes = self.calculator.calculate_with_weapon(
                current_state.current_character,
                current_state.current_weapon,
                include_talent=False  # 不包含天赋属性
            )
        else:
            self.logger.debug("计算仅角色的属性")
            base_attributes = self.calculator.calculate_character_only(
                current_state.current_character
            )

        # 根据设置决定是否发送基础属性更新信号
        if settings.display.show_basic_attributes_section:
            self.logger.debug("基础属性区域显示已启用，发射 base_attributes_updated 信号")
            self.base_attributes_updated.emit(base_attributes)
        else:
            self.logger.debug("基础属性区域显示已禁用")

        # 2. 计算角色属性（根据显示模式决定是否包含天赋属性）
        has_gear = bool(current_state.current_gear_sets or current_state.current_gear_pieces)

        if has_gear or display_mode == 2:
            # 如果有驱动盘配置或者显示局内属性，需要计算完整属性
            self.logger.debug("计算完整角色属性")

            # 根据显示模式决定是否包含天赋属性
            include_talent = (display_mode == 2)  # 模式2包含天赋属性

            character_attributes = self.calculator.calculate(
                character=current_state.current_character,
                weapon=current_state.current_weapon,
                gear_sets=current_state.current_gear_sets,
                gear_pieces=current_state.current_gear_pieces,
                include_talent=include_talent
            )

            self.logger.debug("发射 character_attributes_updated 信号")
            self.character_attributes_updated.emit(character_attributes)
        else:
            # 没有驱动盘配置且显示面板属性，使用基础属性
            self.logger.debug("无驱动盘配置且显示面板属性，使用基础属性")
            self.character_attributes_updated.emit(base_attributes.copy())

    def _calculate_and_update_character_only(self):
        """只计算完整属性（驱动盘变化时调用）"""
        current_state = self.state.get_state()
        if not current_state.current_character:
            return

        # 获取显示设置
        settings = settings_manager.get_settings()
        display_mode = settings.display.character_attribute_display_mode
        include_talent = (display_mode == 2)  # 模式2包含天赋属性

        # 计算完整属性
        character_attributes = self.calculator.calculate(
            character=current_state.current_character,
            weapon=current_state.current_weapon,
            gear_sets=current_state.current_gear_sets,
            gear_pieces=current_state.current_gear_pieces,
            include_talent=include_talent
        )

        # 总是发送更新信号
        self.character_attributes_updated.emit(character_attributes)

    def calculate_and_update(self):
        """兼容原有接口，调用全量更新"""
        self._calculate_and_update_all()

    def clear_all(self):
        """清空所有选择"""
        self.state.clear_all()

        # 发送空的属性更新
        self.base_attributes_updated.emit({})
        self.character_attributes_updated.emit({})

        self.logger.info("已清空所有选择")