#!/usr/bin/env python3
"""test_v5_v121ens_kelly_dt.py — V5 (V121_ENS + KELLY) × {TQ34b, DT_10_25_25}.

Tests canonical V5 architecture (V121 ensemble switching BAL+VN30 ↔ BAL+LAGGED v12.1 with KELLY ETF parking) under both state series.

Per memory: V5 prod spec FULL CAGR 26.09% (TQ34b canonical). This test should reproduce that, then compare against DT.

Hypothesis: KELLY (100% NEUTRAL parking) amplifies state sensitivity. V11→V5 KELLY: DT helped +1.90pp. Maybe V121_ENS+KELLY+DT will also benefit?
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
DEPOSIT = 0.0; BORROW = 0.10
ETF_KELLY = {3: 1.0}        # V5
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
SWITCH_COST = 0.005

STATE_VARIANTS = {
    "TQ":  "vnindex_5state_tam_quan_v3_4b_full_history.csv",
    "DT":  "vnindex_5state_dt_10_25_25.csv",
}

print("="*100); print("  V5 = V121_ENS + KELLY × {TQ34b, DT_10_25_25}"); print("="*100)

# ─── Load common ─────────────────────────────────────────────────────────
print("\n[1] Load...")
cached = pd.read_csv("compare_v11_v12_concentration_switch.csv", index_col=0, parse_dates=True)
sig_m1 = cached["sig_m1"].dropna().astype(int)
sig_m3 = cached["sig_m3"].dropna().astype(int)

with open("ba_v11_unified_12y_sig.pkl", "rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
sig_B = sig_B[(sig_B["time"]>=START_B) & (sig_B["time"]<=END_B)].copy()

with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)
prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# ─── LAGGED v12.1 (state-independent) ────────────────────────────────────
print("\n[2] LAGGED v12.1...")
with open("earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = master_idx
all_dates = np.array(master_idx)
with open("lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
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
ENTRY_OFFSET, HOLD_DAYS, MAX_POS_L, LIQ_MIN = 5, 25, 12, 2e9
schedule = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY_OFFSET); exit_dt = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk,"entry_dt":entry_dt,"exit_dt":exit_dt,"surprise":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")

def run_lagged_v121(init_nav, sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = init_nav; positions = {}; nav_history = []
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    LIQ_CAP, MAX_FILL = 0.20, 5
    sched_dict = {(r["ticker"], r["entry_dt"]): r["surprise"] for _, r in sched_lag.iterrows()}
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
                if tk in positions or len(positions) >= MAX_POS_L: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq_l.at[dt, tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
                surprise = sched_dict.get((tk, dt), 0)
                pos_pct = 0.10 if surprise > 0.5 else 0.08
                target = pos_pct * nav_now; cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt,"exit_dt":en_row["exit_dt"],"shares":shares,"entry_px":fpx}
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nav_history).set_index("time")["nav"]

print("  Running LAGGED v12.1...")
nav_lag = run_lagged_v121(BOOK_NAV)
print(f"    LAGGED: {nav_lag.iloc[-1]/1e9:.2f}B")

# ─── BAL + VN30 with KELLY per state ────────────────────────────────────
def run_state_kelly(state_label):
    csv = STATE_VARIANTS[state_label]
    print(f"\n[{state_label}] BAL_KELLY + VN30_KELLY with {state_label}...")
    state_df = pd.read_csv(csv); state_df["time"] = pd.to_datetime(state_df["time"])
    state_df = state_df[(state_df["time"]>=START_B) & (state_df["time"]<=END_B)][["time","state"]]
    sbd = dict(zip(state_df["time"], state_df["state"]))
    sff = {}; last = None
    for d in vni_dates_B:
        s = sbd.get(d)
        if s is not None: last = s
        sff[d] = last
    v = vni_full.merge(state_df, on="time", how="left"); v["state"] = v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
    overheat_dates = set(v[v["overheat"]]["time"])
    sig_v = sig_B.copy()
    sig_v.loc[sig_v["time"].isin(overheat_dates) & sig_v["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

    print(f"  Running BAL_KELLY...")
    nav_bal, _ = simulate(sig_v, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sff,
        cash_etf_states=ETF_KELLY, vn30_underlying=vn30_underlying, **LIQ, name=f"BAL_KELLY_{state_label}")
    nav_bal["time"] = pd.to_datetime(nav_bal["time"]); nav_bal_s = nav_bal.set_index("time")["nav"]
    print(f"    BAL_KELLY: {nav_bal_s.iloc[-1]/1e9:.2f}B")

    print(f"  Running VN30_KELLY...")
    sig30 = sig_v[sig_v["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v_ for k,v_ in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nav_vn30, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map, deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sff,
        cash_etf_states=ETF_KELLY, vn30_underlying=vn30_underlying, **LIQ30, name=f"VN30_KELLY_{state_label}")
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"]); nav_vn30_s = nav_vn30.set_index("time")["nav"]
    print(f"    VN30_KELLY: {nav_vn30_s.iloc[-1]/1e9:.2f}B")
    return nav_bal_s, nav_vn30_s

state_results = {}
for state_label in STATE_VARIANTS:
    state_results[state_label] = run_state_kelly(state_label)

# ─── Ensemble switching ─────────────────────────────────────────────────
def ensemble_AND_hold(m1, m3):
    out = np.zeros(len(m1), dtype=int)
    cur = int(m1.iloc[0])
    for i, (a, b) in enumerate(zip(m1.values, m3.values)):
        if a == b: cur = int(a)
        out[i] = cur
    return pd.Series(out, index=m1.index)

def switched_nav(bal_ret, vn30_ret, lag_ret, signal, switch_cost=SWITCH_COST):
    common = bal_ret.index
    nav_bal_path = (1+bal_ret).cumprod() * BOOK_NAV
    second = np.full(len(common), BOOK_NAV, dtype=float)
    prev_sig = int(signal.iloc[0])
    for i in range(1, len(common)):
        cur_sig = int(signal.iloc[i])
        if cur_sig != prev_sig: second[i] = second[i-1] * (1 - switch_cost)
        else: second[i] = second[i-1]
        r = vn30_ret.iloc[i] if cur_sig==1 else lag_ret.iloc[i]
        second[i] = second[i] * (1 + r)
        prev_sig = cur_sig
    total = nav_bal_path.values + second
    return pd.Series(total / TOTAL_NAV, index=common)

print("\n[4] Building V5 ensemble NAVs...")
ens_navs = {}
for state_label, (nav_bal, nav_vn30) in state_results.items():
    common = nav_bal.index.intersection(nav_vn30.index).intersection(nav_lag.index)
    if len(common) < 100: continue
    m1 = sig_m1.reindex(common).ffill().fillna(1).astype(int)
    m3 = sig_m3.reindex(common).ffill().fillna(1).astype(int)
    sig_AH = ensemble_AND_hold(m1, m3)
    bal_ret = nav_bal.loc[common].pct_change().fillna(0)
    vn30_ret = nav_vn30.loc[common].pct_change().fillna(0)
    lag_ret = nav_lag.loc[common].pct_change().fillna(0)
    # V5 = V121_ENS + KELLY: ensemble switching BAL+VN30 ↔ BAL+LAGGED, all with KELLY ETF
    ens_navs[f"V5_V121ENS_{state_label}"] = switched_nav(bal_ret, vn30_ret, lag_ret, sig_AH)

# Also build for reference: V11+KELLY, V12.1+KELLY static
for state_label, (nav_bal, nav_vn30) in state_results.items():
    common = nav_bal.index.intersection(nav_vn30.index).intersection(nav_lag.index)
    ens_navs[f"V11_KELLY_static_{state_label}"] = (nav_bal.loc[common] + nav_vn30.loc[common]) / TOTAL_NAV
    ens_navs[f"V12_1_KELLY_static_{state_label}"] = (nav_bal.loc[common] + nav_lag.loc[common]) / TOTAL_NAV

def metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    rets = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((s - s.cummax())/s.cummax()).min()
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100,"wealth":s.iloc[-1]/s.iloc[0]}

periods = [
    ("FULL 2014-26", pd.Timestamp("2014-01-01"), pd.Timestamp("2026-05-15")),
    ("IS 14-19",     pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("OOS 20-26",    pd.Timestamp("2020-01-01"), pd.Timestamp("2026-05-15")),
    ("OOS 24-26",    pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-15")),
]

print("\n" + "="*100)
print("  RESULTS — V5 V121_ENS + KELLY × {TQ34b, DT_10_25_25}")
print("="*100)
for label, st, en in periods:
    print(f"\n  ── {label} ──")
    print(f"  {'System':<32}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Wealth':>9}")
    for name in ["V11_KELLY_static_TQ","V11_KELLY_static_DT",
                 "V12_1_KELLY_static_TQ","V12_1_KELLY_static_DT",
                 "V5_V121ENS_TQ","V5_V121ENS_DT"]:
        if name not in ens_navs: continue
        m = metrics(ens_navs[name], st, en)
        if not m: continue
        print(f"  {name:<32}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+9.2f}{m['DD']:>+8.2f}%{m['wealth']:>+9.2f}")

# Δ analysis: V5 with DT vs TQ
print("\n" + "="*100)
print("  Δ ANALYSIS — V5 (V121_ENS + KELLY) DT vs TQ")
print("="*100)
for label, st, en in periods:
    print(f"\n  [{label}]")
    m_tq = metrics(ens_navs["V5_V121ENS_TQ"], st, en)
    m_dt = metrics(ens_navs["V5_V121ENS_DT"], st, en)
    if not m_tq or not m_dt: continue
    d_cagr = m_dt["CAGR"] - m_tq["CAGR"]
    d_dd   = m_dt["DD"]   - m_tq["DD"]
    print(f"  V5 TQ : {m_tq['CAGR']:+.2f}%  Sh={m_tq['Sharpe']:.2f}  DD={m_tq['DD']:+.1f}%")
    print(f"  V5 DT : {m_dt['CAGR']:+.2f}%  Sh={m_dt['Sharpe']:.2f}  DD={m_dt['DD']:+.1f}%  Δ={d_cagr:+.2f}pp Δ_DD={d_dd:+.1f}pp")

# Sub-period for V5
print("\n  Per-year breakdown V5_V121ENS:")
print(f"  {'Year':<6}{'TQ':>10}{'DT':>10}{'Δ':>9}")
for yr in range(2014, 2027):
    sy = pd.Timestamp(f"{yr}-01-01"); ey = pd.Timestamp(f"{yr}-12-31")
    s_tq = ens_navs["V5_V121ENS_TQ"]; s_dt = ens_navs["V5_V121ENS_DT"]
    sub_tq = s_tq[(s_tq.index>=sy) & (s_tq.index<=ey)]
    sub_dt = s_dt[(s_dt.index>=sy) & (s_dt.index<=ey)]
    if len(sub_tq) < 5 or len(sub_dt) < 5:
        print(f"  {yr:<6}  ---       ---       ---")
        continue
    r_tq = (sub_tq.iloc[-1]/sub_tq.iloc[0]-1)*100
    r_dt = (sub_dt.iloc[-1]/sub_dt.iloc[0]-1)*100
    print(f"  {yr:<6}{r_tq:>+8.1f}%{r_dt:>+8.1f}%{r_dt-r_tq:>+7.1f}pp")

combined = pd.DataFrame(ens_navs)
combined.to_csv(os.path.join(WORKDIR, "data/v5_v121ens_kelly_dt_nav.csv"))
print(f"\n  Saved -> data/v5_v121ens_kelly_dt_nav.csv")
