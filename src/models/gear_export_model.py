import base64
import json
import zlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class GearExportData:
    """单驱动盘导出数据"""
    slot_index: int
    level: int
    main_attribute: Dict[str, Any] = field(default_factory=dict)
    sub_attributes: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_gear_piece(cls, gear_piece) -> 'GearExportData':
        """从GearPiece创建导出数据"""
        main_attr_data = {}
        if gear_piece.main_attribute:
            main_attr_data = {
                'name': gear_piece.main_attribute.name,
                'type': gear_piece.main_attribute.attribute_type.value,
                'value_type': gear_piece.main_attribute.attribute_value_type.value,
                'base': gear_piece.main_attribute.base,
                'growth': gear_piece.main_attribute.growth
            }

        sub_attrs_data = []
        for sub_attr in gear_piece.sub_attributes:
            sub_attrs_data.append({
                'name': sub_attr.name,
                'type': sub_attr.attribute_type.value,
                'value_type': sub_attr.attribute_value_type.value,
                'base': sub_attr.base,
                'growth': sub_attr.growth,
                'enhancement_level': sub_attr.enhancement_level
            })

        return cls(
            slot_index=gear_piece.slot_index,
            level=gear_piece.level,
            main_attribute=main_attr_data,
            sub_attributes=sub_attrs_data
        )


@dataclass
class GearSetExportData:
    """套装导出数据"""
    combination_type: str
    set_ids: List[int]
    set_names: List[str] = field(default_factory=list)


@dataclass
class GearConfigExport:
    """完整的驱动盘配置导出数据"""
    version: str = "1.0.0"
    export_time: str = field(default_factory=lambda: datetime.now().isoformat())
    character_id: int = 0
    character_name: str = ""
    weapon_id: int = 0
    weapon_name: str = ""
    gears: List[GearExportData] = field(default_factory=list)
    gear_set: GearSetExportData = field(default_factory=lambda: GearSetExportData("4+2", []))
    enhance_level: int = 15

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def to_best_encode(self) -> str:
        """转换为紧凑JSON + 压缩 + URL安全Base64"""
        # 紧凑JSON
        json_str = json.dumps(self.to_dict(), separators=(',', ':'), ensure_ascii=False)
        # 压缩
        compressed = zlib.compress(json_str.encode('utf-8'), level=9)
        # URL安全Base64（无填充）
        encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
        return encoded.rstrip('=')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GearConfigExport':
        """从字典创建"""
        # 处理嵌套数据
        gear_set_data = data.get('gear_set', {})
        gear_set = GearSetExportData(
            combination_type=gear_set_data.get('combination_type', '4+2'),
            set_ids=gear_set_data.get('set_ids', []),
            set_names=gear_set_data.get('set_names', [])
        )

        gears_data = []
        for gear_data in data.get('gears', []):
            gears_data.append(GearExportData(
                slot_index=gear_data['slot_index'],
                level=gear_data['level'],
                main_attribute=gear_data.get('main_attribute', {}),
                sub_attributes=gear_data.get('sub_attributes', [])
            ))

        return cls(
            version=data.get('version', '1.0.0'),
            export_time=data.get('export_time', ''),
            character_id=data.get('character_id', 0),
            character_name=data.get('character_name', ''),
            weapon_id=data.get('weapon_id', 0),
            weapon_name=data.get('weapon_name', ''),
            gears=gears_data,
            gear_set=gear_set,
            enhance_level=data.get('enhance_level', 15)
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'GearConfigExport':
        """从JSON字符串创建"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_best_encode(cls, encoded_str: str) -> 'GearConfigExport':
        """从编码字符串创建"""
        # 添加填充
        padding = 4 - (len(encoded_str) % 4)
        if padding != 4:
            encoded_str += '=' * padding
        # Base64解码
        compressed = base64.urlsafe_b64decode(encoded_str.encode('ascii'))
        # 解压缩
        json_str = zlib.decompress(compressed).decode('utf-8')
        # 解析JSON并创建GearConfigExport对象
        data = json.loads(json_str)
        return cls.from_dict(data)