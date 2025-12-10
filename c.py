# 下载所有数据（包括装备）
from src import DownloadService

service = DownloadService()

# 或者只下载装备数据
# service.download_equipment_only()

# 检查数据完整性
# completeness = service.check_data_completeness()

service.download_weapon_only()