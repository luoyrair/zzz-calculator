# src/core/service_factory.py
"""服务工厂 - 适配新架构"""
from typing import Optional

from src.config import config_manager
from src.services.character import CharacterService
from src.services.weapon import WeaponService
from src.core.calculator import GearCalculator
from src.ui.character_manager import CharacterManager


class ServiceFactory:
    """服务工厂 - 统一管理服务实例的创建"""

    def __init__(self):
        self._character_service: Optional[CharacterService] = None
        self._weapon_service: Optional[WeaponService] = None
        self._gear_calculator: Optional[GearCalculator] = None
        self._character_manager: Optional[CharacterManager] = None

    @property
    def character_service(self) -> CharacterService:
        """获取角色服务"""
        if self._character_service is None:
            self._character_service = CharacterService(config_manager)
        return self._character_service

    @property
    def weapon_service(self) -> WeaponService:
        """获取音擎服务"""
        if self._weapon_service is None:
            self._weapon_service = WeaponService(config_manager)
        return self._weapon_service

    @property
    def gear_calculator(self) -> GearCalculator:
        """获取驱动盘计算器"""
        if self._gear_calculator is None:
            self._gear_calculator = GearCalculator(config_manager.gear)
        return self._gear_calculator

    @property
    def character_manager(self) -> CharacterManager:
        """获取角色管理器"""
        if self._character_manager is None:
            self._character_manager = CharacterManager()
        return self._character_manager

    def clear_cache(self):
        """清空所有缓存"""
        if self._character_service:
            self._character_service.clear_cache()
        if self._weapon_service:
            self._weapon_service.clear_cache()
        if self._gear_calculator and hasattr(self._gear_calculator, 'clear_cache'):
            self._gear_calculator.clear_cache()


# 全局服务工厂实例
_service_factory = ServiceFactory()


def get_service_factory() -> ServiceFactory:
    """获取服务工厂单例"""
    return _service_factory
