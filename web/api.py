"""Web API 服务层"""

import uuid

from fastapi import Cookie, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from core.generator import generate, generate_many
from storage import history

app = FastAPI(title="欢乐双色球")

WEB_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

USER_COOKIE = "cp_user_id"


def get_or_create_user_id(request: Request, response: Response) -> str:
    """从 Cookie 获取用户 ID，不存在则生成新 ID 并写入 Cookie"""
    user_id = request.cookies.get(USER_COOKIE)
    if not user_id:
        user_id = uuid.uuid4().hex
        response.set_cookie(
            key=USER_COOKIE,
            value=user_id,
            max_age=60 * 60 * 24 * 365,
            httponly=True,
            samesite="lax",
        )
    return user_id


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.post("/api/generate")
def api_generate(
    request: Request,
    response: Response,
    count: int = 1,
) -> dict:
    """生成号码

    Args:
        count: 生成注数，默认 1

    Returns:
        包含生成号码列表的字典
    """
    user_id = get_or_create_user_id(request, response)
    if count < 1:
        raise HTTPException(status_code=400, detail="注数必须大于等于 1")
    try:
        tickets = generate_many(count)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    history.save_records(tickets, user_id)
    return {"tickets": [{"red": red, "blue": blue} for red, blue in tickets]}


@app.get("/api/history")
def api_history(request: Request, response: Response) -> dict:
    """获取当前用户的历史记录"""
    user_id = get_or_create_user_id(request, response)
    return {"records": history.load_history(user_id)}


@app.delete("/api/history")
def api_clear_history(request: Request, response: Response) -> dict:
    """清空当前用户的历史记录"""
    user_id = get_or_create_user_id(request, response)
    history.clear_history(user_id)
    return {"message": "历史记录已清空"}