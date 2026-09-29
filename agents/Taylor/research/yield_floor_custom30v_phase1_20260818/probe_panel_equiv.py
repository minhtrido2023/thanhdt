# -*- coding: utf-8 -*-
"""Equivalence test: batched yield-floor panel (probe_yield_bonus.py) vs the real
trading_bot.due_diligence._yield_floor(), cell by cell, on a random sample of (ticker, rebal_date).
This is the weakest link of the Phase-1 measurement -- test it, don't assert it."""
import os, sys, bisect
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
from deposit_rate_vn import current_deposit_rate
import corp_action_lib
from trading_bot.due_diligence import (_yield_floor, YIELD_FLOOR_NEAR_LO, YIELD_FLOOR_NEAR_HI,
                                       YIELD_FLOOR_ICB_BANKING)

# recent dates only: corporate_action feed + _read_year cache are reliable there, and the live
# decision (2026-11-05) lives in this regime.
DATES = [pd.Timestamp(x) for x in ("2025-08-05", "2025-11-05", "2026-02-05", "2026-05-05", "2026-08-05")]
END = "2026-08-18"; EFF_START = "2024-01-01"
TICKS = ["FPT","VNM","REE","PNJ","HPG","VCB","ACB","DGC","BMP","GAS","POW","SAB",
         "MWG","VHM","NTP","TNG","IDC","HAH","DHC","VSC","BWE","QNS","PVS","CTG"]
inlist = ",".join(f"'{t}'" for t in TICKS)

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
px["time"] = pd.to_datetime(px["time"]); px = px.sort_values(["ticker","time"])
px_map = {}
for tk, g in px.groupby("ticker"):
    ts, pr, ic = list(g["time"]), list(g["price"]), list(g["icb"])
    for d in DATES:
        i = bisect.bisect_right(ts, d) - 1
        if i >= 0 and (d - ts[i]).days <= 20:
            px_map[(tk, d)] = (float(pr[i]), (None if pd.isna(ic[i]) else int(ic[i])))

def panel_label(tk, d):
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
    if not stable: return ("NO_DATA", False)
    prox = price / (div0 / (dep/100.0))
    return (("BELOW_FLOOR" if prox < YIELD_FLOOR_NEAR_LO else
             "ABOVE_FLOOR" if prox > YIELD_FLOOR_NEAR_HI else "NEAR_FLOOR"), True)

n_ok = n_bad = 0; bad = []
print(f"{'ticker':<7}{'date':<12}{'panel':<18}{'_yield_floor':<18}{'prox_panel':>11}{'prox_dd':>10}  match")
for d in DATES:
    for tk in TICKS:
        pl, _ = panel_label(tk, d)
        dd = _yield_floor(tk, str(d.date()))
        real = dd["yield_floor_note"]
        # panel prox for display
        p = px_map.get((tk, d)); prox_p = None
        if p and real not in ("BANKING_EXCLUDED",):
            g = div_by_tk.get(tk)
            if g is not None:
                lo, hi = d - pd.Timedelta(days=365), d
                d0 = float(g.loc[(g["ex"] > lo) & (g["ex"] <= hi), "value_per_share"].sum())
                dep = current_deposit_rate(str(d.date()))
                if d0 > 0: prox_p = p[0] / (d0/(dep/100.0))
        prox_r = dd.get("prox_to_floor")
        ok = (pl == real)
        n_ok += ok; n_bad += (not ok)
        if not ok: bad.append((tk, str(d.date()), pl, real, prox_p, dd.get("prox_to_floor")))
        print(f"{tk:<7}{str(d.date()):<12}{pl:<18}{real:<18}"
              f"{(f'{prox_p:.4f}' if prox_p else '-'):>11}"
              f"{(f'{prox_r:.4f}' if prox_r else '-'):>10}"
              f"  {'OK' if ok else 'MISMATCH'}")
print(f"\nMATCH {n_ok}/{n_ok+n_bad} ({n_ok/max(n_ok+n_bad,1):.1%})")
if bad:
    print("\nMISMATCHES:")
    for b in bad: print("  ", b)
