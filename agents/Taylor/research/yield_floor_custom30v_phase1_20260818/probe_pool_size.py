# -*- coding: utf-8 -*-
"""Read-only probe: how many names pass the custom30V gate (rating<=3) at each q2m5 rebal?
Answers: is `gated` >= CFO_POOL(60)? is pool > top_n(30)?  No writes, no BQ load."""
import os, sys, bisect
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

END = "2026-08-18"; EFF_START = "2024-01-01"
qliq = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q,
  AVG(t.Volume_3M_P50*{cb.pxw_sql()}) AS liq, COUNT(*) AS nd
FROM tav2_bq.ticker t
WHERE {cb.universe_pred()} AND {cb.UNIVERSE_FILTER}
  AND t.time >= DATE_SUB(DATE '{EFF_START}', INTERVAL 380 DAY) AND t.time <= DATE '{END}'
GROUP BY t.ticker, q HAVING nd >= 20""")
qliq["q"] = pd.to_datetime(qliq["q"])
rat = bq(f"""SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l r
WHERE r.time <= DATE '{END}' ORDER BY r.ticker, r.time""")
rat["time"] = pd.to_datetime(rat["time"])
rat_by_tk = {tk: (list(g["time"]), list(g["rating"])) for tk, g in rat.groupby("ticker")}
def rating_asof(tk, d):
    e = rat_by_tk.get(tk)
    if not e: return np.nan
    i = bisect.bisect_right(e[0], d) - 1
    return float(e[1][i]) if i >= 0 else np.nan

cal = bq(f"""SELECT DISTINCT t.time FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX'
  AND t.time BETWEEN DATE '{EFF_START}' AND DATE '{END}' ORDER BY t.time""")
days_arr = np.array(pd.to_datetime(cal["time"]), dtype="datetime64[ns]")
sd, ed = pd.Timestamp(EFF_START), pd.Timestamp(END)
rebal_dates = []
for Y in range(sd.year, ed.year + 1):
    for mo in (2, 5, 8, 11):
        i = int(np.searchsorted(days_arr, np.datetime64(pd.Timestamp(Y, mo, 5)), side="left"))
        if i < len(days_arr):
            a = pd.Timestamp(days_arr[i])
            if sd <= a <= ed: rebal_dates.append(a)
rebal_dates = sorted(set(rebal_dates))
liq_piv = qliq.pivot_table(index="q", columns="ticker", values="liq")
print(f"CFO_POOL default = {os.environ.get('BASKET_CFO_POOL','60')}, top_n = {cb.N_MEMBERS}\n")
print(f"{'rebal':<12} {'src_q':<12} {'n_liq':>6} {'n_gated(r<=3)':>14} {'pool=min(g,60)':>15} {'pool>30?':>9}")
for d in rebal_dates:
    qd = pd.Timestamp(d).to_period("Q").start_time
    prior = [q for q in liq_piv.index if q < qd]
    if not prior: continue
    src_q = max(prior)
    liq_row = liq_piv.loc[src_q].dropna().sort_values(ascending=False)
    gated = [tk for tk in liq_row.index
             if (lambda rt: pd.notna(rt) and rt <= 3)(rating_asof(tk, d))]
    pool = min(len(gated), 60)
    print(f"{str(d.date()):<12} {str(src_q.date()):<12} {len(liq_row):>6} {len(gated):>14} {pool:>15} {'YES' if pool>30 else 'NO':>9}")
