# src/core/builder/character.py
"""角色构建器"""
from src.core.calculation.factory import StrategyFactory
from src.core.models.character import CharacterSchema, CharacterBaseStats


class CharacterBuilder:
    """角色属性构建器"""

    def __init__(self, schema: CharacterSchema, use_cache: bool = True):
        self.schema = schema
        self.use_cache = use_cache
        print(f"[Builder] 创建角色构建器: {schema.name}(ID:{schema.character_id})")
        print(f"[Builder] 使用缓存: {use_cache}")

        self.calculation_chain = StrategyFactory.create_default_chain(use_cache)

    def build_base_stats(self, level: int, breakthrough_level: int,
                         core_passive_level: int) -> CharacterBaseStats:
        """构建基础属性"""
        from ..calculation.base import CalculationContext

        print(f"\n{'#' * 70}")
        print(f"[Builder] 开始构建角色属性")
        print(f"[Builder] 角色: {self.schema.name}")
        print(f"[Builder] 配置: 等级={level}, 突破={breakthrough_level}, 核心技={core_passive_level}")
        print(f"{'#' * 70}")

        # 验证输入参数
        self._validate_inputs(level, breakthrough_level, core_passive_level)

        # 创建计算上下文
        context = CalculationContext(
            schema=self.schema,
            level=level,
            breakthrough_level=breakthrough_level,
            core_passive_level=core_passive_level-1
        )

        print(f"[Builder] 计算上下文创建完成")
        print(f"[Builder] 上下文缓存键: {context.get_cache_key()}")

        # 执行计算链
        self.calculation_chain.set_context(context)
        calculated_data = self.calculation_chain.execute()

        # 转换为CharacterBaseStats
        stats = CharacterBaseStats()
        conversion_count = 0

        print(f"[Builder] 开始将计算结果转换为CharacterBaseStats")
        for field_name in calculated_data.__dataclass_fields__:
            if hasattr(calculated_data, field_name) and hasattr(stats, field_name):
                value = getattr(calculated_data, field_name)
                setattr(stats, field_name, value)
                conversion_count += 1
                print(f"[Builder]  转换字段 {field_name}: {self._format_value(field_name, value)}")

        # 设置等级信息
        stats.Level = level
        stats.BreakthroughLevel = breakthrough_level
        stats.CorePassiveLevel = core_passive_level

        print(f"[Builder] 属性转换完成: {conversion_count}个字段")
        print(f"[Builder] 基础属性构建完成:")
        self._print_stats_summary(stats)
        print(f"{'#' * 70}\n")

        return stats

    def get_display_info(self) -> dict:
        """获取显示信息"""
        info = {
            "id": self.schema.character_id,
            "name": self.schema.name,
            "code_name": self.schema.code_name,
            "rarity": self.schema.rarity,
            "weapon_type": self.schema.weapon_type,
            "element_type": self.schema.element_type
        }

        print(f"[Builder] 获取显示信息:")
        for key, value in info.items():
            print(f"[Builder]   {key}: {value}")

        return info

    def _validate_inputs(self, level: int, breakthrough_level: int, core_passive_level: int):
        """验证输入参数"""
        print(f"[Builder] 验证输入参数:")

        # 等级验证
        if not (1 <= level <= 60):
            print(f"[Builder] 警告: 等级 {level} 超出范围(1-60)")

        # 突破等级验证
        if not (0 <= breakthrough_level <= 6):
            print(f"[Builder] 警告: 突破等级 {breakthrough_level} 超出范围(0-6)")

        # 核心技等级验证
        if not (1 <= core_passive_level <= 7):
            print(f"[Builder] 警告: 核心技等级 {core_passive_level} 超出范围(1-7)")

        print(f"[Builder] 输入参数验证通过")

    def _print_stats_summary(self, stats: CharacterBaseStats):
        """打印属性摘要"""
        print(f"[Builder] 角色属性摘要:")
        print(f"[Builder]   等级: {stats.Level}")
        print(f"[Builder]   突破: {stats.BreakthroughLevel}")
        print(f"[Builder]   核心技: {stats.CorePassiveLevel}")

        # 主要属性
        if stats.HP > 0:
            print(f"[Builder]   生命值: {stats.HP:.0f}")
        if stats.ATK > 0:
            print(f"[Builder]   攻击力: {stats.ATK:.0f}")
        if stats.DEF > 0:
            print(f"[Builder]   防御力: {stats.DEF:.0f}")
        if stats.Sheer_Force > 0:
            print(f"[Builder]   贯穿力: {stats.Sheer_Force:.0f}")

        # 统计属性数量
        non_zero_count = len([v for v in vars(stats).values() if v != 0])
        print(f"[Builder]   总计 {non_zero_count} 个非零属性")

    def _format_value(self, field: str, value: float) -> str:
        """格式化属性值显示"""
        if field in ["CRIT_Rate", "CRIT_DMG", "PEN_Ratio", "Energy_Regen"]:
            return f"{value:.2%}"
        elif field in ["HP", "ATK", "DEF", "Impact", "Anomaly_Mastery",
                       "Anomaly_Proficiency", "PEN", "Sheer_Force"]:
            return f"{value:.0f}"
        else:
            return f"{value:.2f}"