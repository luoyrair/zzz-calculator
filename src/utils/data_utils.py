"""
数据处理工具函数
"""

from typing import Dict, Any


class DataUtils:
    """数据工具类"""

    @staticmethod
    def sanitize_json_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗JSON数据"""
        # 移除空值
        sanitized = {k: v for k, v in data.items() if v is not None}

        # 确保必要字段存在
        if 'id' not in sanitized:
            sanitized['id'] = 0
        if '名称' not in sanitized:
            sanitized['名称'] = '未知'

        return sanitized

    @staticmethod
    def normalize_value(value: Any, value_type: str = 'float') -> Any:
        """规范化数值"""
        if value_type == 'float':
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        elif value_type == 'int':
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0
        elif value_type == 'percent':
            try:
                val = float(value)
                return val / 100.0 if val > 1 else val  # 处理百分数和分数
            except (ValueError, TypeError):
                return 0.0
        return value
