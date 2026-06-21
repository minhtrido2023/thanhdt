#!/usr/bin/env python3
"""compare_v11_v12_v121_with_v34b.py — V11 / V12 / V12.1 under Tam Quan v3.4b state.

Goal: OOS 2024-2026 evaluation (per user request 2026-05-22).

3 stacks (all using `vnindex_5state_tam_quan_v3_4b_full_history.csv` for state):
  V11   = 25B BAL (BA v11) + 25B VN30 (BA v11 on top-30 universe) + ETF parking
  V12   = 25B BAL + 25B LAGGED HL_3y (fixed 8% sizing) + ETF parking
  V12.1 = 25B BAL + 25B LAGGED HL_3y + S2 sizing (10% if surprise_B_MA>0.5 else 8%) + ETF parking

The BAL and VN30 legs are state-aware (ETF parking by state, plus overheat AVOID).
The LAGGED leg is state-INDEPENDENT (HL_3y filter is fundamentals-driven).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, re, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

# ─────── Config ───────────────────────────────────────────────────────────────
START_B = "2014-01-01"; END_B = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10; ETF_STATES = {3: 0.7}   # cost model per user 2026-05-23
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
STATE_CSV = "vnindex_5state_tam_quan_v3_4b_full_history.csv"

print("="*100); print(f"  V11 vs V12 vs V12.1 — ALL under Tam Quan v3.4b 'Định Tâm' state"); print("="*100)
print(f"  Period: {START_B} → {END_B}   |   NAV: 50B (25B / 25B split)")

# ─────── 1. Load signals + state + universe ──────────────────────────────────
print("\n[1] Loading signals, prices, state...")
with open("ba_v11_unified_12y_sig.pkl", "rb") as f: sig_B = pickle.load(f)
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

# State source = v3.4b
state_df = pd.read_csv(STATE_CSV)
state_df["time"] = pd.to_datetime(state_df["time"])
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

# ─────── 2. BAL leg (shared by all 3) ────────────────────────────────────────
print("\n[2] Running BAL leg @ 25B (BA v11, v3.4b state)...")
nav_bal, _ = simulate(sig_v, prices_B, vni_dates_B,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sbd_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ, name="BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
nav_bal_s = nav_bal.set_index("time")["nav"]
print(f"  BAL final: {nav_bal_s.iloc[-1]/1e9:.2f}B")

# ─────── 3. VN30 leg (V11 only) ──────────────────────────────────────────────
print("\n[3] Running VN30 leg @ 25B (BA v11 on top-30, v3.4b state)...")
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
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
nav_vn30_s = nav_vn30.set_index("time")["nav"]
print(f"  VN30 final: {nav_vn30_s.iloc[-1]/1e9:.2f}B")

# ─────── 4. LAGGED HL_3y leg (V12 / V12.1) ───────────────────────────────────
print("\n[4] Building LAGGED HL_3y schedule (state-independent)...")
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
with open("earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                     on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]
        cur_date = row["Release_Date"]
        n_good = len(good_history)
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
print(f"  HL_3y qualified events: {len(e_hl3):,}")

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
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt,
                     "surprise":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")

def run_lagged_book(init_nav, use_s2_sizing, sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = init_nav; positions = {}; nav_history = []
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    LIQ_CAP, MAX_FILL = 0.20, 5
    # cost model: deposit=0%, no daily cash accrual. LAGGED is no-margin (guard alloc>cash).
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
                gross = pos["shares"]*fpx*(1-SLIP_OUT); net = gross*(1-TAX); cash += net
                del positions[tk]
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
                pos_pct = (0.10 if en_row["surprise"] > 0.5 else 0.08) if use_s2_sizing else 0.08
                target = pos_pct * nav_now
                cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares, "entry_px":fpx}
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nav_history).set_index("time")["nav"]

print("\n[5] Running LAGGED book — V12 (fixed 8%) ...")
nav_lag_v12 = run_lagged_book(BOOK_NAV, use_s2_sizing=False)
print(f"  V12 LAGGED final: {nav_lag_v12.iloc[-1]/1e9:.2f}B")

print("\n[6] Running LAGGED book — V12.1 (S2 sizing) ...")
nav_lag_v121 = run_lagged_book(BOOK_NAV, use_s2_sizing=True)
print(f"  V12.1 LAGGED final: {nav_lag_v121.iloc[-1]/1e9:.2f}B")

# ─────── 7. Combine into 3 stacks ────────────────────────────────────────────
common = nav_bal_s.index.intersection(nav_vn30_s.index).intersection(nav_lag_v121.index)
nav_v11  = (nav_bal_s.loc[common] + nav_vn30_s.loc[common]) / TOTAL_NAV
nav_v12  = (nav_bal_s.loc[common] + nav_lag_v12.loc[common]) / TOTAL_NAV
nav_v121 = (nav_bal_s.loc[common] + nav_lag_v121.loc[common]) / TOTAL_NAV
vni_aligned = vni_B.set_index("time")["Close"].reindex(common).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

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
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100,"Calmar":cal,"wealth":s.iloc[-1]/s.iloc[0],"ret":(s.iloc[-1]/s.iloc[0]-1)*100}

periods = [
    ("FULL 2014-26",     common.min(), common.max()),
    ("OOS 2024-26 ⭐",    pd.Timestamp("2024-01-01"), common.max()),
    ("Pre-OOS 14-19",    pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-23",      pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2024 only",       pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")),
    ("Y2025 only",       pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    ("Q1 2026 + May",    pd.Timestamp("2025-12-30"), common.max()),
]

print("\n" + "="*110)
print("  RESULTS — V11 / V12 / V12.1 all under Tam Quan v3.4b state, 50B NAV")
print("="*110)
for label, st, en in periods:
    print(f"\n  ── {label} ──")
    print(f"  {'System':<22}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>9}{'TotRet':>9}")
    print(f"  {'-'*22}{'-'*9}{'-'*9}{'-'*9}{'-'*8}{'-'*9}{'-'*9}")
    for name, nav in [("V11 (BAL+VN30)", nav_v11), ("V12 (BAL+LAGGED)", nav_v12),
                       ("V12.1 (BAL+LAG+S2)", nav_v121), ("VNI B&H", vni_n)]:
        m = metrics(nav, st, en)
        if not m: continue
        print(f"  {name:<22}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+9.2f}{m['DD']:>+8.2f}%{m['Calmar']:>+8.2f}{m['wealth']:>+9.2f}{m['ret']:>+8.2f}%")

# Year-by-year (OOS only)
print("\n  ── Year-by-year annual returns (%) ──")
print(f"  {'Year':<6}{'V11':>10}{'V12':>10}{'V12.1':>10}{'VNI':>10}")
print(f"  {'-'*6}{'-'*10}{'-'*10}{'-'*10}{'-'*10}")
for yr in range(2014, 2027):
    sy = pd.Timestamp(f"{yr}-01-01"); ey = pd.Timestamp(f"{yr}-12-31")
    row = [f"  {yr:<6}"]
    for nav in [nav_v11, nav_v12, nav_v121, vni_n]:
        s = nav[(nav.index>=sy) & (nav.index<=ey)]
        if len(s)<2: row.append(f"{'—':>10}"); continue
        r = (s.iloc[-1]/s.iloc[0]-1)*100
        row.append(f"{r:>+9.1f}%")
    print("".join(row))

# Save
out_df = pd.DataFrame({"v11":nav_v11, "v12":nav_v12, "v12.1":nav_v121, "vni":vni_n})
out_df.to_csv("compare_v11_v12_v121_v34b.csv")
print(f"\n  Saved daily NAV: compare_v11_v12_v121_v34b.csv")
print("\n" + "="*110); print("DONE.")
