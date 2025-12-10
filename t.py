import re

import requests
import json

def remove_html_tags(text):
    """去除HTML标签和方括号标签"""
    if not isinstance(text, str):
        return text

    # 去除颜色标签
    text = re.sub(r'<color=.*?>', '', text)
    text = re.sub(r'</color>', '', text)
    # 去除其他HTML标签
    text = re.sub(r'<.*?>', '', text)

    return text

def download_equipment_ids():
    """下载并保存驱动盘数据"""
    url = "https://api.hakush.in/zzz/data/equipment.json"

    try:
        response = requests.get(url)
        data = response.json()

        # 提取所有驱动盘ID
        equipment_ids = list(data.keys())

        id_name_mapping = {}
        for equipment_id in equipment_ids:
            id_name_mapping[equipment_id] = data[equipment_id]["CHS"]
            for k, v in id_name_mapping[equipment_id].items():
                id_name_mapping[equipment_id][k] = remove_html_tags(v)


        with open("equipment.json", "w", encoding="utf-8") as f:
            json.dump(id_name_mapping, f, ensure_ascii=False, indent=2)

        # 在控制台也显示ID列表
        print("🎮 驱动盘ID列表:")
        for char_id in equipment_ids:
            print(f"  - {char_id}")

        return equipment_ids
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


# 使用示例
if __name__ == "__main__":
    download_equipment_ids()