# src/utils/file_processor.py
"""重构后的文件处理器"""
import json
import shutil
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from src.config import config_manager
from src.utils.data_downloader import DownloadService


class FileProcessor:
    """文件处理器 - 单一职责：处理文件操作"""

    def __init__(self):
        self.file_config = config_manager.file

    def clean_character_files(self) -> Dict[str, Any]:
        """清理角色文件中的冗余字段"""
        character_files = self.file_config.list_character_files()

        if not character_files:
            return {"processed": 0, "errors": [], "backup_created": False}

        print(f"🧹 开始清理 {len(character_files)} 个角色文件...")

        # 创建备份
        backup_path = self._create_backup(character_files)

        processed_count = 0
        error_files = []

        for file_path in character_files:
            try:
                success = self._clean_single_file(file_path)
                if success:
                    processed_count += 1
                else:
                    error_files.append(str(file_path))
            except Exception as e:
                print(f"❌ 清理失败 {file_path}: {e}")
                error_files.append(str(file_path))

        self._print_processing_summary(processed_count, error_files, backup_path)

        return {
            "processed": processed_count,
            "errors": error_files,
            "backup_created": backup_path is not None,
            "backup_path": str(backup_path) if backup_path else None
        }

    def validate_character_files(self) -> Dict[str, Any]:
        """验证角色文件有效性"""
        character_files = self.file_config.list_character_files()

        if not character_files:
            return {"valid": 0, "invalid": 0, "errors": []}

        print(f"🔍 验证 {len(character_files)} 个角色文件...")

        valid_files = []
        invalid_files = []
        error_details = []

        for file_path in character_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 检查必需字段
                required_fields = ["Id", "Name", "Stats"]
                if all(field in data for field in required_fields):
                    valid_files.append(str(file_path))
                else:
                    invalid_files.append(str(file_path))
                    missing = [field for field in required_fields if field not in data]
                    error_details.append(f"{file_path.name}: 缺少字段 {missing}")

            except Exception as e:
                invalid_files.append(str(file_path))
                error_details.append(f"{file_path.name}: 解析错误 {e}")

        print(f"📊 验证完成: 有效 {len(valid_files)} 个, 无效 {len(invalid_files)} 个")

        return {
            "valid": len(valid_files),
            "invalid": len(invalid_files),
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "error_details": error_details
        }

    def create_backup(self, backup_name: str = None) -> str:
        """创建备份"""
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"characters_backup_{timestamp}"

        backup_path = self.file_config.get_backup_path(backup_name)
        character_files = self.file_config.list_character_files()

        backup_path.mkdir(parents=True, exist_ok=True)

        for file_path in character_files:
            backup_file = backup_path / file_path.name
            shutil.copy2(file_path, backup_file)

        print(f"💾 备份创建成功: {backup_path}")
        return str(backup_path)

    def restore_backup(self, backup_name: str) -> bool:
        """从备份恢复"""
        backup_path = self.file_config.get_backup_path(backup_name)

        if not backup_path.exists():
            print(f"❌ 备份不存在: {backup_path}")
            return False

        print(f"🔄 从备份恢复: {backup_path}")

        try:
            # 清空当前角色目录
            for file_path in self.file_config.list_character_files():
                file_path.unlink()

            # 从备份复制文件
            for backup_file in backup_path.glob("*.json"):
                target_path = self.file_config.characters_dir / backup_file.name
                shutil.copy2(backup_file, target_path)

            print(f"✅ 恢复完成: 从 {backup_path} 恢复了所有文件")
            return True

        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        backups = []

        if not self.file_config.backup_dir.exists():
            return backups

        for backup_path in self.file_config.backup_dir.iterdir():
            if backup_path.is_dir():
                backup_files = list(backup_path.glob("*.json"))
                created_time = datetime.fromtimestamp(backup_path.stat().st_ctime)

                backups.append({
                    "name": backup_path.name,
                    "path": str(backup_path),
                    "file_count": len(backup_files),
                    "created_time": created_time,
                    "size_mb": sum(f.stat().st_size for f in backup_files) / 1024 / 1024
                })

        # 按创建时间排序
        backups.sort(key=lambda x: x["created_time"], reverse=True)
        return backups

    def get_file_statistics(self) -> Dict[str, Any]:
        """获取文件统计信息"""
        character_files = self.file_config.list_character_files()

        total_size = sum(f.stat().st_size for f in character_files)
        file_sizes = [f.stat().st_size for f in character_files]

        return {
            "total_files": len(character_files),
            "total_size_mb": total_size / 1024 / 1024,
            "average_size_kb": (sum(file_sizes) / len(file_sizes)) / 1024 if file_sizes else 0,
            "largest_file_kb": max(file_sizes) / 1024 if file_sizes else 0,
            "smallest_file_kb": min(file_sizes) / 1024 if file_sizes else 0
        }

    def clean_icon_fields(self, file_path: Path) -> bool:
        """清理单个文件的Icon字段"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 清理Icon字段
            cleaned_data = self._remove_redundant_fields(data)

            # 写回文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

            print(f"✅ 清理成功: {file_path}")
            return True

        except Exception as e:
            print(f"❌ 清理失败 {file_path}: {e}")
            return False

    def _clean_single_file(self, file_path: Path) -> bool:
        """清理单个文件"""
        return self.clean_icon_fields(file_path)

    def _remove_redundant_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """移除冗余字段 - 使用ss.py的有效逻辑"""

        # 使用ss.py的排除字段列表
        exclude_fields = {"Icon", "PartnerInfo", "Skin", "LevelEXP", "Skill",
                          "SkillList", "Talent", "Potential", "PotentialDetail",
                          "Image", "Thumbnail"}
        exclude_parts = {"Part4", "Part5", "Part6", "PartSub"}

        def clean_recursive(obj):
            if isinstance(obj, dict):
                cleaned = {}
                for key, value in obj.items():
                    # 排除指定字段
                    if key in exclude_fields:
                        continue

                    # 特殊处理SpecialElementType
                    elif key == "SpecialElementType":
                        if isinstance(value, dict):
                            cleaned[key] = {}
                            for sub_key, sub_value in value.items():
                                if sub_key != "Icon":
                                    cleaned[key][sub_key] = sub_value
                        else:
                            cleaned[key] = value

                    # 特殊处理FairyRecommend
                    elif key == "FairyRecommend":
                        if isinstance(value, dict):
                            cleaned[key] = {}
                            for part_key, part_value in value.items():
                                if part_key not in exclude_parts:
                                    cleaned[key][part_key] = clean_recursive(part_value)
                                else:
                                    if isinstance(part_value, dict):
                                        cleaned[key][part_key] = {}
                                        for attr_key, attr_value in part_value.items():
                                            if attr_key != "Icon":
                                                cleaned[key][part_key][attr_key] = attr_value
                                    else:
                                        cleaned[key][part_key] = part_value
                        else:
                            cleaned[key] = value

                    else:
                        cleaned[key] = clean_recursive(value)
                return cleaned
            elif isinstance(obj, list):
                return [clean_recursive(item) for item in obj]
            else:
                return obj

        return clean_recursive(data)

    def _create_backup(self, files: List[Path]) -> Path:
        """创建备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_clean_backup_{timestamp}"
        return Path(self.create_backup(backup_name))

    def _print_processing_summary(self, processed_count: int, error_files: List[str], backup_path: Optional[Path]):
        """打印处理总结"""
        print("\n" + "=" * 60)
        print("📊 处理完成!")
        print(f"✅ 成功处理: {processed_count} 个文件")
        print(f"❌ 处理失败: {len(error_files)} 个文件")

        if backup_path:
            print(f"💾 备份位置: {backup_path}")

        if error_files:
            print("\n失败的文件:")
            for error_file in error_files:
                print(f"  - {error_file}")


class FileManagementService:
    """文件管理服务 - 提供完整的数据管理功能"""

    def __init__(self):
        self.processor = FileProcessor()
        self.download_service = DownloadService()

    def initialize_data_directory(self) -> Dict[str, Any]:
        """初始化数据目录 - 返回更详细的结果"""
        result = {
            "success": True,
            "directories_created": [],
            "directories_existing": [],
            "data_completeness": {},
            "warnings": []
        }

        print("📁 初始化数据目录结构...")

        # 检查目录结构
        structure_check = self.processor.file_config.validate_data_structure()

        if not structure_check["valid"]:
            print("⚠️ 数据目录结构不完整，正在修复...")

            # 创建缺失的目录
            for dir_name in structure_check["missing_dirs"]:
                dir_path = getattr(self.processor.file_config, f"{dir_name}")
                dir_path.mkdir(parents=True, exist_ok=True)
                result["directories_created"].append(str(dir_path))
                print(f"✅ 创建目录: {dir_path}")
        else:
            print("✅ 数据目录结构完整")
            # 记录已存在的目录
            for dir_name, dir_info in structure_check["details"].items():
                if dir_info["exists"]:
                    result["directories_existing"].append(dir_info["path"])

        # 检查数据完整性 与equipment的适配有问题，后面修改
        # completeness = self.download_service.check_data_completeness()
        # result["data_completeness"] = completeness
        #
        # if completeness["completion_rate"] < 100:
        #     warning_msg = f"数据不完整: {completeness['completion_rate']:.1f}%"
        #     result["warnings"].append(warning_msg)
        #     print(f"⚠️ {warning_msg}")

        # 文件统计
        stats = self.processor.get_file_statistics()
        result["file_statistics"] = stats

        print(f"📊 文件统计: {stats['total_files']} 个角色文件, 总大小: {stats['total_size_mb']:.1f}MB")

        return result

    def download_all_data(self) -> Dict[str, Any]:
        """下载所有数据（完整流程）"""
        print("📥 开始下载所有数据...")

        result = self.download_service.download_all_data()

        if result["character_data_success"]:
            print(f"✅ 下载完成: {result['downloaded_count']}/{result['total_characters']} 个角色")
        else:
            print("❌ 下载失败")

        return result

    def download_character_list(self) -> bool:
        """下载角色列表"""
        print("📋 下载角色列表...")

        success = self.download_service.downloader.download_character_list()

        if success:
            print("✅ 角色列表下载成功")
        else:
            print("❌ 角色列表下载失败")

        return success is not None

    def download_missing_characters(self) -> Tuple[int, List[str]]:
        """下载缺失的角色数据"""
        print("🔍 检查缺失的角色数据...")

        completeness = self.download_service.check_data_completeness()

        if completeness["completion_rate"] == 100:
            print("✅ 没有缺失的角色数据")
            return 0, []

        print(f"📥 开始下载 {len(completeness['missing_files'])} 个缺失的角色...")

        success_count, failed_ids = self.download_service.downloader.batch_download_characters(
            completeness["missing_files"]
        )

        print(f"📊 下载完成: 成功 {success_count} 个, 失败 {len(failed_ids)} 个")

        return success_count, failed_ids

    def retry_failed_downloads(self, max_retries: int = 3) -> Tuple[int, List[str]]:
        """重试失败的下载"""
        print("🔄 重试失败的下载...")

        success_count, still_failed = self.download_service.downloader.retry_failed_downloads(max_retries)

        print(f"📊 重试完成: 成功 {success_count} 个, 仍然失败 {len(still_failed)} 个")

        return success_count, still_failed

    def test_network_connection(self) -> bool:
        """测试网络连接"""
        print("🔗 测试网络连接...")

        success = self.download_service.downloader.test_connection()

        if success:
            print("✅ 网络连接正常")
        else:
            print("❌ 网络连接失败")

        return success

    def perform_maintenance(self) -> Dict[str, Any]:
        """执行维护任务"""
        result = {}

        print("🔧 执行系统维护...")

        # 验证文件
        validation_result = self.processor.validate_character_files()
        result["validation"] = validation_result

        print(f"📋 文件验证: {validation_result['valid']} 个有效, {validation_result['invalid']} 个无效")

        # 清理文件
        clean_result = self.processor.clean_character_files()
        result["cleaning"] = clean_result

        # 文件统计
        stats = self.processor.get_file_statistics()
        result["statistics"] = stats

        print("✅ 系统维护完成")

        return result

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            "file_system": {},
            "data_status": {},
            "network_status": "unknown",
            "recommendations": []
        }

        # 文件系统状态
        structure = self.processor.file_config.validate_data_structure()
        status["file_system"] = {
            "valid": structure["valid"],
            "details": structure["details"]
        }

        # 数据状态
        completeness = self.download_service.check_data_completeness()
        status["data_status"] = completeness

        # 网络状态
        try:
            network_ok = self.test_network_connection()
            status["network_status"] = "connected" if network_ok else "disconnected"
        except:
            status["network_status"] = "unknown"

        # 生成建议
        if not structure["valid"]:
            status["recommendations"].append("修复数据目录结构")

        if completeness["completion_rate"] < 100:
            if status["network_status"] == "connected":
                status["recommendations"].append("下载缺失的角色数据")
            else:
                status["recommendations"].append("检查网络连接后下载缺失数据")

        if completeness["completion_rate"] == 0:
            status["recommendations"].append("运行完整的数据下载流程")

        # 检查是否有失败的下载需要重试
        failed_downloads_file = self.processor.file_config.failed_downloads_file
        if failed_downloads_file.exists():
            try:
                import json
                with open(failed_downloads_file, 'r', encoding='utf-8') as f:
                    failed_ids = json.load(f)
                if failed_ids:
                    status["recommendations"].append(f"重试 {len(failed_ids)} 个失败的下载")
            except:
                pass

        return status

    def cleanup_system(self) -> Dict[str, Any]:
        """清理系统"""
        result = {
            "cache_cleared": False,
            "backups_cleaned": 0,
            "temp_files_removed": 0
        }

        print("🧹 系统清理...")

        # 清空缓存目录
        cache_dir = self.processor.file_config.cache_dir
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            cache_dir.mkdir()
            result["cache_cleared"] = True
            print("✅ 缓存已清空")

        # 清理旧的备份（保留最近5个）
        backups = self.processor.list_backups()
        if len(backups) > 5:
            backups_to_remove = backups[5:]
            for backup in backups_to_remove:
                import shutil
                shutil.rmtree(backup["path"])
                result["backups_cleaned"] += 1
            print(f"✅ 清理了 {result['backups_cleaned']} 个旧备份")

        # 清空计算器缓存
        from src.core.service_factory import get_service_factory
        service_factory = get_service_factory()
        service_factory.clear_cache()
        print("✅ 计算器缓存已清空")

        print("✅ 系统清理完成")
        return result

    def export_data(self, export_path: str = None) -> str:
        """导出数据"""
        import shutil
        from datetime import datetime

        if export_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = f"zzz_calculator_export_{timestamp}"

        export_dir = Path(export_path)
        export_dir.mkdir(parents=True, exist_ok=True)

        # 复制角色数据
        characters_dir = export_dir / "characters"
        shutil.copytree(self.processor.file_config.characters_dir, characters_dir)

        # 复制配置文件
        config_files = [
            self.processor.file_config.character_ids_file,
            self.processor.file_config.id_name_mapping_file
        ]

        for config_file in config_files:
            if config_file.exists():
                shutil.copy2(config_file, export_dir / config_file.name)

        print(f"✅ 数据已导出到: {export_path}")
        return str(export_dir)