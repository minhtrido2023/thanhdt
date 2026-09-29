# -*- coding: utf-8 -*-
"""Doi soat tape FiinX vs tape vnstock (local) tren doan trung 2023-09-11..2023-12-29.
So sanh o muc DAI LUONG MA CHIEN LUOC DUNG (c_first, entry, exitpx, min_low_post, max_high_post),
khong so so bar vi 2 vendor khac quy uoc bar rong (FiinX fill bar volume=0, vnstock bo)."""
import pandas as pd, numpy as np

WC = "/home/trido/thanhdt/WorkingClaude"
loc = pd.read_csv(WC + "/data/vn30f1m_1min.csv")
loc["time"] = pd.to_datetime(loc["time"]); loc["date"] = loc["time"].dt.date
loc["hm"] = loc["time"].dt.strftime("%H:%M")

rows = []
for d, g in loc.groupby("date"):
    g = g.sort_values("time")
    op = g[g["hm"] <= "09:30"]; post = g[g["hm"] > "09:30"]
    seg = post[post["hm"] <= "14:30"]
    if len(op) == 0 or len(seg) == 0: continue
    rows.append(dict(date=str(d), nbars=len(g), nop=len(op), nseg=len(seg),
                     hm0=g["hm"].iloc[0], hmL=g["hm"].iloc[-1],
                     c_first=g["close"].iloc[0], entry=op["close"].iloc[-1],
                     exitpx=seg["close"].iloc[-1],
                     min_low_post=post["low"].min(), max_high_post=post["high"].max()))
L = pd.DataFrame(rows)

F = pd.read_csv("fiinx_daily_2023Q4.csv")
for tag in ["ALL", "V0"]:
    f = F[F["tag"] == tag].copy()
    m = f.merge(L, on="date", suffixes=("_f", "_l"))
    print("=== FiinX tag=%s vs vnstock local | ngay khop: %d/%d ===" % (tag, len(m), len(f)))
    for col in ["c_first", "entry", "exitpx", "min_low_post", "max_high_post"]:
        dv = (m[col + "_f"] - m[col + "_l"]).abs()
        print("  %-14s eq=%3d/%d  maxdiff=%.4f  n_diff>0.05=%d" %
              (col, int((dv <= 1e-9).sum()), len(m), dv.max(), int((dv > 0.05).sum())))
    bad = m[(m["c_first_f"] - m["c_first_l"]).abs() > 1e-9]
    if len(bad):
        print("  NGAY LECH c_first:")
        print(bad[["date", "hm0_f", "hm0_l", "c_first_f", "c_first_l", "nbars_f", "nbars_l"]].to_string(index=False))
    bad2 = m[(m["exitpx_f"] - m["exitpx_l"]).abs() > 1e-9]
    if len(bad2):
        print("  NGAY LECH exitpx: %d" % len(bad2))
        print(bad2[["date", "exitpx_f", "exitpx_l", "nseg_f", "nseg_l"]].head(10).to_string(index=False))
    print()
