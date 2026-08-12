"""Bỏ/nới trần 30%-KL-luỹ-kế thì mình chiếm bao nhiêu % tape thật của phiên?

Trần đó tồn tại để "fleet không bao giờ thành đa số một phiên mỏng" (comment
executor.py:585). Nới nó phải trả lời được câu này bằng SỐ, không bằng lý lẽ.
R&D only (§8).
"""
import os, glob, numpy as np, pandas as pd
import exp_ceiling_tolerance as T

kappa = float(os.environ.get("KAPPA", "0.34"))
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
        d = idx[pos]; adv20 = float(dd.iloc[pos]["adv20"]); dayvol = float(dd.iloc[pos]["vol"])
        b = df[df.date == d]
        if b.empty or adv20 <= 0 or dayvol <= 0: continue
        anchor = float(dd.iloc[pos-5]["close"]); ceil = anchor*1.03
        target = int((tgt*adv20/anchor)//T.LOT*T.LOT)
        if target < T.LOT: continue
        for pac, label in (("current","30%_hien_tai"), ("adv_only","bo_tran")):
            f, c = T.run_session(b, target, ceil, adv20, kappa, pac)
            rows.append({"ticker":tk,"date":d,"pacing":label,"filled":f,
                         "day_vol":dayvol,"share":f/dayvol})
d = pd.DataFrame(rows)
print(f"=== % TAPE THẬT CỦA PHIÊN MÀ MÌNH CHIẾM (κ={kappa}, lệnh {tgt*100:.0f}%ADV, τ=3%) ===")
print(f"{'pacing':>14}{'TB':>8}{'p50':>8}{'p90':>8}{'p95':>8}{'p99':>8}{'max':>8}{'%phiên >30%':>13}{'>50%':>8}")
for lab, g in d.groupby("pacing"):
    s = g.share
    print(f"{lab:>14}{100*s.mean():7.1f}%{100*s.median():7.1f}%{100*s.quantile(.9):7.1f}%"
          f"{100*s.quantile(.95):7.1f}%{100*s.quantile(.99):7.1f}%{100*s.max():7.1f}%"
          f"{100*(s>0.30).mean():12.1f}%{100*(s>0.50).mean():7.1f}%")
