# src/config/file_config.py
"""文件路径配置管理器"""
from pathlib import Path
from typing import Dict, Any

from .base_config import BaseConfig


class FileConfig(BaseConfig):
    """文件路径配置"""

    def __init__(self, base_dir: str = "./data"):
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent
        self.base_dir = project_root / base_dir
        self._ensure_directories()

    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.base_dir,
            self.characters_dir,
            self.backup_dir,
            self.cache_dir,
            self.equipment_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def characters_dir(self) -> Path:
        """角色数据目录"""
        return self.base_dir / "characters"

    @property
    def equipment_dir(self) -> Path:
        """装备数据目录"""
        return self.base_dir / "equipment"

    @property
    def backup_dir(self) -> Path:
        """备份目录"""
        return self.base_dir / "backups"

    @property
    def cache_dir(self) -> Path:
        """缓存目录"""
        return self.base_dir / "cache"

    @property
    def character_ids_file(self) -> Path:
        """角色ID列表文件"""
        return self.base_dir / "character_ids.json"

    @property
    def equipment_ids_file(self) -> Path:
        """装备ID列表文件"""
        return self.base_dir / "equipment_ids.json"

    @property
    def id_name_mapping_file(self) -> Path:
        """ID-名称映射文件"""
        return self.base_dir / "id_name_mapping.json"

    @property
    def equipment_file(self) -> Path:
        """装备数据文件"""
        return self.equipment_dir / "equipment.json"

    @property
    def failed_downloads_file(self) -> Path:
        """失败下载记录文件"""
        return self.base_dir / "failed_downloads.json"

    def get_character_file_path(self, character_id: str) -> Path:
        """获取角色数据文件路径"""
        return self.characters_dir / f"{character_id}.json"

    def get_backup_path(self, backup_name: str) -> Path:
        """获取备份路径"""
        return self.backup_dir / backup_name

    def get_cache_file_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.json"

    def list_character_files(self) -> list[Path]:
        """列出所有角色数据文件"""
        return list(self.characters_dir.glob("*.json"))

    def character_file_exists(self, character_id: str) -> bool:
        """检查角色文件是否存在"""
        return self.get_character_file_path(character_id).exists()

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """获取文件信息"""
        stat = file_path.stat()
        return {
            "path": str(file_path),
            "size": stat.st_size,
            "modified_time": stat.st_mtime,
            "exists": file_path.exists()
        }

    def validate_data_structure(self) -> Dict[str, Any]:
        """验证数据目录结构完整性"""
        result = {
            "valid": True,
            "missing_dirs": [],
            "missing_files": [],
            "details": {}
        }

        # 检查目录
        required_dirs = [
            ("base_dir", self.base_dir),
            ("characters_dir", self.characters_dir),
            ("equipment_dir", self.equipment_dir),
            ("backup_dir", self.backup_dir),
            ("cache_dir", self.cache_dir)
        ]

        for name, directory in required_dirs:
            exists = directory.exists()
            result["details"][name] = {
                "path": str(directory),
                "exists": exists
            }
            if not exists:
                result["missing_dirs"].append(name)
                result["valid"] = False

        return result

    def change_base_directory(self, new_base_dir: str):
        """更改基础目录"""
        project_root = Path(__file__).parent.parent.parent
        self.base_dir = project_root / new_base_dir
        self._ensure_directories()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "base_dir": str(self.base_dir),
            "characters_dir": str(self.characters_dir),
            "equipment_dir": str(self.equipment_dir),
            "backup_dir": str(self.backup_dir),
            "cache_dir": str(self.cache_dir),
            "character_ids_file": str(self.character_ids_file),
            "id_name_mapping_file": str(self.id_name_mapping_file),
            "equipment_file": str(self.equipment_file),
            "failed_downloads_file": str(self.failed_downloads_file)
        }

    def validate(self) -> bool:
        """验证配置完整性"""
        try:
            structure = self.validate_data_structure()
            return structure["valid"]
        except Exception as e:
            print(f"文件配置验证失败: {e}")
            return False