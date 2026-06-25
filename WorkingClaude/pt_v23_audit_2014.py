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
from deposit_rate_vn import DEPOSIT_EVENTS
from signal_v11_sql import SIGNAL_V11
from pt_dates import detect_end_date

START_DATE  = os.environ.get("AUDIT_START", "2014-01-02")  # override via env for windowed audits
_START_TAG  = "" if START_DATE == "2014-01-02" else "_from" + START_DATE.replace("-", "")
STATE_TABLE = "tav2_bq.vnindex_5state_dt5g_live"
END_DATE    = os.environ.get("AUDIT_END") or detect_end_date()  # AUDIT_END pins the data snapshot (reproducible)
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
assert MODE in ("v23a", "v23c", "v22base", "singlebook"), "MODE must be v23a | v23c | v22base | singlebook"
# singlebook (2026-06-20): ONE book = gated custom30 basket (no momentum/PEAD) + CAPIT on idle cash.
# custom30 exposure via cash_etf_states=SB_GATE (DT5G 5-state, no EXBULL leverage); idle cash (crisis/bear/
# neutral) auto-feeds the CAPIT arm (golden deep-value bottom-fish). Reuses the verified per-name engine.
IS_SINGLEBOOK = (MODE == "singlebook")
USE_LAG_ALLOCATOR = (MODE == "v23a")
USE_CAPIT = (MODE != "v22base") and (not IS_SINGLEBOOK or os.environ.get("SB_CAPIT", "1") == "1")
SB_GATE = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.0}   # single-book DT5G exposure (no EXBULL leverage)
if IS_SINGLEBOOK:
    BAL_NAV = TOTAL_NAV; LAG_NAV = 1.0   # LAG inert (1 VND, empty PEAD) -> static-sum combine = single book
# Optional per-event CAPIT deployment cap (fraction of book NAV). argv[2], e.g. 0.15 or 0.20.
# Structural fix for the 2022-04-19 tail: no single washout event may target more than CAP of the
# book, regardless of free-cash x state-size. None = uncapped (original sizing).
def _argf(i):  # parse float-or-"none"/"off" positional
    if len(sys.argv) > i and sys.argv[i].lower() not in ("none", "off", "-"):
        return sys.argv[i]
    return None
CAPIT_EVENT_CAP = float(_argf(2)) if _argf(2) is not None else None
# Exp-2 (Taylor 2026-06-24): hold CAPIT until state returns to >= NEUTRAL instead of fixed 60td.
CAPIT_HOLD_NEUTRAL = os.environ.get("CAPIT_HOLD_NEUTRAL", "0") == "1"
# CAPIT universe (env, 2026-06-16): "golden" (prod) = deep pb_z<-1 + strict-quality from ticker_prune;
# "custom30" = user reframe (liquid custom30 + pb_z<CAPIT_PBZ). Measured IN V2.3 production here (vs the
# isolated V4-faithful harness). Default golden = byte-identical production.
CAPIT_UNIV = os.environ.get("CAPIT_UNIV", "golden").lower()
CAPIT_PBZ  = float(os.environ.get("CAPIT_PBZ", "0"))
CAPIT_STOP = float(os.environ["CAPIT_STOP"]) if os.environ.get("CAPIT_STOP") else None  # e.g. -0.12 = cutloss capit
if CAPIT_UNIV == "custom30":
    _c30 = pd.read_csv(os.path.join(WORKDIR, "data", "custom30_membership.csv"), parse_dates=["effective_from", "effective_to"])
    _c30["effective_to"] = _c30["effective_to"].fillna(pd.Timestamp("2100-01-01"))
    _c30_iv = {tk: list(zip(g.effective_from.values, g.effective_to.values)) for tk, g in _c30.groupby("ticker")}
    def _c30_asof(d):
        dd = np.datetime64(d)
        return [tk for tk, ivs in _c30_iv.items() if any(f <= dd < t for f, t in ivs)]
# C — golden-overflow (user 2026-06-17): in a SAFE BEAR washout (state 2, NOT postbull) where the golden
# basket is thin (deal-scarcity -> capit capital would otherwise sit at 0% since BEAR isn't parked),
# AUGMENT the thin golden set with LIQUID custom30V (golden first, then V) so the size deploys instead of
# being skipped. Env-gated; default OFF = production byte-identical. macro guard = state==BEAR (not CRISIS;
# a bad-macro washout would already be capped to CRISIS by DT5G) AND postbull_mult>=1 (not post-bull).
CAPIT_BEAR_OVERFLOW = os.environ.get("CAPIT_BEAR_OVERFLOW", "0") == "1"
CAPIT_OVERFLOW_MIN  = int(os.environ.get("CAPIT_OVERFLOW_MIN", "8"))   # golden < this names -> overflow
CAPIT_OVERFLOW_N    = int(os.environ.get("CAPIT_OVERFLOW_N", "15"))    # cap total capit names after overflow
# C — HARD GATES (user 2026-06-18). Branch-C overflow is OOS-concentrated (IS -1.07pp / OOS +3.77pp) and
# the 2008 GFC event-study shows pb_z<-1 -> -16.4% in a SYSTEMIC crash (cheap-gets-cheaper in the FIRST
# leg). Two hard gates make overflow safe-by-construction: it fires ONLY on a MATURE capitulation, never
# on a shallow first-leg bear (the 2008 trap):
#   Gate 1 (deep-dd + breadth-broken): VNINDEX dd52w <= CAPIT_OVERFLOW_DD (default -20%) AND the broad
#           market trend is broken (ew2d maturity: weak-half p25 <= EW2D_P25_THR AND >= EW2D_BREADTH_THR
#           below MA200). Requires the washout to be DEEP and the trend mean-reverted, not first-leg.
#   Gate 2 (postbull): postbull_mult(d) >= 1.0 (already enforced) — don't buy a washout right after a
#           strong prolonged bull while still near the top (2007->2008, 2021->2022).
# Default ON when CAPIT_BEAR_OVERFLOW=1 (the gates are the whole point); set to "0"/loose thr to ablate.
CAPIT_OVERFLOW_DD     = float(os.environ.get("CAPIT_OVERFLOW_DD", "-20.0"))   # VNINDEX dd52w floor (deep)
CAPIT_OVERFLOW_MATURE = os.environ.get("CAPIT_OVERFLOW_MATURE", "1") == "1"   # require breadth-broken trend
_c30v_iv = None
def _c30v_asof(d):
    global _c30v_iv
    if _c30v_iv is None:
        _v = bq("SELECT ticker, effective_from, effective_to FROM tav2_bq.custom30v_8l")
        _v["effective_from"] = pd.to_datetime(_v["effective_from"])
        _v["effective_to"]   = pd.to_datetime(_v["effective_to"]).fillna(pd.Timestamp("2100-01-01"))
        _c30v_iv = {tk: list(zip(g.effective_from.values, g.effective_to.values)) for tk, g in _v.groupby("ticker")}
    dd = np.datetime64(d)
    return [tk for tk, ivs in _c30v_iv.items() if any(f <= dd < t for f, t in ivs)]
# Depth-sizing (user 2026-06-17): scale capit deployment by the basket's pb_z DEPTH. Event-study on 68k
# stress-obs / 9y: forward-2M return rises MONOTONICALLY with pb_z depth (pbz>0 -> -4%, -1 -> +7%,
# <-2.5 -> +23%) -> deploy bigger when deeper. Robust SHAPE (whole sample), not a fitted point. Env-gated.
CAPIT_DEPTH_SIZING = os.environ.get("CAPIT_DEPTH_SIZING", "0") == "1"
_basket_pbz_cache = {}
def _depth_mult(pbz):
    if pbz is None or not (pbz == pbz): return 1.0          # NaN -> neutral
    return float(np.clip(-pbz / 1.5, 0.5, 1.5))             # pbz=-1.5->1.0, -0.75->0.5, <=-2.25->1.5 cap
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
if IS_SINGLEBOOK:
    PARK_STATES_DICT = dict(SB_GATE)   # the gated custom30 IS the single-book exposure
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
# Quality-TILT strength sweep (env BASKET_QTILT, dir B 2026-06-16). Only affects custompitgq
# (quality=tilt). Presets or explicit "1:1.5,2:1.25,..."; "default" = module QTILT (None passthrough).
_QTILT_PRESETS = {"default": None, "off": {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0},
                  "gentle":  {1: 1.2, 2: 1.1, 3: 1.0, 4: 0.7, 5: 0.4},
                  "strong":  {1: 2.0, 2: 1.4, 3: 1.0, 4: 0.5, 5: 0.25}}
_qt_raw = os.environ.get("BASKET_QTILT", "default").lower()
if _qt_raw in _QTILT_PRESETS:
    BASKET_QTILT = _QTILT_PRESETS[_qt_raw]; _qt_tag = "" if _qt_raw == "default" else f"_qt{_qt_raw}"
else:
    BASKET_QTILT = {int(k): float(v) for k, v in (kv.split(":") for kv in _qt_raw.split(","))}
    _qt_tag = "_qtcustom"
_capsuf = "" if CAPIT_EVENT_CAP is None else f"_cap{int(round(CAPIT_EVENT_CAP*100))}"
_matsuf = "" if MATURITY is None else (f"_mat{MATURITY}" + (f"_shrink{int(round(EW2D_SHRINK*100))}" if MATURITY in ("ew2d", "postbull") and abs(EW2D_SHRINK - 0.30) > 1e-9 else ""))
_matsuf += "_edge" if USE_EDGE_ALLOC else ""
_matsuf += "_holdneutral" if CAPIT_HOLD_NEUTRAL else ""
LABEL = {"v23a": "V2.3A (allocator + CAPIT)",
         "v23c": "V2.3C (static 50/50 + CAPIT)",
         "v22base": "V2.2-base (static 50/50, NO CAPIT)",
         "singlebook": "SINGLE-BOOK (gated custom30 + CAPIT-on-idle)"}.get(MODE, MODE) \
        + (f" + per-event cap {int(round(CAPIT_EVENT_CAP*100))}%" if CAPIT_EVENT_CAP else "") \
        + (f" + maturity:{MATURITY}" if MATURITY else "") \
        + (f" + edge-cond-allocator(thr{EDGE_THR:.0f}%)" if USE_EDGE_ALLOC else "") \
        + (" + hold-neutral(capit)" if CAPIT_HOLD_NEUTRAL else "")
# Conditional BULL-PARK (mechanism test 2026-06-20): deploy idle cash into the parking basket (custom30V)
# in BULL/EXBULL ONLY when breadth is BROAD (>= thr), soft-tapered by index extension (VNI/MA200). Env-gated,
# default OFF -> cash_etf_states_by_date=None -> byte-identical to production. WHAT/WHEN study (item 21):
# value dominates bull (custom30V vehicle), no robust danger-timer -> simple breadth gate + gentle ext-taper.
BULL_PARK_COND    = os.environ.get("BULL_PARK_COND", "0") == "1"
BULL_PARK_BREADTH = float(os.environ.get("BULL_PARK_BREADTH", "0.60"))   # min % above MA200 = broad
BULL_PARK_FRAC    = float(os.environ.get("BULL_PARK_FRAC", "0.70"))      # max park frac in bull
BULL_PARK_EXT_LO  = float(os.environ.get("BULL_PARK_EXT_LO", "0.10"))    # ext<=lo -> full; ext>=hi -> 0 (soft-taper)
BULL_PARK_EXT_HI  = float(os.environ.get("BULL_PARK_EXT_HI", "0.30"))
_bullpark_tag = "" if not BULL_PARK_COND else f"_bullpark{int(BULL_PARK_BREADTH*100)}f{int(BULL_PARK_FRAC*100)}"
_c30b_tag = "" if os.environ.get("BULL_VEHICLE_C30B", "0") != "1" else f"_c30bfl{os.environ.get('C30B_FLOOR','5')}"
# RECOVERY-PARK (Taylor 2026-06-22): deploy idle cash into the custom30V parking vehicle in CRISIS/BEAR
# ONLY when the market is GENUINELY cheap vs 5Y history (median liquid-universe pb_z deep-negative),
# depth-scaled (bet bigger the cheaper). pb_z-vs-own-history is the falling-knife filter (rejected the
# Jun-2022 "cheap-vs-peak but expensive-vs-history" bounce; fired at COVID). Env-gated, default OFF ->
# cash_etf_states_by_date=None -> byte-identical to production R3. wmax<=1.0 = idle-cash only (no margin).
RECOVERY_PARK      = os.environ.get("RECOVERY_PARK", "0") == "1"
RECOVERY_PBZ_START = float(os.environ.get("RECOVERY_PBZ_START", "-0.3"))   # begin scaling at this cheapness
RECOVERY_PBZ_DEEP  = float(os.environ.get("RECOVERY_PBZ_DEEP", "-0.7"))    # full deploy at/below this
RECOVERY_WMAX      = float(os.environ.get("RECOVERY_WMAX", "1.0"))         # max park frac (<=1.0 = no margin)
# DEPOSIT-GATE (Taylor 2026-06-23): money-condition multiplier m on the recovery deploy. m=clip((CEIL-dep)/
# (CEIL-FLOOR),0,1). High deposit (tight money, big cash opp-cost) -> m->0 -> hold cash even if pb_z cheap;
# learned from the 2011-extension (deploying into 2012's 14%-deposit crisis LOST to cash). FLOOR=7.5 (dormant)
# = no change to 2014-26 (deposit never >7.5% in that era), pure forward insurance; FLOOR=6 (active) trims the
# 2022 SCB-hike deploy. Default ON when RECOVERY_PARK; set RECOVERY_DEP_GATE=0 to disable (pre-gate behaviour).
RECOVERY_DEP_GATE  = os.environ.get("RECOVERY_DEP_GATE", "1") == "1"
RECOVERY_DEP_FLOOR = float(os.environ.get("RECOVERY_DEP_FLOOR", "0.075"))  # deposit at/below -> deploy fully (m=1)
RECOVERY_DEP_CEIL  = float(os.environ.get("RECOVERY_DEP_CEIL",  "0.12"))   # deposit at/above -> no deploy (m=0)
# GATE MODE (Taylor 2026-06-23): "deposit" = deposit-LEVEL gate (above); "fed" = market Fed-spread gate =
# (1/VNINDEX_PE) - deposit (earnings yield vs cash). Fed is a RICHER money-van: captures BOTH stock cheapness
# AND the cash hurdle in one number (user's '1/PE thi truong vs lai gui'); VNINDEX_PE sane back to 2006 (only
# per-stock t.PE is corrupt). Fed is dormant in 2014-26 too (every fire window spread >= +1.8% > ceil) but
# smarter in a future crisis (deploys if stocks are cheap-enough even at moderately high rates).
RECOVERY_GATE_MODE = os.environ.get("RECOVERY_GATE_MODE", "deposit")       # "deposit" | "fed"
RECOVERY_FED_FLOOR = float(os.environ.get("RECOVERY_FED_FLOOR", "0.0"))    # spread at/below -> no deploy (m=0)
RECOVERY_FED_CEIL  = float(os.environ.get("RECOVERY_FED_CEIL",  "0.015"))  # spread at/above -> deploy fully (m=1)
_gate_on = RECOVERY_PARK and RECOVERY_DEP_GATE
_depg_tag = "" if not _gate_on else (f"_fedg{int(RECOVERY_FED_CEIL*1000)}" if RECOVERY_GATE_MODE == "fed"
                                     else f"_depg{int(RECOVERY_DEP_FLOOR*1000)}")
# REAL-MARGIN branch (Taylor 2026-06-23): unlike recovery-park (idle-cash only, gross<=100%), this lets the
# CAPIT deep-washout arm borrow up to (MGE-1)*NAV (real leverage, cash<0, charged borrow_annual=10%/yr). The
# borrow room is restricted to CAPIT plays (MGE_CAPIT_ONLY) so leverage lands ONLY in deep-cheap washouts, NOT
# in normal/EXBULL buys (matches the thesis + trading_rules deep_cheap_recovery_override). 0/<=1 = OFF (leverage-
# free, the go-live default). The CAPIT washout size gets a borrow headroom on top of its cash-based size.
BORROW_ANNUAL  = float(os.environ.get("BORROW_ANNUAL", "0.10"))         # margin borrow rate (era-aware override)
MGE            = float(os.environ.get("MGE", "0"))                         # gross cap, e.g. 1.3 / 1.5; <=1 = off
MGE_CAPIT_ONLY = os.environ.get("MGE_CAPIT_ONLY", "1") == "1"              # borrow room usable ONLY by CAPIT plays
# FORCE_REAL_LEVER (Taylor 2026-06-25): the default MGE_CAPIT_ONLY adds a fixed (MGE-1) borrow HEADROOM on top of a
# cash-funded slug — but in a washout the book is cash-rich (other arms sold off), so that headroom almost never
# binds (prior audit: combined gross maxed 0.995@1.3 / 0.966@1.5, borrow ~0 VND). To MEASURE the true cost of real
# >100% leverage we must FORCE it: when FORCE_REAL_LEVER=1, scale the WHOLE cash-funded CAPIT slug by the MGE
# multiple (wt = cash_slug × (1+(MGE-1)×lgm)) so it deploys MGE× the free cash → cash goes negative → genuine gross
# >100% → real borrow charged at borrow_annual. Excess = max(0, gross-1)×NAV pays borrow/252 each day (engine).
FORCE_REAL_LEVER = os.environ.get("FORCE_REAL_LEVER", "0") == "1"          # force genuine >100% gross (real borrow)
# S4 MARGIN-CALL (Taylor 2026-06-25, margin engine rebuild): force-deleverage when live gross breaches
# MGE_HARD mid-hold (price drop) — the missing risk primitive a real margin account has. Default OFF.
MARGIN_CALL = os.environ.get("MARGIN_CALL", "0") == "1"                    # enable S4 force-deleverage
MGE_HARD    = float(os.environ.get("MGE_HARD", "0"))                       # breach trigger; 0 => cap+0.15 (engine default)
MGE_FLOOR   = float(os.environ.get("MGE_FLOOR", "0"))                      # post-call target; 0 => cap (engine default)
mc_log_bal, mc_log_lag = [], []
_mge = MGE if MGE > 1.0 else None
_mge_tag = "" if not _mge else f"_mge{int(round(MGE*100))}{'cap' if MGE_CAPIT_ONLY else 'all'}{'_real' if FORCE_REAL_LEVER else ''}"
# Part-2 LEVER-GATE (gates ONLY the borrow headroom of the CAPIT arm; the cash-based size is untouched):
#   none      -> borrow headroom always full (current behaviour)
#   deposit   -> scale headroom by deposit money-condition m=clip((CEIL-dep)/(CEIL-FLOOR))  (reuses RECOVERY_DEP_*)
#   fedborrow -> scale by CARRY vs the BORROW rate: mf=clip((eyield-borrow-FLOOR)/(CEIL-FLOOR)). Stands aside when
#                the market earnings-yield (1/VNINDEX_PE) does NOT beat the borrow cost -> e.g. COVID-3/2020
#                (eyield ~9.7% < borrow 10%) -> NO lever there -> avoids the -32.5% 1.5x tail. fail-CLOSED if PE NA.
MGE_GATE      = os.environ.get("MGE_GATE", "none").lower()                 # none | deposit | fedborrow | deposit_eyield | conviction
MGE_FED_FLOOR = float(os.environ.get("MGE_FED_FLOOR", "0.0"))              # eyield-borrow spread floor (m=0 at/below)
MGE_FED_CEIL  = float(os.environ.get("MGE_FED_CEIL", "0.02"))              # spread at/above -> full lever (m=1)
# deposit_eyield gate (Exp-3 Taylor 2026-06-24): gate lever by carry vs DEPOSIT (not BORROW).
# m = clip((eyield-deposit-FLOOR)/(CEIL-FLOOR), 0, 1). Eyield(1/PE_market) 5.9-7.7% > deposit 3-6% in most
# 2014-26 washout episodes -> gate fires more than fedborrow (vs borrow 10% which never fires post-2014).
# Uses same FLOOR/CEIL as fedborrow for spread (MGE_FED_FLOOR / MGE_FED_CEIL). Fail-closed if PE NA.
# conviction gate (Taylor 2026-06-24): lever ONLY when all 3 simultaneously: DT5G state=CRISIS(1) +
# postbull_clear (postbull_mult>=1.0, i.e. not a post-bull shallow drawdown) + US Pillar B OFF (VIX<=35
# AND spx_dd_1y>=-25%). Logic: VN-specific crash that is NOT US contagion AND not a post-bull trap =>
# highest-conviction recovery setup. Loaded from us_market_history.csv (causal: T-1 VN alignment).
_mge_gate_m   = (lambda dd: 1.0)                                           # placeholder; real fn set in recovery block
assert MGE_GATE in ("none", "deposit", "fedborrow", "deposit_eyield", "conviction"), f"MGE_GATE must be none|deposit|fedborrow|deposit_eyield|conviction, got {MGE_GATE!r}"
# DEEP-VALUE POSTBULL OVERRIDE (Taylor 2026-06-24, Exp-5b): when MATURITY=="postbull" zeroes a CAPIT
# event because the market is post-strong-bull + shallow decline, but the UNIVERSE is genuinely CHEAP
# (median liquid-universe pb_z deep-negative), override the postbull guard and restore normal size.
# Hypothesis: postbull guard correctly filters momentum-overhang washouts, but wrongly blocks 2022-type
# events where the market corrected AND got cheap vs 5Y history (pb_z deeply negative = genuine value).
# Implementation: post-pass on capit_events AFTER _pbz_asof() is available (requires RECOVERY_PARK=1
# so the pb_z monthly median data is already loaded).
# DEEP_VALUE_PBZ=-1.0 = strict (only fire when pb_z < -1.0, well below 5Y median PB)
# DEEP_VALUE_PBZ=-0.8 = slightly less strict
# DEEP_VALUE_PBZ=-99  = OFF (default, never fires)
DEEP_VALUE_PBZ = float(os.environ.get("DEEP_VALUE_PBZ", "-99"))  # default OFF
# RECOVERY-GRADUAL V2 (Taylor 2026-06-24, Exp-6): instead of instant full-deploy when pb_z ≤ start,
# spread entry over RECOVERY_DAYS trading days (accumulation campaign), then allow a volume capitulation
# event to trigger full-remaining deploy early.
# Design:
#   • Episode starts when (CRISIS/BEAR + pb_z ≤ PBZ_START) first fires.
#   • Each day: frac += target_frac / RECOVERY_DAYS  (capped at target_frac).
#   • If vol_ratio (VNINDEX Volume / rolling-21d mean, causal T-1) ≥ CAPIT_VOL: snap to target_frac.
#   • RECOVERY_LEVER_ON_CAPIT=1: on capitulation day, use MGE wmax instead of RECOVERY_WMAX.
#   • Episode ends (resets) when state exits CRISIS/BEAR OR pb_z rises above PBZ_START.
# Calibration note: vol_ratio peaks at COVID=1.65x, 2022=1.91x, 2018=1.83x, 2016=1.91x (21d rolling).
# CAPIT_VOL=1.6 catches all major crashes. 2.0+ misses COVID and 2022 entirely.
RECOVERY_GRADUAL      = os.environ.get("RECOVERY_GRADUAL", "0") == "1"      # default OFF
RECOVERY_DAYS         = int(os.environ.get("RECOVERY_DAYS", "10"))           # days to spread entry
RECOVERY_CAPIT_VOL    = float(os.environ.get("RECOVERY_CAPIT_VOL", "1.6"))  # vol_ratio threshold
RECOVERY_LEVER_ON_CAPIT = os.environ.get("RECOVERY_LEVER_ON_CAPIT", "0") == "1"  # use MGE wmax on capit
# CAPIT-ONLY mode (Taylor 2026-06-24, Exp-8): NO instant-deploy, NO gradual accumulation. The recovery-park
# parking stays at 0 (base) until a volume CAPITULATION spike vs a 3M/6M baseline fires, then snaps to FULL
# target on T+1 and HOLDS until reset. Reuses the gradual state machine but disables the daily step and the
# accel/gradual episode-start (episode enters ONLY on a capit fire). RECOVERY_CAPIT_BASE = rolling-mean window
# for the vol_ratio denominator (63 = ~3M, 126 = ~6M) instead of the 21d used by RECOVERY_GRADUAL.
# Calibrated (Exp-8 Step1): threshold 1.7x catches all 6 crises (COVID/2022/2018/2016/2023/2025) at BOTH
# BASE=63 (fires 2.7% of days, P97) and BASE=126 (4.3%, P97). 1.8x starts missing 2016+2023.
RECOVERY_CAPIT_ONLY = os.environ.get("RECOVERY_CAPIT_ONLY", "0") == "1"     # default OFF
RECOVERY_CAPIT_BASE = int(os.environ.get("RECOVERY_CAPIT_BASE", "63"))      # vol_ratio baseline window (63|126)
# Exp-8 REVISED (Mike exp8-revised): expand the CAPIT-ONLY trigger beyond vol-spike (Signal A) to VNINDEX
# technical reversal signals. ANY enabled signal firing (inside the CRISIS/BEAR + pb_z gate) -> full deploy:
#   Signal B (RECOVERY_SIG_B): RSI oversold-reversal — D_RSI_VNINDEX<0.30 for >=3 consecutive days AND turning
#                              up (D_RSI[T] > D_RSI[T-3] + 0.02). Rare & precise (lands at capitulation bottom).
#   Signal C (RECOVERY_SIG_C): RSI bullish-divergence — in a 10d window Close[T] is a new low but D_RSI[T] >
#                              D_RSI at the prior in-window Close-low. Earlier but noisier (high false-positive).
# D_RSI_VNINDEX pulled from BQ (VNINDEX row, 0-1 scale, full coverage 2011+). Causal: all use T / T-3 / trailing.
RECOVERY_SIG_B = os.environ.get("RECOVERY_SIG_B", "0") == "1"
RECOVERY_SIG_C = os.environ.get("RECOVERY_SIG_C", "0") == "1"
# Signal-C as a CONFIRM (not a standalone trigger): A/B deploy only if C armed within the last K sessions.
# C arm = "bottom approaching" (RSI recovering + price flat after a washout); A = capitulation confirm. This
# de-risks A's worst failure (firing leveraged too early in a slow L-grind, e.g. 2012: A-only −166d → A∧C −4d).
RECOVERY_C_CONFIRM = os.environ.get("RECOVERY_C_CONFIRM", "0") == "1"
RECOVERY_C_ARM_K   = int(os.environ.get("RECOVERY_C_ARM_K", "30"))
# LEVER-AT-BOTTOM (Exp-8 v3, user 2026-06-25): on each A∧C-confirm deploy (a confirmed capitulation bottom),
# ALSO buy custom30 on REAL margin — a dedicated CAPITLEV stock sleeve sized to RECOVERY_LEVER_FRAC of NAV,
# funded by borrow (parking already used the cash). Routed through the CAPIT-stock margin path (the V2-proven
# 0-VND-reconciling path) — NOT the parking-margin path (which double-charges interest on cash_etf). Borrow is
# restricted to this sleeve via MGE_CAPIT_ONLY, so leverage lands ONLY at confirmed bottoms, never at the top.
RECOVERY_LEVER_BOTTOM = os.environ.get("RECOVERY_LEVER_BOTTOM", "0") == "1"
RECOVERY_LEVER_FRAC   = float(os.environ.get("RECOVERY_LEVER_FRAC", "0.30"))   # borrowed stock weight per bottom
_lever_dates = []   # filled by the recovery state machine on each A∧C-confirm fire
if RECOVERY_CAPIT_ONLY:
    RECOVERY_GRADUAL = True   # CAPIT-ONLY runs ON the gradual machine (vol load + episode loop), step disabled
# ACCELERATING-DECLINE FILTER (Taylor 2026-06-24, Exp-7):
# Gate the GRADUAL campaign start on an "accelerating decline" signal:
#   dd_5d  = Close[T-1] / Close[T-6]  - 1   (5-day return, fully causal T-1)
#   dd_10d = Close[T-1] / Close[T-11] - 1   (10-day return)
#   accel_ok = (dd_5d < -0.03) OR (dd_5d < dd_10d * 0.6)
# Meaning: 5-day decline >= 3% ("falling fast"), OR recent 5d pace > 1.67x the 10d pace (accelerating).
# When RECOVERY_ACCEL=1:
#   - Gradual campaign STARTS only when CRISIS/BEAR + pb_z ≤ PBZ_START AND accel_ok
#   - Volume capit trigger fires regardless of accel_ok (capit override = deploy instantly even if no campaign yet)
#   - If capit fires before accel_ok (e.g., sudden spike before accelerating decline), it's still caught
# Default OFF: byte-identical to RECOVERY_GRADUAL=1 behaviour.
RECOVERY_ACCEL = os.environ.get("RECOVERY_ACCEL", "0") == "1"
_accel_tag = "_accel" if (RECOVERY_PARK and RECOVERY_GRADUAL and RECOVERY_ACCEL) else ""
_grad_tag = ("" if not (RECOVERY_PARK and RECOVERY_GRADUAL) else
             (f"_capitonly{RECOVERY_CAPIT_BASE}cv{int(RECOVERY_CAPIT_VOL*10)}" if RECOVERY_CAPIT_ONLY else
              f"_grad{RECOVERY_DAYS}cv{int(RECOVERY_CAPIT_VOL*10)}") +
             ("B" if RECOVERY_SIG_B else "") +
             (("Ccf%d" % RECOVERY_C_ARM_K if RECOVERY_C_CONFIRM else "C") if RECOVERY_SIG_C else "") +
             ("lev" if RECOVERY_LEVER_ON_CAPIT else "") + _accel_tag)
if _mge and MGE_GATE != "none":
    if MGE_GATE in ("fedborrow", "deposit_eyield"):
        _mge_tag += "_lg" + ("depeye%d" % int(MGE_FED_CEIL*1000) if MGE_GATE == "deposit_eyield"
                             else "fed%d" % int(MGE_FED_CEIL*1000))
    elif MGE_GATE == "conviction":
        _mge_tag += "_lgconv"
    else:
        _mge_tag += "_lgdep"
_recpark_tag = "" if not RECOVERY_PARK else f"_recpark{int(RECOVERY_WMAX*100)}z{int(abs(RECOVERY_PBZ_DEEP)*100)}{_depg_tag}"
_recpark_tag = _recpark_tag + _mge_tag
_dvo_tag = "" if DEEP_VALUE_PBZ <= -90 else f"_dvo{int(abs(DEEP_VALUE_PBZ)*10)}"
_recpark_tag = _recpark_tag + _dvo_tag + _grad_tag
AUDIT_PATH  = os.path.join(WORKDIR, "data",
                           {"v23a": "v23_golive_audit_2014_now.csv",
                            "v23c": "v23c_golive_audit_2014_now.csv",
                            "v22base": "v22base_audit_2014_now.csv",
                            "singlebook": "singlebook_audit_2014_now.csv"}.get(MODE, MODE+"_audit.csv").replace(".csv", _capsuf + _matsuf + _liqsuf + _park_tag + _wt_tag + _sz_tag + _qt_tag + _bullpark_tag + _c30b_tag + _recpark_tag + _NAV_TAG + _START_TAG + ".csv"))

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                 "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO",
                 "RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
MAX_POS_V11 = 12

STATE_LAG_WEIGHT  = {1: 0.50, 2: 0.00, 3: 0.65, 4: 0.65, 5: 0.65}
ALLOC_REBAL_TC    = 0.001
ALLOC_REBAL_BAND  = 0.10

WASHOUT_GATE = 0.30
CAPIT_HOLD   = int(os.environ.get("CAPIT_HOLD", "60"))   # Part-2: raise to hold levered custom30V to the rebalance cycle
# CAPIT_HOLD_NEUTRAL defined early (before _matsuf) near CAPIT_EVENT_CAP; see Exp-2 note there.
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

# ---- BAL CFO-yield SELECTION BLEND (env BAL_CFO_BLEND; default 0 = byte-identical baseline) ----
# Validated standalone 2026-06-16 (bal_cfo_yield_audit.py): nudging momentum picks toward high CFO-yield
# (1/PCF) lifts Calmar 0.79->0.98 (value cushions momentum blowups). Here we re-test it IN the full book
# (BAL+LAG+allocator) to check the edge survives net (not double-counted by the LAG value leg).
# Mechanism: additive nudge to `ta` (the engine's within-tier SORT key) by per-day CFO-yield rank among
# buyable momentum rows. ta scale/thresholds preserved (the >=120 D1-override at line 282 already ran).
BAL_CFO_BLEND = float(os.environ.get("BAL_CFO_BLEND", "0"))
_BAL_YM = os.environ.get("BAL_YIELD_METRIC", "pcf").lower()   # "pe" = stable earnings yield (preferred)
if BAL_CFO_BLEND > 0:
    _pcf = pd.read_csv(os.path.join(WORKDIR, "data", "bal_open_pcf.csv"), parse_dates=["time"])
    _ycol = "PE" if _BAL_YM == "pe" else "PCF"
    _pcf["cfo"] = np.where(_pcf[_ycol] > 0, 1.0/_pcf[_ycol], np.nan)
    sig_f = sig_f.merge(_pcf[["ticker", "time", "cfo"]], on=["ticker", "time"], how="left")
    _buy = (sig_f["play_type"].str.contains("MOMENTUM", na=False)
            | sig_f["play_type"].isin(["DEEP_VALUE_RECOVERY", "MEGA", "RE_BACKLOG_BUY"]))
    sig_f["_cfor"] = np.nan
    sig_f.loc[_buy, "_cfor"] = sig_f.loc[_buy].groupby("time")["cfo"].rank(pct=True)
    sig_f["_cfor"] = sig_f["_cfor"].fillna(0.5)
    sig_f.loc[_buy, "ta"] = sig_f.loc[_buy, "ta"] + BAL_CFO_BLEND * 40.0 * (sig_f.loc[_buy, "_cfor"] - 0.5)
    sig_f = sig_f.drop(columns=["cfo", "_cfor"])
    print(f"  [BAL yield-blend metric={_BAL_YM}] λ={BAL_CFO_BLEND}: nudged ta of {int(_buy.sum())} buyable momentum rows")

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
                                                       top_n=BASKET_TOPN, name_cap=BASKET_NAMECAP,
                                                       qtilt=BASKET_QTILT)
            CUSTOM_MEMBERS_DF = _memdf
            CUSTOM_MEMBERS = sorted(_memdf["ticker"].unique())
            print(f"  [ETF-LIQ {ETF_LIQ}] ex-VIC PIT basket (quality={_q}, rebal={_reb}, gate={_gate}, weight={BASKET_WT}): "
                  f"{_memdf['rebal_date'].nunique()} rebals, {len(CUSTOM_MEMBERS)} union names, "
                  f"avg {_memdf.groupby('rebal_date')['ticker'].count().mean():.0f}/rebal")
        vn30_underlying = _lvl_d           # parking vehicle = synthetic basket level series
        CUSTOM_LEVEL = _lvl_d
        etf_adv_lookup = _adv_d
        # BULL VEHICLE = custom30B (env BULL_VEHICLE_C30B=1, default OFF -> byte-identical). The parking
        # vehicle becomes custom30B (pemom 1/PE+mom, liq-floor C30B_FLOOR B, namecap) ON bull/exbull days
        # (state 4/5), custom30V on neutral days. Splice the DAILY RETURN (cumprod -> continuous level, so
        # held-lot MTM is the active vehicle's return each day, no transition jump). ADV also spliced so the
        # 20%-ADV parking cap is enforced on custom30B's (thinner) liquidity in bull. (research 2026-06-20)
        if os.environ.get("BULL_VEHICLE_C30B", "0") == "1":
            _envB = {"BASKET_SELECT": "pemom", "BASKET_LIQ_FLOOR_B": os.environ.get("C30B_FLOOR", "5"),
                     "BASKET_MOM_W": os.environ.get("C30B_MOM", "1.0")}
            _saveB = {k: os.environ.get(k) for k in _envB}
            os.environ.update({k: str(v) for k, v in _envB.items()})
            _qB, _rebB, _gateB = _PIT_PARAMS[ETF_LIQ]
            _lvlB, _advB, _memB, _bxB = cb.build_pit(bq, START_DATE, END_DATE, quality=_qB, rebal=_rebB,
                                                     gate_rating=_gateB, weight_scheme=BASKET_WT, top_n=BASKET_TOPN,
                                                     name_cap=BASKET_NAMECAP, qtilt=BASKET_QTILT)
            for k, v in _saveB.items():
                if v is None: os.environ.pop(k, None)
                else: os.environ[k] = v
            _sV = pd.Series(_lvl_d).sort_index(); _sB = pd.Series(_lvlB).reindex(_sV.index)
            _isbull = pd.Series([state_by_date.get(d) in (4, 5) for d in _sV.index], index=_sV.index)
            _r = _sV.pct_change().where(~_isbull, _sB.pct_change()).fillna(0.0)
            _spl = (1 + _r).cumprod() * float(_sV.iloc[0])
            vn30_underlying = _spl.to_dict(); CUSTOM_LEVEL = vn30_underlying
            for _d, _av in _advB.items():
                if state_by_date.get(_d) in (4, 5): etf_adv_lookup[_d] = _av
            print(f"  [BULL VEHICLE] custom30B spliced on bull/exbull days (pemom, floor={_envB['BASKET_LIQ_FLOOR_B']}B, "
                  f"mom={_envB['BASKET_MOM_W']}); {len(sorted(_memB['ticker'].unique()))} c30B union names")
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
# --- LAG quality + forensic gate (2026-06-20, validated lag_forensic_audit) ---
# (1) non-op filter: NP jump where NPM>>EBITM = profit from non-operating/one-off (not a real PEAD
#     beat) -> underperforms clean ~1pp, 9/13yr (worse in BEAR/CRISIS). (2) forensic gate: drop
#     human-flagged related-party/fraud (date-aware, no hindsight). Peak-earnings is NOT filtered:
#     LAG monetizes peak via drift (audit: peak median HIGHER in NEUTRAL/BULL/EXBULL).
_LAG_NONOP = os.environ.get("LAG_NONOP_FILTER", "0") == "1"   # OFF: audit showed +0.44pp CAGR but -2.2pp MaxDD (concentration); not robust
_LAG_FOR  = os.environ.get("LAG_FORENSIC_GATE", "1") == "1"   # ON: forward insurance vs riding confirmed fraud/related-party
_qm = bq("SELECT f.ticker,f.quarter,f.NPM_P0,f.EBITM_P0 FROM tav2_bq.ticker_financial f WHERE f.quarter IS NOT NULL")
ev = ev.merge(_qm, on=["ticker","quarter"], how="left")
ev["_nonop"] = (ev["NPM_P0"] > 1.2 * ev["EBITM_P0"]) & ev["EBITM_P0"].notna()
_forx = {}
try:
    _ff = pd.read_csv("data/forensic_flags.csv")
    _forx = {r["ticker"]: pd.Timestamp(r["date"]) for _, r in _ff.iterrows() if str(r["severity"]).strip() == "exclude"}
except Exception: pass
ev["_forbid"] = [(tk in _forx) and (rd >= _forx[tk]) for tk, rd in zip(ev["ticker"], ev["Release_Date"])]
_m = (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)
if _LAG_NONOP: _m &= ~ev["_nonop"]
if _LAG_FOR:   _m &= ~ev["_forbid"]
e_hl3 = ev[_m].copy()
print(f"  [LAG gate] non_op={_LAG_NONOP} forensic={_LAG_FOR} -> {len(e_hl3)} entries "
      f"(dropped {int((~_m & (ev['NP_R']>=15)&(ev['prior_n_good']>=4)&(ev['pa_HL3']>=5)).sum())} by gates)")

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
        size_premat = size   # save pre-maturity size for deep-value override post-pass
        size *= mat
        capit_events.append({"date": d0, "state": st, "grind": grind, "size": size, "dd": dd_now,
                             "cool": vn_cool_at(d0), "_size_premat": size_premat, "_mat": mat})
        print(f"  washout {d0.date()}: state={st} grind={grind} dd52={dd_now:.1f}% cool={vn_cool_at(d0)} -> size={size:.2f}")

_basket_cache = {}
def capit_basket(d):
    if d in _basket_cache: return _basket_cache[d]
    if CAPIT_UNIV == "custom30":
        mems = _c30_asof(d)
        if not mems:
            _basket_cache[d] = []; return []
        in_list = ",".join(f"'{t}'" for t in mems)
        e = bq(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p WHERE p.time = DATE '{d.date()}' AND p.ticker IN ({in_list})""")
        if e.empty:
            _basket_cache[d] = []; return []
        pick = e[e["pbz"] < CAPIT_PBZ]                       # 'cheap enough' within the liquid custom30 set
        pick = pick.nsmallest(20, "pbz") if len(pick) > 20 else pick
        _basket_cache[d] = list(pick["ticker"]); return _basket_cache[d]
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
    golden = list(pick["ticker"])
    _final_pbz = pick.set_index("ticker")["pbz"]            # pb_z of selected names (for depth-sizing)
    # C v2 — UNIFIED pb_z scale (user 2026-06-17): in a SAFE bear (state 2, NOT postbull) where golden is
    # thin, merge golden + liquid custom30V universe under ONE pb_z ranking (regime-correct: BEAR axis is
    # pb_z=cheap-vs-history, NOT yield) and pick the cheapest. pb_z<0 floor on the liquid join (only join
    # genuinely cheap names). Golden keeps its pb_z. Env CAPIT_BEAR_OVERFLOW; default OFF.
    if CAPIT_BEAR_OVERFLOW and len(golden) < CAPIT_OVERFLOW_MIN:
        st = int(state_ff.get(d) or state_by_date.get(d, 3) or 3)
        # HARD GATES — only deploy into a MATURE capitulation (block the 2008 first-leg trap):
        #   G1a deep-dd: VNINDEX dd52w <= CAPIT_OVERFLOW_DD ; G1b breadth-broken: ew2d maturity OK
        #   G2  postbull: postbull_mult >= 1.0 (not near a post-strong-bull top)
        _ddx = float(vni_hist["dd52"].reindex([d], method="ffill").iloc[0]) if len(vni_hist) else 0.0
        _deep = _ddx <= CAPIT_OVERFLOW_DD
        _mature = (ew2d_mult(d) >= 1.0) if CAPIT_OVERFLOW_MATURE else True
        if st == 2 and postbull_mult(d) >= 1.0 and _deep and _mature:
            print(f"    [C-overflow] {d.date()} GATES PASS: dd52={_ddx:.0f}% (<= {CAPIT_OVERFLOW_DD:.0f}) "
                  f"mature={_mature} postbull_ok=True golden={len(golden)}")
            vmems = _c30v_asof(d)
            if vmems:
                in_v = ",".join(f"'{t}'" for t in vmems)
                ev = bq(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p WHERE p.time = DATE '{d.date()}' AND p.ticker IN ({in_v})""")
                ev = ev[ev["pbz"] < 0]                                  # liquid join only if genuinely cheap
                merged = pd.concat([pick[["ticker", "pbz"]], ev[["ticker", "pbz"]]]).drop_duplicates("ticker")
                merged = merged.nsmallest(CAPIT_OVERFLOW_N, "pbz")                   # one unified pb_z scale
                golden = list(merged["ticker"]); _final_pbz = merged.set_index("ticker")["pbz"]
    _basket_cache[d] = golden
    _basket_pbz_cache[d] = float(_final_pbz.reindex(golden).median()) if golden else np.nan
    return golden

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
def _sessions_to_neutral(d0):
    """Return number of trading sessions from d0 until first session with state >= 3 (NEUTRAL).
    Floor=10 (T+3 buffer), ceiling=CAPIT_HOLD (fallback if no NEUTRAL found in remaining history)."""
    try:
        i0 = vni_dates.index(d0)
    except ValueError:
        return CAPIT_HOLD
    for j in range(i0 + 1, len(vni_dates)):
        if int(state_ff.get(vni_dates[j], 1) or 1) >= 3:
            hold = j - i0
            return max(hold, 10)   # floor: never less than 10 sessions
    return CAPIT_HOLD              # no NEUTRAL found -> fall back to fixed hold

def add_capit_arm(sig_book, base_nav_df, tw_base, tag, book_prices):
    rows, tw2, tiers = [], dict(tw_base), []
    tier_hold = {}    # per-tier hold days (only populated when CAPIT_HOLD_NEUTRAL)
    if not capit_events:
        return sig_book, tw2, {}
    basecash = (base_nav_df.set_index("time")["cash_pct"] / 100.0).clip(lower=0)
    for i, e in enumerate(capit_events):
        if e["size"] <= 0.005: continue
        d = e["date"]
        names = [t for t in capit_basket(d) if t in book_prices and d in book_prices[t]]
        if len(names) < 3: continue
        if e.get("lever"):                                  # LEVER-AT-BOTTOM: fixed borrowed stock weight
            wt = RECOVERY_LEVER_FRAC                         # parking already used the cash -> this draws cash<0
            pt = f"CAPITLEV{tag}_E{i}"
            shn.TIER_PRIORITY[pt] = 96
            tw2[pt] = wt / len(names); tiers.append(pt)
            for t in names:
                rows.append({"time": d, "ticker": t, "play_type": pt, "ta": 500.0, "Close": book_prices[t][d]})
            if CAPIT_HOLD_NEUTRAL:
                tier_hold[pt] = _sessions_to_neutral(d)
            continue
        pos = basecash.index.searchsorted(d)
        cf = float(basecash.iloc[max(0, pos-2):pos+1].mean()) if len(basecash) else 0.0
        wt = e["size"] * max(cf, 0.0)
        if CAPIT_DEPTH_SIZING:                              # scale by basket pb_z depth (deeper=bigger)
            _dm = _depth_mult(_basket_pbz_cache.get(d))
            wt *= _dm
        if CAPIT_EVENT_CAP is not None and wt > CAPIT_EVENT_CAP:
            print(f"    [cap] {tag} E{i} {e['date'].date()}: wt {wt:.3f} -> {CAPIT_EVENT_CAP:.3f} (per-event cap)")
            wt = CAPIT_EVENT_CAP
        if _mge and MGE_CAPIT_ONLY and FORCE_REAL_LEVER:    # FORCE genuine >100%: scale the WHOLE cash slug by MGE
            _lgm = _mge_gate_m(d)
            _mult = 1.0 + (_mge - 1.0) * _lgm               # e.g. 1.3 at lgm=1 -> deploy 1.3x the free-cash slug
            _wt_pre = wt
            wt = wt * _mult                                 # excess (wt-cash) funded by real borrow in the engine
            print(f"    [force-real-lever {tag}] E{i} {d.date()}: m={_lgm:.2f} wt {_wt_pre:.3f} -> {wt:.3f} (x{_mult:.2f})")
        elif _mge and MGE_CAPIT_ONLY:                       # real-margin: borrow headroom ON TOP (deep-washout only)
            _lgm = _mge_gate_m(d)                           # Part-2 lever-gate (deposit / fed-vs-borrow / conviction / none)
            _head = e["size"] * (_mge - 1.0) * _lgm         # scale borrow with washout conviction AND money-condition
            if MGE_GATE == "conviction":
                _st_cv  = int(state_ff.get(d) or state_by_date.get(d, 3) or 3)
                _pb_cv  = _pillar_b_asof(d)
                _pbc_cv = (postbull_mult(d) >= 1.0)
                _reason = ("LEVER" if _lgm > 0 else
                           ("state not CRISIS" if _st_cv != 1 else
                            ("postbull blocked" if not _pbc_cv else "Pillar B active")))
                print(f"    [lever-gate conviction] {tag} E{i} {d.date()}: "
                      f"state={_st_cv} postbull_clear={_pbc_cv} pillar_b={_pb_cv} "
                      f"m={_lgm:.1f} head={e['size']*(_mge-1.0):.3f}->{_head:.3f} => {_reason}")
            elif MGE_GATE != "none":
                print(f"    [lever-gate {MGE_GATE}] {tag} E{i} {d.date()}: m={_lgm:.2f} "
                      f"head {e['size']*(_mge-1.0):.3f} -> {_head:.3f}")
            wt += _head
        if wt <= 0.005: continue
        pt = f"CAPIT{tag}_E{i}"
        shn.TIER_PRIORITY[pt] = 95
        tw2[pt] = wt / len(names); tiers.append(pt)
        for t in names:
            rows.append({"time": d, "ticker": t, "play_type": pt, "ta": 500.0,
                         "Close": book_prices[t][d]})
        # Exp-2: per-event hold until state >= NEUTRAL (different for each event)
        if CAPIT_HOLD_NEUTRAL:
            hd = _sessions_to_neutral(d)
            tier_hold[pt] = hd
            print(f"    [hold-neutral] {tag} E{i} {d.date()}: hold={hd}td (fixed={CAPIT_HOLD}td)")
    if not tiers:
        return sig_book, tw2, {}
    hold_map = tier_hold if CAPIT_HOLD_NEUTRAL else {t: CAPIT_HOLD for t in tiers}
    extra = dict(hold_days_by_tier=hold_map,
                 stop_exempt_tiers=set(tiers), slot_exempt_tiers=set(tiers),
                 tier_position_limit={t: 15 for t in tiers})
    if CAPIT_STOP is not None:                          # cutloss for capit (liquid custom30 can exit; golden can't)
        extra["stop_by_tier"] = {t: CAPIT_STOP for t in tiers}
    return pd.concat([sig_book, pd.DataFrame(rows)], ignore_index=True), tw2, extra

def merge_extra(base_extra, cap_extra):
    if not cap_extra: return dict(base_extra)
    out = dict(base_extra)
    out["hold_days_by_tier"] = {**base_extra.get("hold_days_by_tier", {}), **cap_extra["hold_days_by_tier"]}
    out["stop_exempt_tiers"] = set(base_extra.get("stop_exempt_tiers", set())) | cap_extra["stop_exempt_tiers"]
    out["slot_exempt_tiers"] = cap_extra["slot_exempt_tiers"]
    out["tier_position_limit"] = {**base_extra.get("tier_position_limit", {}), **cap_extra["tier_position_limit"]}
    if "stop_by_tier" in cap_extra:
        out["stop_by_tier"] = {**base_extra.get("stop_by_tier", {}), **cap_extra["stop_by_tier"]}
    return out

# ============================================================================
# 6. BOOK A — BAL 25B
# ============================================================================
if IS_SINGLEBOOK:
    # ONE book = gated custom30 (via cash_etf_states=SB_GATE) + CAPIT on idle; NO momentum/PEAD picks.
    sig_f = sig_f.iloc[0:0].copy()                 # empty momentum signal -> book holds only parking + capit
    sig_lag = sig_lag.iloc[0:0].copy()             # empty PEAD; LAG_NAV=0 so the LAG book is inert
    print(f"  [singlebook] BAL_NAV={BAL_NAV/1e9:.0f}B custom30-gated {SB_GATE} + CAPIT={'ON' if USE_CAPIT else 'OFF'}; momentum/PEAD OFF")
print("\n[6] BOOK A — BAL 25B...")
# Conditional bull-park per-date parking override (mechanism test; None when OFF -> identical to prod)
BULL_PARK_BY_DATE = None
if BULL_PARK_COND:
    _bd = bq(f"""SELECT t.time, AVG(CASE WHEN t.MA200>0 AND t.Close<t.MA200 THEN 0.0 ELSE 1.0 END) AS bd
FROM tav2_bq.ticker_prune AS t WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' AND t.MA200>0
GROUP BY t.time""")
    _bd["time"] = pd.to_datetime(_bd["time"]); _breadth = _bd.set_index("time")["bd"].sort_index()
    _vf = vni_full.set_index("time"); _ext = (_vf["Close"] / _vf["MA200"] - 1.0).sort_index()
    BULL_PARK_BY_DATE = {}; _nfire = 0
    for d in vni_dates:
        base = dict(PARK_STATES_DICT); st = int(state_ff.get(d) or 3)
        if st in (4, 5):
            _b = _breadth.reindex([d], method="ffill"); bb = float(_b.iloc[0]) if len(_b) and pd.notna(_b.iloc[0]) else 0.0
            if bb >= BULL_PARK_BREADTH:
                _e = _ext.reindex([d], method="ffill"); ee = float(_e.iloc[0]) if len(_e) and pd.notna(_e.iloc[0]) else 0.0
                taper = float(np.clip((BULL_PARK_EXT_HI - ee) / (BULL_PARK_EXT_HI - BULL_PARK_EXT_LO), 0.0, 1.0))
                frac = BULL_PARK_FRAC * taper
                if frac > 0.01: base[st] = frac; _nfire += 1
        BULL_PARK_BY_DATE[d] = base
    print(f"  [bull-park] ON breadth>={BULL_PARK_BREADTH} frac{BULL_PARK_FRAC} ext-taper[{BULL_PARK_EXT_LO},{BULL_PARK_EXT_HI}] -> {_nfire} bull-days deploy")
# RECOVERY-PARK per-date override: extend parking into CRISIS/BEAR when GENUINELY cheap (median pb_z deep),
# depth-scaled. Causal: uses PRIOR completed month's median pb_z (no look-ahead). Merges onto BULL_PARK
# (recovery handles states 1/2, bull handles 4/5 -> compatible). OFF -> None -> byte-identical to prod.
RECOVERY_PARK_BY_DATE = None
if RECOVERY_PARK:
    _mc = bq(f"""SELECT FORMAT_DATE('%Y-%m', t.time) ym,
      APPROX_QUANTILES(SAFE_DIVIDE(t.PB - t.PB_MA5Y, NULLIF(t.PB_SD5Y,0)), 2)[OFFSET(1)] AS med_pbz
    FROM tav2_bq.ticker_prune AS t WHERE t.PB_SD5Y>0 AND t.Trading_Value_1M_P50>3e9
      AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' GROUP BY ym""")
    _pbz_m = {r["ym"]: r["med_pbz"] for _, r in _mc.iterrows()}
    def _pbz_asof(dd):
        pm = (pd.Timestamp(dd).to_period("M") - 1).strftime("%Y-%m")   # prior completed month (causal)
        return _pbz_m.get(pm, np.nan)
    # deposit-gate: causal deposit rate as-of date d (ffill from announced DEPOSIT_EVENTS, no look-ahead)
    _dep_evt = sorted((pd.Timestamp(dt), v / 100.0) for dt, v in DEPOSIT_EVENTS)
    def _dep_asof(dd):
        dd = pd.Timestamp(dd); rate = _dep_evt[0][1]
        for t, v in _dep_evt:
            if t <= dd: rate = v
            else: break
        return rate
    # fed-gate: causal prior-month market earnings yield (1/VNINDEX_PE); VNINDEX_PE sane back to 2006
    _eym = {}
    if RECOVERY_GATE_MODE == "fed" or MGE_GATE in ("fedborrow", "deposit_eyield"):
        _pe = bq(f"""SELECT FORMAT_DATE('%Y-%m', t.time) ym, ANY_VALUE(t.VNINDEX_PE) vpe
          FROM tav2_bq.ticker_prune AS t WHERE t.VNINDEX_PE>0
          AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' GROUP BY ym""")
        _eym = {r["ym"]: (1.0 / r["vpe"]) for _, r in _pe.iterrows() if r["vpe"] and r["vpe"] > 0}
    def _eyield_asof(dd):
        pm = (pd.Timestamp(dd).to_period("M") - 1).strftime("%Y-%m")   # prior completed month (causal)
        return _eym.get(pm, np.nan)
    def _dep_m(dd):
        if not RECOVERY_DEP_GATE: return 1.0
        if RECOVERY_GATE_MODE == "fed":
            ey = _eyield_asof(dd)
            if pd.isna(ey): return 1.0                                 # fail-open if PE missing
            spread = ey - _dep_asof(dd)
            return float(np.clip((spread - RECOVERY_FED_FLOOR) /
                                 (RECOVERY_FED_CEIL - RECOVERY_FED_FLOOR), 0.0, 1.0))
        return float(np.clip((RECOVERY_DEP_CEIL - _dep_asof(dd)) /
                             (RECOVERY_DEP_CEIL - RECOVERY_DEP_FLOOR), 0.0, 1.0))
    # conviction gate: US Pillar B lookup (causal: T-1 VN alignment, same as macro_state_live.py).
    # VIX > 35 OR spx_dd_1y < -0.25 => Pillar B active => block lever.
    # us_market_history.csv: T-1 aligned (the US close from the prior calendar day, already present).
    _us_pb = {}
    if MGE_GATE == "conviction":
        _usm = pd.read_csv(os.path.join(WORKDIR, "data", "us_market_history.csv"), parse_dates=["time"])
        _usm = _usm.sort_values("time").reset_index(drop=True)
        # Build T-1 aligned lookup: for each VN date d, use the most recent US row with time < d (T-1 causal)
        _us_dates = _usm["time"].values
        _us_vix   = _usm["vix"].values
        _us_spxdd = _usm["spx_dd_1y"].values
        for _vnd in vni_dates:
            _vnd_np = np.datetime64(_vnd)
            _idx = np.searchsorted(_us_dates, _vnd_np, side="left") - 1   # last US row strictly before VN date
            if _idx < 0:
                _us_pb[_vnd] = True    # no US data -> fail-CLOSED (block lever)
            else:
                _v = float(_us_vix[_idx]) if not np.isnan(float(_us_vix[_idx])) else 0.0
                _d = float(_us_spxdd[_idx]) if not np.isnan(float(_us_spxdd[_idx])) else 0.0
                _us_pb[_vnd] = (_v > 35.0) or (_d < -0.25)
        _npb_active = sum(1 for v in _us_pb.values() if v)
        print(f"  [conviction-gate] US Pillar B loaded: {_npb_active}/{len(_us_pb)} VN dates have Pillar B active "
              f"(VIX>35 or SPX-dd1y<-25%)")
    def _pillar_b_asof(dd):
        """Return True if US Pillar B active on VN date dd (causal T-1). fail-CLOSED if no data."""
        dd = pd.Timestamp(dd)
        if dd in _us_pb: return _us_pb[dd]
        # fallback: find nearest prior key
        keys = sorted(k for k in _us_pb if k <= dd)
        return _us_pb[keys[-1]] if keys else True
    # Part-2 lever-gate fn (gates the CAPIT borrow headroom). deposit reuses the dep money-condition;
    # fedborrow compares the market earnings-yield against the BORROW cost (not deposit);
    # deposit_eyield (Exp-3) compares eyield vs DEPOSIT rate instead — fires whenever stocks yield >
    # deposit (more episodes than fedborrow, all post-2014 washout windows should qualify).
    # conviction (Taylor 2026-06-24): binary gate — m=1.0 only when CRISIS + postbull_clear + Pillar B off.
    def _mge_gate_m(dd):
        if MGE_GATE == "deposit":
            return float(np.clip((RECOVERY_DEP_CEIL - _dep_asof(dd)) /
                                 (RECOVERY_DEP_CEIL - RECOVERY_DEP_FLOOR), 0.0, 1.0))
        if MGE_GATE == "fedborrow":
            ey = _eyield_asof(dd)
            if pd.isna(ey): return 0.0                                 # fail-CLOSED: never borrow blind
            spread = ey - BORROW_ANNUAL                                # carry vs the borrow rate
            return float(np.clip((spread - MGE_FED_FLOOR) /
                                 (MGE_FED_CEIL - MGE_FED_FLOOR), 0.0, 1.0))
        if MGE_GATE == "deposit_eyield":
            ey = _eyield_asof(dd)
            if pd.isna(ey): return 0.0                                 # fail-CLOSED: no PE -> no lever
            spread = ey - _dep_asof(dd)                                # carry vs deposit (not borrow)
            m = float(np.clip((spread - MGE_FED_FLOOR) /
                              (MGE_FED_CEIL - MGE_FED_FLOOR), 0.0, 1.0))
            return m
        if MGE_GATE == "conviction":
            st  = int(state_ff.get(pd.Timestamp(dd)) or state_by_date.get(pd.Timestamp(dd), 3) or 3)
            pb  = _pillar_b_asof(dd)                                   # True = US panic (block)
            pbc = (postbull_mult(pd.Timestamp(dd)) >= 1.0)             # True = clear (not blocked)
            return 1.0 if (st == 1 and pbc and not pb) else 0.0
        return 1.0
    # GRADUAL V2: load VNINDEX volume for vol_ratio lookup (causal: T-1 rolling 21d mean)
    if RECOVERY_GRADUAL:
        _vol_path = os.path.join(WORKDIR, "data", "snapshots", "vnivol_20260624.parquet")
        _vvol = pd.read_parquet(_vol_path)[["time", "Volume"]].copy()
        _vvol["time"] = pd.to_datetime(_vvol["time"])
        _vvol = _vvol.sort_values("time").reset_index(drop=True)
        # Causal vol_ratio: rolling BASE-day mean shifted by 1 (T uses mean of [T-BASE, T-1]).
        # BASE = RECOVERY_CAPIT_BASE (63/126) in CAPIT-ONLY mode (Exp-8); else 21 (gradual Exp-6).
        _GRAD_BASE = RECOVERY_CAPIT_BASE if RECOVERY_CAPIT_ONLY else 21
        _vvol["_volma"] = _vvol["Volume"].rolling(_GRAD_BASE, min_periods=max(10, _GRAD_BASE // 3)).mean().shift(1)
        _vvol["vol_ratio"] = _vvol["Volume"] / _vvol["_volma"]
        _vol_ratio_by_date = dict(zip(_vvol["time"], _vvol["vol_ratio"]))
        # Exp-8 REVISED: VNINDEX RSI reversal signals B/C (pulled from BQ, causal).
        _sigB_by_date = {}; _sigC_by_date = {}
        if RECOVERY_SIG_B or RECOVERY_SIG_C:
            _rsi = bq(f"""SELECT t.time, t.Close, t.D_RSI FROM tav2_bq.ticker AS t
              WHERE t.ticker='VNINDEX' AND t.D_RSI IS NOT NULL
              AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
            _rsi["time"] = pd.to_datetime(_rsi["time"]); _rsi = _rsi.sort_values("time").reset_index(drop=True)
            _r = _rsi["D_RSI"]; _c = _rsi["Close"]
            # Signal B: D_RSI<0.30 for >=3 consecutive days AND turning up (R[T] > R[T-3]+0.02)
            _lt = _r < 0.30
            _dur = _lt.groupby((~_lt).cumsum()).cumsum()
            _rsi["sigB"] = _lt & (_dur >= 3) & (_r > _r.shift(3) + 0.02)
            # Signal C (REFINED, Exp-8 v2 per user + DT5G D_RSI_BullDvg): a leading bottom-approaching ARM —
            # RSI rising vs 3M ago AND price flat/up <=6% vs 3M ago (selling absorbed, no rally yet), after a
            # genuine 3M washout (rolling-63d RSI min < 0.40) and not yet recovered (RSI < 0.60). Causal.
            _rmin3m = _r.rolling(63, min_periods=20).min()
            _rsi["Carm"] = ((_r > _r.shift(63) + 0.02) & (_c <= _c.shift(63) * 1.06) &
                            (_rmin3m < 0.40) & (_r < 0.60))
            # C is a CONFIRM (RECOVERY_C_CONFIRM=1): A/B may deploy only if C armed within last K sessions.
            # As a standalone trigger (RECOVERY_C_CONFIRM=0) C fires deploy directly (early — was harmful in v1).
            _rsi["Carmed"] = _rsi["Carm"].rolling(RECOVERY_C_ARM_K, min_periods=1).max().fillna(0).astype(bool)
            _rsi["sigC"] = _rsi["Carm"] if not RECOVERY_C_CONFIRM else False
            _sigB_by_date = dict(zip(_rsi["time"], _rsi["sigB"]))
            _sigC_by_date = dict(zip(_rsi["time"], _rsi["sigC"]))
            _carmed_by_date = dict(zip(_rsi["time"], _rsi["Carmed"]))
            print(f"  [recovery-RSI-signals] B={'ON' if RECOVERY_SIG_B else 'off'} ({int(_rsi['sigB'].sum())} fires) "
                  f"C={'ON' if RECOVERY_SIG_C else 'off'} (arm {int(_rsi['Carm'].sum())} fires, "
                  f"mode={'CONFIRM K=%d' % RECOVERY_C_ARM_K if RECOVERY_C_CONFIRM else 'trigger'}) — VNINDEX D_RSI from BQ")
        # WMAX to use on capitulation day (if LEVER_ON_CAPIT and MGE > 1.0)
        _capit_wmax = (MGE if (RECOVERY_LEVER_ON_CAPIT and MGE > 1.0) else RECOVERY_WMAX)
        if RECOVERY_CAPIT_ONLY:
            print(f"  [recovery-CAPIT-ONLY] Exp-8: NO instant/gradual deploy; parking idles until vol_ratio "
                  f">= {RECOVERY_CAPIT_VOL:.1f}x vs {_GRAD_BASE}d baseline ({'3M' if _GRAD_BASE==63 else '6M' if _GRAD_BASE==126 else str(_GRAD_BASE)+'d'}), "
                  f"then snap-to-full + HOLD. capit_wmax={_capit_wmax:.2f}")
        else:
            print(f"  [recovery-gradual] GRADUAL=ON days={RECOVERY_DAYS} capit_vol={RECOVERY_CAPIT_VOL:.1f}x base={_GRAD_BASE}d "
                  f"capit_wmax={_capit_wmax:.2f} (calibrated: COVID≈1.65x, 2022≈1.91x, 2025≈2.26x)")
        # ACCEL FILTER (Exp-7): build dd_5d and dd_10d from VNINDEX Close (causal T-1)
        # At day T: uses Close[T-1]/Close[T-6]-1 and Close[T-1]/Close[T-11]-1
        # Source: vni_close_by_date (already loaded from BQ; covers full backtest window)
        if RECOVERY_ACCEL:
            _vni_close_s = pd.Series(vni_close_by_date).sort_index()
            _vni_close_shift1  = _vni_close_s.shift(1)   # T-1 close (causal: most recent known)
            _vni_close_shift6  = _vni_close_s.shift(6)   # T-6 close (5 trading days ago vs T-1)
            _vni_close_shift11 = _vni_close_s.shift(11)  # T-11 close (10 trading days ago vs T-1)
            _dd5d_s  = _vni_close_shift1 / _vni_close_shift6  - 1.0
            _dd10d_s = _vni_close_shift1 / _vni_close_shift11 - 1.0
            _accel_ok_s = (_dd5d_s < -0.03) | (_dd5d_s < _dd10d_s * 0.6)
            _dd5d_by_date    = _dd5d_s.to_dict()
            _dd10d_by_date   = _dd10d_s.to_dict()
            _accel_ok_by_date = _accel_ok_s.to_dict()
            print(f"  [accel-filter] RECOVERY_ACCEL=ON: dd_5d<-3% OR dd_5d<dd_10d*0.6 (T-1 causal)")
    # --- RECOVERY_PARK_BY_DATE loop ---
    RECOVERY_PARK_BY_DATE = {}; _nrec = 0; _msum = 0.0
    # Gradual state machine (only active when RECOVERY_GRADUAL=1)
    _grad_episode_active = False      # are we inside an active episode?
    _grad_episode_day    = 0          # how many days into current episode
    _grad_current_frac   = 0.0        # accumulated frac so far this episode
    _grad_target_frac    = 0.0        # target frac for this episode (from pb_z depth)
    _grad_logs           = []         # per-episode log for reporting
    # Accel-filter episode tracking (only when RECOVERY_ACCEL=1)
    _accel_ep_start      = None       # date when CRISIS/BEAR + pb_z ≤ START first triggered (before accel_ok)
    _accel_ep_accel_date = None       # first date within episode where accel_ok fired
    _accel_ep_capit_date = None       # first capit fire in this episode
    _accel_logs          = []         # [accel-filter] per-episode log entries
    for d in vni_dates:
        base = dict(BULL_PARK_BY_DATE[d]) if BULL_PARK_BY_DATE else dict(PARK_STATES_DICT)
        st = int(state_ff.get(d) or 3)
        if st in (1, 2):
            z = _pbz_asof(d)
            if pd.notna(z) and z <= RECOVERY_PBZ_START:
                frac = float(np.clip((RECOVERY_PBZ_START - z) / (RECOVERY_PBZ_START - RECOVERY_PBZ_DEEP), 0.0, 1.0))
                m = _dep_m(d)                                          # money-condition gate
                base_st = float(PARK_STATES_DICT.get(st, 0.0))
                if RECOVERY_GRADUAL:
                    # Compute the "full" target weight for this day (what instant-deploy would set)
                    _tgt = base_st + m * frac * (RECOVERY_WMAX - base_st)
                    # ACCEL FILTER: check accelerating-decline condition (causal T-1)
                    _this_accel_ok = True   # default: no accel filter = always OK
                    if RECOVERY_CAPIT_ONLY:
                        # Exp-8: episode may ONLY be entered by a capit fire (no instant/gradual/accel start).
                        # Before a capit, _grad_current_frac stays 0 (idle); after, the keep-frac branch HOLDS it.
                        _this_accel_ok = False
                    if RECOVERY_ACCEL:
                        _this_accel_ok = bool(_accel_ok_by_date.get(pd.Timestamp(d), False))
                        # Track episode start (when CRISIS/BEAR + pb_z fires, even before accel_ok)
                        if _accel_ep_start is None:
                            _accel_ep_start = pd.Timestamp(d)
                        if _this_accel_ok and _accel_ep_accel_date is None:
                            _accel_ep_accel_date = pd.Timestamp(d)
                    # Check capitulation (volume spike on this day)
                    _vr = _vol_ratio_by_date.get(pd.Timestamp(d), np.nan)
                    _sigA = (not np.isnan(_vr)) and (_vr >= RECOVERY_CAPIT_VOL)
                    _sigB = RECOVERY_SIG_B and bool(_sigB_by_date.get(pd.Timestamp(d), False))
                    _sigC = RECOVERY_SIG_C and bool(_sigC_by_date.get(pd.Timestamp(d), False))
                    if RECOVERY_SIG_C and RECOVERY_C_CONFIRM:   # C as confirm: A/B deploy only if C armed recently
                        _capit_fired = (_sigA or _sigB) and bool(_carmed_by_date.get(pd.Timestamp(d), False))
                    else:                                       # ANY enabled signal fires (Exp-8 REVISED OR-trigger)
                        _capit_fired = _sigA or _sigB or _sigC
                    # CAPIT OVERRIDE: fire even if accel_ok not met yet (strongest signal)
                    _episode_entry_ok = _this_accel_ok or _capit_fired
                    if _episode_entry_ok:
                        if not _grad_episode_active:
                            # Episode just started (either accel_ok OR capit override)
                            _grad_episode_active = True
                            _grad_episode_day    = 1
                            _grad_current_frac   = 0.0
                            _grad_target_frac    = _tgt
                            if RECOVERY_ACCEL and not _this_accel_ok and _capit_fired:
                                # Capit override: note that accel wasn't met but capit fired
                                if _accel_ep_accel_date is None:
                                    _accel_ep_accel_date = pd.Timestamp(d)  # capit counts as accel confirmation
                        else:
                            # Episode continuing: update target (pb_z/money-gate may drift)
                            _grad_episode_day   += 1
                            _grad_target_frac    = _tgt   # track current day's target
                        if _capit_fired:
                            if RECOVERY_ACCEL and _accel_ep_capit_date is None:
                                _accel_ep_capit_date = pd.Timestamp(d)
                            # Snap to full target (possibly with leverage wmax)
                            _full_wmax = _capit_wmax if RECOVERY_LEVER_ON_CAPIT else RECOVERY_WMAX
                            _capit_tgt = base_st + m * frac * (_full_wmax - base_st)
                            _grad_current_frac = _capit_tgt
                            if RECOVERY_LEVER_BOTTOM:        # record this confirmed bottom for the margin sleeve
                                _lever_dates.append(pd.Timestamp(d))
                            _5d = _dd5d_by_date.get(pd.Timestamp(d), float('nan')) if RECOVERY_ACCEL else float('nan')
                            _10d = _dd10d_by_date.get(pd.Timestamp(d), float('nan')) if RECOVERY_ACCEL else float('nan')
                            _sig_tag = "+".join([s for s, on in [("A", _sigA), ("B", _sigB), ("C", _sigC)] if on])
                            _grad_logs.append(f"  [RECOVERY-CAPIT] {pd.Timestamp(d).date()} sig={_sig_tag} vol_ratio="
                                              f"{_vr:.2f}x -> FULL DEPLOY frac={_grad_current_frac:.3f} "
                                              f"(ep_day={_grad_episode_day})" +
                                              (f" dd5d={_5d:.2%} dd10d={_10d:.2%}" if RECOVERY_ACCEL and not np.isnan(_5d) else ""))
                        else:
                            # Gradual step: add 1/N of target per day
                            _daily_step = _grad_target_frac / RECOVERY_DAYS
                            _grad_current_frac = min(_grad_current_frac + _daily_step, _grad_target_frac)
                        w = _grad_current_frac
                    else:
                        # No entry yet (CAPIT-ONLY idling pre-spike, or accel filter not met): HOLD current frac
                        w = _grad_current_frac   # keep whatever we already deployed (0 if no episode yet)
                        if RECOVERY_ACCEL:       # these debug vars only exist when accel dicts are built
                            _5d = _dd5d_by_date.get(pd.Timestamp(d), float('nan'))
                            _10d = _dd10d_by_date.get(pd.Timestamp(d), float('nan'))
                else:
                    # Original instant-deploy logic
                    w = base_st + m * frac * (RECOVERY_WMAX - base_st)
                if w > base_st + 0.01:
                    base[st] = w; _nrec += 1; _msum += m
            else:
                # pb_z rose above threshold: reset episode
                if RECOVERY_GRADUAL and _grad_episode_active:
                    # Log the completed episode (accel filter) before resetting
                    if RECOVERY_ACCEL and _accel_ep_start is not None:
                        _5d_ep = _dd5d_by_date.get(_accel_ep_start, float('nan'))
                        _10d_ep = _dd10d_by_date.get(_accel_ep_start, float('nan'))
                        _accel_logs.append({
                            "episode_start": _accel_ep_start.date() if _accel_ep_start else None,
                            "dd_5d_start": f"{_5d_ep:.2%}" if not np.isnan(_5d_ep) else "N/A",
                            "dd_10d_start": f"{_10d_ep:.2%}" if not np.isnan(_10d_ep) else "N/A",
                            "accel_first_date": _accel_ep_accel_date.date() if _accel_ep_accel_date else "NEVER",
                            "capit_date": _accel_ep_capit_date.date() if _accel_ep_capit_date else "NONE",
                            "end_reason": "pb_z_above_threshold",
                        })
                    _grad_episode_active = False
                    _grad_current_frac   = 0.0
                    _grad_episode_day    = 0
                if RECOVERY_ACCEL:
                    _accel_ep_start = None; _accel_ep_accel_date = None; _accel_ep_capit_date = None
        else:
            # State exited CRISIS/BEAR: reset episode
            if RECOVERY_GRADUAL and _grad_episode_active:
                if RECOVERY_ACCEL and _accel_ep_start is not None:
                    _5d_ep = _dd5d_by_date.get(_accel_ep_start, float('nan'))
                    _10d_ep = _dd10d_by_date.get(_accel_ep_start, float('nan'))
                    _accel_logs.append({
                        "episode_start": _accel_ep_start.date() if _accel_ep_start else None,
                        "dd_5d_start": f"{_5d_ep:.2%}" if not np.isnan(_5d_ep) else "N/A",
                        "dd_10d_start": f"{_10d_ep:.2%}" if not np.isnan(_10d_ep) else "N/A",
                        "accel_first_date": _accel_ep_accel_date.date() if _accel_ep_accel_date else "NEVER",
                        "capit_date": _accel_ep_capit_date.date() if _accel_ep_capit_date else "NONE",
                        "end_reason": "state_exit",
                    })
                _grad_episode_active = False
                _grad_current_frac   = 0.0
                _grad_episode_day    = 0
            if RECOVERY_ACCEL:
                _accel_ep_start = None; _accel_ep_accel_date = None; _accel_ep_capit_date = None
        RECOVERY_PARK_BY_DATE[d] = base
    if RECOVERY_GRADUAL and _grad_logs:
        print(f"  [recovery-gradual] {len(_grad_logs)} capitulation event(s) detected:")
        for _gl in _grad_logs:
            print(_gl)
    if RECOVERY_ACCEL and _accel_logs:
        print(f"  [accel-filter] {len(_accel_logs)} episode(s):")
        for _al in _accel_logs:
            print(f"    ep_start={_al['episode_start']} dd5d={_al['dd_5d_start']} dd10d={_al['dd_10d_start']}"
                  f" accel_date={_al['accel_first_date']} capit={_al['capit_date']} end={_al['end_reason']}")
    if RECOVERY_DEP_GATE and _nrec:
        _gp = (f"fed-spread floor{RECOVERY_FED_FLOOR:.3f}/ceil{RECOVERY_FED_CEIL:.3f}"
               if RECOVERY_GATE_MODE == "fed"
               else f"deposit floor{RECOVERY_DEP_FLOOR:.3f}/ceil{RECOVERY_DEP_CEIL:.2f}")
        _gtxt = f"{RECOVERY_GATE_MODE}-gate ON {_gp} (avg m={_msum/_nrec:.2f})"
    else:
        _gtxt = "money-gate OFF"
    _grad_info = (f" | GRADUAL={RECOVERY_DAYS}d capit={RECOVERY_CAPIT_VOL:.1f}x" if RECOVERY_GRADUAL else "")
    print(f"  [recovery-park] ON pbz[{RECOVERY_PBZ_START}->{RECOVERY_PBZ_DEEP}] wmax{RECOVERY_WMAX} | {_gtxt}{_grad_info} "
          f"-> {_nrec} deep-cheap CRISIS/BEAR days deploy idle cash into custom30V")
    # DEEP-VALUE POSTBULL OVERRIDE post-pass (Exp-5b, Taylor 2026-06-24):
    # Now that _pbz_asof() is available, re-examine any capit_events that were zeroed by the
    # postbull guard (_mat < 1.0 and _size_premat > 0 but size==0). If the universe pb_z at that
    # date is below DEEP_VALUE_PBZ threshold, restore size to _size_premat (pre-maturity value).
    if DEEP_VALUE_PBZ > -90:
        _dvo_count = 0
        for _e in capit_events:
            if _e.get("_mat", 1.0) < 1.0 and _e["_size_premat"] > 0.005 and _e["size"] <= 0.005:
                _d_ev = _e["date"]
                _z = _pbz_asof(_d_ev)
                if pd.notna(_z) and _z < DEEP_VALUE_PBZ:
                    _old_size = _e["size"]
                    _e["size"] = _e["_size_premat"]
                    _dvo_count += 1
                    print(f"  [deep-value-override] {_d_ev.date()}: postbull zeroed but pb_z={_z:.2f} < "
                          f"{DEEP_VALUE_PBZ:.1f} -> override size {_old_size:.2f} -> {_e['size']:.2f}")
                else:
                    _z_str = f"{_z:.2f}" if pd.notna(_z) else "nan"
                    print(f"  [deep-value-override] {_d_ev.date()}: postbull zeroed, pb_z={_z_str} "
                          f"NOT below {DEEP_VALUE_PBZ:.1f} -> still blocked")
        print(f"  [deep-value-override] {_dvo_count} events restored (threshold pb_z<{DEEP_VALUE_PBZ:.1f})")
PARK_BY_DATE = RECOVERY_PARK_BY_DATE if RECOVERY_PARK else BULL_PARK_BY_DATE
# LEVER-AT-BOTTOM: inject ONE levered custom30 stock event per confirmed-bottom episode (dedup fires within
# 20 trading days). These become CAPITLEV_* plays in add_capit_arm (fixed borrowed weight RECOVERY_LEVER_FRAC).
if RECOVERY_LEVER_BOTTOM and _lever_dates:
    _ld = sorted(set(_lever_dates)); _kept = []
    for _d in _ld:
        if not _kept or (_d - _kept[-1]).days > 28:   # ~20 trading days = one entry per bottom
            _kept.append(_d)
    # CAPITLEV carries the FULL custom30 exposure (RECOVERY_LEVER_FRAC = gross target, e.g. 1.30); to stop the
    # parking from absorbing the cash (parking is cash-bounded so stock+parking would stay ≤1.0), SUPPRESS the
    # recovery parking over each episode's hold window so CAPITLEV's stock buy draws cash<0 = real borrow.
    _vdi = {d: i for i, d in enumerate(vni_dates)}
    for _d in _kept:
        capit_events.append({"date": _d, "state": int(state_ff.get(_d) or 1), "grind": False,
                             "size": RECOVERY_LEVER_FRAC, "dd": 0.0, "cool": False, "lever": True})
        _i0 = _vdi.get(_d)
        if _i0 is not None and RECOVERY_PARK_BY_DATE is not None:
            for _j in range(_i0, min(_i0 + CAPIT_HOLD + 1, len(vni_dates))):
                RECOVERY_PARK_BY_DATE[vni_dates[_j]] = dict(PARK_STATES_DICT)   # drop recovery boost → no parking competition
    print(f"  [lever-at-bottom] {len(_kept)} episode(s) -> CAPITLEV carries custom30 gross={RECOVERY_LEVER_FRAC} "
          f"(parking suppressed over {CAPIT_HOLD}d hold so the buy borrows): {[d.date().isoformat() for d in _kept]}")
BAL_KW = dict(allowed_tiers=RS["allowed_tiers"], max_positions=MAX_POS_V11,
              hold_days=45, stop_loss=-0.20, min_hold=2, slippage=0.0, init_nav=BAL_NAV,
              sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
              sector_cap_exempt_tiers=RS["sector_cap_exempt"],
              tier_weights_by_state=RS["tier_weights_by_state"],
              deposit_annual=0.0, borrow_annual=BORROW_ANNUAL, state_by_date=state_ff,
              cash_etf_states=PARK_STATES_DICT, cash_etf_states_by_date=PARK_BY_DATE, vn30_underlying=vn30_underlying,
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
if _mge:                                                    # real-margin: open the gross cap, restrict room to CAPIT
    kwA["max_gross_exposure"] = _mge
    kwA["margin_tiers"] = set(t for t in tw_balC if t.startswith("CAPIT")) if MGE_CAPIT_ONLY else None
    if MARGIN_CALL:
        kwA["margin_call_on"] = True; kwA["margin_call_log"] = mc_log_bal
        if MGE_HARD > 0: kwA["mge_hard"] = MGE_HARD
        if MGE_FLOOR > 0: kwA["mge_floor"] = MGE_FLOOR
        print(f"  [S4 margin-call BAL] ON | hard={MGE_HARD or (_mge+0.15):.2f} floor={MGE_FLOOR or _mge:.2f}")
    print(f"  [real-margin] max_gross_exposure={_mge} | margin_tiers="
          f"{'CAPIT-only' if MGE_CAPIT_ONLY else 'ALL'} | borrow {BAL_KW['borrow_annual']*100:.0f}%/yr")
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
              deposit_annual=0.0, borrow_annual=BORROW_ANNUAL, state_by_date=state_ff,
              cash_etf_states=PARK_STATES_DICT, cash_etf_states_by_date=PARK_BY_DATE, vn30_underlying=vn30_underlying,
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
if _mge:                                                    # mirror BAL: open the gross cap on LAG so its CAPIT arm can borrow too
    kwB["max_gross_exposure"] = _mge
    kwB["margin_tiers"] = set(t for t in tw_lagC if t.startswith("CAPIT")) if MGE_CAPIT_ONLY else None
    if MARGIN_CALL:
        kwB["margin_call_on"] = True; kwB["margin_call_log"] = mc_log_lag
        if MGE_HARD > 0: kwB["mge_hard"] = MGE_HARD
        if MGE_FLOOR > 0: kwB["mge_floor"] = MGE_FLOOR
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
    # deposit/borrow interest mutates cash WITHOUT a tx row -> add to expected flows so margin runs reconcile
    interest = (navdf["interest"].loc[common].fillna(0.0) if "interest" in navdf.columns
                else pd.Series(0.0, index=common))
    _resid = (dcash - f_full - interest)
    err = _resid.abs().max()
    if os.environ.get("SC_DEBUG") and err > 1e6:   # locate offending days
        _top = _resid.abs().sort_values(ascending=False).head(6)
        print(f"  [SC_DEBUG {book}] top residual days (dcash - flows - interest):")
        for _dt, _ in _top.items():
            print(f"     {pd.Timestamp(_dt).date()}  resid={_resid.loc[_dt]:>+18,.0f}  dcash={dcash.loc[_dt]:>+18,.0f} "
                  f" flows={f_full.loc[_dt]:>+18,.0f}  int={interest.loc[_dt]:>+14,.0f}")
        # DEEP dump for the single worst day: every all_tx flow row for (book, day) from the SAME objects
        _wd = _top.index[0]
        _rows = flows_tx[(flows_tx["book"] == book) & (flows_tx["ymd"] == _wd)]
        print(f"  [SC_DEBUG {book}] worst day {pd.Timestamp(_wd).date()} — {len(_rows)} flow rows; "
              f"cash[d]={cash.loc[_wd]:,.0f} cash[d-1]={cash.shift(1).loc[_wd]:,.0f} int={interest.loc[_wd]:,.0f}")
        for _, _r in _rows.iterrows():
            print(f"       {_r['action']:<5} {str(_r.get('ticker','?')):<10} buy={_r.get('buy_amount',0):>16,.0f} "
                  f"sell={_r.get('sell_amount',0):>16,.0f} fee={_r.get('fee',0):>12,.0f} net={_r['net']:>16,.0f} "
                  f"{str(_r.get('play_type','?')):<10} {str(_r.get('reason','?'))}")
        print(f"       SUM net flows = {_rows['net'].sum():,.0f}  (vs needed dcash-int = {dcash.loc[_wd]-interest.loc[_wd]:,.0f})")
    selfcheck[f"cash_flow_identity_max_err_vnd_{book}"] = float(err)
    # final NAV identity: cash + stocks marks + etf marks == nav
    mtm_sum = sum(r["sell_amount"] for r in mtm_rows if r["book"] == book)
    nav_id_err = abs(float(cash.iloc[-1]) + mtm_sum - float(navdf["nav"].loc[last_day]))
    selfcheck[f"final_nav_identity_err_vnd_{book}"] = nav_id_err
    print(f"  [selfcheck {book}] cash-flow identity max err = {err:,.0f} VND; "
          f"final NAV identity err = {nav_id_err:,.0f} VND")

# --- BORROW-COST + GROSS instrumentation (real-lever audit) ---
# gross exposure = (nav - cash)/nav (= stocks+ETF / nav); >1.0 means real >100% leverage (cash<0).
# borrow cost = -sum(interest where interest<0); deposit credit = sum(interest where interest>0).
_borrow_report = {}
for book, navdf in [("BAL", nb), ("LAG", nl)]:
    intr = navdf["interest"].fillna(0.0) if "interest" in navdf.columns else pd.Series(0.0, index=navdf.index)
    borrow = float(-intr[intr < 0].sum())
    gross = ((navdf["nav"] - navdf["cash"]) / navdf["nav"])
    n_borrow_days = int((navdf["cash"] < 0).sum())
    _borrow_report[book] = {"borrow_vnd": borrow, "max_gross": float(gross.max()),
                            "min_cash_vnd": float(navdf["cash"].min()), "n_borrow_days": n_borrow_days}
    selfcheck[f"borrow_cost_vnd_{book}"] = borrow
    selfcheck[f"max_gross_{book}"] = float(gross.max())
_borrow_total = sum(v["borrow_vnd"] for v in _borrow_report.values())
selfcheck["borrow_cost_total_vnd"] = _borrow_total
# combined gross (both 25B books summed at reference)
_comb_gross = ((navb_c - nb["cash"].loc[common]) + (navl_c - nl["cash"].loc[common])) / (navb_c + navl_c)
selfcheck["max_gross_combined"] = float(_comb_gross.max())
print(f"  [borrow-audit] total borrow cost = {_borrow_total:,.0f} VND "
      f"(BAL {_borrow_report['BAL']['borrow_vnd']:,.0f} / LAG {_borrow_report['LAG']['borrow_vnd']:,.0f}); "
      f"max gross BAL {_borrow_report['BAL']['max_gross']:.3f} LAG {_borrow_report['LAG']['max_gross']:.3f} "
      f"combined {_comb_gross.max():.3f}; borrow-days BAL {_borrow_report['BAL']['n_borrow_days']} "
      f"LAG {_borrow_report['LAG']['n_borrow_days']}")
if MARGIN_CALL:
    _mc_all = mc_log_bal + mc_log_lag
    selfcheck["margin_call_fires"] = len(_mc_all)
    if _mc_all:
        _wost = max(_mc_all, key=lambda r: r["gross_before"])
        print(f"  [S4 margin-call] {len(mc_log_bal)} BAL + {len(mc_log_lag)} LAG fires; "
              f"worst breach gross {_wost['gross_before']:.3f}->{_wost['gross_after']:.3f} on {_wost['ymd'].date() if hasattr(_wost['ymd'],'date') else _wost['ymd']} "
              f"(sold {_wost['sell_vnd']/1e9:.3f}B)")
        for r in _mc_all[:8]:
            _d = r['ymd'].date() if hasattr(r['ymd'],'date') else r['ymd']
            print(f"      {_d}: gross {r['gross_before']:.3f}->{r['gross_after']:.3f}  sold {r['sell_vnd']/1e9:.3f}B  (hard {r['mge_hard']:.2f}/floor {r['mge_floor']:.2f})")
    else:
        print(f"  [S4 margin-call] ON but 0 fires (gross never breached hard cap)")

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
             "v22base": "V2.2-base (= BAL|LAG STATIC 50/50 plain-sum + ETF parking, NO CAPIT sleeve, NO allocator) on DT5G",
             "singlebook": "SINGLE-BOOK = gated custom30 (cash_etf_states DT5G 5-state, no EXBULL lev) + CAPIT-on-idle, NO momentum/PEAD"}.get(MODE, MODE)),
 ("mode", MODE + {"v23a": " (allocator band ±10pp, CAPIT on)", "v23c": " (static 50/50 plain-sum, CAPIT on)",
                  "v22base": " (static 50/50 plain-sum, CAPIT OFF)",
                  "singlebook": f" (gated custom30 {SB_GATE} + CAPIT {'on' if USE_CAPIT else 'off'})"}.get(MODE, "")),
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
     ("custom_basket_pit_params", f"quality={_pq} rebal={_preb} gate_rating={_pgate} weight_scheme={BASKET_WT} top_n={BASKET_TOPN} name_cap={BASKET_NAMECAP} qtilt={';'.join(f'{k}:{v}' for k,v in sorted((BASKET_QTILT if BASKET_QTILT is not None else __import__('custom_basket').QTILT).items()))}" if _is_pit else "n/a"),
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
