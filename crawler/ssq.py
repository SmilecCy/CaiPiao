"""双色球历史开奖数据爬虫

数据来源：中国福利彩票发行管理中心官网
https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

from core.logger import get_logger

logger = get_logger(__name__)

API_URL = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
REFERER = "https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class SsqDraw:
    """双色球开奖记录"""

    code: str
    date: str
    red: list[int] = field(default_factory=list)
    blue: int = 0
    sales: str = ""
    poolmoney: str = ""

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "date": self.date,
            "red": self.red,
            "blue": self.blue,
            "sales": self.sales,
            "poolmoney": self.poolmoney,
        }


def fetch_ssq_history(count: int = 8) -> list[SsqDraw]:
    """获取双色球最近 N 期开奖数据

    Args:
        count: 获取期数，默认 8 期

    Returns:
        开奖记录列表，按时间倒序排列（最新在前）
    """
    params = {
        "name": "ssq",
        "issueCount": "",
        "issueStart": "",
        "issueEnd": "",
        "dayStart": "",
        "dayEnd": "",
        "pageNo": "1",
        "pageSize": str(count),
        "week": "",
        "systemType": "PC",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": REFERER,
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        logger.error("请求福彩网失败: %s", e)
        return []
    except json.JSONDecodeError as e:
        logger.error("解析福彩网返回数据失败: %s", e)
        return []

    results = data.get("result", [])
    draws: list[SsqDraw] = []
    for item in results:
        try:
            red = [int(x) for x in item["red"].split(",")]
            blue = int(item["blue"])
        except (KeyError, ValueError) as e:
            logger.warning("跳过无效开奖记录: %s", e)
            continue

        draws.append(
            SsqDraw(
                code=item.get("code", ""),
                date=item.get("date", ""),
                red=red,
                blue=blue,
                sales=item.get("sales", ""),
                poolmoney=item.get("poolmoney", ""),
            )
        )

    logger.info("成功获取双色球开奖数据 %d 期", len(draws))
    return draws


def fetch_ssq_history_dicts(count: int = 8) -> list[dict]:
    """获取双色球最近 N 期开奖数据（dict 格式）

    Args:
        count: 获取期数，默认 8 期

    Returns:
        开奖记录字典列表
    """
    return [d.to_dict() for d in fetch_ssq_history(count)]


if __name__ == "__main__":
    records = fetch_ssq_history(8)
    for r in records:
        red_str = " ".join(f"{n:02d}" for n in r.red)
        print(f"第{r.code}期  {r.date}  红球:{red_str}  蓝球:{r.blue:02d}")