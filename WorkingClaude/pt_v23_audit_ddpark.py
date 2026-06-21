# -*- coding: utf-8 -*-
"""pt_v23_audit_2014.py — V2.3 GO-LIVE config re-simulated 2014-01-02 -> now, AUDIT EDITION.
=============================================================================================
Purpose (user 2026-06-12): re-run the EXACT go-live V2.3 architecture (pt_v22_dt5g.py) over
the full history 2014->now and emit ONE self-contained audit file that an independent bot can
verify line-by-line against raw BigQuery data (tav2_bq.*) WITHOUT knowing this codebase,
reconstructing the final NAV and confirming CAGR / Sharpe / MaxDD / Calmar.

Architecture (identical to pt_v22_dt5g.py go-live):
  BOOK A BAL 25B : SIGNAL_V11 + SV_TIGHT + overheat + D1 + EXBULL-suppress + regime_size,
                   tier 10%/name, max 12, hold 45d, stop -20%, ETF parking {3:0.7}.
  BOOK B LAG 25B : PEAD schedule (NP_R>=15 & prior_n_good>=4 & pa_HL3>=5), T+5 entry,
                   25td hold, 10%/8%, no stop, ETF parking {3:0.7}.
  CAPIT v2       : washout gate 30%, state routing (CRISIS 1.0/NEUTRAL .75/BULL .5/BEAR guard),
                   grind x0.5, hold 60td, stop/slot-exempt, sized on each book's free cash.
  ALLOCATOR      : state-conditional w_LAG {1:.50, 2:0, 3/4/5:.65}, BAND-only +/-10pp, TC 0.1%.
  STATE          : tav2_bq.vnindex_5state_dt5g_live (DT5G production).

AUDIT deviations from the live forward script (each is REQUIRED for BQ verifiability and
matches the basis on which the published V2.3 backtest numbers were produced):
  1. entry_alt_prices=None — all fills at T+1 Open from tav2_bq.ticker. (Live track also uses
     intraday ATC/11:15 prices from a local pkl; intraday data does NOT exist in BQ, so it
     cannot be audited. Historical published numbers were produced WITHOUT alt fills.)
  2. LAG-book prices/opens/liquidity come from tav2_bq.ticker directly (live script reads the
     same data via locally cached pkl panels that were themselves built from BQ).

Output: data/v23_golive_audit_2014_now.csv  (ONE file, sectioned by record_type)
  META        key/value: every parameter + verification procedure for the audit bot
  EVENT_CAPIT capitulation washout events (date/state/size)
  TX          every transaction, both books: stocks + E1VFVN30 ETF + final MTM marks
  REBAL       allocator band rebalances
  DAILY       per-session: per-book ledger NAV refs, allocator capitals, combined NAV, VNI close
  ANNUAL      calendar-year returns (system vs VNINDEX)
  METRIC      final metrics + internal self-check results
"""
import os, sys, io, pickle, bisect
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate, bq, VNI_QUERY, TC_BUY, TC_SELL, CG_TAX
from signal_v11_sql import SIGNAL_V11
from pt_dates import detect_end_date

START_DATE  = os.environ.get("AUDIT_START", "2014-01-02")  # override via env for windowed audits
_START_TAG  = "" if START_DATE == "2014-01-02" else "_from" + START_DATE.replace("-", "")
STATE_TABLE = "tav2_bq.vnindex_5state_dt5g_live"
END_DATE    = detect_end_date()
TOTAL_NAV   = float(os.environ.get("NAV_TOTAL_B", "50")) * 1e9   # capacity sweep via env
BAL_NAV     = TOTAL_NAV / 2
LAG_NAV     = TOTAL_NAV / 2
_NAV_TAG    = "" if abs(TOTAL_NAV - 50e9) < 1 else f"_nav{int(TOTAL_NAV/1e9)}B"

# MODE (same auditable harness for all: T+1 Open, all-BQ, no intraday):
#   "v23a"    = go-live config WITH LAG/BAL band-allocator + CAPIT  (combined = allocator)
#   "v23c"    = champion plain-sum STATIC 50/50 + CAPIT             (combined = navb + navl)
#   "v22base" = STATIC 50/50, CAPIT DISABLED (BAL stack + LAG PEAD + ETF parking only)
# Holding everything else fixed, the deltas isolate: (v23a - v23c) = allocator;
# (v23c - v22base) = CAPIT sleeve contribution.
MODE = (sys.argv[1].lower() if len(sys.argv) > 1 else "v23a")
assert MODE in ("v23a", "v23c", "v22base"), "MODE must be v23a | v23c | v22base"
USE_LAG_ALLOCATOR = (MODE == "v23a")
USE_CAPIT = (MODE != "v22base")
# Optional per-event CAPIT deployment cap (fraction of book NAV). argv[2], e.g. 0.15 or 0.20.
# Structural fix for the 2022-04-19 tail: no single washout event may target more than CAP of the
# book, regardless of free-cash x state-size. None = uncapped (original sizing).
def _argf(i):  # parse float-or-"none"/"off" positional
    if len(sys.argv) > i and sys.argv[i].lower() not in ("none", "off", "-"):
        return sys.argv[i]
    return None
CAPIT_EVENT_CAP = float(_argf(2)) if _argf(2) is not None else None
# MATURITY rule (argv[3]): scale CAPIT size in CRISIS (state 1) by how DEEP the decline already is
# (dd52w). Encodes the user's hypothesis (2026-06-12): a washout in a FRESH crisis (shallow dd, first
# leg of a macro bear, still near a post-euphoria top) has high mean-reversion risk -> deploy small;
# a MATURE crisis (deep dd, reversion mostly done) is the real capitulation -> full size. NEUTRAL/BULL
# washouts are left to the bull-aware base (data: shallow pullbacks there are safe).
#   "smooth" : CRISIS size *= clip(|dd52w| / 20, 0.25, 1.0)   (linear ramp; -8%->0.40x, -20%->1.0x)
#   "gate15" : CRISIS size *= 1.0 if dd52w<=-15% else 0.30    (binary maturity gate)
MATURITY = (sys.argv[3].lower() if _argf(3) is not None else None)
assert MATURITY in (None, "smooth", "gate15", "ew2d", "postbull"), "MATURITY must be smooth|gate15|ew2d|postbull|off"
# postbull gate (user 2026-06-13): a washout right after a strong PROLONGED bull, still near the top
# (shallow decline), has high pending mean-reversion -> DON'T buy. Confirmed on 2007/2018/2022 (all
# ret_2y +83..+287%, dd_1y -7..-8%, then fell 16-53%). Block if trailing-2yr VNINDEX return >= thr AND
# decline-from-1yr-peak still shallow (> -15%). Keeps 2025-10 (ret_2y +42% < thr) and deep-corrected
# 2018 events (dd_1y -23/-25%). Thresholds: round numbers in a wide margin (kept<=52% vs blocked 83%).
POSTBULL_RET2Y_THR = 0.60   # trailing 2yr (504 session) VNINDEX return
POSTBULL_DD1Y_THR  = -15.0  # % : decline from 1yr peak must be SHALLOWER than this to be 'not yet corrected'
def maturity_mult(dd52w_pct):
    if MATURITY == "smooth": return float(np.clip(abs(dd52w_pct) / 20.0, 0.25, 1.0))
    if MATURITY == "gate15": return 1.0 if dd52w_pct <= -15.0 else 0.30
    return 1.0
# ew2d 2-D gate (user refinement 2026-06-12): deploy full only if the BROAD market has both
# corrected (EW p25 stock dd-from-52w-high <= EW_P25_THR) AND the trend has broken (>= BREADTH_THR
# of stocks below MA200 = market reverted below its own mean, not a fresh post-euphoria first leg).
# Applied to ALL states (the whole point is to REPLACE the megacap-masked index-state lens with the
# equal-weight one). Thresholds set on the audit events: 2022-04 breadth 43% (trend intact -> shrink),
# 2025-10 breadth 51% (broken -> keep). EW_P25 is a loose floor (all events satisfy it); breadth is the lever.
EW2D_P25_THR    = -20.0   # % : weak-half stock drawdown must be at least this deep
EW2D_BREADTH_THR = 0.48   # fraction below MA200 (trend-broken / reverted-to-mean)
# size multiplier when the 2-D gate fails (dangerous washout). argv[4] override: 0.0 = HARD-BLOCK
# (don't buy dangerous washouts at all, per user 2026-06-13: "if dangerous, don't necessarily buy").
EW2D_SHRINK     = float(sys.argv[4]) if len(sys.argv) > 4 else 0.30
# Edge-conditional allocator (argv[5]=="edge", validated walk-forward 2026-06-13): in good states
# (3/4/5) tilt w_LAG to 0.65 ONLY when LAG's own causal edge-health mean12 (trailing-12M mean LAG
# trade post-return, from data/lag_edge_health.csv) >= EDGE_THR%; else hold 0.50. BEAR=0/CRISIS=0.50
# unchanged. Avoids over-weighting LAG when its edge is in a cyclical trough (2022-23/2026).
USE_EDGE_ALLOC = (len(sys.argv) > 5 and sys.argv[5].lower() == "edge")
EDGE_THR = 4.0
# ETF parking liquidity cap (env ETF_LIQ, user 2026-06-13: E1VFVN30 has real ADV limits too).
#   "off"      = no cap (legacy)
#   "strict"   = 20% of E1VFVN30 SECONDARY ADV/day (conservative floor)
#   "creation" = 20% of aggregate VN30-basket ADV/day (allows ETF primary creation; realistic ceiling)
#   "custom"   = parking VEHICLE itself is replaced by a CUSTOM VN30-style basket (ex-VIC, cap-weighted
#                chained index of the 30 most-liquid ticker_prune large-caps ex-VIC/ex-index). Its daily
#                close series overrides vn30_underlying; capacity = 20% of the basket's own aggregate
#                trading value (creation-equivalent, ~100x E1VFVN30 secondary). Tests §5 of the
#                2026-06-13 handoff: at large NAV the strict-ETF cap strands idle cash; a high-capacity
#                ex-VIC beta vehicle gives that cash a place to deploy. ex-VIC = controlled beta (catches
#                less of a VIC-led narrow rally on purpose — justifiable beta, per capacity-ceiling memo).
#   "custompit"  = like custom but POINT-IN-TIME quarterly membership (chosen from prior-quarter
#                  liquidity only, ex-VIC/ex-index) — removes the hindsight survivorship of the fixed
#                  2020-2025 selection. The honest deployable beta.
#   "custompitq" = custompit + 8L quality tilt (as-of fa_ratings_8l multiplier on cap-weight).
#   "custompitg" = custompit + (a) rebalance on 05/Feb,05/May,05/Aug,05/Nov (post-earnings, fresh
#                  fundamentals) AND (b) HARD SAFETY GATE: only as-of 8L rating <=3 (investment-grade)
#                  may enter -> excludes manipulation/distress names (PVX/OGC/HNG/SCR-distress...) that
#                  pure-liquidity would pull in (FLC/ROS already out of ticker_prune). Capital guard.
#   "custompitgq"= custompitg + 8L quality tilt. The full production-honest safe vehicle.
ETF_LIQ = os.environ.get("ETF_LIQ", "off").lower()
assert ETF_LIQ in ("off", "strict", "creation", "custom", "custompit", "custompitq", "custompitg", "custompitgq")
_IS_CUSTOM = ETF_LIQ in ("custom", "custompit", "custompitq", "custompitg", "custompitgq")
# PIT params per mode: (quality, rebal_anchor, gate_rating)
_PIT_PARAMS = {"custompit":   ("none", "qstart", None),
               "custompitq":  ("tilt", "qstart", None),
               "custompitg":  ("none", "q2m5",   3),
               "custompitgq": ("tilt", "q2m5",   3)}
ETF_LIQ_PCT = 0.20
# PARKING-STATE POLICY (env PARK_STATES). Lever for the park-BULL experiment (2026-06-14):
# extend idle-cash parking beyond NEUTRAL. Format "state:frac,..." e.g. "3:0.7,4:1.0" = park 70%
# of idle cash in NEUTRAL + 100% in BULL. Default "3:0.7" == current production (NEUTRAL-only 70%),
# so the single-run audit path is byte-identical to before when PARK_STATES is unset.
_PARK_SPEC = os.environ.get("PARK_STATES", "3:0.7")
PARK_STATES_DICT = {}
for _kv in _PARK_SPEC.split(","):
    _kv = _kv.strip()
    if _kv:
        _s, _f = _kv.split(":"); PARK_STATES_DICT[int(_s)] = float(_f)
_park_tag = ("" if PARK_STATES_DICT == {3: 0.7} else
             "_park" + "_".join(f"{s}-{int(round(f*100))}" for s, f in sorted(PARK_STATES_DICT.items())))
_liqsuf = "" if ETF_LIQ == "off" else f"_etfliq{ETF_LIQ}"
# Basket WEIGHT SCHEME (env BASKET_WT, de-concentration review 2026-06-15): capwt(default, legacy)
# | ew | namecap | sectorcap. Only affects custom* parking vehicles; capwt == current production.
BASKET_WT = os.environ.get("BASKET_WT", "capwt").lower()
assert BASKET_WT in ("capwt", "ew", "namecap", "sectorcap")
_wt_tag = "" if BASKET_WT == "capwt" else f"_wt{BASKET_WT}"
# Basket SIZE x CAP sweep (env BASKET_TOPN / BASKET_NAMECAP, C+D review 2026-06-16): top_n members and
# single-name cap. Defaults = production (30 names, 10% name cap). Only affect custom* vehicles.
BASKET_TOPN = int(os.environ.get("BASKET_TOPN", "30"))
BASKET_NAMECAP = float(os.environ.get("BASKET_NAMECAP", "0.10"))
_sz_tag = "" if (BASKET_TOPN == 30 and abs(BASKET_NAMECAP - 0.10) < 1e-9) else f"_n{BASKET_TOPN}_cap{int(round(BASKET_NAMECAP*100))}"
_capsuf = "" if CAPIT_EVENT_CAP is None else f"_cap{int(round(CAPIT_EVENT_CAP*100))}"
_matsuf = "" if MATURITY is None else (f"_mat{MATURITY}" + (f"_shrink{int(round(EW2D_SHRINK*100))}" if MATURITY in ("ew2d", "postbull") and abs(EW2D_SHRINK - 0.30) > 1e-9 else ""))
_matsuf += "_edge" if USE_EDGE_ALLOC else ""
LABEL = {"v23a": "V2.3A (allocator + CAPIT)",
         "v23c": "V2.3C (static 50/50 + CAPIT)",
         "v22base": "V2.2-base (static 50/50, NO CAPIT)"}[MODE] \
        + (f" + per-event cap {int(round(CAPIT_EVENT_CAP*100))}%" if CAPIT_EVENT_CAP else "") \
        + (f" + maturity:{MATURITY}" if MATURITY else "") \
        + (f" + edge-cond-allocator(thr{EDGE_THR:.0f}%)" if USE_EDGE_ALLOC else "")
AUDIT_PATH  = os.path.join(WORKDIR, "data",
                           {"v23a": "v23_golive_audit_2014_now.csv",
                            "v23c": "v23c_golive_audit_2014_now.csv",
                            "v22base": "v22base_audit_2014_now.csv"}[MODE].replace(".csv", _capsuf + _matsuf + _liqsuf + _park_tag + _wt_tag + _sz_tag + _NAV_TAG + _START_TAG + ".csv"))

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                 "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO",
                 "RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
MAX_POS_V11 = 12

STATE_LAG_WEIGHT  = {1: 0.50, 2: 0.00, 3: 0.65, 4: 0.65, 5: 0.65}
ALLOC_REBAL_TC    = 0.001
ALLOC_REBAL_BAND  = 0.10

WASHOUT_GATE = 0.30
CAPIT_HOLD   = 60
def capit_base(state, dd52w, vn_cooling):
    if state == 1: return 1.0
    if state == 3: return 0.75
    if state in (4, 5): return 0.5
    if state == 2: return 0.5 if (dd52w > -25 or vn_cooling) else 0.0
    return 0.5

print("=" * 100)
print(f"  {LABEL} — FULL AUDIT SIMULATION {START_DATE} -> {END_DATE}")
print(f"  NAV={TOTAL_NAV/1e9:.0f}B (25B BAL + 25B LAG)   state={STATE_TABLE}")
print(f"  PARK vehicle={ETF_LIQ}  parking policy (cash_etf_states) {PARK_STATES_DICT}")
print(f"  combine={'allocator ON '+str(STATE_LAG_WEIGHT)+' band ±'+str(int(ALLOC_REBAL_BAND*100))+'pp' if USE_LAG_ALLOCATOR else 'STATIC 50/50 sum'}   CAPIT={'ON' if USE_CAPIT else 'OFF'}")
print(f"  fills=T+1 Open (BQ-auditable, no intraday)   -> {os.path.basename(AUDIT_PATH)}")
print("=" * 100)

# ============================================================================
# 2. BA v11 signals + filters (identical layering to pt_v22_dt5g.py go-live)
# ============================================================================
print("\n[2] Loading v11 signals + Release_Date + 5-state + overheat + D1...")
sig = bq(SIGNAL_V11.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  signals: {len(sig):,} rows")
assert len(sig) < 1_990_000, "bq() max_rows cap risk"

rel = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE_SUB(DATE '{START_DATE}', INTERVAL 120 DAY) AND DATE '{END_DATE}'""")
rel["Release_Date"] = pd.to_datetime(rel["Release_Date"])
rel_by_tk = rel.sort_values(["ticker","Release_Date"]).groupby("ticker")["Release_Date"].apply(list).to_dict()
ds_arr = np.empty(len(sig))
for i, (tk, t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
    arr = rel_by_tk.get(tk)
    if not arr: ds_arr[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    ds_arr[i] = np.nan if idx == 0 else (pd.Timestamp(t) - arr[idx-1]).days
sig["days_since_release"] = ds_arr

state_df = bq(f"""SELECT s.time, s.state FROM {STATE_TABLE} AS s WHERE s.time <= DATE '{END_DATE}'""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["overheat"] = (vni_full["Close"]/vni_full["MA200"] > 1.30) & \
                       ((vni_full["time"].map(state_by_date) == 5) | (vni_full["D_RSI"] > 0.75))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
sig["state"] = sig["time"].map(state_by_date)

# D1 RE_BACKLOG_BUY override (same as go-live)
d1 = bq(f"""
WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker, t.time, fa.fa_tier,
  SAFE_DIVIDE(t.NP_P0, t.NP_P4)-1 AS np_yoy, fin.Revenue_YoY_P0 AS rev_yoy,
  adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN {STATE_TABLE} AS s5 ON s5.time = t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"] > 0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99) > 0) | (d1["rev_yoy"].fillna(-99) > 0)))
d1_q = d1.loc[d1_mask, ["ticker","time"]].assign(_d1_ok=True)
sig = sig.merge(d1_q, on=["ticker","time"], how="left")
omask = sig["_d1_ok"].fillna(False) & (sig["ta"] >= 120)
sig.loc[omask, "play_type"] = "RE_BACKLOG_BUY"
sig = sig.drop(columns=["_d1_ok"])

# SV_TIGHT (vectorized — logic identical to go-live sv_tight_keep row function)
_st = sig["state"]; _days = sig["days_since_release"]
keep = pd.Series(True, index=sig.index)
m1 = _st == 1
m23 = _st.isin([2, 3])
keep[m1]  = (_days.notna() & (_days <= 30))[m1]
keep[m23] = (_days.notna() & (_days <= 60))[m23]
mb = sig["play_type"].isin(BUY_TIERS_V11)
sig_f = sig[(~mb) | keep].copy()
mp3 = sig_f["time"].isin(overheat_dates) & sig_f["play_type"].isin(BUY_TIERS_V11)
sig_f.loc[mp3, "play_type"] = "AVOID_overheated"

# EXBULL momentum suppression (go-live mp4)
EXB_MOM = {"MEGA", "MOMENTUM", "MOMENTUM_S", "MOMENTUM_QUALITY", "MOMENTUM_A", "S_PRO"}
mp4 = (sig_f["state"] == 5) & sig_f["play_type"].isin(EXB_MOM)
sig_f.loc[mp4, "play_type"] = "AVOID_exbull"
print(f"  [EXBULL fix] suppressed {int(mp4.sum())} momentum signals in EX-BULL (state==5)")

from regime_size_overlay import apply_regime_size
sig_f, RS = apply_regime_size(sig_f, START_DATE, END_DATE, bq, base_tiers=TIER_BAL)

# ============================================================================
# 3. Common data (BAL prices/opens/liquidity, VNI calendar, ETF, sectors)
# ============================================================================
print("\n[3] Loading prices/Open/sector/E1VFVN30...")
opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
assert len(opens_df) < 1_990_000, "bq() max_rows cap risk (opens)"
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk, g in opens_df.groupby("ticker")}
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_f.groupby("ticker")}
liq_map = dict(zip(zip(sig_f["ticker"], sig_f["time"]), sig_f["liq"]))

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
vni_close_by_date = dict(zip(vni["time"], vni["Close"]))

etf_real = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
etf_real["time"] = pd.to_datetime(etf_real["time"])
vn30_underlying = dict(zip(etf_real["time"], etf_real["Close"]))

# ETF parking liquidity ceiling (user 2026-06-13). Build per-date ADV cap for parking.
etf_adv_lookup = None
CUSTOM_MEMBERS = None; CUSTOM_LEVEL = None; CUSTOM_MEMBERS_DF = None   # populated only in custom* modes
if ETF_LIQ != "off":
    if ETF_LIQ == "strict":
        # 60-session trailing mean of E1VFVN30 secondary trading value (Price*Volume)
        _a = bq(f"""SELECT t.time, COALESCE(t.Price,t.Close)*t.Volume AS tv FROM tav2_bq.ticker AS t
WHERE t.ticker='E1VFVN30' AND t.time >= DATE_SUB(DATE '{START_DATE}', INTERVAL 200 DAY)
  AND t.time <= DATE '{END_DATE}' ORDER BY t.time""")
    elif ETF_LIQ == "creation":  # aggregate VN30-basket trading value -> ETF primary-creation ceiling
        _top30 = list(bq("""SELECT t.ticker FROM tav2_bq.ticker t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
        _a = bq(f"""SELECT t.time, SUM(COALESCE(t.Price,t.Close)*t.Volume) AS tv FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({",".join(f"'{x}'" for x in _top30)})
  AND t.time >= DATE_SUB(DATE '{START_DATE}', INTERVAL 200 DAY) AND t.time <= DATE '{END_DATE}'
GROUP BY t.time ORDER BY t.time""")
    else:  # custom*: build the ex-VIC basket as the parking VEHICLE itself
        import custom_basket as cb
        if ETF_LIQ == "custom":   # static hindsight membership (fixed 2020-2025 liquidity selection)
            _cust = cb.select_members(bq)
            print(f"  [ETF-LIQ custom] ex-VIC cap-weighted basket (STATIC), {len(_cust)} names: {', '.join(_cust)}")
            _lvl_d, _adv_d, _bx = cb.build(bq, _cust, START_DATE, END_DATE)
            CUSTOM_MEMBERS = _cust
        else:                     # PIT membership (custompit/q legacy; custompitg/q = +q2m5 timing +gate)
            _q, _reb, _gate = _PIT_PARAMS[ETF_LIQ]
            _lvl_d, _adv_d, _memdf, _bx = cb.build_pit(bq, START_DATE, END_DATE, quality=_q,
                                                       rebal=_reb, gate_rating=_gate, weight_scheme=BASKET_WT,
                                                       top_n=BASKET_TOPN, name_cap=BASKET_NAMECAP)
            CUSTOM_MEMBERS_DF = _memdf
            CUSTOM_MEMBERS = sorted(_memdf["ticker"].unique())
            print(f"  [ETF-LIQ {ETF_LIQ}] ex-VIC PIT basket (quality={_q}, rebal={_reb}, gate={_gate}, weight={BASKET_WT}): "
                  f"{_memdf['rebal_date'].nunique()} rebals, {len(CUSTOM_MEMBERS)} union names, "
                  f"avg {_memdf.groupby('rebal_date')['ticker'].count().mean():.0f}/rebal")
        vn30_underlying = _lvl_d           # parking vehicle = synthetic basket level series
        CUSTOM_LEVEL = _lvl_d
        etf_adv_lookup = _adv_d
    if not _IS_CUSTOM:
        _a["time"] = pd.to_datetime(_a["time"])
        _a["adv"] = _a["tv"].rolling(60, min_periods=20).mean()
        etf_adv_lookup = {t: float(v) for t, v in zip(_a["time"], _a["adv"]) if pd.notna(v)}
    _med = np.median(list(etf_adv_lookup.values())) if etf_adv_lookup else 0
    print(f"  [ETF-LIQ {ETF_LIQ}] cap={ETF_LIQ_PCT:.0%} of ADV; median ADV {_med/1e9:.1f}B/day "
          f"-> ~{_med*ETF_LIQ_PCT/1e9:.1f}B/day parkable")
ETF_LIQ_KW = dict(etf_adv_lookup=etf_adv_lookup, etf_liquidity_pct=(ETF_LIQ_PCT if ETF_LIQ != "off" else None))
# Parking-vehicle label in the TX/MTM log: real ETF for off/strict/creation; synthetic basket for custom*.
PARK_TICKER = {"custom": "CUSTOM_VN30EXVIC", "custompit": "CUSTOM_VN30EXVIC_PIT",
               "custompitq": "CUSTOM_VN30EXVIC_PITQ", "custompitg": "CUSTOM_VN30EXVIC_PITG",
               "custompitgq": "CUSTOM_VN30EXVIC_PITGQ"}.get(ETF_LIQ, "E1VFVN30")

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

state_ff = {}; last_s = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_s = s
    state_ff[d] = last_s

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# ============================================================================
# 4. LAGGED PEAD schedule (signal layer from earnings files; prices from BQ)
# ============================================================================
print("\n[4] Building LAGGED schedule...")
# Extended trading calendar (pre-window buffer so release-date offsets resolve)
cal_df = bq(VNI_QUERY.format(start="2013-06-01", end=END_DATE))
cal_df["time"] = pd.to_datetime(cal_df["time"])
all_dates = np.array(sorted(cal_df["time"].unique()), dtype="datetime64[ns]")

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
    hist = []
    for ri in g.index.tolist():
        row = ev.loc[ri]; cur = row["Release_Date"]
        ev.at[ri, "prior_n_good"] = len(hist)
        if hist:
            da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
            w = np.exp(-LN2 * ((cur - da).days.values / 365.25) / HL)
            ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            hist.append((cur, row["post_ret"]))
e_hl3 = ev[(ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)].copy()

sw, ewd = pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)
def offset_date(ref, off):
    pos = np.searchsorted(all_dates, np.datetime64(ref), side="right") - 1
    tgt = pos + off
    return pd.Timestamp(all_dates[tgt]) if 0 <= tgt < len(all_dates) else None

lag_cand = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]
    entry = offset_date(row["Release_Date"], 5)
    if entry is None or entry < sw or entry > ewd: continue
    sd = offset_date(entry, -1)
    if sd is None: continue
    lag_cand.append({"sd": sd, "ticker": tk, "surprise": row["surprise_B_MA"],
                     "release": row["Release_Date"], "np_r": row["NP_R"]})
print(f"  LAG candidate events in window: {len(lag_cand)}")

# ============================================================================
# 5. CAPIT v2 events (gate 30%, state routing, BEAR guard) + baskets
# ============================================================================
print("\n[5] CAPIT v2 washout events...")
br = bq(f"""SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold
FROM tav2_bq.ticker_prune p
WHERE p.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' AND p.Close_T1>0
GROUP BY p.time ORDER BY p.time""")
br["time"] = pd.to_datetime(br["time"])
vni_hist = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time >= DATE_SUB(DATE '{START_DATE}', INTERVAL 1100 DAY)
  AND t.time <= DATE '{END_DATE}' ORDER BY t.time""")
vni_hist["time"] = pd.to_datetime(vni_hist["time"])
vni_hist = vni_hist.set_index("time")
vni_hist["dd52"] = (vni_hist["Close"] / vni_hist["Close"].rolling(252, min_periods=60).max() - 1) * 100
vni_hist["ret2y"] = vni_hist["Close"] / vni_hist["Close"].shift(504) - 1   # trailing 2yr (504 sessions)
def postbull_mult(d0):
    """Block (EW2D_SHRINK) if washout is post-strong-prolonged-bull AND decline still shallow."""
    r = vni_hist["ret2y"].reindex([d0], method="ffill"); dd = vni_hist["dd52"].reindex([d0], method="ffill")
    r2 = float(r.iloc[0]) if len(r) and pd.notna(r.iloc[0]) else np.nan
    d1 = float(dd.iloc[0]) if len(dd) and pd.notna(dd.iloc[0]) else np.nan
    if np.isnan(r2) or np.isnan(d1): return 1.0   # fail-safe: missing history -> no block
    dangerous = (r2 >= POSTBULL_RET2Y_THR) and (d1 > POSTBULL_DD1Y_THR)
    return EW2D_SHRINK if dangerous else 1.0
_r = vni_hist["Close"].pct_change()
vni_hist["rv10"] = _r.rolling(10).std() * np.sqrt(252) * 100
vni_hist["vn_cooling"] = vni_hist["rv10"] <= vni_hist["rv10"].rolling(30).max() * 0.85
def vn_cool_at(d):
    s = vni_hist["vn_cooling"].reindex([d], method="ffill")
    return bool(s.iloc[0]) if len(s) and pd.notna(s.iloc[0]) else False

_ew_cache = {}
def ew_maturity_at(d0):
    """Equal-weight broad-market maturity at d0 (causal 1y window on ticker_prune):
    returns (ew_p25_dd_pct, pct_below_ma200_frac). p25 = the weak-half stock's drawdown from its
    own 52w high; pct_below = share of stocks below MA200 (= reverted below their own mean)."""
    if d0 in _ew_cache: return _ew_cache[d0]
    q = f"""
    WITH win AS (
      SELECT ticker, time, Close, MA200,
        MAX(Close) OVER (PARTITION BY ticker ORDER BY time ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS hi52,
        ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
      FROM tav2_bq.ticker_prune
      WHERE time BETWEEN DATE_SUB(DATE '{d0.date()}', INTERVAL 365 DAY) AND DATE '{d0.date()}')
    SELECT APPROX_QUANTILES(SAFE_DIVIDE(Close,hi52)-1,100)[OFFSET(25)] AS p25_dd,
           AVG(CASE WHEN MA200>0 AND Close<MA200 THEN 1.0 ELSE 0 END) AS pct_below
    FROM win WHERE rn=1 AND Close>0 AND hi52>0"""
    r = bq(q)
    out = (np.nan, np.nan) if r.empty else (float(r["p25_dd"][0])*100, float(r["pct_below"][0]))
    _ew_cache[d0] = out
    return out

def ew2d_mult(d0):
    p25, below = ew_maturity_at(d0)
    if np.isnan(p25) or np.isnan(below): return 1.0   # fail-safe: missing data -> no shrink
    mature = (p25 <= EW2D_P25_THR) and (below >= EW2D_BREADTH_THR)
    return 1.0 if mature else EW2D_SHRINK

ws = br[br["oversold"] >= WASHOUT_GATE].copy().sort_values("time")
capit_events = []
if not USE_CAPIT:
    print("  CAPIT DISABLED (v22base) — sleeves off, books run BAL stack + LAG PEAD + parking only")
if USE_CAPIT and len(ws):
    ws["g"] = ws["time"].diff().dt.days.fillna(999)
    ws["c"] = (ws["g"] >= 30).cumsum()
    for _, grp in ws.groupby("c"):
        d0 = grp.iloc[0]["time"]
        st = int(state_ff.get(d0) or state_by_date.get(d0, 3) or 3)
        di = {dd: i for i, dd in enumerate(vni_dates)}
        i0 = di.get(d0, None)
        grind = False
        if i0 is not None:
            wdays = set(br[br["oversold"] >= WASHOUT_GATE]["time"])
            for back in range(20, 91):
                j = i0 - back
                if j >= 0 and vni_dates[j] in wdays: grind = True; break
        dd_now = float(vni_hist["dd52"].reindex([d0], method="ffill").iloc[0]) if len(vni_hist) else -99.0
        base = capit_base(st, dd_now, vn_cool_at(d0))
        size = base * (0.5 if grind else 1.0)
        # maturity scaling:
        #  smooth/gate15 -> index dd52w, CRISIS only (state 1)
        #  ew2d          -> equal-weight 2-D gate (EW-depth x breadth-below-MA200), ALL states
        if MATURITY == "ew2d":
            mat = ew2d_mult(d0)
            if mat < 1.0:
                p25e, belowe = ew_maturity_at(d0)
                print(f"    [ew2d] {d0.date()} st{st} EW_p25={p25e:.1f}% breadth_below={belowe*100:.0f}% "
                      f"-> trend-not-broken -> size x{mat:.2f} ({size:.2f}->{size*mat:.2f})")
        elif MATURITY == "postbull":
            mat = postbull_mult(d0)
            _r2 = float(vni_hist["ret2y"].reindex([d0], method="ffill").iloc[0])
            if mat < 1.0:
                print(f"    [postbull] {d0.date()} ret2y={_r2*100:+.0f}% dd1y={dd_now:.0f}% "
                      f"-> post-strong-bull + shallow -> size x{mat:.2f} ({size:.2f}->{size*mat:.2f})")
        else:
            mat = maturity_mult(dd_now) if st == 1 else 1.0
            if MATURITY and st == 1 and mat < 1.0:
                print(f"    [maturity:{MATURITY}] {d0.date()} CRISIS dd52={dd_now:.1f}% -> size x{mat:.2f} ({size:.2f}->{size*mat:.2f})")
        size *= mat
        capit_events.append({"date": d0, "state": st, "grind": grind, "size": size, "dd": dd_now,
                             "cool": vn_cool_at(d0)})
        print(f"  washout {d0.date()}: state={st} grind={grind} dd52={dd_now:.1f}% cool={vn_cool_at(d0)} -> size={size:.2f}")

_basket_cache = {}
def capit_basket(d):
    if d in _basket_cache: return _basket_cache[d]
    e = bq(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{d.date()}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")
    if e.empty:
        _basket_cache[d] = []
        return []
    g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
    pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
    pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
    _basket_cache[d] = list(pick["ticker"])
    return _basket_cache[d]

# pre-fetch baskets (also defines extra tickers the LAG book may need prices for)
capit_names_all = set()
for e in capit_events:
    if e["size"] > 0.005:
        capit_names_all |= set(capit_basket(e["date"]))

# ============================================================================
# 4b. LAG-book price panels from BQ (auditable; replaces local pkl panels)
# ============================================================================
lag_universe = sorted({c["ticker"] for c in lag_cand} | capit_names_all)
print(f"\n[4b] Fetching BQ prices for LAG universe ({len(lag_universe)} tickers)...")
_chunks = [lag_universe[i:i+250] for i in range(0, len(lag_universe), 250)]
_parts = []
for ci, ch in enumerate(_chunks):
    in_list = ",".join(f"'{t}'" for t in ch)
    part = bq(f"""SELECT t.ticker, t.time, t.Open, t.Close, t.Volume_3M_P50
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' AND t.ticker IN ({in_list})""")
    assert len(part) < 1_990_000, f"bq() max_rows cap risk (lag prices chunk {ci})"
    _parts.append(part)
    print(f"  chunk {ci+1}/{len(_chunks)}: {len(part):,} rows")
lagpx = pd.concat(_parts, ignore_index=True)
lagpx["time"] = pd.to_datetime(lagpx["time"])
prices_lag, opens_lag, liq_lag = {}, {}, {}
for tk, g in lagpx.groupby("ticker"):
    gc = g[g["Close"].notna()]
    prices_lag[tk] = dict(zip(gc["time"], gc["Close"].astype(float)))
    go = g[g["Open"].notna()]
    opens_lag[tk] = dict(zip(go["time"], go["Open"].astype(float)))
    gl = g[g["Volume_3M_P50"].notna() & g["Close"].notna()]
    for d, adv, px in zip(gl["time"], gl["Volume_3M_P50"].astype(float), gl["Close"].astype(float)):
        liq_lag[(tk, d)] = adv * px
LIQ_LAG = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
           "liquidity_lookup": liq_lag, "exit_slippage_tiered": True}

lag_rows = []
for c in lag_cand:
    tk, sd = c["ticker"], c["sd"]
    px_sd = prices_lag.get(tk, {}).get(sd, np.nan)
    if pd.isna(px_sd) or px_sd <= 0: continue
    lag_rows.append({"time": sd, "ticker": tk,
                     "play_type": "LAG_HI" if c["surprise"] > 0.5 else "LAG_LO",
                     "ta": 400.0, "Close": float(px_sd)})
sig_lag = pd.DataFrame(lag_rows, columns=["time","ticker","play_type","ta","Close"])
print(f"  LAG signals in window: {len(sig_lag)}")
shn.TIER_PRIORITY.update({"LAG_HI": 88, "LAG_LO": 82})
LAG_TW = {"LAG_HI": 0.10, "LAG_LO": 0.08}

# ============================================================================
# 5b. CAPIT arm builder (two-pass, identical to go-live)
# ============================================================================
def add_capit_arm(sig_book, base_nav_df, tw_base, tag, book_prices):
    rows, tw2, tiers = [], dict(tw_base), []
    if not capit_events:
        return sig_book, tw2, {}
    basecash = (base_nav_df.set_index("time")["cash_pct"] / 100.0).clip(lower=0)
    for i, e in enumerate(capit_events):
        if e["size"] <= 0.005: continue
        d = e["date"]
        names = [t for t in capit_basket(d) if t in book_prices and d in book_prices[t]]
        if len(names) < 3: continue
        pos = basecash.index.searchsorted(d)
        cf = float(basecash.iloc[max(0, pos-2):pos+1].mean()) if len(basecash) else 0.0
        wt = e["size"] * max(cf, 0.0)
        if CAPIT_EVENT_CAP is not None and wt > CAPIT_EVENT_CAP:
            print(f"    [cap] {tag} E{i} {e['date'].date()}: wt {wt:.3f} -> {CAPIT_EVENT_CAP:.3f} (per-event cap)")
            wt = CAPIT_EVENT_CAP
        if wt <= 0.005: continue
        pt = f"CAPIT{tag}_E{i}"
        shn.TIER_PRIORITY[pt] = 95
        tw2[pt] = wt / len(names); tiers.append(pt)
        for t in names:
            rows.append({"time": d, "ticker": t, "play_type": pt, "ta": 500.0,
                         "Close": book_prices[t][d]})
    if not tiers:
        return sig_book, tw2, {}
    extra = dict(hold_days_by_tier={t: CAPIT_HOLD for t in tiers},
                 stop_exempt_tiers=set(tiers), slot_exempt_tiers=set(tiers),
                 tier_position_limit={t: 15 for t in tiers})
    return pd.concat([sig_book, pd.DataFrame(rows)], ignore_index=True), tw2, extra

def merge_extra(base_extra, cap_extra):
    if not cap_extra: return dict(base_extra)
    out = dict(base_extra)
    out["hold_days_by_tier"] = {**base_extra.get("hold_days_by_tier", {}), **cap_extra["hold_days_by_tier"]}
    out["stop_exempt_tiers"] = set(base_extra.get("stop_exempt_tiers", set())) | cap_extra["stop_exempt_tiers"]
    out["slot_exempt_tiers"] = cap_extra["slot_exempt_tiers"]
    out["tier_position_limit"] = {**base_extra.get("tier_position_limit", {}), **cap_extra["tier_position_limit"]}
    return out

# ============================================================================
# 6. BOOK A — BAL 25B
# ============================================================================

# === DEEP-DD de-risk parking overlay (research, env-gated) =====================
# Park idle cash into the parking vehicle in CRISIS/BEAR states ONLY on deep-DD days
# (DD52w <= thresh). Implements the quality-deploy hypothesis via the engine's native
# per-date parking override; absent dates fall back to PARK_STATES_DICT ({3:0.7}).
DEEP_DD_PARK = {}
_ddp = os.environ.get("DEEP_DD_PARK","")
if _ddp:
    _add = {int(k): float(v) for k,v in (p.split(":") for p in _ddp.split(","))}
    _thr = float(os.environ.get("DEEP_DD_THRESH","-15"))
    _dd = vni_hist["dd52"]
    for d in vni_dates:
        ts = pd.Timestamp(d); st = state_ff.get(ts)
        if st in (1,2):
            try: ddv = float(_dd.reindex([ts], method="ffill").iloc[0])
            except Exception: ddv = 0.0
            if ddv <= _thr:
                DEEP_DD_PARK[ts] = {**PARK_STATES_DICT, **_add}
    print(f"  [DEEP_DD_PARK] active {len(DEEP_DD_PARK)} deep-DD de-risk days (add {_add}, thr {_thr}%)")
# ==============================================================================
print("\n[6] BOOK A — BAL 25B...")
BAL_KW = dict(allowed_tiers=RS["allowed_tiers"], max_positions=MAX_POS_V11,
              hold_days=45, stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BAL_NAV,
              sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
              sector_cap_exempt_tiers=RS["sector_cap_exempt"],
              tier_weights_by_state=RS["tier_weights_by_state"],
              deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_ff,
              cash_etf_states=PARK_STATES_DICT, cash_etf_states_by_date=DEEP_DD_PARK, vn30_underlying=vn30_underlying,
              etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
              open_prices=open_prices, t1_open_exec=True,
              entry_alt_prices=None,           # AUDIT: BQ-verifiable T+1 Open fills only
              force_close_eod=False, **ETF_LIQ_KW)
if capit_events:
    nav_bal0, _ = simulate(sig_f, prices, vni_dates, tier_weights=RS["tier_weights"],
                           name="v23audit_BAL_base", **BAL_KW, **LIQ_FULL)
    nav_bal0["time"] = pd.to_datetime(nav_bal0["time"])
    sig_balC, tw_balC, ex_balC = add_capit_arm(sig_f, nav_bal0, RS["tier_weights"], "B", prices)
else:
    sig_balC, tw_balC, ex_balC = sig_f, RS["tier_weights"], {}
events_bal, etf_bal = [], []
kwA = dict(BAL_KW); kwA["allowed_tiers"] = list(RS["allowed_tiers"]) + [t for t in tw_balC if t.startswith("CAPIT")]
nav_bal, _ = simulate(sig_balC, prices, vni_dates, tier_weights=tw_balC,
                      event_log=events_bal, etf_log=etf_bal,
                      name="v23audit_BAL", **merge_extra(kwA, ex_balC), **LIQ_FULL)
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
print(f"  BAL events: {len(events_bal)} stock + {len(etf_bal)} ETF; final {nav_bal.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

# ============================================================================
# 7. BOOK B — LAG 25B always-on + parking
# ============================================================================
print("\n[7] BOOK B — LAG 25B (always-on, parked)...")
LAG_KW = dict(allowed_tiers=["LAG_HI","LAG_LO"], max_positions=12,
              hold_days=25, stop_loss=-0.99, min_hold=2, slippage=0.001, init_nav=LAG_NAV,
              stop_exempt_tiers={"LAG_HI","LAG_LO"},
              hold_days_by_tier={"LAG_HI": 25, "LAG_LO": 25},
              tier_position_limit={"LAG_HI": 12, "LAG_LO": 12},
              deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_ff,
              cash_etf_states=PARK_STATES_DICT, cash_etf_states_by_date=DEEP_DD_PARK, vn30_underlying=vn30_underlying,
              etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
              open_prices=opens_lag, t1_open_exec=True, force_close_eod=False, **ETF_LIQ_KW)
if capit_events:
    nav_lag0, _ = simulate(sig_lag, prices_lag, vni_dates, tier_weights=LAG_TW,
                           name="v23audit_LAG_base", **LAG_KW, **LIQ_LAG)
    nav_lag0["time"] = pd.to_datetime(nav_lag0["time"])
    sig_lagC, tw_lagC, ex_lagC = add_capit_arm(sig_lag, nav_lag0, LAG_TW, "L", prices_lag)
else:
    sig_lagC, tw_lagC, ex_lagC = sig_lag, dict(LAG_TW), {}
events_lag, etf_lag = [], []
kwB = dict(LAG_KW); kwB["allowed_tiers"] = ["LAG_HI","LAG_LO"] + [t for t in tw_lagC if t.startswith("CAPIT")]
nav_lag, _ = simulate(sig_lagC, prices_lag, vni_dates, tier_weights=tw_lagC,
                      event_log=events_lag, etf_log=etf_lag,
                      name="v23audit_LAG", **merge_extra(kwB, ex_lagC), **LIQ_LAG)
nav_lag["time"] = pd.to_datetime(nav_lag["time"])
print(f"  LAG events: {len(events_lag)} stock + {len(etf_lag)} ETF; final {nav_lag.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

# ============================================================================
# 8. Allocator overlay (band-only ±10pp) — instrumented for audit
# ============================================================================
print(f"\n[8] Combine books ({'allocator' if USE_LAG_ALLOCATOR else 'static 50/50 sum'})...")
nb = nav_bal.set_index("time"); nl = nav_lag.set_index("time")
common = nb.index.intersection(nl.index)
navb_c = nb["nav"].loc[common]; navl_c = nl["nav"].loc[common]
states_c = [int(state_ff.get(d) or state_by_date.get(d, 3) or 3) for d in common]
rb = navb_c.pct_change().fillna(0.0).values
rl = navl_c.pct_change().fillna(0.0).values
w_tgt_a = np.full(len(common), np.nan); rebal_cost_a = np.zeros(len(common))
n_rebal = 0; rebal_rows = []

# edge-conditional w_LAG target: gate the good-state (3/4/5) LAG tilt by LAG's own causal edge-health
_edge_m12 = None
if USE_EDGE_ALLOC:
    _eh = pd.read_csv(os.path.join(WORKDIR, "data", "lag_edge_health.csv"), parse_dates=["entry"])
    _eh = _eh.drop_duplicates("entry").set_index("entry").sort_index()["mean12"]
    _edge_m12 = _eh.reindex(common, method="ffill")
    print(f"  [edge-alloc] thr={EDGE_THR}%; mean12 latest={_edge_m12.iloc[-1]:.1f}%, "
          f"%time<thr={(_edge_m12 < EDGE_THR).mean()*100:.0f}%")
def w_lag_target(i):
    s = states_c[i]
    if USE_EDGE_ALLOC and s in (3, 4, 5):
        m = _edge_m12.iloc[i]
        return 0.65 if (pd.notna(m) and m >= EDGE_THR) else 0.50
    return STATE_LAG_WEIGHT.get(s, 0.5)

if USE_LAG_ALLOCATOR:
    # V2.3A — state-conditional band-only allocator on the two 25B reference ledgers
    cap_b_a = np.empty(len(common)); cap_l_a = np.empty(len(common))
    w0 = w_lag_target(0)
    cb = (1.0 - w0) * TOTAL_NAV; cl = w0 * TOTAL_NAV
    for i in range(len(common)):
        if i > 0:
            cb *= (1.0 + rb[i]); cl *= (1.0 + rl[i])
        P = cb + cl; w_tgt = w_lag_target(i)
        w_tgt_a[i] = w_tgt
        if P > 0 and abs(cl / P - w_tgt) > ALLOC_REBAL_BAND:
            w_pre = cl / P
            cost = ALLOC_REBAL_TC * abs(w_tgt * P - cl)
            P -= cost
            cl = w_tgt * P; cb = (1.0 - w_tgt) * P; n_rebal += 1
            rebal_cost_a[i] = cost
            rebal_rows.append({"ymd": common[i], "state": states_c[i], "value": cost,
                               "reason": f"w_LAG {w_pre:.4f} -> {w_tgt:.2f} (band ±{ALLOC_REBAL_BAND:.2f})"})
        cap_b_a[i] = cb; cap_l_a[i] = cl
    combined_nav = pd.Series(cap_b_a + cap_l_a, index=common)
    print(f"  {n_rebal} band rebalances; final combined = {combined_nav.iloc[-1]/1e9:.4f}B")
else:
    # V2.3C — static plain-sum: each book runs at its 25B reference, combined = navb + navl.
    # No rebalancing, no friction; cap_bal/cap_lag ARE the raw book NAVs.
    cap_b_a = navb_c.values.copy(); cap_l_a = navl_c.values.copy()
    combined_nav = pd.Series(cap_b_a + cap_l_a, index=common)
    print(f"  static 50/50 sum; final combined = {combined_nav.iloc[-1]/1e9:.4f}B")

# ============================================================================
# 9. Build TX table (stocks + ETF + MTM phantoms), per book
# ============================================================================
print("\n[9] Building TX table + self-checks...")
def annot(events, book):
    if not events: return pd.DataFrame()
    df = pd.DataFrame(events); df["book"] = book
    df["ymd"] = pd.to_datetime(df["ymd"]); return df
def etf_to_tx(etf_evts, book):
    if not etf_evts: return pd.DataFrame()
    d = pd.DataFrame(etf_evts); d["ymd"] = pd.to_datetime(d["ymd"])
    return pd.DataFrame({
        "ymd": d["ymd"], "ticker": PARK_TICKER,
        "action": d["action"].apply(lambda a: "buy" if a == "buy_etf" else "sell"),
        "buy_amount": np.where(d["action"] == "buy_etf", d["amount_vnd"], 0.0),
        "sell_amount": np.where(d["action"] == "sell_etf", d["amount_vnd"], 0.0),
        "fee": d["friction_cost"], "adj_price": d["price_vn30"], "shares": d["shares"],
        "holding_id": d["holding_id"], "play_type": "ETF_PARK",
        "cash_after": d["cash_after"],
        "reason": "ETF_REBAL_state" + d["state"].astype(str), "book": book})

all_tx = pd.concat([annot(events_bal, "BAL"), annot(events_lag, "LAG"),
                    etf_to_tx(etf_bal, "BAL"), etf_to_tx(etf_lag, "LAG")], ignore_index=True)

# MTM phantoms: open positions & ETF lots marked at last session Close (NOT cash events).
# A pending partial-fill residual (filled shares of an order still completing on the last
# session) lives in nav_*_ref via pending_mv but is NOT in open_positions_final (the engine
# only snapshots completed positions). We emit one explicit MTM_PENDING phantom per book so
# the file's own MTM rows fully reconstruct each book's final stocks value.
last_day = common[-1]
mtm_rows = []
for navdf, ndf_idx, book in [(nav_bal, nb, "BAL"), (nav_lag, nl, "LAG")]:
    op = navdf.attrs.get("open_positions_final")
    lots = navdf.attrs.get("etf_lots_final")
    pos_mark_sum = 0.0
    if op is not None and not op.empty:
        for _, p in op.iterrows():
            mv = float(p["mark_value"]); pos_mark_sum += mv
            mtm_rows.append({"ymd": last_day, "ticker": p["ticker"], "action": "sell",
                "buy_amount": 0.0, "sell_amount": mv, "fee": 0.0,
                "adj_price": float(p["last_price"]) if pd.notna(p.get("last_price", np.nan)) else None,
                "shares": float(p["shares"]), "holding_id": p["holding_id"],
                "play_type": p.get("play_type", "?"), "cash_after": None,
                "reason": "MTM_UNREALIZED", "book": book})
    # pending partial-fill residual = stocks_ref(last) - sum(completed position marks)
    stocks_ref_last = float((ndf_idx["positions_mv"] + ndf_idx["pending_mv"]).loc[last_day])
    pending_resid = stocks_ref_last - pos_mark_sum
    if pending_resid > 1.0:
        mtm_rows.append({"ymd": last_day, "ticker": "(pending_partial_fill)", "action": "sell",
            "buy_amount": 0.0, "sell_amount": pending_resid, "fee": 0.0,
            "adj_price": None, "shares": None, "holding_id": f"PENDING_{book}",
            "play_type": "PENDING_FILL", "cash_after": None,
            "reason": "MTM_PENDING_PARTIAL", "book": book})
    if lots is not None and not lots.empty:
        for _, lot in lots.iterrows():
            mtm_rows.append({"ymd": last_day, "ticker": PARK_TICKER, "action": "sell",
                "buy_amount": 0.0, "sell_amount": float(lot["mark_value"]), "fee": 0.0,
                "adj_price": float(lot["last_price"]) if pd.notna(lot["last_price"]) else None,
                "shares": float(lot["shares"]), "holding_id": lot["holding_id"],
                "play_type": "ETF_PARK", "cash_after": None, "reason": "MTM_UNREALIZED", "book": book})
if mtm_rows:
    all_tx = pd.concat([all_tx, pd.DataFrame(mtm_rows)], ignore_index=True)
all_tx = all_tx.sort_values(["ymd", "book", "action", "ticker"]).reset_index(drop=True)

# --- SELF-CHECK 1: per-book daily cash-flow identity (order-independent) ---
# cash(d) - cash(d-1) == sum(sell_amount - fee) - sum(buy_amount + fee) over day d
selfcheck = {}
flows_tx = all_tx[~all_tx["reason"].astype(str).str.startswith("MTM")].copy()
flows_tx["net"] = (flows_tx["sell_amount"] - flows_tx["fee"]).where(
    flows_tx["action"] == "sell", -(flows_tx["buy_amount"] + flows_tx["fee"]))
for book, navdf, init in [("BAL", nb, BAL_NAV), ("LAG", nl, LAG_NAV)]:
    f = flows_tx[flows_tx["book"] == book].groupby("ymd")["net"].sum()
    cash = navdf["cash"].loc[common]
    dcash = cash.diff(); dcash.iloc[0] = cash.iloc[0] - init
    f_full = f.reindex(common).fillna(0.0)
    err = (dcash - f_full).abs().max()
    selfcheck[f"cash_flow_identity_max_err_vnd_{book}"] = float(err)
    # final NAV identity: cash + stocks marks + etf marks == nav
    mtm_sum = sum(r["sell_amount"] for r in mtm_rows if r["book"] == book)
    nav_id_err = abs(float(cash.iloc[-1]) + mtm_sum - float(navdf["nav"].loc[last_day]))
    selfcheck[f"final_nav_identity_err_vnd_{book}"] = nav_id_err
    print(f"  [selfcheck {book}] cash-flow identity max err = {err:,.0f} VND; "
          f"final NAV identity err = {nav_id_err:,.0f} VND")

# --- SELF-CHECK 2: combination recurrence replay ---
if USE_LAG_ALLOCATOR:
    cb2 = (1.0 - w_lag_target(0)) * TOTAL_NAV
    cl2 = w_lag_target(0) * TOTAL_NAV
    for i in range(len(common)):
        if i > 0:
            cb2 *= (1.0 + rb[i]); cl2 *= (1.0 + rl[i])
        P2 = cb2 + cl2; wt = w_lag_target(i)
        if P2 > 0 and abs(cl2 / P2 - wt) > ALLOC_REBAL_BAND:
            P2 -= ALLOC_REBAL_TC * abs(wt * P2 - cl2); cl2 = wt * P2; cb2 = (1.0 - wt) * P2
    alloc_err = abs((cb2 + cl2) - combined_nav.iloc[-1])
else:
    # static: combined must equal navb + navl exactly
    alloc_err = abs(float((navb_c + navl_c).iloc[-1]) - float(combined_nav.iloc[-1]))
selfcheck["combination_replay_err_vnd"] = float(alloc_err)

# ============================================================================
# 10. Metrics
# ============================================================================
def calc_metrics(s):
    s = s.dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    r = s.pct_change().dropna()
    spy = len(r) / yrs
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    sh252 = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    shspy = r.mean() / r.std() * np.sqrt(spy) if r.std() > 0 else 0
    dn = r[r < 0]
    sortino = r.mean() / np.sqrt((dn**2).mean()) * np.sqrt(252) if len(dn) else 0
    peak = s.cummax(); dds = s / peak - 1
    maxdd = dds.min()
    under = dds < -1e-12; mx = cur = 0
    for u in under:
        cur = cur + 1 if u else 0
        mx = max(mx, cur)
    return dict(years=yrs, sessions_per_year=spy, total_ret=s.iloc[-1]/s.iloc[0]-1,
                cagr=cagr, sharpe_252=sh252, sharpe_spy=shspy, sortino_252=sortino,
                max_dd=maxdd, calmar=cagr/abs(maxdd) if maxdd < 0 else 0, dd_dur_sessions=mx)

m_sys = calc_metrics(combined_nav)
vni_s = pd.Series([vni_close_by_date[d] for d in common], index=common, dtype=float)
m_vni = calc_metrics(vni_s / vni_s.iloc[0] * TOTAL_NAV)

print("\n" + "=" * 100)
print(f" {LABEL} AUDIT — FULL {common[0].date()} -> {common[-1].date()} ({m_sys['years']:.2f}y)")
print(f" Final NAV {combined_nav.iloc[-1]/1e9:,.2f}B  CAGR {m_sys['cagr']*100:.2f}%  "
      f"Sharpe(252) {m_sys['sharpe_252']:.2f}  MaxDD {m_sys['max_dd']*100:.1f}%  Calmar {m_sys['calmar']:.2f}")
print(f" VNINDEX B&H: CAGR {m_vni['cagr']*100:.2f}%  Sharpe {m_vni['sharpe_252']:.2f}  MaxDD {m_vni['max_dd']*100:.1f}%")
print("=" * 100)

# ============================================================================
# 11. Assemble ONE audit file
# ============================================================================
print("\n[11] Writing audit file...")
COLS = ["record_type","key","value","ymd","book","ticker","action","play_type","holding_id",
        "shares","adj_price","buy_amount","sell_amount","fee","cash_after","reason","state",
        "nav_bal_ref","nav_lag_ref","bal_cash_ref","bal_stocks_ref","bal_etf_ref",
        "lag_cash_ref","lag_stocks_ref","lag_etf_ref",
        "w_lag_tgt","rebal_cost","cap_bal","cap_lag","combined_nav","vni_close"]

meta = [
 ("system", {"v23a": "V2.3A go-live (= V2.2 BAL|LAG static+park + CAPIT v2 + LAG-allocator band) on DT5G",
             "v23c": "V2.3C champion (= V2.2 BAL|LAG STATIC 50/50 plain-sum + park + CAPIT v2, NO allocator) on DT5G",
             "v22base": "V2.2-base (= BAL|LAG STATIC 50/50 plain-sum + ETF parking, NO CAPIT sleeve, NO allocator) on DT5G"}[MODE]),
 ("mode", MODE + {"v23a": " (allocator band ±10pp, CAPIT on)", "v23c": " (static 50/50 plain-sum, CAPIT on)",
                  "v22base": " (static 50/50 plain-sum, CAPIT OFF)"}[MODE]),
 ("source_script",f"pt_v23_audit_2014.py {MODE} (auditable harness: T+1 Open fills, ALL data from BigQuery; NO intraday alt-fills, NO curated panel)"),
 ("period",f"{common[0].date()} -> {common[-1].date()}"),
 ("init_nav_vnd",f"{int(TOTAL_NAV):,} = BAL {int(BAL_NAV):,} + LAG {int(LAG_NAV):,} (two real single-ledger books)"),
 ("price_source","ALL prices from BigQuery project lithe-record-440915-m9, dataset tav2_bq"),
 ("price_basis","adjusted prices (column Open / Close of tav2_bq.ticker); tolerance note: if a corporate action re-adjusted history after this run, compare RATIOS not absolute levels"),
 ("state_source",f"{STATE_TABLE} (DT5G production market regime, states 1..5 = CRISIS..EX-BULL)"),
 ("execution_rule","signal on session t => entry/exit executed at session t+1 OPEN (t1_open_exec; no look-ahead). MULTI-DAY FILLS: one TX row per fill day, each at that day's Open, capped at 20% of ticker ADV/day, max 5 fill days"),
 ("fee_buy","fee = buy_amount x ((1+0.0015)x(1+slippage_book)-1); slippage_book: BAL=0.0, LAG=0.001"),
 ("fee_sell","fee = sell_amount x (1-(1-0.0015-0.001)x(1-slippage_book)x(1-tier_slip)); tier_slip: 0 if trade<=5% ADV, 0.001 if >5%, 0.003 if >10%, 0.005 if >20% ADV"),
 ("fee_etf","E1VFVN30 parking rebalance friction = 0.15% of amount_vnd per side; ETF priced at tav2_bq.ticker Close of E1VFVN30"),
 ("cash_identity","per book per day: cash(d)-cash(d-1) == SUM over that day's TX of [sell: +(sell_amount-fee) | buy: -(buy_amount+fee)]. cash(d) = bal_cash_ref / lag_cash_ref in DAILY rows. No other cash flows exist (deposit interest = 0, no margin)"),
 ("nav_identity","book NAV ref (nav_bal_ref/nav_lag_ref) = cash_ref + stocks_ref(mark at BQ Close) + etf_ref(mark at E1VFVN30 Close). Positions reconstructable from TX by holding_id (buys add shares, sells remove)"),
 ("mtm_rows","TX rows whose reason starts with MTM are NOT cash events. MTM_UNREALIZED = open stock positions & ETF lots marked at final session Close. MTM_PENDING_PARTIAL = residual market value of an order still completing its multi-day fill on the final session (its filled shares already appear as ENTRY_FILL buys earlier in the TX log; this phantom marks them to the final stocks value). Property: final cash_ref + SUM(all MTM sell_amount) == final book NAV ref, per book"),
 ("combination_rule", (f"V2.3A ALLOCATOR: cap_bal/cap_lag start at (1-w0)/w0 x 50e9 with w0=w_LAG(state day1); each day cap_x *= (1+book ref-NAV daily return); if |cap_lag/(cap_bal+cap_lag) - w_tgt(state)| > {ALLOC_REBAL_BAND} then total -= {ALLOC_REBAL_TC} x |moved capital| and reset to target. w_tgt by state: {STATE_LAG_WEIGHT}. combined_nav = cap_bal + cap_lag"
                       if USE_LAG_ALLOCATOR else
                       "V2.3C STATIC 50/50 plain-sum: each book runs at its own 25e9 reference ledger; combined_nav = nav_bal_ref + nav_lag_ref EXACTLY every day. No rebalancing, no allocator friction. cap_bal/cap_lag columns == nav_bal_ref/nav_lag_ref. w_lag_tgt/rebal_cost are blank")),
 ("combination_note", ("books are independent 25B reference ledgers; the allocator scales their RETURN STREAMS into combined NAV (documented go-live architecture). Verify: (a) each ref ledger from TX, (b) the recurrence from DAILY columns, (c) combined_nav = cap_bal + cap_lag"
                       if USE_LAG_ALLOCATOR else
                       "verify simply: combined_nav == nav_bal_ref + nav_lag_ref for every DAILY row")),
 ("metric_formulas","CAGR=(NAV_end/NAV_0)^(365.25/calendar_days)-1; Sharpe_252=mean(daily ret)/std(daily ret)*sqrt(252); Sortino_252=mean/sqrt(mean(neg_ret^2))*sqrt(252); MaxDD=min(NAV/cummax(NAV)-1); Calmar=CAGR/|MaxDD|; all on DAILY combined_nav"),
 ("verification_procedure","1) sample TX rows: adj_price vs tav2_bq.ticker Open (real buy/sell fills) / Close (E1VFVN30 ETF, and MTM marks) on ymd. NOTE for MTM_UNREALIZED rows: mark price = last available Close ON OR BEFORE the final session (forward-filled) — a ticker that halted trading before the last session is marked at its last real Close (e.g. PXI 700.0 from 2026-06-05), so verify against the most recent Close<=ymd, not Close exactly on ymd; 2) amounts: buy_amount==shares*adj_price, sell_amount==shares*adj_price (MTM_PENDING_PARTIAL has null price/shares — it is an aggregate residual, verify only that it makes the book NAV identity close); 3) fees within documented formulas; 4) rebuild per-book cash by cash_identity, compare bal_cash_ref/lag_cash_ref; 5) rebuild book NAV by nav_identity; 6) replay combination_rule -> combined_nav; 7) recompute metrics from combined_nav; compare with METRIC rows"),
 ("audit_note_fills","ALL fills = T+1 Open (no intraday alt-fills). VERIFIED 2026-06-12 that the published V2.3C 25.77% and V2.3A 26.29% figures were ALSO T+1 Open (scripts pt_v22_capit_v21.py / pt_onewallet_allocator.py: t1_open_exec=True, no entry_alt_prices). So this audit does NOT differ from the published numbers on fills"),
 ("audit_note_datasource","KEY DIFFERENCE vs published numbers: this audit reads ALL data live from tav2_bq.* (prices, opens, liquidity, LAG earnings panel, CAPIT baskets). The published 25.77%/26.29% were computed on a curated local panel data/v4f_panel_2014.csv + hardcoded CAPIT event list. Any gap between this audit and the published figure is attributable to (a) curated-panel vs live-BQ universe/price differences and (b) live-washout vs hardcoded CAPIT events — NOT to execution/fills"),
 ("bal_signal_rule","BAL buys: SIGNAL_V11 tiers (tav2_bq columns), SV_TIGHT release-freshness gate (state 1: <=30d since Release_Date; 2-3: <=60d), overheat & EX-BULL suppression, 8L regime-size (weak names half size in states 1-2); tier weight 10%/name (5% weak), max 12 positions, hold 45 sessions, stop -20%, sector-8 cap 4"),
 ("lag_signal_rule","LAG buys: earnings events with NP_R>=15 AND >=4 prior good events AND decay-weighted prior post-return >=5%; entry at Release_Date+5 sessions (T+1 Open of signal day); hold 25 sessions; no stop; weights LAG_HI 10% (surprise>0.5) / LAG_LO 8%"),
 ("capit_rule",f"washout = >=30% of tav2_bq.ticker_prune with D_RSI<0.3 (events clustered, >=30d gap); sleeve size = state_base x grind_half x book free-cash; state_base: CRISIS 1.0, NEUTRAL 0.75, BULL/EXBULL 0.5, BEAR 0.5 only if dd52w>-25% or domestic vol cooling; basket = quality (ROE_Min5Y>=12%, ROIC5Y>=10%, FSCORE>=6, liq>=2B/day) ranked by PB z-score, max 15 names; hold 60 sessions, stop/slot-exempt"),
 ("etf_parking_rule", f"parking policy {{state:frac}} of (cash+park) parked in {PARK_TICKER} = {PARK_STATES_DICT} (default prod {{3:0.7}} = NEUTRAL-only 70%); sells pre-fill (JIT) if state target drops or cash needed, buys post-fill sweep"),
 ("n_tx_rows", str(len(all_tx))),
 ("n_daily_rows", str(len(common))),
 ("baseline_label", LABEL + "; window FULL 2014->now, calendar-year basis"),
 ("capit_status", "CAPIT sleeve ON (washout-driven crisis buys)" if USE_CAPIT else "CAPIT sleeve OFF (v22base: pure BAL stack + LAG PEAD + ETF parking)"),
 ("capit_event_cap", "none (uncapped: per-event target = state-size x free-cash)" if CAPIT_EVENT_CAP is None else f"{CAPIT_EVENT_CAP:.2f} of book NAV per washout event (structural tail guard; caps the 2022-04-19-type max-free-cash full-size deployment)"),
 ("capit_maturity_rule", "none" if MATURITY is None else (
     f"ew2d: 2-D equal-weight gate (ALL states). Full size only if EW p25 stock dd-from-52w-high <= {EW2D_P25_THR}% AND >= {EW2D_BREADTH_THR:.0%} of ticker_prune below MA200 (broad trend broken / reverted below own mean); else x{EW2D_SHRINK}. Replaces the megacap-masked index lens with equal-weight breadth. In-sample (thresholds set on 18 audit events); NOT walk-forward validated"
     if MATURITY == "ew2d" else
     f"{MATURITY}: in CRISIS (state 1) scale size by index decline depth dd52w — " + ("smooth ramp clip(|dd52w|/20, 0.25, 1.0)" if MATURITY=="smooth" else "1.0 if dd52w<=-15% else 0.30") + ". In-sample (2 loss events / 18), NOT walk-forward validated")),
]
if _IS_CUSTOM:
    _is_pit = ETF_LIQ in ("custompit", "custompitq", "custompitg", "custompitgq")
    _pq, _preb, _pgate = _PIT_PARAMS.get(ETF_LIQ, ("none", "qstart", None))
    _reb_desc = ("first trading day on/after 05-Feb/05-May/05-Aug/05-Nov (post-earnings)" if _preb == "q2m5"
                 else "first trading day of each calendar quarter")
    _recipe = ("STATIC: members = 30 most-liquid ticker_prune names over 2020-01-01..2025-01-01 by "
               "AVG(Volume_3M_P50*Close), ex-VIC/ex-index (hindsight selection)." if not _is_pit else
               f"PIT: rebalance = {_reb_desc}; members = top-30 ticker_prune ex-VIC/ex-index by "
               "PRIOR-completed-quarter AVG(Volume_3M_P50*Close) (no look-ahead)"
               + (f", HARD GATE keep only as-of fa_ratings_8l.rating<={_pgate}" if _pgate is not None else "")
               + (" then 8L quality tilt cap-weight x QTILT[rating]{1:1.5,2:1.25,3:1.0,4:0.7,5:0.4}"
                  if _pq == "tilt" else " (pure cap-weight)") + "; membership in CUSTOM_MEMBERS rows below.")
    meta += [
     ("parking_vehicle", f"{PARK_TICKER} — synthetic ex-VIC basket (NOT E1VFVN30). Parking TX/MTM rows use "
                         f"ticker '{PARK_TICKER}'; verify adj_price against CUSTOM_BASKET levels (or rebuild from BQ)"),
     ("custom_basket_mode", ETF_LIQ + (" (PIT membership)" if _is_pit else " (static hindsight membership)")),
     ("custom_basket_pit_params", f"quality={_pq} rebal={_preb} gate_rating={_pgate} weight_scheme={BASKET_WT} top_n={BASKET_TOPN} name_cap={BASKET_NAMECAP}" if _is_pit else "n/a"),
     ("custom_basket_members", ",".join(CUSTOM_MEMBERS) + ("" if not _is_pit else "  [UNION across quarters; see CUSTOM_MEMBERS rows for per-quarter]")),
     ("custom_basket_recipe", _recipe + " Per name per day: mcap = adjusted Close (tav2_bq.ticker) * OShares "
                              "(tav2_bq.ticker_financial as-of/ffilled). Daily return = SUM(w*mcap_t)/SUM(w*mcap_{t-1})-1 "
                              "over active-membership names valid BOTH days (chained); level=1000*cumprod(1+ret). "
                              "ADV cap = 20% of 60d-rolling SUM(Price*Volume) of active members. "
                              "Reproduced by custom_basket.py " + ("build_pit()" if _is_pit else "build()")),
     ("custom_basket_capacity_note", "creation-equivalent: parking capped at 20% of the basket's own aggregate "
                                     "trading value (~100x E1VFVN30 secondary). ex-VIC = controlled beta"),
    ]
meta_df = pd.DataFrame([{"record_type":"META","key":k,"value":v} for k,v in meta])

basket_df = pd.DataFrame()
if _IS_CUSTOM and CUSTOM_LEVEL:
    basket_df = pd.DataFrame([{"record_type": "CUSTOM_BASKET", "ymd": t, "ticker": PARK_TICKER,
                               "value": lv} for t, lv in sorted(CUSTOM_LEVEL.items())])

members_rec_df = pd.DataFrame()
if CUSTOM_MEMBERS_DF is not None and not CUSTOM_MEMBERS_DF.empty:
    members_rec_df = CUSTOM_MEMBERS_DF.rename(columns={"ticker": "ticker"}).copy()
    members_rec_df.insert(0, "record_type", "CUSTOM_MEMBERS")
    members_rec_df["ymd"] = members_rec_df["rebal_date"]
    members_rec_df["value"] = members_rec_df["qmult"]
    members_rec_df["reason"] = ("rating=" + members_rec_df["rating"].astype(str)
                                + " liq_rank=" + members_rec_df["liq_rank"].astype(str)
                                + " quarter=" + members_rec_df["quarter"].astype(str))
    members_rec_df = members_rec_df[["record_type", "ymd", "ticker", "value", "reason"]]

ev_df = pd.DataFrame([{"record_type":"EVENT_CAPIT","ymd":e["date"],"state":e["state"],
                       "value":e["size"],
                       "reason":f"grind={e['grind']} dd52w={e['dd']:.1f}% cool={e['cool']}"}
                      for e in capit_events])

tx_df = all_tx.copy(); tx_df.insert(0, "record_type", "TX")

rb_df = pd.DataFrame(rebal_rows)
if not rb_df.empty: rb_df.insert(0, "record_type", "REBAL")

daily_df = pd.DataFrame({
    "record_type": "DAILY", "ymd": common,
    "state": [state_ff.get(d) for d in common],
    "nav_bal_ref": navb_c.values, "nav_lag_ref": navl_c.values,
    "bal_cash_ref": nb["cash"].loc[common].values,
    "bal_stocks_ref": (nb["positions_mv"] + nb["pending_mv"]).loc[common].values,
    "bal_etf_ref": nb["cash_etf"].loc[common].values,
    "lag_cash_ref": nl["cash"].loc[common].values,
    "lag_stocks_ref": (nl["positions_mv"] + nl["pending_mv"]).loc[common].values,
    "lag_etf_ref": nl["cash_etf"].loc[common].values,
    "w_lag_tgt": w_tgt_a, "rebal_cost": rebal_cost_a,
    "cap_bal": cap_b_a, "cap_lag": cap_l_a, "combined_nav": combined_nav.values,
    "vni_close": [vni_close_by_date.get(d, np.nan) for d in common],
})

annual_rows = []
yr_idx = pd.Series(combined_nav.values, index=common)
for yr in sorted({d.year for d in common}):
    s_y = yr_idx[yr_idx.index.year == yr]
    v_y = vni_s[vni_s.index.year == yr]
    if len(s_y) < 2: continue
    annual_rows.append({"record_type":"ANNUAL","key":str(yr),
                        "value": s_y.iloc[-1]/s_y.iloc[0]-1,
                        "reason": f"vni={v_y.iloc[-1]/v_y.iloc[0]-1:+.4f}"})
annual_df = pd.DataFrame(annual_rows)

metric_rows = [("final_nav_vnd", combined_nav.iloc[-1]),
               ("init_nav_vnd", TOTAL_NAV),
               ("final_nav_bal_ref_vnd", float(navb_c.iloc[-1])),
               ("final_nav_lag_ref_vnd", float(navl_c.iloc[-1])),
               ("n_allocator_rebalances", n_rebal),
               ("n_capit_events_fired", sum(1 for e in capit_events if e["size"] > 0.005))]
metric_rows += [(k, v) for k, v in m_sys.items()]
metric_rows += [("vni_bh_" + k, v) for k, v in m_vni.items()]
metric_rows += list(selfcheck.items())
metric_df = pd.DataFrame([{"record_type":"METRIC","key":k,"value":v} for k,v in metric_rows])

audit = pd.concat([meta_df, ev_df, tx_df, rb_df, daily_df, annual_df, metric_df, basket_df, members_rec_df],
                  ignore_index=True).reindex(columns=COLS)
os.makedirs(os.path.join(WORKDIR, "data"), exist_ok=True)
audit.to_csv(AUDIT_PATH, index=False, encoding="utf-8")
print(f"  -> {AUDIT_PATH}  ({len(audit):,} rows)")

print("\nANNUAL (sys vs VNINDEX):")
for r in annual_rows:
    print(f"  {r['key']}: {r['value']:+.2%}   ({r['reason']})")
print("\nDone.")
