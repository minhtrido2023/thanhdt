#!/usr/bin/env python3
"""probe_sanity_direct_call.py — CÂU HỎI CÒN TREO vòng 4: người gọi THẲNG `oshares_at`
(`corp_action_daily.py`) có cần cổng biên độ `SANITY_FACTOR` không?

Cổng biên độ sống ở `oshares_pit` (lớp NGƯỜI TIÊU THỤ) và so số của `oshares_live` với SỐ NỀN CỦA
CALLER. `corp_action_daily.py` không đi qua lớp đó ⇒ nếu có ô lỗi thô nào chỉ cổng biên độ bắt
được, người gọi thẳng sẽ NUỐT nó.

Docstring `oshares_live` khẳng định con số đó là "~27 ô" (đo trên lưới custom30, bậc thang
12,44→12,51 ở ngưỡng 13-14×). Ở đây KHÔNG chép lại khẳng định — đo lại độc lập, trên một lưới
RỘNG HƠN custom30 (mọi mã có ít nhất một dòng AIS `executed`), và qua ĐÚNG đường gọi thẳng.

Định nghĩa "ô lọt": `oshares_at` TRẢ SỐ (`value is not None` — tức cổng chứng nhận đã cho qua),
nhưng số đó lệch quá `SANITY_FACTOR` lần so với dòng quý `ticker_financial` gần nhất ≤ ngày đó
(tức cổng biên độ SẼ chặn nếu có). Đó chính xác là tập "chỉ cổng biên độ bắt được".
"""
import collections
import json
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

from corp_action_lib import bq                                             # noqa: E402
from oshares_live import _fetch, oshares_at                                # noqa: E402
import oshares_pit as PIT                                                  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "sanity_direct_call.json"
UNTIL = "2026-06-16"
# 48 mốc quý 2014Q3→2026Q2 — cùng nhịp tái cân bằng mà `custom30_core_select_audit` dùng, để so
# được với con số "~27 ô" của nó, nhưng trên universe RỘNG HƠN.
DATES = [f"{y}-{m}" for y in range(2014, 2027) for m in ("03-31", "06-30", "09-30", "12-31")]
DATES = [d for d in DATES if "2014-03-31" < d <= UNTIL]

univ = sorted({r["ticker"] for r in bq(
    'SELECT DISTINCT ticker FROM `tav2_bq.corporate_action` '
    'WHERE event_status = "executed" AND event_code = "AIS"')})
print(f"universe={len(univ)} mã có ≥1 dòng AIS executed · {len(DATES)} mốc quý → "
      f"{len(univ) * len(DATES):,} ô")

cache = _fetch(univ, UNTIL)
quarters, _corp = cache
q_by_tk = collections.defaultdict(list)
for q in quarters:
    q_by_tk[q["ticker"]].append((q["time"], float(q["OShares"])))
for v in q_by_tk.values():
    v.sort()


def fallback_at(tk, d):
    """Số nền của caller = dòng quý gần nhất ≤ d (ĐÚNG cái `custom30`/`rating_8l` đang dùng)."""
    prev = [v for t, v in q_by_tk.get(tk, []) if t <= d]
    return prev[-1] if prev else None


# CẮT CACHE THEO MÃ trước vòng lặp. `oshares_at` lọc `corp` bằng list-comprehension trên TOÀN
# BỘ danh sách cho MỖI mã, nên gọi nguyên khối là O(ngày × mã × mọi dòng corp) — ~500 triệu phép
# trên lưới này và không bao giờ xong. Cắt sẵn ⇒ mỗi lời gọi chỉ quét dòng của chính mã đó.
# Kết quả KHÔNG đổi: `oshares_at` chỉ đọc dòng có `ticker == tk`.
corp_by_tk = collections.defaultdict(list)
for c in _corp:
    corp_by_tk[c["ticker"]].append(c)
q_rows_by_tk = collections.defaultdict(list)
for q in quarters:
    q_rows_by_tk[q["ticker"]].append(q)

leaks, n_served, n_cells = [], 0, 0
for tk in univ:
    tk_cache = (q_rows_by_tk.get(tk, []), corp_by_tk.get(tk, []))
    for d in DATES:
        r = oshares_at([tk], d, _cache=tk_cache)[tk]
        n_cells += 1
        lv = r.get("value")
        if lv is None:
            continue                                   # cổng chứng nhận/blocker đã chặn rồi
        n_served += 1
        fb = fallback_at(tk, d)
        if fb is None or fb <= 0:
            continue                                   # không có số nền ⇒ cổng biên độ cũng câm
        if not PIT._sane(float(lv), fb):
            leaks.append({"ticker": tk, "date": d, "live": float(lv), "quarterly": fb,
                          "ratio": float(lv) / fb, "method": r.get("method"),
                          "anchor_date": r.get("anchor_date"),
                          "anchor_source": r.get("anchor_source")})

by_tk = collections.Counter(x["ticker"] for x in leaks)
res = {"until": UNTIL, "n_tickers": len(univ), "n_dates": len(DATES), "n_cells": n_cells,
       "n_served_by_oshares_at": n_served, "sanity_factor": PIT.SANITY_FACTOR,
       "n_leaks": len(leaks), "n_leak_tickers": len(by_tk),
       "leak_tickers": dict(by_tk.most_common()), "leaks": leaks}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1, sort_keys=True)

print(f"\nô = {n_cells:,} | `oshares_at` TRẢ SỐ ở {n_served:,} ô")
print(f"LỌT cổng chứng nhận nhưng cổng biên độ ×{PIT.SANITY_FACTOR:g} SẼ chặn: "
      f"{len(leaks)} ô / {len(by_tk)} mã")
for tk, n in by_tk.most_common(15):
    ex = next(x for x in leaks if x["ticker"] == tk)
    print(f"  {tk:5s} {n:3d} ô · vd {ex['date']} live {ex['live']:,.0f} vs quý "
          f"{ex['quarterly']:,.0f} = {ex['ratio']:.1f}× ({ex['method']})")
print(f"-> {OUT}")
