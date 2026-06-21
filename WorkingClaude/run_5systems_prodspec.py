#!/usr/bin/env python3
"""run_5systems_prodspec.py — **CANONICAL** 5-system backtest (prod spec, 2026-05-25+).

This script REPLACES run_full_5systems_2014_2026.py (now deprecated). Use this for
every new 5-system backtest. Spec matches production paper-trade (pt_v11_tq34b /
pt_v12_tq34b / pt_v12_live / pt_v121_ensemble / pt_v121_ens_q2) except for the
intraday HYBRID buy rule (requires intraday_full.pkl which only covers ~2024+).


Differences from old run_full_5systems_2014_2026.py:
  - max_positions=12 (was 10)
  - tier_weights={tier:0.10} for all TIER_BAL (was simulator default)
  - t1_open_exec=True + open_prices (was legacy T-close)
  - RE_BACKLOG_BUY tier added via D1 reclassification
  - sector_cap_exempt_tiers={"RE_BACKLOG_BUY"}
  - SV_TIGHT state-conditional days_since_release filter
  - etf_rebalance_friction=0.0015

NOT applied (intraday data missing pre-2024):
  - entry_alt_prices=alt_hybrid (HYBRID ATC/T1115 buy rule)

Parameterized for fresh-start sims:
  Set env var START_DATE=YYYY-MM-DD; output goes to data/5sys_prodspec_<startshort>_<endshort>.csv
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B = os.environ.get("START_DATE", "2014-01-01")
END_B   = os.environ.get("END_DATE",   "2026-05-15")
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10
ETF_BASE  = {3: 0.7}   # V1/V2/V3/V4
ETF_KELLY = {3: 1.0}   # V5
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
STATE_CSV_TQ34B = os.environ.get("STATE_CSV_OVERRIDE", "data/vnindex_5state_tam_quan_v3_4b_full_history.csv")  # crisis-release ablation 2026-06-02
SWITCH_COST = 0.005
CASH = {}   # label -> DataFrame[cash_pct, cashetf_pct] (real per-sleeve idle reserve, for capitulation-overlay research)

start_short = START_B.replace("-","")[:6]
end_short = END_B.replace("-","")[:6]
TAG = f"{start_short}_{end_short}{os.environ.get('TAG_SUFFIX','')}"
print("="*100); print(f"  5-SYSTEM PROD-SPEC BACKTEST {START_B} -> {END_B}  (50B per system)  TAG={TAG}"); print("="*100)

# ─── 1. Load signals/prices/VNI ─────────────────────────────────────────────
print("\n[1] Loading signals + prices + VNI + Open prices...")
PKL_PATH = os.environ.get("PKL_PATH", "data/ba_v11_unified_12y_sig.pkl")
FA_TABLE = os.environ.get("FA_TABLE", "tav2_bq.fa_ratings")
print(f"  [variant] PKL={PKL_PATH}  FA_TABLE={FA_TABLE}")
with open(PKL_PATH,"rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
# Trim to window EARLY (we need history before START_B for some signal computations but pkl is daily snapshot, OK to trim)
sig_B = sig_B[(sig_B["time"]>=START_B) & (sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)

prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
# ETF parking underlying = REAL E1VFVN30 (tracks VN30, exists 2016-01-07+).
# Pre-2016 fallback = rescaled VNINDEX proxy so the parking leg has a price every day.
# (Fix 2026-05-28: was VNINDEX proxy → overstated KELLY V5 ~3pp; integrity audit.)
vn30_proxy = dict(zip(vni_B["time"], vni_B["Close"]))
try:
    _etf = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='E1VFVN30'
    AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
except Exception:
    _etf = pd.DataFrame(columns=["time", "Close"])   # E1VFVN30 vanished from ticker (2026-06) -> proxy fallback
_etf["time"] = pd.to_datetime(_etf["time"]); _etf_real = dict(zip(_etf["time"], _etf["Close"]))
if len(_etf):
    _splice = _etf["time"].min()
    _scale = (_etf_real[_splice] / vn30_proxy[_splice]) if vn30_proxy.get(_splice) else 1.0
    vn30_underlying = {}
    for d in vni_dates_B:
        if d in _etf_real: vn30_underlying[d] = _etf_real[d]
        elif d < _splice and d in vn30_proxy: vn30_underlying[d] = vn30_proxy[d] * _scale
        elif d in vn30_proxy: vn30_underlying[d] = vn30_proxy[d]
    print(f"  ETF underlying: REAL E1VFVN30 from {_splice.date()} (pre-2016 = rescaled VNINDEX proxy)")
else:
    vn30_underlying = vn30_proxy
    print("  ETF underlying: VNINDEX proxy (no E1VFVN30 data found)")

opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk,g in opens_df.groupby("ticker")}
print(f"  Open: {len(opens_df):,} rows / {len(open_prices)} tk")

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

# ─── 2. State forward-fill (TQ34b + LIVE) ───────────────────────────────────
print("\n[2] Loading states (TQ34b + LIVE)...")
STATE_OVERRIDE = os.environ.get("STATE_OVERRIDE", "none")   # none | dt4 | dt5g  (DT5G ablation, 2026-05-29)
if STATE_OVERRIDE in ("dt4", "dt5g"):
    from macro_state_live import get_macro_state
    _ms = get_macro_state(START_B, END_B, bq=bq)
    _col = "state" if STATE_OVERRIDE == "dt5g" else "state_dt4"
    state_df_tq = _ms[["time", _col]].rename(columns={_col: "state"}).copy()
    print(f"  [STATE_OVERRIDE={STATE_OVERRIDE}] TQ34b state replaced by macro_state_live.{_col} "
          f"({len(state_df_tq)} rows, {int((_ms['state']!=_ms['state_dt4']).sum())} macro-diff days)")
else:
    state_df_tq = pd.read_csv(STATE_CSV_TQ34B)
    state_df_tq["time"] = pd.to_datetime(state_df_tq["time"])
state_df_tq = state_df_tq[(state_df_tq["time"]>=START_B) & (state_df_tq["time"]<=END_B)][["time","state"]]
state_ff_tq = {}; last=None
sbd_tq = dict(zip(state_df_tq["time"], state_df_tq["state"]))
for d in vni_dates_B:
    s = sbd_tq.get(d)
    if s is not None: last = s
    state_ff_tq[d] = last

state_df_live = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time""")
state_df_live["time"] = pd.to_datetime(state_df_live["time"])
sbd_live = dict(zip(state_df_live["time"], state_df_live["state"]))
state_ff_live = {}; last=None
for d in vni_dates_B:
    s = sbd_live.get(d)
    if s is not None: last = s
    state_ff_live[d] = last

# ─── 3. D1 RE_BACKLOG reclassification ──────────────────────────────────────
print("\n[3] D1 RE_BACKLOG_BUY reclassification...")
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
  FROM {FA_TABLE} AS f
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
sig_B = sig_B.merge(d1_q, on=["ticker","time"], how="left")
omask = sig_B["_d1_ok"].fillna(False) & (sig_B["ta"]>=120)
sig_B.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig_B = sig_B.drop(columns=["_d1_ok"])
print(f"  RE_BACKLOG_BUY reclassified: {int(omask.sum()):,}")

# ─── 4. SV_TIGHT filter ─────────────────────────────────────────────────────
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
print(f"  After SV_TIGHT: {len(sig_B):,} rows")

# ─── 5. Overheat AVOID for TQ34b and LIVE ───────────────────────────────────
v_tq = vni_full.merge(state_df_tq, on="time", how="left"); v_tq["state"] = v_tq["state"].ffill()
v_tq["overheat"] = ((v_tq["Close"]/v_tq["MA200"]>1.30) & ((v_tq["state"]==5) | (v_tq["D_RSI"]>0.75)))
oh_tq = set(v_tq[v_tq["overheat"]]["time"])
sig_v_tq = sig_B.copy()
sig_v_tq.loc[sig_v_tq["time"].isin(oh_tq) & sig_v_tq["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

v_live = vni_full.merge(state_df_live, on="time", how="left"); v_live["state"] = v_live["state"].ffill()
v_live["overheat"] = ((v_live["Close"]/v_live["MA200"]>1.30) & ((v_live["state"]==5) | (v_live["D_RSI"]>0.75)))
oh_live = set(v_live[v_live["overheat"]]["time"])
sig_v_live = sig_B.copy()
sig_v_live.loc[sig_v_live["time"].isin(oh_live) & sig_v_live["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

# ─── 5b. regime_size overlay (8L rating>=4 names halved in BEAR/CRISIS) — env-gated ─────────
REGIME_SIZE = os.environ.get("REGIME_SIZE","").lower() in ("1","true","yes")
if REGIME_SIZE:
    from regime_size_overlay import apply_regime_size, build_capit_suppress_windows
    # CAPIT_SUPPRESS: turn OFF regime_size during capitulation windows (deploy TOGETHER with the
    # capitulation overlay — validated RS-off-in-capitulation, V5 +cap+grind 34.73->35.37).
    _capw = build_capit_suppress_windows() if os.environ.get("CAPIT_SUPPRESS","").lower() in ("1","true","yes") else None
    print(f"\n[5b] REGIME_SIZE on (CAPIT_SUPPRESS={'on' if _capw else 'off'}): halving 8L-rating>=4 names in BEAR/CRISIS")
    sig_v_tq, RS   = apply_regime_size(sig_v_tq,   START_B, END_B, bq, base_tiers=TIER_BAL, capit_windows=_capw)
    sig_v_live, _r = apply_regime_size(sig_v_live, START_B, END_B, bq, base_tiers=TIER_BAL, capit_windows=_capw)
    ALLOWED, TW, TWBS, EXEMPT = RS["allowed_tiers"], RS["tier_weights"], RS["tier_weights_by_state"], RS["sector_cap_exempt"]
    SUPPRESS = RS["regime_suppress_dates"]
else:
    ALLOWED, TW, TWBS, EXEMPT, SUPPRESS = TIER_BAL, TIER_WEIGHTS_V11, None, SECTOR_CAP_EXEMPT, None

# ─── 6. Universe + sector ───────────────────────────────────────────────────
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * COALESCE(t.Price, t.Close)) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# ─── 7. Re-usable BAL/VN30 runners (PROD SPEC) ──────────────────────────────
def run_bal(sig_use, state_ff, etf_states, label):
    nav, _ = simulate(sig_use, prices_B, vni_dates_B,
        allowed_tiers=ALLOWED, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=EXEMPT,
        tier_weights=TW, tier_weights_by_state=TWBS, regime_suppress_dates=SUPPRESS,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); s = nav.set_index("time")["nav"]
    ix = nav.set_index("time")
    CASH[label] = pd.DataFrame({"cash_pct": ix["cash"]/ix["nav"], "cashetf_pct": ix["cash_etf"]/ix["nav"]})
    print(f"  {label} final: {s.iloc[-1]/1e9:.3f}B"); return s

def run_vn30(sig_use, state_ff, etf_states, label):
    sig30 = sig_use[sig_use["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nav, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=ALLOWED, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        tier_weights=TW, tier_weights_by_state=TWBS, regime_suppress_dates=SUPPRESS,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ30, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); s = nav.set_index("time")["nav"]
    ix = nav.set_index("time")
    CASH[label] = pd.DataFrame({"cash_pct": ix["cash"]/ix["nav"], "cashetf_pct": ix["cash_etf"]/ix["nav"]})
    print(f"  {label} final: {s.iloc[-1]/1e9:.3f}B"); return s

# ─── 8. Run all 5 legs ──────────────────────────────────────────────────────
print("\n[8] Running legs (prod spec)...")
bal_tq_base   = run_bal(sig_v_tq,   state_ff_tq,   ETF_BASE,  "BAL_TQ_base")
bal_live_base = run_bal(sig_v_live, state_ff_live, ETF_BASE,  "BAL_LIVE_base")
bal_tq_kelly  = run_bal(sig_v_tq,   state_ff_tq,   ETF_KELLY, "BAL_TQ_kelly")
vn30_tq_base  = run_vn30(sig_v_tq, state_ff_tq, ETF_BASE,  "VN30_TQ_base")
vn30_tq_kelly = run_vn30(sig_v_tq, state_ff_tq, ETF_KELLY, "VN30_TQ_kelly")

# ─── 9. LAGGED schedule (v12 + v121) ────────────────────────────────────────
print("\n[9] LAGGED schedule + books...")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = master_idx
all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
# real (unadjusted) daily traded notional for the liquidity gate/cap: Volume_3M_P50 * Price (NOT back-adjusted Close)
_liqr = bq(f"""SELECT t.time, t.ticker, t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS liq_real
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.Volume_3M_P50 IS NOT NULL""")
_liqr["time"] = pd.to_datetime(_liqr["time"])
liq_real_l = _liqr.pivot_table(index="time", columns="ticker", values="liq_real", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
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

def run_lagged(init_nav, use_s2, sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
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
                liq_real = liq_real_l.at[dt, tk] if tk in liq_real_l.columns else 0
                if pd.isna(liq_real) or liq_real < LIQ_MIN: continue   # real VND notional (Volume_3M_P50 * Price)
                pos_pct = (0.10 if en_row["surprise"] > 0.5 else 0.08) if use_s2 else 0.08
                target = pos_pct * nav_now; cap = LIQ_CAP * liq_real * MAX_FILL
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt,"exit_dt":en_row["exit_dt"],"shares":shares,"entry_px":fpx}
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"time":dt,"nav":cash+mtm,"cash":cash})
    ndf = pd.DataFrame(nav_history).set_index("time")
    CASH[f"LAG_{'v121' if use_s2 else 'v12'}"] = pd.DataFrame(
        {"cash_pct": ndf["cash"]/ndf["nav"], "cashetf_pct": 0.0}, index=ndf.index)
    return ndf["nav"]

nav_lag_v12  = run_lagged(BOOK_NAV, use_s2=False); print(f"  LAG v12 : {nav_lag_v12.iloc[-1]/1e9:.3f}B")
nav_lag_v121 = run_lagged(BOOK_NAV, use_s2=True);  print(f"  LAG v121: {nav_lag_v121.iloc[-1]/1e9:.3f}B")

# ─── 10. M1+M3r ensemble signal ─────────────────────────────────────────────
print("\n[10] M1+M3r ensemble signal...")
cached = pd.read_csv("data/compare_v11_v12_concentration_switch.csv", index_col=0, parse_dates=True)
sig_m1 = cached["sig_m1"].dropna().astype(int)
m3r_q = """WITH base AS (
  SELECT t.time, t.ticker,
    SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret_6m,
    AVG(t.Volume_3M_P50 * COALESCE(t.Price, t.Close)) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS adv_1y
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

# ─── 11. Build 5 systems ────────────────────────────────────────────────────
print("\n[11] Building NAV series...")
common = bal_tq_base.index.intersection(vn30_tq_base.index).intersection(nav_lag_v12.index).intersection(nav_lag_v121.index).intersection(bal_live_base.index).intersection(bal_tq_kelly.index).intersection(vn30_tq_kelly.index)
m1 = sig_m1.reindex(common).ffill().fillna(1).astype(int)
m3r_a = sig_m3r.reindex(common).ffill().fillna(1).astype(int)
def ensemble_AND_hold(m1, m3):
    out = np.zeros(len(m1), dtype=int); cur = int(m1.iloc[0])
    for i, (a, b) in enumerate(zip(m1.values, m3.values)):
        if a == b: cur = int(a)
        out[i] = cur
    return pd.Series(out, index=m1.index)
sig_AH = ensemble_AND_hold(m1, m3r_a)

nav_V1 = (bal_tq_base.loc[common] + vn30_tq_base.loc[common]) / TOTAL_NAV
nav_V2 = (bal_tq_base.loc[common] + nav_lag_v12.loc[common]) / TOTAL_NAV
nav_V3 = (bal_live_base.loc[common] + nav_lag_v12.loc[common]) / TOTAL_NAV

def switched_nav(bal_s, vn30_s, lag_s, signal, switch_cost=SWITCH_COST,
                 bal_lbl=None, vn30_lbl=None, lag_lbl=None):
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
    nav_total = (nav_bal_path.values + second) / TOTAL_NAV
    cash_df = None
    if bal_lbl and bal_lbl in CASH:
        # combine REAL per-sleeve cash: BAL sleeve + active second sleeve (VN30 when sig==1 else LAGGED)
        def col(lbl, c): return CASH[lbl][c].reindex(common).ffill().fillna(0).values if lbl in CASH else np.zeros(len(common))
        bal_c, bal_e = col(bal_lbl,"cash_pct"), col(bal_lbl,"cashetf_pct")
        v30_c, v30_e = col(vn30_lbl,"cash_pct"), col(vn30_lbl,"cashetf_pct")
        lag_c, lag_e = col(lag_lbl,"cash_pct"), col(lag_lbl,"cashetf_pct")
        sig = signal.reindex(common).fillna(1).values
        sec_c = np.where(sig==1, v30_c, lag_c); sec_e = np.where(sig==1, v30_e, lag_e)
        bal_nav = nav_bal_path.values; tot = bal_nav + second
        cash_abs   = bal_c*bal_nav + sec_c*second
        cashetf_abs= bal_e*bal_nav + sec_e*second
        cash_df = pd.DataFrame({"cash_pct": cash_abs/tot, "reserve_pct": (cash_abs+cashetf_abs)/tot}, index=common)
    return pd.Series(nav_total, index=common), cash_df

nav_V4, cash_V4 = switched_nav(bal_tq_base.loc[common],  vn30_tq_base.loc[common],  nav_lag_v121.loc[common], sig_AH,
                               bal_lbl="BAL_TQ_base",  vn30_lbl="VN30_TQ_base",  lag_lbl="LAG_v121")
nav_V5, cash_V5 = switched_nav(bal_tq_kelly.loc[common], vn30_tq_kelly.loc[common], nav_lag_v121.loc[common], sig_AH,
                               bal_lbl="BAL_TQ_kelly", vn30_lbl="VN30_TQ_kelly", lag_lbl="LAG_v121")
# save REAL daily cash/reserve fractions for V4/V5 (capitulation-overlay research — no proxy)
if cash_V4 is not None:
    cdf = pd.DataFrame({"V4_cash_pct":cash_V4["cash_pct"],"V4_reserve_pct":cash_V4["reserve_pct"],
                        "V5_cash_pct":cash_V5["cash_pct"],"V5_reserve_pct":cash_V5["reserve_pct"]})
    cdf.index.name="time"; cdf.to_csv(f"data/5sys_prodspec_{TAG}_cashfrac.csv")
    print(f"  Saved REAL cash fractions: data/5sys_prodspec_{TAG}_cashfrac.csv")
vni_aligned = vni_B.set_index("time")["Close"].reindex(common).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

# ─── 12. Save + summary ─────────────────────────────────────────────────────
out = pd.DataFrame({
    "V1_V11_TQ34b": nav_V1, "V2_V12_TQ34b": nav_V2, "V3_V12_LIVE": nav_V3,
    "V4_V121_ENS_TQ34b": nav_V4, "V5_V4_KellyQ2": nav_V5, "VNI": vni_n,
    "sig_AH": sig_AH,
    # standalone momentum legs (start 1.0) for BA-only vs BA+VN30 analysis
    "BAL_kelly_leg": bal_tq_kelly.loc[common] / BOOK_NAV,
    "VN30_kelly_leg": vn30_tq_kelly.loc[common] / BOOK_NAV,
})
out.index.name = "time"
out_path = f"data/5sys_prodspec_{TAG}.csv"
out.to_csv(out_path)
print(f"\n  Saved: {out_path}  shape={out.shape}")

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
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100,"Calmar":cal,"wealth":s.iloc[-1]/s.iloc[0],"tot":(s.iloc[-1]/s.iloc[0]-1)*100}

print("\n"+"="*100); print(f"  HEADLINE  ({START_B} -> {common.max().date()})  init=50B"); print("="*100)
print(f"  {'System':<22}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>9}{'TotRet':>9}")
for name, nav in [("V1 V11+TQ34b", nav_V1),("V2 V12+TQ34b", nav_V2),("V3 V12+LIVE", nav_V3),
                   ("V4 V121_ENS+TQ34b", nav_V4),("V5 V4+KellyQ2", nav_V5),("VNI B&H", vni_n)]:
    m = metrics(nav, common.min(), common.max())
    if not m: continue
    print(f"  {name:<22}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+9.2f}{m['DD']:>+8.2f}%{m['Calmar']:>+8.2f}{m['wealth']:>+9.2f}{m['tot']:>+8.2f}%")
print("DONE.")
