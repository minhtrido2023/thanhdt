#!/usr/bin/env python3
"""Print the [now: ...] context line for fleet hook injection (headless dispatch path).

Mirrors claude_discord.discord_ui.outbound_format.now_context_line() in the Discord
bridge (ccdb) so the fleet's headless dispatch path shows the same derived time+market
fact the Discord path shows — see
agents/Mike/research/discord_time_reasoning_by_construction_plan_20260821.md §S2.3.
Never raises: any failure degrades to the plain time line, never to no output at all.
"""
import datetime as dt
import sys
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
_VN_MARKET_DIR = "/home/trido/thanhdt/WorkingClaude/trading_bot"

_WEEKDAYS_VN = [
    "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật",
]

_PHASE_LABELS = {
    "ATO": "ATO — sắp khớp lệnh mở cửa",
    "MORNING": "ĐANG MỞ CỬA (phiên sáng)",
    "AFTERNOON": "ĐANG MỞ CỬA (phiên chiều)",
    "ATC": "ATC — sắp khớp lệnh đóng cửa",
}


def _market_suffix() -> str:
    try:
        sys.path.insert(0, _VN_MARKET_DIR)
        from vn_market import next_trading_day, now_ict, session_phase  # type: ignore

        phase, _cont = session_phase()
        if phase == "CLOSED":
            nd = next_trading_day(now_ict().date())
            wd = _WEEKDAYS_VN[nd.weekday()]
            return f" · HOSE: ĐÃ ĐÓNG CỬA — phiên kế tiếp {wd} {nd.strftime('%d/%m')} 09:00 ICT"
        if phase == "PRE":
            return " · HOSE: CHƯA MỞ CỬA — phiên sáng mở lúc 09:00 ICT"
        if phase == "LUNCH":
            return " · HOSE: NGHỈ TRƯA — phiên chiều mở lúc 13:00 ICT"
        label = _PHASE_LABELS.get(phase)
        return f" · HOSE: {label}" if label else ""
    except Exception:
        return ""


def now_line() -> str:
    now = dt.datetime.now(_ICT)
    wd = _WEEKDAYS_VN[now.weekday()]
    suffix = _market_suffix()
    return f"[now: {now.strftime('%H:%M')} ICT · {wd} {now.strftime('%d/%m/%Y')}{suffix}]"


if __name__ == "__main__":
    print(now_line())
