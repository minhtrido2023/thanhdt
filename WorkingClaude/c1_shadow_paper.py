#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""c1_shadow_paper.py — PAPER-ONLY shadow NAV tracker for C1 (state-conditional BULL-only
LAG->DC book swap). Job Taylor_20260825_170138 (Việc 2), dispatch Mike, user đã duyệt tầng 1
(DC state-adaptive plan) 2026-08-25. RESEARCH/MONITOR ONLY — does not touch production code,
trading_rules.json, the allocator, or any real nav_history_<account>.csv.

WHY THIS EXISTS: research job Taylor_20260825_153800 (P3_A_backtest_c1_stateswap.md) backtested
C1 on 2014-2026 history and found it net-positive but UNDER-POWERED to wire — only N=10
independent BULL episodes in 11.9 years, below the DSR/PBO significance threshold, and the whole
net benefit concentrated OOS. Recommendation was "theo dõi" (monitor), not GO/NO-GO. This script
is that monitor: it runs the SAME two-bucket mechanism the backtest validated
(exp_dc3book_c1_stateswap_20260825.py), but forward, on REAL live data, so every future BULL
episode adds a genuine (not backtested) data point to N.

MECHANISM (mirrors exp_dc3book_c1_stateswap_20260825.py's sim_c1_stateswap() exactly):
  Two dollar buckets, V_bal + V_slot. V_bal always earns r_BAL(t). V_slot earns r_LAG(t) outside
  BULL, r_DC(t) inside BULL (state==4). Target w_slot(t) = production's REAL w_lag_target(t)
  (read live from data/golive_v23_status.json — the same file dc_book_waterfall_paper.py already
  treats as its trigger source, i.e. this literally reads what production computed today, not a
  reimplementation). Band ±10pp around target (BAND). Turnover cost TC=0.1%/side (0.2%
  round-trip) charged on V_slot's full dollar value on every regime flip (LAG<->DC), same
  worst-case no-overlap assumption as the backtest (different tickers, no netting credit).

DC LEG — REAL, uses Việc 1 hygiene (job Taylor_20260825_170138 same dispatch): imports
dc_book_waterfall_paper's live double-confirm loader + membership/weight functions directly
(dc_membership/dc_weights/EXCLUDED_DEFAULT/PER_NAME_CAP) — ex-DHG/MSH, per-name capacity caps for
the 10 CAP_NEEDED names. Unlike that sleeve's compute_waterfall_targets(), this does NOT blend in
the custom30V park leg for the unfilled residual — the C1 backtest's r_DC definition
(build_dc_returns() in exp_dc3book_20260825.py) only parks residual cash in NEUTRAL state, and
this leg only matters in BULL, so any unfilled residual (capped-out names) is plain CASH (0%)
here, matching that definition exactly.

*** KNOWN LIMITATION — r_BAL/r_LAG are proxied by VNINDEX daily return, NOT real book returns. ***
Checked before deciding this (2026-08-26): production does not persist any live per-book (BAL or
LAG) daily NAV/return series anywhere this script can read cheaply.
  - `recommend_v23.recommendations` (BQ, canonical daily picks) book=BAL has only 1 row/day
    (today's single top pick, not the full held book); book=LAG has been EMPTY for 2 weeks
    (checked 2026-08-26: last LAG row 2026-08-12) — neither is a book-NAV series.
  - `data/lag_edge_health.csv` is PER-TRADE realized returns at exit, not a daily mark-to-market
    curve.
  - The only place a real nav_bal_ref/nav_lag_ref series exists is pt_v23_audit_2014.py's own
    backtest output — a full 2014→now re-run, too heavy to invoke as a daily EOD cron step and
    not a live-updating file.
Consequence: on every NON-BULL day this shadow's return == VNINDEX return exactly (no alpha
claimed for BAL or LAG — both sides of the trade are the same proxy, so they cancel). Only on a
BULL day does the DC-vs-VNINDEX-proxy delta become a genuine live signal. This is sufficient to
keep accumulating real forward BULL-episode evidence (the actual gap the backtest flagged), but
NOT sufficient to reproduce production's absolute NAV level — do not read this CSV's nav_vnd as
"what V2.4 would have made." If genuine book-level fidelity is wanted later, that is a separate,
larger scope (replicate the BAL/LAG selection+holding engine live) — flag to Mike/user, don't
silently upgrade this script to claim it.

State/CSV are entirely self-contained (own 1B basis, own state file) — same pattern as
dc_book_waterfall_paper.py's paper sleeve, chosen for consistency and because there is no real
paper/live account this shadow is meant to represent.
"""
import os
import sys
import json

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
if WORKDIR not in sys.path:
    sys.path.insert(0, WORKDIR)

import dc_book_waterfall_paper as dcw   # reuse Việc-1-hygienized DC engine (surgical: no reimpl)

DATA_DIR = os.path.join(WORKDIR, "data")
STATUS_FILE = os.path.join(DATA_DIR, "golive_v23_status.json")
STATE_FILE = os.path.join(DATA_DIR, "c1_shadow_paper_state.json")
NAV_CSV = os.path.join(DATA_DIR, "nav_history_shadow_c1.csv")   # NOT nav_history_<account>.csv —
                                                                 # never touches production (§8)

BULL_STATE = 4                  # DT5G state coding: 1 CRISIS,2 BEAR,3 NEUTRAL,4 BULL,5 EXBULL
NAV_BASIS = 1_000_000_000.0     # paper 1B, same convention as dc_book_waterfall_paper.py
TC = 0.001                      # 0.1% one-way — CLAUDE.md standard, matches dcw.TC
BAND = 0.10                     # ±10pp — matches exp_dc3book_c1_stateswap_20260825.py BAND
JOB_ID = "Taylor_20260825_170138"


# ======================================================================================
# LOADERS — all fail-safe: None/empty on any failure, never raise into advance()
# ======================================================================================

def load_state_and_wlag(status_file=STATUS_FILE):
    """(state:int|None, state_name:str, w_lag_target:float|None) from the REAL production
    status snapshot (data/golive_v23_status.json — same file dc_book_waterfall_paper.py's
    load_trigger() reads, state_source=DT5G_macro). None on any failure → caller fails safe."""
    try:
        with open(status_file, encoding="utf-8") as f:
            s = json.load(f)
        state = int(s.get("state"))
        name = str(s.get("state_name", "?"))
        wl = s.get("w_lag_target")
        wl = float(wl) if wl is not None else None
        return state, name, wl
    except Exception:
        return None, "?", None


def load_vnindex_close():
    """(close:float|None, data_date:str|None) — VNINDEX is a per-row mirror column on every
    ticker in the bq_cache `ticker` parquet (same source dcw.latest_closes() reads), not its own
    ticker row; read it off a liquid, always-present name (ACB)."""
    try:
        import duckdb
        con = duckdb.connect(); con.execute("SET threads=1")
        df = con.execute(f"""
            SELECT time, VNINDEX FROM read_parquet('{dcw.BQ_CACHE}/ticker/*.parquet')
            WHERE ticker = 'ACB' ORDER BY time DESC LIMIT 1""").df()
        con.close()
        if df.empty or df["VNINDEX"].iloc[0] != df["VNINDEX"].iloc[0]:   # NaN check
            return None, None
        return float(df["VNINDEX"].iloc[0]), str(df["time"].iloc[0])
    except Exception:
        return None, None


def dc_book_weights_today():
    """dict|None — Việc-1-hygienized DC book (ex-DHG/MSH, per-name capacity caps), equal-weight-
    then-capped. Reuses dc_book_waterfall_paper's live loaders directly, no reimplementation.
    None on failure (double-confirm signal unreadable) → caller carries forward yesterday's set."""
    dc_set = dcw.load_double_confirm()
    if dc_set is None:
        return None
    liq = dcw.load_liquidity(set(dc_set))
    members, _floor_active, _dropped = dcw.dc_membership(dc_set, liq)
    return dcw.dc_weights(members, dcw.CAP_PER_NAME, dcw.PER_NAME_CAP)


# ======================================================================================
# STATE I/O (atomic)
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
    os.replace(tmp, STATE_FILE)   # atomic


def _init_state():
    return {
        "meta": {
            "name": "C1 shadow paper tracker — state-conditional BULL-only LAG->DC swap",
            "job": JOB_ID,
            "start_date": None,
            "nav_basis_vnd": NAV_BASIS,
            "tc_per_side": TC,
            "band": BAND,
            "mechanism": "V_bal always r_BAL-proxy(VNINDEX); V_slot = r_LAG-proxy(VNINDEX) "
                         "outside BULL, r_DC (real, Việc-1-hygienized book) inside BULL. Target "
                         "w_slot = production's REAL w_lag_target(t) (data/golive_v23_status.json)"
                         ", band ±10pp, flip cost 0.1%/side on regime change — same method as "
                         "exp_dc3book_c1_stateswap_20260825.py (P3_A), continued forward LIVE.",
            "known_limitation": "r_BAL/r_LAG proxied by VNINDEX daily return, NOT real book "
                                "returns — production persists no live per-book NAV series "
                                "(checked: recommend_v23.recommendations book=BAL is a 1-row/day "
                                "'top pick' not the full book, book=LAG empty since 2026-08-12; "
                                "lag_edge_health.csv is per-trade realized, not a daily MTM curve"
                                "). r_DC IS real. Non-BULL days: shadow == VNINDEX exactly (BAL/"
                                "LAG proxies cancel). Only BULL-day DC-vs-VNINDEX delta is a "
                                "genuine live signal — sufficient to accumulate real forward "
                                "BULL-episode N (P3_A: only N=10 backtest episodes, below DSR/PBO"
                                " threshold), NOT sufficient to reproduce production's absolute "
                                "NAV. True book-level fidelity = separate, larger scope.",
            "approved": "user 2026-08-25 (tầng 1 DC state-adaptive plan), dispatch " + JOB_ID,
            "scope": "PAPER — research/monitor only, touches no production file",
        },
        "clock_date": None,
        "regime": None,                 # "DC" | "LAG"
        "V_bal": None,
        "V_slot": None,
        "last_vnindex_close": None,
        "last_dc_weights": {},
        "last_dc_closes": {},
        "history": [],
    }


# ======================================================================================
# FORWARD MTM STEP
# ======================================================================================

def advance():
    """Advance the shadow to the freshest available VNINDEX close (one step). Idempotent per
    data_date. Returns (status_str, state_dict). status ∈ {no_data, unchanged, advanced}."""
    st = _load_state() or _init_state()

    state, state_name, w_lag_tgt = load_state_and_wlag()
    vnindex_close, data_date = load_vnindex_close()
    dc_w_today = dc_book_weights_today()   # None on failure → carried forward below

    if vnindex_close is None or data_date is None:
        return "no_data", st

    if st.get("clock_date") == data_date and st.get("history"):
        return "unchanged", st

    fail_safe = state is None or w_lag_tgt is None
    first = not st.get("history")

    # r_DC(t): yesterday's DC weights, priced forward to today's closes (matches
    # build_dc_returns()'s W.loc[dprev] * stock_ret.loc[d] convention — weights fixed at prior
    # day, one-day-forward price move; missing price for a held name -> that slice earns 0%,
    # same fail-safe convention as dc_book_waterfall_paper.advance()'s r_i=0.0 fallback).
    prev_dc_w = st.get("last_dc_weights", {})
    prev_dc_c = st.get("last_dc_closes", {})
    r_dc = 0.0
    dc_closes_now = {}
    if prev_dc_w or dc_w_today:
        want = set(prev_dc_w) | set(dc_w_today or {})
        dc_closes_now, _ = dcw.latest_closes(want)
    if prev_dc_w and not first:
        for t, w in prev_dc_w.items():
            c0, c1 = prev_dc_c.get(t), dc_closes_now.get(t)
            r_i = (c1 / c0 - 1.0) if (c0 and c1) else 0.0
            r_dc += w * r_i

    prev_vn = st.get("last_vnindex_close")
    r_bal_proxy = (vnindex_close / prev_vn - 1.0) if (prev_vn and not first) else 0.0
    r_lag_proxy = r_bal_proxy   # same VNINDEX proxy — documented limitation, see module docstring

    n_flip_today = False
    n_rebal_today = False
    flip_cost = 0.0
    rebal_cost = 0.0

    if first:
        w0 = w_lag_tgt if w_lag_tgt is not None else 0.5   # 0.50 = allocator's own fail-safe dft
        V_bal = NAV_BASIS * (1.0 - w0)
        V_slot = NAV_BASIS * w0
        regime = "DC" if (state == BULL_STATE) else "LAG"
        gross_r = 0.0
    else:
        V_bal = float(st["V_bal"]); V_slot = float(st["V_slot"])
        prev_total = V_bal + V_slot
        regime = st.get("regime", "LAG")

        target_regime = regime if fail_safe else ("DC" if state == BULL_STATE else "LAG")
        n_flip_today = (target_regime != regime)
        if n_flip_today:
            flip_cost = V_slot * TC * 2.0
            regime = target_regime

        r_slot = r_dc if regime == "DC" else r_lag_proxy
        V_bal = V_bal * (1.0 + r_bal_proxy)
        V_slot = (V_slot - flip_cost) * (1.0 + r_slot)
        total = V_bal + V_slot
        gross_r = (total / prev_total - 1.0) if prev_total > 0 else 0.0

        w_slot = V_slot / total if total > 0 else 0.0
        w_slot_tgt = w_lag_tgt if w_lag_tgt is not None else w_slot   # fail-safe: no rebal target
        if not fail_safe and abs(w_slot - w_slot_tgt) > BAND:
            moved = abs(V_slot - total * w_slot_tgt)
            rebal_cost = moved * TC
            total_after = total - rebal_cost
            V_bal = (1.0 - w_slot_tgt) * total_after
            V_slot = w_slot_tgt * total_after
            n_rebal_today = True

    total_cost = flip_cost + rebal_cost
    new_total = V_bal + V_slot
    prev_total_for_ret = (float(st["V_bal"]) + float(st["V_slot"])) if not first else NAV_BASIS
    net_r = (new_total / prev_total_for_ret - 1.0) if prev_total_for_ret > 0 else 0.0

    # self-check 0 VND leak (§ quant-research skill) — V_bal/V_slot are constructed to sum
    # exactly to new_total by algebra above; assert defensively rather than trust it silently.
    leak = abs((V_bal + V_slot) - new_total)
    assert leak < 1e-6, f"C1 shadow leak {leak} VND — bucket sum != total, do not trust this row"

    row = {
        "date": data_date,
        "state": state, "state_name": state_name,
        "fail_safe": fail_safe,
        "regime": regime,
        "w_lag_target": w_lag_tgt,
        "w_slot_actual": round(V_slot / new_total, 6) if new_total > 0 else None,
        "r_bal_proxy_pct": round(r_bal_proxy * 100, 4),
        "r_lag_proxy_pct": round(r_lag_proxy * 100, 4),
        "r_dc_pct": round(r_dc * 100, 4),
        "n_dc_names": len(dc_w_today) if dc_w_today else 0,
        "flip_today": n_flip_today,
        "rebal_today": n_rebal_today,
        "flip_cost_vnd": round(flip_cost),
        "rebal_cost_vnd": round(rebal_cost),
        "gross_ret_pct": round(gross_r * 100, 4),
        "net_ret_pct": round(net_r * 100, 4),
        "V_bal_vnd": round(V_bal),
        "V_slot_vnd": round(V_slot),
        "nav_vnd": round(new_total),
        "cum_pnl_pct": round((new_total / NAV_BASIS - 1.0) * 100, 4),
        "vnindex_close": vnindex_close,
    }

    st["clock_date"] = data_date
    st["regime"] = regime
    st["V_bal"] = V_bal
    st["V_slot"] = V_slot
    st["last_vnindex_close"] = vnindex_close
    if dc_w_today:                      # only overwrite membership on a successful fresh load —
        st["last_dc_weights"] = dc_w_today          # fail-safe: keep yesterday's set on failure
        st["last_dc_closes"] = {t: dc_closes_now[t] for t in dc_w_today if t in dc_closes_now}
    elif prev_dc_w:
        st["last_dc_closes"] = {t: dc_closes_now.get(t, prev_dc_c.get(t)) for t in prev_dc_w}
    if st["meta"]["start_date"] is None:
        st["meta"]["start_date"] = data_date
    st["history"].append(row)

    _save_state(st)
    _append_nav_csv(row)
    return "advanced", st


def _append_nav_csv(row):
    import csv
    cols = ["date", "state", "state_name", "fail_safe", "regime", "w_lag_target",
            "w_slot_actual", "r_bal_proxy_pct", "r_lag_proxy_pct", "r_dc_pct", "n_dc_names",
            "flip_today", "rebal_today", "flip_cost_vnd", "rebal_cost_vnd", "gross_ret_pct",
            "net_ret_pct", "V_bal_vnd", "V_slot_vnd", "nav_vnd", "cum_pnl_pct", "vnindex_close"]
    is_new = not os.path.exists(NAV_CSV)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NAV_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if is_new:
            w.writeheader()
        w.writerow(row)


def main():
    status, st = advance()
    print(f"c1_shadow_paper: {status}")
    if status == "advanced" and st.get("history"):
        last = st["history"][-1]
        print(f"  date={last['date']} state={last['state_name']} regime={last['regime']} "
              f"w_lag_tgt={last['w_lag_target']} nav={last['nav_vnd']:,} "
              f"cum_pnl={last['cum_pnl_pct']}% n_dc={last['n_dc_names']} "
              f"flip={last['flip_today']} rebal={last['rebal_today']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
