#!/usr/bin/env python3
"""
test_option2_approximation.py — Approximate Option 2 (LAGGED replaces ETF parking)

True Option 2: BAL@~50B (single book) + LAGGED uses idle cash dynamically
Hard to simulate without engine modification. Approximate via fixed weights:

Variants tested:
  BAL40_LAG10  : BAL@40B + LAGGED@10B + ETF (small LAGGED parking)
  BAL35_LAG15  : BAL@35B + LAGGED@15B + ETF (moderate LAGGED)
  BAL30_LAG20  : BAL@30B + LAGGED@20B + ETF
  BAL25_LAG25  : Option 1 baseline (already known winner)
  BAL50_LAG0   : Pure BAL@50B + ETF (no LAGGED)
  BAL50_LAG10  : BAL@50B + LAGGED@10B (parallel allocation, +20% NAV — leveraged?)

Compare to Current production (BAL+VN30+ETF) and Option 1.
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
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
DEPOSIT = 0.01; ETF_STATES = {3: 0.7}
OOS_START = pd.Timestamp("2024-01-01")

print("="*100)
print("  OPTION 2 APPROXIMATION — varying BAL/LAGGED sizes")
print("="*100)

# Load signals
with open("ba_v11_unified_12y_sig.pkl", "rb") as f: sig = pickle.load(f)
sig["time"] = pd.to_datetime(sig["time"])

# P3 overheat
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

# Common data
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map_ba = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
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
LIQ_FULL_BA = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map_ba, "exit_slippage_tiered": True}

def run_bal(book_nav):
    nav_bal, trades_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=book_nav,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
        **LIQ_FULL_BA, name=f"BAL_{book_nav/1e9:.0f}B")
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])
    return nav_bal.set_index("time")["nav"]

# Load LAGGED setup
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

ev = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
LN2 = np.log(2); HL = 3.0
ev["pa_HL3"] = np.nan; ev["prior_n_good"] = 0
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

POST_MIN, N_MIN, NPR_MIN, ENTRY, HOLD, MAX_POS, POS_PCT = 5.0, 4, 0.15, 5, 25, 12, 0.08
e_lag = ev[(ev["NP_R"] >= NPR_MIN*100) & (ev["prior_n_good"] >= N_MIN) & (ev["pa_HL3"] >= POST_MIN)].copy()
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])
schedule = []
for _, row in e_lag.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY); exit_dt = offset_date(rdt, ENTRY + HOLD)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day_l = sched_lag.groupby("entry_dt"); exits_by_day_l = sched_lag.groupby("exit_dt")

def run_lagged(init_nav):
    sw, ew = pd.Timestamp("2014-01-02"), pd.Timestamp("2026-05-15")
    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = init_nav; positions = {}; nav_history = []
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    LIQ_CAP=0.20; MAX_FILL=5; LIQ_MIN=2e9
    daily_rate = (1+DEPOSIT)**(1/365.25) - 1
    for dt in sim_days:
        cash *= (1 + daily_rate)
        if dt in exits_by_day_l.groups:
            for _, ex_row in exits_by_day_l.get_group(dt).iterrows():
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
        if dt in entries_by_day_l.groups:
            mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm
            for _, en_row in entries_by_day_l.get_group(dt).iterrows():
                tk = en_row["ticker"]
                if tk in positions or len(positions) >= MAX_POS: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq_l.at[dt, tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
                target = POS_PCT * nav_now
                cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares, "entry_px":fpx}
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"time":dt, "nav":cash+mtm})
    return pd.DataFrame(nav_history).set_index("time")["nav"]

# Run all combinations at TOTAL NAV = 50B
TOTAL = 50e9
configs = [
    ("BAL50_LAG0",   50e9,   0,  "pure BAL no LAGGED"),
    ("BAL40_LAG10",  40e9,  10e9, "Opt2 light LAGGED parking"),
    ("BAL35_LAG15",  35e9,  15e9, "Opt2 moderate"),
    ("BAL30_LAG20",  30e9,  20e9, "Opt2 stronger LAGGED"),
    ("BAL25_LAG25",  25e9,  25e9, "Opt1 baseline (50/50)"),
    ("BAL20_LAG30",  20e9,  30e9, "LAGGED dominant"),
]

print("\n[Running] BAL @ various sizes ...")
bal_navs = {}
for nav in sorted(set(c[1] for c in configs if c[1] > 0)):
    print(f"  BAL@{nav/1e9:.0f}B ...", flush=True)
    bal_navs[nav] = run_bal(nav)

print("\n[Running] LAGGED @ various sizes ...")
lag_navs = {}
for nav in sorted(set(c[2] for c in configs if c[2] > 0)):
    print(f"  LAGGED@{nav/1e9:.0f}B ...", flush=True)
    lag_navs[nav] = run_lagged(nav)

print("\n[Combining] ...")
combined = {}
for name, bal_n, lag_n, _ in configs:
    bal_s = bal_navs[bal_n] if bal_n > 0 else pd.Series(0, index=master_idx)
    lag_s = lag_navs[lag_n] if lag_n > 0 else pd.Series(0, index=master_idx)
    common = bal_s.index.intersection(lag_s.index) if lag_n > 0 else bal_s.index
    total = (bal_s.loc[common] if bal_n > 0 else 0) + (lag_s.loc[common] if lag_n > 0 else 0)
    combined[name] = total / TOTAL

# Load Current production
ba_v11_prod = pd.read_csv("ba_v11_production_12y_nav.csv", index_col=0, parse_dates=True).iloc[:,0]

# Common index
common = ba_v11_prod.index
for k, v in combined.items():
    common = common.intersection(v.index)
ba_v11_prod = ba_v11_prod.loc[common]
combined = {k: v.loc[common] for k, v in combined.items()}

# VNI
vni_aligned = vni.set_index("time")["Close"].reindex(common).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

def m(nav, start, end):
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
    ("FULL 2014-26", common.min(), common.max()),
    ("OOS 2024-26",  OOS_START, common.max()),
    ("Y2022",        pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Y2025",        pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
]

print("\n" + "="*120)
print("  ARCHITECTURE COMPARISON: Current vs Opt1 (Opt2 approximations)")
print("="*120)
print(f"  {'Config':<18}{'Period':<16}{'CAGR%':>9}{'Sharpe':>9}{'DD%':>9}{'Calmar':>9}{'Wealth':>9}")
print("  " + "-"*90)
for label, st, en in periods:
    print(f"  --- {label} ---")
    cur_m = m(ba_v11_prod, st, en)
    print(f"  {'CURRENT (BA+VN30)':<18}{label[:14]:<16}{cur_m['CAGR']:>+8.2f}{cur_m['Sharpe']:>+9.2f}{cur_m['DD']:>+8.2f}{cur_m['Calmar']:>+9.2f}{cur_m['wealth']:>+9.2f}")
    for name, _, _, _ in configs:
        nav = combined[name]
        x = m(nav, st, en)
        if x is None: continue
        delta = x['CAGR'] - cur_m['CAGR']
        print(f"  {name:<18}{label[:14]:<16}{x['CAGR']:>+8.2f}{x['Sharpe']:>+9.2f}{x['DD']:>+8.2f}{x['Calmar']:>+9.2f}{x['wealth']:>+9.2f}  (Δ vs cur: {delta:+.2f}pp)")
    vm = m(vni_n, st, en)
    if vm:
        print(f"  {'VNI':<18}{label[:14]:<16}{vm['CAGR']:>+8.2f}{vm['Sharpe']:>+9.2f}{vm['DD']:>+8.2f}{vm['Calmar']:>+9.2f}{vm['wealth']:>+9.2f}")
    print()

# Save
out = pd.DataFrame({"CURRENT": ba_v11_prod, **combined})
out.to_csv("option2_approximation_navs.csv")
print("Saved: option2_approximation_navs.csv")
