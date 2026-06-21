#!/usr/bin/env python3
"""test_rolling_m3_v121_ensemble.py — Two upgrades on top of M1+M3 ensemble.

Upgrades:
  (1) M3r = rolling Top10 (trailing 1Y ADV ranking per date) — no lookahead.
      Replaces static Top10 chosen from full 2020-2025 ADV window.
  (2) Replace V12 LAGGED leg with V12.1 (S2 sizing: 10% if surprise>0.5 else 8%).

Reports each axis independently and combined.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B = "2014-01-01"; END_B = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10; ETF_STATES = {3: 0.7}   # cost model per user 2026-05-23
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
STATE_CSV = "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"
SWITCH_COST = 0.005

print("="*100); print("  ROLLING M3 + V12.1 LAGGED ensemble test"); print("="*100)

# ─── 1. Compute rolling Top10 M3 (no lookahead) ──────────────────────────────
print("\n[1] Computing M3r (rolling Top10 by trailing 1Y ADV)...")
m3r_q = """WITH base AS (
  SELECT t.time, t.ticker,
    SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret_6m,
    AVG(t.Volume_3M_P50 * t.Close) OVER (
      PARTITION BY t.ticker ORDER BY t.time
      ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING
    ) AS adv_1y
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '2026-05-15'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
),
ranked AS (
  SELECT time, ticker, ret_6m, adv_1y,
    ROW_NUMBER() OVER (PARTITION BY time ORDER BY adv_1y DESC) AS rnk
  FROM base
  WHERE adv_1y IS NOT NULL AND ret_6m IS NOT NULL
)
SELECT time, AVG(IF(rnk<=10, ret_6m, NULL)) AS top10_ret, AVG(ret_6m) AS all_ret
FROM ranked GROUP BY time ORDER BY time"""
m3r_df = bq(m3r_q); m3r_df["time"] = pd.to_datetime(m3r_df["time"])
m3r_df["M3r"] = m3r_df["top10_ret"] - m3r_df["all_ret"]
m3r = m3r_df.set_index("time")["M3r"]
print(f"  M3r range: {m3r.dropna().min():.3f} to {m3r.dropna().max():.3f}")

# Load cached M1 signal from previous run (it's daily and unchanged)
print("\n[2] Loading M1 signal from cache...")
cached = pd.read_csv("data/compare_v11_v12_concentration_switch.csv", index_col=0, parse_dates=True)
sig_m1 = cached["sig_m1"].dropna().astype(int)

# Build M3r binary signal (expanding median, T+1)
def make_signal(metric, min_history=252):
    s = metric.dropna().sort_index()
    expanding_med = s.expanding(min_periods=min_history).median()
    raw_signal = (s > expanding_med).astype(int)
    raw_signal = raw_signal.reindex(metric.index).ffill().fillna(1).astype(int)
    return raw_signal.shift(1).fillna(1).astype(int)
sig_m3r = make_signal(m3r)
print(f"  M3r signal days: {len(sig_m3r)}")

# ─── 3. Re-run 3 legs + V12.1 LAGGED variant ────────────────────────────────
print("\n[3] Re-running legs (BAL / VN30 / LAGGED-v12 / LAGGED-v121)...")
with open("data/ba_v11_unified_12y_sig.pkl", "rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
VNI_QUERY_UNIFIED = _extract("VNI_QUERY_UNIFIED")

prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
state_df = pd.read_csv(STATE_CSV); state_df["time"] = pd.to_datetime(state_df["time"])
state_df = state_df[(state_df["time"]>=START_B) & (state_df["time"]<=END_B)][["time","state"]]
sbd = dict(zip(state_df["time"], state_df["state"]))
sbd_ff = {}; last = None
for d in vni_dates_B:
    s = sbd.get(d)
    if s is not None: last = s
    sbd_ff[d] = last
v = vni_full.merge(state_df, on="time", how="left"); v["state"] = v["state"].ffill()
v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
overheat_dates = set(v[v["overheat"]]["time"])
sig_v = sig_B.copy()
sig_v.loc[sig_v["time"].isin(overheat_dates) & sig_v["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

nav_bal, _ = simulate(sig_v, prices_B, vni_dates_B,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sbd_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ, name="BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"]); nav_bal_s = nav_bal.set_index("time")["nav"]
print(f"  BAL: {nav_bal_s.iloc[-1]/1e9:.2f}B")

sig30 = sig_v[sig_v["ticker"].isin(top30)].copy()
prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
LIQ30 = {**LIQ, "liquidity_lookup":liq30}
nav_vn30, _ = simulate(sig30, prices30, vni_dates_B,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sbd_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ30, name="VN30")
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"]); nav_vn30_s = nav_vn30.set_index("time")["nav"]
print(f"  VN30: {nav_vn30_s.iloc[-1]/1e9:.2f}B")

# LAGGED books (v12 fixed-8% and v12.1 S2)
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = master_idx
all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("data/earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                     on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]; cur_date = row["Release_Date"]; n_good = len(good_history)
        ev.at[row_idx, "prior_n_good"] = n_good
        if n_good >= 1:
            dates_arr = pd.to_datetime([d for d,_ in good_history])
            posts_arr = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates_arr).days.values / 365.25
            w = np.exp(-LN2 * age_yrs / HL)
            ev.at[row_idx, "pa_HL3"] = (posts_arr * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))
e_hl3 = ev[(ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)].copy()
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])
ENTRY_OFFSET, HOLD_DAYS, MAX_POS, LIQ_MIN = 5, 25, 12, 2e9
schedule = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY_OFFSET); exit_dt = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk,"entry_dt":entry_dt,"exit_dt":exit_dt,"surprise":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")

def run_lagged(init_nav, use_s2, sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = init_nav; positions = {}; nav_history = []
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    LIQ_CAP, MAX_FILL = 0.20, 5
    # cost model: deposit=0%, no daily cash accrual. LAGGED is no-margin.
    for dt in sim_days:
        if dt in exits_by_day.groups:
            for _, ex_row in exits_by_day.get_group(dt).iterrows():
                tk = ex_row["ticker"]
                if tk not in positions: continue
                pos = positions[tk]
                if pos["exit_dt"] != dt: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0:
                    fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx <= 0: continue
                gross = pos["shares"]*fpx*(1-SLIP_OUT); cash += gross*(1-TAX); del positions[tk]
        if dt in entries_by_day.groups:
            mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm
            for _, en_row in entries_by_day.get_group(dt).iterrows():
                tk = en_row["ticker"]
                if tk in positions or len(positions) >= MAX_POS: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq_l.at[dt, tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
                pos_pct = (0.10 if en_row["surprise"] > 0.5 else 0.08) if use_s2 else 0.08
                target = pos_pct * nav_now; cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt,"exit_dt":en_row["exit_dt"],"shares":shares,"entry_px":fpx}
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nav_history).set_index("time")["nav"]

nav_lag_v12  = run_lagged(BOOK_NAV, use_s2=False); print(f"  LAGGED v12: {nav_lag_v12.iloc[-1]/1e9:.2f}B")
nav_lag_v121 = run_lagged(BOOK_NAV, use_s2=True);  print(f"  LAGGED v12.1: {nav_lag_v121.iloc[-1]/1e9:.2f}B")

# ─── 4. Build signals + switched NAVs ────────────────────────────────────────
print("\n[4] Building switched NAVs (V12 LAGGED and V12.1 LAGGED)...")
common_idx = nav_bal_s.index.intersection(nav_vn30_s.index).intersection(nav_lag_v12.index).intersection(nav_lag_v121.index)
m1 = sig_m1.reindex(common_idx).ffill().fillna(1).astype(int)
m3r = sig_m3r.reindex(common_idx).ffill().fillna(1).astype(int)

def ensemble_AND_hold(m1, m3):
    out = np.zeros(len(m1), dtype=int); cur = int(m1.iloc[0])
    for i, (a, b) in enumerate(zip(m1.values, m3.values)):
        if a == b: cur = int(a)
        out[i] = cur
    return pd.Series(out, index=m1.index)

def ensemble_AND_v11(m1, m3):
    return ((m1 == 1) & (m3 == 1)).astype(int)

sig_AND_hold = ensemble_AND_hold(m1, m3r)
sig_AND_v11  = ensemble_AND_v11(m1, m3r)

bal_ret  = nav_bal_s.loc[common_idx].pct_change().fillna(0)
vn30_ret = nav_vn30_s.loc[common_idx].pct_change().fillna(0)
lag12_ret  = nav_lag_v12.loc[common_idx].pct_change().fillna(0)
lag121_ret = nav_lag_v121.loc[common_idx].pct_change().fillna(0)

def switched_nav(bal_ret, vn30_ret, lag_ret, signal, switch_cost=SWITCH_COST):
    common = bal_ret.index
    nav_bal_path = (1+bal_ret).cumprod() * BOOK_NAV
    second = np.full(len(common), BOOK_NAV, dtype=float)
    prev_sig = int(signal.iloc[0]); flips = 0
    for i in range(1, len(common)):
        cur_sig = int(signal.iloc[i])
        if cur_sig != prev_sig:
            second[i] = second[i-1] * (1 - switch_cost); flips += 1
        else:
            second[i] = second[i-1]
        r = vn30_ret.iloc[i] if cur_sig==1 else lag_ret.iloc[i]
        second[i] = second[i] * (1 + r)
        prev_sig = cur_sig
    total = nav_bal_path.values + second
    return pd.Series(total / TOTAL_NAV, index=common), flips

# Static baselines (per LAGGED variant)
nav_v11_static = (nav_bal_s.loc[common_idx] + nav_vn30_s.loc[common_idx]) / TOTAL_NAV
nav_v12_static = (nav_bal_s.loc[common_idx] + nav_lag_v12.loc[common_idx])    / TOTAL_NAV
nav_v121_static = (nav_bal_s.loc[common_idx] + nav_lag_v121.loc[common_idx])  / TOTAL_NAV
vni_aligned = vni_B.set_index("time")["Close"].reindex(common_idx).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

# Single-metric switches
nav_m1_v12,   fm1_12 = switched_nav(bal_ret, vn30_ret, lag12_ret,  m1)
nav_m3r_v12,  f3r_12 = switched_nav(bal_ret, vn30_ret, lag12_ret,  m3r)
nav_m3r_v121, f3r_121= switched_nav(bal_ret, vn30_ret, lag121_ret, m3r)
nav_m1_v121,  fm1_121= switched_nav(bal_ret, vn30_ret, lag121_ret, m1)

# Ensembles with V12 LAGGED
nav_AH_v12,  fAH_12 = switched_nav(bal_ret, vn30_ret, lag12_ret,  sig_AND_hold)
nav_AV_v12,  fAV_12 = switched_nav(bal_ret, vn30_ret, lag12_ret,  sig_AND_v11)
# Ensembles with V12.1 LAGGED (S2 sizing)
nav_AH_v121, fAH_121= switched_nav(bal_ret, vn30_ret, lag121_ret, sig_AND_hold)
nav_AV_v121, fAV_121= switched_nav(bal_ret, vn30_ret, lag121_ret, sig_AND_v11)

print(f"  Flips: M1={fm1_12}|M3r={f3r_12}|AND-H={fAH_12}|AND-V11={fAV_12}")

# ─── 5. Metrics ──────────────────────────────────────────────────────────────
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
    ("FULL 2014-26",     common_idx.min(), common_idx.max()),
    ("OOS 2024-26 ⭐",    pd.Timestamp("2024-01-01"), common_idx.max()),
    ("Pre-OOS 14-19",    pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-23",      pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2024",            pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")),
    ("Y2025",            pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    ("Q1 2026 + May",    pd.Timestamp("2025-12-30"), common_idx.max()),
]

variants = [
    ("V11 static",                            nav_v11_static),
    ("V12 static (fixed 8%)",                 nav_v12_static),
    ("V12.1 static (S2 sizing)",              nav_v121_static),
    ("M1 switch  → V12 LAG",                  nav_m1_v12),
    ("M1 switch  → V12.1 LAG",                nav_m1_v121),
    ("M3r switch → V12 LAG",                  nav_m3r_v12),
    ("M3r switch → V12.1 LAG",                nav_m3r_v121),
    ("M1+M3r AND-HOLD → V12 LAG",             nav_AH_v12),
    ("M1+M3r AND-HOLD → V12.1 LAG ⭐",         nav_AH_v121),
    ("M1+M3r AND-V11 → V12 LAG",              nav_AV_v12),
    ("M1+M3r AND-V11 → V12.1 LAG ⭐",          nav_AV_v121),
    ("VNI B&H",                               vni_n),
]
print("\n" + "="*120)
print("  RESULTS — Rolling M3 + V12.1 LAGGED comparison")
print("="*120)
for label, st, en in periods:
    print(f"\n  ── {label} ──")
    print(f"  {'System':<36}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>9}")
    print(f"  {'-'*36}{'-'*9}{'-'*9}{'-'*9}{'-'*8}{'-'*9}")
    for name, nav in variants:
        m = metrics(nav, st, en)
        if not m: continue
        print(f"  {name:<36}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+9.2f}{m['DD']:>+8.2f}%{m['Calmar']:>+8.2f}{m['wealth']:>+9.2f}")

# Year-by-year focused on key variants
print("\n" + "="*100)
print("  YEAR-BY-YEAR (key variants only)")
print("="*100)
print(f"  {'Year':<6}{'V11':>9}{'V12':>9}{'V12.1':>10}{'AH-V12':>10}{'AH-V121':>10}{'AV-V12':>10}{'AV-V121':>10}{'VNI':>9}")
for yr in range(2014, 2027):
    sy = pd.Timestamp(f"{yr}-01-01"); ey = pd.Timestamp(f"{yr}-12-31")
    row = [f"  {yr:<6}"]
    for nav in [nav_v11_static, nav_v12_static, nav_v121_static,
                nav_AH_v12, nav_AH_v121, nav_AV_v12, nav_AV_v121, vni_n]:
        s = nav[(nav.index>=sy) & (nav.index<=ey)]
        if len(s)<2: row.append(f"{'—':>9}"); continue
        r = (s.iloc[-1]/s.iloc[0]-1)*100
        # adjust width per column header
        w = 9 if nav is nav_v11_static or nav is nav_v12_static or nav is vni_n else 10
        row.append(f"{r:>+{w-1}.1f}%")
    print("".join(row))

# Old vs new M3 comparison
print("\n" + "="*100)
print("  M3 STATIC vs M3r ROLLING (lookahead check)")
print("="*100)
sig_m3_old = pd.read_csv("data/compare_v11_v12_concentration_switch.csv", index_col=0, parse_dates=True)["sig_m3"].dropna().astype(int)
m3_old = sig_m3_old.reindex(common_idx).ffill().fillna(1).astype(int)
overlap = (m3_old.values == m3r.values).mean()*100
print(f"  Signal agreement (M3 static vs M3r rolling): {overlap:.1f}%")
nav_m3_old_v12, fold = switched_nav(bal_ret, vn30_ret, lag12_ret, m3_old)
for label, st, en in [("FULL", common_idx.min(), common_idx.max()),
                       ("OOS 2024-26", pd.Timestamp("2024-01-01"), common_idx.max())]:
    print(f"\n  -- {label} --")
    print(f"  {'Variant':<26}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}")
    for name, nav in [("M3 STATIC (lookahead) → V12", nav_m3_old_v12),
                       ("M3r ROLLING → V12",           nav_m3r_v12)]:
        m = metrics(nav, st, en)
        if not m: continue
        print(f"  {name:<26}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+9.2f}{m['DD']:>+8.2f}%")

# Save
out_df = pd.DataFrame({
    "v11":nav_v11_static,"v12":nav_v12_static,"v121":nav_v121_static,
    "m1_v12":nav_m1_v12,"m1_v121":nav_m1_v121,
    "m3r_v12":nav_m3r_v12,"m3r_v121":nav_m3r_v121,
    "AH_v12":nav_AH_v12,"AH_v121":nav_AH_v121,
    "AV_v12":nav_AV_v12,"AV_v121":nav_AV_v121,
    "vni":vni_n,"sig_AND_hold":sig_AND_hold,"sig_AND_v11":sig_AND_v11,"sig_m3r":sig_m3r.reindex(common_idx)})
out_df.to_csv("data/test_rolling_m3_v121_ensemble.csv")
print(f"\n  Saved: test_rolling_m3_v121_ensemble.csv")
print("\n" + "="*120); print("DONE.")
