#!/usr/bin/env python3
"""
compare_ba_v11b_v11c.py
========================
Iterate on BA v11 with v8c FA:

  v11a: v8c FA, NO Fin/RE modifier (already tested, lost on Sharpe/DD)
  v11b: v8c FA, KEEP Fin/RE +10/-10 modifier
  v11c: v8c FA, KEEP modifier but adjust thresholds (TA cutoffs)

Compare to v10 baseline.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE
from test_round14_stability import SIGNAL_V10

# v11b: just swap FA table source, KEEP Fin/RE modifier
SIGNAL_V11b = SIGNAL_V10.replace(
    "FROM tav2_bq.fa_ratings AS f",
    "FROM tav2_bq.fa_ratings_v8c AS f"
)
assert "fa_ratings_v8c" in SIGNAL_V11b
assert 'fa_tier="D" THEN 10' in SIGNAL_V11b  # modifier kept

# v11c: v11b but loosen TA thresholds for new FA distribution
SIGNAL_V11c = SIGNAL_V11b.replace(
    "WHEN ta >= 170 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MEGA'",
    "WHEN ta >= 165 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MEGA'"
).replace(
    "WHEN ta >= 170 AND state5 IN (4,5) THEN 'S_PRO'",
    "WHEN ta >= 165 AND state5 IN (4,5) THEN 'S_PRO'"
).replace(
    "WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MOMENTUM'",
    "WHEN ta >= 150 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MOMENTUM'"
).replace(
    "WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'",
    "WHEN ta >= 150 AND state5 IN (4,5) AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'"
).replace(
    "WHEN ta >= 155 AND state5 = 3 AND fa_tier IN ('C','D') THEN 'MOMENTUM_N'",
    "WHEN ta >= 150 AND state5 = 3 AND fa_tier IN ('C','D') THEN 'MOMENTUM_N'"
)

TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
OOS_START = pd.Timestamp("2024-01-01")


def run_canonical(label, query_text):
    print(f"\n{'='*70}\n  RUN: {label}\n{'='*70}")
    sig = bq(query_text.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows")

    play_dist = sig.groupby("play_type").size().sort_values(ascending=False).head(12)
    print(f"  play_type (top 12): {dict(play_dist)}")

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
    vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())
    sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                    FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                """).set_index("ticker")["s"].to_dict()
    top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
                    WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
                    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                    GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    nav_bal, trades_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    sig_vn30 = sig[sig["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k:v for k,v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, vni, len(trades_bal), len(trades_vn30)


def window_metrics(nav, start, end):
    sub = nav[(nav.index >= start) & (nav.index <= end)]
    if len(sub) < 30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((sub - sub.cummax()) / sub.cummax()).min()
    return {"cagr": cagr*100, "sharpe": sharpe, "mdd": dd*100,
            "calmar": cagr/abs(dd) if dd<0 else 0, "wealth": sub.iloc[-1]/sub.iloc[0]}


print(f"Window: {START_DATE} → {END_DATE}")
ba_v10, vni, t10b, t10v = run_canonical("v10 + v4 (baseline)", SIGNAL_V10)
ba_v11b, _,  t11b_b, t11b_v = run_canonical("v11b: v8c FA + KEEP Fin/RE modifier", SIGNAL_V11b)
ba_v11c, _,  t11c_b, t11c_v = run_canonical("v11c: v11b + lower TA thresholds (170→165, 155→150)", SIGNAL_V11c)

periods = [
    ("FULL 2014-2026",  ba_v10.index.min(), ba_v10.index.max()),
    ("OOS 2024-2026",   OOS_START,           ba_v10.index.max()),
    ("Mid 2018-2023",   pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Pre-OOS 2014-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
]

print("\n" + "═"*100)
print("  BA v11b / v11c comparison")
print("═"*100)
print(f"  Trades: v10 BAL={t10b}, v11b BAL={t11b_b}, v11c BAL={t11c_b}")
print()
hdr = f"  {'Period':<22}{'Variant':<22}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}"
print(hdr); print("  " + "-"*len(hdr))

for label, st, en in periods:
    m10 = window_metrics(ba_v10, st, en)
    m11b = window_metrics(ba_v11b, st, en)
    m11c = window_metrics(ba_v11c, st, en)
    if not (m10 and m11b and m11c): continue
    print(f"  {label:<22}{'v10+v4':<22}{m10['cagr']:>8.2f}{m10['sharpe']:>8.2f}"
          f"{m10['mdd']:>9.1f}{m10['calmar']:>8.2f}{m10['wealth']:>8.2f}")
    print(f"  {label:<22}{'v11b: v8c+FinRE_mod':<22}{m11b['cagr']:>8.2f}{m11b['sharpe']:>8.2f}"
          f"{m11b['mdd']:>9.1f}{m11b['calmar']:>8.2f}{m11b['wealth']:>8.2f}")
    print(f"  {label:<22}{'v11c: v11b+lower_TA':<22}{m11c['cagr']:>8.2f}{m11c['sharpe']:>8.2f}"
          f"{m11c['mdd']:>9.1f}{m11c['calmar']:>8.2f}{m11c['wealth']:>8.2f}")
    print(f"  {label:<22}{'Δ(v11b-v10)':<22}{m11b['cagr']-m10['cagr']:>+8.2f}"
          f"{m11b['sharpe']-m10['sharpe']:>+8.2f}{m11b['mdd']-m10['mdd']:>+9.1f}"
          f"{m11b['calmar']-m10['calmar']:>+8.2f}{m11b['wealth']-m10['wealth']:>+8.2f}")
    print(f"  {label:<22}{'Δ(v11c-v10)':<22}{m11c['cagr']-m10['cagr']:>+8.2f}"
          f"{m11c['sharpe']-m10['sharpe']:>+8.2f}{m11c['mdd']-m10['mdd']:>+9.1f}"
          f"{m11c['calmar']-m10['calmar']:>+8.2f}{m11c['wealth']-m10['wealth']:>+8.2f}")
    print()

pd.DataFrame({"v10_v4":ba_v10,"v11b":ba_v11b,"v11c":ba_v11c}).to_csv("ba_v11bc_vs_v10_nav.csv")
print("Saved ba_v11bc_vs_v10_nav.csv")
