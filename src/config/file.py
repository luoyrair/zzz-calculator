"""文件路径配置"""
from pathlib import Path


class FileConfig:
    """文件路径配置"""

    def __init__(self, base_dir: str = "./data"):
        project_root = Path(__file__).parent.parent.parent
        self.base_dir = project_root / base_dir
        self._ensure_directories()

    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        directories = [
            self.base_dir,
            self.characters_dir,
            self.weapons_dir,
            self.equipment_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def characters_dir(self) -> Path:
        return self.base_dir / "characters"

    @property
    def weapons_dir(self) -> Path:
        return self.base_dir / "weapons"

    @property
    def equipment_dir(self) -> Path:
        return self.base_dir / "equipment"

    @property
    def character_ids_file(self) -> Path:
        """角色ID列表文件"""
        return self.base_dir / "character_ids.json"

    @property
    def weapon_ids_file(self) -> Path:
        """音擎ID列表文件"""
        return self.base_dir / "weapon_ids.json"

    @property
    def equipment_ids_file(self) -> Path:
        """装备ID列表文件"""
        return self.base_dir / "equipment_ids.json"

    @property
    def character_id_name_mapping_file(self) -> Path:
        """角色ID-名称映射文件"""
        return self.base_dir / "character_id_name_mapping.json"

    @property
    def weapon_id_name_mapping_file(self) -> Path:
        """音擎ID-名称映射文件"""
        return self.base_dir / "weapon_id_name_mapping.json"

    @property
    def equipment_file(self) -> Path:
        """装备数据文件"""
        return self.equipment_dir / "equipment.json"

    @property
    def failed_downloads_file(self) -> Path:
        """失败下载记录文件"""
        return self.base_dir / "failed_downloads.json"

    def get_character_file_path(self, character_id: str) -> Path:
        return self.characters_dir / f"{character_id}.json"

    def get_weapon_file_path(self, weapon_id: str) -> Path:
        return self.weapons_dir / f"{weapon_id}.json"

    def list_character_files(self) -> list[Path]:
        """列出所有角色数据文件"""
        return list(self.characters_dir.glob("*.json"))

    def character_file_exists(self, character_id: str) -> bool:
        """检查角色文件是否存在"""
        return self.get_character_file_path(character_id).exists()