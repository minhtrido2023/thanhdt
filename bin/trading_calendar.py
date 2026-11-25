#!/usr/bin/env python3
"""Lớp đọc lịch giao dịch dùng chung cho tooling điều phối — KHÔNG phải nguồn lịch.

Nguồn lịch DUY NHẤT vẫn là `trading_bot/vn_market.py` (_FIXED_HOLIDAYS/_VARIABLE_HOLIDAYS, sửa tay khi
có thông báo SSI/HOSE). File này chỉ: (1) hỏi "ngày D có giao dịch không" kèm bằng chứng in được (§28),
(2) liệt kê ngày T2-T6 sắp tới CHƯA được người xác nhận lịch (mốc trong FILE DỮ LIỆU
`config/trading_calendar_confirmed.json` — ngoài trading_bot, sửa mốc không đụng module executor import;
thiếu/null/không có `source` ⇒ coi như chưa xác nhận ngày nào — fail-safe về phía CẢNH BÁO, không đoán lễ).
Thêm 2026-11-25 (sự cố "không ra plan 25/11": lễ 24/11 khai SAU chuỗi 19:00-23:00 ngày 23/11).
"""
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

WC_ROOT = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
if WC_ROOT not in sys.path:
    sys.path.insert(0, WC_ROOT)
try:
    from trading_bot import vn_market as VM  # noqa: E402
    _VM_ERR = None
except Exception as _exc:  # noqa: BLE001 — §28: import hỏng KHÔNG được ra rc=1 (= "ngày giao dịch") của CLI
    VM, _VM_ERR = None, _exc
    if __name__ != "__main__":
        raise

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
CONFIRMED_FILE = os.environ.get("TC_CONFIRMED_FILE") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "trading_calendar_confirmed.json")
WD = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]


def today_ict():
    raw = os.environ.get("MIKE_NOW_ICT")  # chỉ cho selfcheck
    return (dt.datetime.fromisoformat(raw) if raw else dt.datetime.now(ICT)).date()


def as_date(d):
    return d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d)[:10])


def is_trading_day(d):
    d = as_date(d)
    return d.weekday() < 5 and not VM.is_holiday(d)


def non_trading_evidence(d):
    """None nếu D là ngày giao dịch; ngược lại chuỗi bằng chứng (dùng làm --evidence khi đóng question)."""
    d = as_date(d)
    if is_trading_day(d):
        return None
    why = "cuối tuần" if d.weekday() >= 5 else "ngày lễ đã khai"
    return (f"{d.isoformat()} ({WD[d.weekday()]}) KHÔNG phải ngày giao dịch — {why}: "
            f"trading_bot.vn_market.is_holiday({d.isoformat()})={VM.is_holiday(d)}, weekday={d.weekday()}")


def confirmed_through():
    """Mốc người đã đối chiếu lịch (file dữ liệu). Thiếu file / JSON hỏng / ngày sai / KHÔNG có source ⇒ None."""
    try:
        with open(CONFIRMED_FILE, encoding="utf-8") as f:
            j = json.load(f)
        v, src = j.get("confirmed_through"), str(j.get("source") or "").strip()
        return as_date(v) if (v and src) else None
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def upcoming(today=None, days=14):
    """Cửa sổ (today, today+days]: ngày nghỉ T2-T6 đã khai + ngày T2-T6 giao dịch CHƯA xác nhận lịch."""
    today = as_date(today or today_ict())
    ct = confirmed_through()
    hol, unconf = [], []
    for i in range(1, days + 1):
        d = today + dt.timedelta(days=i)
        if d.weekday() >= 5:
            continue
        if VM.is_holiday(d):
            hol.append(d)
        elif ct is None or d > ct:
            unconf.append(d)
    return {"today": today, "end": today + dt.timedelta(days=days), "confirmed_through": ct,
            "holidays": hol, "unconfirmed": unconf}


def fmt_day(d):
    return f"{WD[d.weekday()]} {d.strftime('%d/%m')}"


def main(argv=None):
    """CLI: `trading_calendar.py --evidence YYYY-MM-DD` → rc 0 + in bằng chứng nếu KHÔNG giao dịch,
    rc 1 nếu là ngày giao dịch, rc 2 nếu LỖI (ngày sai định dạng / import vn_market hỏng / exception) —
    §28: rc 1 chỉ có nghĩa "đã đọc lịch và đó là ngày giao dịch"; crash KHÔNG bao giờ ra rc 1. `--upcoming [N]` → in cửa sổ N ngày."""
    argv = sys.argv[1:] if argv is None else argv
    if VM is None:
        print(f"trading_calendar: ERROR không import được trading_bot.vn_market từ {WC_ROOT}: "
              f"{type(_VM_ERR).__name__}: {_VM_ERR}")
        return 2
    try:
        if argv[:1] == ["--evidence"] and len(argv) == 2:
            ev = non_trading_evidence(argv[1])
            print(ev or f"{as_date(argv[1]).isoformat()} là ngày giao dịch")
            return 0 if ev else 1
        if argv[:1] == ["--upcoming"]:
            u = upcoming(days=int(argv[1]) if len(argv) > 1 else 14)
            print("holidays=" + ",".join(map(str, u["holidays"])) + " unconfirmed=" +
                  ",".join(map(str, u["unconfirmed"])) + f" confirmed_through={u['confirmed_through']}")
            return 0
    except Exception as exc:  # noqa: BLE001 — mọi lỗi ⇒ rc 2, không bao giờ trùng rc 0/1 có nghĩa
        print(f"trading_calendar: ERROR {type(exc).__name__}: {exc}")
        return 2
    print("usage: trading_calendar.py --evidence YYYY-MM-DD | --upcoming [N]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
