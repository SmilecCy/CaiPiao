"""双色球模拟 - 命令行交互层"""

from core.generator import generate, generate_many
from core.logger import get_logger
from storage import history

logger = get_logger(__name__)

CLI_USER_ID = "cli"


def _format_ticket(red: list[int], blue: int) -> str:
    red_str = " ".join(f"{n:02d}" for n in red)
    return f"红球: {red_str}  |  蓝球: {blue:02d}"


def _do_generate() -> None:
    try:
        raw = input("请输入生成注数（直接回车默认 1 注）: ").strip()
        count = int(raw) if raw else 1
    except ValueError:
        logger.warning("用户输入的注数不是整数: %s", raw)
        print("输入无效，请输入整数。")
        return

    if count < 1:
        logger.warning("用户输入的注数小于 1: %d", count)
        print("注数必须大于等于 1。")
        return

    if count == 1:
        red, blue = generate()
        history.save_record(red, blue, CLI_USER_ID)
        print(f"\n生成号码: {_format_ticket(red, blue)}\n")
    else:
        tickets = generate_many(count)
        print(f"\n共生成 {count} 注:\n")
        for i, (red, blue) in enumerate(tickets, 1):
            history.save_record(red, blue, CLI_USER_ID)
            print(f"  {i:02d}. {_format_ticket(red, blue)}")
        print()


def _do_show_history() -> None:
    records = history.load_history(CLI_USER_ID)
    if not records:
        print("\n暂无历史记录。\n")
        return
    print(f"\n历史记录（共 {len(records)} 条）:\n")
    for i, rec in enumerate(records, 1):
        red = rec.get("red", [])
        blue = rec.get("blue")
        time_str = rec.get("time", "")
        print(f"  {i:03d}. [{time_str}]  {_format_ticket(red, blue)}")
    print()


def _do_clear_history() -> None:
    confirm = input("确定要清空全部历史记录吗？(y/N): ").strip().lower()
    if confirm == "y":
        history.clear_history(CLI_USER_ID)
        print("历史记录已清空。\n")
    else:
        logger.info("用户取消清空历史记录")
        print("已取消。\n")


MENU = """
================== 双色球模拟器 ==================
  1. 机选号码
  2. 查看历史记录
  3. 清空历史记录
  0. 退出
=================================================
"""


def run() -> None:
    """启动 CLI 主循环"""
    logger.info("双色球模拟器启动")
    while True:
        print(MENU)
        choice = input("请选择操作: ").strip()
        logger.debug("用户选择菜单: %s", choice)
        if choice == "1":
            _do_generate()
        elif choice == "2":
            _do_show_history()
        elif choice == "3":
            _do_clear_history()
        elif choice == "0":
            logger.info("双色球模拟器退出")
            print("再见！")
            break
        else:
            logger.warning("无效菜单选择: %s", choice)
            print("无效选择，请重新输入。\n")