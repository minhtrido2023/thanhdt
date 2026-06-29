# -*- coding: utf-8 -*-
"""
macro_healthcheck.py — pre/at go-live health-check for the DT5G macro pipeline.

Scope: Tier 1 (anti silent-staleness) + Tier 2 (value sanity & frozen-feed) +
Tier 5 (liveness/heartbeat) + Tier 6 (fail-safe: revert to DT4-only + SEV alert).
(Tier 3 fire-drill + Tier 4 reconciliation are deliberately OUT of scope here.)

WHY: DT5G (macro_state_live.py) is a DE-RISK overlay whose dangerous failure mode is
SILENT STALENESS — a dead feed does not crash, it just carries the last value forward,
so the system *thinks* it is protected while the macro cap can no longer fire. This
script makes that failure loud and, on detection, recommends reverting to DT4-only
(never trust a stale macro cap) — with SEV1 escalation if the market is simultaneously
showing stress (the worst case: feed dead WHILE VIX rising / VNINDEX below MA200).

DATA SOURCES CHECKED (the four DT5G inputs):
  1. BQ tav2_bq.vnindex_5state_tam_quan_v34b_clean  — DT4 base state (freshness)
  2. BQ tav2_bq.ticker (VNINDEX)                     — price/MA200/RSI (freshness)
  3. us_market_history.csv                           — Pillar B VIX/SPX (fresh+sane+frozen)
  4. sbv_macro_overlay.SBV_REFI_EVENTS               — Pillar A refi (value sane; age=INFO)
Plus an END-TO-END liveness probe: call macro_state_live.get_macro_state() for a recent
window — if it throws, the whole pipeline is FAILED.

OUTPUTS:
  data/macro_health.json                 — full machine-readable status (always written)
  data/macro_health_last_success.txt     — heartbeat marker (written on non-FAILED run)
  data/MACRO_HEALTH_ALERT.md             — human alert (written only when not HEALTHY)
  Telegram message (best-effort) on DEGRADED/FAILED; on HEALTHY only if MACRO_HEALTH_PING=1.

EXIT CODE: 0 HEALTHY, 1 DEGRADED, 2 FAILED  (so a scheduler/watchdog can branch).

Run: python macro_healthcheck.py   (intended right AFTER macro_state_live in the daily job)
"""
import os, sys, io, json, traceback
from datetime import datetime, date
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
DATADIR = os.path.join(WORKDIR, "data"); os.makedirs(DATADIR, exist_ok=True)

# ── thresholds (configurable) ────────────────────────────────────────────────
STATE_MAX_TDAYS  = 3      # BQ DT4 state table: stale if > N trading days behind today
TICKER_MAX_TDAYS = 3      # BQ ticker VNINDEX
US_MAX_TDAYS     = 3      # us_market_history.csv (US calendar; T-1 aligned)
SBV_STALE_DAYS   = 550    # SBV refi: INFO reminder to verify if last event older than this
SBV_VERIFY_MAX_DAYS = 14  # fire sbv_verify_reminder if last manual/auto verify > this many days ago
FROZEN_WINDOW    = 10     # frozen-feed: VIX identical across last N rows -> dead feed
VIX_RANGE        = (5.0, 150.0)
SPXDD_RANGE      = (-1.0, 0.20)
REFI_RANGE       = (0.0, 20.0)
PROBE_LOOKBACK_DAYS = 120  # window for the get_macro_state liveness probe

NOW = datetime.now()
TODAY = NOW.date()

def tdays(asof: date, ref: date = TODAY) -> int:
    """Trading-day age (Mon-Fri, holidays ignored = slightly conservative)."""
    try:
        return int(np.busday_count(np.datetime64(asof, "D"), np.datetime64(ref, "D")))
    except Exception:
        return (ref - asof).days

# accumulators
sources, checks = [], []
def add_source(name, as_of, max_tdays, kind="trading"):
    ok, age, detail = False, None, ""
    if as_of is None:
        detail = "MISSING / unreadable"
    else:
        age = tdays(as_of) if kind == "trading" else (TODAY - as_of).days
        ok = age <= max_tdays
        detail = f"as_of={as_of} age={age}{'td' if kind=='trading' else 'd'} (max {max_tdays})"
    sources.append({"name": name, "as_of": str(as_of) if as_of else None,
                    "age": age, "ok": bool(ok), "detail": detail})
    return ok
def add_check(name, ok, sev, detail):
    checks.append({"name": name, "ok": bool(ok), "sev": sev, "detail": detail})
    return ok

print("=" * 90)
print(f"  MACRO HEALTH-CHECK (DT5G)  {NOW:%Y-%m-%d %H:%M}")
print("=" * 90)

# bq handle (best-effort)
try:
    from simulate_holistic_nav import bq
except Exception as e:
    bq = None
    add_check("import_bq", False, "SEV1", f"cannot import bq: {e}")

# ── TIER 1: freshness of the 4 sources ───────────────────────────────────────
state_fresh = ticker_fresh = us_fresh = True

# 1. LOCAL v3.4b base-state CSV (rebuilt daily from BQ ticker via ew_v1->...->v3.4b chain;
#    this is what macro_state_live now reads — NOT the lagging BQ v34b_clean table).
V34B_CSV = os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
try:
    _b = pd.read_csv(V34B_CSV)
    d = pd.to_datetime(_b["time"]).max().date()
    state_fresh = add_source("local_v34b_state_csv", d, STATE_MAX_TDAYS)
except Exception as e:
    state_fresh = add_source("local_v34b_state_csv", None, STATE_MAX_TDAYS)
    add_check("v34b_csv_read", False, "SEV1", str(e))
# 2. BQ ticker VNINDEX (upstream source the rebuild chain pulls from)
if bq is not None:
    try:
        r = bq("SELECT MAX(t.time) AS mx FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX'")
        d = pd.to_datetime(r["mx"].iloc[0]).date()
        ticker_fresh = add_source("bq_ticker_vnindex", d, TICKER_MAX_TDAYS)
    except Exception as e:
        ticker_fresh = add_source("bq_ticker_vnindex", None, TICKER_MAX_TDAYS)
        add_check("bq_ticker_query", False, "SEV1", str(e))
else:
    ticker_fresh = add_source("bq_ticker_vnindex", None, TICKER_MAX_TDAYS)

# 3. US feed
us = None
try:
    us = pd.read_csv(os.path.join(WORKDIR, "data/us_market_history.csv"), parse_dates=["time"]).sort_values("time")
    us_fresh = add_source("data/us_market_history.csv", us["time"].iloc[-1].date(), US_MAX_TDAYS)
except Exception as e:
    us_fresh = add_source("data/us_market_history.csv", None, US_MAX_TDAYS)
    add_check("us_csv_read", False, "SEV1", str(e))

# 4. SBV refi (age is INFO only — stable refi for years is NORMAL; can't auto-detect a
#    missed SBV change without an external feed, so this is a verify-reminder, not a block)
refi_now = None
try:
    from sbv_macro_overlay import SBV_REFI_EVENTS
    last_ev = pd.to_datetime(SBV_REFI_EVENTS[-1][0]).date(); refi_now = float(SBV_REFI_EVENTS[-1][1])
    sbv_age = (TODAY - last_ev).days
    sources.append({"name": "sbv_refi_events", "as_of": str(last_ev), "age": sbv_age,
                    "ok": True, "detail": f"refi={refi_now}% last_event={last_ev} age={sbv_age}d (INFO)"})
    # sbv_verify_reminder: fire based on last_verified in sbv_verify_log.json (updated by
    # check_sbv_weekly.sh every Friday), not on the age of the last SBV event.
    # Weekly check → threshold is 14 calendar days (2 weeks = enough buffer for Friday cron).
    sbv_verify_log_path = os.path.join(DATADIR, "sbv_verify_log.json")
    verify_age_days = None
    try:
        vlog = json.loads(open(sbv_verify_log_path, encoding="utf-8").read())
        last_v = pd.to_datetime(vlog.get("last_verified")).date()
        verify_age_days = (TODAY - last_v).days
    except Exception:
        pass  # file missing → verify_age_days stays None

    if verify_age_days is None:
        # No verify log yet — fall back to legacy: warn if SBV event age > SBV_STALE_DAYS
        if sbv_age > SBV_STALE_DAYS:
            add_check("sbv_verify_reminder", False, "INFO",
                      f"last SBV refi event {sbv_age}d old ({refi_now}%) — run check_sbv_weekly.sh "
                      f"to initialise sbv_verify_log.json (no verify record found)")
    elif verify_age_days > SBV_VERIFY_MAX_DAYS:
        add_check("sbv_verify_reminder", False, "INFO",
                  f"last SBV verify {verify_age_days}d ago (> {SBV_VERIFY_MAX_DAYS}d) — "
                  f"check_sbv_weekly.sh should run Fridays; current rate {refi_now}% (event: {last_ev})")
except Exception as e:
    sources.append({"name": "sbv_refi_events", "as_of": None, "age": None, "ok": False,
                    "detail": f"unreadable: {e}"})
    add_check("sbv_import", False, "SEV1", str(e))

# ── TIER 2: value sanity + frozen-feed (on US + refi) ─────────────────────────
us_sane = True
if us is not None and len(us):
    last = us.iloc[-1]
    vix = float(last["vix"]) if pd.notna(last["vix"]) else np.nan
    sdd = float(last["spx_dd_1y"]) if pd.notna(last["spx_dd_1y"]) else np.nan
    vma = last.get("vix_ma252", np.nan)
    # range / NaN
    vix_ok = (not np.isnan(vix)) and VIX_RANGE[0] <= vix <= VIX_RANGE[1]
    sdd_ok = (not np.isnan(sdd)) and SPXDD_RANGE[0] <= sdd <= SPXDD_RANGE[1]
    add_check("vix_in_range", vix_ok, "SEV1" if not vix_ok else "OK", f"vix={vix} range{VIX_RANGE}")
    add_check("spx_dd_in_range", sdd_ok, "SEV1" if not sdd_ok else "OK", f"spx_dd_1y={sdd} range{SPXDD_RANGE}")
    add_check("vix_ma252_present", bool(pd.notna(vma)), "SEV2" if pd.isna(vma) else "OK", f"vix_ma252={vma}")
    # frozen feed (VIX never moves across last N rows = dead source despite fresh-looking dates)
    tailv = us["vix"].tail(FROZEN_WINDOW)
    frozen = (tailv.nunique(dropna=True) <= 1) and len(tailv) >= FROZEN_WINDOW
    add_check("vix_not_frozen", not frozen, "SEV1" if frozen else "OK",
              f"VIX unique vals over last {FROZEN_WINDOW}: {int(tailv.nunique(dropna=True))}")
    # NaN-rate in recent window
    tail = us.tail(FROZEN_WINDOW)
    nanrate = float(tail[["vix", "spx_dd_1y"]].isna().mean().max())
    add_check("us_nan_rate", nanrate < 0.2, "SEV2" if nanrate >= 0.2 else "OK", f"max NaN-rate last {FROZEN_WINDOW} = {nanrate:.0%}")
    us_sane = vix_ok and sdd_ok and (not frozen)
else:
    us_sane = False
if refi_now is not None:
    refi_ok = REFI_RANGE[0] <= refi_now <= REFI_RANGE[1]
    add_check("refi_in_range", refi_ok, "SEV1" if not refi_ok else "OK", f"refi={refi_now}% range{REFI_RANGE}")
    if not refi_ok: us_sane = us_sane  # refi range failure handled in severity below

# ── TIER 5: end-to-end liveness probe + heartbeat / missed-runs ───────────────
macro_now, probe_ok = None, False
if bq is not None:
    try:
        from macro_state_live import get_macro_state
        start = (NOW - pd.Timedelta(days=PROBE_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
        m = get_macro_state(start, TODAY.strftime("%Y-%m-%d"), bq=bq)
        if m is None or not len(m):
            add_check("macro_probe", False, "SEV1", "get_macro_state returned no rows")
        else:
            row = m.iloc[-1]
            st, sdt, cap = int(row["state"]), int(row["state_dt4"]), int(row["cap"])
            active = (st != sdt) or (cap != 9)
            macro_now = {"date": str(pd.to_datetime(row["time"]).date()), "state": st,
                         "state_dt4": sdt, "cap": cap, "easing": bool(row["easing"]), "active": bool(active)}
            states_ok = m["state"].isin([1, 2, 3, 4, 5]).all() and m["state_dt4"].isin([1, 2, 3, 4, 5]).all()
            add_check("macro_states_valid", states_ok, "SEV1" if not states_ok else "OK", "state in {1..5}")
            probe_ok = states_ok
            print(f"  macro now: {macro_now['date']} state={st} (DT4={sdt}, cap={cap}, "
                  f"easing={macro_now['easing']}) -> {'ACTIVE' if active else 'idle/armed'}")
    except Exception as e:
        add_check("macro_probe", False, "SEV1", f"get_macro_state failed: {e}")
        traceback.print_exc()

# missed-runs: compare previous success marker to now
MARKER = os.path.join(DATADIR, "macro_health_last_success.txt")
missed = 0
try:
    if os.path.exists(MARKER):
        prev = datetime.fromisoformat(open(MARKER, encoding="utf-8").read().strip().split()[0][:19])
        missed = tdays(prev.date())
        if missed > 1:
            add_check("missed_runs", False, "SEV2", f"{missed} trading days since last successful run ({prev:%Y-%m-%d})")
except Exception:
    pass

# ── TIER 6: market-stress flag + overall status + fail-safe decision ──────────
stress = False; stress_detail = "n/a"
try:
    if us is not None and len(us):
        v = float(us["vix"].iloc[-1]); vm = float(us["vix_ma252"].iloc[-1])
        vix_elev = (not np.isnan(v)) and (not np.isnan(vm)) and v > vm
    else:
        vix_elev = False
    vni_below = False
    if bq is not None:
        try:
            r = bq("SELECT t.Close, t.MA200 FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.MA200 IS NOT NULL ORDER BY t.time DESC LIMIT 1")
            vni_below = bool(float(r["Close"].iloc[0]) < float(r["MA200"].iloc[0]))
        except Exception:
            vni_below = False
    stress = bool(vix_elev or vni_below)
    stress_detail = f"vix_elevated={vix_elev}, vni_below_ma200={vni_below}"
except Exception:
    pass

# any SEV1 among checks?
sev1 = [c for c in checks if not c["ok"] and c["sev"] == "SEV1"]
sev2 = [c for c in checks if not c["ok"] and c["sev"] == "SEV2"]
core_state_stale = (not state_fresh) or (not ticker_fresh)
macro_feed_bad = (not us_fresh) or (not us_sane) or (refi_now is None) or \
                 (refi_now is not None and not (REFI_RANGE[0] <= refi_now <= REFI_RANGE[1]))

# INFO checks (e.g. the SBV verify-reminder for a long-stable refi) are surfaced in the
# JSON/console but do NOT degrade status or trigger alerts — they are nudges, not faults.
if sev1 or core_state_stale or not probe_ok:
    status = "FAILED"
elif sev2 or macro_feed_bad:
    status = "DEGRADED"
else:
    status = "HEALTHY"

# fail-safe state-source recommendation: never trust a stale/insane macro cap
if core_state_stale:
    recommended = "DT4_only"            # whole state pipeline stale -> macro moot, use best available, SEV1 anyway
elif macro_feed_bad or status == "FAILED":
    recommended = "DT4_only"            # macro de-risk blind -> revert to base
else:
    recommended = "DT5G_macro"

# SEV escalation: a bad/stale macro feed WHILE the market is stressed = page now
if status != "HEALTHY" and stress and (macro_feed_bad or core_state_stale):
    sev = "SEV1"
elif status == "FAILED":
    sev = "SEV1"
elif status == "DEGRADED":
    sev = "SEV2"
else:
    sev = "OK"

report = {
    "ts": NOW.isoformat(timespec="seconds"), "status": status, "sev": sev,
    "recommended_state_source": recommended,
    "market_stress": {"flag": stress, "detail": stress_detail},
    "macro_now": macro_now, "missed_runs_tdays": missed,
    "sources": sources, "checks": checks,
}
with open(os.path.join(DATADIR, "macro_health.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

# console summary
print("-" * 90)
for s in sources:
    print(f"  [{'OK ' if s['ok'] else 'XX '}] src {s['name']:<32} {s['detail']}")
for c in checks:
    if not c["ok"]:
        print(f"  [{c['sev']:<4}] {c['name']:<24} {c['detail']}")
print("-" * 90)
print(f"  STATUS = {status}   SEV = {sev}   -> USE STATE SOURCE: {recommended}")
print(f"  market_stress = {stress} ({stress_detail})")
print(f"  written: data/macro_health.json")

# heartbeat marker (write unless FAILED — a FAILED run should NOT refresh the success marker)
if status != "FAILED":
    try:
        open(MARKER, "w", encoding="utf-8").write(f"{NOW.isoformat(timespec='seconds')} status={status}")
    except Exception:
        pass

# ── alerting ──────────────────────────────────────────────────────────────────
def build_alert_text():
    lines = [f"⚠️ MACRO HEALTH {status} (SEV {sev}) @ {NOW:%Y-%m-%d %H:%M}",
             f"-> use state source: {recommended}",
             f"market stress: {stress} ({stress_detail})"]
    bad = [c for c in checks if not c["ok"]]
    if bad:
        lines.append("failing checks:")
        for c in bad: lines.append(f"  [{c['sev']}] {c['name']}: {c['detail']}")
    stale = [s for s in sources if not s["ok"]]
    if stale:
        lines.append("stale/missing sources:")
        for s in stale: lines.append(f"  {s['name']}: {s['detail']}")
    if macro_now:
        lines.append(f"macro now: {macro_now}")
    return "\n".join(lines)

if status != "HEALTHY":
    alert = build_alert_text()
    try:
        open(os.path.join(DATADIR, "MACRO_HEALTH_ALERT.md"), "w", encoding="utf-8").write(alert)
    except Exception:
        pass

ping = os.environ.get("MACRO_HEALTH_PING", "0") == "1"
if status != "HEALTHY" or ping:
    try:
        import json as _j
        cfg = _j.load(open(os.path.join(WORKDIR, "secrets/telegram_config.json"), encoding="utf-8"))
        from telegram_recommend import send_telegram_text
        msg = build_alert_text() if status != "HEALTHY" else \
              f"✅ MACRO HEALTH OK @ {NOW:%Y-%m-%d %H:%M} | source={recommended} | macro={macro_now}"
        send_telegram_text(cfg["bot_token"], cfg["chat_id"], msg)
        print("  telegram alert sent" if status != "HEALTHY" else "  telegram OK-ping sent")
    except Exception as e:
        print(f"  (telegram alert skipped: {e}) — see data/MACRO_HEALTH_ALERT.md")

print("DONE.")
sys.exit({"HEALTHY": 0, "DEGRADED": 1, "FAILED": 2}[status])
