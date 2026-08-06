#!/usr/bin/env python3
"""
rubber_weekly.py — natural-rubber price feed + DAILY threshold alerting
======================================================================
Why: the WB Pink Sheet rubber series (data/rubber_monthly.csv, RSS3 USD/kg) is
MONTHLY — too coarse to catch a fast cyclical move in the rubber names
(GVR, PHR, DPR, DRI, TRC, HRC). This fills the gap with a higher-frequency feed
and — per user request — fires an alert the SAME DAY a move crosses a threshold
vs the PRIOR WEEK's close, so Taylor (model/forecast) and Bill (PM action) hear
about it immediately, not at week-end.

Sources (both confirmed parseable, 2026-06):
  1. regionalert.com/prices/natural-rubber  — RSS3/TSR20 SGX SICOM settlement
     (USD/ton, daily). PRIMARY: RSS3 continues the WB RSS3 USD/kg series 1:1.
  2. SunSirs prodetail-586                   — China natural-rubber spot
     (RMB/ton). Cross-check on Chinese demand; reuses the HW_CHECK cookie-wall
     solver proven in phosphorus_dgc_weekly.py.

Cadence: run DAILY (Mon-Fri after close, cron). It is idempotent — re-running
is safe; the alert state file dedupes so the same WATCH is not re-sent every day
(only re-affirmed weekly, or fired immediately if it escalates WATCH->ALERT).

Alert tiers (thresholds approved by user; grounded in 20yr RSS3 vol:
weekly 1sigma ~4%, monthly |chg| p75 8.9%/p90 13%, 3mo p75 18%/p90 28%):
  WATCH  -> ping Taylor : |WoW| >= 7%  OR |4wk cum| >= 15%
  ALERT  -> ping Bill+Taylor (+Telegram +user): |WoW| >= 12% OR |3mo cum| >= 25%
            OR new 52-week cycle-band high/low. The band needs a window that COVERS
            ~52 weeks of calendar time (WB monthly spliced under the short daily
            feed), and an ALERT must repeat on 2 consecutive observation dates
            before the loud channel (Telegram/Bill) opens — both hardened after the
            2026-08-04 false "52w low" ALERT (rubber_weekly_selfcheck.py).

A SECOND, INDEPENDENT tier rides along (rubber_trend_break.py): TREND_BREAK/TREND_OK,
a MONTHLY long-horizon regime confirmation on the WB series. It is deliberately NOT part
of the WATCH/ALERT ladder above — different question, different horizon (6-24 months vs
1 week), different cadence (~1 fire / 18.7 months vs weekly). It is a REGIME CONFIRMATION,
never a sell signal or a forecast; see that module's docstring for the evidence.

Outputs:
  data/rubber_weekly.csv        price series (appendable, deduped by date)
  data/rubber_watch.md          living dated assessment
  data/rubber_alert_state.json  dedupe memory for the alert engine
"""
import os, re, ssl, sys, json, subprocess
from datetime import datetime, timedelta
import urllib.request, urllib.parse
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:            # the selfcheck imports this file by path, not by name
    sys.path.insert(0, _HERE)
import rubber_trend_break as rtb     # sibling module: the monthly TREND_BREAK tier
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

WORKDIR = os.environ.get("WORKDIR_8L", os.path.dirname(os.path.abspath(__file__)))
DATA       = os.path.join(WORKDIR, "data")
CSV        = os.path.join(DATA, "rubber_weekly.csv")
MONTHLY    = os.path.join(DATA, "rubber_monthly.csv")        # WB seed source
NOTE       = os.path.join(DATA, "rubber_watch.md")
STATEF     = os.path.join(DATA, "rubber_alert_state.json")
TG_CONFIG  = os.path.join(WORKDIR, "secrets", "telegram_config.json")
APPEND_EVT = "/home/trido/thanhdt/WorkingClaude/mike/bin/append_event.sh"

RA_URL  = "https://regionalert.com/prices/natural-rubber/"
SS_URL  = "https://www.sunsirs.com/uk/prodetail-586.html"   # China natural rubber spot
UA      = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"

# --- alert thresholds (percent) -------------------------------------------------
WATCH_WOW, WATCH_4WK, WATCH_3MO = 7.0, 15.0, 18.0   # 3mo p75 hist = slow-trend catch
ALERT_WOW, ALERT_3MO = 12.0, 25.0
STOCKS = ["GVR", "PHR", "DPR", "DRI", "TRC", "HRC"]

# --- 52-week cycle band ---------------------------------------------------------
# The band gate is a CALENDAR-COVERAGE test, not a row count. The daily feed only
# started 2026-06-19; a row count opens after ~30 prints (~6 weeks) and then calls
# every dip a "52-week low" (real false ALERT, 2026-08-04 — see selfcheck).
BAND_DAYS     = 365    # look-back window
BAND_MIN_SPAN = 330    # window must genuinely span >= this many days to be a "52w" band
BAND_MAX_GAP  = 45     # no hole bigger than this inside the window (monthly step ~31d)


# ------------------------------------------------------------------ fetchers ----
def fetch_regionalert():
    """RSS3/TSR20 (USD/kg) + date from regionalert og:description (stable target)."""
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    html = urllib.request.urlopen(urllib.request.Request(RA_URL, headers={"User-Agent": UA}),
                                  timeout=30, context=ctx).read().decode("utf-8", "ignore")
    rss3 = re.search(r'RSS3 \$([0-9,]+)\s*/?\s*ton', html)
    tsr20 = re.search(r'TSR20 \$([0-9,]+)\s*/?\s*ton', html)
    mdate = re.search(r'on ([A-Z][a-z]+ \d{1,2}, \d{4})', html)
    if not (rss3 and mdate):
        raise RuntimeError("regionalert format changed (RSS3/date not found)")
    d = datetime.strptime(mdate.group(1), "%B %d, %Y").strftime("%Y-%m-%d")
    row = {"date": d, "src": "regionalert",
           "rss3_usdkg": float(rss3.group(1).replace(",", "")) / 1000.0}
    if tsr20:
        row["tsr20_usdkg"] = float(tsr20.group(1).replace(",", "")) / 1000.0
    return row


def fetch_sunsirs():
    """China spot rubber (RMB/ton) latest print — HW_CHECK cookie wall, best-effort."""
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    hdr = {"User-Agent": UA}
    stub = urllib.request.urlopen(urllib.request.Request(SS_URL, headers=hdr), timeout=30, context=ctx).read().decode("utf-8", "ignore")
    m = re.search(r'var _0x2 = "([0-9a-f]+)"', stub)
    if not m:
        raise RuntimeError("SunSirs HW_CHECK token not found")
    h2 = dict(hdr); h2["Cookie"] = "HW_CHECK=" + m.group(1)
    html = urllib.request.urlopen(urllib.request.Request(SS_URL, headers=h2), timeout=30, context=ctx).read().decode("utf-8", "ignore")
    rows = re.findall(r'(\d{4,6}\.\d{2})\s*</td>\s*<td[^>]*>\s*(\d{4}-\d{2}-\d{2})', html)
    if not rows:
        raise RuntimeError("SunSirs price table not parsed")
    p, d = rows[0]                          # newest row first
    return {"date": d, "cn_rmb_ton": float(p)}


# ------------------------------------------------------------------ storage -----
def seed_from_monthly():
    """Bootstrap the weekly CSV from the last ~4 WB monthly points so 4wk/3mo
    context exists on the very first live run. Real daily prints take over."""
    if not os.path.exists(MONTHLY):
        return pd.DataFrame()
    m = pd.read_csv(MONTHLY).tail(4).copy()
    m["date"] = m["month"].astype(str) + "-15"          # mid-month anchor
    m = m.rename(columns={"price": "rss3_usdkg"})
    m["src"] = "wb_seed"
    return m[["date", "rss3_usdkg", "src"]]


def monthly_series():
    """Full WB Pink Sheet monthly RSS3 (USD/kg) as a dated series, mid-month anchor.
    Same anchor convention as seed_from_monthly(); used to back-fill the 52w band
    window for the stretch the daily feed does not reach."""
    empty = pd.Series(dtype=float, index=pd.DatetimeIndex([]))   # must stay date-indexed:
    try:                                                         # a RangeIndex here crashes
        m = pd.read_csv(MONTHLY)                                 # band_52w's date compare
        s = pd.Series(m["price"].astype(float).values,
                      index=pd.to_datetime(m["month"].astype(str) + "-15"))
    except Exception as e:
        print(f"  [warn] WB monthly seed unreadable ({e}) — 52w band will fail closed")
        return empty
    return s[s.notna()].sort_index()


def update_csv(rows):
    new = pd.DataFrame([r for r in rows if r])
    if not new.empty:
        new["fetched"] = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(CSV):
        old = pd.read_csv(CSV)
        comb = pd.concat([old, new], ignore_index=True)
    else:
        comb = pd.concat([seed_from_monthly(), new], ignore_index=True)
    # merge same-date rows (RSS3 from regionalert + RMB from sunsirs land separately)
    comb = comb.sort_values("date")
    agg = comb.groupby("date", as_index=False).agg(
        lambda s: s.dropna().iloc[-1] if s.dropna().size else None)
    agg = agg.sort_values("date").reset_index(drop=True)
    os.makedirs(DATA, exist_ok=True)
    agg.to_csv(CSV, index=False)
    return agg


# ------------------------------------------------------------------ trend -------
def _nearest(s, latest_dt, days, tol):
    """% change of latest vs the point nearest (latest - days), within +/-tol days."""
    target = latest_dt - timedelta(days=days)
    diff = (s.index - target)
    dd = pd.Series([d.days for d in diff])
    i = int(dd.abs().idxmin()); ref = s.index[i]
    if ref == latest_dt or abs(int(dd.iloc[i])) > tol:
        return None, None
    return (float(s.iloc[-1]) / float(s.iloc[i]) - 1) * 100, ref


def trend(df):
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    d = d[d["rss3_usdkg"].notna()].sort_values("date").set_index("date")
    s = d["rss3_usdkg"].astype(float)
    latest, latest_dt = float(s.iloc[-1]), s.index[-1]
    real = d[d["src"] != "wb_seed"]                    # exclude monthly seeds

    # WoW vs PRIOR WEEK's close: most recent print in an earlier ISO week,
    # but only if it is genuinely ~a week old (<=12d) — guards against a stale
    # monthly seed masquerading as "last week".
    cur_wk = latest_dt.isocalendar()[:2]
    prior = s[[ix.isocalendar()[:2] < cur_wk for ix in s.index]]
    wow, wow_ref = None, None
    if len(prior):
        pv_dt = prior.index[-1]
        if (latest_dt - pv_dt).days <= 12:
            wow = (latest / float(prior.iloc[-1]) - 1) * 100; wow_ref = pv_dt

    c4w, c4w_ref = _nearest(s, latest_dt, 28, 12)
    c3m, c3m_ref = _nearest(s, latest_dt, 91, 21)

    band, bd = band_52w(real, latest, latest_dt)
    return dict(latest=latest, latest_dt=latest_dt, wow=wow, wow_ref=wow_ref,
                c4w=c4w, c4w_ref=c4w_ref, c3m=c3m, c3m_ref=c3m_ref, band=band,
                band_lo=bd["lo"], band_hi=bd["hi"], band_span=bd["span"],
                band_ok=bd["ok"], band_soft=bd["soft"], band_note=bd["note"], series=s)


def band_52w(real, latest, latest_dt):
    """52-week cycle band. Judged ONLY when the window genuinely covers ~52 weeks
    of CALENDAR time (>= BAND_MIN_SPAN days, no hole > BAND_MAX_GAP) — the daily
    feed alone cannot, so the WB monthly series is spliced in ahead of the daily
    series' first print. Returns (band|None, detail dict) — detail always populated
    so the note/payload can show the band actually compared against."""
    bd = {"lo": None, "hi": None, "span": 0, "ok": False, "soft": False, "note": ""}
    if not len(real) or real.index[-1] != latest_dt:
        bd["note"] = "chưa có giá thật ở phiên mới nhất"     # latest print is a seed
        return None, bd

    win_start = latest_dt - timedelta(days=BAND_DAYS)
    parts = [real[real.index >= win_start]["rss3_usdkg"].astype(float)]
    mo = monthly_series()
    mo = mo[(mo.index >= win_start) & (mo.index < real.index[0])]
    if len(mo):
        parts.insert(0, mo)
    win = pd.concat(parts).sort_index()
    win = win[~win.index.duplicated(keep="last")]

    bd["span"] = (latest_dt - win.index[0]).days
    gap = max((b - a).days for a, b in zip(win.index[:-1], win.index[1:])) if len(win) > 1 else 10**6
    if bd["span"] < BAND_MIN_SPAN:
        bd["note"] = f"chuỗi mới phủ {bd['span']}/{BAND_MIN_SPAN} ngày — chưa đủ 52 tuần"
        return None, bd
    if gap > BAND_MAX_GAP:
        bd["note"] = f"chuỗi thủng {gap} ngày (> {BAND_MAX_GAP}) — biên không đáng tin"
        return None, bd

    bd["lo"], bd["hi"], bd["ok"] = float(win.min()), float(win.max()), True
    bd["note"] = (f"biên {bd['lo']:.2f}–{bd['hi']:.2f} USD/kg, phủ {bd['span']}d "
                  f"({len(mo)} điểm WB monthly + {len(parts[-1])} phiên thật)")
    if latest >= bd["hi"]:  band = "high"
    elif latest <= bd["lo"]: band = "low"
    else: return None, bd

    # A WB monthly point is a monthly AVERAGE: it sits strictly inside that month's true
    # daily range, so the spliced stretch hides its own daily extremes and the band comes
    # out NARROWER than reality on BOTH sides — measured on the months where we hold both
    # (monthly means 2.69-2.81 vs true daily 2.60-2.92). A break test against a compressed
    # band OVER-fires: exactly the false-ALERT class this fix exists to kill. So while the
    # window still leans on monthly points at all, a break is "soft" — real enough to
    # report, never enough to prove a 52-week record on its own. It hardens by itself on
    # 2027-06-16, the first day the 365d window clears the last monthly anchor before the
    # daily feed began (2026-06-15) — verified by simulation, not estimated.
    bd["soft"] = bool(len(mo))
    if bd["soft"]:
        bd["note"] += (f" · biên MỀM: {len(mo)} điểm là TRUNG BÌNH THÁNG (WB), cực trị ngày "
                       f"thật của giai đoạn đó không quan sát được — chưa đủ khẳng định kỷ lục")
    return band, bd


def classify(m):
    """Return (tier, [reasons]). tier in {INFO,WATCH,ALERT}."""
    reasons = []
    wow, c4w, c3m = m["wow"], m["c4w"], m["c3m"]
    if wow is not None and abs(wow) >= ALERT_WOW:
        reasons.append(f"WoW {wow:+.1f}% (>= ±{ALERT_WOW:.0f}%)")
    if c3m is not None and abs(c3m) >= ALERT_3MO:
        reasons.append(f"3 tháng {c3m:+.1f}% (>= ±{ALERT_3MO:.0f}%)")
    edge = "đỉnh" if m["band"] == "high" else "đáy"
    if m["band"] and not m["band_soft"]:
        reasons.append(f"phá biên 52 tuần ({edge} mới; "
                       f"biên {m['band_lo']:.2f}–{m['band_hi']:.2f}, phủ {m['band_span']}d)")
    if reasons:
        return "ALERT", reasons
    if m["band"] and m["band_soft"]:          # soft edge: report, but never ALERT alone
        reasons.append(f"chạm {edge} biên 52 tuần {m['band_lo']:.2f}–{m['band_hi']:.2f} "
                       f"nhưng cực trị lấy từ WB monthly (trung bình tháng, bị nén) "
                       f"— chưa đủ khẳng định kỷ lục, cần chuỗi ngày thật dài hơn")
    if wow is not None and abs(wow) >= WATCH_WOW:
        reasons.append(f"WoW {wow:+.1f}% (>= ±{WATCH_WOW:.0f}%)")
    if c4w is not None and abs(c4w) >= WATCH_4WK:
        reasons.append(f"4 tuần {c4w:+.1f}% (>= ±{WATCH_4WK:.0f}%)")
    if c3m is not None and abs(c3m) >= WATCH_3MO:   # slow grind (18-25%); >=25% is ALERT above
        reasons.append(f"3 tháng {c3m:+.1f}% (>= ±{WATCH_3MO:.0f}%)")
    if reasons:
        return "WATCH", reasons
    return "INFO", []


# ------------------------------------------------------------------ alerting ----
def _load_state():
    try:
        with open(STATEF) as f: return json.load(f)
    except Exception:
        return {}


def _save_state(patch):
    """Merge-write: pending_alert must survive a record_fire() and vice versa."""
    st = _load_state(); st.update(patch)
    os.makedirs(DATA, exist_ok=True)
    tmp = STATEF + ".tmp"
    with open(tmp, "w") as f: json.dump(st, f, indent=2)
    os.replace(tmp, STATEF)                      # atomic (coding_guidelines §5)
    return st


def confirm_alert(tier, m):
    """An ALERT must repeat on TWO CONSECUTIVE observation dates before it escalates
    to Telegram + Bill — one anomalous print is not an alert (2026-08-04: RSS3 -6.95%
    in a day while China spot printed +1.52%, data quality unresolved). The bus event
    still goes out immediately so Taylor sees it; only the loud channel waits.
    Returns True once the same ALERT has been seen on a second, later date."""
    cur = str(m["latest_dt"].date())
    if tier != "ALERT":
        st = _load_state()
        dropped = st.get("pending_alert")
        # Did this streak already escalate? record_fire() sets last_alert_confirmed when a
        # CONFIRMED ALERT actually went out, so "streak ended" and "streak fizzled before
        # anyone was paged" are different events and must not share a message.
        escalated = bool(st.get("last_alert_confirmed"))
        _save_state({"pending_alert": None, "last_alert_confirmed": False})
        if dropped and dropped != cur:
            if escalated:
                topic = "rubber: đợt ALERT đã kết thúc (giá không còn vượt ngưỡng)"
                note = ("Đợt ALERT bắt đầu {d} ĐÃ được xác nhận và ĐÃ gửi Telegram/Bill trước đó; "
                        "nay giá không còn vượt ngưỡng nào — coi như đóng đợt.").format(d=dropped)
            else:
                topic = "rubber: ALERT chờ xác nhận đã tự huỷ (phiên sau không lặp lại)"
                note = ("1 phiên vượt ngưỡng rồi đảo lại, CHƯA từng gửi Telegram/Bill — đúng thiết kế "
                        "của lớp xác nhận 2 phiên. Trễ tối đa là 1 phiên chạy (cron T2-T6 18:35 ICT), "
                        "tức tối đa ~3 ngày lịch nếu phiên đầu rơi vào thứ Sáu. Nếu đây là sụt giảm "
                        "hình chữ V thật, Taylor đã nhận event ALERT của phiên đầu.")
            # event_type MUST stay in the set mike_json.py:cmd_delta_append forwards
            # ("finding","answer","decision","verification") — a "status" event never reaches
            # the auto-injected RECENT block, i.e. Taylor would not actually see this.
            bus("finding", topic,
                {"pending_since": dropped, "resolved_on": cur, "tier_now": tier,
                 "escalated_before": escalated, "rss3_usdkg": round(m["latest"], 3),
                 "audience": ["Taylor"] + (["DollarBill"] if escalated else []),
                 "note": note})
        return False
    first = _load_state().get("pending_alert")
    if not first:
        _save_state({"pending_alert": cur})      # first sighting
        return False
    return first != cur                          # re-run on the SAME date confirms nothing


def should_fire(tier, m, confirmed=False):
    """Dedupe: fire WATCH/ALERT once per ISO-week, but ALWAYS on escalation."""
    if tier == "INFO":
        return False
    st = _load_state()
    cur_wk = "%d-W%02d" % m["latest_dt"].isocalendar()[:2]
    rank = {"INFO": 0, "WATCH": 1, "ALERT": 2}
    last_tier, last_wk = st.get("last_tier", "INFO"), st.get("last_week", "")
    if rank[tier] > rank.get(last_tier, 0):     # escalation -> always
        return True
    if tier == "ALERT" and confirmed and not st.get("last_alert_confirmed", False):
        return True                              # unconfirmed -> confirmed is an escalation too
    if cur_wk != last_wk:                        # new week -> re-affirm
        return True
    return False                                 # same week, same/lower tier -> mute


def record_fire(tier, m, confirmed=False):
    _save_state({"last_tier": tier,
                 "last_week": "%d-W%02d" % m["latest_dt"].isocalendar()[:2],
                 "last_date": str(m["latest_dt"].date()),
                 "last_alert_confirmed": bool(tier == "ALERT" and confirmed)})


def bus(event_type, topic, payload):
    try:
        subprocess.run([APPEND_EVT, "Winston", event_type, topic, json.dumps(payload, ensure_ascii=False)],
                       timeout=30, check=False)
    except Exception as e:
        print(f"  [warn] bus append failed: {e}")


def telegram(text):
    try:
        with open(TG_CONFIG) as f: cfg = json.load(f)
        chat_ids = cfg["chat_id"] if isinstance(cfg["chat_id"], (list, tuple)) else [cfg["chat_id"]]
        url = f"https://api.telegram.org/bot{cfg['bot_token']}/sendMessage"
        for cid in chat_ids:
            data = urllib.parse.urlencode({"chat_id": cid, "text": text,
                                           "parse_mode": "HTML", "disable_web_page_preview": "true"}).encode()
            urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30).read()
        return True
    except Exception as e:
        print(f"  [warn] telegram send failed: {e}")
        return False


def fire(tier, reasons, m, confirmed=False):
    direction = "TĂNG" if (m["wow"] or m["c3m"] or m["c4w"] or 0) > 0 else "GIẢM"
    loud = tier == "ALERT" and confirmed          # Telegram + Bill only once confirmed
    audience = ["Taylor", "DollarBill"] if loud else ["Taylor"]
    is_3mo_watch = any("3 tháng" in r for r in reasons)
    if tier == "ALERT":
        action = "Taylor rà mô hình/dự báo nhóm cao su; Bill cân nhắc kế hoạch hành động vị thế"
    elif is_3mo_watch:
        action = ("Taylor CHẠY LẠI mô hình 8L xem có đổi đánh giá nhóm cao su không "
                  "(xu hướng 3 tháng vượt ±18%)")
    else:
        action = "Taylor rà xem input giá đã lệch giả định mô hình chưa (nhóm cao su)"
    payload = {"tier": tier, "confirmed": confirmed if tier == "ALERT" else None,
               "direction": direction, "rss3_usdkg": round(m["latest"], 3),
               "date": str(m["latest_dt"].date()), "reasons": reasons, "audience": audience,
               "band_52w": None if not m["band_ok"] else [round(m["band_lo"], 3), round(m["band_hi"], 3)],
               "band_note": m["band_note"],
               "wow_pct": None if m["wow"] is None else round(m["wow"], 1),
               "cum4wk_pct": None if m["c4w"] is None else round(m["c4w"], 1),
               "cum3mo_pct": None if m["c3m"] is None else round(m["c3m"], 1),
               "stocks": STOCKS, "action": action}
    topic_tier = tier if loud else (f"{tier} (chờ xác nhận)" if tier == "ALERT" else tier)
    bus("finding", f"rubber {topic_tier}: cao su {direction} {m['latest']:.2f} USD/kg", payload)

    if loud:
        emoji = "🔴"
        msg = (f"{emoji} <b>CAO SU — {tier} ({direction})</b>\n"
               f"RSS3 <b>{m['latest']:.2f} USD/kg</b> ({m['latest_dt'].date()})\n"
               f"{' · '.join(reasons)}\n"
               f"→ <b>Taylor</b>: rà mô hình/dự báo nhóm cao su\n"
               f"→ <b>Bill</b>: cân nhắc kế hoạch hành động vị thế\n"
               f"CP: {', '.join(STOCKS)}")
        telegram(msg)
        print(f"\n{'='*60}\n🔴 ALERT (gửi Telegram + bus → Taylor & Bill)\n{msg}\n{'='*60}")
    elif tier == "ALERT":
        print(f"\n🟠 ALERT CHỜ XÁC NHẬN (chỉ bus → Taylor, chưa gửi Telegram/Bill; "
              f"cần lặp lại ở phiên kế tiếp): {' · '.join(reasons)}")
    else:
        print(f"\n🟡 WATCH (bus → Taylor): {' · '.join(reasons)}")
    record_fire(tier, m, confirmed)


# -------------------------------------------------------- TREND_BREAK tier ------
def trend_break_check():
    """Evaluate the INDEPENDENT monthly regime tier and fire only on a STATE FLIP.

    Why a flip and not a level: the tier is a state (UPTREND/DOWNTREND) that holds for
    ~18.7 months on average, so firing on "currently below the line" would page the team
    every single day of a downtrend. The last confirmed state lives in the same state
    file as the WATCH/ALERT dedupe, under its own keys.

    Three behaviours worth stating explicitly:
      * FIRST run ever (no stored state) = baseline initialisation, silent. Otherwise
        wiring the tier would itself look like a signal. The baseline adopted is the
        PUBLISHED-ONLY state (`state_firm`), never the one that leans on the running
        month's estimate: an unpublished figure written into the state file is permanent
        and unflagged, and would manufacture a fake flip later when WB publishes the real
        number. (Found by quant-skeptic on the first wiring attempt, 2026-08-06.)
      * PROVISIONAL flip (the state depends on the still-running month, estimated from
        the daily feed) -> bus notice to Taylor, flagged, deduped by month, and the
        stored state is NOT advanced. It only becomes final when WB publishes the month.
        No Telegram: an unpublished figure must not page anyone.
      * Any message carries the regime-confirmation wording from rubber_trend_break.py.
        This tier is NOT a sell signal and NOT a forecast (see that module's docstring).
    Returns the evaluation dict (state UNKNOWN if the monthly series is unusable) so the
    note can render it; never raises into the caller."""
    try:
        r = rtb.evaluate(MONTHLY, CSV)
    except Exception as e:
        print(f"  [warn] TREND_BREAK không tính được ({e}) — bỏ qua tầng này")
        return {"state": rtb.UNKNOWN, "note": f"lỗi đọc dữ liệu: {e}"}
    if r["state"] == rtb.UNKNOWN:
        return r

    st = _load_state()
    prev = st.get("trend_state")
    r["prev_state"] = prev
    since = f"{r['since']:%Y-%m}"

    if prev is None:                                  # first run: adopt, stay silent
        base = r["state_firm"]                        # published months ONLY — see docstring
        base_since = f"{r['since_firm']:%Y-%m}" if r.get("since_firm") is not None else None
        _save_state({"trend_state": base, "trend_since": base_since,
                     "trend_prov_notice": None})
        print(f"  TREND_BREAK: khởi tạo trạng thái nền = {base} (từ {base_since}) — không bắn"
              + (f"  [tháng {r['prov_month']} chưa công bố, KHÔNG dùng để khởi tạo; "
                 f"ước lượng hiện chỉ sang {r['state']}]" if r["provisional"] else ""))
        return r

    if r["state"] == prev:
        if st.get("trend_prov_notice"):               # a provisional flip that reverted
            _save_state({"trend_prov_notice": None})
        return r

    signal = rtb.SIGNAL_OF[r["state"]]
    payload = {"signal": signal, "tier": "TREND_BREAK", "state": r["state"],
               "prev_state": prev, "provisional": r["provisional"],
               "provisional_month": r["prov_month"], "since": since,
               "rss3_usdkg": round(r["price"], 3), "ma200eq": round(r["ma"], 3),
               "dist_pct": round(r["dist_pct"], 1), "confirm_months": rtb.CONFIRM,
               "source": "World Bank Pink Sheet monthly RSS3",
               "reading": ("XÁC NHẬN CHẾ ĐỘ (regime-confirmation) — KHÔNG PHẢI tín hiệu bán, "
                           "KHÔNG PHẢI dự báo giảm tiếp. P(giảm thêm >=15%/6th sau tín hiệu) = "
                           f"{rtb.BT['p_further_drop']}% ~ base {rtb.BT['p_further_drop_base']}%; "
                           f"rổ CP cao su fwd-12m sau tín hiệu +{rtb.BT['stock_fwd12m']}% vs base "
                           f"+{rtb.BT['stock_fwd12m_base']}% -> KHÔNG dùng để bán GVR/PHR/DPR/DRI."),
               "independent_of": "WATCH/ALERT (nhịp tuần, chân trời 1 tuần)",
               "stocks": STOCKS,
               "action": ("Taylor cập nhật BỐI CẢNH chế độ dài hạn cho mô hình nhóm cao su; "
                          "KHÔNG phải lệnh hành động vị thế")}

    if r["provisional"]:
        if st.get("trend_prov_notice") == r["prov_month"]:
            return r                                  # already announced for this month
        payload["audience"] = ["Taylor"]
        bus("finding", f"rubber {signal} (TẠM TÍNH, chờ WB công bố {r['prov_month']}): "
                       f"cao su {r['price']:.2f} USD/kg", payload)
        _save_state({"trend_prov_notice": r["prov_month"]})
        print(f"\n⏳ {signal} TẠM TÍNH (chỉ bus → Taylor; tháng {r['prov_month']} chưa đóng)")
        print(rtb.message(r, prev))
        return r

    payload["audience"] = ["Taylor", "DollarBill"]
    bus("finding", f"rubber {signal}: chế độ xu thế dài hạn đổi {prev} → {r['state']} "
                   f"({r['price']:.2f} USD/kg)", payload)
    telegram(rtb.message(r, prev, html=True))
    _save_state({"trend_state": r["state"], "trend_since": since, "trend_prov_notice": None})
    print(f"\n{'='*60}\n{rtb.message(r, prev)}\n{'='*60}")
    return r


# ------------------------------------------------------------------ note --------
def render_note(m, tier, reasons, today, tb=None):
    def pct(v, ref): return "—" if v is None else f"{v:+.1f}% (vs {ref.date()})"
    badge = {"ALERT": "🔴 ALERT", "WATCH": "🟡 WATCH", "INFO": "🟢 INFO"}[tier]
    s = m["series"]
    wk = s.reset_index(); wk.columns = ["date", "p"]
    wk["w"] = wk["date"].dt.to_period("W")
    wk = wk.groupby("w", as_index=False).last()[["date", "p"]].tail(8)
    L = [f"# Cao su (RSS3) — theo dõi tuần\n",
         f"_Cập nhật {today} · nguồn: regionalert (SGX SICOM RSS3, USD/kg) + SunSirs-586 (spot TQ)_\n",
         f"## Trạng thái: **{badge}**",
         "" if not reasons else "- Lý do: " + "; ".join(reasons),
         "## Giá & xu hướng",
         f"- **Mới nhất:** {m['latest']:.2f} USD/kg ({m['latest_dt'].date()})",
         f"- **vs tuần trước (WoW):** {pct(m['wow'], m['wow_ref']) if m['wow'] is not None else '— (chưa đủ chuỗi ngày)'}",
         f"- **4 tuần:** {pct(m['c4w'], m['c4w_ref'])}  ·  **3 tháng:** {pct(m['c3m'], m['c3m_ref'])}",
         f"- **Biên 52 tuần:** " + (f"{m['band_lo']:.2f}–{m['band_hi']:.2f} USD/kg "
             f"(WB monthly ghép chuỗi ngày, phủ {m['band_span']}d) — "
             + {"high": "**giá đang phá ĐỈNH biên**", "low": "**giá đang phá ĐÁY biên**"}.get(
                 m["band"], f"giá nằm trong biên")
             if m["band_ok"] else f"— chưa tính được ({m['band_note']})"),
         "",
         "| Tuần (giá đóng) | RSS3 USD/kg |", "|---|---|"]
    for _, r in wk.iterrows():
        L.append(f"| {r['date'].date()} | {r['p']:.2f} |")
    L += [""] + (rtb.note_lines(tb) if tb else [])
    L += ["## Ngưỡng cảnh báo (đã duyệt)",
          f"- 🟡 **WATCH → Taylor**: |WoW| ≥ {WATCH_WOW:.0f}% hoặc |4 tuần| ≥ {WATCH_4WK:.0f}% — rà mô hình/dự báo nhóm cao su.",
          f"- 🟡 **WATCH 3-tháng → Taylor**: |3 tháng| ≥ {WATCH_3MO:.0f}% (xu hướng trườn) → **chạy lại mô hình 8L** xem có đổi đánh giá nhóm cao su không.",
          f"- 🔴 **ALERT → Bill + Taylor** (+Telegram): |WoW| ≥ {ALERT_WOW:.0f}% hoặc |3 tháng| ≥ {ALERT_3MO:.0f}% hoặc phá biên 52 tuần — Bill quyết kế hoạch vị thế.",
          f"  - Biên 52 tuần chỉ được tính khi chuỗi PHỦ ĐỦ ≥ {BAND_MIN_SPAN} ngày lịch (ghép WB monthly vào phần chuỗi ngày chưa với tới), không phải khi đủ số dòng.",
          "  - ALERT phải lặp lại ở **2 phiên đo liên tiếp** mới gửi Telegram/Bill; lần đầu chỉ báo bus cho Taylor.",
          f"- CP cao su theo dõi: {', '.join(STOCKS)}",
          "- Lưu ý: truyền dẫn giá mủ → lợi nhuận trễ ~1 quý; GVR còn chịu chi phối câu chuyện chuyển đổi đất. Giá biến động là điều kiện cần, Taylor phán materiality.", ""]
    with open(NOTE, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# ------------------------------------------------------------------ main --------
def main():
    rows = []
    try:
        ra = fetch_regionalert(); rows.append(ra)
        print(f"regionalert: RSS3 {ra['rss3_usdkg']:.2f} USD/kg ({ra['date']})")
    except Exception as e:
        print(f"  [warn] regionalert fetch failed: {e}")
    try:
        ss = fetch_sunsirs(); rows.append(ss)
        print(f"sunsirs-586: {ss['cn_rmb_ton']:,.0f} RMB/ton ({ss['date']})")
    except Exception as e:
        print(f"  [warn] sunsirs fetch failed: {e}")

    df = update_csv(rows)
    if df["rss3_usdkg"].notna().sum() == 0:
        print("  [error] no RSS3 price available — aborting");
        bus("error", "rubber feed: no RSS3 price", {"detail": "both sources failed or no USD price"})
        sys.exit(1)

    m = trend(df)
    tier, reasons = classify(m)
    confirmed = confirm_alert(tier, m)
    tb = trend_break_check()               # independent monthly tier; fires only on a flip
    today = str(m["latest_dt"].date())
    render_note(m, tier, reasons, today, tb)
    print(f"RSS3 {m['latest']:.2f} USD/kg  WoW={m['wow'] and round(m['wow'],1)}  "
          f"4wk={m['c4w'] and round(m['c4w'],1)}  3mo={m['c3m'] and round(m['c3m'],1)}  "
          f"band={m['band'] or '—'} [{m['band_note']}]  -> {tier}"
          + ("" if tier != "ALERT" else (" (đã xác nhận)" if confirmed else " (chờ xác nhận)")))

    # heartbeat: this tier is silent for months by design — silence must not be
    # indistinguishable from a dead pipeline (fleet heartbeat convention).
    if tb["state"] != rtb.UNKNOWN:
        print(f"TREND_BREAK: {rtb.SIGNAL_OF[tb['state']]} ({tb['state']}, từ {tb['since']:%Y-%m}), "
              f"giá {tb['price']:.2f} vs MA200-eq {tb['ma']:.2f} = {tb['dist_pct']:+.1f}%"
              + (f"  [tạm tính theo tháng {tb['prov_month']}]" if tb["provisional"] else ""))
    else:
        print(f"TREND_BREAK: chưa tính được ({tb.get('note', '')})")

    if should_fire(tier, m, confirmed):
        fire(tier, reasons, m, confirmed)
    else:
        print(f"  ({tier}: không bắn — đã cảnh báo tuần này hoặc dưới ngưỡng)")
    print(f"-> {CSV} ({len(df)} rows)\n-> {NOTE}")


if __name__ == "__main__":
    main()
