# 欢乐双色球 · CaiPiao

一个简洁清新的双色球号码模拟器，支持 Web 端和命令行两种使用方式。

## 功能特性

- 🎱 **号码生成**：机选红球 6 个（1-33 不重复）+ 蓝球 1 个（1-16），支持批量多注
- 🎰 **摇奖机动画**：圆形滚筒 + 搅拌杆旋转，球在轨道上滚动，模拟真实摇奖场景
- 📋 **历史记录**：每次生成的号码自动保存，可查看与清空
- 👤 **多用户隔离**：基于 Cookie 标识用户，每位用户的历史记录相互独立
- 📱 **响应式适配**：页面按屏幕比例等比例缩放，完美适配手机与桌面端
- 📝 **日志记录**：自动记录运行日志，支持按大小（2MB）和时间（7天）轮转清理

## 双色球规则

- 红球：从 **1–33** 中选 **6** 个（不重复）
- 蓝球：从 **1–16** 中选 **1** 个

## 项目结构

```
CaiPiao/
├── main.py                 # 程序入口（启动 Web 服务）
├── pyproject.toml          # 项目配置 & 依赖
├── Dockerfile              # Docker 镜像构建文件
├── docker-compose.yml      # Docker Compose 编排
│
├── core/                   # 核心逻辑
│   ├── generator.py        # 号码生成器
│   ├── validator.py        # 号码合法性校验
│   └── logger.py           # 日志模块
│
├── storage/                # 数据持久化
│   └── history.py          # 历史记录读写（按用户隔离，JSON 存储）
│
├── cli/                    # 命令行交互层
│   └── app.py
│
├── web/                    # Web 前端 & API
│   ├── api.py              # FastAPI 后端接口
│   ├── index.html          # 页面结构
│   ├── style.css           # 样式（毛玻璃透明模块风格）
│   └── app.js              # 交互逻辑与动画
│
├── data/                   # 历史记录数据（运行时生成）
├── logs/                   # 日志文件（运行时生成）
└── tests/                  # 单元测试
```

## 快速开始

### 环境要求

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) 包管理器

### 安装依赖

```bash
uv sync
```

### 启动 Web 服务

```bash
uv run python main.py
```

服务默认运行在 `http://127.0.0.1:8000`，浏览器访问即可使用。

#### 环境变量配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HOST` | `0.0.0.0` | 监听地址 |
| `PORT` | `8000` | 监听端口 |
| `RELOAD` | `false` | 是否开启热重载（开发时设为 `true`） |

### 使用命令行模式

```bash
uv run python -m cli.app
```

> CLI 模式使用独立的用户标识（`cli`），与 Web 端的历史记录相互隔离。

### 运行测试

```bash
uv run pytest tests/ -v
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 首页 |
| `POST` | `/api/generate?count=N` | 生成 N 注号码（默认 1 注） |
| `GET` | `/api/history` | 获取当前用户的历史记录 |
| `DELETE` | `/api/history` | 清空当前用户的历史记录 |

## Docker 部署

### 使用 docker compose（推荐）

```bash
docker compose up -d --build
```

容器内端口 `8000` 映射到宿主机 `8888`，访问 `http://服务器IP:8888`。

### 纯 Docker 命令

```bash
# 构建镜像
docker build -t caipiao .

# 运行容器
docker run -d \
  --name caipiao \
  -p 8888:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  caipiao
```



## 多用户隔离说明

- Web 端通过 Cookie（`cp_user_id`）标识用户，每个浏览器/设备拥有独立的历史记录
- 历史记录以 `data/history_{user_id}.json` 形式存储，互不干扰
- CLI 端使用固定用户标识 `cli`

## 日志策略

- 日志输出到控制台与 `logs/app.log` 文件
- 单文件最大 **2 MB**，保留 **7 个**备份，超出自动删除最旧
- 文件保存 **7 天**，过期自动清理
