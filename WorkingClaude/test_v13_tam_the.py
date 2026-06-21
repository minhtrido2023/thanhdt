#!/usr/bin/env python3
"""
test_v13_tam_the.py — v13 "Tam Thế" full architecture backtest

Architecture:
  - 25B BA v11 BAL book (unchanged from v12)
  - 25B LAGGED V5 book (NEW: NP_R≥15 + surprise_B_MA≥0.5, hold 25, max_pos=12, pos_pct=0.08)
  - V6 ETF parking on BAL leg

Compare to:
  - v11 production (BAL+VN30+ETF) — 19.42% CAGR baseline
  - v12 (BAL+LAGGED HL_3y+ETF) — 21.37% CAGR
  - v13 (BAL+LAGGED V5+ETF) — expected ~22%

Plus walk-forward IS/OOS for v13.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq

with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
SIGNAL_V11_UNIFIED = _extract("SIGNAL_V11_UNIFIED")
VNI_QUERY_UNIFIED = _extract("VNI_QUERY_UNIFIED")

START_DATE = "2014-01-01"; END_DATE = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
DEPOSIT = 0.01; ETF_STATES = {3: 0.7}

print("="*100)
print("  v13 'TAM THẾ' 🔱 — BAL + LAGGED V5 (surprise) + ETF")
print("="*100)

# ─── 1. BAL book at 25B (reuse production code) ──────────────────────────
print("\n[1] Running BA v11 BAL book at 25B ...")
with open("ba_v11_unified_12y_sig.pkl", "rb") as f: sig = pickle.load(f)
sig["time"] = pd.to_datetime(sig["time"])
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
state5 = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state5["time"] = pd.to_datetime(state5["time"])
vni_full = vni_full.merge(state5, on="time", how="left")
vni_full["state"] = vni_full["state"].ffill()
vni_full["overheat"] = ((vni_full["Close"]/vni_full["MA200"] > 1.30) & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
mask = sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11)
sig.loc[mask, "play_type"] = "AVOID_overheated"
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
vni = bq(VNI_QUERY_UNIFIED.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
vn30_underlying = dict(zip(vni["time"], vni["Close"]))
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
state_by_date = dict(zip(state5["time"], state5["state"]))
state_by_date_ff = {}
last_state = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_state = s
    state_by_date_ff[d] = last_state

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    **LIQ_FULL, name="BAL_25B")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
nav_bal_s = nav_bal.set_index("time")["nav"]
print(f"  BAL final at 25B: {nav_bal_s.iloc[-1]/1e9:.2f}B  | trades: {len(trades_bal)}")

# ─── 2. LAGGED V5 book at 25B ────────────────────────────────────────────
print("\n[2] Running LAGGED V5 (NP_R + surprise B_MA) at 25B ...")

with open("earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)
with open("lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

# Compute surprise
with open("earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)

ev_class = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev_v5 = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                        on=["ticker","quarter","Release_Date"], how="left")
# V5 filter
e_v5 = ev_v5[(ev_v5["NP_R"] >= 15) & (ev_v5["surprise_B_MA"] >= 0.5)].copy()
print(f"  V5 qualified events: {len(e_v5):,}")

def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

ENTRY_OFFSET, HOLD_DAYS, MAX_POS, POS_PCT, LIQ_MIN = 5, 25, 12, 0.08, 2e9
schedule = []
for _, row in e_v5.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY_OFFSET); exit_dt = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")

# LAGGED V5 sim at 25B
LAGGED_INIT = BOOK_NAV
sw, ew = pd.Timestamp("2014-01-02"), pd.Timestamp("2026-05-15")
sim_days = [d for d in master_idx if sw <= d <= ew]
cash_l = LAGGED_INIT; positions_l = {}; nav_history_l = []; trades_l = []
SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
LIQ_CAP, MAX_FILL = 0.20, 5
daily_rate = (1+DEPOSIT)**(1/365.25) - 1
for dt in sim_days:
    cash_l *= (1 + daily_rate)
    if dt in exits_by_day.groups:
        for _, ex_row in exits_by_day.get_group(dt).iterrows():
            tk = ex_row["ticker"]
            if tk not in positions_l: continue
            pos = positions_l[tk]
            if pos["exit_dt"] != dt: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx <= 0:
                fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
            gross = pos["shares"]*fpx*(1-SLIP_OUT); net = gross*(1-TAX); cash_l += net
            trades_l.append({"ret_pct":(fpx/pos["entry_px"]-1)*100})
            del positions_l[tk]
    if dt in entries_by_day.groups:
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions_l.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_now = cash_l + mtm
        for _, en_row in entries_by_day.get_group(dt).iterrows():
            tk = en_row["ticker"]
            if tk in positions_l or len(positions_l) >= MAX_POS: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx <= 0: continue
            adv = liq_l.at[dt, tk] if tk in liq_l.columns else 0
            if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
            target = POS_PCT * nav_now
            cap = LIQ_CAP * adv * MAX_FILL * fpx
            alloc = min(target, cap)
            if alloc < 1e6 or alloc > cash_l: continue
            eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
            cash_l -= cost
            positions_l[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares, "entry_px":fpx}
    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions_l.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav_history_l.append({"time":dt,"nav":cash_l+mtm})
nav_lag_df = pd.DataFrame(nav_history_l).set_index("time")
nav_lag_s = nav_lag_df["nav"]
print(f"  LAGGED V5 final at 25B: {nav_lag_s.iloc[-1]/1e9:.2f}B  | trades: {len(trades_l)}")

# ─── 3. Combine + Load v11 + v12 baselines ───────────────────────────────
print("\n[3] Combining v13 + loading v11/v12 baselines ...")
common = nav_bal_s.index.intersection(nav_lag_s.index)
nav_v13 = (nav_bal_s.loc[common] + nav_lag_s.loc[common]) / TOTAL_NAV  # normalize

# v11 production (already saved)
ba_v11_prod = pd.read_csv("ba_v11_production_12y_nav.csv", index_col=0, parse_dates=True).iloc[:,0]
# v12 from option1 result (saved earlier)
v12 = pd.read_csv("option1_bal_lagged_vs_prod.csv", index_col=0, parse_dates=True)["OPT1_BAL+LAGGED"]

common_all = nav_v13.index.intersection(ba_v11_prod.index).intersection(v12.index)
nav_v13 = nav_v13.loc[common_all]
nav_v11 = ba_v11_prod.loc[common_all]
nav_v12 = v12.loc[common_all]

vni_aligned = vni.set_index("time")["Close"].reindex(common_all).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

# ─── 4. Metrics ──────────────────────────────────────────────────────────
def metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    rets = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((s - s.cummax())/s.cummax()).min()
    cal = cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100,"Calmar":cal,"wealth":s.iloc[-1]/s.iloc[0]}

periods = [
    ("FULL 2014-26",  common_all.min(), common_all.max()),
    ("OOS 2024-26",   pd.Timestamp("2024-01-01"), common_all.max()),
    ("Pre-OOS 14-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-23",   pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2022",         pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Y2025",         pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    ("Q1 2026",       pd.Timestamp("2025-12-30"), common_all.max()),
]

print("\n" + "="*120)
print("  v11 'Song Sinh' vs v12 'Âm Dương' vs v13 'Tam Thế'")
print("="*120)
for label, st, en in periods:
    print(f"\n  --- {label} ---")
    print(f"  {'System':<22}{'CAGR':>9}{'Sharpe':>9}{'DD':>9}{'Calmar':>8}{'Wealth':>9}")
    for name, nav in [("v11 Song Sinh", nav_v11), ("v12 Âm Dương", nav_v12), ("v13 Tam Thế", nav_v13), ("VNI", vni_n)]:
        m = metrics(nav, st, en)
        if not m: continue
        print(f"  {name:<22}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+9.2f}{m['DD']:>+8.2f}%{m['Calmar']:>+8.2f}{m['wealth']:>+9.2f}")

# ─── 5. Walk-forward v13 ─────────────────────────────────────────────────
print("\n" + "="*100)
print("  WALK-FORWARD v13 vs v12 vs v11")
print("="*100)
windows = [
    ("P1_IS_14-18",  pd.Timestamp("2014-01-01"), pd.Timestamp("2018-12-31")),
    ("P2_OOS_19-26", pd.Timestamp("2019-01-01"), common_all.max()),
    ("P3_IS_14-20",  pd.Timestamp("2014-01-01"), pd.Timestamp("2020-12-31")),
    ("P4_OOS_21-26", pd.Timestamp("2021-01-01"), common_all.max()),
    ("P5_IS_14-22",  pd.Timestamp("2014-01-01"), pd.Timestamp("2022-12-31")),
    ("P6_OOS_23-26", pd.Timestamp("2023-01-01"), common_all.max()),
]
print(f"\n  {'Window':<14}{'v11 CAGR':>10}{'v12 CAGR':>10}{'v13 CAGR':>10}{'v13-v12 Δ':>12}{'v11 Sh':>9}{'v12 Sh':>9}{'v13 Sh':>9}")
print("  " + "-"*88)
for wn, sw, ew in windows:
    m11 = metrics(nav_v11, sw, ew); m12 = metrics(nav_v12, sw, ew); m13 = metrics(nav_v13, sw, ew)
    if not (m11 and m12 and m13): continue
    delta = m13["CAGR"] - m12["CAGR"]
    print(f"  {wn:<14}{m11['CAGR']:>+9.2f}%{m12['CAGR']:>+9.2f}%{m13['CAGR']:>+9.2f}%{delta:>+11.2f}{m11['Sharpe']:>+9.2f}{m12['Sharpe']:>+9.2f}{m13['Sharpe']:>+9.2f}")

# ─── 6. Save ─────────────────────────────────────────────────────────────
out_df = pd.DataFrame({"v11":nav_v11, "v12":nav_v12, "v13":nav_v13})
out_df.to_csv("v13_tam_the_comparison.csv")
print("\nSaved: v13_tam_the_comparison.csv")
