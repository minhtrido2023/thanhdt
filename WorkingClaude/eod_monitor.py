# -*- coding: utf-8 -*-
"""
eod_monitor.py — independent EOD pipeline health check (OPS-1 + OPS-7).

Runs at 23:55 ICT (AFTER daily_refresh at 23:15 + BQ cache sync at 23:45).
Orthogonal to the pipeline: fires even if the refresh script aborted early.

Checks:
  1. DT5G live freshness    — dt5g_live parquet max date must be today or yesterday (T-1)
  2. v34b_clean freshness   — base parquet max date (DT5G input, should also be fresh)
  3. ffill-frozen (OPS-7)   — dt5g_live frozen if max date < v34b_clean max (pipeline ran base
                               but failed to push new rows through publish_gated_state)
  4. Refresh log success     — data/refresh_v34b_linux_<today>.log must end with "DONE"
  5. Telegram report sent    — telegram_run_<today>.log must contain "sent=1"
  6. macro_health.json age   — must be <90 min old (meaning healthcheck ran post-refresh)
  7. macro_health status     — must not be FAILED

Outputs:
  data/eod_monitor_<today>.json — machine-readable result
  Telegram message (compact health summary)
  bus event via append_event.sh

Exit: 0=ALL_OK  1=WARN  2=CRITICAL
"""
import os, sys, json, subprocess
from datetime import datetime, date, timedelta

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
DATADIR = os.path.join(WORKDIR, "data")
CACHE   = os.path.join(DATADIR, "bq_cache")
BIN     = "/home/trido/thanhdt/WorkingClaude/mike/bin"
PJ      = "lithe-record-440915-m9"

os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

NOW   = datetime.now()
TODAY = NOW.date()

def _prev_bday(d: date) -> date:
    d2 = d - timedelta(days=1)
    while d2.weekday() >= 5:  # skip Sat/Sun
        d2 -= timedelta(days=1)
    return d2

PREV_BDAY = _prev_bday(TODAY)

# ── helpers ──────────────────────────────────────────────────────────────────

def parquet_max_date(fname: str):
    """Return max value of 'time' column from a parquet file, or None."""
    path = os.path.join(CACHE, fname)
    if not os.path.exists(path):
        return None
    try:
        import pandas as pd
        df = pd.read_parquet(path, columns=["time"])
        val = df["time"].max()
        if hasattr(val, "date"):
            return val.date()
        return date.fromisoformat(str(val))
    except Exception as e:
        return None

def log_contains(logfile: str, marker: str) -> bool:
    try:
        with open(logfile, encoding="utf-8", errors="replace") as f:
            return marker in f.read()
    except Exception:
        return False

def _bq_max_date(table: str):
    """Fallback: query BQ directly if parquet unavailable."""
    try:
        out = subprocess.check_output(
            ["bq", "query", "--use_legacy_sql=false", "--format=csv",
             f"--project_id={PJ}", f"SELECT MAX(time) FROM tav2_bq.{table}"],
            timeout=60, stderr=subprocess.DEVNULL
        ).decode().strip().splitlines()
        return date.fromisoformat(out[-1].strip()) if out else None
    except Exception:
        return None

# ── run checks ───────────────────────────────────────────────────────────────

results = []  # list of (name, ok, detail)

def check(name, ok, detail):
    results.append({"name": name, "ok": ok, "detail": detail})
    return ok

# 1. DT5G live freshness
dt5g_max = parquet_max_date("vnindex_5state_dt5g_live.parquet")
if dt5g_max is None:
    dt5g_max = _bq_max_date("vnindex_5state_dt5g_live")
if dt5g_max is None:
    check("dt5g_freshness", False, "CANNOT READ dt5g_live parquet or BQ")
else:
    lag = (TODAY - dt5g_max).days
    ok = dt5g_max >= PREV_BDAY  # today or yesterday acceptable
    check("dt5g_freshness", ok, f"dt5g_live max={dt5g_max} lag={lag}d (prev_bday={PREV_BDAY})")

# 2. v34b_clean freshness
v34b_max = parquet_max_date("vnindex_5state_tam_quan_v34b_clean.parquet")
if v34b_max is None:
    v34b_max = _bq_max_date("vnindex_5state_tam_quan_v34b_clean")
if v34b_max is None:
    check("v34b_freshness", False, "CANNOT READ v34b_clean parquet or BQ")
else:
    lag2 = (TODAY - v34b_max).days
    ok2 = v34b_max >= PREV_BDAY
    check("v34b_freshness", ok2, f"v34b_clean max={v34b_max} lag={lag2}d")

# 3. ffill-frozen check A: if v34b advanced but dt5g lagged, publish_gated_state failed
if dt5g_max and v34b_max:
    frozen_a = dt5g_max < v34b_max
    check("ffill_frozen_publish", not frozen_a,
          f"OK: dt5g={dt5g_max} >= v34b={v34b_max}" if not frozen_a
          else f"FROZEN: dt5g={dt5g_max} < v34b={v34b_max} — publish_gated_state may have failed")

# 3b. ffill-frozen check B (OPS-7): state values suspiciously uniform over last 7 rows
dt5g_pq = os.path.join(CACHE, "vnindex_5state_dt5g_live.parquet")
if os.path.exists(dt5g_pq):
    try:
        import pandas as pd
        df = pd.read_parquet(dt5g_pq).sort_values("time").tail(7)
        states = df["state"].tolist()
        n_unique = len(set(states))
        if len(states) >= 5 and n_unique == 1:
            check("ffill_value_frozen", False,
                  f"WARN: last {len(states)} rows all state={states[0]} — may be ffill-frozen (or genuinely stable)")
        else:
            check("ffill_value_frozen", True,
                  f"OK: {n_unique} distinct states over last {len(states)} rows {states}")
    except Exception as e:
        check("ffill_value_frozen", True, f"skipped: {e}")

# 4. Refresh log success
refresh_log = os.path.join(DATADIR, f"refresh_v34b_linux_{TODAY}.log")
if not os.path.exists(refresh_log):
    # try previous trading day (today = Saturday → yesterday = Friday)
    alt_log = os.path.join(DATADIR, f"refresh_v34b_linux_{PREV_BDAY}.log")
    if os.path.exists(alt_log) and TODAY.weekday() >= 5:
        refresh_log = alt_log  # weekend: use Friday's log
        check("refresh_log", log_contains(refresh_log, "refresh DONE"),
              f"weekend: using prev-bday log {PREV_BDAY}: {'DONE found' if log_contains(refresh_log, 'refresh DONE') else 'DONE NOT found'}")
    else:
        check("refresh_log", False, f"log not found: {refresh_log}")
else:
    done = log_contains(refresh_log, "refresh DONE")
    check("refresh_log", done, f"log exists {'+ DONE found' if done else '— DONE missing (may have aborted)'}")

# 5. Telegram sent
tg_log = os.path.join(WORKDIR, f"telegram_run_{TODAY}.log")
if not os.path.exists(tg_log) and TODAY.weekday() >= 5:
    tg_log = os.path.join(WORKDIR, f"telegram_run_{PREV_BDAY}.log")
if not os.path.exists(tg_log):
    check("telegram_sent", False, f"telegram log not found for {TODAY}")
else:
    sent = log_contains(tg_log, "sent=1")
    check("telegram_sent", sent, "✓ sent=1 found" if sent else "FAIL: sent=1 not found — check ISP block or script failure")

# 6. macro_health.json age
mh_path = os.path.join(DATADIR, "macro_health.json")
if not os.path.exists(mh_path):
    check("macro_health_age", False, "macro_health.json not found")
else:
    age_min = (NOW - datetime.fromtimestamp(os.path.getmtime(mh_path))).total_seconds() / 60
    ok3 = age_min < 90
    check("macro_health_age", ok3, f"age={age_min:.0f}min {'OK' if ok3 else 'STALE>90min — healthcheck may not have run'}")

# 7. macro_health status
if os.path.exists(mh_path):
    try:
        mh = json.load(open(mh_path))
        status = mh.get("status", "?")
        sev    = mh.get("sev", "?")
        ok4 = status in ("HEALTHY", "DEGRADED")  # DEGRADED = warn only; FAILED = critical
        check("macro_health_status", ok4,
              f"status={status} sev={sev}" + ("" if ok4 else " — DT5G may be degraded"))
    except Exception as e:
        check("macro_health_status", False, f"cannot parse macro_health.json: {e}")

# ── severity + Telegram message ───────────────────────────────────────────────

n_fail = sum(1 for r in results if not r["ok"])
sev = "OK" if n_fail == 0 else ("WARN" if n_fail <= 1 else "CRITICAL")
icon = {"OK": "✅", "WARN": "⚠️", "CRITICAL": "🚨"}[sev]

lines = [f"<b>{icon} EOD Monitor {TODAY} — {sev}</b>", ""]
for r in results:
    emoji = "✅" if r["ok"] else "❌"
    lines.append(f"{emoji} <b>{r['name']}</b>: {r['detail']}")
lines += ["", f"<i>Checked {NOW.strftime('%H:%M ICT')} by eod_monitor.py</i>"]
msg = "\n".join(lines)

# Send Telegram (best-effort)
sent_tg = False
try:
    cfg = json.load(open(os.path.join(WORKDIR, "secrets/telegram_config.json")))
    from telegram_recommend import send_telegram_text
    resp = send_telegram_text(cfg["bot_token"], cfg["chat_id"], msg)
    sent_tg = resp.get("ok", False)
except Exception as e:
    print(f"[eod_monitor] Telegram send failed: {e}")

# Write result file
out = {
    "ts": NOW.isoformat(),
    "sev": sev,
    "n_fail": n_fail,
    "checks": results,
    "telegram_sent": sent_tg,
}
outfile = os.path.join(DATADIR, f"eod_monitor_{TODAY}.json")
json.dump(out, open(outfile, "w"), indent=2, default=str)
print(f"[eod_monitor] {sev} ({n_fail} fail) → {outfile}")
for r in results:
    print(f"  {'OK' if r['ok'] else 'FAIL'} {r['name']}: {r['detail']}")

# Post to bus
bus_payload = json.dumps({
    "date": str(TODAY), "sev": sev, "n_fail": n_fail,
    "checks": {r["name"]: ("OK" if r["ok"] else "FAIL") for r in results}
})
bus_type = "status" if sev == "OK" else "error"
subprocess.run(
    [f"{BIN}/append_event.sh", "Winston", bus_type, "eod-health", bus_payload],
    timeout=15
)

sys.exit(0 if n_fail == 0 else (1 if n_fail <= 1 else 2))
