# src/utils/cli_tools.py
"""命令行工具"""
import sys
from typing import List

from src import config_manager
from src.utils.file_processor import FileManagementService


def init_command():
    """初始化命令"""
    print("🚀 初始化应用程序...")

    file_service = FileManagementService()
    result = file_service.initialize_data_directory()

    if result["success"]:
        print("✅ 初始化完成")

        # 显示系统状态
        status = file_service.get_system_status()
        print(f"📊 系统状态:")
        print(f"  文件系统: {'正常' if status['file_system']['valid'] else '异常'}")
        print(f"  数据完整度: {status['data_status']['completion_rate']:.1f}%")
        print(f"  网络状态: {status['network_status']}")

        if status["recommendations"]:
            print("💡 建议操作:")
            for recommendation in status["recommendations"]:
                print(f"  - {recommendation}")
    else:
        print("❌ 初始化失败")


def status_command():
    """状态检查命令"""
    file_service = FileManagementService()
    status = file_service.get_system_status()

    print("📊 系统状态报告:")
    print(f"✅ 文件系统: {'正常' if status['file_system']['valid'] else '异常'}")
    print(f"📁 数据完整度: {status['data_status']['completion_rate']:.1f}%")
    print(f"📋 角色文件: {status['data_status']['existing_count']}/{status['data_status']['total_characters']}")
    print(f"🌐 网络状态: {status['network_status']}")

    if status["recommendations"]:
        print("\n💡 建议操作:")
        for recommendation in status["recommendations"]:
            print(f"  - {recommendation}")


def download_command(args: List[str]):
    """下载命令"""
    file_service = FileManagementService()

    if len(args) == 0 or args[0] == "all":
        # 下载所有数据
        file_service.download_all_data()
    elif args[0] == "list":
        # 只下载角色列表
        file_service.download_character_list()
    elif args[0] == "missing":
        # 下载缺失的角色
        file_service.download_missing_characters()
    elif args[0] == "retry":
        # 重试失败的下载
        max_retries = int(args[1]) if len(args) > 1 else 3
        file_service.retry_failed_downloads(max_retries)
    else:
        print("未知下载命令，可用命令: all, list, missing, retry")


def maintenance_command():
    """维护命令"""
    file_service = FileManagementService()
    result = file_service.perform_maintenance()
    print("✅ 维护任务完成")


def cleanup_command():
    """清理命令"""
    file_service = FileManagementService()
    result = file_service.cleanup_system()
    print(f"✅ 清理完成: 清空缓存, 清理 {result['backups_cleaned']} 个备份")


def export_command(args: List[str]):
    """导出命令"""
    file_service = FileManagementService()
    export_path = args[0] if args else None
    export_dir = file_service.export_data(export_path)
    print(f"✅ 数据已导出到: {export_dir}")


def main():
    """命令行主入口"""
    if len(sys.argv) < 2:
        print("用法: python cli_tools.py [init|status|download|maintenance|cleanup|export]")
        print("下载子命令: python cli_tools.py download [all|list|missing|retry]")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "init":
        init_command()
    elif command == "status":
        status_command()
    elif command == "download":
        download_command(args)
    elif command == "maintenance":
        maintenance_command()
    elif command == "cleanup":
        cleanup_command()
    elif command == "export":
        export_command(args)
    else:
        print("未知命令，可用命令: init, status, download, maintenance, cleanup, export")


if __name__ == "__main__":
    main()