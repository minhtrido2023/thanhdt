# -*- coding: utf-8 -*-
"""Read-only probe: how often does the custom30V yieldcombo score TIE, especially at the 30/31 cut?
A true tiebreaker can only fire on an exact tie that spans the cut boundary."""
import os, sys, bisect
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

END = "2026-08-18"; EFF_START = "2018-01-01"
CFO_POOL, TOP_N = 60, 30
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
def ypiv(col):
    _y = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG(SAFE_DIVIDE(1, t.{col})) AS y
FROM tav2_bq.ticker t WHERE t.{col} > 0 AND t.time BETWEEN DATE '{EFF_START}' AND DATE '{END}'
GROUP BY t.ticker, q""")
    _y["q"] = pd.to_datetime(_y["q"])
    return _y.pivot_table(index="q", columns="ticker", values="y")
pe_piv, pcf_piv = ypiv("PE"), ypiv("PCF")

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

n_dates = 0; n_with_boundary_tie = 0; tot_tie_groups = 0; tot_tied_names = 0
rows = []
for d in rebal_dates:
    qd = pd.Timestamp(d).to_period("Q").start_time
    prior = [q for q in liq_piv.index if q < qd]
    if not prior: continue
    src_q = max(prior)
    liq_row = liq_piv.loc[src_q].dropna().sort_values(ascending=False)
    gated = [tk for tk in liq_row.index if (lambda rt: pd.notna(rt) and rt <= 3)(rating_asof(tk, d))]
    pool = gated[:CFO_POOL]
    if not pool: continue
    pe_s  = pe_piv.loc[src_q]  if src_q in pe_piv.index  else None
    pcf_s = pcf_piv.loc[src_q] if src_q in pcf_piv.index else None
    pe_r  = pd.Series({t: (pe_s.get(t, np.nan)  if pe_s  is not None else np.nan) for t in pool}).rank(pct=True).fillna(0.5)
    pcf_r = pd.Series({t: (pcf_s.get(t, np.nan) if pcf_s is not None else np.nan) for t in pool}).rank(pct=True).fillna(0.5)
    score = {t: float(pe_r[t] + pcf_r[t]) for t in pool}
    order = sorted(pool, key=lambda t: score[t], reverse=True)
    # tie groups anywhere in pool
    vc = pd.Series(list(score.values())).round(12).value_counts()
    tie_groups = int((vc > 1).sum()); tied_names = int(vc[vc > 1].sum())
    # boundary tie: score of the 30th == score of the 31st (i.e. tie SPANS the cut)
    boundary_tie = False; n_boundary = 0
    if len(order) > TOP_N:
        s30, s31 = round(score[order[TOP_N-1]], 12), round(score[order[TOP_N]], 12)
        boundary_tie = (s30 == s31)
        if boundary_tie:
            n_boundary = sum(1 for t in pool if round(score[t], 12) == s30)
    n_dates += 1; n_with_boundary_tie += int(boundary_tie)
    tot_tie_groups += tie_groups; tot_tied_names += tied_names
    rows.append((str(d.date()), len(pool), tie_groups, tied_names, "YES" if boundary_tie else "-", n_boundary))
print(f"{'rebal':<12}{'pool':>5}{'tie_grp':>9}{'tied_n':>8}{'BOUNDARY_TIE':>14}{'n_at_bnd':>9}")
for r in rows: print(f"{r[0]:<12}{r[1]:>5}{r[2]:>9}{r[3]:>8}{r[4]:>14}{r[5]:>9}")
print(f"\nDates: {n_dates}. Boundary tie (30th==31st score): {n_with_boundary_tie} ({n_with_boundary_tie/max(n_dates,1):.1%})")
print(f"Tie groups/date avg {tot_tie_groups/max(n_dates,1):.2f}; tied names/date avg {tot_tied_names/max(n_dates,1):.2f}")
