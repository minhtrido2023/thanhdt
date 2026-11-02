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

This gate DECIDES + PERSISTS; it does not itself run the (cheap) DCF recompute. Intended use: a
consumer that regenerates DCF numbers calls run_gate() first and only recomputes its fair values
when the returned dict has refresh=True. As of 2026-10-12 NO such consumer exists — the only caller
is this file's CLI (cron `--season`, hằng ngày 08:12 ICT — xem MÙA BCTC), so the gate is a drift monitor: state + log
only, nothing reads refresh. Fail-safe: any error → returns refresh=True (recompute rather than
silently serve stale on a broken gate) and logs the error.

MÙA BCTC (job Taylor_20261101_181016, user duyệt 2026-11-01; REPORT dcf_vn_calibration_20261101 §1):
  `--season` THAY cron ngày 11 hằng tháng bằng MỘT cron HẰNG NGÀY (`12 1 * * *`, 08:12 ICT; ngoài cửa
  sổ slot vẫn in JSON no_slot_in_window ra log ⇒ log luôn tươi cho cron_health_check, không báo STALE giả
  như bản 2 dòng thưa gap 79-82 ngày; catch-up THẬT nhờ SEASON_GRACE_DAYS). Dưới DCF_RATE_FRAME=domestic_v2 r hằng ⇒ trigger lãi suất ở
  trên là no-op, nên lịch chuyển sang theo mùa công bố BCTC: 8 slot/năm, mỗi slot là MỘT lượt quét
  idempotent theo slot (state["season_done"]) — "early" 05/02 05/05 03/08 03/11 (mã đã có BCTC) và
  "full" 15/02 15/05 15/08 15/11 (sau p95 công bố + ~2 tuần vendor nạp). Chạy lại cùng ngày/cùng slot
  ⇒ no-op; cron lỡ ⇒ bù trong SEASON_GRACE_DAYS ngày. Lượt quét CHỈ đo (số mã theo quý BCTC mới nhất,
  số mã STALE >105 ngày) và ghi log/state — KHÔNG tính lại FV (FV tính theo yêu cầu trong dcf_check, MoS
  theo giá mới mỗi lần dùng), KHÔNG đổi mặc định domestic_v2, KHÔNG ai đọc kết quả để chặn gì.
  Chế độ cũ (không cờ) vẫn chạy được cho mục đích soi trôi lãi suất thủ công.

Run: $DNA_PYEXE dcf_refresh_gate.py --season   # lượt mùa BCTC (cron hằng ngày)
     $DNA_PYEXE dcf_refresh_gate.py            # evaluate + persist + log (real)
     $DNA_PYEXE dcf_refresh_gate.py --dry      # evaluate + print only, no state/log write
     $DNA_PYEXE dcf_refresh_gate.py --show      # print current state
"""
import os, sys, json, argparse
from datetime import datetime, date
from zoneinfo import ZoneInfo

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
import deposit_rate_vn as _dep

STATE_FP = f"{WORKDIR}/data/dcf_refresh_state.json"
LOG_FP = f"{WORKDIR}/data/dcf_refresh_gate.log"
THRESHOLD_PP = 1.0                 # percentage-point band
THRESHOLD_INCLUSIVE = True         # exactly 1.0pp → refresh (see BOUNDARY note above)
_EPS = 1e-9


def _now_ict_date(asof=None):
    """Return the as-of date string. `asof` overridable for tests; else today's calendar date in
    ICT (Asia/Ho_Chi_Minh), independent of the process TZ. The date is an audit label only
    (state last_check_date/last_used_date + log line) — decide() never compares it."""
    if asof is not None:
        return str(asof)[:10]
    return datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d")


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
        # consumer_deposit_rate() wired 2026-10-01 (job Taylor_20261001_054110) -- must match
        # dcf_valuation.py::discount_rate()'s deposit leg exactly, else this gate's delta-vs-
        # last-used-rate drifts out of sync with the rate the DCF chain actually used.
        current = _dep.consumer_deposit_rate(asof)      # effective (Big-4 or CCTG) deposit %, as-of
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


# ---------------------------------------------------------------------------- MÙA BCTC
SEASON_SLOTS = ((2, 5, "early"), (2, 15, "full"), (5, 5, "early"), (5, 15, "full"),
                (8, 3, "early"), (8, 15, "full"), (11, 3, "early"), (11, 15, "full"))
SEASON_GRACE_DAYS = 7              # cron HẰNG NGÀY lỡ ⇒ ngày sau bù tới 7 ngày sau slot (khoảng cách slot gần nhất = 10 ngày)
SEASON_KEEP = 8                    # giữ 8 slot gần nhất trong state


def season_slot(today, done):
    """Thuần (không I/O): lượt quét mùa BCTC hôm nay. `today` = date (lịch ICT), `done` = list slot id đã chạy.
    Trả (scan_bool, slot_id|None, kind|None, reason). Slot id = 'YYYY-MM-DD:kind'. Chọn slot gần nhất
    <= today trong SEASON_GRACE_DAYS; slot đã chạy ⇒ no-op (idempotent)."""
    cands = [(date(today.year, m, d), k) for m, d, k in SEASON_SLOTS]
    cands = [(sd, k) for sd, k in cands if 0 <= (today - sd).days <= SEASON_GRACE_DAYS]
    if not cands:
        return False, None, None, "no_slot_in_window"
    sd, kind = max(cands)
    sid = f"{sd.isoformat()}:{kind}"
    if sid in (done or []):
        return False, sid, kind, "slot_already_done"
    return True, sid, kind, "slot_due"


def season_stats(asof, fin_path=None):
    """Đo chất lượng dữ liệu BCTC tại asof từ cache ticker_financial local (KHÔNG BQ): với mã có dòng
    trong 400 ngày gần nhất — phân bố quý mới nhất và số mã STALE (tuổi > STALE_BCTC_DAYS). Thuần đọc."""
    import pandas as pd
    import dcf_valuation as _dv
    fp = fin_path or f"{WORKDIR}/data/bq_cache/ticker_financial.parquet"
    df = pd.read_parquet(fp, columns=["ticker", "time", "quarter"])
    df["time"] = pd.to_datetime(df["time"])
    a = pd.Timestamp(asof)
    df = df[df.time <= a].sort_values(["ticker", "time"])
    last = df.groupby("ticker").tail(1)
    last = last[(a - last.time).dt.days <= 400]
    ages = (a.normalize() - last.time.dt.normalize()).dt.days
    return {"n_tickers": int(len(last)),
            "n_stale": int((ages > _dv.STALE_BCTC_DAYS).sum()),
            "stale_days": _dv.STALE_BCTC_DAYS,
            "age_p50": float(ages.median()) if len(ages) else None,
            "by_quarter": {str(k): int(v) for k, v in last.quarter.value_counts().head(3).items()}}


def run_season(asof=None, state_path=STATE_FP, log_path=LOG_FP, dry=False, stats_fn=None):
    """Lượt mùa BCTC. Idempotent theo slot; lỗi ⇒ KHÔNG đánh dấu done (lượt sau thử lại), scan=False,
    reason='season_error:...' (rc!=0 ở CLI). Không đổi last_used_rate/last_used_date (khóa lãi suất cũ)."""
    d = _now_ict_date(asof)
    try:
        state = load_state(state_path)
        done = (state or {}).get("season_done", [])
        scan, sid, kind, reason = season_slot(date.fromisoformat(d), done)
        out = {"date": d, "mode": "season", "scan": scan, "slot": sid, "kind": kind, "reason": reason}
        if scan:
            out["stats"] = (stats_fn or season_stats)(d)
            if not dry:
                new_state = dict(state) if isinstance(state, dict) else {}
                new_state["season_done"] = (list(done) + [sid])[-SEASON_KEEP:]
                new_state["season_last_date"] = d
                _atomic_write(state_path, new_state)
        if not dry and (scan or reason != "no_slot_in_window"):
            with open(log_path, "a") as f:
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
        return out
    except Exception as exc:
        out = {"date": d, "mode": "season", "scan": False, "slot": None, "kind": None,
               "reason": f"season_error: {type(exc).__name__}: {str(exc)[:120]}"}
        if not dry:
            try:
                with open(log_path, "a") as f:
                    f.write(json.dumps(out, ensure_ascii=False) + "\n")
            except Exception:
                pass
        return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="DCF discount-rate conditional refresh gate")
    ap.add_argument("--dry", action="store_true", help="evaluate + print only, no write")
    ap.add_argument("--show", action="store_true", help="print current state and exit")
    ap.add_argument("--season", action="store_true", help="lượt mùa BCTC (idempotent theo slot)")
    ap.add_argument("--asof", default=None, help="override as-of date (YYYY-MM-DD, tests)")
    a = ap.parse_args()
    if a.show:
        print(json.dumps(load_state() or {"state": "none"}, indent=2)); sys.exit(0)
    if a.season:
        d = run_season(asof=a.asof, dry=a.dry)
        print(json.dumps(d, indent=2, ensure_ascii=False))
        if str(d["reason"]).startswith("season_error"):
            # khớp ^\s*❌ trong ERROR_PATTERNS của cron_health_check (stdout JSON không đủ: pattern neo đầu dòng)
            print(f"❌ dcf_refresh_gate --season: {d['reason']}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)
    d = run_gate(asof=a.asof, dry=a.dry)
    print(json.dumps(d, indent=2))
    print(("REFRESH — recompute DCF fair values" if d["refresh"]
           else "SKIP — keep existing DCF fair values") + (" [DRY]" if a.dry else ""))
