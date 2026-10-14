"""日志记录模块

提供统一的日志配置，同时输出到控制台和日志文件。

轮转策略：
- 按大小轮转：单个文件最大 2 MB，最多保留 7 个备份文件。
- 按时间清理：日志文件保存 7 天，超时自动删除。
"""

import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "app.log"

MAX_BYTES = 2 * 1024 * 1024
BACKUP_COUNT = 7
RETENTION_SECONDS = 7 * 24 * 60 * 60
CLEANUP_INTERVAL_SECONDS = 60 * 60

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


class CleanupRotatingFileHandler(RotatingFileHandler):
    """带过期清理的按大小轮转文件处理器"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._last_cleanup = 0.0

    def emit(self, record: logging.LogRecord) -> None:
        try:
            super().emit(record)
        finally:
            self._maybe_cleanup()

    def _maybe_cleanup(self) -> None:
        now = time.time()
        if now - self._last_cleanup < CLEANUP_INTERVAL_SECONDS:
            return
        self._last_cleanup = now
        self._cleanup_expired()

    def _cleanup_expired(self) -> None:
        now = time.time()
        cutoff = now - RETENTION_SECONDS
        for log_file in LOG_DIR.glob("app.log*"):
            try:
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    logging.getLogger(__name__).info(
                        "已清理过期日志文件: %s", log_file.name
                    )
            except OSError:
                pass


def setup_logging(level: int = logging.INFO) -> None:
    """初始化全局日志配置（只需调用一次）

    Args:
        level: 日志级别，默认 INFO
    """
    global _initialized
    if _initialized:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    file_handler = CleanupRotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的 logger

    Args:
        name: 日志器名称，通常传 __name__

    Returns:
        配置好的 Logger 实例
    """
    if not _initialized:
        setup_logging()
    return logging.getLogger(name)