"""设置配置 - 使用单例模式"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any


@dataclass
class LevelConstraintSettings:
    """等级约束设置"""

    # 角色等级约束模式
    # 1: 默认模式（等级变化时，突破等级设置为等级最小值小于等于等级的最大等级最小值对应的突破等级）
    # 2: 模式2（等级变化时，突破等级设置为等级最大值大于等于等级且等级大于等级最大值的等级最小值的等级最大值对应的突破等级）
    # 3: 模式3（当等级由小于突破等级的等级最大值的等级变为等级最大值时，突破等级不变化，但当等级是突破等级的等级最大级时，再进行升级则突破等级+1）
    character_level_constraint_mode: int = 1

    # 突破等级约束模式
    # 1: 默认模式（突破等级变化时，等级设置为突破等级的等级最大值）
    # 2: 模式2（突破等级变化时，等级设置为突破等级的等级最小值）
    breakthrough_constraint_mode: int = 1


@dataclass
class AutoSelectSettings:
    """自动选择设置"""

    # 选择角色时自动选择专属音擎
    auto_select_weapon: bool = True

    # 使用原始推荐数据设置角色的推荐数据
    use_original_recommendations: bool = True


@dataclass
class DisplaySettings:
    """显示设置"""

    # 角色属性显示模式
    # 1: 显示角色面板属性（不包含音擎天赋属性）
    # 2: 显示角色局内属性（包含音擎天赋属性）
    character_attribute_display_mode: int = 1

    # 是否显示角色基础属性区域
    show_basic_attributes_section: bool = False  # 默认不显示

    # 属性显示内容模式
    # 1: 显示角色基础属性（根据角色类型显示对应的属性）
    # 2: 显示所有属性
    basic_attributes_display_mode: int = 1  # 默认显示角色基础属性


@dataclass
class AppSettings:
    """应用设置"""

    # 等级约束设置
    level_constraints: LevelConstraintSettings = None

    # 自动选择设置
    auto_select: AutoSelectSettings = None

    # 显示设置
    display: DisplaySettings = None

    def __post_init__(self):
        if self.level_constraints is None:
            self.level_constraints = LevelConstraintSettings()
        if self.auto_select is None:
            self.auto_select = AutoSelectSettings()
        if self.display is None:
            self.display = DisplaySettings()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'level_constraints': asdict(self.level_constraints),
            'auto_select': asdict(self.auto_select),
            'display': asdict(self.display)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """从字典创建"""
        settings = cls()
        if 'level_constraints' in data:
            settings.level_constraints = LevelConstraintSettings(**data['level_constraints'])
        if 'auto_select' in data:
            settings.auto_select = AutoSelectSettings(**data['auto_select'])
        if 'display' in data:
            settings.display = DisplaySettings(**data['display'])
        return settings


class SettingsManager:
    """设置管理器单例"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.data_dir = Path(__file__).parent.parent.parent / 'data'
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.app_dir = self.data_dir / 'app'
            self.app_dir.mkdir(parents=True, exist_ok=True)
            self.settings_file = self.app_dir / 'settings.json'
            print(self.settings_file)
            self.settings = self._load_settings()
            self.one_run_create_settings()
            self._initialized = True

    def _load_settings(self) -> AppSettings:
        """加载设置"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AppSettings.from_dict(data)
            except Exception as e:
                print(f"加载设置失败: {e}")

        # 返回默认设置
        return AppSettings()

    def save_settings(self):
        """保存设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存设置失败创建: {e}")
            return False

    def one_run_create_settings(self):
        """<UNK>"""
        if not self.settings_file.exists():
            print(f"设置文件不存在, 创建默认设置文件")
            self.save_settings()
        else:
            print(f"设置文件存在, 使用存在的设置文件")

    def get_settings(self) -> AppSettings:
        """获取当前设置"""
        return self.settings

    def update_settings(self, new_settings: AppSettings):
        """更新设置"""
        self.settings = new_settings
        self.save_settings()

    def refresh(self):
        """重新加载设置文件（用于热更新）"""
        self.settings = self._load_settings()


# 创建全局实例
settings_manager = SettingsManager()