# -*- coding: utf-8 -*-
"""
paper_v11_v12_v121_apr2026.py — 3-way parallel paper-trade v11/v12/v12.1 from 2026-04-01

All at 50B NAV init, same period (2026-04-01 → today).

v11 "Song Sinh":
  - 25B BAL + 25B VN30 + V6 ETF
v12 "Âm Dương":
  - 25B BAL + 25B LAGGED HL_3y (fixed 8%) + V6 ETF
v12.1 "Âm Dương Tinh Tế":
  - 25B BAL + 25B LAGGED HL_3y + S2 sizing (10% if surprise>0.5 else 8%) + V6 ETF
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

with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
SIGNAL_V11_UNIFIED = _extract("SIGNAL_V11_UNIFIED")
VNI_QUERY_UNIFIED = _extract("VNI_QUERY_UNIFIED")

START_DATE = "2026-04-01"
END_DATE   = datetime.now().strftime("%Y-%m-%d")
TOTAL_NAV  = 50e9
BOOK_NAV   = 25e9

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
ETF_STATES = {3: 0.7}

print("="*100)
print(f"  PAPER-TRADE 3-WAY: v11 Song Sinh / v12 Âm Dương / v12.1 Âm Dương Tinh Tế")
print(f"  Period: {START_DATE} → {END_DATE}, NAV={TOTAL_NAV/1e9:.0f}B each")
print("="*100)

# ============================================================================
# 1) Load BA v11 signals + P3 overheat
# ============================================================================
print("\n[1/9] Loading BA v11 signals + P3 overheat ...")
with open("data/ba_v11_unified_12y_sig.pkl", "rb") as f: sig_all = pickle.load(f)
sig_all["time"] = pd.to_datetime(sig_all["time"])
sig = sig_all[(sig_all["time"] >= pd.Timestamp(START_DATE)) & (sig_all["time"] <= pd.Timestamp(END_DATE))].copy()
print(f"  Signals: {len(sig):,} rows")

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
mask_oh = sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11)
sig.loc[mask_oh, "play_type"] = "AVOID_overheated"
print(f"  Overheat blocked: {mask_oh.sum()}")

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

# ============================================================================
# 2) v11 BAL book + 3) v11 VN30 book (shared between v11 and v12/v12.1 use BAL)
# ============================================================================
print("\n[2/9] v11/v12/v12.1 BAL book sim (25B) — shared ...")
events_bal = []; etf_bal = []
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    deposit_annual=0.01, state_by_date=state_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
    event_log=events_bal, etf_log=etf_bal, force_close_eod=False,
    **LIQ_FULL, name="BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
print(f"  BAL: {len(events_bal)} events, {len(etf_bal)} ETF reb, {len(trades_bal)} closed")

print("\n[3/9] v11 VN30 book sim (25B) ...")
events_vn30 = []; etf_vn30 = []
sig_vn30 = sig[sig["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    deposit_annual=0.01, state_by_date=state_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
    event_log=events_vn30, etf_log=etf_vn30, force_close_eod=False,
    **LIQ_VN30, name="VN30")
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
print(f"  VN30: {len(events_vn30)} events, {len(etf_vn30)} ETF reb, {len(trades_vn30)} closed")

# ============================================================================
# 4) LAGGED setup (shared between v12 and v12.1)
# ============================================================================
print("\n[4/9] LAGGED setup (shared HL_3y profile + surprise) ...")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx

print("  Pulling fresh OV (2026-01 → today) ...")
ov_fresh = bq(f"""SELECT t.ticker, t.time, t.Open, t.Volume_3M_P50
FROM tav2_bq.ticker AS t WHERE t.time >= '2026-01-01' AND t.time <= '{END_DATE}' AND t.Close > 0""")
ov_fresh["time"] = pd.to_datetime(ov_fresh["time"])
with open("data/lagged_pos_ov.pkl","rb") as f: ov_old = pickle.load(f)
ov_old["time"] = pd.to_datetime(ov_old["time"])
ov = pd.concat([ov_old, ov_fresh], ignore_index=True).drop_duplicates(["ticker","time"], keep="last")
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index()
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index()
all_dates_combined = sorted(set(master_idx) | set(px_open.index) | set(liq_l.index))
master_idx = pd.DatetimeIndex(all_dates_combined).as_unit("ns")
px_close = px_close.reindex(master_idx).ffill(limit=5)
px_open = px_open.reindex(master_idx).ffill(limit=5)
liq_l = liq_l.reindex(master_idx).ffill(limit=5)
all_dates = np.array(master_idx)

# Fetch new earnings events
ev_old = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
last_known = ev_old["Release_Date"].max()
print(f"  Fetching new earnings events > {last_known.date()} ...")
new_ev_raw = bq(f"""
SELECT f.ticker, f.quarter, f.Release_Date, f.NP_R, f.Revenue_YoY_P0,
       f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4
FROM tav2_bq.ticker_financial AS f
WHERE f.Release_Date > '{last_known.date()}' AND f.Release_Date <= '{END_DATE}'
  AND f.NP_R IS NOT NULL
""")
new_ev_raw["Release_Date"] = pd.to_datetime(new_ev_raw["Release_Date"])
print(f"    Fetched {len(new_ev_raw)} new events")

# Load surprise data (which has NP_P0..P7 for OLD events)
with open("data/earnings_surprise_data.pkl","rb") as f: fin_old = pickle.load(f)
fin_old["Release_Date"] = pd.to_datetime(fin_old["Release_Date"])

def get_off_close(tk, ref_dt, offset):
    if tk not in px_close.columns: return np.nan
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return np.nan
    tgt = pos + offset
    if tgt < 0 or tgt >= len(all_dates): return np.nan
    return px_close.iloc[tgt][tk]

# Compute pre/release/post + surprise for new events
new_ev_rows = []
for _, row in new_ev_raw.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    p_m30 = get_off_close(tk, rdt, -30); p_m1 = get_off_close(tk, rdt, -1)
    p_p5 = get_off_close(tk, rdt, +5);   p_p30 = get_off_close(tk, rdt, +30)
    pre_ret = (p_m1/p_m30 - 1)*100 if pd.notna(p_m30) and p_m30>0 and pd.notna(p_m1) else np.nan
    rel_ret = (p_p5/p_m1 - 1)*100 if pd.notna(p_p5) and p_p5>0 and pd.notna(p_m1) and p_m1>0 else np.nan
    post_ret = (p_p30/p_p5 - 1)*100 if pd.notna(p_p30) and pd.notna(p_p5) and p_p5>0 else np.nan
    # surprise B_MA
    p1,p2,p3,p4 = row.get("NP_P1"), row.get("NP_P2"), row.get("NP_P3"), row.get("NP_P4")
    p0 = row.get("NP_P0")
    if pd.notna(p0) and pd.notna(p1) and pd.notna(p2) and pd.notna(p3) and pd.notna(p4):
        exp_bma = (p1+p2+p3+p4)/4
        sur = (p0 - exp_bma) / max(abs(exp_bma), 1e9)
        sur = max(-5, min(5, sur))
    else:
        sur = np.nan
    new_ev_rows.append({
        "ticker":tk, "quarter":row["quarter"], "Release_Date":rdt,
        "NP_R": row["NP_R"]*100 if pd.notna(row["NP_R"]) else np.nan,
        "Rev_YoY": row["Revenue_YoY_P0"]*100 if pd.notna(row["Revenue_YoY_P0"]) else np.nan,
        "pre_ret":pre_ret, "rel_ret":rel_ret, "post_ret":post_ret,
        "surprise_B_MA":sur,
    })
new_ev = pd.DataFrame(new_ev_rows)

# Compute surprise for OLD events
fin_old["exp_B_MA"] = fin_old[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin_old["surprise_B_MA"] = ((fin_old["NP_P0"] - fin_old["exp_B_MA"]) / np.maximum(np.abs(fin_old["exp_B_MA"]), 1e9)).clip(-5, 5)
old_with_sur = ev_old.merge(fin_old[["ticker","quarter","Release_Date","surprise_B_MA"]],
                              on=["ticker","quarter","Release_Date"], how="left")
ev_use_cols = ["ticker","quarter","Release_Date","NP_R","Rev_YoY","pre_ret","rel_ret","post_ret","surprise_B_MA"]
all_ev = pd.concat([old_with_sur[ev_use_cols], new_ev[ev_use_cols]], ignore_index=True)
all_ev = all_ev.drop_duplicates(subset=["ticker","quarter"], keep="last")
all_ev = all_ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
all_ev["surprise_B_MA"] = all_ev["surprise_B_MA"].fillna(0)

# HL_3y profile
import math
LN2 = math.log(2); HL = 3.0
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

POST_MIN, N_MIN, NPR_MIN, ENTRY, HOLD, MAX_POS = 5.0, 4, 0.15, 5, 25, 12
e_lag = all_ev[
    (all_ev["NP_R"] >= NPR_MIN*100) &
    (all_ev["prior_n_good"] >= N_MIN) &
    (all_ev["pa_HL3"] >= POST_MIN) &
    (all_ev["Release_Date"] >= pd.Timestamp(START_DATE))
].copy()
print(f"  Qualified LAGGED signals: {len(e_lag)} | with surprise>0.5: {(e_lag['surprise_B_MA']>0.5).sum()}")

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
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt, "release_dt":rdt,
                     "NP_R":row["NP_R"], "surprise_B_MA":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt") if len(sched_lag)>0 else None
exits_by_day = sched_lag.groupby("exit_dt") if len(sched_lag)>0 else None

# ============================================================================
# 5) Run LAGGED sim with TWO sizing modes
# ============================================================================
LAGGED_INIT = BOOK_NAV
sw, ew = pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)
sim_days_l = [d for d in master_idx if sw <= d <= ew]
SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
LIQ_CAP=0.20; MAX_FILL=5; LIQ_MIN=2e9
daily_rate = (1+0.01)**(1/365.25) - 1

def run_lagged(s2_sizing):
    cash_l = LAGGED_INIT; positions_l = {}; nav_history_l = []; trades_l = []
    for dt in sim_days_l:
        cash_l *= (1 + daily_rate)
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
                del positions_l[tk]
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
                if s2_sizing:
                    pos_pct = 0.10 if en_row["surprise_B_MA"] > 0.5 else 0.08
                else:
                    pos_pct = 0.08
                target = pos_pct * nav_now
                cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash_l: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash_l -= cost
                positions_l[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares,
                                    "entry_px":fpx, "release_dt":en_row["release_dt"]}
                trades_l.append({"dt":dt,"ticker":tk,"side":"BUY","px":fpx,
                                "shares":shares,"ret_pct":0,"entry_dt":dt,"entry_px":fpx,
                                "hold_days":0,"release_dt":en_row["release_dt"],
                                "size_used": pos_pct})
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions_l.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history_l.append({"time":dt,"nav":cash_l+mtm,"cash":cash_l,"positions_mv":mtm,"n_pos":len(positions_l)})
    return pd.DataFrame(nav_history_l), trades_l, positions_l

print("\n[5/9] LAGGED v12 (fixed 8%) ...")
nav_v12lag, trades_v12lag, pos_v12 = run_lagged(s2_sizing=False)
print(f"  trades: {len(trades_v12lag)} | open: {len(pos_v12)} | final NAV: {nav_v12lag['nav'].iloc[-1]/1e9:.2f}B")

print("\n[6/9] LAGGED v12.1 (S2 sizing) ...")
nav_v121lag, trades_v121lag, pos_v121 = run_lagged(s2_sizing=True)
print(f"  trades: {len(trades_v121lag)} | open: {len(pos_v121)} | final NAV: {nav_v121lag['nav'].iloc[-1]/1e9:.2f}B")
n_high = sum(1 for t in trades_v121lag if t["side"]=="BUY" and t.get("size_used", 0.08) > 0.08)
n_low = sum(1 for t in trades_v121lag if t["side"]=="BUY" and t.get("size_used", 0.08) == 0.08)
print(f"  v12.1 sizing breakdown — 10% sizing: {n_high} | 8% sizing: {n_low}")

# ============================================================================
# 7) Combine + 8) Metrics
# ============================================================================
print("\n[7/9] Combining all 3 systems ...")
nav_b = nav_bal.set_index("time")["nav"]
nav_v30 = nav_vn30.set_index("time")["nav"]
nav_v12 = nav_v12lag.set_index("time")["nav"]
nav_v121 = nav_v121lag.set_index("time")["nav"]

common = nav_b.index.intersection(nav_v30.index).intersection(nav_v12.index).intersection(nav_v121.index)
nav_v11_total = nav_b.loc[common] + nav_v30.loc[common]
nav_v12_total = nav_b.loc[common] + nav_v12.loc[common]
nav_v121_total = nav_b.loc[common] + nav_v121.loc[common]
vni_s = vni.set_index("time")["Close"]
common_all = common.intersection(vni_s.index)
nav_v11_total = nav_v11_total.loc[common_all]
nav_v12_total = nav_v12_total.loc[common_all]
nav_v121_total = nav_v121_total.loc[common_all]
vni_aligned = vni_s.loc[common_all]
vni_n = vni_aligned / vni_aligned.iloc[0]

print("\n[8/9] Computing metrics ...")
def metrics(nav, label):
    s = nav if isinstance(nav, pd.Series) else nav.set_index("time")["nav"]
    rets = s.pct_change().dropna()
    days = (s.index[-1] - s.index[0]).days
    pct = (s.iloc[-1] / s.iloc[0] - 1) * 100
    yrs = max(days/365.25, 0.01)
    cagr = ((s.iloc[-1]/s.iloc[0])**(1/yrs) - 1) * 100
    vol = rets.std()*np.sqrt(252)*100 if len(rets)>0 else 0
    dd = ((s - s.cummax())/s.cummax()).min() * 100
    return {"label":label, "days":days, "pct":pct, "cagr_ann":cagr, "vol":vol, "dd":dd,
            "final":s.iloc[-1]}

vm = {"label":"VNI", "days":(common_all[-1]-common_all[0]).days,
      "pct":(vni_aligned.iloc[-1]/vni_aligned.iloc[0]-1)*100,
      "cagr_ann":((vni_aligned.iloc[-1]/vni_aligned.iloc[0])**(1/((common_all[-1]-common_all[0]).days/365.25))-1)*100,
      "vol":vni_aligned.pct_change().dropna().std()*np.sqrt(252)*100,
      "dd":((vni_aligned-vni_aligned.cummax())/vni_aligned.cummax()).min()*100,
      "final":vni_aligned.iloc[-1]}

m11 = metrics(nav_v11_total, "v11 Song Sinh")
m12 = metrics(nav_v12_total, "v12 Âm Dương")
m121 = metrics(nav_v121_total, "v12.1 Tinh Tế")

print("\n" + "="*100)
print(f"  3-WAY PAPER-TRADE COMPARISON ({common_all[0].date()} → {common_all[-1].date()}, {(common_all[-1]-common_all[0]).days}d)")
print("="*100)
print(f"  {'System':<22}{'Days':>6}{'Total Return':>14}{'Annualized':>14}{'Vol':>10}{'MaxDD':>10}{'Final NAV':>14}")
print("  " + "-"*88)
for m in [m11, m12, m121, vm]:
    final_str = f"{m['final']/1e9:.2f}B" if m["label"] != "VNI" else f"{m['final']:.2f}"
    print(f"  {m['label']:<22}{m['days']:>6d}{m['pct']:>+13.2f}%{m['cagr_ann']:>+13.2f}%{m['vol']:>+9.2f}%{m['dd']:>+9.2f}%{final_str:>14}")

print(f"\n  Δ v12 vs v11:      {m12['pct'] - m11['pct']:+.2f}pp  | NAV diff: {(m12['final']-m11['final'])/1e9:+.2f}B")
print(f"  Δ v12.1 vs v12:    {m121['pct'] - m12['pct']:+.2f}pp  | NAV diff: {(m121['final']-m12['final'])/1e9:+.2f}B")
print(f"  Δ v12.1 vs v11:    {m121['pct'] - m11['pct']:+.2f}pp  | NAV diff: {(m121['final']-m11['final'])/1e9:+.2f}B")
print(f"  Δ v12 vs VNI:      {m12['pct'] - vm['pct']:+.2f}pp")
print(f"  Δ v12.1 vs VNI:    {m121['pct'] - vm['pct']:+.2f}pp")

# Open positions
print(f"\n  v11 BAL open: {nav_bal['n_pos'].iloc[-1] if 'n_pos' in nav_bal.columns else 'n/a'}")
print(f"  v11 VN30 open: {nav_vn30['n_pos'].iloc[-1] if 'n_pos' in nav_vn30.columns else 'n/a'}")
print(f"  v12 LAGGED open: {len(pos_v12)}")
print(f"  v12.1 LAGGED open: {len(pos_v121)}")

# ============================================================================
# 9) Save
# ============================================================================
print("\n[9/9] Saving outputs ...")
out_df = pd.DataFrame({
    "v11_NAV_B": nav_v11_total / 1e9,
    "v12_NAV_B": nav_v12_total / 1e9,
    "v121_NAV_B": nav_v121_total / 1e9,
    "VNI_norm": vni_n,
})
out_df.to_csv("data/paper_v11_v12_v121_apr2026_nav.csv")
pd.DataFrame(trades_v12lag).to_csv("data/paper_v12_lagged_trades.csv", index=False)
pd.DataFrame(trades_v121lag).to_csv("data/paper_v121_lagged_trades.csv", index=False)

# v12.1 open positions
if len(pos_v121) > 0:
    rows = []
    last_dt = common_all[-1]
    for tk, pos in pos_v121.items():
        cur_px = px_close.at[last_dt, tk] if (tk in px_close.columns and last_dt in px_close.index) else pos["entry_px"]
        if pd.isna(cur_px): cur_px = pos["entry_px"]
        rows.append({"ticker":tk, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"],
                     "cur_px":cur_px, "shares":pos["shares"],
                     "unrealized_pct":(cur_px/pos["entry_px"]-1)*100,
                     "days_held":(last_dt-pos["entry_dt"]).days})
    open_df = pd.DataFrame(rows)
    open_df.to_csv("data/paper_v121_lagged_open_positions.csv", index=False)
    print(f"\n  v12.1 LAGGED open positions ({len(open_df)}):")
    print(open_df.sort_values("days_held", ascending=False)[["ticker","entry_dt","entry_px","cur_px","unrealized_pct","days_held"]].to_string(index=False))

print(f"\n  Saved: paper_v11_v12_v121_apr2026_nav.csv (3-way NAV)")
print(f"         paper_v12_lagged_trades.csv, paper_v121_lagged_trades.csv")
print(f"         paper_v121_lagged_open_positions.csv")
