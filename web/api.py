"""Web API 服务层"""

import uuid
from datetime import datetime

from fastapi import Cookie, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from core.generator import generate, generate_many
from core.prize import check_prize
from crawler.ssq import fetch_ssq_history_dicts
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


def _parse_draw_date(date_str: str) -> datetime | None:
    """解析开奖日期字符串，如 '2026-10-13(二)'"""
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d")
    except (ValueError, IndexError):
        return None


def _attach_prize(records: list[dict], draws: list[dict]) -> list[dict]:
    """为每条历史记录附加中奖信息

    匹配规则：用户生成号码的时间必须早于开奖时间（先买后开），
    取用户生成时间之后最近的一期已开奖号码进行匹配；
    若该时间之后尚无开奖数据，则标记为"未开奖"。

    Args:
        records: 用户历史记录列表
        draws: 开奖记录列表（按时间倒序）

    Returns:
        附加了 prize 字段的记录列表
    """
    draw_list = []
    for d in draws:
        dt = _parse_draw_date(d.get("date", ""))
        if dt is not None:
            draw_list.append((dt, d))
    draw_list.sort(key=lambda x: x[0])

    enriched = []
    for rec in records:
        try:
            user_time = datetime.strptime(rec["time"], "%Y-%m-%d %H:%M:%S")
        except (KeyError, ValueError):
            user_time = None

        matched_draw = None
        if user_time is not None:
            for dt, d in draw_list:
                if dt >= user_time:
                    matched_draw = d
                    break

        if matched_draw is not None:
            prize = check_prize(
                user_red=rec.get("red", []),
                user_blue=rec.get("blue", 0),
                draw_red=matched_draw.get("red", []),
                draw_blue=matched_draw.get("blue", 0),
            )
            rec["prize"] = prize.to_dict()
            rec["matched_draw"] = {
                "code": matched_draw.get("code", ""),
                "date": matched_draw.get("date", ""),
            }
        else:
            rec["prize"] = {"level": 0, "name": "未开奖", "red_hit": 0, "blue_hit": False}
            rec["matched_draw"] = None

        enriched.append(rec)
    return enriched


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
    """获取当前用户的历史记录（含中奖等级匹配）"""
    user_id = get_or_create_user_id(request, response)
    records = history.load_history(user_id)
    draws = fetch_ssq_history_dicts(count=100)
    records = _attach_prize(records, draws)
    return {"records": records}


@app.delete("/api/history")
def api_clear_history(request: Request, response: Response) -> dict:
    """清空当前用户的历史记录"""
    user_id = get_or_create_user_id(request, response)
    history.clear_history(user_id)
    return {"message": "历史记录已清空"}


@app.get("/api/draws")
def api_draws(count: int = 8) -> dict:
    """获取双色球最近开奖数据

    Args:
        count: 获取期数，默认 8 期

    Returns:
        包含开奖记录列表的字典
    """
    draws = fetch_ssq_history_dicts(count)
    return {"draws": draws}