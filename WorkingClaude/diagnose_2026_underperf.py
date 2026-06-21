#!/usr/bin/env python3
"""
diagnose_2026_underperf.py
==========================
J3: investigate why D1+slot12 is -15% YTD 2026 while VNI is +22%.

Hypotheses to check:
  H1: System entered on overheated days (would have been blocked by V11 P3 filter)
  H2: System entered on stale-quarter tickers (would have been blocked by V11 SV_TIGHT)
  H3: System missed the recovery rally (entered after rally was over)
  H4: Pure bad luck — concentrated in wrong sectors

Approach:
  1. Re-run sim and extract all 2026 trades
  2. For each, look up VNI/MA200, state5, days_since_release at entry date
  3. Classify which V11 filter would have triggered
  4. Compute hypothetical PnL without V11-blocked trades
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, re as _re
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate, bq, VNI_QUERY

START_DATE = "2014-01-01"
END_DATE   = "2026-05-15"

with open(os.path.join(WORKDIR, "test_round14_stability.py"), encoding="utf-8") as _f:
    _src = _f.read()
_m = _re.search(r'SIGNAL_V10\s*=\s*"""(.+?)"""', _src, _re.DOTALL)
SIGNAL_V10_BASE = _m.group(0).split('"""', 1)[1].rsplit('"""', 1)[0]
SIGNAL_V10_BASE = SIGNAL_V10_BASE.replace(
    "CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END",
    "CASE WHEN FALSE THEN 10 ELSE 0 END")

D1_QUERY = SIGNAL_V10_BASE.replace(
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,",
    "fin_dated AS (\n  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,\n"
    "    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4, 0)) - 1 AS adv_yoy,"
).replace(
    "fin.Revenue_YoY_P0 AS rev_yoy,",
    "fin.Revenue_YoY_P0 AS rev_yoy, fin.adv_yoy AS adv_yoy, t.ICB_Code AS icb,"
).replace(
    "WHEN fa_tier = 'E' THEN 'AVOID_faE'",
    "WHEN icb = 8633.0 AND adv_yoy > 0.5 AND fa_tier IN ('C','D') "
    "AND ta >= 120 AND state5 IN (3,4,5) AND (np_yoy > 0 OR rev_yoy > 0) "
    "THEN 'RE_BACKLOG_BUY'\n"
    "    WHEN fa_tier = 'E' THEN 'AVOID_faE'"
)

TIER_BAL_D1 = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]

print("Loading data ...")
_vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
_vni["time"] = pd.to_datetime(_vni["time"])
_vni_dates = sorted(_vni["time"].unique())
_sec_map = bq("""SELECT DISTINCT t.ticker,
                CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                """).set_index("ticker")["s"].to_dict()
_top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
                WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                GROUP BY t.ticker
                ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

# Pull D1 signals
print("Pulling D1 signals ...")
sig = bq(D1_QUERY.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
       "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

print("Running D1+slot12 sim ...")
nav_bal, tr_bal = simulate(sig, prices, _vni_dates,
    allowed_tiers=TIER_BAL_D1, max_positions=12, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8: 4}, ticker_sector_map=_sec_map,
    sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},
    tier_weights={t: 0.10 for t in TIER_BAL_D1}, **LIQ)
nav_bal["time"] = pd.to_datetime(nav_bal["time"])

sig_vn30 = sig[sig["ticker"].isin(_top30)]
prices_vn30 = {tk: prices[tk] for tk in _top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in _top30}
LIQ_VN30 = {**LIQ, "liquidity_lookup": liq_vn30}
nav_vn30, tr_vn30 = simulate(sig_vn30, prices_vn30, _vni_dates,
    allowed_tiers=TIER_BAL_D1, max_positions=12, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},
    tier_weights={t: 0.10 for t in TIER_BAL_D1}, **LIQ_VN30)
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

all_trades = pd.concat([tr_bal.assign(leg="BAL"), tr_vn30.assign(leg="VN30")], ignore_index=True)
all_trades["entry_date"] = pd.to_datetime(all_trades["entry_date"])
all_trades["exit_date"]  = pd.to_datetime(all_trades["exit_date"])

# Filter 2026 trades
t26 = all_trades[all_trades["entry_date"].dt.year == 2026].copy()
print(f"\n=== 2026 TRADES SUMMARY (n={len(t26)}) ===")
print(f"  Mean ret_net: {t26['ret_net'].mean()*100:+.2f}%  Median: {t26['ret_net'].median()*100:+.2f}%  "
      f"WR: {(t26['ret_net']>0).mean()*100:.1f}%")
print(f"  By exit reason: {t26['reason'].value_counts().to_dict()}")
print(f"  By play_type: {t26['play_type'].value_counts().to_dict()}")
print(f"  By leg: {t26['leg'].value_counts().to_dict()}")

# Pull V11 context at entry date for each 2026 trade
print("\nPulling V11 context (VNI/MA200, state5, days_since_release) for 2026 entries ...")
entries_str = ",".join(f"('{r.ticker}', DATE '{r.entry_date.date()}')"
                       for _, r in t26.iterrows())
V11_CTX_SQL = f"""
WITH entries AS (
  SELECT ticker, entry_date FROM UNNEST([
    STRUCT<ticker STRING, entry_date DATE>
    {entries_str}
  ])
),
vni AS (
  SELECT time, Close AS vni_close, MA200 AS vni_ma200, D_RSI AS vni_d_rsi,
    Close / NULLIF(MA200, 0) AS vni_ratio
  FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE ticker = "VNINDEX" AND time BETWEEN DATE '2025-12-01' AND DATE '2026-05-15'
),
state AS (
  SELECT time, state AS state5
  FROM `lithe-record-440915-m9.tav2_bq.vnindex_5state`
),
last_release AS (
  SELECT e.ticker, e.entry_date,
    DATE_DIFF(e.entry_date, MAX(f.Release_Date), DAY) AS days_since_release
  FROM entries e
  LEFT JOIN `lithe-record-440915-m9.tav2_bq.ticker_financial` f
    ON f.ticker = e.ticker AND f.Release_Date <= e.entry_date
  GROUP BY e.ticker, e.entry_date
)
SELECT e.ticker, e.entry_date,
  v.vni_close, v.vni_ma200, v.vni_ratio, v.vni_d_rsi,
  s.state5,
  r.days_since_release
FROM entries e
LEFT JOIN vni v ON v.time = e.entry_date
LEFT JOIN state s ON s.time = e.entry_date
LEFT JOIN last_release r ON r.ticker = e.ticker AND r.entry_date = e.entry_date
ORDER BY e.entry_date, e.ticker
"""
ctx = bq(V11_CTX_SQL)
ctx["entry_date"] = pd.to_datetime(ctx["entry_date"])

# Forward-fill state5 (state may be missing for May 2026 dates)
ctx = ctx.sort_values("entry_date")
ctx["state5"] = ctx["state5"].ffill()

# Merge with trades
m = t26.merge(ctx, on=["ticker", "entry_date"], how="left")

# Apply V11 filters
P3_VNI_MA200_THR = 1.30
P3_VNI_RSI_THR = 0.75
FRESH_Q_BY_STATE = {1: 30, 2: 60, 3: 60}  # 4,5: no filter

def v11_block(row):
    flags = []
    # P3 overheat
    ratio = row.get("vni_ratio"); state = row.get("state5"); rsi = row.get("vni_d_rsi")
    if pd.notna(ratio) and ratio > P3_VNI_MA200_THR:
        regime_conf = (pd.notna(state) and int(state) == 5) or (pd.notna(rsi) and rsi > P3_VNI_RSI_THR)
        if regime_conf:
            flags.append("P3")
    # SV_TIGHT Fresh-Q
    days = row.get("days_since_release")
    if pd.notna(state) and pd.notna(days):
        s = int(state)
        if s in FRESH_Q_BY_STATE and days > FRESH_Q_BY_STATE[s]:
            flags.append(f"SV_TIGHT(state{s}>{FRESH_Q_BY_STATE[s]}d)")
    return "+".join(flags) if flags else "OK"

m["v11_block"] = m.apply(v11_block, axis=1)

print(f"\n=== V11 FILTER ANALYSIS ON 2026 TRADES ===")
print(f"\nDistribution of V11 block status:")
print(m["v11_block"].value_counts().to_string())

print(f"\nP&L by V11 status:")
gb = m.groupby("v11_block").agg(
    n=("ret_net","count"),
    mean=("ret_net", lambda x: x.mean()*100),
    median=("ret_net", lambda x: x.median()*100),
    wr=("ret_net", lambda x: (x>0).mean()*100),
).sort_values("n", ascending=False)
print(gb.round(2).to_string())

# Hypothetical: what if we excluded all V11-blocked trades?
allowed = m[m["v11_block"] == "OK"]
blocked = m[m["v11_block"] != "OK"]
print(f"\n=== HYPOTHETICAL: V11-filtered universe ===")
print(f"  Original 2026: n={len(m)}, mean={m['ret_net'].mean()*100:+.2f}%, "
      f"sum_ret={m['ret_net'].sum()*100:+.2f}%")
print(f"  V11-allowed:   n={len(allowed)}, mean={allowed['ret_net'].mean()*100:+.2f}%, "
      f"sum_ret={allowed['ret_net'].sum()*100:+.2f}%")
print(f"  V11-blocked:   n={len(blocked)}, mean={blocked['ret_net'].mean()*100:+.2f}%, "
      f"sum_ret={blocked['ret_net'].sum()*100:+.2f}%")

# Per-trade detail
print(f"\n=== ALL 2026 TRADES DETAIL ===")
display_cols = ["entry_date","exit_date","ticker","play_type","ret_net","reason",
                "vni_ratio","state5","days_since_release","v11_block"]
m_show = m[display_cols].copy()
m_show["ret_net"] = (m_show["ret_net"]*100).round(2)
m_show["vni_ratio"] = m_show["vni_ratio"].round(3)
m_show = m_show.sort_values("entry_date")
print(m_show.to_string(index=False))

m.to_csv("data/diagnose_2026_trades.csv", index=False)
print(f"\nSaved diagnose_2026_trades.csv")

# Recovery rally check: when did state5 shift from BEAR/CRISIS to NEUTRAL+
print(f"\n=== STATE5 TIMELINE 2026 ===")
state_2026 = bq("""SELECT time, state AS state5
                   FROM `lithe-record-440915-m9.tav2_bq.vnindex_5state`
                   WHERE time >= "2026-01-01"
                   ORDER BY time""")
state_2026["time"] = pd.to_datetime(state_2026["time"])
# Find transitions
state_2026["prev_state"] = state_2026["state5"].shift(1)
transitions = state_2026[state_2026["state5"] != state_2026["prev_state"]].dropna(subset=["prev_state"])
print(transitions.to_string(index=False))

# VNI 2026 trajectory
print(f"\n=== VNINDEX 2026 trajectory (key dates) ===")
vni_26 = _vni[_vni["time"] >= pd.Timestamp("2026-01-01")].copy()
print(f"  Start (2026-01): {vni_26.iloc[0]['Close']:.2f}")
print(f"  Min:             {vni_26['Close'].min():.2f} on {vni_26.loc[vni_26['Close'].idxmin(),'time'].date()}")
print(f"  Max:             {vni_26['Close'].max():.2f} on {vni_26.loc[vni_26['Close'].idxmax(),'time'].date()}")
print(f"  Latest:          {vni_26.iloc[-1]['Close']:.2f} on {vni_26.iloc[-1]['time'].date()}")
print(f"  YTD ret:         {(vni_26.iloc[-1]['Close']/vni_26.iloc[0]['Close']-1)*100:+.2f}%")
print(f"  Peak-to-trough DD: {(vni_26['Close'].min()/vni_26['Close'].cummax().loc[vni_26['Close'].idxmin()]-1)*100:+.2f}%")
print(f"  Trough-to-current: {(vni_26.iloc[-1]['Close']/vni_26['Close'].min()-1)*100:+.2f}%")
