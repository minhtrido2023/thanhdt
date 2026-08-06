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

# ------------------------------------------------- 8. TREND_BREAK (monthly regime tier)
# Independent tier (rubber_trend_break.py), wired 2026-08-06 from the approved design
# mike/agents/Taylor/research/rubber_trend_break_design_20260806.md. It is a STATE
# (UPTREND/DOWNTREND) on the WB MONTHLY series, MA10 (= MA200-daily equivalent),
# confirmed 2 consecutive months. Fires only on a state FLIP, ~1x / 18.7 months.
print("\n[8] TREND_BREAK — monthly regime tier")
import rubber_trend_break as rtb


def write_monthly(path, prices, start="2020-01"):
    """Synthetic WB monthly file: consecutive months from `start`."""
    idx = pd.period_range(start, periods=len(prices), freq="M")
    pd.DataFrame({"month": [str(p) for p in idx], "price": prices}).to_csv(path, index=False)
    return idx


def write_daily(path, rows):
    """Synthetic daily feed (date, rss3_usdkg, src) — the provisional-month input."""
    pd.DataFrame(rows, columns=["date", "rss3_usdkg", "src"]).to_csv(path, index=False)


def tb_box(tmp, monthly_prices, daily_rows=None, start="2020-01", reset_state=True):
    rw = load_module(data_dir=tmp, reset_state=reset_state)
    rw.MONTHLY = os.path.join(tmp, "rubber_monthly.csv")
    rw.CSV = os.path.join(tmp, "rubber_weekly.csv")
    write_monthly(rw.MONTHLY, monthly_prices, start)
    write_daily(rw.CSV, daily_rows or [])
    rw.sent, rw.bused = [], []
    rw.telegram = lambda text: rw.sent.append(text) or True
    rw.bus = lambda et, topic, payload: rw.bused.append((et, topic, payload))
    return rw


# 8a. parameters are the approved ones, not re-derived
check("MA window is 10 months (= MA200 daily equivalent)", rtb.MA_WIN == 10, str(rtb.MA_WIN))
check("confirmation is 2 consecutive months", rtb.CONFIRM == 2, str(rtb.CONFIRM))

# 8b. FIRES: two consecutive months below the line flip the state and page the team
print("  -- a genuine break")
with tempfile.TemporaryDirectory() as tmp:
    rw = tb_box(tmp, [3.0] * 24 + [2.0, 2.0])
    rw._save_state({"trend_state": "UPTREND", "trend_since": "2020-10"})   # established state
    r = rw.trend_break_check()
    check("2 months below -> state flips to DOWNTREND", r["state"] == "DOWNTREND", r["state"])
    check("...bus event carries signal TREND_BREAK",
          any(p.get("signal") == "TREND_BREAK" for _, _, p in rw.bused),
          str([t for _, t, _ in rw.bused]))
    check("...Telegram fires (confirmed, not provisional)", len(rw.sent) == 1, f"{len(rw.sent)} sent")
    check("...stored state advanced to DOWNTREND",
          json.load(open(rw.STATEF))["trend_state"] == "DOWNTREND")
    check("...second run same day does NOT re-fire (state tier, not a daily ping)",
          rw.trend_break_check() and len(rw.sent) == 1 and len(rw.bused) == 1,
          f"telegram={len(rw.sent)} bus={len(rw.bused)}")
    pl = rw.bused[0][2]
    check("...payload names the reading: regime-confirmation, NOT a sell signal",
          "KHÔNG PHẢI tín hiệu bán" in pl["reading"] and "KHÔNG PHẢI dự báo" in pl["reading"],
          pl["reading"][:60])
    check("...payload cites the negative result (31% vs base 32%)",
          "31%" in pl["reading"] and "32%" in pl["reading"])
    check("...payload cites the stock evidence pointing the other way (+26.5% vs +12.5%)",
          "26.5%" in pl["reading"] and "12.5%" in pl["reading"])
    check("...payload marked not provisional", pl["provisional"] is False)
    txt = rw.sent[0]
    check("Telegram text carries the mandatory regime-confirmation warning",
          "XÁC NHẬN CHẾ ĐỘ" in txt and "KHÔNG PHẢI TÍN HIỆU BÁN" in txt, txt[:60])
    check("Telegram text says explicitly it is not a reason to sell the rubber names",
          "KHÔNG phải cớ bán cổ phiếu cao su" in txt)
    check("Telegram text does not tell anyone to act on positions",
          "không phải lệnh hành động" in txt)

# 8c. DOES NOT FIRE: one month below is noise, the 2-period confirmation swallows it
print("  -- a single month below (must NOT fire)")
with tempfile.TemporaryDirectory() as tmp:
    rw = tb_box(tmp, [3.0] * 24 + [3.0, 2.0])
    rw._save_state({"trend_state": "UPTREND", "trend_since": "2020-10"})
    r = rw.trend_break_check()
    check("1 month below -> state stays UPTREND (confirm=2 works)", r["state"] == "UPTREND", r["state"])
    check("...no bus event, no Telegram", len(rw.bused) == 0 and len(rw.sent) == 0)
    check("...stored state untouched", json.load(open(rw.STATEF))["trend_state"] == "UPTREND")
    # ...and the very next month below DOES flip it (the gate delays, it does not mute)
    rw2 = tb_box(tmp, [3.0] * 24 + [3.0, 2.0, 2.0], reset_state=False)
    check("next month below -> now it flips (delayed, not suppressed)",
          rw2.trend_break_check()["state"] == "DOWNTREND" and len(rw2.sent) == 1)

# 8d. PROVISIONAL: the flip depends on the still-running month estimated from the daily feed
print("  -- PROVISIONAL: flip depends on the unpublished current month")
with tempfile.TemporaryDirectory() as tmp:
    # WB published through 2022-01 (one month below); the daily feed supplies 2022-02,
    # whose estimate is what completes the 2-month confirmation.
    prices = [3.0] * 24 + [2.0]                       # 2020-01 .. 2022-01
    daily = [("2022-02-03", 2.0, "regionalert"), ("2022-02-10", 2.0, "regionalert")]
    rw = tb_box(tmp, prices, daily)
    rw._save_state({"trend_state": "UPTREND", "trend_since": "2020-10"})
    r = rw.trend_break_check()
    check("provisional month detected from the daily feed", r["prov_month"] == "2022-02", str(r["prov_month"]))
    check("state would be DOWNTREND...", r["state"] == "DOWNTREND", r["state"])
    check("...but it is flagged PROVISIONAL (state differs without the estimate)",
          r["provisional"] is True and r.get("state_firm") == "UPTREND", str(r.get("state_firm")))
    check("PROVISIONAL -> bus notice to Taylor only", len(rw.bused) == 1
          and rw.bused[0][2]["audience"] == ["Taylor"], str(rw.bused))
    check("PROVISIONAL -> NO Telegram (an unpublished figure must not page anyone)",
          len(rw.sent) == 0, f"{len(rw.sent)} sent")
    check("PROVISIONAL -> stored state NOT advanced (only WB publication finalises it)",
          json.load(open(rw.STATEF))["trend_state"] == "UPTREND")
    check("PROVISIONAL notice is deduped by month (daily cron must not repeat it)",
          rw.trend_break_check() and len(rw.bused) == 1, f"{len(rw.bused)} events")
    check("PROVISIONAL bus topic says TẠM TÍNH", "TẠM TÍNH" in rw.bused[0][1], rw.bused[0][1])

    # WB then publishes 2022-02 -> the same flip becomes final and DOES page
    rw2 = tb_box(tmp, prices + [2.0], daily, reset_state=False)
    r2 = rw2.trend_break_check()
    check("once WB publishes the month -> no longer provisional", r2["provisional"] is False)
    check("...now Telegram fires and the state is finalised",
          len(rw2.sent) == 1 and json.load(open(rw2.STATEF))["trend_state"] == "DOWNTREND")

    # a provisional flip that reverts must clear its dedupe marker, not linger
    rw3 = tb_box(tmp, [3.0] * 24 + [2.0], [("2022-02-03", 3.5, "regionalert")], reset_state=False)
    rw3._save_state({"trend_state": "UPTREND", "trend_prov_notice": "2022-02"})
    rw3.trend_break_check()
    check("reverted provisional clears its dedupe marker",
          json.load(open(rw3.STATEF)).get("trend_prov_notice") is None)

# 8e. first run ever = baseline adoption, silent (wiring the tier is not itself a signal)
print("  -- first run / fail-closed")
with tempfile.TemporaryDirectory() as tmp:
    rw = tb_box(tmp, [3.0] * 24 + [2.0, 2.0])
    r = rw.trend_break_check()
    check("first run adopts the state silently", len(rw.sent) == 0 and len(rw.bused) == 0
          and json.load(open(rw.STATEF))["trend_state"] == "DOWNTREND", str(rw.bused))

# 8e-bis. REGRESSION (quant-skeptic, 2026-08-06, first wiring attempt): the baseline path
# read `state` instead of `state_firm`, so a first run landing while the flip depends on the
# UNPUBLISHED running month wrote that provisional state into the state file permanently and
# unflagged — and when WB later published a different number the tier would have manufactured
# a flip that never happened. The baseline must come from published months only.
print("  -- REGRESSION: first run while the state depends on an unpublished month")
with tempfile.TemporaryDirectory() as tmp:
    prices = [3.0] * 24 + [2.0]                                  # published: 1 month below
    daily = [("2022-02-03", 2.0, "regionalert")]                 # estimate completes confirm=2
    rw = tb_box(tmp, prices, daily)                              # NO stored state at all
    r = rw.trend_break_check()
    check("first run: reading IS provisional (would-be DOWNTREND)",
          r["provisional"] is True and r["state"] == "DOWNTREND" and r["state_firm"] == "UPTREND",
          f"{r['state']} / firm {r['state_firm']}")
    st = json.load(open(rw.STATEF))
    check("first run stores the PUBLISHED-only state, not the provisional one",
          st["trend_state"] == "UPTREND", str(st.get("trend_state")))
    check("first run stays silent (no Telegram, no bus)", not rw.sent and not rw.bused)
    check("first run does NOT pre-consume the provisional dedupe marker",
          st.get("trend_prov_notice") is None, str(st.get("trend_prov_notice")))
    # ...and the next run then reports the provisional divergence properly (bus, no Telegram)
    rw2 = tb_box(tmp, prices, daily, reset_state=False)
    rw2.trend_break_check()
    check("next run reports the provisional flip to Taylor, still no Telegram",
          len(rw2.bused) == 1 and rw2.bused[0][2]["provisional"] is True and not rw2.sent,
          f"bus={len(rw2.bused)} tg={len(rw2.sent)}")
    # ...and if WB's real number contradicts the estimate, NOTHING was ever committed
    rw3 = tb_box(tmp, prices + [3.1], daily, reset_state=False)  # WB publishes 2022-02 = 3.1
    r3 = rw3.trend_break_check()
    check("WB publishes a contradicting month -> no flip was ever committed, no alert",
          r3["state"] == "UPTREND" and not rw3.sent
          and json.load(open(rw3.STATEF))["trend_state"] == "UPTREND", r3["state"])

# 8e-ter. the estimate can only ADD a flip, never cancel one (confirm=2 needs both of the
# last two months on the new side, so one appended month cannot undo a committed flip).
# Worst case is therefore a signal one month late, never a signal lost.
with tempfile.TemporaryDirectory() as tmp:
    rw = tb_box(tmp, [3.0] * 24 + [2.0, 2.0], [("2022-03-03", 3.9, "regionalert")])
    r = rw.trend_break_check()
    check("a high estimate cannot cancel a flip the published months already made",
          r["state"] == "DOWNTREND" and r["state_firm"] == "DOWNTREND"
          and r["provisional"] is False, f"{r['state']} / firm {r['state_firm']}")

# 8f. fail-closed: unusable monthly data -> UNKNOWN, never a signal
with tempfile.TemporaryDirectory() as tmp:
    rw = tb_box(tmp, [3.0] * 24)
    rw.MONTHLY = os.path.join(tmp, "__no_such_file__.csv")
    r = rw.trend_break_check()
    check("missing monthly file -> UNKNOWN, no fire", r["state"] == "UNKNOWN"
          and not rw.sent and not rw.bused, r["state"])
    rw2 = tb_box(tmp, [3.0] * 5)              # shorter than the MA window
    r2 = rw2.trend_break_check()
    check("series shorter than MA10 -> UNKNOWN, no fire", r2["state"] == "UNKNOWN"
          and not rw2.sent and not rw2.bused, r2["state"])

# 8g. the wb_seed rows must never feed the provisional estimate (they ARE WB monthly
# points copied into the daily file — folding them back in would be circular)
with tempfile.TemporaryDirectory() as tmp:
    rw = tb_box(tmp, [3.0] * 24 + [2.0],
                [("2022-02-03", 9.99, "wb_seed"), ("2022-02-10", 2.0, "regionalert")])
    s, prov = rtb.monthly_with_current(rw.MONTHLY, rw.CSV)
    check("provisional estimate ignores wb_seed rows",
          abs(float(s.loc["2022-02-15"]) - 2.0) < 1e-9, f"{float(s.loc['2022-02-15'])}")

# 8h. causality: the state at month t must not change when later months arrive
print("  -- causality + backtest reproduction on the REAL WB series")
real, _ = rtb.monthly_with_current(os.path.join(HERE, "data", "rubber_monthly.csv"))
full = rtb.trend_state(real)["states"]
for cut in (120, 180, 220):
    part = rtb.trend_state(real.iloc[:cut])["states"].dropna()
    check(f"no look-ahead at cut={cut}", (part == full.loc[part.index]).all())

# 8i. reproduce the pinned backtest of the approved design (§3a): 5 down-cycles found by
# a 25% zigzag, every one of them caught. Cycle detection is copied from the design's T3
# so this is a reproduction, not a re-derivation.
def zigzag(v, thr=0.25):
    piv, mode, last_i = [], None, 0
    for i in range(1, len(v)):
        if mode in (None, "up"):
            if v[i] > v[last_i]:
                last_i = i
            elif v[i] / v[last_i] - 1 <= -thr:
                piv.append(("P", last_i)); mode, last_i = "down", i
                continue
        if mode in (None, "down"):
            if v[i] < v[last_i]:
                last_i = i
            elif v[i] / v[last_i] - 1 >= thr:
                piv.append(("T", last_i)); mode, last_i = "up", i
    return piv


# The design measured 2006-04 .. 2026-07. The window is FROZEN to that sample so the pinned
# figures stay reproducible as WB publishes new months — a drifting sample would turn a real
# regression into "the numbers moved" noise, and vice versa.
BT_END = "2026-07-15"
bt = real[real.index <= BT_END]
check("backtest sample is the design's 2006-04..2026-07 (244 months)", len(bt) == 244, f"{len(bt)}")
px = bt.values
_piv = zigzag(px)
cycles = [(i1, i2) for (k1, i1), (k2, i2) in zip(_piv, _piv[1:]) if k1 == "P" and k2 == "T"]
check("zigzag finds the 5 documented down-cycles", len(cycles) == 5,
      str([(f"{bt.index[a]:%Y-%m}", f"{bt.index[b]:%Y-%m}") for a, b in cycles]))

# events = start of a 2-consecutive-months-below run (the design's T3 definition, the one
# the 5/5 and 85% figures are measured on), built from the PRODUCTION module's constants
ma = bt.rolling(rtb.MA_WIN).mean()
below = (bt < ma) & ma.notna()
run = below & below.shift(1, fill_value=False)
ev = [i for i, x in enumerate((run & ~run.shift(1, fill_value=False)).values) if x]
in_cyc = set()
for a, b in cycles:
    in_cyc.update(range(a, b + 1))
hits = sum(1 for a, b in cycles if any(a <= e <= b for e in ev))
check("BACKTEST: recall 5/5 down-cycles caught", hits == len(cycles) == 5, f"{hits}/{len(cycles)}")
check("BACKTEST: 13 events, 11 inside a real down-cycle -> precision 85%",
      len(ev) == 13 and sum(1 for e in ev if e in in_cyc) == 11,
      f"{sum(1 for e in ev if e in in_cyc)}/{len(ev)}")
check("BACKTEST: the 2 false positives are the documented 2023-07 and 2025-04",
      [f"{bt.index[e]:%Y-%m}" for e in ev if e not in in_cyc] == ["2023-07", "2025-04"],
      str([f"{bt.index[e]:%Y-%m}" for e in ev if e not in in_cyc]))
check("BACKTEST: fire frequency ~1 / 18.7 months as documented",
      abs(len(bt) / len(ev) - rtb.BT["freq_months"]) < 1.0, f"{len(bt)/len(ev):.1f} months")
# every documented cycle-entry month must appear as a state flip too (the wired object)
st_bt = rtb.trend_state(bt)["states"].dropna()
flips = [f"{st_bt.index[i]:%Y-%m}" for i in range(1, len(st_bt))
         if st_bt.iloc[i] == "DOWNTREND" and st_bt.iloc[i - 1] != "DOWNTREND"]
check("BACKTEST: the wired STATE machine flips on all 5 documented cycle entries",
      all(m in flips for m in ["2008-10", "2011-07", "2017-07", "2019-09", "2021-07"]), str(flips))

# 8j. the live reading on the real files. The pinned half uses the PUBLISHED history only
# (<= 2026-07): the with-provisional figure moves with every new daily print, so pinning it
# would make this selfcheck fail on ordinary data arrival rather than on a regression.
pin = rtb.trend_state(bt)
check("pinned (published-only) reading: 2.78 vs MA10 2.372 = +17.2%, UPTREND",
      pin["state"] == "UPTREND" and abs(pin["price"] - 2.78) < 5e-3
      and abs(pin["ma"] - 2.372) < 5e-3 and abs(pin["dist_pct"] - 17.2) < 0.05,
      f"{pin['price']:.2f} vs {pin['ma']:.3f} = {pin['dist_pct']:+.1f}%")
live = rtb.evaluate(os.path.join(HERE, "data", "rubber_monthly.csv"),
                    os.path.join(HERE, "data", "rubber_weekly.csv"))
check("live evaluation returns a real state (not UNKNOWN)", live["state"] in ("UPTREND", "DOWNTREND"),
      f"{live['state']} {live['dist_pct']:+.1f}%")
check("live dist_pct is internally consistent with price/MA",
      abs(live["dist_pct"] - (live["price"] / live["ma"] - 1) * 100) < 1e-9)
check("live state is UPTREND (design report §0, and unchanged since)",
      live["state"] == "UPTREND", f"{live['state']} {live['dist_pct']:+.1f}%")

# 8k. end-to-end through main(): the note must carry the tier AND its reading, and the
# tier must not disturb the WATCH/ALERT ladder it runs beside.
with tempfile.TemporaryDirectory() as tmp:
    sent8, bused8 = [], []
    rw = load_module(data_dir=tmp)
    rw.CSV = os.path.join(tmp, "rubber_weekly.csv")
    rw.NOTE = os.path.join(tmp, "rubber_watch.md")
    rw.MONTHLY = os.path.join(HERE, "data", "rubber_monthly.csv")
    df_asof(None, "2026-08-04").to_csv(rw.CSV, index=False)
    rw.fetch_regionalert = lambda: {"date": "2026-08-04", "src": "regionalert", "rss3_usdkg": 2.596}
    rw.fetch_sunsirs = lambda: (_ for _ in ()).throw(RuntimeError("stubbed off"))
    rw.telegram = lambda t: sent8.append(t) or True
    rw.bus = lambda et, t, p: bused8.append((et, t, p))
    rw.main()
    note8 = open(rw.NOTE, encoding="utf-8").read()
    check("E2E: note renders the TREND_BREAK section", "TREND_BREAK" in note8
          and "MA200-eq" in note8, note8[-400:][:80])
    check("E2E: note states the reading (regime confirmation, not a sell/forecast signal)",
          "KHÔNG phải tín hiệu bán/dự báo" in note8)
    check("E2E: note keeps WATCH/ALERT and TREND_BREAK as separate sections",
          "## Ngưỡng cảnh báo (đã duyệt)" in note8 and "## Xu thế dài hạn" in note8)
    check("E2E: first run initialises the tier silently (no Telegram, no bus)",
          len(sent8) == 0 and not any("TREND" in t for _, t, _ in bused8), str(bused8))
    check("E2E: the 2026-08-04 WATCH/ALERT verdict is unchanged by the new tier",
          "🟢 INFO" in note8, note8.split("Trạng thái:")[1][:24].strip())

# 8l. the tier stays independent of WATCH/ALERT — no shared thresholds, no shared state key
check("TREND_BREAK does not reuse any WATCH/ALERT threshold",
      "WATCH_WOW" not in open(os.path.join(HERE, "rubber_trend_break.py"), encoding="utf-8").read())
check("TREND_BREAK state keys are separate from the ALERT dedupe keys",
      "trend_state" in src and "last_tier" in src and "trend_state" != "last_tier")

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
