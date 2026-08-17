# -*- coding: utf-8 -*-
"""H2: tham chiếu UPCOM = avgPrice (VWAP sở công bố) phiên trước, làm tròn về bước giá?

CHỈ ĐỌC (endpoint giá DNSE). Đối chứng nội bộ HOSE/HNX trong cùng lần đo, cùng feed.
"""
import csv, os, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from trading_bot.brokers import get_dnse_client
from trading_bot.vn_market import tick_size

SRC = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/upcom_ref_basis_probe_20260818.csv"
OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/upcom_vwap_source_probe_20260818.csv"
c = get_dnse_client()

rows = list(csv.DictReader(open(SRC)))
out = []
for i, r in enumerate(rows):
    tk, ex = r["ticker"], r["exchange"]
    ref = float(r["ref_live"]); close = float(r["prev_close"]); tick = float(r["tick"])
    try:
        tr = (c.latest_trade(tk) or {}).get("trades") or []
    except Exception as e:
        out.append({"ticker": tk, "exchange": ex, "err": f"{type(e).__name__}"}); continue
    g1 = [t for t in tr if t.get("boardId") == "G1"]
    if not g1:
        out.append({"ticker": tk, "exchange": ex, "err": "no_G1"}); continue
    t = g1[0]
    avg = t.get("avgPrice")
    if not avg:
        out.append({"ticker": tk, "exchange": ex, "err": "no_avgPrice"}); continue
    avg_vnd = float(avg) * 1000.0
    r_avg = round(avg_vnd / tick) * tick          # nearest-tick
    out.append({"ticker": tk, "exchange": ex, "ref_live": ref, "prev_close": close,
                "avg_price_vnd": avg_vnd, "avg_rounded": r_avg,
                "dev_close_vnd": ref - close, "dev_avg_vnd": ref - r_avg,
                "dev_avg_ticks": (ref - r_avg) / tick, "tick": tick,
                "vol_g1": t.get("totalVolumeTraded"), "err": ""})
    if i % 100 == 0:
        print(f"  ... {i}/{len(rows)}", flush=True)

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader(); w.writerows(out)

for ex in ("HOSE", "HNX", "UPCOM"):
    s = [o for o in out if o["exchange"] == ex and not o.get("err")]
    if not s: continue
    mc = sum(1 for o in s if abs(o["dev_close_vnd"]) < 1)
    ma = sum(1 for o in s if abs(o["dev_avg_vnd"]) < 1)
    m1 = sum(1 for o in s if abs(o["dev_avg_ticks"]) <= 1.0001)
    print(f"{ex:6s} n={len(s):4d} | ref==close: {mc:4d} ({mc/len(s):6.1%}) | "
          f"ref==round(avgPrice): {ma:4d} ({ma/len(s):6.1%}) | within 1 tick of avg: "
          f"{m1:4d} ({m1/len(s):6.1%})")
errs = {}
for o in out:
    if o.get("err"): errs[o["err"]] = errs.get(o["err"], 0) + 1
print("errors:", errs, "| CSV:", OUT)
