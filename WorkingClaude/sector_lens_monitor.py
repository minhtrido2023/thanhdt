#!/usr/bin/env python3
"""
sector_lens_monitor.py — weekly read-only status monitor for the Group-A sector watchlist.
Job Taylor_20260706_062405 (builds Section 7 "Harvesting Workflow Proposal" of
mike/agents/Taylor/sector_watchlist_framework.md; user-approved). RESEARCH / MONITOR ONLY —
touches no production file (custom30V / BAL / LAG / rating_8l.py unchanged). This is a
display/audit tool, NOT an automated selector: a raw multiple crossing a threshold is
NECESSARY-NOT-SUFFICIENT (every Group-A lens failed OOS as a standalone book — Rule 3), so a
BUY here still routes through the Taylor-validate -> DollarBill-plan -> user-approve -> Mafee
chain. It only surfaces STATUS + TRANSITIONS.

WHAT IT DOES
  - Reads the BQ local DuckDB cache (data/bq_cache/, threads=1): latest `ticker` row per name
    (price-current PE/PB/EVEB/PE_MA5Y) + latest `ticker_financial` row (fundamentals +
    PE_MA1Y/PB_MA1Y/GPM_P0..P7) + latest `vnindex_5state_dt5g_live` state.
  - Reads the on-disk commodity feeds (hog_price_vn.csv, maize_monthly.csv,
    soybean_meal_monthly.csv) for the DBC livestock 2-part overlay.
  - Evaluates each name against the ENTRY CONDITION defined in its own *_framework.md (formulas
    NOT re-invented here — see per-lens comments) -> one of SIX standardized states.
  - Prints a status table, writes data/sector_lens_status_<date>.csv (history for audit), and
    diffs vs the most recent prior status file -> HIGHLIGHTS only names that changed state
    (the Section-7 alert condition: "alert only on a state transition").

SIX STATES (standardized 2026-07-06, replacing the old discrete labels in Section 1)
  1. EXCLUDED   fail a hard gate (quality floor / leverage / forensic flag / euphoria cap)
  2. RICH_WAIT  passes the gate but is currently EXPENSIVE vs its own history
  3. WATCH      passes the gate + cheap, but no confirmed turn/catalyst yet
  4. ARMED      (only for a sector with a fast-proxy/slow-confirm structure; today ONLY DBC via
                 the hog-feed spread) early-warning has turned supportive, not yet confirmed
  5. BUY        confirmed entry; sub-mode STRONG (deep in window) vs ACCUMULATE (moderate) using
                each framework's OWN thresholds. STRONG lines (all walk-forward-calibrated, job
                Taylor_20260706_070219 — depth-quintile fwd-return step surviving OOS):
                  CTR EVEB<9 · Banking discount>=0.45 · Tech(FPT) PE<PE_MA1Y*0.75 · Securities PB<0.75.
                Textile/Pharma/Logistics are ACCUMULATE-ONLY BY DESIGN (no robust deep-discount
                step — see their eval fns): pharma = flat depth-return (buy-and-hold anchor, timing
                adds nothing); logistics = deepest bucket underperforms IS (high-beta tactical, do
                NOT size up when "cheaper still"); textile = IS/OOS disagree at the extreme (no break).
  6. STALE      data feed not fresh -> FAIL-SAFE: hold the last known state, never fabricate

FAIL-SAFE: a stale ticker/financial row, missing name, or stale feed -> hold the prior status
(from the last status CSV) and flag; it NEVER invents a signal from missing data (same discipline
as DT5G get_gated_state fail-closed and coding_guidelines.md 6 report-provenance).
"""
import os, sys, glob, json, datetime as dt
import numpy as np
import pandas as pd

ROOT = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
CACHE = os.path.join(ROOT, "data", "bq_cache")
OUTDIR = os.path.join(ROOT, "data")
TODAY = dt.date.today()

# staleness tolerances (days). Weekly monitor -> generous; STALE => hold last state.
PRICE_STALE_DAYS = 21     # ticker daily row; cache syncs ~weekly
FIN_STALE_DAYS = 200      # quarterly filing: >200d = a full quarter missed
STATE_STALE_DAYS = 21     # DT5G daily state
FEED_STALE_DAYS = 45      # hog weekly / feed monthly -> DBC overlay

# ---- Group-A watchlist (Section 0). Each entry: sector, lens, eval fn key ----
NAMES = [
    ("MBB", "Banking",       "bank"),
    ("ACB", "Banking",       "bank"),
    ("HDB", "Banking",       "bank"),
    ("TCB", "Banking",       "bank"),
    ("VCB", "Banking",       "bank"),
    ("FPT", "Tech",          "fpt"),
    ("SSI", "Securities",    "sec"),
    ("VCI", "Securities",    "sec"),
    ("VND", "Securities",    "sec"),
    ("HCM", "Securities",    "sec"),
    ("CTR", "Viettel-infra", "ctr"),
    ("MSH", "Textile",       "msh"),
    ("DHG", "Pharma",        "dhg"),
    ("PVT", "Logistics",     "pvt"),
    ("HAH", "Logistics",     "hah"),
    ("DBC", "Livestock",     "dbc"),
]


def _f(v):
    """float or nan (treat None/NaN uniformly)."""
    try:
        x = float(v)
        return x if np.isfinite(x) else np.nan
    except (TypeError, ValueError):
        return np.nan


# ----------------------------------------------------------------------------
# Data load (DuckDB, threads=1, read-only)
# ----------------------------------------------------------------------------
def load_data(names):
    import duckdb
    con = duckdb.connect(":memory:")
    con.execute("SET threads=1")
    TKG = f"read_parquet('{CACHE}/ticker/*.parquet')"
    FIN = f"read_parquet('{CACHE}/ticker_financial.parquet')"
    DT5G = f"read_parquet('{CACHE}/vnindex_5state_dt5g_live.parquet')"
    q = ",".join(f"'{n}'" for n in names)

    val = con.execute(f"""
        WITH r AS (SELECT *, ROW_NUMBER() OVER(PARTITION BY ticker ORDER BY time DESC) rn
                   FROM {TKG} WHERE ticker IN ({q}))
        SELECT ticker, time AS price_time, PE, PB, EVEB, PE_MA5Y
        FROM r WHERE rn=1""").df()

    fin = con.execute(f"""
        WITH r AS (SELECT *, ROW_NUMBER() OVER(PARTITION BY ticker ORDER BY time DESC) rn
                   FROM {FIN} WHERE ticker IN ({q}))
        SELECT ticker, quarter, Release_Date, PE_MA1Y, PB_MA1Y, PE_MA5Y,
               ROE5Y, ROIC5Y, ROE_Trailing, ROE3Y, ROE_Min3Y, IntCov_P0,
               CF_OA_3Y, Debt_Eq_P0, NP_P0, NP_P4,
               GPM_P0, GPM_P1, GPM_P2, GPM_P3, GPM_P4, GPM_P5, GPM_P6, GPM_P7
        FROM r WHERE rn=1""").df()

    st = con.execute(f"SELECT time, state FROM {DT5G} ORDER BY time DESC LIMIT 1").df()
    con.close()

    v = val.set_index("ticker").to_dict("index")
    f = fin.set_index("ticker").to_dict("index")
    state = {"state": int(st.iloc[0]["state"]),
             "time": pd.Timestamp(st.iloc[0]["time"]).date()}
    return v, f, state


def dbc_hog_feed_spread():
    """Latest quarterly hog-FEED margin-spread YoY for DBC (job Taylor_20260706_022555 method:
    60:40 corn:soybean-meal basket, Bac hog; unit-free YoY). spread_yoy>0 = early-warning
    supportive (margin turning up). Returns (spread_yoy, asof_date) or (nan, None) if feeds stale."""
    try:
        maize = pd.read_csv(os.path.join(ROOT, "data", "maize_monthly.csv"))
        sbm = pd.read_csv(os.path.join(ROOT, "data", "soybean_meal_monthly.csv"))
        hog = pd.read_csv(os.path.join(ROOT, "data", "hog_price_vn.csv"))
    except FileNotFoundError:
        return np.nan, None
    for d in (maize, sbm):
        d["month"] = pd.PeriodIndex(d["month"], freq="M")
    feed = (maize.rename(columns={"price": "maize"})
            .merge(sbm.rename(columns={"price": "sbm"}), on="month").set_index("month"))
    basket = 0.60 * feed["maize"] + 0.40 * feed["sbm"]
    fq = basket.groupby(basket.index.asfreq("Q")).mean().rename("feed").to_frame()
    fq["feed_yoy"] = fq["feed"].pct_change(4)
    hog = hog[hog["region"] == "Bắc"].copy()
    hog["date"] = pd.to_datetime(hog["date"], errors="coerce")
    hog = hog.dropna(subset=["date"])
    feed_asof = hog["date"].max().date()
    hq = hog.groupby(hog["date"].dt.to_period("Q"))["price_vnd_kg"].mean().rename("hog").to_frame()
    hq["hog_yoy"] = hq["hog"].pct_change(4)
    j = fq.join(hq, how="outer")
    j["spread_yoy"] = j["hog_yoy"] - j["feed_yoy"]
    latest = j.dropna(subset=["spread_yoy"])
    if latest.empty:
        return np.nan, feed_asof
    return float(latest["spread_yoy"].iloc[-1]), feed_asof


# ----------------------------------------------------------------------------
# Per-lens evaluators. Each returns dict(status, mode, primary, value, reference, reason).
# Formulas are quoted from the per-sector *_framework.md — NOT re-invented here.
# ----------------------------------------------------------------------------
def eval_bank(tk, v, f):
    # banking_valuation_framework: Gordon justified P/B = (ROE5Y-0.05)/0.08; quality floor
    # ROE5Y>=0.12 & ROE_Min3Y>=0.08; CHEAP-BUY when 0<PB<2.0 AND PB<justPB (else premium=RICH).
    pb = _f(v.get("PB")); roe5 = _f(f.get("ROE5Y")); rmin = _f(f.get("ROE_Min3Y"))
    if np.isnan(pb) or np.isnan(roe5):
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=np.nan,
                    reason="missing PB/ROE5Y")
    just = (roe5 - 0.05) / 0.08
    ref = f"justPB {just:.2f}"
    if roe5 < 0.12 or (not np.isnan(rmin) and rmin < 0.08):
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"quality floor fail (ROE5Y {roe5:.3f}<0.12 or ROE_Min3Y {rmin:.3f}<0.08)")
    if 0 < pb < 2.0 and pb < just:
        disc = (just - pb) / just
        # STRONG line = discount>=0.45 (job Taylor_20260706_070219): pooled-bank depth quintile
        # shows a real OOS-surviving step at Q5 (disc>=0.46: fwd-1M 3.7% / 3M 11.8% / hit 69% vs
        # ~1.6%/5%/54% for Q1-4). 0.45 rounds the ALL/OOS Q5 floor (0.462/0.468).
        mode = "STRONG" if disc >= 0.45 else "ACCUMULATE"
        tag = "(screaming buy, deep-discount step)" if mode == "STRONG" else ""
        return dict(status="BUY", mode=mode, primary="PB", value=pb, reference=ref,
                    reason=f"PB {pb:.2f} < justPB {just:.2f} (discount {disc:.0%}) {tag}".rstrip())
    return dict(status="RICH_WAIT", mode="", primary="PB", value=pb, reference=ref,
                reason=f"PB {pb:.2f} >= justPB {just:.2f} (premium — archetype-B, value screen can't catch)")


def eval_fpt(tk, v, f):
    # tech_valuation_framework: PE < PE_MA1Y*0.9 (entry window) AND ROIC5Y>0.12 AND ROE5Y>0.15.
    pe = _f(v.get("PE")); ma1 = _f(f.get("PE_MA1Y"))
    roic5 = _f(f.get("ROIC5Y")); roe5 = _f(f.get("ROE5Y"))
    if np.isnan(pe) or np.isnan(ma1):
        return dict(status="EXCLUDED", mode="", primary="PE", value=pe, reference=np.nan,
                    reason="missing PE/PE_MA1Y")
    thr = ma1 * 0.9
    thr_strong = ma1 * 0.75   # STRONG line (job Taylor_20260706_070219)
    ref = f"PE_MA1Y*0.9 {thr:.2f} · *0.75 {thr_strong:.2f}"
    if roic5 < 0.12 or roe5 < 0.15:
        return dict(status="EXCLUDED", mode="", primary="PE", value=pe, reference=ref,
                    reason=f"quality floor fail (ROIC5Y {roic5:.3f}<0.12 or ROE5Y {roe5:.3f}<0.15)")
    if pe < thr:
        # STRONG = PE < PE_MA1Y*0.75 (depth>=0.25 below own 1Y): tech(FPT) depth-quintile Q5
        # (both IS & OOS) is the best fwd-return bucket, and the framework's named great entries
        # (2018 post-divestment PE/MA1Y=0.71, 2022-23 IT-slowdown) all sit at depth ~0.25-0.29.
        # LOW-CONFIDENCE line (job Taylor_20260706_074228 bootstrap): universe is FPT-only
        # (VLA untradeable, ITD/ICT fail quality); the 26 STRONG weekly obs are only ~5 de-rating
        # episodes and IS is literally ONE (2018). Direction robust at 1M (P>0 ~0.9-1.0) but the
        # episode-clustered CI is wide and spans 0 at 2M/3M -> treat STRONG(FPT) as a "watch-close,
        # confirm independently" flag, NOT a statistically-standalone screaming buy. Line kept
        # (loosening dilutes the step; a companion-gate would over-engineer a display flag).
        mode = "STRONG" if pe < thr_strong else "ACCUMULATE"
        tag = "(deep entry, 2018/2022-class — LOW-CONFIDENCE: FPT-only, ~5 episodes/1 IS)" if mode == "STRONG" else ""
        return dict(status="BUY", mode=mode, primary="PE", value=pe, reference=ref,
                    reason=f"PE {pe:.1f} < PE_MA1Y*0.9 {thr:.1f} (cheap vs own history) {tag}".rstrip())
    return dict(status="RICH_WAIT", mode="", primary="PE", value=pe, reference=ref,
                reason=f"PE {pe:.1f} >= PE_MA1Y*0.9 {thr:.1f}")


def eval_sec(tk, v, f, state):
    # securities_valuation_framework: PB in (0,1.8) [euphoria cap] AND ROE_Trailing>0.08 AND
    # ROE_Trailing>ROE3Y [inflection] AND IntCov_P0>1.5 (NULL-tolerant). DT5G-GATED: cash when
    # DT5G in {CRISIS(1), BEAR(2)} -> gate CLOSED. The `state` column is 1-based
    # (1=CRISIS..5=EX-BULL, NEUTRAL=3); source design securities_screen.py L37/72/92 forces cash
    # at st in (1,2). (Fixed 2026-07-06: was (0,1) 0-based -> gate stayed OPEN in BEAR; job
    # Taylor_20260706_083933.)
    pb = _f(v.get("PB")); roet = _f(f.get("ROE_Trailing")); roe3 = _f(f.get("ROE3Y"))
    ic = _f(f.get("IntCov_P0"))
    gate_open = state["state"] not in (1, 2)
    ref = f"cap PB<1.8; DT5G={state['state']}({'open' if gate_open else 'CLOSED'})"
    if np.isnan(pb):
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=ref,
                    reason="missing PB")
    if pb >= 1.8 or pb <= 0:
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"PB {pb:.2f} >= 1.8 euphoria cap")
    if not np.isnan(ic) and ic <= 1.5:
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"IntCov {ic:.2f} <= 1.5 (over-levered margin book)")
    if np.isnan(roet) or roet <= 0.08:
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"ROE_Trailing {roet:.3f} <= 0.08 (min efficiency)")
    if roet <= roe3:
        return dict(status="WATCH", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"fails inflection (ROE_TTM {roet:.3f} <= ROE3Y {roe3:.3f})")
    if not gate_open:
        return dict(status="RICH_WAIT", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"qualifies on fundamentals but DT5G gate CLOSED (state {state['state']}) -> cash")
    # STRONG = PB<0.75 (job Taylor_20260706_070219): pooled-broker depth step in ALL sits at
    # Q3->Q4 (PB~0.75: fwd-1M 2.1%->4.5%, 3M 7.0%->8.9%), the Q4 elevation holds in BOTH IS & OOS
    # (Q5/PB<0.42 is spectacular OOS +9.3%/1M but WEAK IS -> the robust line is PB<0.75, not deeper).
    # Edge is OOS-loaded (sector's documented character) and already DT5G-gated -> crisis-only trigger.
    mode = "STRONG" if 0 < pb < 0.75 else "ACCUMULATE"
    tag = "(screaming buy: deep-value + gate open)" if mode == "STRONG" else ""
    return dict(status="BUY", mode=mode, primary="PB", value=pb, reference=ref,
                reason=f"QUALIFIES: PB {pb:.2f}<1.8, ROE_TTM {roet:.3f}>ROE3Y {roe3:.3f}, gate open {tag}".rstrip())


def eval_ctr(tk, v, f):
    # viettel_logistics_infra_framework: EVEB<9 STRONG / <11 ACCUMULATE AND ROIC5Y>0.20 AND
    # ROE_Trailing>0.25.
    eveb = _f(v.get("EVEB")); roic5 = _f(f.get("ROIC5Y")); roet = _f(f.get("ROE_Trailing"))
    if np.isnan(eveb) or eveb <= 0:
        return dict(status="EXCLUDED", mode="", primary="EVEB", value=eveb, reference="<9 strong/<11 accum",
                    reason="missing/invalid EVEB")
    ref = "<9 strong · <11 accum"
    if roic5 < 0.20 or roet < 0.25:
        return dict(status="EXCLUDED", mode="", primary="EVEB", value=eveb, reference=ref,
                    reason=f"quality gate fail (ROIC5Y {roic5:.3f}<0.20 or ROE_TTM {roet:.3f}<0.25)")
    if eveb < 9:
        return dict(status="BUY", mode="STRONG", primary="EVEB", value=eveb, reference=ref,
                    reason=f"EVEB {eveb:.1f} < 9 (screaming buy)")
    if eveb < 11:
        return dict(status="BUY", mode="ACCUMULATE", primary="EVEB", value=eveb, reference=ref,
                    reason=f"EVEB {eveb:.1f} in [9,11) mid-bucket (accumulate)")
    return dict(status="RICH_WAIT", mode="", primary="EVEB", value=eveb, reference=ref,
                reason=f"EVEB {eveb:.1f} >= 11 (not cheap)")


def _gpm_cv(f):
    g = np.array([_f(f.get(f"GPM_P{i}")) for i in range(8)], float)
    g = g[np.isfinite(g)]
    if len(g) < 4 or g.mean() == 0:
        return np.nan, np.nan, len(g)
    return g.std(ddof=0) / abs(g.mean()), g.mean(), len(g)


def eval_msh(tk, v, f):
    # textile_valuation_framework: single-name entry gates = PE<PE_MA1Y AND ROE5Y>0.15 AND
    # IntCov_P0>1.5. GPM-CV(P0..P7) is the framework's RANKING / elite-tier lens (line 139:
    # "correctly ranks MSH(elite)>TCM>>TNG"), NOT a hard binary book gate — reported here as
    # transparent quality context. NOTE: MSH trailing GPM-CV has ticked to ~0.178 (> the nominal
    # 0.15 elite line) purely because its margin is RISING (monotone 0.13->0.22), which inflates
    # trailing CV; it is still far from the erratic 0.38 crowd the gate was built to reject.
    pe = _f(v.get("PE")); ma1 = _f(f.get("PE_MA1Y"))
    roe5 = _f(f.get("ROE5Y")); ic = _f(f.get("IntCov_P0"))
    cv, gmean, n = _gpm_cv(f)
    cv_note = f"GPM-CV {cv:.3f}" + (f" (>0.15 elite line: rising-margin window)" if np.isfinite(cv) and cv >= 0.15 else "")
    if np.isnan(pe) or np.isnan(ma1):
        return dict(status="EXCLUDED", mode="", primary="PE", value=pe, reference=np.nan,
                    reason="missing PE/PE_MA1Y")
    ref = f"PE_MA1Y {ma1:.2f}; {cv_note}"
    if roe5 < 0.15 or (not np.isnan(ic) and ic <= 1.5):
        return dict(status="EXCLUDED", mode="", primary="PE", value=pe, reference=ref,
                    reason=f"quality floor fail (ROE5Y {roe5:.3f}<0.15 or IntCov {ic:.2f}<=1.5)")
    if pe < ma1:
        # ACCUMULATE-ONLY BY DESIGN (job Taylor_20260706_070219): a STRONG deep-discount tier is
        # NOT robust for textile — IS says the MIDDLE depth bucket pays best while OOS says the
        # deepest; the sign disagreement at the extreme is a red flag, so no fabricated break.
        return dict(status="BUY", mode="ACCUMULATE", primary="PE", value=pe, reference=ref,
                    reason=f"PE {pe:.1f} < PE_MA1Y {ma1:.1f} (in entry window; {cv_note})")
    return dict(status="RICH_WAIT", mode="", primary="PE", value=pe, reference=ref,
                reason=f"PE {pe:.1f} >= PE_MA1Y {ma1:.1f}")


def eval_dhg(tk, v, f):
    # pharma_valuation_framework: buy-and-hold — PE<PE_MA5Y AND ROE5Y>0.15 AND ROIC5Y>0.15.
    # NO timing (accumulate on weakness only) -> mode always ACCUMULATE.
    pe = _f(v.get("PE")); ma5 = _f(v.get("PE_MA5Y"))
    roe5 = _f(f.get("ROE5Y")); roic5 = _f(f.get("ROIC5Y"))
    if np.isnan(pe) or np.isnan(ma5):
        return dict(status="EXCLUDED", mode="", primary="PE", value=pe, reference=np.nan,
                    reason="missing PE/PE_MA5Y")
    ref = f"PE_MA5Y {ma5:.2f}"
    if roe5 < 0.15 or roic5 < 0.15:
        return dict(status="EXCLUDED", mode="", primary="PE", value=pe, reference=ref,
                    reason=f"quality floor fail (ROE5Y {roe5:.3f}<0.15 or ROIC5Y {roic5:.3f}<0.15)")
    if pe < ma5:
        # ACCUMULATE-ONLY, PERMANENT BY DESIGN (job Taylor_20260706_070219): depth vs fwd-return is
        # FLAT for pharma (deepest PE-discount does NOT beat the shallowest, both IS & OOS) — this
        # is the DATA confirming the buy-and-hold-anchor thesis: timing on cheapness adds nothing,
        # so there is no "screaming buy" tier, only accumulate-on-weakness.
        return dict(status="BUY", mode="ACCUMULATE", primary="PE", value=pe, reference=ref,
                    reason=f"PE {pe:.1f} < PE_MA5Y {ma5:.1f} (quality anchor, no timing)")
    return dict(status="RICH_WAIT", mode="", primary="PE", value=pe, reference=ref,
                reason=f"PE {pe:.1f} >= PE_MA5Y {ma5:.1f}")


def eval_pvt(tk, v, f):
    # logistics Screen B (shipping cyclical trough): PB<0.9 AND CF_OA_3Y>0 (cash-quality) AND
    # Debt_Eq_P0<2.0 (leverage-trap filter; VOS excluded on Debt_Eq 5.74). Empty outside troughs
    # by design. High-beta tactical, size small.
    pb = _f(v.get("PB")); cfoa = _f(f.get("CF_OA_3Y")); de = _f(f.get("Debt_Eq_P0"))
    if np.isnan(pb):
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference="<0.9 trough",
                    reason="missing PB")
    ref = "<0.9 trough"
    if not np.isnan(cfoa) and cfoa <= 0:
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"CF_OA_3Y {cfoa:.2e} <= 0 (dying-cheap, not trough)")
    if not np.isnan(de) and de >= 2.0:
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"Debt_Eq {de:.2f} >= 2.0 (leverage trap)")
    if pb < 0.9:
        # ACCUMULATE-ONLY BY DESIGN (job Taylor_20260706_070219): NO STRONG tier for logistics —
        # the deepest cheapness bucket UNDERPERFORMS in IS (middle bucket pays best), so "cheaper
        # still" is not a reason to size up. High-beta tactical: keep the size-small discipline.
        return dict(status="BUY", mode="ACCUMULATE", primary="PB", value=pb, reference=ref,
                    reason=f"PB {pb:.2f} < 0.9 trough + CF_OA+ + Debt_Eq {de:.2f}<2 (tactical, size small)")
    return dict(status="WATCH", mode="", primary="PB", value=pb, reference=ref,
                reason=f"PB {pb:.2f} >= 0.9 (not at trough)")


def eval_hah(tk, v, f):
    # logistics Screen A (EV/EBITDA cheap cyclical): EVEB in (0,10) AND ROE5Y>0.15 AND CF_OA_3Y>0.
    eveb = _f(v.get("EVEB")); roe5 = _f(f.get("ROE5Y")); cfoa = _f(f.get("CF_OA_3Y"))
    if np.isnan(eveb) or eveb <= 0:
        return dict(status="EXCLUDED", mode="", primary="EVEB", value=eveb, reference="<10 cheap",
                    reason="missing/invalid EVEB")
    ref = "<10 cheap"
    if roe5 < 0.15 or (not np.isnan(cfoa) and cfoa <= 0):
        return dict(status="EXCLUDED", mode="", primary="EVEB", value=eveb, reference=ref,
                    reason=f"quality fail (ROE5Y {roe5:.3f}<0.15 or CF_OA_3Y<=0)")
    if eveb < 10:
        return dict(status="BUY", mode="ACCUMULATE", primary="EVEB", value=eveb, reference=ref,
                    reason=f"EVEB {eveb:.1f} < 10 cheap cyclical, ROE5Y {roe5:.3f} (tactical)")
    return dict(status="RICH_WAIT", mode="", primary="EVEB", value=eveb, reference=ref,
                reason=f"EVEB {eveb:.1f} >= 10 (not cheap)")


def eval_dbc(tk, v, f, spread_yoy, feed_ok):
    # livestock_valuation_framework: PB<PB_MA1Y (value, cheap-vs-history) AND GPM_P0>GPM_P4
    # (margin-inflection, the signal that carries the return) + solvency CF_OA_3Y>0 & IntCov_P0>1.0.
    # 2-part structure -> ARMED: value present + GPM-turn NOT yet, but the hog-FEED spread
    # (job Taylor_20260706_022555) has turned supportive (spread_yoy>0) = early-warning.
    pb = _f(v.get("PB")); pbma = _f(f.get("PB_MA1Y"))
    g0 = _f(f.get("GPM_P0")); g4 = _f(f.get("GPM_P4"))
    cfoa = _f(f.get("CF_OA_3Y")); ic = _f(f.get("IntCov_P0"))
    if np.isnan(pb) or np.isnan(pbma):
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=np.nan,
                    reason="missing PB/PB_MA1Y")
    ref = f"PB_MA1Y {pbma:.2f}; GPM_P0 {g0:.3f} vs P4 {g4:.3f}; spread_yoy {spread_yoy:+.3f}" if feed_ok else \
          f"PB_MA1Y {pbma:.2f}; GPM_P0 {g0:.3f} vs P4 {g4:.3f}; spread FEED-STALE"
    if (not np.isnan(cfoa) and cfoa <= 0) or (not np.isnan(ic) and ic <= 1.0):
        return dict(status="EXCLUDED", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"solvency fail (CF_OA_3Y<=0 or IntCov {ic:.2f}<=1.0)")
    value_half = pb < pbma
    gpm_turn = (not np.isnan(g0) and not np.isnan(g4) and g0 > g4)
    if value_half and gpm_turn:
        return dict(status="BUY", mode="ACCUMULATE", primary="PB", value=pb, reference=ref,
                    reason=f"CONFIRMED: PB {pb:.2f}<MA1Y {pbma:.2f} AND GPM turn {g0:.3f}>{g4:.3f} (high-beta, size small)")
    if not value_half:
        return dict(status="RICH_WAIT", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"PB {pb:.2f} >= MA1Y {pbma:.2f} (not cheap vs history)")
    # value present, GPM-turn absent -> ARMED if hog-feed early-warning supportive, else WATCH
    if feed_ok and np.isfinite(spread_yoy) and spread_yoy > 0:
        return dict(status="ARMED", mode="", primary="PB", value=pb, reference=ref,
                    reason=f"value ✓ (PB {pb:.2f}<MA1Y), GPM-turn ✗ ({g0:.3f}<= {g4:.3f}) but hog-FEED spread +{spread_yoy:.3f} supportive")
    return dict(status="WATCH", mode="", primary="PB", value=pb, reference=ref,
                reason=f"value ✓ (PB {pb:.2f}<MA1Y {pbma:.2f}), GPM-turn ✗ ({g0:.3f}<= {g4:.3f}), spread {spread_yoy:+.3f} not supportive")


# ----------------------------------------------------------------------------
def prior_status_file():
    """Most recent data/sector_lens_status_*.csv strictly before today's file."""
    todays = os.path.join(OUTDIR, f"sector_lens_status_{TODAY}.csv")
    files = sorted(glob.glob(os.path.join(OUTDIR, "sector_lens_status_*.csv")))
    files = [f for f in files if f != todays]
    return files[-1] if files else None


# ----------------------------------------------------------------------------
# 8L rating cross-check (job Taylor_20260706_082923). rating_8l.csv is produced by step [1] of
# pt_8l_daily.sh (same run, same day) — the 8L composite-v3 quality gate (rating<=3 investable;
# rating<=2 = golden/strong tier). The sector-lens (a per-name valuation/timing screen) and the
# 8L rating (a cross-sectional fundamental-quality rank) are TWO INDEPENDENT systems. When both
# agree on the SAME name — 8L rating<=2 AND sector-lens says BUY — that is a genuine two-system
# consensus, flagged "✓✓ DOUBLE-CONFIRM". We deliberately do NOT interpret any other combination
# (rating>2 + BUY, or rating<=2 + RICH/WATCH/EXCLUDED): the rating is shown next to every name for
# reference only, no derived narrative from a single disagreeing data point (per dispatch req 3c).
RATING_CSV = os.path.join(OUTDIR, "rating_8l.csv")


def load_ratings():
    """ticker -> int rating from the fresh rating_8l.csv (same-day step [1]). Missing file/name
    -> empty dict / no entry (cross-check simply shows 'R?'); never fabricate a rating."""
    if not os.path.exists(RATING_CSV):
        return {}
    try:
        rdf = pd.read_csv(RATING_CSV, usecols=["ticker", "rating"])
    except Exception:
        return {}
    out = {}
    for _, r in rdf.iterrows():
        rt = _f(r["rating"])
        if np.isfinite(rt):
            out[str(r["ticker"])] = int(rt)
    return out


STATUS_EMO = {"BUY": "🟢", "ARMED": "🔵", "WATCH": "👀",
              "RICH_WAIT": "🟡", "EXCLUDED": "⛔", "STALE": "⚠️"}


def _rating_tag(tk, status, ratings):
    """'R2 ✓✓' when 8L golden/strong (rating<=2) AND sector-lens BUY; else 'R2' / 'R?'."""
    rt = ratings.get(tk)
    if rt is None:
        return "R?"
    double = (rt <= 2 and status == "BUY")
    return f"R{rt} ✓✓" if double else f"R{rt}"


def build_telegram_message(df, transitions, prior, state, spread_yoy, feed_ok, feed_asof, ratings):
    """Compose the daily sector-lens Telegram (HTML). Order per dispatch req 3:
      (a) transitions FIRST (the point of a daily read) — or 'no transitions today';
      (b) current-status table — full detail on BUY/ARMED always; WATCH/RICH/EXCLUDED shown in
          full only when there IS a transition, else collapsed to a count line (avoid daily spam);
      (c) 8L-rating cross-check inline per name, ✓✓ DOUBLE-CONFIRM when rating<=2 AND BUY."""
    # DT5G `state` column is 1-based (1=CRISIS..5=EX-BULL; NEUTRAL=3 per KB), matching cheap_pb_floor.py.
    slbl = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}.get(state["state"], "?")
    L = [f"<b>🔭 SECTOR LENS (Nhóm A) — {TODAY}</b>",
         f"DT5G: <b>{slbl}</b>({state['state']}) · hog-feed spread "
         f"{spread_yoy:+.3f}{'' if feed_ok else ' (STALE)'}"]

    # (a) transitions
    if not prior:
        L.append("\n<b>⚡ Chuyển trạng thái:</b> <i>(baseline run — no prior file)</i>")
    elif transitions:
        L.append(f"\n<b>⚡ CHUYỂN TRẠNG THÁI ({len(transitions)}):</b>")
        for tk, a, b in transitions:
            L.append(f"🔀 <b>{tk}</b>: {a} → <b>{b}</b>")
    else:
        L.append("\n<b>⚡ Chuyển trạng thái:</b> <i>no transitions today</i>")

    # (b)+(c) status table. df already sorted BUY->ARMED->WATCH->RICH_WAIT->EXCLUDED->STALE.
    def line(r):
        cur = r["status"] + (f"·{r['buy_mode']}" if r["buy_mode"] else "")
        tag = _rating_tag(r["ticker"], r["status"], ratings)
        emo = STATUS_EMO.get(r["status"], "•")
        bold = "<b>" + r["ticker"] + "</b>" if r["status"] in ("BUY", "ARMED") else r["ticker"]
        return f"{emo} {bold} {r['sector']} <b>{cur}</b> {tag}"

    actionable = df[df["status"].isin(["BUY", "ARMED"])]
    rest = df[~df["status"].isin(["BUY", "ARMED"])]
    L.append("\n<b>📋 BUY / ARMED:</b>")
    if actionable.empty:
        L.append("<i>(none today)</i>")
    else:
        for _, r in actionable.iterrows():
            L.append(line(r))

    show_rest_full = bool(transitions)   # full detail only when something moved
    if show_rest_full and not rest.empty:
        L.append("\n<b>📋 WATCH / RICH_WAIT / EXCLUDED / STALE:</b>")
        for _, r in rest.iterrows():
            L.append(line(r))
    elif not rest.empty:
        # collapsed count line (no transition day) + list any DOUBLE-CONFIRM-adjacent WATCH for ref
        counts = rest["status"].value_counts().to_dict()
        summ = " · ".join(f"{STATUS_EMO.get(k,'•')}{k} {v}" for k, v in
                          sorted(counts.items(), key=lambda kv: kv[0]))
        L.append(f"\n<b>📋 Khác:</b> {summ}")

    L.append("\n<i>✓✓ DOUBLE-CONFIRM = 8L rating≤2 (golden/strong) VÀ sector-lens BUY — 2 hệ độc "
             "lập cùng đồng thuận. R# = 8L rating (tham khảo). Đây là công cụ research/monitor: "
             "BUY vẫn phải qua Taylor→DollarBill→user→Mafee.</i>")
    return "\n".join(L)


def send_telegram(msg):
    """Reuse the same telegram_recommend.send_telegram_text + load_config wiring as
    cheap_pb_floor.py / rank_8l_daily_alert.py (same bot_token/chat_id = the 8L research channel)."""
    try:
        from telegram_recommend import send_telegram_text, load_config
        cfg = load_config()
        res = send_telegram_text(cfg["bot_token"], cfg["chat_id"], msg)
        print("telegram:", res.get("ok"))
        return res.get("ok", False)
    except Exception as e:
        print("telegram skipped:", e)
        return False


def compute_status():
    """Load caches, evaluate every Group-A name, diff vs the most recent prior status file, and
    persist data/sector_lens_status_<date>.csv. Returns everything a caller needs to RENDER (df,
    transitions, prior, state, feed context, per-row transition label) — deliberately medium-
    agnostic so multiple reports reuse ONE evaluation (pt_8l_daily --telegram; newdeals_daily_report
    Discord). Raises on cache-read failure; the caller decides how to fail (main() exits, a report
    fails gracefully without sending a misleading message). Extracted from main() 2026-07-06
    (job Taylor_20260706_091624) — evaluation logic unchanged."""
    names = [n[0] for n in NAMES]
    val, fin, state = load_data(names)

    spread_yoy, feed_asof = dbc_hog_feed_spread()
    feed_ok = feed_asof is not None and (TODAY - feed_asof).days <= FEED_STALE_DAYS

    prior_path = prior_status_file()
    prior = {}          # ticker -> status (for the fail-safe hold text)
    prior_label = {}    # ticker -> "STATUS·MODE" (transition key: a conviction upgrade
                        # inside BUY, e.g. CTR ACCUMULATE->STRONG on EVEB<9, IS alert-worthy)
    if prior_path:
        pdf = pd.read_csv(prior_path)
        prior = dict(zip(pdf["ticker"], pdf["status"]))
        pmode = dict(zip(pdf["ticker"], pdf.get("buy_mode", pd.Series(dtype=object))))
        prior_label = {tk: st + (f"·{pmode[tk]}" if isinstance(pmode.get(tk), str) and pmode[tk] else "")
                       for tk, st in prior.items()}

    state_stale = (TODAY - state["time"]).days > STATE_STALE_DAYS

    rows = []
    for tk, sector, key in NAMES:
        v = val.get(tk); f = fin.get(tk)
        stale_reason = ""
        if v is None or f is None:
            stale_reason = "missing ticker/financial row"
        else:
            page = (TODAY - pd.Timestamp(v["price_time"]).date()).days
            fage = (TODAY - pd.Timestamp(f["Release_Date"]).date()).days if pd.notna(f.get("Release_Date")) else 9999
            if page > PRICE_STALE_DAYS:
                stale_reason = f"price row {page}d stale (>{PRICE_STALE_DAYS})"
            elif fage > FIN_STALE_DAYS:
                stale_reason = f"financial {fage}d stale (>{FIN_STALE_DAYS})"
            elif key == "sec" and state_stale:
                stale_reason = f"DT5G state {(TODAY-state['time']).days}d stale"

        if stale_reason:
            # FAIL-SAFE: hold last known status, never fabricate
            held = prior.get(tk, "UNKNOWN")
            rows.append(dict(date=str(TODAY), ticker=tk, sector=sector,
                             status="STALE", buy_mode="", primary="", value=np.nan,
                             reference="", reason=f"{stale_reason}; holding last={held}",
                             held_status=held, price_asof="", fin_quarter=""))
            continue

        if key == "bank":
            r = eval_bank(tk, v, f)
        elif key == "fpt":
            r = eval_fpt(tk, v, f)
        elif key == "sec":
            r = eval_sec(tk, v, f, state)
        elif key == "ctr":
            r = eval_ctr(tk, v, f)
        elif key == "msh":
            r = eval_msh(tk, v, f)
        elif key == "dhg":
            r = eval_dhg(tk, v, f)
        elif key == "pvt":
            r = eval_pvt(tk, v, f)
        elif key == "hah":
            r = eval_hah(tk, v, f)
        elif key == "dbc":
            r = eval_dbc(tk, v, f, spread_yoy, feed_ok)
        else:
            continue

        rows.append(dict(date=str(TODAY), ticker=tk, sector=sector,
                         status=r["status"], buy_mode=r["mode"],
                         primary=r["primary"], value=round(_f(r["value"]), 3) if np.isfinite(_f(r["value"])) else "",
                         reference=r["reference"], reason=r["reason"],
                         held_status="", price_asof=str(pd.Timestamp(v["price_time"]).date()),
                         fin_quarter=str(f.get("quarter"))))

    df = pd.DataFrame(rows)

    order = {"BUY": 0, "ARMED": 1, "WATCH": 2, "RICH_WAIT": 3, "EXCLUDED": 4, "STALE": 5}
    df["_o"] = df["status"].map(order).fillna(9)
    df = df.sort_values(["_o", "sector", "ticker"]).drop(columns="_o").reset_index(drop=True)

    # ---- diff vs prior status file -> transitions + per-row transition label ----
    transitions = []
    trans_label = {}     # ticker -> console TRANSITION-column text
    for _, r in df.iterrows():
        cur = r["status"] + (f"·{r['buy_mode']}" if r["buy_mode"] else "")
        prev = prior_label.get(r["ticker"])
        if not prior:
            trans = "(baseline)"
        elif prev is None:
            trans = "NEW"
        elif prev != cur:
            trans = f">>> {prev}->{cur}"
            # a STALE in/out is a data-outage (view is "held, unchanged"), NOT a real state
            # change -> keep it out of the alert list to avoid training people to ignore alerts.
            if r["status"] != "STALE" and prior.get(r["ticker"]) != "STALE":
                transitions.append((r["ticker"], prev, cur))
        else:
            trans = "—"
        trans_label[r["ticker"]] = trans

    # ---- write status CSV (history for audit) ----
    outpath = os.path.join(OUTDIR, f"sector_lens_status_{TODAY}.csv")
    df.to_csv(outpath, index=False)

    return dict(df=df, transitions=transitions, prior=prior, prior_path=prior_path,
                state=state, spread_yoy=spread_yoy, feed_ok=feed_ok, feed_asof=feed_asof,
                trans_label=trans_label, outpath=outpath)


def main(telegram=False):
    try:
        r = compute_status()
    except Exception as e:
        print(f"[FATAL] cache read failed: {e}", file=sys.stderr)
        sys.exit(1)
    df, transitions, prior, prior_path = r["df"], r["transitions"], r["prior"], r["prior_path"]
    state, spread_yoy, feed_ok, feed_asof = r["state"], r["spread_yoy"], r["feed_ok"], r["feed_asof"]
    trans_label, outpath = r["trans_label"], r["outpath"]

    # ---- console table ----
    print("=" * 100)
    print(f"SECTOR LENS MONITOR — {TODAY}   DT5G state={state['state']} (asof {state['time']})"
          f"   hog-feed spread_yoy={spread_yoy:+.3f} (asof {feed_asof}){' STALE' if not feed_ok else ''}")
    print("=" * 100)
    hdr = f"{'TICKER':7s} {'SECTOR':14s} {'STATUS':10s} {'MODE':11s} {'PRIMARY':22s} {'TRANSITION':18s}"
    print(hdr); print("-" * len(hdr))
    for _, row in df.iterrows():
        prim = f"{row['primary']} {row['value']}" if row["value"] != "" else ""
        trans = trans_label.get(row["ticker"], "")
        print(f"{row['ticker']:7s} {row['sector']:14s} {row['status']:10s} {row['buy_mode']:11s} {prim:22s} {trans:18s}")
    print("-" * len(hdr))
    for _, row in df.iterrows():
        print(f"  {row['ticker']:5s} {row['status']:9s} {row['reason']}")

    print("\nwrote", outpath)

    # ---- data-staleness banner (fail-safe, not a state-change alert) ----
    stale_names = list(df[df["status"] == "STALE"]["ticker"])
    if stale_names:
        print("\n" + "!" * 100)
        print(f"DATA STALE ({len(stale_names)}): {', '.join(stale_names)} — holding last known status "
              f"(fail-safe; refresh the BQ cache / feeds). NOT counted as state transitions.")
        print("!" * 100)

    # ---- transition summary (the alert condition) ----
    print("\n" + "=" * 100)
    if not prior:
        print("BASELINE RUN — no prior status file; no transitions to report. "
              "Next run diffs against this file.")
    elif transitions:
        print(f"*** {len(transitions)} STATE TRANSITION(S) — ALERT-WORTHY ***  (prior: {os.path.basename(prior_path)})")
        for tk, a, b in transitions:
            print(f"    {tk}: {a} -> {b}")
    else:
        print(f"NO state transitions vs {os.path.basename(prior_path)} — all names held. (silent, logged only)")
    print("=" * 100)

    # ---- Telegram (opt-in; pt_8l_daily.sh step [9] passes --telegram) ----
    if telegram:
        ratings = load_ratings()
        if not ratings:
            print("[telegram] rating_8l.csv missing/unreadable — sending without 8L cross-check (R? shown).")
        msg = build_telegram_message(df, transitions, prior, state, spread_yoy, feed_ok, feed_asof, ratings)
        send_telegram(msg)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--telegram", action="store_true",
                    help="send the daily status + transitions + 8L cross-check to the 8L Telegram channel")
    a = ap.parse_args()
    main(telegram=a.telegram)
