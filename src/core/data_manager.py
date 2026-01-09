"""简化版数据管理器"""

import json
from typing import Dict, List, Optional


from src.config.constants import PathConstants
from src.parsers.character_parser import parse_character_data
from src.parsers.gear_set_parser import parse_gear_set_data
from src.parsers.weapon_parser import parse_weapon_data
from .models import Character, Weapon, GearSet


class SimpleDataManager:
    """简化数据管理器"""

    def __init__(self):
        self._loaded = False

        self._equipments: any = None

        self.data_dir = PathConstants.get_data_dir()
        self.characters: Dict[int, Character] = {}
        self.weapons: Dict[int, Weapon] = {}
        self.weapon_growth_data: Dict[str, Weapon] = {}
        self.gear_sets: Dict[str, GearSet] = {}

    def load_all(self) -> bool:
        """加载所有数据"""
        try:
            # 加载角色数据
            self._load_characters()

            # 加载音擎数据
            self._load_weapon_growth()
            self._load_weapons()

            # 加载驱动盘数据
            self._load_gear_sets()

            self._loaded = True

            print(f"数据加载完成: {len(self.characters)}个角色数据文件, "
                  f"{len(self.weapons)}个音擎数据文件, "
                  f"{len(self.weapon_growth_data)}个音擎成长数据文件, "
                  f"{len(self.gear_sets)}个驱动盘套装数据文件。")

            return True
        except Exception as e:
            print(f"加载数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _load_characters(self):
        """加载角色数据"""
        chars_dir = self.data_dir / "characters"
        if not chars_dir.exists():
            print(f"角色目录不存在: {chars_dir}")
            return

        for json_file in chars_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 使用原有解析器（稍后简化）
                parsed = parse_character_data(data)

                # 转换为简化模型
                character = Character(
                    id=parsed.character_id,
                    name=parsed.name,
                    rarity=parsed.rarity,
                    weapon_type=parsed.weapon_type,
                    element_type=parsed.element_type,
                    base_attributes=parsed.stats,
                    breakthrough_attributes=parsed.breakthrough,
                    core_passive_attributes=parsed.core_passive,
                    passive_data=parsed.passive if parsed.passive else None,
                    recommend=parsed.recommend,
                )

                self.characters[character.id] = character

            except Exception as e:
                print(f"加载角色文件失败 {json_file}: {e}")
                import traceback
                traceback.print_exc()

    def _load_weapons(self):
        """加载音擎数据"""
        weapons_dir = self.data_dir / "weapons"
        if not weapons_dir.exists():
            print(f"音擎目录不存在: {weapons_dir}")
            return

        for json_file in weapons_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                parsed = parse_weapon_data(data)

                # 转换为简化模型
                weapon = Weapon(
                    id=parsed.weapon_id,
                    name=parsed.name,
                    rarity=parsed.rarity,
                    weapon_type=parsed.weapon_type,
                    base_attack=parsed.attrs[0],
                    advanced_attribute=parsed.attrs[1],
                    talent_attributes=parsed.talents.attrs
                )

                weapon.set_actual_attributes(self)

                self.weapons[weapon.id] = weapon

            except Exception as e:
                print(f"加载音擎文件失败 {json_file}: {e}")
                import traceback
                traceback.print_exc()

    def _load_weapon_growth(self):
        """加载音擎成长数据"""
        weapon_growth_dir = self.data_dir / "weapons" / "growth"
        if not weapon_growth_dir.exists():
            print(f"音擎成长数据目录不存在: {weapon_growth_dir}")
            return

        # 加载所有成长数据文件
        growth_files = ["2.json", "3.json", "4.json", "stars.json"]

        for file_name in growth_files:
            json_file = weapon_growth_dir / file_name
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 保存数据，key为文件名（不含扩展名）
                key = file_name.replace(".json", "")
                self.weapon_growth_data[key] = data

            except Exception as e:
                print(f"✗ 加载音擎成长数据失败 {json_file}: {e}")

    def _load_gear_sets(self):
        """加载驱动盘套装数据"""
        gear_file = self.data_dir / "equipment" / "equipment.json"
        if not gear_file.exists():
            print(f"驱动盘文件不存在: {gear_file}")
            return

        try:
            with open(gear_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._equipments = data

            parsed = parse_gear_set_data(data)

            for set_id, set_data in parsed.gear_set_effects.items():
                gear_set = GearSet(
                    id=set_id,
                    name=set_data.gear_set_name,
                    effect_2=set_data.effect2
                )
                self.gear_sets[set_id] = gear_set

        except Exception as e:
            print(f"加载驱动盘数据失败: {e}")

    def get_character(self, character_id: int) -> Optional[Character]:
        """获取角色"""
        return self.characters.get(character_id)

    def get_all_characters(self) -> List[Character]:
        """获取所有角色"""
        return list(self.characters.values())

    def get_weapon(self, weapon_id: int) -> Optional[Weapon]:
        """获取音擎"""
        return self.weapons.get(weapon_id)

    def get_all_weapons(self) -> List[Weapon]:
        """获取所有音擎"""
        return list(self.weapons.values())

    def get_equipment(self):
        """获取所有驱动盘"""
        return [(k, v["名称"]) for k, v in self._equipments.items()]

    def get_gear_set(self, set_id: str) -> Optional[GearSet]:
        """获取驱动盘套装"""
        return self.gear_sets.get(set_id)

    def get_all_gear_sets(self) -> List[GearSet]:
        """获取所有驱动盘套装"""
        return list(self.gear_sets.values())

    def is_loaded(self) -> bool:
        """是否已加载数据"""
        return self._loaded