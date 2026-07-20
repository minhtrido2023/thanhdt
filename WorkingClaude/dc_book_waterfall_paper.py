#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dc_book_waterfall_paper.py — PAPER-TRADING the NEUTRAL idle-cash WATERFALL sleeve.

User APPROVED 2026-07-06 (dispatch Taylor_20260706_132553) after the waterfall research
(job Taylor_20260706_125540: "DC-below-BAL/LAG CONFIRMED, +~1pp/yr full-V2.4 / +3.5pp
SpaceX-now, insurance-grade DSR 0.775"). This is IMPLEMENTATION of an approved paper trial,
NOT more research — same gated-flag pattern as the two prior paper trials
(`extreme_regime_enabled`, `chase_cap_vol_scale_enabled`): default OFF everywhere, ON only on
the paper account `main` (override in secrets/trading_bot_accounts.json).

*** v2 — 2026-07-20 (job Taylor_20260720_091731, user approved fixing NOW, not at the review
    milestone). Four changes, all reverting to specs ALREADY backtested and pinned; no new
    research, no re-declared N-trials, DSR 0.775 "insurance-grade" characterisation unchanged:
      #1 CONTINUOUS-RESIDUAL trigger (the real bug — v1 flattened the whole sleeve whenever
         BAL/LAG had a deal; the pinned spec never goes flat). job Taylor_20260713_100550.
      #2 q2m5 rebalance cadence (was daily) — same/better result at ~1/4 churn. job _20260706_173317.
      #3 combined DC+custom30V cap 0.15/name (5/8 DC names overlapped the basket). job _20260707_042827.
      #4 liquidity floor 3B on Trading_Value_1M_P50, replacing the DHG hard-exclude. job _20260707_042827.
    v1 ran 26/06→17/07 at cum −7.12% (worse than VNINDEX −4.51% and worse than no-DC-book
    baseline). Its NAV series is ARCHIVED to data/dc_book_waterfall_paper_nav_v1.csv and v2
    restarts from the 1B basis — a mechanism change means a new track record, and compounding a
    known-buggy stretch forward would make the v2 numbers uninterpretable. ***

WHAT THE WATERFALL IS (exactly as the dispatch/research fixed it — nothing invented here):
  When DT5G state = NEUTRAL, the parked idle cash is filled in priority order:
      BAL / LAG (unchanged, upstream)  →  DC book (ConvergePort double-confirm)  →  custom30V
  DC book = names where 8L rating ≤ 2 (golden/strong) AND sector_lens_monitor says BUY
  (the exact double-confirm signal, read live — no re-implementation), equal-weight, each
  capped 0.20 of the sleeve, membership additionally requiring Trading_Value_1M_P50 ≥ 3B (v2
  #4 — the floor removes DHG on its own merit; capacity §6.1: DHG's thin ADV drags the
  full-universe ceiling to ~2B, ex-DHG the sleeve deploys ~10-15B). Whatever the DC book does
  not absorb (thin set → 0.20 cap binds) parks in custom30V, and any single name's COMBINED
  DC+custom30V exposure is capped at 0.15 (v2 #3).
  This sleeve MODELS THE PARKED FRACTION ITSELF. BAL/LAG taking cash back shrinks that
  fraction upstream; it does NOT flatten the sleeve's allocation (v2 #1). The sleeve goes flat
  only when the regime leaves NEUTRAL.

MODEL. This is a self-contained forward paper sleeve (like converge_report.py's DC-book paper,
but modelling the *waterfall allocation* rather than a static seed book). It is NOT wired into
the live executor or the production plan builder — it advances one step per fresh close, marks
to market, writes an auditable state file, and renders a report section. It touches NO
production trading file (custom30V / BAL / LAG / rating_8l.py / executor / plan builder).

  Trigger source   : data/golive_v23_status.json  (live V2.4 status: state, n_bal, n_lag_*)
  DC book source   : sector_lens_monitor.compute_status() + load_ratings()  (double-confirm)
  Parking source   : tav2_bq.custom30v_8l  (bq_cache/custom30v_8l.parquet, latest rebal)
  Prices / MTM     : bq_cache/ticker/*.parquet latest Close per name (same as converge_report)
  State file       : data/dc_book_waterfall_paper_state.json   (audit; atomic write)
  NAV series       : data/dc_book_waterfall_paper_nav.csv

Usage:
  python dc_book_waterfall_paper.py --update            # advance sleeve one step (idempotent/date)
  python dc_book_waterfall_paper.py --section           # advance-if-needed + print report markdown
  python dc_book_waterfall_paper.py --show              # dump current state file
  (generate_section() is importable for the EOD report — see bin/eod_trading_report.sh handoff.)
"""

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

WORKDIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(WORKDIR, "data")
BQ_CACHE = os.path.join(DATA_DIR, "bq_cache")
STATE_FILE = os.path.join(DATA_DIR, "dc_book_waterfall_paper_state.json")
NAV_CSV = os.path.join(DATA_DIR, "dc_book_waterfall_paper_nav.csv")
STATUS_FILE = os.path.join(DATA_DIR, "golive_v23_status.json")

NEUTRAL = 3
CUSTOM30V = "CUSTOM30V"                 # legacy pseudo-ticker (v1 aggregate) — kept for report labels
EXCLUDED_DEFAULT = ("DHG",)             # v2: only a FALL-BACK when the liquidity floor is unreadable
CAP_PER_NAME = 0.20                     # 0.20 of sleeve NAV per DC name (DC layer cap)
OVERLAP_CAP = 0.15                      # v2 fix#3: combined DC+custom30V cap per name (job _042827)
LIQ_FLOOR_VND = 3_000_000_000.0         # v2 fix#4: Trading_Value_1M_P50 floor 3B (job _042827)
TC = 0.001                             # 0.1% per unit one-way turnover (matches backtest §3)
ACCOUNT_DEFAULT = "main"
FLAG = "dc_book_waterfall_enabled"
SLEEVE_VERSION = "v2"                   # v2 = post trigger-bug fix (2026-07-20, job Taylor_20260720_091731)


# ======================================================================================
# PURE CORE — deterministic, no I/O. This is what the stress-test exercises directly.
# ======================================================================================

def dc_membership(dc_set, liq=None, liq_floor=LIQ_FLOOR_VND, excluded=EXCLUDED_DEFAULT):
    """v2 fix#4 — DC book membership = double-confirm ∧ Trading_Value_1M_P50 ≥ liq_floor.

    The liquidity floor REPLACES the DHG hard-exclude (job Taylor_20260707_042827: the floor
    improved both IS and OOS, and removes DHG on its own merit rather than by name). Fail-safe,
    exactly as the backtest: a name whose TV is missing does NOT clear the floor. If the whole
    liquidity map is unreadable (liq is None) we fall back to the v1 hard-exclude list rather
    than silently dropping the floor — degrading to the older, stricter behaviour, never to a
    looser one.

    Returns (members:dict, floor_active:bool, dropped:list).
    """
    src = dict(dc_set or {})
    if liq is None:
        excl = {t.upper() for t in excluded}
        members = {t: m for t, m in src.items() if t.upper() not in excl}
        return members, False, sorted(set(src) - set(members))
    members = {t: m for t, m in src.items()
               if isinstance(liq.get(t), (int, float)) and liq[t] >= liq_floor}
    return members, True, sorted(set(src) - set(members))


def apply_overlap_cap(base, basket_members, cap=OVERLAP_CAP, passes=12):
    """v2 fix#3 — cap COMBINED per-name weight (DC leg + custom30V leg) at `cap`, redistributing
    the trimmed excess to current custom30V basket members that still have headroom; whatever
    cannot be placed falls to cash. Port of `dc_overlap_cap_backtest.eff_cap` (job _042827),
    same iterate-until-placed loop, same members-only redistribution rule.

    Args:
      base            : {ticker: combined weight} before capping.
      basket_members  : set of tickers in the CURRENT custom30V basket (redistribution targets).
    Returns (capped:dict, residual_cash:float).
    """
    row = dict(base)
    residual = 0.0
    for _ in range(passes):
        excess = sum(max(0.0, w - cap) for w in row.values())
        if excess <= 1e-12:
            break
        row = {t: min(w, cap) for t, w in row.items()}
        head = {t: cap - row.get(t, 0.0) for t in basket_members if cap - row.get(t, 0.0) > 1e-12}
        H = sum(head.values())
        if H <= 1e-12:
            residual += excess          # nowhere to place it → cash
            break
        placed = 0.0
        for t, h in head.items():
            add = min(h, h / H * excess)
            row[t] = row.get(t, 0.0) + add
            placed += add
        if excess - placed > 1e-12:
            residual += excess - placed  # headroom exhausted mid-pass → cash
            break
    else:
        # passes exhausted with excess still present → trim it to cash rather than loop forever
        residual += sum(max(0.0, w - cap) for w in row.values())
        row = {t: min(w, cap) for t, w in row.items()}
    return {t: w for t, w in row.items() if w > 1e-12}, round(residual, 10)


def compute_waterfall_targets(state, dc_set, basket, liq=None,
                              cap_per_name=CAP_PER_NAME, overlap_cap=OVERLAP_CAP,
                              liq_floor=LIQ_FLOOR_VND, excluded=EXCLUDED_DEFAULT):
    """The waterfall allocation, as a pure function — v2 (post trigger-bug fix 2026-07-20).

    v2 fix#1 (CONTINUOUS-RESIDUAL): the DC book runs on the residual parked cash EVERY NEUTRAL
    session. It is NOT switched off when BAL/LAG have a deal. The v1 binary trigger
    (`bal_lag_has_deal → sleeve FLAT`) under-implemented the pinned spec: the backtest that
    approved this sleeve is `vehicle(flat_mask=None)` in dc_trigger_gap_backtest.py — the vehicle
    never goes flat, it simply rides whatever fraction of NAV is parked at the time (the overlay's
    `w_park_prev`). Measured cost of the binary version: edge-capture 43% of the continuous spec,
    i.e. WORSE than no DC book at all (27.26% vs baseline 27.35% CAGR, job Taylor_20260713_100550).
    The sleeve here models the parked fraction itself, so "BAL/LAG took cash back" shrinks the
    sleeve's real-world notional upstream — it does not flatten the sleeve's allocation.

    Args:
      state        : int DT5G state code (NEUTRAL == 3).
      dc_set       : {ticker: buy_mode} live double-confirm set (8L≤2 ∧ sector-lens BUY).
      basket       : {ticker: weight} current custom30V basket (the parking leg).
      liq          : {ticker: Trading_Value_1M_P50} or None (→ fall back to hard-exclude).

    Returns (target_weights, deployed, reason, detail):
      target_weights : {ticker: COMBINED effective weight} summing to ≤ 1.0 (rest = cash).
                       v2 resolves the parking leg PER NAME (no CUSTOM30V pseudo-ticker), because
                       the overlap cap can only be applied on combined per-name exposure.
      detail         : dict of leg decomposition for the audit trail.
    """
    if state != NEUTRAL:
        return {}, False, "not-NEUTRAL → sleeve flat (waterfall is a NEUTRAL-only mechanism)", {}

    members, floor_active, dropped = dc_membership(dc_set, liq, liq_floor, excluded)
    n = len(members)
    w_dc = min(cap_per_name, 1.0 / n) if n else 0.0
    dc_frac = w_dc * n
    park_frac = round(max(0.0, 1.0 - dc_frac), 10)

    bk = {t: w for t, w in (basket or {}).items() if w > 0}
    bk_tot = sum(bk.values())
    base = {t: w_dc for t in members}
    if bk_tot > 0 and park_frac > 1e-9:
        for t, w in bk.items():
            base[t] = base.get(t, 0.0) + park_frac * (w / bk_tot)

    capped, residual = apply_overlap_cap(base, set(bk), overlap_cap)
    cash = round(max(0.0, 1.0 - sum(capped.values())), 10)
    overlap = sorted(set(members) & set(bk))

    if not n:
        # No double-confirm name today → 100% custom30V. NOT a defect: an empty DC day = full
        # parking = automatic safety (the UNION experiment that tried to "fix" it was REFUTED).
        reason = "NEUTRAL, no DC name clears double-confirm(+floor) → 100% custom30V"
    else:
        reason = (f"NEUTRAL continuous-residual → DC {n} names @ {w_dc:.4f} "
                  f"(leg {dc_frac:.3f}) + custom30V {park_frac:.3f}; "
                  f"overlap-cap {overlap_cap:.2f} on {len(overlap)} shared name(s)")
    if not bk:
        reason += f" | custom30V basket unavailable → {park_frac:.3f} held as CASH (degraded)"
    if floor_active and dropped:
        reason += f" | liq-floor {liq_floor/1e9:.0f}B dropped {','.join(dropped)}"
    elif not floor_active:
        reason += " | ⚠ liq map unreadable → fell back to hard-exclude " + ",".join(excluded)

    detail = {
        "dc_leg": round(dc_frac, 6), "park_leg": round(park_frac, 6),
        "cash": cash, "cap_residual": residual,
        "overlap_names": overlap, "floor_active": floor_active, "floor_dropped": dropped,
        "dc_weight_each": round(w_dc, 6), "dc_names": sorted(members),
    }
    return capped, bool(capped), reason, detail


def build_orders(prev_w, target_w, dc_names=None):
    """Ordered order list to move sleeve from prev_w → target_w, encoding the dispatch
    priority explicitly for the audit trail:
      SELLS first (custom30V-only names before DC book — reverse-unwind order),
      BUYS  after (DC book before custom30V — deploy waterfall order).
    v2: weights are COMBINED per-name effective weights, so "the custom30V leg" is identified by
    `dc_names` (everything not in it is parking-only). The legacy CUSTOM30V pseudo-ticker still
    sorts as parking so v1 state/tests keep their ordering semantics.
    Returns list of {side, ticker, dw} with dw > 0 (magnitude of weight change)."""
    prev_w = prev_w or {}
    target_w = target_w or {}
    names = set(prev_w) | set(target_w)
    dc = set(dc_names or ())

    def _is_park(t):
        return t == CUSTOM30V or (t not in dc if dc else t == CUSTOM30V)

    sells, buys = [], []
    for t in names:
        d = round(target_w.get(t, 0.0) - prev_w.get(t, 0.0), 10)
        if d < -1e-9:
            sells.append({"side": "sell", "ticker": t, "dw": -d})
        elif d > 1e-9:
            buys.append({"side": "buy", "ticker": t, "dw": d})

    def _sell_key(o):    # parking sold first, then DC by size desc
        return (0 if _is_park(o["ticker"]) else 1, -o["dw"])

    def _buy_key(o):     # DC bought first, then parking
        return (1 if _is_park(o["ticker"]) else 0, -o["dw"])

    sells.sort(key=_sell_key)
    buys.sort(key=_buy_key)
    return sells + buys


def turnover(prev_w, target_w):
    """One-way turnover = 0.5·Σ|Δw| (sum of buys == sum of sells for a self-financed book;
    a flat→deploy or deploy→flat move is one-sided so 0.5·Σ|Δw| is the traded fraction)."""
    prev_w = prev_w or {}
    target_w = target_w or {}
    names = set(prev_w) | set(target_w)
    return 0.5 * sum(abs(target_w.get(t, 0.0) - prev_w.get(t, 0.0)) for t in names)


# ======================================================================================
# FAIL-SAFE I/O WRAPPERS — every one degrades to None/empty, never raises, never fabricates.
# ======================================================================================

def load_trigger(status_file=STATUS_FILE):
    """→ (state:int|None, state_name:str, bal_lag_has_deal:bool|None). None state / None
    bal_lag → caller must fail-safe (hold prior sleeve, do not rebalance on missing trigger)."""
    try:
        with open(status_file, encoding="utf-8") as f:
            s = json.load(f)
        state = int(s.get("state"))
        name = str(s.get("state_name", "?"))
        # A qualifying BAL/LAG deal that would consume idle cash T+1 = a new BAL entry
        # (n_bal>0) or a LAG position coming due (n_lag_upcoming>0). n_lag_recent = already
        # deployed, not competing for *new* idle cash → excluded from the trigger.
        n_bal = int(s.get("n_bal", 0) or 0)
        n_lag_up = int(s.get("n_lag_upcoming", 0) or 0)
        return state, name, (n_bal > 0 or n_lag_up > 0)
    except Exception:
        return None, "?", None


def load_double_confirm():
    """Live double-confirm set {ticker: buy_mode}. None on any failure (→ fail-safe hold).
    Identical selection to converge_report._live_double_confirm (8L≤2 ∧ sector-lens BUY)."""
    try:
        import sector_lens_monitor as slm
        r = slm.compute_status()
        ratings = slm.load_ratings()
        df = r["df"]
        out = {}
        for _, row in df[df["status"] == "BUY"].iterrows():
            rt = ratings.get(row["ticker"])
            if rt is not None and int(rt) <= 2:
                out[str(row["ticker"])] = row["buy_mode"] or "ACCUMULATE"
        return out
    except Exception:
        return None


def load_custom30v_basket():
    """Latest custom30V basket {ticker: weight} + rebal_date. ({}, None) on failure."""
    try:
        import duckdb
        con = duckdb.connect(); con.execute("SET threads=1")
        p = os.path.join(BQ_CACHE, "custom30v_8l.parquet")
        df = con.execute(f"""
            SELECT ticker, weight FROM read_parquet('{p}')
            WHERE rebal_date = (SELECT MAX(rebal_date) FROM read_parquet('{p}'))""").df()
        rd = con.execute(f"SELECT MAX(rebal_date) m FROM read_parquet('{p}')").fetchone()[0]
        con.close()
        return {str(r["ticker"]): float(r["weight"]) for _, r in df.iterrows()}, str(rd)
    except Exception:
        return {}, None


def load_liquidity(tickers):
    """v2 fix#4 — {ticker: Trading_Value_1M_P50} latest row per name from the prune cache.
    None on any failure (→ dc_membership falls back to the hard-exclude list, never to a
    looser rule). Names simply absent from the result do not clear the floor."""
    if not tickers:
        return {}
    try:
        import duckdb
        con = duckdb.connect(); con.execute("SET threads=1")
        q = ",".join(f"'{t}'" for t in sorted(set(tickers)))
        df = con.execute(f"""
            WITH r AS (SELECT ticker, Trading_Value_1M_P50 tv,
                       ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) rn
                       FROM read_parquet('{BQ_CACHE}/ticker_prune/*.parquet')
                       WHERE ticker IN ({q}))
            SELECT ticker, tv FROM r WHERE rn=1""").df()
        con.close()
        return {str(r["ticker"]): float(r["tv"]) for _, r in df.iterrows()
                if r["tv"] is not None and float(r["tv"]) == float(r["tv"])}
    except Exception:
        return None


def latest_closes(tickers):
    """{ticker: Close} (latest row per ticker) + data_date. ({}, None) on failure."""
    if not tickers:
        return {}, None
    try:
        import duckdb
        con = duckdb.connect(); con.execute("SET threads=1")
        q = ",".join(f"'{t}'" for t in sorted(set(tickers)))
        df = con.execute(f"""
            WITH r AS (SELECT ticker, time, Close,
                       ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) rn
                       FROM read_parquet('{BQ_CACHE}/ticker/*.parquet')
                       WHERE ticker IN ({q}))
            SELECT ticker, time, Close FROM r WHERE rn=1""").df()
        con.close()
        px = {str(r["ticker"]): float(r["Close"]) for _, r in df.iterrows()}
        dd = str(df["time"].max()) if not df.empty else None
        return px, dd
    except Exception:
        return {}, None


# ======================================================================================
# ACCOUNT / FLAG GATING
# ======================================================================================

def sleeve_enabled(account=ACCOUNT_DEFAULT):
    """True only when the resolved account has dc_book_waterfall_enabled=True. Fail-safe:
    any config error → False (do nothing). This is the negative-control guarantee — SpaceX
    and any live account resolve to False and this sleeve never touches them."""
    try:
        sys.path.insert(0, WORKDIR)
        from trading_bot.config import load_config, load_accounts, pick_accounts
        prof = pick_accounts(load_accounts(load_config()), [account])[0]
        return bool(prof["cfg"].get(FLAG, False))
    except Exception:
        return False


def nav_basis(account=ACCOUNT_DEFAULT):
    """Sleeve notional basis (VND) — the paper account's cash basis, scaled to the real paper
    NAV. Falls back to 1B if config unreadable."""
    try:
        sys.path.insert(0, WORKDIR)
        from trading_bot.config import load_config, load_accounts, pick_accounts
        prof = pick_accounts(load_accounts(load_config()), [account])[0]
        return float(prof["cfg"].get("paper_init_cash", 1_000_000_000))
    except Exception:
        return 1_000_000_000.0


# ======================================================================================
# STATE I/O (atomic) + FORWARD MTM SIMULATOR
# ======================================================================================

def _load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def _save_state(st):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)  # atomic


def _init_state(basis):
    return {
        "meta": {
            "name": "DC-book NEUTRAL idle-cash Waterfall — Paper Sleeve",
            "version": SLEEVE_VERSION,
            "version_note": "v2 (2026-07-20, job Taylor_20260720_091731): continuous-residual "
                            "trigger + q2m5 rebalance cadence + overlap cap 0.15 + liq floor 3B. "
                            "v1 (26/06→17/07, cum −7.12%) ran a BINARY trigger that "
                            "under-implemented the pinned spec — its NAV series is archived at "
                            "data/dc_book_waterfall_paper_nav_v1.csv, NOT compounded into v2.",
            "flag": FLAG,
            "account": ACCOUNT_DEFAULT,
            "start_date": None,
            "nav_basis_vnd": basis,
            "excluded_fallback": list(EXCLUDED_DEFAULT),
            "cap_per_name": CAP_PER_NAME,
            "overlap_cap": OVERLAP_CAP,
            "liq_floor_vnd": LIQ_FLOOR_VND,
            "rebal_cadence": "q2m5 (follows the custom30V basket rebal_date; no daily churn)",
            "tc_per_turnover": TC,
            "priority": "BAL/LAG → DC book (double-confirm, liq≥3B) → custom30V (continuous residual)",
            "capacity_note": "standalone-sleeve capacity ~10-15B ex-DHG (framework §6.1); "
                             "non-binding at paper NAV",
            "approved": "user 2026-07-06 (job Taylor_20260706_132553); research "
                        "Taylor_20260706_125540 DSR0.775 insurance-grade",
            "scope": "PAPER — research/monitor, not an order; touches no production trading file",
        },
        "clock_date": None,       # data_date of the last advance (sim clock)
        "nav_vnd": basis,
        "cum_pnl_pct": 0.0,
        "deployed": False,
        "reverse_unwind_last": False,
        "weights": {},            # v2: COMBINED effective per-name weights (drift between rebals)
        "last_close": {},         # {ticker: close} for every held name
        "rebal_date": None,       # custom30V rebal_date the current target was built on (q2m5)
        "history": [],
    }


def advance(account=ACCOUNT_DEFAULT):
    """Advance the sleeve to the freshest available close (one step). Idempotent per data_date.
    Returns (status_str, state_dict). status ∈ {disabled, no_data, held, advanced, unchanged}."""
    if not sleeve_enabled(account):
        return "disabled", None

    st = _load_state() or _init_state(nav_basis(account))

    state, state_name, bal_lag = load_trigger()
    dc_set = load_double_confirm()               # None on failure
    basket, rebal_date = load_custom30v_basket()  # {} on failure
    liq = load_liquidity(set(dc_set or {}))      # None on failure → hard-exclude fallback

    # names we may need prices for = current holdings ∪ prospective DC set ∪ basket
    prospective = set(dc_set or {}) | set(st.get("weights", {})) | set(basket or {})
    prospective.discard(CUSTOM30V)
    closes, data_date = latest_closes(prospective)

    if data_date is None:
        return "no_data", st                      # price cache unreadable → do nothing safely

    # idempotent: already advanced for this close
    if st.get("clock_date") == data_date and st.get("history"):
        return "unchanged", st

    prev_w = dict(st.get("weights", {}))
    prev_close = dict(st.get("last_close", {}))
    nav = float(st.get("nav_vnd", st["meta"]["nav_basis_vnd"]))
    first = not st.get("history")

    # ---- 1) mark-to-market + DRIFT: yesterday's weights earn today's per-name return, then
    # the weights themselves drift with those returns (v2: no daily snap-back to target —
    # the parking leg drifts between rebalances exactly as the pinned backtest models it).
    gross_r = 0.0
    grown = {}
    if not first:
        for t, w in prev_w.items():
            if w <= 0:
                continue
            c0, c1 = prev_close.get(t), closes.get(t)
            r_i = (c1 / c0 - 1.0) if (c0 and c1) else 0.0
            gross_r += w * r_i
            grown[t] = w * (1.0 + r_i)
    drifted = ({t: v / (1.0 + gross_r) for t, v in grown.items()}
               if grown and abs(1.0 + gross_r) > 1e-12 else dict(prev_w))

    # ---- 2) decide whether to REBALANCE this session (v2 fix#2: q2m5 cadence) ----
    # Membership/target is refreshed ONLY when the custom30V basket rebalances (q2m5, the same
    # schedule custom30V itself uses — job Taylor_20260706_173317: equal-or-better result at
    # ~1/4 the churn), on the first session, or when the regime crosses the NEUTRAL boundary
    # (a flat↔deployed transition can't wait for a quarterly date). NOT on a BAL/LAG deal —
    # that binary trigger was the v1 bug (fix#1).
    fail_safe_hold = dc_set is None or state is None
    want_deployed = (state == NEUTRAL)
    regime_flip = want_deployed != bool(st.get("deployed", False))
    cadence_due = (rebal_date is not None and rebal_date != st.get("rebal_date"))
    do_rebal = (not fail_safe_hold) and (first or regime_flip or cadence_due)

    if fail_safe_hold:
        target_w, deployed = drifted, st.get("deployed", False)
        reason = ("FAIL-SAFE: " + ("double-confirm set" if dc_set is None else "DT5G state")
                  + " unavailable → hold prior allocation (no rebalance)")
        detail = {}
    elif do_rebal:
        target_w, deployed, reason, detail = compute_waterfall_targets(state, dc_set, basket, liq)
        reason = ("REBAL[" + ("first" if first else "regime-flip" if regime_flip else "q2m5")
                  + "] " + reason)
    else:
        target_w, deployed = drifted, st.get("deployed", False)
        detail = {}
        reason = (f"HOLD (no rebal — cadence q2m5, next on a new basket rebal_date; "
                  f"current {rebal_date}); weights drifting")

    # ---- 3) turnover cost + NAV update ----
    to = 0.0 if first else turnover(drifted, target_w)
    tc_cost = to * TC
    net_r = gross_r - tc_cost
    nav = nav * (1.0 + net_r)

    orders = [] if first else build_orders(drifted, target_w, detail.get("dc_names"))
    reverse_unwind = (st.get("deployed", False) and not deployed
                      and any(o["side"] == "sell" for o in orders))

    # ---- 4) record new sleeve state ----
    new_close = {t: closes[t] for t in target_w if t in closes}

    # on a HOLD/fail-safe session the membership was not refreshed → carry the stored set forward
    dc_names = detail.get("dc_names", st.get("dc_names", []))
    row = {
        "date": data_date,
        "state": state, "state_name": state_name,
        "bal_lag_has_deal": bal_lag,          # informational only in v2 (no longer a trigger)
        "deployed": deployed,
        "rebalanced": bool(do_rebal),
        "dc_names": dc_names,
        "dc_weight_each": detail.get("dc_weight_each", 0.0),
        "dc_leg": detail.get("dc_leg", 0.0),
        "c30v_weight": detail.get("park_leg", 0.0),
        "cash_weight": round(max(0.0, 1.0 - sum(target_w.values())), 4),
        "overlap_names": detail.get("overlap_names", []),
        "cap_residual": detail.get("cap_residual", 0.0),
        "floor_active": detail.get("floor_active"),
        "floor_dropped": detail.get("floor_dropped", []),
        "gross_ret_pct": round(gross_r * 100, 4),
        "turnover": round(to, 4),
        "tc_pct": round(tc_cost * 100, 4),
        "sleeve_ret_pct": round(net_r * 100, 4),
        "nav_vnd": round(nav),
        "cum_pnl_pct": round((nav / st["meta"]["nav_basis_vnd"] - 1.0) * 100, 4),
        "reverse_unwind": reverse_unwind,
        "fail_safe": fail_safe_hold,
        "custom30v_rebal": rebal_date,
        "note": reason,
        "orders": orders,
    }

    st["clock_date"] = data_date
    st["nav_vnd"] = nav
    st["cum_pnl_pct"] = round((nav / st["meta"]["nav_basis_vnd"] - 1.0) * 100, 4)
    st["deployed"] = deployed
    st["reverse_unwind_last"] = reverse_unwind
    st["weights"] = target_w
    st["last_close"] = new_close
    st["dc_names"] = dc_names
    if do_rebal and rebal_date is not None:
        st["rebal_date"] = rebal_date
    if st["meta"]["start_date"] is None:
        st["meta"]["start_date"] = data_date
    st["history"].append(row)

    _save_state(st)
    _append_nav_csv(row)
    return "advanced", st


def _append_nav_csv(row):
    header = ("date,state_name,bal_lag_has_deal,deployed,rebalanced,n_dc,dc_weight_each,"
              "dc_leg,c30v_weight,cash_weight,turnover,sleeve_ret_pct,nav_vnd,cum_pnl_pct,"
              "reverse_unwind\n")
    exists = os.path.exists(NAV_CSV)
    line = (f"{row['date']},{row['state_name']},{row['bal_lag_has_deal']},{row['deployed']},"
            f"{row.get('rebalanced')},{len(row['dc_names'])},{row['dc_weight_each']},"
            f"{row.get('dc_leg',0)},{row['c30v_weight']},"
            f"{row['cash_weight']},{row.get('turnover',0)},{row['sleeve_ret_pct']},{row['nav_vnd']},"
            f"{row.get('cum_pnl_pct','')},{row['reverse_unwind']}\n")
    try:
        with open(NAV_CSV, "a", encoding="utf-8") as f:
            if not exists:
                f.write(header)
            f.write(line)
    except Exception:
        pass


# ======================================================================================
# REPORT SECTION (importable by bin/eod_trading_report.sh)
# ======================================================================================

def _dcf_echo_line(dc_names, last_close, asof):
    """DCF check echo (Pha 2, informational — user directive 2026-07-15: kể cả paper) cho
    các mã double-confirm đang active. CHỈ hiển thị — không tham gia chọn mã/sizing của
    waterfall. Đọc cache local qua trading_bot.strategies._dcf_check_for_order (fail-safe
    NOT_COMPUTED, không BQ live). Trả "" khi lỗi/không có tên → caller bỏ dòng."""
    try:
        if not dc_names:
            return ""
        if WORKDIR not in sys.path:
            sys.path.insert(0, WORKDIR)
        from trading_bot.strategies import (_dcf_check_for_order, format_dcf_check,
                                            log_dcf_history)
        from dcf_valuation import DCF_DISCLAIMER
        parts = []
        for t in dc_names:
            px = last_close.get(t)
            if not isinstance(px, (int, float)) or px <= 0:
                parts.append(f"{t} NOT_COMPUTED (thiếu giá close trong state)")
                continue
            d = _dcf_check_for_order(t, px, asof)
            log_dcf_history(t, d, "dc_book_waterfall_paper", asof=asof)
            # side="paper": không kích đuôi "cần dcf_override_reason" (chỉ áp cho BUY order thật)
            s = format_dcf_check(d, side="paper", ticker=t)
            if s.startswith("DCF: NOT_COMPUTED"):
                s = s.replace("DCF: ", "", 1)          # gọn cho dòng gộp nhiều mã
            else:
                s = s.replace(" DCF: ", " ", 1)
            parts.append(f"{t} {s}")
        return ("- DCF check (informational, không tham gia chọn mã): " + " · ".join(parts)
                + f"\n  ℹ️ _{DCF_DISCLAIMER}_")
    except Exception:
        return ""


def generate_section(account=ACCOUNT_DEFAULT, do_advance=True):
    """Markdown section for the EOD report. Advances the sleeve first (idempotent) unless
    do_advance=False. Never raises — degrades to a single ⚠️ line (the caller must not abort)."""
    try:
        if not sleeve_enabled(account):
            return ""   # silently absent when the paper trial isn't enabled (e.g. live accounts)
        status, st = ("skipped", _load_state()) if not do_advance else advance(account)
        if st is None:
            return "⚠️ DC-book Waterfall (paper): chưa có state (chưa advance được — thiếu dữ liệu giá)."

        h = st.get("history") or []
        last = h[-1] if h else {}
        L = [f"### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve ({SLEEVE_VERSION})"]
        L.append(f"*Tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, liq≥"
                 f"{LIQ_FLOOR_VND/1e9:.0f}B) → custom30V, **continuous-residual** | cap gộp "
                 f"{OVERLAP_CAP:.2f}/tên · rebal q2m5 | flag `{FLAG}`=ON (chỉ paper `{account}`) "
                 f"| as-of {last.get('date','?')}*")
        L.append("")

        if not last:
            L.append("*(chưa có phiên nào được ghi)*")
            return "\n".join(L)

        deployed = last.get("deployed")
        bal_lag = last.get("bal_lag_has_deal")
        regime = last.get("state_name", "?")
        if regime != "NEUTRAL":
            trig = f"regime **{regime}** (≠NEUTRAL) → sleeve FLAT (waterfall chỉ chạy ở NEUTRAL)"
        else:
            trig = ("NEUTRAL → waterfall chạy LIÊN TỤC trên phần tiền dư"
                    + (" (BAL/LAG có deal hôm nay — v2 KHÔNG tắt sleeve, chỉ phần dư nhỏ lại)"
                       if bal_lag else " (BAL/LAG rỗng)"))
        L.append(f"- Trạng thái hôm nay: {trig}")
        L.append("- Nhịp rebal: " + ("**REBALANCE hôm nay** (q2m5/regime-flip)"
                                     if last.get("rebalanced") else
                                     "giữ nguyên, trọng số drift (q2m5 — chưa tới kỳ)"))

        dc = last.get("dc_names") or []
        if deployed:
            L.append(f"- DC book ({len(dc)}): {', '.join(dc) if dc else '—'} "
                     f"@ {last.get('dc_weight_each',0)*100:.1f}%/tên "
                     f"(leg {last.get('dc_leg',0)*100:.1f}%) "
                     f"| custom30V {last.get('c30v_weight',0)*100:.1f}% "
                     f"| cash {last.get('cash_weight',0)*100:.1f}%")
            ov = last.get("overlap_names") or []
            if ov:
                L.append(f"- Trùng mã DC↔custom30V ({len(ov)}): {', '.join(ov)} — cap gộp "
                         f"{OVERLAP_CAP*100:.0f}%/tên đã áp"
                         + (f", {last['cap_residual']*100:.2f}% không đặt được → cash"
                            if last.get("cap_residual", 0) > 1e-9 else ""))
            dropped = last.get("floor_dropped") or []
            if dropped:
                L.append(f"- Liq-floor {LIQ_FLOOR_VND/1e9:.0f}B loại: {', '.join(dropped)}")
            if last.get("floor_active") is False:
                L.append("- ⚠️ Không đọc được thanh khoản → fallback hard-exclude "
                         + ",".join(EXCLUDED_DEFAULT))
            dcf_line = _dcf_echo_line(dc, st.get("last_close") or {}, last.get("date"))
            if dcf_line:
                L.append(dcf_line)
        else:
            L.append("- Sleeve đang FLAT (0% deploy — không có tiền rảnh do sleeve này quản)")
        if last.get("reverse_unwind"):
            L.append("- 🔄 **REVERSE-UNWIND** hôm nay: bán custom30V trước, DC book sau (BAL/LAG lấy lại tiền)")
        if last.get("fail_safe"):
            L.append("- ⚠️ FAIL-SAFE: thiếu dữ liệu tín hiệu → giữ nguyên phân bổ, không rebalance")

        nav = st.get("nav_vnd", 0)
        basis = st["meta"]["nav_basis_vnd"]
        cum = st.get("cum_pnl_pct", 0.0)
        sign = "+" if cum >= 0 else ""
        L.append(f"- **P&L sleeve tích luỹ: {sign}{cum:.2f}%** "
                 f"(NAV {nav/1e9:.3f}B / cơ sở {basis/1e9:.3f}B, {len(h)} phiên) "
                 f"| ret hôm nay {last.get('sleeve_ret_pct',0):+.3f}% (sau TC {last.get('tc_pct',0):.3f}%)")
        L.append("*PAPER — theo dõi/kiểm định, không phải lệnh thật. State: "
                 "data/dc_book_waterfall_paper_state.json*")
        return "\n".join(L)
    except Exception as e:
        return f"⚠️ DC-book Waterfall (paper): section lỗi ({e}) — bỏ qua, không chặn báo cáo."


def main():
    ap = argparse.ArgumentParser(description="DC-book NEUTRAL idle-cash waterfall — paper sleeve")
    ap.add_argument("--account", default=ACCOUNT_DEFAULT)
    ap.add_argument("--update", action="store_true", help="advance one step (idempotent per close)")
    ap.add_argument("--section", action="store_true", help="advance-if-needed + print report markdown")
    ap.add_argument("--show", action="store_true", help="dump current state file")
    a = ap.parse_args()

    if a.show:
        st = _load_state()
        print(json.dumps(st, ensure_ascii=False, indent=2) if st else "(no state file)")
        return 0
    if a.section:
        print(generate_section(a.account, do_advance=True))
        return 0
    # default / --update
    status, st = advance(a.account)
    print(f"[dc_book_waterfall_paper] advance → {status}")
    if st and st.get("history"):
        print(json.dumps(st["history"][-1], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
