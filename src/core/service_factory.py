# src/core/service_factory.py
"""服务工厂 - 解决循环导入问题"""
from typing import Optional

from src.config import config_manager
from .async_loader import CharacterLoader, CharacterManager
from .calculator import GearCalculator
from .character_calculator import CharacterCalculator


class ServiceFactory:
    """服务工厂 - 统一管理服务实例的创建"""

    def __init__(self):
        self._character_loader: Optional[CharacterLoader] = None
        self._character_manager: Optional[CharacterManager] = None
        self._character_calculator: Optional[CharacterCalculator] = None
        self._gear_calculator = None

    @property
    def character_loader(self) -> CharacterLoader:
        """获取角色加载器"""
        if self._character_loader is None:
            self._character_loader = CharacterLoader(use_async=True)
        return self._character_loader

    @property
    def character_manager(self) -> CharacterManager:
        """获取角色管理器"""
        if self._character_manager is None:
            self._character_manager = CharacterManager()
        return self._character_manager

    @property
    def character_calculator(self) -> CharacterCalculator:
        """获取角色计算器"""
        if self._character_calculator is None:
            self._character_calculator = CharacterCalculator(
                self.character_loader, config_manager
            )
        return self._character_calculator

    @property
    def gear_calculator(self):
        """获取驱动盘计算器"""
        if self._gear_calculator is None:
            self._gear_calculator = GearCalculator(
                config_manager.gear
            )
        return self._gear_calculator

    def clear_cache(self):
        """清空所有缓存"""
        if self._character_calculator:
            self._character_calculator.clear_cache()
        if self._gear_calculator and hasattr(self._gear_calculator, 'clear_cache'):
            self._gear_calculator.clear_cache()

    def shutdown(self):
        """关闭所有服务"""
        if self._character_loader:
            self._character_loader.shutdown()


# 全局服务工厂实例
_service_factory = ServiceFactory()


def get_service_factory() -> ServiceFactory:
    """获取服务工厂单例"""
    return _service_factory