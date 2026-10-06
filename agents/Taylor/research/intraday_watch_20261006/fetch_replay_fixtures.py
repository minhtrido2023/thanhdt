#!/usr/bin/env python3
"""Tải dữ liệu PHÚT (DNSE /price/ohlc resolution=1, chỉ đọc market data) cho replay selfcheck
intraday_price_watch — ghi ra fixtures/replay_bars.json để selfcheck chạy offline, tất định.

Ca: PNJ 23/09→05/10 (HOSE), DGC 22-23/07 (HOSE, đang bị hạn chế ⇒ chỉ khớp định kỳ), TV1 15-16/07
(UPCOM), VNINDEX cùng ngày. Tham chiếu = giá đóng cửa 1D phiên trước (UPCOM thật dùng BÌNH QUÂN
phiên trước — giới hạn ghi rõ trong selfcheck). Chạy: $DNA_PYEXE fetch_replay_fixtures.py
"""
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from trading_bot.brokers import get_dnse_client  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
HERE = os.path.dirname(os.path.abspath(__file__))
CASES = {
    "PNJ": ("stock", "HOSE", ["2026-09-24", "2026-09-25", "2026-09-28", "2026-09-29",
                               "2026-09-30", "2026-10-01", "2026-10-02", "2026-10-05"]),
    "DGC": ("stock", "HOSE", ["2026-07-22", "2026-07-23"]),
    "TV1": ("stock", "UPCOM", ["2026-07-15", "2026-07-16"]),
}


def _bars(c, sym, typ, day):
    a = dt.datetime.fromisoformat(day + "T08:30").replace(tzinfo=ICT)
    b = a + dt.timedelta(hours=7)
    r = c.ohlc(sym, resolution="1", bar_type=typ, **{"from": int(a.timestamp()), "to": int(b.timestamp())})
    out = []
    for i, t in enumerate(r.get("t", [])):
        hhmm = dt.datetime.fromtimestamp(t, ICT).strftime("%H:%M")
        out.append([hhmm, r["o"][i], r["h"][i], r["l"][i], r["c"][i], r["v"][i]])
    return out


def _daily(c, sym, typ, d0, d1):
    a = dt.datetime.fromisoformat(d0 + "T00:00").replace(tzinfo=ICT)
    b = dt.datetime.fromisoformat(d1 + "T23:00").replace(tzinfo=ICT)
    r = c.ohlc(sym, resolution="1D", bar_type=typ, **{"from": int(a.timestamp()), "to": int(b.timestamp())})
    return {dt.datetime.fromtimestamp(t, ICT).strftime("%Y-%m-%d"): r["c"][i] for i, t in enumerate(r.get("t", []))}


def main():
    c = get_dnse_client()
    out = {"source": "DNSE /price/ohlc resolution=1 (đơn vị nghìn đồng), tải " +
           dt.datetime.now(ICT).strftime("%Y-%m-%d %H:%M ICT"), "cases": {}}
    for sym, (typ, exch, days) in CASES.items():
        d0 = (dt.date.fromisoformat(days[0]) - dt.timedelta(days=10)).isoformat()
        daily = _daily(c, sym, typ, d0, days[-1])
        vdaily = _daily(c, "VNINDEX", "index", d0, days[-1])
        out["cases"][sym] = {"exchange": exch, "daily_close": daily, "vni_daily_close": vdaily,
                             "days": {d: {"bars": _bars(c, sym, typ, d),
                                          "vni_bars": _bars(c, "VNINDEX", "index", d)} for d in days}}
        print(sym, {d: len(v["bars"]) for d, v in out["cases"][sym]["days"].items()})
    p = os.path.join(HERE, "fixtures", "replay_bars.json")
    with open(p, "w") as f:
        json.dump(out, f, ensure_ascii=False)
    print("ghi", p, os.path.getsize(p), "bytes")


if __name__ == "__main__":
    main()
