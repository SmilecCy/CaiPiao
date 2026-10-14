"""双色球号码合法性校验"""

RED_MIN = 1
RED_MAX = 33
RED_COUNT = 6
BLUE_MIN = 1
BLUE_MAX = 16
BLUE_COUNT = 1


class ValidationError(ValueError):
    """号码校验失败时抛出"""


def validate_red(red: list[int]) -> None:
    """校验红球列表

    Args:
        red: 红球号码列表

    Raises:
        ValidationError: 当红球数量、范围或唯一性不满足规则时
    """
    if len(red) != RED_COUNT:
        raise ValidationError(f"红球数量必须为 {RED_COUNT} 个，当前为 {len(red)} 个")
    seen: set[int] = set()
    for num in red:
        if not isinstance(num, int) or isinstance(num, bool):
            raise ValidationError(f"红球号码必须为整数，非法值: {num!r}")
        if not (RED_MIN <= num <= RED_MAX):
            raise ValidationError(f"红球号码必须在 {RED_MIN}-{RED_MAX} 之间，非法值: {num}")
        if num in seen:
            raise ValidationError(f"红球号码不能重复，重复值: {num}")
        seen.add(num)


def validate_blue(blue: int) -> None:
    """校验蓝球号码

    Args:
        blue: 蓝球号码

    Raises:
        ValidationError: 当蓝球范围不满足规则时
    """
    if not isinstance(blue, int) or isinstance(blue, bool):
        raise ValidationError(f"蓝球号码必须为整数，非法值: {blue!r}")
    if not (BLUE_MIN <= blue <= BLUE_MAX):
        raise ValidationError(f"蓝球号码必须在 {BLUE_MIN}-{BLUE_MAX} 之间，非法值: {blue}")


def validate(red: list[int], blue: int) -> None:
    """同时校验红球和蓝球

    Args:
        red: 红球号码列表
        blue: 蓝球号码

    Raises:
        ValidationError: 当红球或蓝球不满足规则时
    """
    validate_red(red)
    validate_blue(blue)