import json
from typing import Dict, Any

from src import config_manager
from src import CharacterLoader
from src import Attribute, AttributeType, AttributeValueType
from src import RawCharacterData

# # 创建 CharacterLoader 实例
# loader = CharacterLoader()
#
# # 使用实例调用 load_character
# data = loader.load_character(character_id="1371")
# print(data)
file_path = config_manager.file.get_character_file_path("1371")
with open(file_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

def _convert_to_raw_character_data(json_data: Dict[str, Any]) -> RawCharacterData:
        """将JSON数据转换为RawCharacterData对象"""
        return RawCharacterData(
            Id=json_data.get("Id", 0),
            Name=json_data.get("Name", ""),
            CodeName=json_data.get("CodeName", ""),
            Rarity=json_data.get("Rarity", 4),
            WeaponType=json_data.get("WeaponType", {}),
            ElementType=json_data.get("ElementType", {}),
            SpecialElementType=json_data.get("SpecialElementType", {}),
            Stats=json_data.get("Stats", {}),
            Level=json_data.get("Level", {}),
            ExtraLevel=json_data.get("ExtraLevel", {}),
            Passive=json_data.get("Passive", {}),
            FairyRecommend=json_data.get("FairyRecommend", {})
        )
# 转换为RawCharacterData对象
# raw_data = _convert_to_raw_character_data(json_data)
# d = {}
# data = json_data.get("Level", {})
# print(data)
# for k, v in data.items():
#     d[k] = []
#     print(k, v)
#     for k1, v1 in v.items():
#         if k1 == "HpMax":
#             d[k].append(Attribute(AttributeType.HP,))
#         elif k1 == "Attack":
#             print()
#         elif k1 == "Defence":
#             print()
d = {}
data = json_data.get("Stats", {})
print(data)
for k, v in data.items():
    print(k, v)
    if k == "HpMax":
        d[AttributeType.HP.value] = Attribute(AttributeType.HP, v, data["HpGrowth"], AttributeValueType.NUMERIC_VALUE)
    elif k == "Attack":
        print(d[AttributeType.HP.value])
    elif k == "Defence":
        print(d[AttributeType.HP.value])
    elif k == "HpMin":
        print(d[AttributeType.HP.value])
    elif k == "HpMin":
        print(d[AttributeType.HP.value])
    elif k == "HpMin":
        print(d[AttributeType.HP.value])
    elif k == "HpMin":
        print(d[AttributeType.HP.value])
    elif k == "HpMin":
        print(d[AttributeType.HP.value])
    elif k == "HpMin":
        print(d[AttributeType.HP.value])
    elif k == "HpMin":
        print(d[AttributeType.HP.value])
    elif k == "HpMin":
        print(d[AttributeType.HP.value])
print(d)