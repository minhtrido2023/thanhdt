# -*- coding: utf-8 -*-
"""
paper_v11_v12_apr2026.py — Parallel paper-trade v11 vs v12 from 2026-04-01

Both at 50B NAV init, same period (2026-04-01 → today).

v11 "Song Sinh":
  - 25B BAL book (V11 SIGNAL_V11_UNIFIED + P3 overheat + V6 ETF)
  - 25B VN30 book (same signal restricted to top30)

v12 "Âm Dương":
  - 25B BAL book (same as v11)
  - 25B LAGGED HL_3y book (post-release drift T+5→T+30, post_min=5, max_pos=12, pos_pct=0.08)

Transparent pattern:
  - event_log + etf_log + force_close_eod=False
  - MTM phantoms for open positions
  - Daily NAV, transactions, open positions CSVs
  - Reconciliation report at end
"""
import os, sys, io, pickle, re
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY

# Extract SIGNAL_V11_UNIFIED from sim_v11_for_analyzer
with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
SIGNAL_V11_UNIFIED = _extract("SIGNAL_V11_UNIFIED")
VNI_QUERY_UNIFIED = _extract("VNI_QUERY_UNIFIED")

START_DATE = "2026-04-01"
END_DATE   = datetime.now().strftime("%Y-%m-%d")
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9   # per book

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
ETF_STATES = {3: 0.7}

print("="*100)
print(f"  PAPER-TRADE COMPARISON: v11 Song Sinh vs v12 Âm Dương")
print(f"  Period: {START_DATE} → {END_DATE}, NAV={TOTAL_NAV/1e9:.0f}B each")
print(f"  v11 = BAL+VN30+ETF | v12 = BAL+LAGGED+ETF")
print("="*100)

# ============================================================================
# 1) Load BA v11 signals + apply P3 overheat filter
# ============================================================================
print("\n[1/8] Loading BA v11 signals + P3 overheat ...")
sig_cache_full = "ba_v11_unified_12y_sig.pkl"
with open(sig_cache_full, "rb") as f: sig_all = pickle.load(f)
sig_all["time"] = pd.to_datetime(sig_all["time"])
# Filter to our window (with buffer for state lookup)
sig = sig_all[(sig_all["time"] >= pd.Timestamp(START_DATE)) & (sig_all["time"] <= pd.Timestamp(END_DATE))].copy()
print(f"  Filtered signals: {len(sig):,} rows in window")

# P3 overheat
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '2026-01-01' AND DATE '{END_DATE}'
ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
state5 = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '2026-01-01' AND DATE '{END_DATE}' ORDER BY s.time""")
state5["time"] = pd.to_datetime(state5["time"])
vni_full = vni_full.merge(state5, on="time", how="left")
vni_full["state"] = vni_full["state"].ffill()
vni_full["overheat"] = ((vni_full["Close"]/vni_full["MA200"] > 1.30) & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
mask = sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11)
sig.loc[mask, "play_type"] = "AVOID_overheated"
print(f"  Overheat blocked: {mask.sum()}")

# Common data
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
vni = bq(VNI_QUERY_UNIFIED.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
vn30_underlying = dict(zip(vni["time"], vni["Close"]))
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
state_by_date = dict(zip(state5["time"], state5["state"]))
state_ff = {}
last_s = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_s = s
    state_ff[d] = last_s

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
print(f"  Trading days: {len(vni_dates)} | Top30 size: {len(top30)}")

# ============================================================================
# 2) v11 BAL book (transparent)
# ============================================================================
print("\n[2/8] v11 BAL book sim (25B) ...")
events_v11_bal = []; etf_v11_bal = []
nav_v11_bal, trades_v11_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    deposit_annual=0.01, state_by_date=state_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
    etf_rebalance_friction=0.0015,
    event_log=events_v11_bal, etf_log=etf_v11_bal,
    force_close_eod=False,
    **LIQ_FULL, name="v11_BAL")
nav_v11_bal["time"] = pd.to_datetime(nav_v11_bal["time"])
print(f"  Events: {len(events_v11_bal)} | ETF rebalances: {len(etf_v11_bal)} | Closed trades: {len(trades_v11_bal)}")

# ============================================================================
# 3) v11 VN30 book (transparent)
# ============================================================================
print("\n[3/8] v11 VN30 book sim (25B) ...")
events_v11_v30 = []; etf_v11_v30 = []
sig_vn30 = sig[sig["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_v11_v30, trades_v11_v30 = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    deposit_annual=0.01, state_by_date=state_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
    etf_rebalance_friction=0.0015,
    event_log=events_v11_v30, etf_log=etf_v11_v30,
    force_close_eod=False,
    **LIQ_V30, name="v11_VN30")
nav_v11_v30["time"] = pd.to_datetime(nav_v11_v30["time"])
print(f"  Events: {len(events_v11_v30)} | ETF rebalances: {len(etf_v11_v30)} | Closed trades: {len(trades_v11_v30)}")

# ============================================================================
# 4) v12 BAL book — IDENTICAL to v11 BAL (re-use)
# ============================================================================
print("\n[4/8] v12 BAL book = v11 BAL (identical)")
nav_v12_bal = nav_v11_bal.copy()
trades_v12_bal = trades_v11_bal.copy()
events_v12_bal = events_v11_bal.copy()
etf_v12_bal = etf_v11_bal.copy()

# ============================================================================
# 5) v12 LAGGED HL_3y book — standalone sim (25B)
# ============================================================================
print("\n[5/8] v12 LAGGED HL_3y book sim (25B) ...")

with open("earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

# Pull fresh OV data including 2026-04 to today
print("  Pulling fresh OV (2026-01 → today) for current LAGGED ...")
ov_fresh = bq(f"""SELECT t.ticker, t.time, t.Open, t.Volume_3M_P50
FROM tav2_bq.ticker AS t WHERE t.time >= '2026-01-01' AND t.time <= '{END_DATE}' AND t.Close > 0""")
ov_fresh["time"] = pd.to_datetime(ov_fresh["time"])
# Merge with older cached
with open("lagged_pos_ov.pkl","rb") as f: ov_old = pickle.load(f)
ov_old["time"] = pd.to_datetime(ov_old["time"])
ov = pd.concat([ov_old, ov_fresh], ignore_index=True).drop_duplicates(["ticker","time"], keep="last")
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index()
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index()

# Extend master_idx to include recent dates
all_dates_combined = sorted(set(master_idx) | set(px_open.index) | set(liq_l.index))
master_idx = pd.DatetimeIndex(all_dates_combined).as_unit("ns")
px_close = px_close.reindex(master_idx).ffill(limit=5)
px_open = px_open.reindex(master_idx).ffill(limit=5)
liq_l = liq_l.reindex(master_idx).ffill(limit=5)
all_dates = np.array(master_idx)

# Reload + recompute earnings events with HL_3y profile (including new Q1 2026 releases)
ev_old = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
# Fetch new events
last_known = ev_old["Release_Date"].max()
print(f"  Fetching new earnings events > {last_known.date()} ...")
new_ev_raw = bq(f"""
SELECT f.ticker, f.quarter, f.Release_Date, f.NP_R, f.Revenue_YoY_P0
FROM tav2_bq.ticker_financial AS f
WHERE f.Release_Date > '{last_known.date()}' AND f.Release_Date <= '{END_DATE}'
  AND f.NP_R IS NOT NULL
""")
new_ev_raw["Release_Date"] = pd.to_datetime(new_ev_raw["Release_Date"])
print(f"    Fetched {len(new_ev_raw)} new events")

# Compute pre/release/post returns for new events
def get_off_close(tk, ref_dt, offset):
    if tk not in px_close.columns: return np.nan
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return np.nan
    tgt = pos + offset
    if tgt < 0 or tgt >= len(all_dates): return np.nan
    return px_close.iloc[tgt][tk]

new_ev_rows = []
for _, row in new_ev_raw.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    p_m30 = get_off_close(tk, rdt, -30); p_m1 = get_off_close(tk, rdt, -1)
    p_p5 = get_off_close(tk, rdt, +5);   p_p30 = get_off_close(tk, rdt, +30)
    pre_ret = (p_m1/p_m30 - 1)*100 if pd.notna(p_m30) and p_m30 > 0 and pd.notna(p_m1) else np.nan
    rel_ret = (p_p5/p_m1 - 1)*100 if pd.notna(p_p5) and p_p5 > 0 and pd.notna(p_m1) and p_m1 > 0 else np.nan
    post_ret = (p_p30/p_p5 - 1)*100 if pd.notna(p_p30) and pd.notna(p_p5) and p_p5 > 0 else np.nan
    new_ev_rows.append({
        "ticker":tk, "quarter":row["quarter"], "Release_Date":rdt,
        "NP_R": row["NP_R"]*100 if pd.notna(row["NP_R"]) else np.nan,
        "Rev_YoY": row["Revenue_YoY_P0"]*100 if pd.notna(row["Revenue_YoY_P0"]) else np.nan,
        "pre_ret":pre_ret, "rel_ret":rel_ret, "post_ret":post_ret,
    })
new_ev = pd.DataFrame(new_ev_rows)
ev_use_cols = ["ticker","quarter","Release_Date","NP_R","Rev_YoY","pre_ret","rel_ret","post_ret"]
all_ev = pd.concat([ev_old[ev_use_cols], new_ev[ev_use_cols]], ignore_index=True)
all_ev = all_ev.drop_duplicates(subset=["ticker","quarter"], keep="last")
all_ev = all_ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)

# HL_3y profile (no lookahead)
LN2 = np.log(2); HL = 3.0
all_ev["pa_HL3"] = np.nan; all_ev["prior_n_good"] = 0
for tk, g in all_ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = all_ev.loc[row_idx]
        cur_date = row["Release_Date"]
        n_good = len(good_history)
        all_ev.at[row_idx, "prior_n_good"] = n_good
        if n_good >= 1:
            dates_arr = pd.to_datetime([d for d,_ in good_history])
            posts_arr = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates_arr).days.values / 365.25
            w = np.exp(-LN2 * age_yrs / HL)
            all_ev.at[row_idx, "pa_HL3"] = (posts_arr * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))

POST_MIN, N_MIN, NPR_MIN, ENTRY, HOLD, MAX_POS, POS_PCT = 5.0, 4, 0.15, 5, 25, 12, 0.08
e_lag = all_ev[
    (all_ev["NP_R"] >= NPR_MIN*100) &
    (all_ev["prior_n_good"] >= N_MIN) &
    (all_ev["pa_HL3"] >= POST_MIN) &
    (all_ev["Release_Date"] >= pd.Timestamp(START_DATE))
].copy()
print(f"  Qualified LAGGED signals in window: {len(e_lag)}")

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
    if entry_dt is None: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt, "release_dt":rdt, "NP_R":row["NP_R"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt") if len(sched_lag)>0 else None
exits_by_day = sched_lag.groupby("exit_dt") if len(sched_lag)>0 else None

# Simulate LAGGED book
LAGGED_INIT = BOOK_NAV  # 25B
sw, ew = pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)
sim_days_l = [d for d in master_idx if sw <= d <= ew]
cash_l = LAGGED_INIT; positions_l = {}; nav_history_l = []; trades_l = []
events_v12_lag = []
SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
LIQ_CAP=0.20; MAX_FILL=5; LIQ_MIN=2e9
daily_rate = (1+0.01)**(1/365.25) - 1
for dt in sim_days_l:
    cash_l *= (1 + daily_rate)
    # Exits
    if exits_by_day is not None and dt in exits_by_day.groups:
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
            ret_pct = (fpx/pos["entry_px"]-1)*100
            trades_l.append({"dt":dt,"ticker":tk,"side":"SELL","px":fpx,
                            "shares":pos["shares"],"ret_pct":ret_pct,
                            "entry_dt":pos["entry_dt"],"entry_px":pos["entry_px"],
                            "hold_days":(dt-pos["entry_dt"]).days,
                            "release_dt":pos["release_dt"]})
            events_v12_lag.append({"ymd":dt.strftime("%Y-%m-%d"),"action":"sell","ticker":tk,
                                    "amount_vnd":pos["shares"]*fpx, "price":fpx,
                                    "book":"v12_LAGGED","reason":"TIME_EXIT"})
            del positions_l[tk]
    # Entries
    if entries_by_day is not None and dt in entries_by_day.groups:
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
            positions_l[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares,
                                "entry_px":fpx, "release_dt":en_row["release_dt"]}
            trades_l.append({"dt":dt,"ticker":tk,"side":"BUY","px":fpx,
                            "shares":shares,"ret_pct":0,
                            "entry_dt":dt,"entry_px":fpx,"hold_days":0,
                            "release_dt":en_row["release_dt"]})
            events_v12_lag.append({"ymd":dt.strftime("%Y-%m-%d"),"action":"buy","ticker":tk,
                                    "amount_vnd":cost,"price":fpx,
                                    "book":"v12_LAGGED","reason":"LAGGED_T5"})
    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions_l.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav_history_l.append({"time":dt,"nav":cash_l+mtm,"cash":cash_l,"positions_mv":mtm,"n_pos":len(positions_l)})

nav_v12_lag = pd.DataFrame(nav_history_l)
print(f"  LAGGED trades: {len(trades_l)} | open positions: {len(positions_l)} | final NAV: {nav_v12_lag['nav'].iloc[-1]/1e9:.2f}B")

# ============================================================================
# 6) Combine v11 (BAL+VN30) and v12 (BAL+LAGGED)
# ============================================================================
print("\n[6/8] Combining books ...")
nav_b = nav_v11_bal.set_index("time")["nav"]
nav_v30 = nav_v11_v30.set_index("time")["nav"]
nav_lag = nav_v12_lag.set_index("time")["nav"]

# v11 NAV
common_v11 = nav_b.index.intersection(nav_v30.index)
nav_v11 = nav_b.loc[common_v11] + nav_v30.loc[common_v11]
# v12 NAV
common_v12 = nav_b.index.intersection(nav_lag.index)
nav_v12 = nav_b.loc[common_v12] + nav_lag.loc[common_v12]
# VNI
vni_s = vni.set_index("time")["Close"]
common_all = common_v11.intersection(common_v12).intersection(vni_s.index)
nav_v11 = nav_v11.loc[common_all]
nav_v12 = nav_v12.loc[common_all]
vni_aligned = vni_s.loc[common_all]
vni_n = vni_aligned / vni_aligned.iloc[0]

# ============================================================================
# 7) Metrics + Report
# ============================================================================
print("\n[7/8] Computing metrics ...")
def metrics(nav, label):
    if isinstance(nav, pd.Series):
        s = nav
    else:
        s = nav.set_index("time")["nav"] if "time" in nav.columns else nav
    rets = s.pct_change().dropna()
    days = (s.index[-1] - s.index[0]).days
    pct = (s.iloc[-1] / s.iloc[0] - 1) * 100
    yrs = days / 365.25 if days > 0 else 1
    cagr_ann = ((s.iloc[-1] / s.iloc[0]) ** (1/yrs) - 1) * 100 if yrs > 0 else 0
    vol = rets.std() * np.sqrt(252) * 100 if len(rets) > 0 else 0
    dd = ((s - s.cummax()) / s.cummax()).min() * 100
    return {"label":label, "days":days, "pct_chg":pct, "cagr_ann":cagr_ann, "vol":vol, "dd":dd,
            "final_nav":s.iloc[-1], "start_nav":s.iloc[0]}

vni_metric = {"label":"VNI", "days":(common_all[-1]-common_all[0]).days,
              "pct_chg":(vni_aligned.iloc[-1]/vni_aligned.iloc[0]-1)*100,
              "cagr_ann":((vni_aligned.iloc[-1]/vni_aligned.iloc[0])**(1/((common_all[-1]-common_all[0]).days/365.25))-1)*100,
              "vol":vni_aligned.pct_change().dropna().std()*np.sqrt(252)*100,
              "dd":((vni_aligned-vni_aligned.cummax())/vni_aligned.cummax()).min()*100,
              "final_nav":vni_aligned.iloc[-1], "start_nav":vni_aligned.iloc[0]}

m_v11 = metrics(nav_v11, "v11 Song Sinh")
m_v12 = metrics(nav_v12, "v12 Âm Dương")

print("\n" + "="*100)
print(f"  PAPER-TRADE COMPARISON ({common_all[0].date()} → {common_all[-1].date()}, {(common_all[-1]-common_all[0]).days}d)")
print("="*100)
print(f"  {'System':<20}{'Days':>6}{'Total Return':>14}{'Annualized':>14}{'Vol':>10}{'MaxDD':>10}{'Final NAV':>14}")
print("  " + "-"*86)
for m in [m_v11, m_v12, vni_metric]:
    if m["label"] == "VNI":
        final_str = f"{m['final_nav']:.2f}"
    else:
        final_str = f"{m['final_nav']/1e9:.2f}B"
    print(f"  {m['label']:<20}{m['days']:>6d}{m['pct_chg']:>+13.2f}%{m['cagr_ann']:>+13.2f}%{m['vol']:>+9.2f}%{m['dd']:>+9.2f}%{final_str:>14}")

# Δ comparison
print(f"\n  Δ v12 vs v11: Total {m_v12['pct_chg'] - m_v11['pct_chg']:+.2f}pp  |  NAV: {(m_v12['final_nav'] - m_v11['final_nav'])/1e9:+.2f}B")
print(f"  Δ v11 vs VNI: Total {m_v11['pct_chg'] - vni_metric['pct_chg']:+.2f}pp")
print(f"  Δ v12 vs VNI: Total {m_v12['pct_chg'] - vni_metric['pct_chg']:+.2f}pp")

# Open positions at end
print(f"\n  v11 BAL open: {nav_v11_bal['n_pos'].iloc[-1] if 'n_pos' in nav_v11_bal.columns else 'n/a'}")
print(f"  v11 VN30 open: {nav_v11_v30['n_pos'].iloc[-1] if 'n_pos' in nav_v11_v30.columns else 'n/a'}")
print(f"  v12 BAL open: {nav_v11_bal['n_pos'].iloc[-1]}  (same as v11 BAL)")
print(f"  v12 LAGGED open: {len(positions_l)}")

# ============================================================================
# 8) Save outputs
# ============================================================================
print("\n[8/8] Saving outputs ...")
out_df = pd.DataFrame({
    "v11_NAV_B": nav_v11 / 1e9,
    "v12_NAV_B": nav_v12 / 1e9,
    "VNI_norm": vni_n,
})
out_df.to_csv("paper_v11_v12_apr2026_nav.csv")

# Combined trade log
trades_combined = []
for ev in events_v11_bal:
    if isinstance(ev, dict):
        trades_combined.append({**ev, "system":"v11", "book":"BAL"})
for ev in events_v11_v30:
    if isinstance(ev, dict):
        trades_combined.append({**ev, "system":"v11", "book":"VN30"})
for ev in events_v12_lag:
    trades_combined.append({**ev, "system":"v12"})
trades_df = pd.DataFrame(trades_combined)
if len(trades_df) > 0:
    trades_df.to_csv("paper_v11_v12_apr2026_trades.csv", index=False)

# LAGGED open positions
if len(positions_l) > 0:
    open_rows = []
    last_dt = common_all[-1]
    for tk, pos in positions_l.items():
        cur_px = px_close.at[last_dt, tk] if (tk in px_close.columns and last_dt in px_close.index) else pos["entry_px"]
        if pd.isna(cur_px): cur_px = pos["entry_px"]
        unrealized = (cur_px/pos["entry_px"] - 1) * 100
        open_rows.append({"ticker":tk, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"],
                          "cur_px":cur_px, "shares":pos["shares"],
                          "mtm_value":pos["shares"]*cur_px,
                          "unrealized_pct":unrealized,
                          "days_held":(last_dt-pos["entry_dt"]).days,
                          "release_dt":pos["release_dt"]})
    open_df = pd.DataFrame(open_rows)
    open_df.to_csv("paper_v12_lagged_open_positions.csv", index=False)
    print(f"\n  v12 LAGGED open positions ({len(open_df)}):")
    print(open_df.sort_values("days_held", ascending=False)[["ticker","entry_dt","entry_px","cur_px","unrealized_pct","days_held"]].to_string(index=False))

print(f"\nSaved:")
print(f"  paper_v11_v12_apr2026_nav.csv      ({len(out_df)} daily rows)")
print(f"  paper_v11_v12_apr2026_trades.csv   ({len(trades_combined)} events)")
print(f"  paper_v12_lagged_open_positions.csv  ({len(positions_l)} open)")
