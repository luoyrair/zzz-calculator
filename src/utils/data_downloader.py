# src/utils/data_downloader.py
"""重构后的数据下载器"""
import json
import time
import re
from typing import List, Tuple, Optional, Dict, Any

import requests

from src.config import config_manager


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


class DataDownloader:
    """数据下载器 - 单一职责：负责从API下载数据"""

    def __init__(self):
        self.file_config = config_manager.file
        self.api_config = {
            "base_url": "https://api.hakush.in/zzz/data",
            "endpoints": {
                "character_list": "/character.json",
                "character_data": "/zh/character/{character_id}.json",
                "equipment_data": "/equipment.json"
            },
            "request_delay": 0.1,
            "timeout": 10
        }
        self._session = requests.Session()

    def download_character_list(self) -> Optional[Dict[str, Any]]:
        """下载角色列表"""
        print("📥 开始下载角色列表...")

        url = self._build_url("character_list")
        print(f"🔗 请求URL: {url}")

        try:
            response = self._session.get(url, timeout=self.api_config["timeout"])
            response.raise_for_status()

            data = response.json()
            self._save_character_mapping(data)

            print(f"✅ 角色列表下载成功: {len(data)} 个角色")
            return data

        except Exception as e:
            print(f"❌ 角色列表下载失败: {e}")
            return None

    def download_character_data(self, character_id: str) -> bool:
        """下载单个角色数据"""
        url = self._build_url("character_data", character_id=character_id)

        try:
            response = self._session.get(url, timeout=self.api_config["timeout"])

            if response.status_code == 200:
                data = response.json()
                self._save_character_file(character_id, data)

                character_name = data.get('Name', '未知角色')
                print(f"   ✅ 下载成功: {character_name}")
                return True
            else:
                print(f"   ❌ 下载失败: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ 下载失败: {e}")
            return False

    def download_equipment_data(self) -> Optional[List[str]]:
        """下载并保存驱动盘数据"""
        print("🎮 开始下载驱动盘数据...")

        url = self._build_url("equipment_data")
        print(f"🔗 请求URL: {url}")

        try:
            response = self._session.get(url, timeout=self.api_config["timeout"])
            response.raise_for_status()

            data = response.json()

            # 提取所有驱动盘ID
            equipment_ids = list(data.keys())

            # 清理数据中的HTML标签
            equipment_data = {}
            for equipment_id in equipment_ids:
                equipment_data[equipment_id] = data[equipment_id]["CHS"]
                for k, v in equipment_data[equipment_id].items():
                    equipment_data[equipment_id][k] = remove_html_tags(v)

            # 保存清理后的装备数据
            with open(self.file_config.equipment_file, "w", encoding="utf-8") as f:
                json.dump(equipment_data, f, ensure_ascii=False, indent=2)

            # 保存装备ID列表
            with open(self.file_config.equipment_ids_file, "w", encoding="utf-8") as f:
                json.dump(equipment_ids, f, ensure_ascii=False, indent=2)

            # 在控制台显示ID列表
            print("🎮 驱动盘ID列表:")
            for equip_id in equipment_ids:
                equip_name = equipment_data[equip_id].get("name", "未知装备")
                print(f"  - {equip_id}: {equip_name}")

            print(f"✅ 驱动盘数据下载成功: {len(equipment_ids)} 个装备")
            return equipment_ids

        except Exception as e:
            print(f"❌ 驱动盘数据下载失败: {e}")
            return None

    def batch_download_characters(self, character_ids: List[str] = None) -> Tuple[int, List[str]]:
        """批量下载角色数据"""
        if character_ids is None:
            character_ids = self._load_character_ids()
            if not character_ids:
                print("❌ 没有可用的角色ID")
                return 0, []

        print(f"📥 开始批量下载 {len(character_ids)} 个角色数据...")

        success_count = 0
        failed_ids = []

        for index, char_id in enumerate(character_ids, 1):
            print(f"🔍 正在下载 ({index}/{len(character_ids)}): {char_id}")

            success = self.download_character_data(char_id)

            if success:
                success_count += 1
            else:
                failed_ids.append(char_id)

            time.sleep(self.api_config["request_delay"])

        self._save_failed_downloads(failed_ids)
        self._print_download_summary(success_count, failed_ids, len(character_ids))

        return success_count, failed_ids

    def retry_failed_downloads(self, max_retries: int = 3) -> Tuple[int, List[str]]:
        """重试失败的下载"""
        failed_ids = self._load_failed_downloads()

        if not failed_ids:
            print("✅ 没有需要重试的下载")
            return 0, []

        print(f"🔄 开始重试 {len(failed_ids)} 个失败的下载...")

        for retry_count in range(1, max_retries + 1):
            print(f"\n🔄 重试第 {retry_count} 次...")

            still_failed = []

            for char_id in failed_ids:
                print(f"   🔄 重试: {char_id}")
                success = self.download_character_data(char_id)

                if not success:
                    still_failed.append(char_id)

                time.sleep(self.api_config["request_delay"])

            failed_ids = still_failed

            if not failed_ids:
                print("✅ 所有重试都成功了!")
                break

        self._save_failed_downloads(failed_ids)
        success_count = len(failed_ids) - len(still_failed)

        print(f"📊 重试完成: 成功 {success_count} 个, 仍然失败 {len(still_failed)} 个")
        return success_count, still_failed

    def test_connection(self) -> bool:
        """测试API连接"""
        print("🔗 测试API连接...")

        test_url = self._build_url("character_list")

        try:
            response = self._session.get(test_url, timeout=10)
            if response.status_code == 200:
                print("✅ API连接正常")
                return True
            else:
                print(f"❌ API连接失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API连接失败: {e}")
            return False

    def _build_url(self, endpoint_key: str, **kwargs) -> str:
        """构建完整的URL"""
        endpoint = self.api_config["endpoints"][endpoint_key]
        if kwargs:
            endpoint = endpoint.format(**kwargs)
        return self.api_config["base_url"] + endpoint

    def _save_character_mapping(self, data: Dict[str, Any]):
        """保存角色ID-名称映射"""
        id_name_mapping = {}

        for character_id, character_data in data.items():
            name = (character_data.get("CHS") or
                    character_data.get("EN") or
                    character_data.get("JP") or
                    f"角色_{character_id}")
            id_name_mapping[character_id] = name

        # 保存映射文件
        with open(self.file_config.id_name_mapping_file, "w", encoding="utf-8") as f:
            json.dump(id_name_mapping, f, ensure_ascii=False, indent=2)

        # 保存角色ID列表
        character_ids = list(data.keys())
        with open(self.file_config.character_ids_file, "w", encoding="utf-8") as f:
            json.dump(character_ids, f, ensure_ascii=False, indent=2)

        print(f"💾 角色映射已保存: {len(id_name_mapping)} 个角色")

    def _save_character_file(self, character_id: str, data: Dict[str, Any]):
        """保存角色数据文件"""
        file_path = self.file_config.get_character_file_path(character_id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_character_ids(self) -> List[str]:
        """加载角色ID列表"""
        try:
            with open(self.file_config.character_ids_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ 角色ID文件不存在")
            return []
        except Exception as e:
            print(f"❌ 加载角色ID失败: {e}")
            return []

    def _save_failed_downloads(self, failed_ids: List[str]):
        """保存失败下载列表"""
        with open(self.file_config.failed_downloads_file, "w", encoding="utf-8") as f:
            json.dump(failed_ids, f, ensure_ascii=False, indent=2)

    def _load_failed_downloads(self) -> List[str]:
        """加载失败下载列表"""
        try:
            with open(self.file_config.failed_downloads_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"❌ 加载失败下载列表失败: {e}")
            return []

    def _print_download_summary(self, success_count: int, failed_ids: List[str], total_count: int):
        """打印下载总结"""
        print("\n" + "=" * 60)
        print("📊 下载完成!")
        print(f"✅ 成功: {success_count} 个")
        print(f"❌ 失败: {len(failed_ids)} 个")

        if total_count > 0:
            success_rate = success_count / total_count * 100
            print(f"📈 成功率: {success_rate:.1f}%")

        if failed_ids:
            print(f"\n失败的角色ID:")
            for failed_id in failed_ids:
                print(f"  - {failed_id}")


class DownloadService:
    """下载服务 - 提供高级下载功能"""

    def __init__(self):
        self.downloader = DataDownloader()

    def download_all_data(self) -> Dict[str, Any]:
        """下载所有数据（完整流程）"""
        result = {
            "character_list_success": False,
            "character_data_success": False,
            "equipment_data_success": False,
            "total_characters": 0,
            "downloaded_count": 0,
            "failed_count": 0,
            "equipment_count": 0
        }

        # 测试连接
        if not self.downloader.test_connection():
            print("❌ 网络连接失败，无法下载数据")
            return result

        # 下载装备数据
        equipment_ids = self.downloader.download_equipment_data()
        if equipment_ids:
            result["equipment_data_success"] = True
            result["equipment_count"] = len(equipment_ids)

        # 下载角色列表
        character_data = self.downloader.download_character_list()
        if not character_data:
            return result

        result["character_list_success"] = True
        result["total_characters"] = len(character_data)

        # 下载角色数据
        character_ids = list(character_data.keys())
        success_count, failed_ids = self.downloader.batch_download_characters(character_ids)

        result["character_data_success"] = True
        result["downloaded_count"] = success_count
        result["failed_count"] = len(failed_ids)

        return result

    def download_equipment_only(self) -> bool:
        """仅下载装备数据"""
        equipment_ids = self.downloader.download_equipment_data()
        return equipment_ids is not None

    def check_data_completeness(self) -> Dict[str, Any]:
        """检查数据完整性"""
        try:
            character_ids = self.downloader._load_character_ids()
            equipment_ids = self._load_equipment_ids()

            character_stats = {
                "total": len(character_ids) if character_ids else 0,
                "existing": 0,
                "missing": []
            }

            equipment_stats = {
                "total": len(equipment_ids) if equipment_ids else 0,
                "existing": 0,
                "missing": []
            }

            # 检查角色数据完整性
            if character_ids:
                for char_id in character_ids:
                    if self.downloader.file_config.character_file_exists(char_id):
                        character_stats["existing"] += 1
                    else:
                        character_stats["missing"].append(char_id)

            # 检查装备数据完整性
            if equipment_ids:
                equipment_stats["existing"] = 1 if self.downloader.file_config.equipment_mapping_file.exists() else 0

            character_completion = character_stats["existing"] / character_stats["total"] * 100 if character_stats["total"] > 0 else 0
            equipment_completion = equipment_stats["existing"] / equipment_stats["total"] * 100 if equipment_stats["total"] > 0 else 0
            overall_completion = (character_completion + equipment_completion) / 2 if character_stats["total"] > 0 and equipment_stats["total"] > 0 else 0

            return {
                "status": "complete" if overall_completion == 100 else "incomplete",
                "overall_completion_rate": overall_completion,
                "characters": character_stats,
                "equipment": equipment_stats,
                "character_completion_rate": character_completion,
                "equipment_completion_rate": equipment_completion
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "overall_completion_rate": 0}

    def _load_equipment_ids(self) -> List[str]:
        """加载装备ID列表"""
        try:
            with open(self.downloader.file_config.equipment_ids_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"❌ 加载装备ID失败: {e}")
            return []