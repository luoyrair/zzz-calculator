# src/utils/cache.py
"""缓存管理器"""
from typing import Dict, Any, Optional


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        return self._cache.get(key)

    def set(self, key: str, value: Any):
        """设置缓存值"""
        self._cache[key] = value

    def delete(self, key: str):
        """删除缓存值"""
        self._cache.pop(key, None)

    def clear(self):
        """清空缓存"""
        self._cache.clear()

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return key in self._cache