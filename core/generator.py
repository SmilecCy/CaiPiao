"""双色球号码生成器"""

import random

from .logger import get_logger
from .validator import validate

logger = get_logger(__name__)

RED_MIN = 1
RED_MAX = 33
RED_COUNT = 6
BLUE_MIN = 1
BLUE_MAX = 16


def generate(seed: int | None = None) -> tuple[list[int], int]:
    """随机生成一注双色球号码

    Args:
        seed: 随机种子，传入固定值可复现结果，默认 None 使用系统随机源

    Returns:
        (red, blue) 红球列表（升序）和蓝球号码
    """
    rng = random.Random(seed)
    red = sorted(rng.sample(range(RED_MIN, RED_MAX + 1), RED_COUNT))
    blue = rng.randint(BLUE_MIN, BLUE_MAX)
    validate(red, blue)
    logger.info("生成号码: red=%s, blue=%d", red, blue)
    return red, blue


def generate_many(count: int, seed: int | None = None) -> list[tuple[list[int], int]]:
    """批量生成多注双色球号码

    Args:
        count: 生成注数
        seed: 随机种子

    Returns:
        注数列表，每注为 (red, blue)

    Raises:
        ValueError: 当 count 小于 1 时
    """
    if count < 1:
        logger.error("批量生成失败，注数非法: %d", count)
        raise ValueError(f"生成注数必须大于等于 1，当前为 {count}")
    rng = random.Random(seed)
    results: list[tuple[list[int], int]] = []
    for _ in range(count):
        red = sorted(rng.sample(range(RED_MIN, RED_MAX + 1), RED_COUNT))
        blue = rng.randint(BLUE_MIN, BLUE_MAX)
        validate(red, blue)
        results.append((red, blue))
    logger.info("批量生成 %d 注号码", count)
    return results