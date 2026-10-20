#!/usr/bin/env python3
"""intraday_oos_monthly.py — số liệu tích luỹ OOS của shadow intraday cutloss, cho mục NỘI BỘ của báo cáo tháng.

Đọc `data/intraday_watch/shadow_<ngày>.jsonl` (chỉ đọc). Chỉ đếm — KHÔNG chấm H1, không suy ra alpha.
Mốc quyết định (PREREG ADDENDUM 09/10/2026): ≥30 NGÀY có ca live trên mã ADV20 ≥ 10 tỷ.
File này không có ADV20 ⇒ cột `ngay_co_ca` là CẬN TRÊN của tử số; lọc ADV20 làm lúc chấm H1.

    intraday_oos_monthly.py --month 2026-10 [--json]
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import sys

WC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_DIR = os.path.join(WC, "data", "intraday_watch")
OOS_START = dt.date(2026, 10, 12)      # shadow chạy code luật (A)(B)(C)(D) từ ngày này
TARGET_DAYS = 30


def _events(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass            # dòng cụt do crash giữa chừng (ca ENOSPC 12/10) — bỏ, đếm ở `dong_hong`
    return out


def _day_stats(path):
    ev = _events(path)
    total = sum(1 for _ in open(path, encoding="utf-8"))
    kinds = collections.Counter(e.get("kind") for e in ev)
    case_tk = set()
    for e in ev:
        if e.get("kind") == "EOD_OOS":
            for r in e.get("rows") or []:
                if r.get("kind") == "case":
                    case_tk.add(r.get("ticker"))
    return {"scan": kinds["SCAN"], "eod_oos": kinds["EOD_OOS"], "crash": kinds["CRASH"],
            "quote_error": kinds["QUOTE_ERROR"], "health": kinds["HEALTH"],
            "dong_hong": total - len(ev), "case_tickers": sorted(case_tk)}


def summarize(month, state_dir=STATE_DIR):
    """month = 'YYYY-MM'. Trả dict: tháng + luỹ kế từ OOS_START."""
    first = dt.date.fromisoformat(month + "-01")
    nxt = (first.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    days = {}
    for p in sorted(glob.glob(os.path.join(state_dir, "shadow_*.jsonl"))):
        d = dt.date.fromisoformat(os.path.basename(p)[7:17])
        if d >= OOS_START and d < nxt:
            days[d] = _day_stats(p)
    in_m = {d: s for d, s in days.items() if first <= d < nxt}
    case_days = {d: s["case_tickers"] for d, s in days.items() if s["case_tickers"]}
    return {
        "month": month, "oos_start": OOS_START.isoformat(), "target_case_days": TARGET_DAYS,
        "thang": {
            "phien_co_log": len(in_m),
            "phien_thieu_eod_oos": sorted(d.isoformat() for d, s in in_m.items() if not s["eod_oos"]),
            "scan": sum(s["scan"] for s in in_m.values()),
            "crash": sum(s["crash"] for s in in_m.values()),
            "quote_error": sum(s["quote_error"] for s in in_m.values()),
            "health": sum(s["health"] for s in in_m.values()),
            "dong_hong": sum(s["dong_hong"] for s in in_m.values()),
            "ngay_co_ca": sorted(d.isoformat() for d in case_days if first <= d < nxt),
        },
        "luy_ke": {
            "phien_co_log": len(days),
            "ngay_co_ca": len(case_days),
            "ma_co_ca": sorted({t for v in case_days.values() for t in v}),
            "con_thieu_toi_muc_tieu": max(TARGET_DAYS - len(case_days), 0),
        },
        "luu_y": "ngay_co_ca = CẬN TRÊN (chưa lọc ADV20 ≥ 10 tỷ, chưa dedupe lại theo ngày-ca độc lập); "
                 "chỉ đếm, KHÔNG phải kết quả H1.",
    }


def render(r):
    t, k = r["thang"], r["luy_ke"]
    return "\n".join([
        f"Shadow intraday cutloss — tích luỹ OOS (từ {r['oos_start']}), tháng {r['month']}:",
        f"- Tháng: {t['phien_co_log']} phiên có log · {t['scan']} lượt quét · {t['crash']} crash · "
        f"{t['quote_error']} lỗi giá · {t['health']} cảnh báo sức khoẻ · {t['dong_hong']} dòng log hỏng · "
        f"thiếu EOD_OOS: {', '.join(t['phien_thieu_eod_oos']) or 'không'}",
        f"- Ngày có ca live trong tháng: {', '.join(t['ngay_co_ca']) or 'không có'}",
        f"- Luỹ kế: {k['ngay_co_ca']}/{r['target_case_days']} ngày có ca (cận trên, chưa lọc ADV20 ≥ 10 tỷ) "
        f"· còn thiếu ≥ {k['con_thieu_toi_muc_tieu']} · mã: {', '.join(k['ma_co_ca']) or '—'}",
        f"- {r['luu_y']}",
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--state-dir", default=STATE_DIR)
    a = ap.parse_args()
    r = summarize(a.month, a.state_dir)
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
