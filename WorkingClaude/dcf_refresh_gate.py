# -*- coding: utf-8 -*-
"""
dcf_refresh_gate.py — conditional monthly refresh gate for the DCF discount rate (Việc 2, job
Taylor_20260717_063638).

The DCF discount rate r = Big-4 12M deposit rate (deposit_rate_vn.py) + ERP. The deposit rate moves
in discrete steps and is only material to fair value when it moves a lot (§5: a 1pp r view ≈ ±10% FV).
So instead of recomputing DCF every month, this gate recomputes ONLY when the current Big-4 deposit
rate has moved >= 1.0 percentage point from the rate last used in a DCF run; otherwise it keeps the
existing numbers (skip). This is an OPERATIONAL mechanism, not a model change — nothing about the
valuation math is touched.

STATE  : data/dcf_refresh_state.json  (last_used_rate, last_used_date, last_check_date) — atomic write.
LOG    : data/dcf_refresh_gate.log    (append-only audit of every decision).
DECISION: |current_rate - last_used_rate| >= THRESHOLD_PP  → REFRESH (update last_used_rate/date)
                                            <  THRESHOLD_PP → SKIP    (update last_check_date only)
          first run / no state         → REFRESH (initialize).

BOUNDARY (=exactly 1.0pp): treated INCLUSIVE → REFRESH. The user's phrasing was ">1pp"; a strict
  reading would SKIP at exactly 1.0. Chosen INCLUSIVE deliberately because (a) a DCF recompute is
  cheap while a stale discount rate is the real risk, and (b) float equality (e.g. 6.8-5.8) is fragile
  to test with strict '>'. Flagged here so the user can flip to strict '>' (set THRESHOLD_INCLUSIVE
  = False) if preferred — this is the one judgment call in the gate.

This gate DECIDES + PERSISTS; it does not itself run the (cheap) DCF recompute. The consumer that
regenerates DCF numbers for a report/dashboard calls run_gate() first and only recomputes its
fair values when the returned dict has refresh=True. Fail-safe: any error → returns refresh=True
(recompute rather than silently serve stale on a broken gate) and logs the error.

Run: $DNA_PYEXE dcf_refresh_gate.py            # evaluate + persist + log (real)
     $DNA_PYEXE dcf_refresh_gate.py --dry      # evaluate + print only, no state/log write
     $DNA_PYEXE dcf_refresh_gate.py --show      # print current state
"""
import os, sys, json, argparse
from datetime import datetime, timezone

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
import deposit_rate_vn as _dep

STATE_FP = f"{WORKDIR}/data/dcf_refresh_state.json"
LOG_FP = f"{WORKDIR}/data/dcf_refresh_gate.log"
THRESHOLD_PP = 1.0                 # percentage-point band
THRESHOLD_INCLUSIVE = True         # exactly 1.0pp → refresh (see BOUNDARY note above)
_EPS = 1e-9


def _now_ict_date(asof=None):
    """Return the as-of date string. `asof` overridable for tests; else today (UTC date is fine —
    the gate is monthly-granularity, no intraday boundary sensitivity)."""
    if asof is not None:
        return str(asof)[:10]
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_state(path=STATE_FP):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return None
    return None


def _atomic_write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _triggers(delta):
    if THRESHOLD_INCLUSIVE:
        return delta >= THRESHOLD_PP - _EPS
    return delta > THRESHOLD_PP + _EPS


def decide(current_rate, state):
    """Pure decision: return (refresh_bool, reason, delta_or_None) given the current deposit rate
    and prior state dict (or None). No I/O."""
    if state is None or "last_used_rate" not in state:
        return True, "first_run_no_state", None
    last = float(state["last_used_rate"])
    delta = abs(current_rate - last)
    if _triggers(delta):
        return True, f"rate_moved_{delta:.2f}pp_>=_{THRESHOLD_PP:.1f}pp", delta
    return False, f"rate_stable_{delta:.2f}pp_<_{THRESHOLD_PP:.1f}pp", delta


def run_gate(asof=None, state_path=STATE_FP, log_path=LOG_FP, dry=False):
    """Evaluate the gate, persist state + append log (unless dry). Returns a decision dict.
    Fail-safe: on any exception returns refresh=True and logs the error."""
    date = _now_ict_date(asof)
    try:
        current = _dep.current_deposit_rate(asof)      # Big-4 12M deposit %, as-of
        state = load_state(state_path)
        refresh, reason, delta = decide(current, state)
        out = {"date": date, "current_rate": round(current, 4),
               "last_used_rate": (None if state is None else state.get("last_used_rate")),
               "delta_pp": (None if delta is None else round(delta, 4)),
               "refresh": refresh, "reason": reason}
        if not dry:
            new_state = dict(state) if isinstance(state, dict) else {}
            new_state["last_check_date"] = date
            if refresh:
                new_state["last_used_rate"] = round(current, 4)
                new_state["last_used_date"] = date
            _atomic_write(state_path, new_state)
            with open(log_path, "a") as f:
                f.write(json.dumps(out) + "\n")
        return out
    except Exception as exc:                            # fail-safe: recompute rather than serve stale
        out = {"date": date, "refresh": True, "reason": f"gate_error_failsafe: {str(exc)[:120]}"}
        if not dry:
            try:
                with open(log_path, "a") as f:
                    f.write(json.dumps(out) + "\n")
            except Exception:
                pass
        return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="DCF discount-rate conditional refresh gate")
    ap.add_argument("--dry", action="store_true", help="evaluate + print only, no write")
    ap.add_argument("--show", action="store_true", help="print current state and exit")
    ap.add_argument("--asof", default=None, help="override as-of date (YYYY-MM-DD, tests)")
    a = ap.parse_args()
    if a.show:
        print(json.dumps(load_state() or {"state": "none"}, indent=2)); sys.exit(0)
    d = run_gate(asof=a.asof, dry=a.dry)
    print(json.dumps(d, indent=2))
    print(("REFRESH — recompute DCF fair values" if d["refresh"]
           else "SKIP — keep existing DCF fair values") + (" [DRY]" if a.dry else ""))
