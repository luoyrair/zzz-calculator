"""简化版应用核心"""

from typing import Optional, Dict
from PyQt6.QtCore import QObject, pyqtSignal
from .models import Character, Weapon, GearSet, GearPiece
from .calculator import AttributeCalculator
from .data_manager import SimpleDataManager


class ApplicationCore(QObject):
    """应用核心 - 连接UI和数据层"""

    # 信号定义
    character_changed: pyqtSignal = pyqtSignal(Character)
    weapon_changed: pyqtSignal = pyqtSignal(Weapon)
    gear_set_changed: pyqtSignal = pyqtSignal(list)  # [set_id1, set_id2]
    gear_piece_changed: pyqtSignal = pyqtSignal(int, GearPiece)  # position
    base_attributes_updated: pyqtSignal = pyqtSignal(dict)  # 基础属性更新信号
    character_attributes_updated: pyqtSignal = pyqtSignal(dict)  # 角色属性更新信号

    def __init__(self):
        super().__init__()
        print("[DEBUG AppCore] ApplicationCore 初始化开始")
        self.data_manager = SimpleDataManager()
        self.calculator = AttributeCalculator(self.data_manager)

        # 当前状态
        self.current_character: Optional[Character] = None
        self.current_weapon: Optional[Weapon] = None
        self.current_gear_sets: Dict[str, GearSet] = {}
        self.current_gear_pieces: Dict[int, GearPiece] = {}

        # 记录上次触发状态，避免重复触发
        self._last_base_attributes = None
        self._last_character_attributes = None

        # 加载数据
        self._load_data()
        print("[DEBUG AppCore] ApplicationCore 初始化完成")

    def _load_data(self):
        """加载数据"""
        print("[DEBUG AppCore] 开始加载数据")
        if not self.data_manager.load_all():
            print("[ERROR AppCore] 数据加载失败")
        else:
            print("[DEBUG AppCore] 数据加载成功")

    def set_character(self, character_id: int, level: int = 60,
                      breakthrough: int = 6, core_passive: int = 7):
        """设置当前角色"""
        print(
            f"[DEBUG AppCore] set_character 调用开始: id={character_id}, level={level}, breakthrough={breakthrough}, core_passive={core_passive}")

        # 检查递归调用
        import traceback
        stack = traceback.extract_stack()
        print(f"[DEBUG AppCore] 调用栈深度: {len(stack)}")
        if len(stack) > 50:
            print("[WARNING AppCore] 调用栈深度超过50，可能存在递归")
            for i, frame in enumerate(stack[-10:]):
                print(f"  Frame {i}: {frame.filename}:{frame.lineno} in {frame.name}")

        character = self.data_manager.get_character(character_id)
        if not character:
            print(f"[ERROR AppCore] 未找到角色: {character_id}")
            return

        print(f"[DEBUG AppCore] 找到角色: {character.name} (ID: {character.id})")

        # 更新角色信息
        if character.level != level:
            print(f"[DEBUG AppCore] 更新角色等级: {character.level} -> {level}")
            character.level = level
        if character.breakthrough != breakthrough:
            print(f"[DEBUG AppCore] 更新角色突破等级: {character.breakthrough} -> {breakthrough}")
            character.breakthrough = breakthrough
        if character.core_passive != core_passive:
            print(f"[DEBUG AppCore] 更新角色核心被动: {character.core_passive} -> {core_passive}")
            character.core_passive = core_passive

        self.current_character = character
        print(f"[DEBUG AppCore] 设置当前角色: {character.name}")

        # 更新角色对象中的武器ID
        if self.current_weapon:
            if character.weapon_id != self.current_weapon.id:
                print(f"[DEBUG AppCore] 更新角色武器ID: {character.weapon_id} -> {self.current_weapon.id}")
                character.weapon_id = self.current_weapon.id

        # 发出信号
        print("[DEBUG AppCore] 发射 character_changed 信号")
        self.character_changed.emit(character)

        # 角色变化时：计算并更新所有属性
        print("[DEBUG AppCore] 开始计算属性")
        self._calculate_and_update_all()
        print("[DEBUG AppCore] set_character 调用完成")

    def set_weapon(self, weapon_id: int, level: int = 60,
                   refinement: int = 5, talent: int = 1, flag=None):
        """设置当前武器"""
        print(
            f"[DEBUG AppCore] set_weapon 调用开始: id={weapon_id}, level={level}, refinement={refinement}, talent={talent}")

        weapon = self.data_manager.get_weapon(weapon_id)
        if not weapon:
            print(f"[ERROR AppCore] 未找到武器: {weapon_id}")
            return

        print(f"[DEBUG AppCore] 找到武器: {weapon.name} (ID: {weapon.id})")

        # 更新武器信息
        if weapon.level != level:
            print(f"[DEBUG AppCore] 更新武器等级: {weapon.level} -> {level}")
            weapon.level = level
        if weapon.refinement != refinement:
            print(f"[DEBUG AppCore] 更新武器突破等级: {weapon.refinement} -> {refinement}")
            weapon.refinement = refinement
        if weapon.talent != talent:
            print(f"[DEBUG AppCore] 更新武器天赋等级: {weapon.talent} -> {talent}")
            weapon.talent = talent

        if flag:
            print("[DEBUG AppCore] 设置武器数据计算标志为False")
            weapon.data_calculation_flag = False

        self.current_weapon = weapon
        print(f"[DEBUG AppCore] 设置当前武器: {weapon.name}")

        # 更新角色对象中的武器ID
        if self.current_character:
            if self.current_character.weapon_id != weapon.id:
                print(f"[DEBUG AppCore] 更新角色武器ID: {self.current_character.weapon_id} -> {weapon.id}")
                self.current_character.weapon_id = weapon.id

        # 发出信号
        print("[DEBUG AppCore] 发射 weapon_changed 信号")
        self.weapon_changed.emit(weapon)

        # 武器变化时：计算并更新所有属性
        print("[DEBUG AppCore] 开始计算属性")
        self._calculate_and_update_all()
        print("[DEBUG AppCore] set_weapon 调用完成")

    def set_gear_sets(self, set_ids: list):
        """设置驱动盘套装"""
        # 清空当前套装
        self.current_gear_sets.clear()

        # 加载新套装
        if set_ids:
            for set_id in set_ids:
                gear_set = self.data_manager.get_gear_set(set_id)
                if gear_set:
                    self.current_gear_sets[set_id] = gear_set

        # 更新角色对象中的套装ID
        if self.current_character:
            self.current_character.gear_set_ids = set_ids

        # 发出信号
        self.gear_set_changed.emit(set_ids)

        # 驱动盘变化时：只计算完整属性
        self._calculate_and_update_character_only()

    def set_gear_piece(self, position: int, main_attribute=None, sub_attributes=None):
        """设置单个驱动盘 - 合并更新而非覆盖"""
        # 获取现有的驱动盘（如果有）
        if position in self.current_gear_pieces:
            gear_piece = self.current_gear_pieces[position]
        else:
            gear_piece = GearPiece(position=position)

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

        self.current_gear_pieces[position] = gear_piece

        # 更新角色对象
        if self.current_character:
            if position not in self.current_character.gear_pieces:
                self.current_character.gear_pieces[position] = {'main': None, 'subs': {}}

            if main_attribute:
                self.current_character.gear_pieces[position]['main'] = main_attribute

            if sub_attributes:
                for slot, attr in sub_attributes.items():
                    if attr:
                        self.current_character.gear_pieces[position]['subs'][slot] = attr
                    elif slot in self.current_character.gear_pieces[position]['subs']:
                        del self.current_character.gear_pieces[position]['subs'][slot]

        # 发出信号
        self.gear_piece_changed.emit(position, gear_piece)

        # 驱动盘变化时：只计算完整属性
        self._calculate_and_update_character_only()

    def _calculate_and_update_all(self):
        """计算并更新所有属性（角色/武器变化时调用）"""
        print("[DEBUG AppCore] _calculate_and_update_all 开始")
        if not self.current_character:
            print("[WARNING AppCore] 没有当前角色，跳过计算")
            return

        # 1. 计算基础属性（仅角色+武器）
        print("[DEBUG AppCore] 计算基础属性")
        if self.current_weapon:
            print(f"[DEBUG AppCore] 计算带武器的属性，武器: {self.current_weapon.name}")
            base_attributes = self.calculator.calculate_with_weapon(
                self.current_character,
                self.current_weapon
            )
        else:
            print("[DEBUG AppCore] 计算仅角色的属性")
            base_attributes = self.calculator.calculate_character_only(
                self.current_character
            )

        # 避免重复触发相同属性
        print("[DEBUG AppCore] 检查是否需要发射 base_attributes_updated 信号")
        if base_attributes != self._last_base_attributes:
            print("[DEBUG AppCore] 属性有变化，发射 base_attributes_updated 信号")
            self.base_attributes_updated.emit(base_attributes)
            self._last_base_attributes = base_attributes.copy()
        else:
            print("[DEBUG AppCore] 属性未变化，跳过信号发射")

        # 2. 如果有驱动盘配置，计算完整属性
        print("[DEBUG AppCore] 检查是否有驱动盘配置")
        has_gear = bool(self.current_gear_sets or self.current_gear_pieces)
        if has_gear:
            print("[DEBUG AppCore] 有驱动盘配置，计算完整属性")
            character_attributes = self.calculator.calculate(
                character=self.current_character,
                weapon=self.current_weapon,
                gear_sets=self.current_gear_sets,
                gear_pieces=self.current_gear_pieces
            )

            # 避免重复触发相同属性
            print("[DEBUG AppCore] 检查是否需要发射 character_attributes_updated 信号")
            if character_attributes != self._last_character_attributes:
                print("[DEBUG AppCore] 属性有变化，发射 character_attributes_updated 信号")
                self.character_attributes_updated.emit(character_attributes)
                self._last_character_attributes = character_attributes.copy()
            else:
                print("[DEBUG AppCore] 属性未变化，跳过信号发射")
        else:
            print("[DEBUG AppCore] 无驱动盘配置，跳过完整属性计算")

        print("[DEBUG AppCore] _calculate_and_update_all 完成")

    def _calculate_and_update_character_only(self):
        """只计算完整属性（驱动盘变化时调用）"""
        if not self.current_character:
            return

        # 只计算完整属性
        character_attributes = self.calculator.calculate(
            character=self.current_character,
            weapon=self.current_weapon,
            gear_sets=self.current_gear_sets,
            gear_pieces=self.current_gear_pieces
        )

        # 避免重复触发相同属性
        if character_attributes != self._last_character_attributes:
            self.character_attributes_updated.emit(character_attributes)
            self._last_character_attributes = character_attributes.copy()

    def calculate_and_update(self):
        """兼容原有接口，调用全量更新"""
        self._calculate_and_update_all()

    def clear_all(self):
        """清空所有选择"""
        self.current_character = None
        self.current_weapon = None
        self.current_gear_sets.clear()
        self.current_gear_pieces.clear()
        self._last_base_attributes = None
        self._last_character_attributes = None
        self.calculator.clear_cache()
        print("已清空所有选择")