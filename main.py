"""双色球模拟器入口 - 启动 Web 服务"""

import logging
import os

import uvicorn

from core.logger import setup_logging


if __name__ == "__main__":
    setup_logging(level=logging.INFO)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    uvicorn.run("web.api:app", host=host, port=port, reload=reload)