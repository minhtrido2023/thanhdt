"""Đo tác động của ABSORPTION TEST (job Taylor_20260820_043511) trên rổ ticker_prune.

Chỉ nhánh LIVE mới bị chạm, nên phép đo chạy `oshares_at(..., live=True)` cho toàn rổ tại một
`asof` và đếm theo `absorption_test.verdict`:
  ABSORBED         — dòng quý ĐÃ gồm sự kiện ⇒ số KHÔNG đổi (hành vi cũ vốn đúng ở ca này)
  ROLLED           — dòng quý CHƯA gồm ⇒ số ĐỔI (đây là phần undercount được vá)
  WINDOW_AMBIGUOUS — không quyết được ⇒ số KHÔNG đổi, chỉ gắn nhãn
Không có field  — cửa sổ rỗng hoặc neo không phải dòng quý-chưa-verified ⇒ không liên quan.

Chạy: python3 absorption_impact_probe.py [--asof YYYY-MM-DD] [--out ket_qua.json]
"""
import argparse, json, os, sys

sys.path.insert(0, os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"))
from corp_action_lib import bq                       # noqa: E402
from oshares_live import _fetch, oshares_at          # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--asof", default="2026-08-19")
ap.add_argument("--out", default="absorption_impact.json")
a = ap.parse_args()

uni = [r["ticker"] for r in bq(f"""
    SELECT DISTINCT ticker FROM `lithe-record-440915-m9.tav2_bq.ticker_prune`
    WHERE time = (SELECT MAX(time) FROM `lithe-record-440915-m9.tav2_bq.ticker_prune`
                  WHERE time <= DATE "{a.asof}")
    ORDER BY ticker""")]
print(f"rổ = {len(uni)} mã ticker_prune tại {a.asof}", flush=True)

buckets, rows = {}, []
for i in range(0, len(uni), 25):
    chunk = uni[i:i + 25]
    cache = _fetch(chunk, a.asof)
    res = oshares_at(chunk, a.asof, _cache=cache, live=True)
    for tk, r in res.items():
        ab = r.get("absorption_test")
        v = ab["verdict"] if ab else "N/A"
        buckets[v] = buckets.get(v, 0) + 1
        if ab:
            rows.append({"ticker": tk, "verdict": v, "value": r["value"],
                         "method": r["method"], "anchor_date": r["anchor_date"],
                         "window": [ab["window_from"], ab["window_to"]],
                         "n_events": len(ab["events"]), "rolled": len(ab["rolled"]),
                         "note": ab["note"]})
    print(f"  {i+len(chunk)}/{len(uni)} … {buckets}", flush=True)

out = {"asof": a.asof, "universe": len(uni), "buckets": buckets, "detail": rows}
json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
print(json.dumps(buckets, ensure_ascii=False))
print(f"→ {a.out}")
