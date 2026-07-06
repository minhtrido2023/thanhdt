#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dc_book_waterfall_paper.py — PAPER-TRADING the NEUTRAL idle-cash WATERFALL sleeve.

User APPROVED 2026-07-06 (dispatch Taylor_20260706_132553) after the waterfall research
(job Taylor_20260706_125540: "DC-below-BAL/LAG CONFIRMED, +~1pp/yr full-V2.4 / +3.5pp
SpaceX-now, insurance-grade DSR 0.775"). This is IMPLEMENTATION of an approved paper trial,
NOT more research — same gated-flag pattern as the two prior paper trials
(`extreme_regime_enabled`, `chase_cap_vol_scale_enabled`): default OFF everywhere, ON only on
the paper account `main` (override in secrets/trading_bot_accounts.json).

WHAT THE WATERFALL IS (exactly as the dispatch/research fixed it — nothing invented here):
  When DT5G state = NEUTRAL and BAL/LAG have NO qualifying deal at plan-build time, the idle
  cash is filled in priority order:
      BAL / LAG (unchanged, upstream)  →  DC book (ConvergePort double-confirm)  →  custom30V
  DC book = names where 8L rating ≤ 2 (golden/strong) AND sector_lens_monitor says BUY
  (the exact double-confirm signal, read live — no re-implementation), equal-weight, each
  capped 0.20 of the sleeve, DHG hard-EXCLUDED from active rebalancing (capacity §6.1: DHG's
  thin ADV drags the full-universe ceiling to ~2B; ex-DHG the sleeve deploys ~10-15B — the
  same `excluded_tickers` reasoning used for ZaloPay/DGC). Whatever the DC book does not
  absorb (thin set → 0.20 cap binds → idle) parks in custom30V.
  When BAL/LAG get a qualifying deal back → REVERSE-UNWIND: sell custom30V first, DC book
  second, cash goes back up to BAL/LAG (modelled here as the sleeve returning to flat/cash,
  since BAL/LAG deployment lives upstream of this sleeve).

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
CUSTOM30V = "CUSTOM30V"                 # pseudo-ticker for the parking aggregate
EXCLUDED_DEFAULT = ("DHG",)             # DHG excluded from active DC rebalancing (capacity §6.1)
CAP_PER_NAME = 0.20                     # 0.20 of sleeve NAV per DC name
TC = 0.001                             # 0.1% per unit one-way turnover (matches backtest §3)
ACCOUNT_DEFAULT = "main"
FLAG = "dc_book_waterfall_enabled"


# ======================================================================================
# PURE CORE — deterministic, no I/O. This is what the stress-test exercises directly.
# ======================================================================================

def compute_waterfall_targets(state, bal_lag_has_deal, dc_set,
                              excluded=EXCLUDED_DEFAULT, cap_per_name=CAP_PER_NAME):
    """The waterfall allocation, as a pure function.

    Args:
      state            : int DT5G state code (NEUTRAL == 3).
      bal_lag_has_deal : bool — do BAL/LAG have a qualifying deal at plan-build time?
      dc_set           : {ticker: buy_mode} live double-confirm set (8L≤2 ∧ sector-lens BUY).
      excluded         : iterable of tickers held-not-traded (DHG) → out of active book.
      cap_per_name     : per-name weight cap (0.20).

    Returns (target_weights, deployed, reason):
      target_weights : {ticker: weight, ..., CUSTOM30V: w} summing to ≤ 1.0 (rest = cash),
                       or {} when the sleeve is flat.
      deployed       : bool — is any idle cash deployed by the waterfall this step?
      reason         : short human string for the audit trail.

    Waterfall is NEUTRAL-only (per dispatch). Outside NEUTRAL, or when BAL/LAG have a deal,
    the sleeve is flat (cash) — the idle cash is claimed upstream (BAL/LAG) or the regime is
    not the one this mechanism serves.
    """
    if state != NEUTRAL:
        return {}, False, "not-NEUTRAL → sleeve flat (waterfall is a NEUTRAL-only mechanism)"
    if bal_lag_has_deal:
        return {}, False, "BAL/LAG has qualifying deal → idle cash → BAL/LAG (sleeve unwound to cash)"

    excl = {t.upper() for t in excluded}
    active = {t: m for t, m in (dc_set or {}).items() if t.upper() not in excl}
    if not active:
        # NEUTRAL, BAL/LAG dry, but no double-confirm name today → 100% custom30V.
        # (This is NOT a defect: an empty DC day = full parking = automatic safety — the
        # UNION experiment that tried to "fix" empty days was REFUTED, framework §7.)
        return {CUSTOM30V: 1.0}, True, "NEUTRAL, BAL/LAG dry, no DC name → 100% custom30V"

    n = len(active)
    w = min(cap_per_name, 1.0 / n)
    tgt = {t: w for t in active}
    active_frac = w * n
    park = round(max(0.0, 1.0 - active_frac), 10)
    if park > 1e-9:
        tgt[CUSTOM30V] = park
    reason = (f"NEUTRAL, BAL/LAG dry → DC {n} names @ {w:.4f} each "
              f"(active {active_frac:.3f}) + custom30V {park:.3f}")
    return tgt, True, reason


def build_orders(prev_w, target_w):
    """Ordered order list to move sleeve from prev_w → target_w, encoding the dispatch
    priority explicitly for the audit trail:
      SELLS first (custom30V before DC book — reverse-unwind order),
      BUYS  after (DC book before custom30V — deploy waterfall order).
    Weights are top-level sleeve fractions; CUSTOM30V is the parking aggregate pseudo-ticker.
    Returns list of {side, ticker, dw} with dw > 0 (magnitude of weight change)."""
    prev_w = prev_w or {}
    target_w = target_w or {}
    names = set(prev_w) | set(target_w)

    sells, buys = [], []
    for t in names:
        d = round(target_w.get(t, 0.0) - prev_w.get(t, 0.0), 10)
        if d < -1e-9:
            sells.append({"side": "sell", "ticker": t, "dw": -d})
        elif d > 1e-9:
            buys.append({"side": "buy", "ticker": t, "dw": d})

    def _sell_key(o):    # custom30V sold first, then DC by size desc
        return (0 if o["ticker"] == CUSTOM30V else 1, -o["dw"])

    def _buy_key(o):     # DC bought first, then custom30V
        return (1 if o["ticker"] == CUSTOM30V else 0, -o["dw"])

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
            "flag": FLAG,
            "account": ACCOUNT_DEFAULT,
            "start_date": None,
            "nav_basis_vnd": basis,
            "excluded": list(EXCLUDED_DEFAULT),
            "cap_per_name": CAP_PER_NAME,
            "tc_per_turnover": TC,
            "priority": "BAL/LAG → DC book (double-confirm, ex-DHG) → custom30V",
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
        "weights": {},            # top-level sleeve weights (DC names + CUSTOM30V)
        "last_close": {},         # {dc_ticker: close, CUSTOM30V: basket_index}
        "custom30v_basket": {},   # composition used for the parking index
        "history": [],
    }


def _basket_index(basket, closes):
    """Synthetic custom30V unit price = Σ weight·Close over available constituents (renormalised
    to the covered weight so a missing name doesn't silently deflate the index)."""
    num = cov = 0.0
    for t, w in (basket or {}).items():
        c = closes.get(t)
        if c is not None:
            num += w * c
            cov += w
    if cov <= 0:
        return None
    return num / cov


def advance(account=ACCOUNT_DEFAULT):
    """Advance the sleeve to the freshest available close (one step). Idempotent per data_date.
    Returns (status_str, state_dict). status ∈ {disabled, no_data, held, advanced, unchanged}."""
    if not sleeve_enabled(account):
        return "disabled", None

    st = _load_state() or _init_state(nav_basis(account))

    state, state_name, bal_lag = load_trigger()
    dc_set = load_double_confirm()               # None on failure
    basket, rebal_date = load_custom30v_basket()  # {} on failure

    # names we may need prices for = current holdings ∪ prospective DC set ∪ basket
    prospective = set(dc_set or {}) | set(st.get("weights", {}))
    prospective.discard(CUSTOM30V)
    prospective |= set(basket or {})
    closes, data_date = latest_closes(prospective)

    if data_date is None:
        return "no_data", st                      # price cache unreadable → do nothing safely

    # idempotent: already advanced for this close
    if st.get("clock_date") == data_date and st.get("history"):
        return "unchanged", st

    prev_w = dict(st.get("weights", {}))
    prev_close = dict(st.get("last_close", {}))
    prev_basket = dict(st.get("custom30v_basket", {}))
    nav = float(st.get("nav_vnd", st["meta"]["nav_basis_vnd"]))
    first = not st.get("history")

    # ---- 1) mark-to-market: return earned by YESTERDAY's weights over the new close ----
    gross_r = 0.0
    if not first:
        for t, w in prev_w.items():
            if w <= 0:
                continue
            if t == CUSTOM30V:
                new_idx = _basket_index(prev_basket, closes)
                old_idx = prev_close.get(CUSTOM30V)
                if new_idx is not None and old_idx:
                    gross_r += w * (new_idx / old_idx - 1.0)
            else:
                c0, c1 = prev_close.get(t), closes.get(t)
                if c0 and c1:
                    gross_r += w * (c1 / c0 - 1.0)

    # ---- 2) fail-safe: if the DC signal is unavailable, HOLD prior allocation ----
    fail_safe_hold = dc_set is None
    if fail_safe_hold:
        target_w, deployed, reason = prev_w, st.get("deployed", False), \
            "FAIL-SAFE: double-confirm set unavailable → hold prior allocation (no rebalance)"
    else:
        target_w, deployed, reason = compute_waterfall_targets(
            state if state is not None else -1,
            bool(bal_lag) if bal_lag is not None else False,
            dc_set)
        if bal_lag is None or state is None:
            # trigger unreadable → do not deploy on a guess; hold prior (fail-safe)
            target_w, deployed = prev_w, st.get("deployed", False)
            reason = "FAIL-SAFE: trigger (state/BAL-LAG) unreadable → hold prior allocation"

    # ---- 2b) if custom30V parking is required but its basket is missing → park as CASH ----
    if target_w.get(CUSTOM30V, 0.0) > 0 and not basket:
        park = target_w.pop(CUSTOM30V)
        reason += f" | custom30V basket unavailable → {park:.3f} held as CASH (degraded)"
        deployed = deployed and bool(target_w)

    # ---- 3) turnover cost + NAV update ----
    to = 0.0 if first else turnover(prev_w, target_w)
    tc_cost = to * TC
    net_r = gross_r - tc_cost
    nav = nav * (1.0 + net_r)

    orders = [] if first else build_orders(prev_w, target_w)
    reverse_unwind = (st.get("deployed", False) and not deployed
                      and any(o["side"] == "sell" for o in orders))

    # ---- 4) record new sleeve state ----
    new_close = {t: closes[t] for t in target_w if t != CUSTOM30V and t in closes}
    if target_w.get(CUSTOM30V, 0.0) > 0:
        idx = _basket_index(basket, closes)
        if idx is not None:
            new_close[CUSTOM30V] = idx

    dc_names = sorted(t for t in target_w if t != CUSTOM30V)
    row = {
        "date": data_date,
        "state": state, "state_name": state_name,
        "bal_lag_has_deal": bal_lag,
        "deployed": deployed,
        "dc_names": dc_names,
        "dc_weight_each": round(target_w.get(dc_names[0], 0.0), 4) if dc_names else 0.0,
        "c30v_weight": round(target_w.get(CUSTOM30V, 0.0), 4),
        "cash_weight": round(max(0.0, 1.0 - sum(target_w.values())), 4),
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
    st["custom30v_basket"] = basket if target_w.get(CUSTOM30V, 0.0) > 0 else {}
    if st["meta"]["start_date"] is None:
        st["meta"]["start_date"] = data_date
    st["history"].append(row)

    _save_state(st)
    _append_nav_csv(row)
    return "advanced", st


def _append_nav_csv(row):
    header = ("date,state_name,bal_lag_has_deal,deployed,n_dc,dc_weight_each,"
              "c30v_weight,cash_weight,sleeve_ret_pct,nav_vnd,cum_pnl_pct,reverse_unwind\n")
    exists = os.path.exists(NAV_CSV)
    line = (f"{row['date']},{row['state_name']},{row['bal_lag_has_deal']},{row['deployed']},"
            f"{len(row['dc_names'])},{row['dc_weight_each']},{row['c30v_weight']},"
            f"{row['cash_weight']},{row['sleeve_ret_pct']},{row['nav_vnd']},"
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
        L = ["### 🪜 DC-book NEUTRAL Waterfall — Paper Sleeve"]
        L.append(f"*Ưu tiên tiền rảnh NEUTRAL: BAL/LAG → DC book (double-confirm, ex-DHG) → custom30V "
                 f"| flag `{FLAG}`=ON (chỉ paper `{account}`) | as-of {last.get('date','?')}*")
        L.append("")

        if not last:
            L.append("*(chưa có phiên nào được ghi)*")
            return "\n".join(L)

        deployed = last.get("deployed")
        bal_lag = last.get("bal_lag_has_deal")
        regime = last.get("state_name", "?")
        if regime != "NEUTRAL":
            trig = f"regime **{regime}** (≠NEUTRAL) → sleeve FLAT (waterfall chỉ chạy ở NEUTRAL)"
        elif bal_lag:
            trig = "NEUTRAL, **BAL/LAG CÓ deal** → tiền rảnh về BAL/LAG, sleeve unwound"
        else:
            trig = "NEUTRAL, **BAL/LAG rỗng** → waterfall DEPLOY"
        L.append(f"- Trạng thái hôm nay: {trig}")

        dc = last.get("dc_names") or []
        if deployed:
            L.append(f"- DC book ({len(dc)}): {', '.join(dc) if dc else '—'} "
                     f"@ {last.get('dc_weight_each',0)*100:.1f}%/tên "
                     f"| custom30V {last.get('c30v_weight',0)*100:.1f}% "
                     f"| cash {last.get('cash_weight',0)*100:.1f}%")
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
