# ===== src/core/runtime_data_loader.py =====
"""运行时数据加载器 - 仅读取预生成的缓存文件"""
import dill
from dataclasses import dataclass
from typing import Dict, Optional, Any

from src.config.constants import PathConstants
from src.core.models import Character, Weapon, GearSet
from src.utils.logger import get_logger

logger = get_logger("runtime_data_loader")


@dataclass
class RuntimeData:
    """运行时数据容器"""
    characters: Dict[int, Any]  # 角色解析数据
    weapons: Dict[int, Any]  # 武器解析数据
    gear_sets: Dict[str, Any]  # 驱动盘套装数据
    weapon_growth: Dict[str, Any]  # 武器成长数据


class RuntimeDataLoader:
    """运行时数据加载器 - 仅读取预生成的缓存文件"""

    def __init__(self):
        """初始化数据加载器"""
        self.data_dir = PathConstants.get_data_dir()

        self.characters: Dict[int, Character] = {}
        self.weapons: Dict[int, Weapon] = {}
        self.weapon_growth_data: Dict[str, Weapon] = {}
        self.gear_sets: Dict[str, GearSet] = {}

        self.data = None
        self._loaded = False

    def load_all(self) -> bool:
        """加载所有数据"""
        try:
            logger.info(f"从 {self.data_dir} 加载数据...")

            # 检查数据目录是否存在
            if not self.data_dir.exists():
                logger.error(f"数据目录不存在: {self.data_dir}")
                return False

            # 加载角色数据
            characters = self._load_pickle("characters.pkl")
            if characters is None:
                return False

            for k, v in characters.items():
                character = Character(
                    id=int(v['character_id']),
                    name=v['name'],
                    rarity=v['rarity'],
                    weapon_type=v['weapon_type'],
                    element_type=v['element_type'],
                    base_attributes=v['stats'],
                    promotions_attributes=v['promotions'],
                    core_passive_attributes=v['core_passive'],
                    passive_data=v['passive'] if v['passive'] else None,
                    recommend=v['recommend'],
                )
                self.characters[int(k)] = character

            # 加载武器成长数据
            weapon_growth = self._load_pickle("weapon_growth.pkl", required=False)

            # 加载武器数据
            weapons = self._load_pickle("weapons.pkl")
            if weapons is None:
                return False

            for k, v in weapons.items():
                weapon = Weapon(
                    id=int(v['weapon_id']),
                    name=v['name'],
                    rarity=v['rarity'],
                    weapon_type=v['weapon_type'],
                    base_attack=v['attrs'][0],
                    advanced_attribute=v['attrs'][1],
                    talent_attributes=v['talents']['attrs']
                )
                weapon.set_actual_attributes(
                    weapon_growth["levels"],
                    weapon_growth["stars"]
                )
                self.weapons[int(k)] = weapon

            # 加载驱动盘套装数据
            gear_sets = self._load_pickle("gear_sets.pkl")
            if gear_sets is None:
                return False

            for k, v in gear_sets.items():
                gear_set = GearSet(
                    id=v['gear_set_id'],
                    name=v['gear_set_name'],
                    effect_2=v.get('effect2', None)
                )
                self.gear_sets[k] = gear_set

            self.data = RuntimeData(
                characters=self.characters,
                weapons=self.weapons,
                gear_sets=self.gear_sets,
                weapon_growth=weapon_growth or {}
            )

            self._loaded = True
            logger.info(f"数据加载成功: {len(characters)} 角色, {len(weapons)} 武器, {len(gear_sets)} 驱动盘套装")
            return True

        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_pickle(self, filename: str, required: bool = True) -> Optional[Any]:
        """加载pickle文件"""
        file_path = self.data_dir / filename

        if not file_path.exists():
            if required:
                logger.error(f"必需的数据文件不存在: {file_path}")
                return None
            else:
                logger.warning(f"可选数据文件不存在: {file_path}")
                return None

        try:
            with open(file_path, 'rb') as f:
                data = dill.load(f)
            logger.debug(f"加载 {filename} 成功")
            return data
        except Exception as e:
            logger.error(f"加载 {filename} 失败: {e}")
            if required:
                return None
            return None

    # ========== 获取数据的方法 ==========

    def get_character_data(self, character_id: int) -> Optional[Any]:
        """获取角色解析数据"""
        return self.data.characters.get(character_id)

    def get_weapon_data(self, weapon_id: int) -> Optional[Any]:
        """获取武器解析数据"""
        return self.data.weapons.get(weapon_id)

    def get_gear_set_data(self, gear_set_id: str) -> Optional[Any]:
        """获取驱动盘套装数据"""
        return self.data.gear_sets.get(gear_set_id)

    def get_weapon_growth(self, rarity: str, level: str) -> Optional[Dict]:
        """获取武器成长数据"""
        if not self.data.weapon_growth:
            return None
        return self.data.weapon_growth.get(rarity, {}).get(level)