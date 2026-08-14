"""Cận TRÊN κ-free của % tape mình có thể chiếm nếu BỎ trần 30%-KL-luỹ-kế.

Khác exp_participation_check.py: ở đó con số bị chính giả định κ chặn (max = κ),
nên KHÔNG đọc được rủi ro đuôi. Ở đây tính cận trên cơ học:
    share_max = min(10%×ADV20/giá , KL cần) / KL thật của phiên
Không phụ thuộc κ. Đây là điều TỆ NHẤT có thể xảy ra khi ta là người mua duy nhất.
R&D only (§8).
"""
import os, glob, numpy as np, pandas as pd
import exp_ceiling_tolerance as T

tgt = float(os.environ.get("TARGET_PCT_ADV", "0.10"))
rows = []
for p in sorted(glob.glob(os.path.join(T.BARS, "*.csv"))):
    tk = os.path.basename(p)[:-4]
    df = T.load(p)
    dd = df.groupby("date").agg(vol=("volume","sum"), close=("close","last"))
    dd["turn"] = dd.vol*dd.close
    dd["adv20"] = dd.turn.rolling(20, min_periods=10).mean().shift(1)
    dd = dd.dropna(); idx = list(dd.index)
    for pos in range(max(20, len(idx)-80), len(idx)):
        adv20 = float(dd.iloc[pos]["adv20"]); dayvol = float(dd.iloc[pos]["vol"])
        px = float(dd.iloc[pos-5]["close"])
        if adv20 <= 0 or dayvol <= 0 or px <= 0: continue
        target = tgt*adv20/px
        cap_adv = 0.10*adv20/px
        rows.append({"ticker":tk, "share_max": min(cap_adv, target)/dayvol,
                     "thin": dayvol*px/adv20})
d = pd.DataFrame(rows)
s = d.share_max.clip(0,1)
print(f"=== CẬN TRÊN κ-free: %tape phiên nếu ta là NGƯỜI MUA DUY NHẤT (lệnh {tgt*100:.0f}%ADV) ===")
print(f"  TB {100*s.mean():.1f}% · p50 {100*s.median():.1f}% · p90 {100*s.quantile(.9):.1f}%"
      f" · p99 {100*s.quantile(.99):.1f}% · max {100*s.max():.1f}%")
for th in (0.30, 0.50, 0.80):
    print(f"  %phiên cận trên vượt {th*100:.0f}% tape: {100*(s>th).mean():.1f}%")
print(f"  (phiên MỎNG BẤT THƯỜNG, KL<30% ADV20: {100*(d.thin<0.30).mean():.1f}% số phiên — "
      f"đó là nhóm trần 30% đang bảo vệ)")
