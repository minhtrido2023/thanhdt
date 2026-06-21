#!/usr/bin/env python3
"""test_v121_ens_dt_c3clean.py — V121_ENS + DT + C3_clean full stack test.

Final untested combo: do all 3 levers stack for V12.1 ensemble?
  - Architecture: V12.1 LAG ensemble (BAL + LAGGED v12.1 + M1+M3 AND-HOLD switching)
  - State: TQ34b vs DT_10_25_25
  - Filter: V_PROD (Python SVT applied) vs C3_clean (no SVT)

2×2 matrix per architecture. Compare to canonical baseline.

Production V121_ENS uses Python post-filter sv_tight_keep (V_PROD-style).
Removing it = C3_clean for the ensemble.
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
DEPOSIT = 0.0; BORROW = 0.10; ETF_STATES = {3: 0.7}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
SWITCH_COST = 0.005

STATE_VARIANTS = {
    "TQ":  "data/vnindex_5state_tam_quan_v3_4b_full_history.csv",
    "DT":  "data/vnindex_5state_dt_10_25_25.csv",
}
FILTERS = {
    "PROD":  {1: 30, 2: 60, 3: 60},  # Python SVT applied
    "CLEAN": None,                    # No SVT
}

print("="*100); print("  V121_ENS + DT + C3_clean — 2×2 matrix"); print("="*100)

# ─── Common load ─────────────────────────────────────────────────────────
print("\n[1] Loading...")
cached = pd.read_csv("data/compare_v11_v12_concentration_switch.csv", index_col=0, parse_dates=True)
sig_m1 = cached["sig_m1"].dropna().astype(int)
sig_m3 = cached["sig_m3"].dropna().astype(int)

with open("data/ba_v11_unified_12y_sig.pkl", "rb") as f: sig_B = pickle.load(f)
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

# ─── LAGGED leg (state-independent, runs ONCE) ──────────────────────────
print("\n[2] LAGGED leg (V12.1 with S2 sizing)...")
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

print("  Running LAGGED V12.1 (S2 sizing)...")
nav_lag = run_lagged_v121(BOOK_NAV)
print(f"    LAGGED: {nav_lag.iloc[-1]/1e9:.2f}B")

# ─── BAL + VN30 per state × filter ──────────────────────────────────────
def apply_sv_tight(sig, sff, days_by_state):
    if days_by_state is None: return sig.copy()
    sig = sig.copy()
    if "state5" in sig.columns: sig = sig.drop(columns=["state5"])
    sss = pd.DataFrame({"time": list(sff.keys()), "state5": list(sff.values())})
    sig = sig.merge(sss, on="time", how="left")
    def keep(row):
        s = row.get("state5"); days = row.get("days_since_release")
        if pd.isna(s): return True
        s = int(s)
        if s in (4,5): return True
        thr = days_by_state.get(s)
        if thr is None: return True
        return pd.notna(days) and days <= thr
    mb_buy = sig["play_type"].isin(BUY_TIERS_V11)
    keep_mask = (~mb_buy) | sig.apply(keep, axis=1)
    return sig[keep_mask].copy()

def run_state_filter(state_label, filter_label):
    print(f"\n[{state_label}+{filter_label}] BAL + VN30...")
    state_df = pd.read_csv(STATE_VARIANTS[state_label])
    state_df["time"] = pd.to_datetime(state_df["time"])
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

    # Apply SVT filter (or skip if C3_clean)
    sig_v = apply_sv_tight(sig_B, sff, FILTERS[filter_label])
    sig_v.loc[sig_v["time"].isin(overheat_dates) & sig_v["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

    nav_bal, _ = simulate(sig_v, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ, name=f"BAL_{state_label}_{filter_label}")
    nav_bal["time"] = pd.to_datetime(nav_bal["time"]); nav_bal_s = nav_bal.set_index("time")["nav"]
    print(f"  BAL: {nav_bal_s.iloc[-1]/1e9:.2f}B")

    sig30 = sig_v[sig_v["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v_ for k,v_ in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nav_vn30, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map, deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ30, name=f"VN30_{state_label}_{filter_label}")
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"]); nav_vn30_s = nav_vn30.set_index("time")["nav"]
    print(f"  VN30: {nav_vn30_s.iloc[-1]/1e9:.2f}B")
    return nav_bal_s, nav_vn30_s

results = {}
for state_label in STATE_VARIANTS:
    for filter_label in FILTERS:
        key = f"{state_label}+{filter_label}"
        results[key] = run_state_filter(state_label, filter_label)

# ─── Ensemble + metrics ─────────────────────────────────────────────────
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

print("\n[4] Building ensemble V121_ENS NAVs for each combo...")
ens_navs = {}
for key, (nav_bal, nav_vn30) in results.items():
    common = nav_bal.index.intersection(nav_vn30.index).intersection(nav_lag.index)
    if len(common) < 100: continue
    m1 = sig_m1.reindex(common).ffill().fillna(1).astype(int)
    m3 = sig_m3.reindex(common).ffill().fillna(1).astype(int)
    sig_AH = ensemble_AND_hold(m1, m3)
    bal_ret = nav_bal.loc[common].pct_change().fillna(0)
    vn30_ret = nav_vn30.loc[common].pct_change().fillna(0)
    lag_ret = nav_lag.loc[common].pct_change().fillna(0)
    # V121 static = BAL + LAGGED
    ens_navs[f"V121_static_{key}"] = (nav_bal.loc[common] + nav_lag.loc[common]) / TOTAL_NAV
    # V121_ENS = M1+M3 switcher (V11 mode = BAL+VN30 / V12 mode = BAL+LAGGED)
    ens_navs[f"V121_ENS_{key}"] = switched_nav(bal_ret, vn30_ret, lag_ret, sig_AH)

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
print("  RESULTS — V121_ENS × 4 combos (state × filter)")
print("="*100)

for label, st, en in periods:
    print(f"\n  ── {label} ──")
    print(f"  {'System':<32}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Wealth':>9}")
    for k in ["TQ+PROD","TQ+CLEAN","DT+PROD","DT+CLEAN"]:
        for arch_prefix in ["V121_static_", "V121_ENS_"]:
            name = arch_prefix + k
            if name not in ens_navs: continue
            m = metrics(ens_navs[name], st, en)
            if not m: continue
            print(f"  {name:<32}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+9.2f}{m['DD']:>+8.2f}%{m['wealth']:>+9.2f}")

# Additivity for V121_ENS
print("\n" + "="*100)
print("  V121_ENS ADDITIVITY (state × filter)")
print("="*100)
for label, st, en in periods:
    print(f"\n  [{label}]")
    base = "V121_ENS_TQ+PROD"
    if base not in ens_navs: continue
    m_base = metrics(ens_navs[base], st, en)
    if not m_base: continue
    m_filter = metrics(ens_navs.get("V121_ENS_TQ+CLEAN"), st, en)
    m_state = metrics(ens_navs.get("V121_ENS_DT+PROD"), st, en)
    m_both = metrics(ens_navs.get("V121_ENS_DT+CLEAN"), st, en)
    if not all([m_filter, m_state, m_both]): continue
    d_f = m_filter["CAGR"] - m_base["CAGR"]
    d_s = m_state["CAGR"] - m_base["CAGR"]
    d_b = m_both["CAGR"] - m_base["CAGR"]
    print(f"    Base TQ+PROD          : {m_base['CAGR']:+.2f}%")
    print(f"    Filter alone (TQ+CLEAN): Δ {d_f:+.2f}pp -> {m_filter['CAGR']:+.2f}%")
    print(f"    State alone (DT+PROD)  : Δ {d_s:+.2f}pp -> {m_state['CAGR']:+.2f}%")
    print(f"    Both (DT+CLEAN)        : Δ {d_b:+.2f}pp -> {m_both['CAGR']:+.2f}%")
    print(f"    Sum of singles: {d_f + d_s:+.2f}pp; Combined: {d_b:+.2f}pp; Interaction: {d_b - (d_f + d_s):+.2f}pp")
    if d_b > max(d_f, d_s) and d_b > 0:
        print(f"    -> SOMEWHAT ADDITIVE: combined > both singletons")
    elif d_b > 0:
        print(f"    -> POSITIVE BUT NOT SUPERIOR to best singleton")
    else:
        print(f"    -> CONFLICT or NEGATIVE")

combined = pd.DataFrame(ens_navs)
combined.to_csv(os.path.join(WORKDIR, "data/v121_ens_dt_c3clean_nav.csv"))
print(f"\n  Saved -> data/v121_ens_dt_c3clean_nav.csv")
