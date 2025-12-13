# src/__init__.py
"""绝区零属性计算器"""
from src.data.manager import data_manager
from src.services.calculation_service import calculation_service

__version__ = "1.0.0"
__all__ = ['data_manager', 'calculation_service']