#!/usr/bin/env python3
"""Chụp TOÀN BỘ câu trả lời của `oshares_at` trên một rổ/asof, cho CẢ HAI nhánh, ra JSON.

Mục đích DUY NHẤT: đo delta giữa hai bản code (trước/sau cửa sổ nhìn lùi 2026-08-20) bằng cách
chạy CÙNG script này từ hai cây làm việc rồi diff hai file JSON. Không tự so sánh gì bên trong —
so sánh là việc của `diff_snapshots.py`, để hai vế của phép đo không bao giờ dùng chung một bản
code.

Rổ = `ticker_prune` tại phiên cuối <= asof (point-in-time, giống `lookahead_cost_probe.py`, nên
hai phép đo trích dẫn được cùng một con số "263 mã").

Chạy:  WORKDIR_8L=<cây> python3 snapshot_probe.py --asof 2026-03-01 --out snap_<nhãn>.json
"""
import argparse
import json
import os
import sys

WC = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WC)
os.environ.pop("BQ_LOCAL_CACHE", None)

from corp_action_lib import bq                                          # noqa: E402
from oshares_live import _fetch, oshares_at                             # noqa: E402

PRUNE = "lithe-record-440915-m9.tav2_bq.ticker_prune"
KEEP = ("value", "method", "anchor_date", "anchor_value", "anchor_source", "anchor_verified")


def universe(asof):
    rows = bq(f"""
        SELECT DISTINCT ticker FROM `{PRUNE}`
        WHERE time = (SELECT MAX(time) FROM `{PRUNE}` WHERE time <= "{asof}")
        ORDER BY ticker""")
    return [r["ticker"] for r in rows]


def restate_hits(corp, tk, asof, value):
    """AIS SAU `asof` có `shares_total_after` trùng khít `value` — chữ ký look-ahead.

    Định nghĩa GIỮ NGUYÊN từ `lookahead_cost_probe.py` để hai probe trích dẫn được lẫn nhau.
    """
    if value is None:
        return []
    return sorted(c["effective_date"] for c in corp
                  if c["ticker"] == tk and c["event_code"] == "AIS"
                  and c.get("shares_total_after") and c.get("effective_date")
                  and c["effective_date"] > asof
                  and abs(float(c["shares_total_after"]) - float(value)) < 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default="2026-03-01")
    ap.add_argument("--future-until", default="2026-08-20")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tks = universe(a.asof)
    print(f"[universe] {len(tks)} mã tại phiên cuối <= {a.asof} (WC={WC})", flush=True)
    cache = _fetch(tks, a.future_until)
    corp = cache[1]
    snap = {"wc": WC, "asof": a.asof, "future_until": a.future_until,
            "n_universe": len(tks), "tickers": tks, "branches": {}}
    for tag, live in (("pit", False), ("live", True)):
        res = oshares_at(tks, a.asof, _cache=cache, live=live)
        snap["branches"][tag] = {
            tk: {**{k: res[tk].get(k) for k in KEEP},
                 "restate_future_ais": restate_hits(corp, tk, a.asof, res[tk]["value"]),
                 "absorption": (res[tk].get("absorption_test") or {}).get("verdict")}
            for tk in tks}
        n_none = sum(1 for tk in tks if res[tk]["value"] is None)
        print(f"[{tag}] từ chối {n_none}/{len(tks)}", flush=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, ensure_ascii=False, indent=1)
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
