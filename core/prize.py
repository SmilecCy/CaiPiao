"""双色球中奖等级判定

规则：
- 一等奖：6 红 + 1 蓝
- 二等奖：6 红 + 0 蓝
- 三等奖：5 红 + 1 蓝
- 四等奖：5 红 + 0 蓝 或 4 红 + 1 蓝
- 五等奖：4 红 + 0 蓝 或 3 红 + 1 蓝
- 六等奖：2 红 + 1 蓝 或 1 红 + 1 蓝 或 0 红 + 1 蓝
- 未中奖：其他
"""

from dataclasses import dataclass


@dataclass
class PrizeResult:
    """中奖结果"""

    level: int
    name: str
    red_hit: int
    blue_hit: bool

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "name": self.name,
            "red_hit": self.red_hit,
            "blue_hit": self.blue_hit,
        }


PRIZE_NONE = PrizeResult(level=0, name="未中奖", red_hit=0, blue_hit=False)

_PRIZE_RULES = [
    (6, True, 1, "一等奖"),
    (6, False, 2, "二等奖"),
    (5, True, 3, "三等奖"),
    (5, False, 4, "四等奖"),
    (4, True, 4, "四等奖"),
    (4, False, 5, "五等奖"),
    (3, True, 5, "五等奖"),
    (2, True, 6, "六等奖"),
    (1, True, 6, "六等奖"),
    (0, True, 6, "六等奖"),
]


def check_prize(
    user_red: list[int],
    user_blue: int,
    draw_red: list[int],
    draw_blue: int,
) -> PrizeResult:
    """判定用户号码相对某期开奖号码的中奖等级

    Args:
        user_red: 用户的红球列表
        user_blue: 用户的蓝球号码
        draw_red: 开奖红球列表
        draw_blue: 开奖蓝球号码

    Returns:
        PrizeResult 中奖结果
    """
    red_set = set(draw_red)
    red_hit = sum(1 for n in user_red if n in red_set)
    blue_hit = user_blue == draw_blue

    for need_red, need_blue, level, name in _PRIZE_RULES:
        if red_hit == need_red and blue_hit == need_blue:
            return PrizeResult(
                level=level,
                name=name,
                red_hit=red_hit,
                blue_hit=blue_hit,
            )

    return PrizeResult(
        level=0,
        name="未中奖",
        red_hit=red_hit,
        blue_hit=blue_hit,
    )