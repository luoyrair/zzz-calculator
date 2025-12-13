from math import floor

from src.calculators.character_calculator import CharacterAttributeCalculator

c = CharacterAttributeCalculator()

d = c.calculate_character_attributes(
    "../data/characters/1091.json", 60, 6, 7
)

o = {
    "生命值": d.hp,
    "攻击力": d.attack,
    "防御力": d.defence,
    "冲击力": d.impact,
    "暴击率": d.crit_rate,
    "暴击伤害": d.crit_dmg,
    "异常掌控": d.anomaly_mastery,
    "异常精通": d.anomaly_proficiency,
    "穿透率": d.pen_ratio,
    "能量自动回复": d.energy_regen
}
for key, value in o.items():
    if key in ["暴击率", "暴击伤害", "穿透率"]:
        # 百分比类型：显示一位小数（转换为百分比）
        formatted = f"{value * 100:.1f}"
        o[key] = float(formatted)
    elif key == "能量自动回复":
        # 能量自动回复：保留原样
        continue
    else:
        # 其他数值类型：向下取整
        o[key] = int(floor(value))
print(o)