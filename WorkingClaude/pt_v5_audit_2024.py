# -*- coding: utf-8 -*-
"""V12.1 Âm Dương Tinh Tế + M1+M3r AND-HOLD Ensemble + Tam Quan v3.4b — paper-trade sim.

Architecture (per backtest 2026-05-22 winner — test_rolling_m3_v121_ensemble.py):
  - 25B BAL leg: BA v11 stack (SV_TIGHT + P3 + RE_BACKLOG + V6 ETF parking) — always on
  - 25B SWITCHED leg: routes between VN30 (BA v11 on top-30) and LAGGED HL_3y (V12.1 S2 sizing)
    based on M1+M3r AND-HOLD ensemble signal:
      M1 = VNI − Equal-Weight 6M-return (high → concentrated → V11/VN30)
      M3r = Top10 (rolling 1Y ADV) − all-prune 6M-return (no lookahead)
      Binary rule: each metric > its expanding-median (252d warmup) ⇒ 1 (V11) else 0 (V12).
      AND-HOLD: both agree ⇒ adopt; disagree ⇒ keep current state.
    Switch cost: 0.5% on the 25B leg per round-trip flip.

5-state source: `tav2_bq.vnindex_5state_tam_quan_v34b_clean`

Outputs (analyze_portfolio.py compatible):
  data/pt_v5_2024_logs.csv          - daily NAV + cash + n_pos + n_tx + active_leg + signal
  data/pt_v5_2024_transactions.csv  - every buy/sell + ETF rebalance + MTM phantoms + SWITCH events
  data/pt_v5_2024_open_positions.csv - unrealized P&L snapshot at end (active leg only)
  data/pt_v5_2024_report.md         - reconciliation block (analyze_portfolio.py appends)
"""
import os, sys, io, pickle, bisect
from datetime import datetime
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v11_sql import SIGNAL_V11
from pt_dates import START_DATE, detect_end_date
START_DATE = "2024-01-01"   # V5 audit: full 2024 -> now

END_DATE = detect_end_date()
TOTAL_NAV   = 50e9
BAL_NAV     = 25e9
SECOND_NAV  = 25e9
SWITCH_COST = 0.005     # 0.5% round-trip per ensemble flip
POSITION_VND = 1.25e9
FILL_CAP = 0.20
T1_TOP_ADV = 50e9

INTRADAY_PKL = os.path.join(WORKDIR, "data/intraday_full.pkl")

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO",
                  "RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
MAX_POS_V11 = 12
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}

print("="*100)
print(f"  V12.1 ÂD-TT + ENSEMBLE (M1+M3r AND-HOLD) + TQ v3.4b — TRANSPARENT SIM")
print(f"  period={START_DATE} -> {END_DATE}   NAV={TOTAL_NAV/1e9:.0f}B   switch_cost={SWITCH_COST*100:.2f}%/flip")
print(f"  Architecture: 25B BAL + 25B SWITCHED leg (VN30 ⇄ LAGGED V12.1)")
print("="*100)

# ============================================================================
# 1. Intraday cache for v4 HYBRID BUY fill
# ============================================================================
print("\n[1] Building v4 HYBRID alt-fill prices...")
with open(INTRADAY_PKL,"rb") as f: intraday = pickle.load(f)
adv_by_ticker = {}
slot_price_atc, slot_vol_atc, slot_price_t1115, slot_vol_t1115 = {},{},{},{}
for tk, bars in intraday.items():
    if bars is None or bars.empty: continue
    b = bars.copy()
    b["time"] = pd.to_datetime(b["time"]); b["date_ts"] = b["time"].dt.normalize()
    b["hm"] = b["time"].dt.strftime("%H:%M"); b["close_vnd"] = b["close"].astype(float)*1000.0
    b["vnd_traded"] = b["close_vnd"]*b["volume"].astype(float)
    sess = b.groupby("date_ts", sort=False)["vnd_traded"].sum()
    adv_by_ticker[tk] = float(sess.mean())
    for label, hm, pd_, vd_ in [("atc","14:45",slot_price_atc,slot_vol_atc),
                                  ("t1115","11:15",slot_price_t1115,slot_vol_t1115)]:
        sub = b[b["hm"]==hm]
        for _, row in sub.iterrows():
            d_ts = row["date_ts"]
            pd_.setdefault(tk,{})[d_ts] = float(row["close_vnd"])
            vd_.setdefault(tk,{})[d_ts] = float(row["vnd_traded"])
alt_hybrid = {}
for tk in set(slot_price_atc.keys()) | set(slot_price_t1115.keys()):
    adv = adv_by_ticker.get(tk,0)
    is_top = adv >= T1_TOP_ADV
    src_p = slot_price_atc.get(tk,{}) if is_top else slot_price_t1115.get(tk,{})
    src_v = slot_vol_atc.get(tk,{}) if is_top else slot_vol_t1115.get(tk,{})
    for d_ts, p in src_p.items():
        v = src_v.get(d_ts)
        if v is not None and v*FILL_CAP >= POSITION_VND:
            alt_hybrid.setdefault(tk,{})[d_ts] = p

# ============================================================================
# 2. Load BA v11 signals + filters
# ============================================================================
print("\n[2] Loading v11 signals + Release_Date + 5-state + overheat + D1 override...")
sig = bq(SIGNAL_V11.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  signals: {len(sig):,} rows")

rel = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
rel["Release_Date"] = pd.to_datetime(rel["Release_Date"])
rel_by_tk = rel.sort_values(["ticker","Release_Date"]).groupby("ticker")["Release_Date"].apply(list).to_dict()
ds_arr = np.empty(len(sig))
for i,(tk,t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
    arr = rel_by_tk.get(tk)
    if not arr: ds_arr[i]=np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    ds_arr[i] = np.nan if idx==0 else (pd.Timestamp(t)-arr[idx-1]).days
sig["days_since_release"] = ds_arr

state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["ratio"] = vni_full["Close"]/vni_full["MA200"]
vni_full["state"] = vni_full["time"].map(state_by_date)
vni_full["overheat"] = (vni_full["ratio"]>1.30) & ((vni_full["state"]==5)|(vni_full["D_RSI"]>0.75))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])

sig["state"] = sig["time"].map(state_by_date)

# D1 RE_BACKLOG_BUY override
d1 = bq(f"""
WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f
),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
)
SELECT t.ticker, t.time, fa.fa_tier,
  SAFE_DIVIDE(t.NP_P0, t.NP_P4)-1 AS np_yoy,
  fin.Revenue_YoY_P0 AS rev_yoy, adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time = t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_q = d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
sig = sig.merge(d1_q, on=["ticker","time"], how="left")
omask = sig["_d1_ok"].fillna(False) & (sig["ta"]>=120)
sig.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig = sig.drop(columns=["_d1_ok"])

def sv_tight_keep(row):
    s = row["state"]; days = row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb = sig["play_type"].isin(BUY_TIERS_V11)
mk = (~mb) | sig.apply(sv_tight_keep, axis=1)
sig_f = sig[mk].copy()
mp3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
sig_f.loc[mp3,"play_type"] = "AVOID_overheated"
print(f"  D1 reclassified: {int(omask.sum())}; SV_TIGHT filtered: {int((mb & ~sig.apply(sv_tight_keep,axis=1)).sum())}; P3 blocked: {int(mp3.sum())}")

# ============================================================================
# 3. Common data (prices, opens, sec_map, ETF prices, state ff, top30)
# ============================================================================
print("\n[3] Loading prices/Open/sector/E1VFVN30/top30...")
opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk,g in opens_df.groupby("ticker")}
prices = {tk: dict(zip(g["time"], g["Close"])) for tk,g in sig_f.groupby("ticker")}
liq_map = {(r["ticker"],r["time"]): r["liq"] for _,r in sig_f.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

etf_real = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
etf_real["time"] = pd.to_datetime(etf_real["time"])
vn30_underlying = dict(zip(etf_real["time"], etf_real["Close"]))

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

state_ff = {}; last_s=None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_s = s
    state_ff[d] = last_s

LIQ_FULL = {"liquidity_volume_pct":0.20,"max_fill_days":5,
            "liquidity_lookup":liq_map,"exit_slippage_tiered":True}

# ============================================================================
# 4. Compute ensemble signal (M1 + M3r AND-HOLD)
#    Pulls history back to 2013 for expanding-median baseline (no lookahead).
# ============================================================================
print("\n[4] Computing M1 (VNI−EW 6M) and M3r (rolling Top10 − all 6M) signals...")
hist_start = "2013-01-01"
m1_raw = bq(f"""WITH base AS (
  SELECT t.time, t.ticker,
    SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret_6m
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '{hist_start}' AND DATE '{END_DATE}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
),
vni AS (
  SELECT t.time, SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (ORDER BY t.time)) - 1 AS vni_ret_6m
  FROM tav2_bq.ticker AS t
  WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{hist_start}' AND DATE '{END_DATE}'
)
SELECT b.time, vni.vni_ret_6m - AVG(b.ret_6m) AS M1
FROM base b JOIN vni USING (time)
GROUP BY b.time, vni.vni_ret_6m ORDER BY b.time""")
m1_raw["time"] = pd.to_datetime(m1_raw["time"])
m1_series = m1_raw.set_index("time")["M1"]

m3r_raw = bq(f"""WITH base AS (
  SELECT t.time, t.ticker,
    SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret_6m,
    AVG(t.Volume_3M_P50 * t.Close) OVER (
      PARTITION BY t.ticker ORDER BY t.time
      ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING
    ) AS adv_1y
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '{hist_start}' AND DATE '{END_DATE}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
),
ranked AS (
  SELECT time, ret_6m, adv_1y,
    ROW_NUMBER() OVER (PARTITION BY time ORDER BY adv_1y DESC) AS rnk
  FROM base WHERE adv_1y IS NOT NULL AND ret_6m IS NOT NULL
)
SELECT time, AVG(IF(rnk<=10, ret_6m, NULL)) - AVG(ret_6m) AS M3r
FROM ranked GROUP BY time ORDER BY time""")
m3r_raw["time"] = pd.to_datetime(m3r_raw["time"])
m3r_series = m3r_raw.set_index("time")["M3r"]

def make_signal(metric, min_history=252):
    s = metric.dropna().sort_index()
    expanding_med = s.expanding(min_periods=min_history).median()
    raw = (s > expanding_med).astype(int)
    raw = raw.reindex(metric.index).ffill().fillna(1).astype(int)
    return raw.shift(1).fillna(1).astype(int)
sig_m1 = make_signal(m1_series); sig_m3r = make_signal(m3r_series)

def ensemble_AND_hold(s1, s3):
    out = np.zeros(len(s1), dtype=int); cur = int(s1.iloc[0])
    for i, (a, b) in enumerate(zip(s1.values, s3.values)):
        if a == b: cur = int(a)
        out[i] = cur
    return pd.Series(out, index=s1.index)

# Align on intersection of all signal dates AND the trading dates within paper window
common_sig_idx = sig_m1.index.intersection(sig_m3r.index)
m1_aligned = sig_m1.loc[common_sig_idx]; m3r_aligned = sig_m3r.loc[common_sig_idx]
ens_full = ensemble_AND_hold(m1_aligned, m3r_aligned)
# Reindex onto VNI trading dates within paper window, forward-fill from history
ens_signal = ens_full.reindex(pd.DatetimeIndex(vni_dates), method="ffill").fillna(1).astype(int)
print(f"  Signal coverage: {len(ens_signal)} days   V11-active: {(ens_signal==1).sum()}d   V12-active: {(ens_signal==0).sum()}d")
print(f"  Signal flips in window: {int((ens_signal.diff().abs()>0).sum())}")

# ============================================================================
# 5. Run BAL book @ 25B (transparent — always on)
# ============================================================================
print("\n[5] Running BAL book @ 25B...")
events_bal = []; etf_bal = []
nav_bal, trades_bal = simulate(sig_f, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.0, init_nav=BAL_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
    tier_weights=TIER_WEIGHTS_V11,
    deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_ff,  # deposit=0% / borrow=10% (user 2026-05-23)
    cash_etf_states={3:1.0}, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
    etf_rebalance_friction=0.0015,
    open_prices=open_prices, t1_open_exec=True,
    entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
    event_log=events_bal, etf_log=etf_bal,
    force_close_eod=False,
    **LIQ_FULL, name="pt_v5_2024_BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
print(f"  BAL events: {len(events_bal)} stock + {len(etf_bal)} ETF; final: {nav_bal.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

# ============================================================================
# 6. Run VN30 book @ 25B (transparent — for V11 mode of switched leg)
# ============================================================================
print("\n[6] Running VN30 book @ 25B...")
events_v30 = []; etf_v30 = []
sig_vn30 = sig_f[sig_f["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k,v in liq_map.items() if k[0] in top30}
LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_v30, trades_v30 = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=MAX_POS_V11, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.0, init_nav=SECOND_NAV,
    ticker_sector_map=sec_map,
    tier_weights=TIER_WEIGHTS_V11,
    deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_ff,  # deposit=0% / borrow=10% (user 2026-05-23)
    cash_etf_states={3:1.0}, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
    etf_rebalance_friction=0.0015,
    open_prices=open_prices, t1_open_exec=True,
    entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid",
    event_log=events_v30, etf_log=etf_v30,
    force_close_eod=False,
    **LIQ_V30, name="pt_v5_2024_VN30")
nav_v30["time"] = pd.to_datetime(nav_v30["time"])
print(f"  VN30 events: {len(events_v30)} stock + {len(etf_v30)} ETF; final: {nav_v30.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

# ============================================================================
# 7. Run LAGGED V12.1 book @ 25B (S2 sizing — for V12 mode of switched leg)
# ============================================================================
print("\n[7] Running LAGGED V12.1 book @ 25B (S2 sizing)...")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

# Build surprise_B_MA from full earnings_surprise_data (needed for S2 sizing).
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
            w = np.exp(-LN2*age_yrs/HL)
            ev.at[row_idx,"pa_HL3"] = (posts_arr*w).sum()/w.sum() if w.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))
POST_MIN, N_MIN, NPR_MIN, ENTRY, HOLD, MAX_POS_L, LIQ_MIN = 5.0, 4, 0.15, 5, 25, 12, 2e9
e = ev[(ev["NP_R"]>=NPR_MIN*100) & (ev["prior_n_good"]>=N_MIN) & (ev["pa_HL3"]>=POST_MIN)].copy()

sw = pd.Timestamp(START_DATE); ew = pd.Timestamp(END_DATE)
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right")-1
    if pos<0: return None
    tgt = pos+offset
    if tgt>=len(all_dates) or tgt<0: return None
    return pd.Timestamp(all_dates[tgt])
schedule = []
for _, row in e.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY); exit_dt = offset_date(rdt, ENTRY+HOLD)
    if entry_dt is None or exit_dt is None: continue
    if entry_dt < sw or entry_dt > ew: continue
    schedule.append({"ticker":tk,"entry_dt":entry_dt,"exit_dt":exit_dt,"release_dt":rdt,
                     "surprise":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
print(f"  LAGGED V12.1 signals in window: {len(sched_lag)}")
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")

sim_days_lag = [d for d in master_idx if sw <= d <= ew]
cash_l = SECOND_NAV; positions_l = {}; nav_history_l = []; events_lag = []
SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
LIQ_CAP_L=0.20; MAX_FILL_L=5; hid_seq = 0
for dt in sim_days_lag:
    # EXITS
    if dt in exits_by_day.groups:
        for _, ex_row in exits_by_day.get_group(dt).iterrows():
            tk = ex_row["ticker"]
            if tk not in positions_l: continue
            pos = positions_l[tk]
            if pos["exit_dt"] != dt: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx<=0:
                fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                if pd.isna(fpx) or fpx<=0: continue
            gross = pos["shares"]*fpx
            slip = gross*SLIP_OUT
            tax = (gross-slip)*TAX
            fee_total = slip + tax
            proceeds = gross - fee_total
            cash_l += proceeds
            events_lag.append({"ymd":dt,"ticker":tk,"action":"sell","buy_amount":0.0,
                "sell_amount":float(gross),"fee":float(fee_total),"adj_price":float(fpx),
                "shares":float(pos["shares"]),"holding_id":pos["holding_id"],
                "play_type":"LAGGED_HL3_S2","cash_after":float(cash_l),
                "reason":"LAGGED_EXIT_T30","book":"LAGGED"})
            del positions_l[tk]
    # ENTRIES — with S2 sizing
    if dt in entries_by_day.groups:
        mtm = sum(p["shares"]*(px_close.at[dt,tk] if tk in px_close.columns and pd.notna(px_close.at[dt,tk]) else p["entry_px"]) for tk,p in positions_l.items())
        nav_now = cash_l + mtm
        for _, en_row in entries_by_day.get_group(dt).iterrows():
            tk = en_row["ticker"]
            if tk in positions_l or len(positions_l)>=MAX_POS_L: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx<=0: continue
            adv = liq_l.at[dt, tk] if tk in liq_l.columns else 0
            if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
            pos_pct = 0.10 if en_row["surprise"] > 0.5 else 0.08    # S2 sizing
            target = pos_pct * nav_now; cap = LIQ_CAP_L * adv * MAX_FILL_L * fpx
            alloc = min(target, cap)
            if alloc<1e6 or alloc>cash_l: continue
            eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px
            share_cost = shares*fpx; slip_cost = shares*fpx*SLIP_IN
            cash_l -= (share_cost + slip_cost)
            hid_seq += 1
            hid = f"{tk}_{dt.strftime('%Y%m%d')}_LAG{hid_seq:03d}"
            positions_l[tk] = {"entry_dt":dt,"exit_dt":en_row["exit_dt"],
                               "shares":shares,"entry_px":fpx,"holding_id":hid,
                               "surprise":en_row["surprise"]}
            events_lag.append({"ymd":dt,"ticker":tk,"action":"buy","buy_amount":float(share_cost),
                "sell_amount":0.0,"fee":float(slip_cost),"adj_price":float(fpx),
                "shares":float(shares),"holding_id":hid,
                "play_type":"LAGGED_HL3_S2","cash_after":float(cash_l),
                "reason":f"LAGGED_ENTRY_T5_pos{int(pos_pct*100)}","book":"LAGGED"})
    # EOD NAV
    mtm = 0.0
    for tk, p in positions_l.items():
        px = px_close.at[dt, tk] if tk in px_close.columns else np.nan
        if pd.isna(px): px = p["entry_px"]
        mtm += p["shares"]*px
    nav_history_l.append({"time":dt, "cash":cash_l, "positions_mv":mtm, "nav":cash_l+mtm, "n_pos":len(positions_l)})
nav_lag = pd.DataFrame(nav_history_l)
nav_lag["time"] = pd.to_datetime(nav_lag["time"])
print(f"  LAGGED V12.1 events: {len(events_lag)}   final: {nav_lag['nav'].iloc[-1]/1e9:.4f}B")

# ============================================================================
# 8. Build SWITCHED NAV — daily route the SECOND leg per ensemble signal
#    + emit virtual SWITCH events on flip days
# ============================================================================
print("\n[8] Building switched NAV...")
nav_bal_s  = nav_bal.set_index("time")["nav"]
nav_v30_s  = nav_v30.set_index("time")["nav"]
nav_lag_s  = nav_lag.set_index("time")["nav"]
common = nav_bal_s.index.intersection(nav_v30_s.index).intersection(nav_lag_s.index)
bal_r  = nav_bal_s.loc[common].pct_change().fillna(0)
v30_r  = nav_v30_s.loc[common].pct_change().fillna(0)
lag_r  = nav_lag_s.loc[common].pct_change().fillna(0)
sig_loc = ens_signal.reindex(common).ffill().fillna(1).astype(int)

# 2nd-leg capital path with switching cost on flip
second_path = np.full(len(common), SECOND_NAV, dtype=float)
flip_dates = []
prev = int(sig_loc.iloc[0])
for i in range(1, len(common)):
    cur = int(sig_loc.iloc[i])
    if cur != prev:
        second_path[i] = second_path[i-1] * (1 - SWITCH_COST)
        flip_dates.append((common[i], prev, cur, second_path[i-1] - second_path[i]))
    else:
        second_path[i] = second_path[i-1]
    r = v30_r.iloc[i] if cur==1 else lag_r.iloc[i]
    second_path[i] = second_path[i] * (1 + r)
    prev = cur
second_series = pd.Series(second_path, index=common)

# BAL path (no compounding error — use sim NAV directly)
combined_nav = nav_bal_s.loc[common] + second_series

# ============================================================================
# 9. Build transparent transactions log
#    - BAL events always counted
#    - VN30 events counted only on days signal==1
#    - LAGGED events counted only on days signal==0
#    - SWITCH events emitted on flip days (book="SWITCH")
# ============================================================================
print("\n[9] Merging transparent logs...")
def annot(events, book):
    if not events: return pd.DataFrame()
    df = pd.DataFrame(events); df["book"] = book
    return df

ev_bal_df = annot(events_bal, "BAL")
ev_v30_df = annot(events_v30, "VN30")
ev_lag_df = annot(events_lag, "LAGGED")
for d in (ev_bal_df, ev_v30_df, ev_lag_df):
    if not d.empty: d["ymd"] = pd.to_datetime(d["ymd"])

# Filter VN30 events to days signal==1, LAGGED events to days signal==0
def sig_at(ts):
    if ts in sig_loc.index: return int(sig_loc.loc[ts])
    # forward-fill if needed
    valid = sig_loc[sig_loc.index <= ts]
    return int(valid.iloc[-1]) if len(valid) else 1

if not ev_v30_df.empty:
    keep_v30 = ev_v30_df["ymd"].apply(lambda t: sig_at(t)==1)
    ev_v30_df = ev_v30_df[keep_v30].copy()
if not ev_lag_df.empty:
    keep_lag = ev_lag_df["ymd"].apply(lambda t: sig_at(t)==0)
    ev_lag_df = ev_lag_df[keep_lag].copy()

# ETF events — BAL ETF always; VN30 ETF only when active
def etf_to_tx(etf_evts, book):
    if not etf_evts: return pd.DataFrame()
    d = pd.DataFrame(etf_evts)
    d["ymd"] = pd.to_datetime(d["ymd"])
    return pd.DataFrame({
        "ymd": d["ymd"], "ticker": "E1VFVN30",
        "action": d["action"].apply(lambda a: "buy" if a=="buy_etf" else "sell"),
        "buy_amount": np.where(d["action"]=="buy_etf", d["amount_vnd"], 0.0),
        "sell_amount": np.where(d["action"]=="sell_etf", d["amount_vnd"], 0.0),
        "fee": d["friction_cost"], "adj_price": d["price_vn30"], "shares": d["shares"],
        "holding_id": d["holding_id"], "play_type": "ETF_PARK",
        "cash_after": d["cash_after"],
        "reason": "ETF_REBAL_state" + d["state"].astype(str), "book": book,
    })
etf_bal_tx = etf_to_tx(etf_bal, "BAL")
etf_v30_tx = etf_to_tx(etf_v30, "VN30")
if not etf_v30_tx.empty:
    keep_etf = etf_v30_tx["ymd"].apply(lambda t: sig_at(t)==1)
    etf_v30_tx = etf_v30_tx[keep_etf].copy()

# SWITCH virtual events
switch_rows = []
for ts, prv, cur, cost_vnd in flip_dates:
    switch_rows.append({"ymd":ts,"ticker":"_SWITCH_","action":"switch",
        "buy_amount":0.0,"sell_amount":0.0,"fee":float(cost_vnd),
        "adj_price":None,"shares":0.0,
        "holding_id":f"SW_{ts.strftime('%Y%m%d')}",
        "play_type":"ENSEMBLE_SWITCH","cash_after":None,
        "reason":f"FLIP_{'V11toV12' if cur==0 else 'V12toV11'}", "book":"SWITCH"})
switch_df = pd.DataFrame(switch_rows) if switch_rows else pd.DataFrame()

all_tx = pd.concat([ev_bal_df, ev_v30_df, ev_lag_df, etf_bal_tx, etf_v30_tx, switch_df], ignore_index=True)
if not all_tx.empty:
    all_tx["ymd"] = pd.to_datetime(all_tx["ymd"])
    all_tx = all_tx.sort_values(["ymd","book","action","ticker"]).reset_index(drop=True)

# Cumulative transaction count
tx_counts = all_tx.groupby(all_tx["ymd"]).size().cumsum() if not all_tx.empty else pd.Series(dtype=int)
n_tx_series = pd.Series(0, index=common, dtype=int)
for d, n in tx_counts.items():
    n_tx_series.loc[n_tx_series.index >= d] = int(n)

# Per-component breakdown (BAL always; second-leg from selected leg's stock+ETF MV)
cash_b = nav_bal.set_index("time")["cash"].loc[common]
etf_b  = nav_bal.set_index("time")["cash_etf"].loc[common]
stk_b  = (nav_bal.set_index("time")["positions_mv"] + nav_bal.set_index("time")["pending_mv"]).loc[common]
n_pos_b = nav_bal.set_index("time")["n_pos"].loc[common]

# For the switched-leg breakdown, take the leg that was active on each day.
# This is for display/sanity only — combined_nav is the source of truth for NAV.
cash_v = nav_v30.set_index("time")["cash"].loc[common]
etf_v  = nav_v30.set_index("time")["cash_etf"].loc[common]
stk_v  = (nav_v30.set_index("time")["positions_mv"] + nav_v30.set_index("time")["pending_mv"]).loc[common]
n_pos_v = nav_v30.set_index("time")["n_pos"].loc[common]
cash_l_ser = nav_lag.set_index("time")["cash"].loc[common]
stk_l_ser  = nav_lag.set_index("time")["positions_mv"].loc[common]
n_pos_l_ser = nav_lag.set_index("time")["n_pos"].loc[common]

# Scale active-leg breakdown so that (active cash + ETF + stocks) = second_series.
# Independent sims started at 25B; switched leg may differ due to cumulative switching cost.
active_total = pd.Series(np.where(sig_loc==1, (cash_v+etf_v+stk_v).values, (cash_l_ser+stk_l_ser).values), index=common)
scale = (second_series / active_total).replace([np.inf,-np.inf], np.nan).fillna(1.0)

second_cash  = np.where(sig_loc==1, cash_v.values, cash_l_ser.values) * scale.values
second_etf   = np.where(sig_loc==1, etf_v.values,   0.0) * scale.values
second_stk   = np.where(sig_loc==1, stk_v.values,   stk_l_ser.values) * scale.values
second_npos  = np.where(sig_loc==1, n_pos_v.values, n_pos_l_ser.values)

combined_logs = pd.DataFrame({
    "ymd": common,
    "nav": combined_nav.values,
    "BAL_cash": cash_b.values, "BAL_stocks": stk_b.values, "BAL_etf": etf_b.values,
    "SECOND_cash": second_cash, "SECOND_stocks": second_stk, "SECOND_etf": second_etf,
    "cash": cash_b.values + second_cash,
    "cash_etf": etf_b.values + second_etf,
    "stocks_mv": stk_b.values + second_stk,
    "num_holdings": n_pos_b.values + second_npos,
    "num_transactions": n_tx_series.values,
    "state": pd.Series(common).map(state_ff).values,
    "active_leg": np.where(sig_loc==1, "VN30", "LAGGED"),
    "ens_signal": sig_loc.values,
})

# ============================================================================
# 10. Save CSVs + open positions + MTM phantoms
# ============================================================================
print("\n[10] Saving CSVs + open positions...")
os.makedirs(os.path.join(WORKDIR,"data"), exist_ok=True)

def safe_to_csv(df, path):
    try:
        df.to_csv(path, index=False); return path
    except PermissionError:
        alt = path.replace(".csv",".new.csv"); df.to_csv(alt, index=False); return alt

logs_path = safe_to_csv(combined_logs, os.path.join(WORKDIR,"data","pt_v5_2024_logs.csv"))

# Open positions: BAL always + active leg at last day
last_day = common[-1]
final_sig = int(sig_loc.iloc[-1])
open_bal = nav_bal.attrs.get("open_positions_final") if hasattr(nav_bal,"attrs") else None
etf_lots_bal = nav_bal.attrs.get("etf_lots_final") if hasattr(nav_bal,"attrs") else None

if final_sig == 1:
    # Active leg = VN30
    open_active = nav_v30.attrs.get("open_positions_final") if hasattr(nav_v30,"attrs") else None
    etf_lots_active = nav_v30.attrs.get("etf_lots_final") if hasattr(nav_v30,"attrs") else None
    active_label = "VN30"
else:
    # Active leg = LAGGED
    open_active_rows = []
    for tk, p in positions_l.items():
        last_px = px_close.at[last_day, tk] if tk in px_close.columns and pd.notna(px_close.at[last_day, tk]) else p["entry_px"]
        cost = p["shares"]*p["entry_px"]; mark = p["shares"]*last_px
        open_active_rows.append({"ticker":tk,"holding_id":p["holding_id"],"entry_date":p["entry_dt"],
                                 "days_held":(last_day-p["entry_dt"]).days,"shares":p["shares"],
                                 "last_price":last_px,"cost_basis":cost,"mark_value":mark,
                                 "unrealised_pnl":mark-cost,
                                 "unrealised_ret_pct":(mark/cost-1)*100 if cost>0 else 0,
                                 "play_type":"LAGGED_HL3_S2"})
    open_active = pd.DataFrame(open_active_rows)
    etf_lots_active = None
    active_label = "LAGGED"

# Scale active-leg open positions to match second_series final value
if open_active is not None and not open_active.empty and active_total.iloc[-1] > 0:
    scale_final = second_series.iloc[-1] / active_total.iloc[-1]
    for col in ("cost_basis","mark_value","unrealised_pnl"):
        if col in open_active.columns:
            open_active[col] = open_active[col] * scale_final
    open_active["scaled_by_switch_cost"] = scale_final

open_df = pd.concat([
    (open_bal.assign(book="BAL") if open_bal is not None and not open_bal.empty else pd.DataFrame()),
    (etf_lots_bal.assign(book="BAL") if etf_lots_bal is not None and not etf_lots_bal.empty else pd.DataFrame()),
    (open_active.assign(book=active_label) if open_active is not None and not open_active.empty else pd.DataFrame()),
    (etf_lots_active.assign(book=active_label) if etf_lots_active is not None and not etf_lots_active.empty else pd.DataFrame()),
], ignore_index=True)

# MTM phantoms (BAL stocks/ETF + active leg) for analyze_portfolio.py
mtm_rows = []
if open_bal is not None and not open_bal.empty:
    for _, p in open_bal.iterrows():
        mtm_rows.append({"ymd":last_day,"ticker":p["ticker"],"action":"sell",
            "buy_amount":0.0,"sell_amount":float(p["mark_value"]),"fee":0.0,
            "adj_price":float(p["last_price"]),"shares":float(p["shares"]),
            "holding_id":p["holding_id"],"play_type":p["play_type"],"cash_after":None,
            "reason":"MTM_UNREALIZED","book":"BAL"})
if etf_lots_bal is not None and not etf_lots_bal.empty:
    for _, lot in etf_lots_bal.iterrows():
        mtm_rows.append({"ymd":last_day,"ticker":"E1VFVN30","action":"sell",
            "buy_amount":0.0,"sell_amount":float(lot["mark_value"]),"fee":0.0,
            "adj_price":float(lot["last_price"]) if pd.notna(lot["last_price"]) else None,
            "shares":float(lot["shares"]),"holding_id":lot["holding_id"],
            "play_type":"ETF_PARK","cash_after":None,"reason":"MTM_UNREALIZED","book":"BAL"})
if open_active is not None and not open_active.empty:
    for _, p in open_active.iterrows():
        mtm_rows.append({"ymd":last_day,"ticker":p["ticker"],"action":"sell",
            "buy_amount":0.0,"sell_amount":float(p["mark_value"]),"fee":0.0,
            "adj_price":float(p["last_price"]) if "last_price" in p and pd.notna(p["last_price"]) else None,
            "shares":float(p["shares"]),"holding_id":p["holding_id"],
            "play_type":p.get("play_type","ACTIVE_LEG"),"cash_after":None,
            "reason":"MTM_UNREALIZED","book":active_label})
if etf_lots_active is not None and not etf_lots_active.empty:
    for _, lot in etf_lots_active.iterrows():
        mtm_rows.append({"ymd":last_day,"ticker":"E1VFVN30","action":"sell",
            "buy_amount":0.0,"sell_amount":float(lot["mark_value"]),"fee":0.0,
            "adj_price":float(lot["last_price"]) if pd.notna(lot["last_price"]) else None,
            "shares":float(lot["shares"]),"holding_id":lot["holding_id"],
            "play_type":"ETF_PARK","cash_after":None,"reason":"MTM_UNREALIZED","book":active_label})

if mtm_rows:
    mtm_df = pd.DataFrame(mtm_rows)
    all_tx = pd.concat([all_tx, mtm_df], ignore_index=True)
    all_tx = all_tx.sort_values(["ymd","book","action","ticker"]).reset_index(drop=True)

tx_path = safe_to_csv(all_tx, os.path.join(WORKDIR,"data","pt_v5_2024_transactions.csv"))
open_path = safe_to_csv(open_df, os.path.join(WORKDIR,"data","pt_v5_2024_open_positions.csv"))
print(f"  {logs_path}")
print(f"  {tx_path}  (incl {len(mtm_rows)} MTM phantoms, {len(switch_rows)} SWITCH events)")
print(f"  {open_path}: {len(open_df)} open positions   (active leg = {active_label})")

# ============================================================================
# 11. Summary
# ============================================================================
final_nav = combined_nav.iloc[-1]
years = max((common[-1]-common[0]).days/365.25, 1e-9)
cagr = (final_nav/TOTAL_NAV)**(1/years)-1
total_ret = (final_nav/TOTAL_NAV-1)*100
peak = combined_nav.cummax()
dd = ((combined_nav-peak)/peak).min()*100

print("\n" + "="*100)
print(f" SUMMARY — V12.1 + ENSEMBLE + TQ v3.4b")
print(f" Period: {common[0].date()} → {common[-1].date()} ({years:.3f} years)")
print(f" Init: {TOTAL_NAV/1e9:.2f}B   Final: {final_nav/1e9:.4f}B   ret={total_ret:+.2f}%   CAGR={cagr*100:+.2f}%   DD={dd:+.2f}%")
print(f" Active leg today: {active_label}  (ens_signal={final_sig})")
print(f" Switch flips in window: {len(flip_dates)}  (cost ~{sum(c for *_,c in flip_dates)/1e9:.4f}B total)")
print("="*100)

# Save report scaffold (analyze_portfolio.py will append)
report_path = os.path.join(WORKDIR, "data", "pt_v5_2024_report.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write(f"# pt_v5_2024 — V12.1 ÂD-TT + Ensemble Switch (M1+M3r AND-HOLD) + TQ v3.4b\n\n")
    f.write(f"*Period*: {common[0].date()} → {common[-1].date()} ({years:.3f}y, {len(common)} trading days)\n\n")
    f.write(f"*Init NAV*: 50B  |  *Final NAV*: {final_nav/1e9:.4f}B  |  *Total ret*: {total_ret:+.2f}%  |  *CAGR*: {cagr*100:+.2f}%  |  *MaxDD*: {dd:+.2f}%\n\n")
    f.write(f"*Switch flips*: {len(flip_dates)}  |  *Switch cost*: 0.50%/flip  |  *Active leg today*: {active_label}\n\n")
    if flip_dates:
        f.write("## Switch events\n\n| Date | From | To | Cost (B) |\n|---|---|---|---|\n")
        for ts, prv, cur, cost in flip_dates:
            f.write(f"| {ts.date()} | {'VN30' if prv==1 else 'LAG'} | {'VN30' if cur==1 else 'LAG'} | {cost/1e9:.4f} |\n")
print(f"  {report_path}")

print("\nDone. Now run analyze_portfolio.py for full report.")
