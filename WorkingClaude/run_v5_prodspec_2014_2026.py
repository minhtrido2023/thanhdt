#!/usr/bin/env python3
"""run_v5_prodspec_2014_2026.py — V5 with PRODUCTION spec (minus intraday HYBRID buy).

Differences vs simplified V5 (run_full_5systems_2014_2026.py):
  (1) max_positions=12          (was 10)
  (2) tier_weights = 10% fixed per slot (was simulator default)
  (3) t1_open_exec=True + open_prices loaded (was legacy T-close)
  (4) RE_BACKLOG_BUY tier added via D1 reclassification
  (5) sector_cap_exempt_tiers={"RE_BACKLOG_BUY"}
  (6) SV_TIGHT (state-conditional days_since_release filter)
  (7) etf_rebalance_friction=0.0015
  (8) slippage=0.001 retained (paper-trade uses 0.0 because alt_hybrid bakes it in)

NOT applied (data unavailable for 2014-2020):
  (X) entry_alt_prices = alt_hybrid (HYBRID ATC/T1115 buy rule)
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
ETF_KELLY = {3: 1.0}              # V5
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
STATE_CSV_TQ34B = "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"
SWITCH_COST = 0.005

print("="*100); print("  V5 PROD-SPEC BACKTEST 2014-01-01 -> 2026-05-15  (50B per system)"); print("="*100)

# ─── 1. Load shared data ─────────────────────────────────────────────────────
print("\n[1] Loading signals, prices, VNI, Open prices...")
with open("data/ba_v11_unified_12y_sig.pkl","rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)

prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))

# Open prices for t1_open_exec
print("\n[1b] Loading Open prices for t1_open_exec...")
opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk,g in opens_df.groupby("ticker")}
print(f"  Open prices: {len(opens_df):,} rows, {len(open_prices)} tickers")

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

# ─── 2. TQ34b state forward-fill ────────────────────────────────────────────
print("\n[2] Loading TQ34b state...")
state_df_tq = pd.read_csv(STATE_CSV_TQ34B)
state_df_tq["time"] = pd.to_datetime(state_df_tq["time"])
state_df_tq = state_df_tq[(state_df_tq["time"]>=START_B) & (state_df_tq["time"]<=END_B)][["time","state"]]
sbd_tq = dict(zip(state_df_tq["time"], state_df_tq["state"]))
state_ff_tq = {}; last=None
for d in vni_dates_B:
    s = sbd_tq.get(d)
    if s is not None: last = s
    state_ff_tq[d] = last

# ─── 3. Overheat dates (TQ34b) ──────────────────────────────────────────────
v_tq = vni_full.merge(state_df_tq, on="time", how="left"); v_tq["state"] = v_tq["state"].ffill()
v_tq["overheat"] = ((v_tq["Close"]/v_tq["MA200"]>1.30) & ((v_tq["state"]==5) | (v_tq["D_RSI"]>0.75)))
overheat_dates_tq = set(v_tq[v_tq["overheat"]]["time"])

# ─── 4. D1 RE_BACKLOG_BUY reclassification (12y) ────────────────────────────
print("\n[4] Querying D1 RE_BACKLOG_BUY signal (ICB 8633 / AdvCust YoY / FA tier C/D / state 3-5)...")
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
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_q = d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
print(f"  D1 events qualifying for RE_BACKLOG_BUY: {len(d1_q):,}")

# Apply to sig_B
sig_B = sig_B.merge(d1_q, on=["ticker","time"], how="left")
omask = sig_B["_d1_ok"].fillna(False) & (sig_B["ta"]>=120)
sig_B.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig_B = sig_B.drop(columns=["_d1_ok"])
print(f"  Reclassified to RE_BACKLOG_BUY: {int(omask.sum()):,}")

# ─── 5. SV_TIGHT state-conditional filter ───────────────────────────────────
print("\n[5] Applying SV_TIGHT (state-conditional 30/60d fresh-Q gate)...")
def sv_tight_keep(row):
    s = row.get("state5"); days = row.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb_buy = sig_B["play_type"].isin(BUY_TIERS_V11)
keep_mask = (~mb_buy) | sig_B.apply(sv_tight_keep, axis=1)
sig_B = sig_B[keep_mask].copy()
print(f"  After SV_TIGHT keep: {len(sig_B):,} rows")

# ─── 6. P3 overheat AVOID for TQ34b ─────────────────────────────────────────
sig_v_tq = sig_B.copy()
sig_v_tq.loc[sig_v_tq["time"].isin(overheat_dates_tq) & sig_v_tq["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

# ─── 7. Top30 universe + sector map ─────────────────────────────────────────
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# ─── 8. BAL leg (prod spec) ─────────────────────────────────────────────────
print("\n[8] Running BAL leg @ 25B — prod spec (max_pos=12, 10% sizing, t1_open_exec, RE_BACKLOG)...")
nav_bal, _ = simulate(sig_v_tq, prices_B, vni_dates_B,
    allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
    tier_weights=TIER_WEIGHTS_V11,
    deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff_tq,
    cash_etf_states=ETF_KELLY, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
    etf_rebalance_friction=0.0015,
    open_prices=open_prices, t1_open_exec=True,
    **LIQ, name="BAL_prod")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
bal_s = nav_bal.set_index("time")["nav"]
print(f"  BAL final: {bal_s.iloc[-1]/1e9:.2f}B")

# ─── 9. VN30 leg (prod spec) ────────────────────────────────────────────────
print("\n[9] Running VN30 leg @ 25B — prod spec...")
sig30 = sig_v_tq[sig_v_tq["ticker"].isin(top30)].copy()
prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
LIQ30 = {**LIQ, "liquidity_lookup":liq30}
nav_vn30, _ = simulate(sig30, prices30, vni_dates_B,
    allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    tier_weights=TIER_WEIGHTS_V11,
    deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff_tq,
    cash_etf_states=ETF_KELLY, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
    etf_rebalance_friction=0.0015,
    open_prices=open_prices, t1_open_exec=True,
    **LIQ30, name="VN30_prod")
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
vn30_s = nav_vn30.set_index("time")["nav"]
print(f"  VN30 final: {vn30_s.iloc[-1]/1e9:.2f}B")

# ─── 10. LAGGED book v121 (same as before) ──────────────────────────────────
print("\n[10] Running LAGGED v121 book @ 25B...")
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
ENTRY_OFFSET, HOLD_DAYS, LAG_MAX_POS, LIQ_MIN = 5, 25, 12, 2e9
schedule = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY_OFFSET); exit_dt = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk,"entry_dt":entry_dt,"exit_dt":exit_dt,"surprise":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")

def run_lagged(init_nav, use_s2=True, sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = init_nav; positions = {}; nav_history = []
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    LIQ_CAP, MAX_FILL = 0.20, 5
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
                if tk in positions or len(positions) >= LAG_MAX_POS: continue
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

nav_lag_v121 = run_lagged(BOOK_NAV, use_s2=True)
print(f"  LAGGED v121 final: {nav_lag_v121.iloc[-1]/1e9:.2f}B")

# ─── 11. M1+M3r ensemble signal ─────────────────────────────────────────────
print("\n[11] Loading M1+M3r ensemble signals...")
cached = pd.read_csv("data/compare_v11_v12_concentration_switch.csv", index_col=0, parse_dates=True)
sig_m1 = cached["sig_m1"].dropna().astype(int)
m3r_q = """WITH base AS (
  SELECT t.time, t.ticker,
    SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret_6m,
    AVG(t.Volume_3M_P50 * t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS adv_1y
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '2026-05-15'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
),
ranked AS (
  SELECT time, ticker, ret_6m, adv_1y,
    ROW_NUMBER() OVER (PARTITION BY time ORDER BY adv_1y DESC) AS rnk
  FROM base WHERE adv_1y IS NOT NULL AND ret_6m IS NOT NULL
)
SELECT time, AVG(IF(rnk<=10, ret_6m, NULL)) AS top10_ret, AVG(ret_6m) AS all_ret
FROM ranked GROUP BY time ORDER BY time"""
m3r_df = bq(m3r_q); m3r_df["time"] = pd.to_datetime(m3r_df["time"])
m3r_df["M3r"] = m3r_df["top10_ret"] - m3r_df["all_ret"]
m3r = m3r_df.set_index("time")["M3r"]
def make_signal(metric, min_history=252):
    s = metric.dropna().sort_index()
    em = s.expanding(min_periods=min_history).median()
    raw = (s > em).astype(int).reindex(metric.index).ffill().fillna(1).astype(int)
    return raw.shift(1).fillna(1).astype(int)
sig_m3r = make_signal(m3r)

# ─── 12. Build V5_prod NAV ──────────────────────────────────────────────────
common = bal_s.index.intersection(vn30_s.index).intersection(nav_lag_v121.index)
m1 = sig_m1.reindex(common).ffill().fillna(1).astype(int)
m3r_a = sig_m3r.reindex(common).ffill().fillna(1).astype(int)
def ensemble_AND_hold(m1, m3):
    out = np.zeros(len(m1), dtype=int); cur = int(m1.iloc[0])
    for i, (a, b) in enumerate(zip(m1.values, m3.values)):
        if a == b: cur = int(a)
        out[i] = cur
    return pd.Series(out, index=m1.index)
sig_AH = ensemble_AND_hold(m1, m3r_a)

def switched_nav(bal_s, vn30_s, lag_s, signal, switch_cost=SWITCH_COST):
    bal_ret = bal_s.pct_change().fillna(0); vn30_ret = vn30_s.pct_change().fillna(0); lag_ret = lag_s.pct_change().fillna(0)
    nav_bal_path = (1+bal_ret).cumprod() * BOOK_NAV
    second = np.full(len(common), BOOK_NAV, dtype=float)
    prev_sig = int(signal.iloc[0])
    for i in range(1, len(common)):
        cur_sig = int(signal.iloc[i])
        if cur_sig != prev_sig: second[i] = second[i-1] * (1 - switch_cost)
        else: second[i] = second[i-1]
        r = vn30_ret.iloc[i] if cur_sig==1 else lag_ret.iloc[i]
        second[i] = second[i] * (1 + r); prev_sig = cur_sig
    return pd.Series((nav_bal_path.values + second) / TOTAL_NAV, index=common)

nav_V5_prod = switched_nav(bal_s.loc[common], vn30_s.loc[common], nav_lag_v121.loc[common], sig_AH)

# Compare to old V5
old = pd.read_csv("data/full_5systems_2014_2026.csv", index_col=0, parse_dates=True)
nav_V5_old = old["V5_V4_KellyQ2"].reindex(common).ffill()
vni_aligned = vni_B.set_index("time")["Close"].reindex(common).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

# ─── 13. Save + report ──────────────────────────────────────────────────────
out = pd.DataFrame({"V5_prod": nav_V5_prod, "V5_old": nav_V5_old, "VNI": vni_n,
                     "sig_AH": sig_AH, "state": pd.Series(state_ff_tq).reindex(common)})
out.index.name = "time"
out.to_csv("data/v5_prodspec_2014_2026.csv")
print(f"\n  Saved: data/v5_prodspec_2014_2026.csv")

def metrics(nav, start, end):
    s = nav[(nav.index>=start) & (nav.index<=end)].dropna()
    if len(s)<30: return None
    rets = s.pct_change().dropna()
    yrs = (s.index[-1]-s.index[0]).days/365.25
    spy = len(rets)/yrs if yrs>0 else 252
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((s-s.cummax())/s.cummax()).min()
    cal = cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100,"Calmar":cal,"wealth":s.iloc[-1]/s.iloc[0]}

periods = [
    ("FULL 2014-26", common.min(), common.max()),
    ("OOS 2024-26",  pd.Timestamp("2024-01-01"), common.max()),
    ("IS 2014-19",   pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-23",  pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2022 bear",   pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Y2025 bull",   pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    ("2026 YTD",     pd.Timestamp("2025-12-30"), common.max()),
]
print("\n"+"="*100)
print("  V5_prod (max_pos=12 + 10% sizing + t1_open + RE_BACKLOG + SV_TIGHT)")
print("  vs V5_old (max_pos=10 + default sizing)")
print("="*100)
for label, st, en in periods:
    print(f"\n  -- {label} --")
    print(f"  {'System':<14}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>9}")
    print(f"  {'-'*14}{'-'*9}{'-'*9}{'-'*9}{'-'*8}{'-'*9}")
    for name, nav in [("V5_prod", nav_V5_prod), ("V5_old", nav_V5_old), ("VNI B&H", vni_n)]:
        m = metrics(nav, st, en)
        if not m: continue
        print(f"  {name:<14}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+9.2f}{m['DD']:>+8.2f}%{m['Calmar']:>+8.2f}{m['wealth']:>+9.2f}")
    m_prod = metrics(nav_V5_prod, st, en); m_old = metrics(nav_V5_old, st, en)
    if m_prod and m_old:
        print(f"  Δ(prod-old)       {m_prod['CAGR']-m_old['CAGR']:+8.2f}pp{m_prod['Sharpe']-m_old['Sharpe']:+9.2f}{m_prod['DD']-m_old['DD']:+8.2f}pp")

print("\n  YEAR-BY-YEAR (%)")
print(f"  {'Year':<6}{'V5_prod':>10}{'V5_old':>10}{'VNI':>10}")
for yr in range(2014, 2027):
    sy = pd.Timestamp(f"{yr}-01-01"); ey = pd.Timestamp(f"{yr}-12-31")
    row = [f"  {yr:<6}"]
    for nav in [nav_V5_prod, nav_V5_old, vni_n]:
        s = nav[(nav.index>=sy) & (nav.index<=ey)].dropna()
        if len(s)<2: row.append(f"{'-':>10}"); continue
        r = (s.iloc[-1]/s.iloc[0]-1)*100
        row.append(f"{r:>+9.1f}%")
    print("".join(row))
print("\n"+"="*100); print("DONE.")
