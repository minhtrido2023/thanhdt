#!/usr/bin/env python3
"""Pha SAU KHOA rev4: chiet khau thanh khoan sigma*sqrt(Q/ADV60) tu calc_rev3/px_vcp_post_lock.csv."""
import csv, json, math, os, statistics
H = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(H, "..", "calc_rev3", "px_vcp_post_lock.csv"))))
cl = [float(r["Close"]) for r in rows]; tv = [float(r["Price"]) * float(r["Volume"]) / 1e9 for r in rows]
ret = [math.log(cl[i] / cl[i - 1]) for i in range(len(cl) - 250, len(cl))]
sig = statistics.pstdev(ret); adv60 = statistics.median(tv[-60:]); adv250 = statistics.median(tv[-250:]); adv20 = statistics.median(tv[-20:])
M = json.load(open(os.path.join(H, "model_out_rev4.json")))
out = {"last_date": rows[-1]["time"], "last_close": cl[-1], "sigma250": round(sig, 4), "adv60_bn": round(adv60, 3), "adv250_bn": round(adv250, 3), "adv20_bn": round(adv20, 2), "pos": {}}
for q in (1.0, 0.3, 0.1):
    d = sig * math.sqrt(q / adv60)
    out["pos"][str(q)] = {"disc": round(d, 4), "center_after": round(M["center_ps"] * (1 - d)), "bear_after": round(M["value_ps"]["bear"] * (1 - d)),
                          "bull_after": round(M["value_ps"]["bull"] * (1 - d)), "days_10pct": round(q / (0.1 * adv60), 1), "days_20pct": round(q / (0.2 * adv60), 1)}
print(json.dumps(out, indent=1))
