#!/usr/bin/env python3
"""
rubber_weekly_selfcheck.py — regression test for the 52-week band gate + ALERT confirm
=====================================================================================
Guards the 2026-08-04 false ALERT: the band gate counted ROWS (len(real) >= 30) on a
daily series that only began 2026-06-19, so ~6 weeks of prints opened a "52-week"
comparison and every dip printed a new "52w low". Real band (WB monthly, data/
rubber_monthly.csv) over 2025-08→2026-08 was 2.00–2.86; the flagged 2.596 sits
64.9% of the way UP the band the code actually compares against (2.00–2.919, WB
monthly spliced with the real daily feed), nowhere near the low.
NB "69%" appears in the incident writeups: that is the same range position measured
against the WB-monthly-only band (2.596-2.00)/(2.86-2.00). Both are RANGE POSITIONS,
not empirical percentiles — the empirical CDF of the same window sits at ~75-83%
depending on lookback. Stated explicitly because "p69" was misread as a percentile
during review; no gate uses any of these figures, they are framing only.

Run:  /home/trido/thanhdt/wc_venv/bin/python rubber_weekly_selfcheck.py
Env:  no TZ dependency by design, but re-run under `env -u TZ` and TZ=UTC anyway
      (coding_guidelines §16 / verify-before-done skill) — both are asserted below.
"""
import os, sys, json, tempfile, importlib.util
from datetime import timedelta
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS, CHECKS = [], 0

# Baselines for the side-effect assertions in section [7]. Captured before anything runs.
_BUS_SIZE_AT_START = os.path.getsize("/home/trido/thanhdt/WorkingClaude/mike/bus/inbox/Winston.jsonl")
_STATE_MTIME_AT_START = os.path.getmtime(os.path.join(HERE, "data", "rubber_alert_state.json"))


def load_module(data_dir=None, reset_state=True):
    """Fresh import of rubber_weekly with DATA/STATEF optionally redirected to tmp.
    reset_state=True clears any leftover state file first (Executor-style stale-fixture
    trap, coding_guidelines §7: never let an earlier run decide this run's result).
    reset_state=False is for multi-day sequences that MUST carry state forward —
    the confirmation streak lives in that file."""
    spec = importlib.util.spec_from_file_location("rw_sc", os.path.join(HERE, "rubber_weekly.py"))
    rw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rw)
    # NEVER let a selfcheck reach the real fleet bus or Telegram. confirm_alert() emits a
    # bus event on a dropped streak, which silently appended 13 junk events to
    # mike/bus/inbox/Winston.jsonl before this stub existed (found 2026-08-06). Callers
    # that want to inspect the calls rebind these; the default is a hard no-op.
    rw.bus = lambda *a, **k: None
    rw.telegram = lambda *a, **k: True
    if data_dir:
        rw.DATA = data_dir
        rw.STATEF = os.path.join(data_dir, "rubber_alert_state.json")
        if reset_state and os.path.exists(rw.STATEF):
            os.remove(rw.STATEF)
    return rw


def check(name, cond, detail=""):
    global CHECKS
    CHECKS += 1
    print(("  PASS  " if cond else "  FAIL  ") + name + (f"   [{detail}]" if detail else ""))
    if not cond:
        FAILS.append(name)


def df_asof(rw, day):
    """The real production CSV, truncated to <= day — i.e. exactly what the script
    saw on that date. No synthetic data: this is the run that misfired."""
    d = pd.read_csv(os.path.join(HERE, "data", "rubber_weekly.csv"))
    return d[d["date"] <= day].copy()


# ---------------------------------------------------------------- 1. the regression
print("\n[1] 2026-08-04 — the run that fired the false ALERT")
rw = load_module()
m = rw.trend(df_asof(rw, "2026-08-04"))
tier, reasons = rw.classify(m)

check("band is NOT 'low' (was 'low' -> false ALERT)", m["band"] is None, f"band={m['band']}")
check("no '52 tuần' reason survives", not any("52 tuần" in r for r in reasons), str(reasons))
check("tier is not ALERT", tier != "ALERT", f"tier={tier} reasons={reasons}")

# the band it now compares against must be the WB-monthly-backed one, not the
# 6-week daily window (2.596-2.919) that produced the bug.
mo = pd.read_csv(os.path.join(HERE, "data", "rubber_monthly.csv"))
mo["dt"] = pd.to_datetime(mo["month"].astype(str) + "-15")
w = mo[(mo.dt >= pd.Timestamp("2026-08-04") - timedelta(days=365)) & (mo.dt <= pd.Timestamp("2026-08-04"))]
check("band window computed (band_ok)", m["band_ok"], m["band_note"])
check("band low == WB 52w low 2.00", m["band_ok"] and abs(m["band_lo"] - float(w.price.min())) < 1e-9,
      f"got {m['band_lo']} vs WB {w.price.min()}")
check("band spans >= 330 calendar days", m["band_span"] >= rw.BAND_MIN_SPAN, f"span={m['band_span']}d")
check("2.596 sits INSIDE the band", m["band_ok"] and m["band_lo"] < m["latest"] < m["band_hi"],
      f"{m['band_lo']} < {m['latest']} < {m['band_hi']}")

# the real move is preserved untouched — the fix must not mute genuine numbers
check("WoW still measured at -6.6% (real number, unchanged)", round(m["wow"], 1) == -6.6, f"{m['wow']:.2f}%")
check("4wk still measured at -7.4% (real number, unchanged)", round(m["c4w"], 1) == -7.4, f"{m['c4w']:.2f}%")
# ...and it correctly stays below the APPROVED WATCH gate (|WoW| >= 7.0%): -6.6% < 7.0%
check("WoW -6.6% is below the approved WATCH gate 7.0% -> INFO is correct",
      abs(m["wow"]) < rw.WATCH_WOW and tier == "INFO", f"|{m['wow']:.2f}| vs {rw.WATCH_WOW}")

# ---------------------------------------------------------- 2. the old gate is dead
print("\n[2] the row-count gate must be gone (len(real) >= 30 opened it at ~6 weeks)")
d = df_asof(rw, "2026-08-04")
dd = d.copy(); dd["date"] = pd.to_datetime(dd["date"])
real = dd[dd["rss3_usdkg"].notna()].sort_values("date").set_index("date")
real = real[real["src"] != "wb_seed"]
check("row count would have passed the old gate", len(real) >= 30, f"{len(real)} rows")
check("but calendar span is far short of 52 weeks",
      (real.index[-1] - real.index[0]).days < rw.BAND_MIN_SPAN,
      f"{(real.index[-1]-real.index[0]).days}d of real feed")
src = open(os.path.join(HERE, "rubber_weekly.py"), encoding="utf-8").read()
check("no 'len(real) >= 30' left in source", "len(real) >= 30" not in src)

# --------------------------------------------------- 3. band fails CLOSED, not open
print("\n[3] fail-safe: no usable history -> no band (never a spurious break)")
rw2 = load_module()
rw2.MONTHLY = os.path.join(HERE, "data", "__no_such_monthly__.csv")   # WB seed gone
m2 = rw2.trend(df_asof(rw2, "2026-08-04"))
check("monthly file missing -> band None (fails closed)", m2["band"] is None, m2["band_note"])
check("...and classify() raises no ALERT", rw2.classify(m2)[0] != "ALERT")

rw3 = load_module()
_orig = rw3.monthly_series
rw3.monthly_series = lambda: _orig()[_orig().index < pd.Timestamp("2025-10-01")]  # 8-month hole
m3 = rw3.trend(df_asof(rw3, "2026-08-04"))
check("hole > BAND_MAX_GAP -> band None", m3["band"] is None, m3["band_note"])

# a genuine break must still be detected: push the latest print under the WB low
print("    (and a REAL break must still fire)")
rw4 = load_module()
d4 = df_asof(rw4, "2026-08-04")
d4.loc[d4["date"] == "2026-08-04", "rss3_usdkg"] = 1.80        # below WB 52w low 2.00
m4 = rw4.trend(d4)
check("genuine sub-52w-low print -> band 'low'", m4["band"] == "low", f"band={m4['band']}")
check("...and classify() escalates to ALERT", rw4.classify(m4)[0] == "ALERT")

# ------------------------------------- 3b. monthly-average compression (soft band)
# A WB monthly point is a monthly AVERAGE: it lies inside that month's true daily
# range, so the spliced band is NARROWER than reality on BOTH sides and a break test
# against it OVER-fires. Measured on the 3 months where we hold both: monthly means
# span 2.69-2.81 while true daily spans 2.60-2.92. So while the window still leans on
# monthly points, a break must NOT raise an ALERT on its own.
print("\n[3b] monthly-average compression -> band breaks are 'soft' until real daily history accrues")
dm = pd.read_csv(os.path.join(HERE, "data", "rubber_weekly.csv"))
dm = dm[dm.src == "regionalert"].copy()
dm["date"] = pd.to_datetime(dm["date"]); dm["mo"] = dm["date"].dt.to_period("M")
gm = dm.groupby("mo")["rss3_usdkg"].agg(["min", "mean", "max"])
check("averaging compresses the low (mean-min > true-min)", gm["mean"].min() > gm["min"].min(),
      f"{gm['mean'].min():.3f} > {gm['min'].min():.3f}")
check("averaging compresses the high (mean-max < true-max)", gm["mean"].max() < gm["max"].max(),
      f"{gm['mean'].max():.3f} < {gm['max'].max():.3f}")

rw_s = load_module()
check("today's window is still monthly-spliced (11 WB points)", "11 điểm WB monthly" in m["band_note"],
      m["band_note"])

# Isolate the BAND rule from the %-change rules: a real price low enough to break the
# 2.00 band necessarily also trips |WoW| >= 12%, so a full-series test cannot separate
# them. Drive classify() directly with the %-changes held at zero.
def band_only(band, soft):
    return dict(wow=0.0, c4w=0.0, c3m=0.0, band=band, band_soft=soft,
                band_lo=2.00, band_hi=2.92, band_span=354)

t_lo, r_lo = rw_s.classify(band_only("low", True))
check("soft LOW break alone does NOT raise ALERT (the over-fire class)", t_lo != "ALERT", f"tier={t_lo}")
check("...but it IS still reported to Taylor as WATCH", t_lo == "WATCH" and any("52 tuần" in x for x in r_lo),
      str(r_lo))
t_hi, r_hi = rw_s.classify(band_only("high", True))
check("soft HIGH break alone does NOT raise ALERT (reviewer's missing high-side case)",
      t_hi != "ALERT", f"tier={t_hi}")
check("hard LOW break alone DOES raise ALERT", rw_s.classify(band_only("low", False))[0] == "ALERT")
check("hard HIGH break alone DOES raise ALERT", rw_s.classify(band_only("high", False))[0] == "ALERT")

# and the soft flag hardens by itself once the daily feed alone covers the window
# (~2027-05 in reality). Simulate that future: a dense business-day real series that
# spans the whole 52 weeks on its own, so no monthly point falls inside the window.
rw_h = load_module()
bd = pd.bdate_range("2025-08-10", "2026-08-04")
d_h = pd.DataFrame({"date": bd.strftime("%Y-%m-%d"), "rss3_usdkg": 2.60,
                    "src": "regionalert"})
d_h.loc[d_h.index[-1], "rss3_usdkg"] = 1.95                  # genuine new low, real data
m_h = rw_h.trend(d_h)
check("no monthly points in window -> band is HARD", m_h["band"] == "low" and m_h["band_soft"] is False,
      m_h["band_note"])
check("...and that hard break DOES raise ALERT", rw_h.classify(m_h)[0] == "ALERT")


# ------------------------------------------------- 4. ALERT needs 2 consecutive reads
print("\n[4] ALERT confirmation: 2 consecutive observation dates before Telegram/Bill")
with tempfile.TemporaryDirectory() as tmp:
    rw5 = load_module(data_dir=tmp)
    a = dict(latest=1.80, latest_dt=pd.Timestamp("2026-08-04"))
    b = dict(latest=1.80, latest_dt=pd.Timestamp("2026-08-05"))
    check("1st sighting -> unconfirmed", rw5.confirm_alert("ALERT", a) is False)
    check("re-run SAME date -> still unconfirmed (idempotent)", rw5.confirm_alert("ALERT", a) is False)
    check("next date, still ALERT -> confirmed", rw5.confirm_alert("ALERT", b) is True)
    check("unconfirmed->confirmed counts as escalation (not muted by weekly dedupe)",
          rw5.should_fire("ALERT", b, confirmed=True) is True)
    rw5.record_fire("ALERT", b, confirmed=True)
    check("confirmed ALERT re-run same week -> muted", rw5.should_fire("ALERT", b, confirmed=True) is False)
    check("streak broken by INFO -> pending cleared", rw5.confirm_alert("INFO", b) is False
          and json.load(open(rw5.STATEF)).get("pending_alert") is None)
    check("...so the next ALERT starts unconfirmed again", rw5.confirm_alert("ALERT", b) is False)
    check("state write is atomic (no .tmp left behind)",
          not os.path.exists(rw5.STATEF + ".tmp"))

# ------------------------------------------------------------- 5. environment sanity
print("\n[5] environment independence")
check("no naive datetime.now()/date.today() in the band path",
      "datetime.now()" not in src.split("def band_52w")[1].split("def classify")[0])
print(f"    TZ={os.environ.get('TZ', '(unset)')}  — band math is date-index only, no wall clock")

# ------------------------------------------- 6. end-to-end main(), real code path
# Sandboxed: DATA -> tmpdir, fetchers/telegram/bus stubbed. Exercises update_csv +
# render_note + should_fire + fire() together — the units above can all pass while
# the wiring between them is wrong.
print("\n[6] end-to-end main() — sandboxed, no network / no Telegram / no bus")
with tempfile.TemporaryDirectory() as tmp:
    sent, bused = [], []

    def sandbox(price, day, reset_state=False):
        rw6 = load_module(data_dir=tmp, reset_state=reset_state)   # state MUST carry over
        rw6.CSV = os.path.join(tmp, "rubber_weekly.csv")
        rw6.NOTE = os.path.join(tmp, "rubber_watch.md")
        rw6.MONTHLY = os.path.join(HERE, "data", "rubber_monthly.csv")
        rw6.fetch_regionalert = lambda: {"date": day, "src": "regionalert", "rss3_usdkg": price}
        rw6.fetch_sunsirs = lambda: (_ for _ in ()).throw(RuntimeError("stubbed off"))
        rw6.telegram = lambda text: sent.append(text) or True
        rw6.bus = lambda et, topic, payload: bused.append((et, topic, payload))
        return rw6

    # seed the sandbox CSV with real history up to the day BEFORE the incident
    df_asof(None, "2026-08-03").to_csv(os.path.join(tmp, "rubber_weekly.csv"), index=False)

    sandbox(2.596, "2026-08-04", reset_state=True).main()     # the incident, replayed
    check("E2E: 2026-08-04 sends NO Telegram", len(sent) == 0, f"{len(sent)} sent")
    check("E2E: 2026-08-04 raises no ALERT on the bus",
          not any("ALERT" in t for _, t, _ in bused), str([t for _, t, _ in bused]))
    note = open(os.path.join(tmp, "rubber_watch.md"), encoding="utf-8").read()
    check("E2E: note renders the real band 2.00–2.92", "2.00–2.92" in note)
    check("E2E: note badge is INFO", "🟢 INFO" in note, note.split("Trạng thái:")[1][:24].strip())

    sandbox(1.80, "2026-08-05").main()                        # genuine break, day 1
    check("E2E: genuine break day-1 -> bus ALERT but STILL no Telegram",
          len(sent) == 0 and any("ALERT" in t for _, t, _ in bused),
          f"telegram={len(sent)} bus={[t for _, t, _ in bused]}")
    check("E2E: day-1 bus payload marked unconfirmed",
          bused[-1][2]["confirmed"] is False and bused[-1][2]["audience"] == ["Taylor"])

    sandbox(1.79, "2026-08-06").main()                        # genuine break, day 2
    check("E2E: day-2 confirmation -> Telegram fires", len(sent) == 1, f"{len(sent)} sent")
    check("E2E: confirmed payload reaches Bill",
          bused[-1][2]["confirmed"] is True and "DollarBill" in bused[-1][2]["audience"])
    check("E2E: Telegram text cites the WoW collapse", "WoW" in sent[0], sent[0][:70])

# V-shaped crash: spike on day 1, reverts on day 2. The confirmation gate swallows the
# Telegram BY DESIGN (that is the point) — but it must not swallow it SILENTLY.
print("\n[6b] V-shaped one-session spike that reverts — must be audible, not silent")
with tempfile.TemporaryDirectory() as tmp:
    sent, bused = [], []

    def vbox(price, day, reset_state=False):
        rw7 = load_module(data_dir=tmp, reset_state=reset_state)
        rw7.CSV = os.path.join(tmp, "rubber_weekly.csv")
        rw7.NOTE = os.path.join(tmp, "rubber_watch.md")
        rw7.MONTHLY = os.path.join(HERE, "data", "rubber_monthly.csv")
        rw7.fetch_regionalert = lambda: {"date": day, "src": "regionalert", "rss3_usdkg": price}
        rw7.fetch_sunsirs = lambda: (_ for _ in ()).throw(RuntimeError("stubbed off"))
        rw7.telegram = lambda text: sent.append(text) or True
        rw7.bus = lambda et, topic, payload: bused.append((et, topic, payload))
        return rw7

    df_asof(None, "2026-08-03").to_csv(os.path.join(tmp, "rubber_weekly.csv"), index=False)
    vbox(1.80, "2026-08-04", reset_state=True).main()          # crash print
    check("V: day-1 spike -> bus only, no Telegram", len(sent) == 0 and len(bused) == 1)
    vbox(2.79, "2026-08-05").main()                            # fully reverts
    check("V: day-2 revert -> still no Telegram (gate working as designed)", len(sent) == 0)
    check("V: the dropped pending alert is announced on the bus, not silently forgotten",
          any("tự huỷ" in t for _, t, _ in bused), str([t for _, t, _ in bused]))
    st = json.load(open(os.path.join(tmp, "rubber_alert_state.json")))
    check("V: pending cleared so the next ALERT starts fresh", st.get("pending_alert") is None)
    ev = [p for et, t, p in bused if "tự huỷ" in t][0]
    check("V: notice says Telegram/Bill were NOT sent, and that is true",
          ev["escalated_before"] is False and "CHƯA từng gửi" in ev["note"])
    check("V: notice uses an event_type the bus actually forwards to Taylor",
          [et for et, t, _ in bused if "tự huỷ" in t] == ["finding"],
          "mike_json.py:cmd_delta_append forwards finding/answer/decision/verification only")

# A CONFIRMED alert (Telegram already sent) that later reverts is a DIFFERENT event from
# an unconfirmed one fizzling — the close-out notice must not claim nobody was paged.
print("\n[6c] confirmed ALERT that later reverts — close-out notice must tell the truth")
with tempfile.TemporaryDirectory() as tmp:
    sent, bused = [], []

    def cbox(price, day, reset_state=False):
        rw8 = load_module(data_dir=tmp, reset_state=reset_state)
        rw8.CSV = os.path.join(tmp, "rubber_weekly.csv")
        rw8.NOTE = os.path.join(tmp, "rubber_watch.md")
        rw8.MONTHLY = os.path.join(HERE, "data", "rubber_monthly.csv")
        rw8.fetch_regionalert = lambda: {"date": day, "src": "regionalert", "rss3_usdkg": price}
        rw8.fetch_sunsirs = lambda: (_ for _ in ()).throw(RuntimeError("stubbed off"))
        rw8.telegram = lambda text: sent.append(text) or True
        rw8.bus = lambda et, topic, payload: bused.append((et, topic, payload))
        return rw8

    df_asof(None, "2026-08-03").to_csv(os.path.join(tmp, "rubber_weekly.csv"), index=False)
    cbox(1.80, "2026-08-04", reset_state=True).main()      # day 1: ALERT, unconfirmed
    cbox(1.78, "2026-08-05").main()                        # day 2: confirmed -> Telegram
    check("C: Telegram fired on day 2", len(sent) == 1, f"{len(sent)} sent")
    cbox(2.79, "2026-08-06").main()                        # day 4: reverts
    ev = [p for et, t, p in bused if "kết thúc" in t or "tự huỷ" in t]
    check("C: a close-out notice is emitted", len(ev) == 1, str([t for _, t, _ in bused]))
    check("C: it records that the streak HAD escalated", ev and ev[0]["escalated_before"] is True)
    check("C: it does NOT falsely claim Telegram/Bill were unsent",
          ev and "CHƯA từng gửi" not in ev[0]["note"] and "ĐÃ gửi" in ev[0]["note"],
          ev[0]["note"][:80] if ev else "")
    check("C: Bill, who was paged, is told it closed", ev and "DollarBill" in ev[0]["audience"])
    check("C: no extra Telegram on close-out", len(sent) == 1, f"{len(sent)} sent")

# --------------------------------------------- 7. the selfcheck must be side-effect free
print("\n[7] selfcheck side-effects: the live bus and production state must be untouched")
LIVE_BUS = "/home/trido/thanhdt/WorkingClaude/mike/bus/inbox/Winston.jsonl"
check("live bus size unchanged by this run", os.path.getsize(LIVE_BUS) == _BUS_SIZE_AT_START,
      f"{_BUS_SIZE_AT_START} -> {os.path.getsize(LIVE_BUS)}")
check("production state file untouched",
      os.path.getmtime(os.path.join(HERE, "data", "rubber_alert_state.json")) == _STATE_MTIME_AT_START)

print("\n" + "=" * 70)
print(f"{CHECKS - len(FAILS)}/{CHECKS} PASS" + ("" if not FAILS else f"   FAILED: {FAILS}"))
print("=" * 70)
sys.exit(1 if FAILS else 0)
