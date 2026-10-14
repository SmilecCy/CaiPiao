"""历史记录持久化（JSON 存储，按用户隔离）"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _history_file(user_id: str) -> Path:
    """获取指定用户的历史记录文件路径"""
    return DATA_DIR / f"history_{user_id}.json"


def load_history(user_id: str) -> list[dict]:
    """读取指定用户的全部历史记录

    Args:
        user_id: 用户标识

    Returns:
        历史记录列表，每条记录包含 time、red、blue、batch 字段；文件不存在时返回空列表
    """
    history_file = _history_file(user_id)
    if not history_file.exists():
        logger.debug("用户 %s 历史记录文件不存在，返回空列表", user_id)
        return []
    try:
        with history_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            logger.warning("用户 %s 历史记录文件格式异常（非列表），返回空列表", user_id)
            return []
        logger.info("用户 %s 读取历史记录 %d 条", user_id, len(data))
        return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("用户 %s 读取历史记录失败: %s", user_id, exc)
        return []


def save_record(red: list[int], blue: int, user_id: str) -> None:
    """追加保存一条生成记录（单注）

    Args:
        red: 红球列表
        blue: 蓝球号码
        user_id: 用户标识
    """
    save_records([(red, blue)], user_id)


def save_records(tickets: list[tuple[list[int], int]], user_id: str) -> None:
    """批量保存一组生成记录（同批次共享时间与批次号）

    Args:
        tickets: (red, blue) 列表
        user_id: 用户标识
    """
    if not tickets:
        return
    _ensure_data_dir()
    history = load_history(user_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    batch = uuid.uuid4().hex[:8]
    for red, blue in tickets:
        history.append({
            "time": now,
            "red": list(red),
            "blue": blue,
            "batch": batch,
        })
    history_file = _history_file(user_id)
    with history_file.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    logger.info("用户 %s 批量保存 %d 条记录，累计 %d 条", user_id, len(tickets), len(history))


def clear_history(user_id: str) -> None:
    """清空指定用户的全部历史记录

    Args:
        user_id: 用户标识
    """
    _ensure_data_dir()
    history_file = _history_file(user_id)
    with history_file.open("w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    logger.info("用户 %s 已清空全部历史记录", user_id)