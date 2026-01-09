"""
数据处理工具函数
"""

import json
from typing import Dict, List, Any, Union
from pathlib import Path


class DataUtils:
    """数据工具类"""

    @staticmethod
    def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
        """深度合并两个字典"""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DataUtils.deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        return result

    @staticmethod
    def sanitize_json_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗JSON数据"""
        # 移除空值
        sanitized = {k: v for k, v in data.items() if v is not None}

        # 确保必要字段存在
        if 'Id' not in sanitized:
            sanitized['Id'] = 0
        if 'Name' not in sanitized:
            sanitized['Name'] = '未知'

        return sanitized

    @staticmethod
    def extract_by_pattern(text: str, patterns: List[Union[str, Dict]]) -> List[Dict[str, Any]]:
        """根据多个模式从文本中提取信息"""
        import re
        results = []

        for pattern in patterns:
            if isinstance(pattern, dict):
                regex = pattern.get('pattern', '')
                name = pattern.get('name', '')
                match = re.search(regex, text)
                if match:
                    results.append({
                        'name': name,
                        'match': match.group(),
                        'groups': match.groups()
                    })
            elif isinstance(pattern, str):
                matches = re.findall(pattern, text)
                for match in matches:
                    results.append({
                        'pattern': pattern,
                        'match': match
                    })

        return results

    @staticmethod
    def ensure_dir_exists(directory: Union[str, Path]) -> Path:
        """确保目录存在，如果不存在则创建"""
        if isinstance(directory, str):
            directory = Path(directory)

        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @staticmethod
    def load_json_file(file_path: Union[str, Path], default: Any = None) -> Any:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    @staticmethod
    def save_json_file(file_path: Union[str, Path], data: Any, indent: int = 2) -> bool:
        """保存数据到JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            return True
        except (IOError, TypeError):
            return False

    @staticmethod
    def filter_data_by_conditions(data_list: List[Dict], conditions: Dict[str, Any]) -> List[Dict]:
        """根据条件过滤数据列表"""
        filtered = []
        for item in data_list:
            match = True
            for key, value in conditions.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(item)
        return filtered

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