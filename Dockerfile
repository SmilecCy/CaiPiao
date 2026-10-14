# 双色球模拟器 - Docker 镜像构建文件
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_NO_CACHE=1

WORKDIR /app

# 安装 uv
RUN pip install --no-cache-dir uv

# 先复制依赖声明文件，利用 Docker 缓存层
COPY pyproject.toml uv.lock* ./

# 安装运行时依赖（不含开发依赖）
RUN uv sync --frozen --no-dev || uv sync --no-dev

# 复制应用代码
COPY core ./core
COPY storage ./storage
COPY web ./web
COPY main.py ./

# 创建数据和日志目录（用于挂载卷）
RUN mkdir -p /app/data /app/logs

# 暴露容器内部端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "python", "main.py"]