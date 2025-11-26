from typing import Dict, Any


class BaseConfig:
    """配置基类"""

    def validate(self) -> bool:
        """验证配置完整性"""
        return True

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}