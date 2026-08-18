# -*- coding: utf-8 -*-
"""Read-only measurement: what WOULD a yield-floor overlay do to custom30V membership?
Three variants, all measured against the real pinned selector (score = rank(1/PE)+rank(1/PCF)):
  V0 = production (control)
  V1 = TRUE tiebreaker    -> sort key (-score, yield_priority, ticker): fires only on exact ties
  V2 = SOFT score bonus   -> score += W * yield_bonus  (the DCF_MODE='tiebreak' pattern in-file)
  V3 = LITERAL dispatch spec -> sort key (yield_priority, ticker) ONLY  [shown to size the damage]
Yield-floor labels replicate trading_bot/due_diligence._yield_floor EXACTLY (365d windows, dedup
by (ticker,exright_date,dividend_year,dividend_stage_vi) latest public_date, prox = px/floor_px,
raw COALESCE(Price,Close), banking ICB 8355 excluded). No writes.
"""
import os, sys, bisect
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb
from deposit_rate_vn import current_deposit_rate
import corp_action_lib
from trading_bot.due_diligence import (YIELD_FLOOR_NEAR_LO, YIELD_FLOOR_NEAR_HI,
                                       YIELD_FLOOR_ICB_BANKING)

END = "2026-08-18"; EFF_START = "2018-01-01"; CFO_POOL, TOP_N = 60, 30
W_GRID = [0.05, 0.10, 0.20, 0.50]

qliq = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q,
  AVG(t.Volume_3M_P50*{cb.pxw_sql()}) AS liq, COUNT(*) AS nd
FROM tav2_bq.ticker t WHERE {cb.universe_pred()} AND {cb.UNIVERSE_FILTER}
  AND t.time >= DATE_SUB(DATE '{EFF_START}', INTERVAL 380 DAY) AND t.time <= DATE '{END}'
GROUP BY t.ticker, q HAVING nd >= 20""")
qliq["q"] = pd.to_datetime(qliq["q"])
rat = bq(f"SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l r WHERE r.time <= DATE '{END}' ORDER BY r.ticker, r.time")
rat["time"] = pd.to_datetime(rat["time"])
rat_by_tk = {tk: (list(g["time"]), list(g["rating"])) for tk, g in rat.groupby("ticker")}
def rating_asof(tk, d):
    e = rat_by_tk.get(tk)
    if not e: return np.nan
    i = bisect.bisect_right(e[0], d) - 1
    return float(e[1][i]) if i >= 0 else np.nan
def ypiv(col):
    _y = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG(SAFE_DIVIDE(1, t.{col})) AS y
FROM tav2_bq.ticker t WHERE t.{col} > 0 AND t.time BETWEEN DATE '{EFF_START}' AND DATE '{END}' GROUP BY t.ticker, q""")
    _y["q"] = pd.to_datetime(_y["q"]); return _y.pivot_table(index="q", columns="ticker", values="y")
pe_piv, pcf_piv = ypiv("PE"), ypiv("PCF")
cal = bq(f"SELECT DISTINCT t.time FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{EFF_START}' AND DATE '{END}' ORDER BY t.time")
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

# ---- pass 1: pools + yieldcombo scores (the production control) ----
pools = {}
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
    pe_r  = pd.Series({t:(pe_s.get(t,np.nan)  if pe_s  is not None else np.nan) for t in pool}).rank(pct=True).fillna(0.5)
    pcf_r = pd.Series({t:(pcf_s.get(t,np.nan) if pcf_s is not None else np.nan) for t in pool}).rank(pct=True).fillna(0.5)
    pools[d] = (pool, {t: float(pe_r[t] + pcf_r[t]) for t in pool})
uni = sorted({t for p, _ in pools.values() for t in p})
print(f"pools: {len(pools)} rebal dates, {len(uni)} distinct pool names")

# ---- yield-floor panel (batched; same definition as _yield_floor) ----
inlist = ",".join(f"'{t}'" for t in uni)
div = pd.DataFrame(corp_action_lib.bq(f"""WITH dd AS (
  SELECT c.ticker, c.exright_date AS ex, c.value_per_share,
    ROW_NUMBER() OVER (PARTITION BY c.ticker,c.exright_date,c.dividend_year,c.dividend_stage_vi
                       ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` c
  WHERE c.event_code="DIV" AND c.event_status="executed" AND c.ticker IN ({inlist})
    AND c.exright_date IS NOT NULL AND c.value_per_share > 0
    AND c.exright_date BETWEEN DATE_SUB(DATE '{EFF_START}', INTERVAL 1095 DAY) AND DATE '{END}')
SELECT ticker, ex, value_per_share FROM dd WHERE rn=1"""))
div["ex"] = pd.to_datetime(div["ex"])
div["value_per_share"] = pd.to_numeric(div["value_per_share"], errors="coerce")
div = div[div["value_per_share"] > 0]
div_by_tk = {tk: g.sort_values("ex") for tk, g in div.groupby("ticker")}
px = bq(f"""SELECT t.ticker, t.time, COALESCE(t.Price,t.Close) AS price, t.ICB_Code AS icb
FROM tav2_bq.ticker t WHERE t.ticker IN ({inlist})
  AND t.time BETWEEN DATE '{EFF_START}' AND DATE '{END}' AND COALESCE(t.Price,t.Close) > 0""")
px["time"] = pd.to_datetime(px["time"])
px = px.sort_values(["ticker", "time"])
px_map = {}
for tk, g in px.groupby("ticker"):
    ts = list(g["time"]); pr = list(g["price"]); ic = list(g["icb"])
    for d in pools:
        i = bisect.bisect_right(ts, d) - 1
        if i >= 0 and (d - ts[i]).days <= 20:
            px_map[(tk, d)] = (float(pr[i]), (None if pd.isna(ic[i]) else int(ic[i])))

def yfloor(tk, d):
    """-> (note, is_stable). Mirrors _yield_floor's label logic."""
    p = px_map.get((tk, d))
    if p is None: return ("NO_DATA", None)
    price, icb = p
    if icb is not None and icb == YIELD_FLOOR_ICB_BANKING: return ("BANKING_EXCLUDED", None)
    g = div_by_tk.get(tk)
    if g is None: return ("NO_DATA", False)
    w = [(d - pd.Timedelta(days=365*(k+1)), d - pd.Timedelta(days=365*k)) for k in range(3)]
    n = [int(((g["ex"] > lo) & (g["ex"] <= hi)).sum()) for lo, hi in w]
    div0 = float(g.loc[(g["ex"] > w[0][0]) & (g["ex"] <= w[0][1]), "value_per_share"].sum())
    stable = (n[0] >= 1 and n[1] >= 1 and n[2] >= 1)
    dep = current_deposit_rate(str(d.date()))
    if div0 <= 0 or dep <= 0: return ("NO_DATA", stable)
    prox = price / (div0 / (dep/100.0))
    if not stable: return ("NO_DATA", False)
    return (("BELOW_FLOOR" if prox < YIELD_FLOOR_NEAR_LO else
             "ABOVE_FLOOR" if prox > YIELD_FLOOR_NEAR_HI else "NEAR_FLOOR"), True)

# dispatch priority: 1=BELOW 2=NEAR 3=stable-but-ABOVE 4=ABOVE 5->4 neutral(NO_DATA/BANKING)
PRIO = {"BELOW_FLOOR": 1, "NEAR_FLOOR": 2, "ABOVE_FLOOR": 4, "NO_DATA": 4, "BANKING_EXCLUDED": 4}
def prio(note, stable): return 3 if (note == "ABOVE_FLOOR" and stable) else PRIO.get(note, 4)
# soft bonus: higher = better, mapped from priority (1->1.0 ... 4->0.0)
BONUS = {1: 1.0, 2: 0.6, 3: 0.2, 4: 0.0}

lab = {}
for d, (pool, _) in pools.items():
    for t in pool:
        note, st = yfloor(t, d); lab[(t, d)] = (note, st, prio(note, st))
cnt = pd.Series([v[0] for v in lab.values()]).value_counts()
print("\nyield_floor label distribution over all pool-name-dates:"); print(cnt.to_string())

rows = []
for d, (pool, score) in sorted(pools.items()):
    v0 = set(sorted(pool, key=lambda t: (-score[t], t))[:TOP_N])
    v1 = set(sorted(pool, key=lambda t: (-score[t], lab[(t,d)][2], t))[:TOP_N])
    v3 = set(sorted(pool, key=lambda t: (lab[(t,d)][2], t))[:TOP_N])
    r = {"rebal": str(d.date()), "V1_chg": len(v0 - v1)}
    for W in W_GRID:
        vs = set(sorted(pool, key=lambda t: (-(score[t] + W*BONUS[lab[(t,d)][2]]), t))[:TOP_N])
        r[f"V2_W{W}"] = len(v0 - vs)
    r["V3_chg"] = len(v0 - v3)
    r["n_below_pool"] = sum(1 for t in pool if lab[(t,d)][0] == "BELOW_FLOOR")
    r["n_below_v0"] = sum(1 for t in v0 if lab[(t,d)][0] == "BELOW_FLOOR")
    rows.append(r)
R = pd.DataFrame(rows)
print("\nnames REPLACED vs production top-30 (out of 30):")
print(R.to_string(index=False))
print("\nMEAN names changed per rebal:")
for c in ["V1_chg"] + [f"V2_W{W}" for W in W_GRID] + ["V3_chg"]:
    print(f"  {c:<10} {R[c].mean():.2f}   (max {R[c].max()}, dates with any change: {(R[c]>0).sum()}/{len(R)})")
print(f"\nBELOW_FLOOR names: mean {R['n_below_pool'].mean():.2f}/60 in pool, "
      f"{R['n_below_v0'].mean():.2f}/30 already in production basket")
