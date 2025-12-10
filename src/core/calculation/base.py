# src/core/calculation/base.py
"""计算策略基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from src.core.models.character import CharacterSchema, CharacterBaseStats


class CalculationStrategy(ABC):
    """计算策略基类"""
    @abstractmethod
    def calculate(self, context: 'CalculationContext') -> 'BaseStats':
        """执行计算"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取策略名称"""
        pass

    def debug(self, message: str):
        """调试输出"""
        print(f"[DEBUG-{self.get_name()}] {message}")


@dataclass
class CalculationContext:
    """计算上下文"""
    schema: CharacterSchema
    level: int = 1
    breakthrough_level: int = 0
    core_passive_level: int = 1
    base_stats: Optional[CharacterBaseStats] = None

    def get_cache_key(self) -> str:
        """生成缓存键"""
        return f"L{self.level}_B{self.breakthrough_level}_C{self.core_passive_level}"

    def debug_info(self) -> str:
        """获取调试信息"""
        return (f"角色: {self.schema.name}(ID:{self.schema.character_id}), "
                f"等级:{self.level}, 突破:{self.breakthrough_level}, 核心技:{self.core_passive_level}")