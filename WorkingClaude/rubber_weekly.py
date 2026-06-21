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
            OR new 52-week cycle-band high/low (once real history accrued)

Outputs:
  data/rubber_weekly.csv        price series (appendable, deduped by date)
  data/rubber_watch.md          living dated assessment
  data/rubber_alert_state.json  dedupe memory for the alert engine
"""
import os, re, ssl, sys, json, subprocess
from datetime import datetime, timedelta
import urllib.request, urllib.parse
import pandas as pd
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

    # 52-week cycle band — only once we have real (non-seed) history
    band = None
    if len(real) >= 30:
        win = real[real.index >= latest_dt - timedelta(days=365)]["rss3_usdkg"].astype(float)
        if latest >= win.max():   band = "high"
        elif latest <= win.min(): band = "low"
    return dict(latest=latest, latest_dt=latest_dt, wow=wow, wow_ref=wow_ref,
                c4w=c4w, c4w_ref=c4w_ref, c3m=c3m, c3m_ref=c3m_ref, band=band, series=s)


def classify(m):
    """Return (tier, [reasons]). tier in {INFO,WATCH,ALERT}."""
    reasons = []
    wow, c4w, c3m = m["wow"], m["c4w"], m["c3m"]
    if wow is not None and abs(wow) >= ALERT_WOW:
        reasons.append(f"WoW {wow:+.1f}% (>= ±{ALERT_WOW:.0f}%)")
    if c3m is not None and abs(c3m) >= ALERT_3MO:
        reasons.append(f"3 tháng {c3m:+.1f}% (>= ±{ALERT_3MO:.0f}%)")
    if m["band"]:
        reasons.append(f"phá biên 52 tuần ({'đỉnh' if m['band']=='high' else 'đáy'} mới)")
    if reasons:
        return "ALERT", reasons
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


def _save_state(st):
    os.makedirs(DATA, exist_ok=True)
    with open(STATEF, "w") as f: json.dump(st, f, indent=2)


def should_fire(tier, m):
    """Dedupe: fire WATCH/ALERT once per ISO-week, but ALWAYS on escalation."""
    if tier == "INFO":
        return False
    st = _load_state()
    cur_wk = "%d-W%02d" % m["latest_dt"].isocalendar()[:2]
    rank = {"INFO": 0, "WATCH": 1, "ALERT": 2}
    last_tier, last_wk = st.get("last_tier", "INFO"), st.get("last_week", "")
    if rank[tier] > rank.get(last_tier, 0):     # escalation -> always
        return True
    if cur_wk != last_wk:                        # new week -> re-affirm
        return True
    return False                                 # same week, same/lower tier -> mute


def record_fire(tier, m):
    _save_state({"last_tier": tier,
                 "last_week": "%d-W%02d" % m["latest_dt"].isocalendar()[:2],
                 "last_date": str(m["latest_dt"].date())})


def bus(event_type, topic, payload):
    try:
        subprocess.run([APPEND_EVT, "Winston", event_type, topic, json.dumps(payload, ensure_ascii=False)],
                       timeout=30, check=False)
    except Exception as e:
        print(f"  [warn] bus append failed: {e}")


def telegram(text):
    try:
        with open(TG_CONFIG) as f: cfg = json.load(f)
        data = urllib.parse.urlencode({"chat_id": cfg["chat_id"], "text": text,
                                       "parse_mode": "HTML", "disable_web_page_preview": "true"}).encode()
        url = f"https://api.telegram.org/bot{cfg['bot_token']}/sendMessage"
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30).read()
        return True
    except Exception as e:
        print(f"  [warn] telegram send failed: {e}")
        return False


def fire(tier, reasons, m):
    direction = "TĂNG" if (m["wow"] or m["c3m"] or m["c4w"] or 0) > 0 else "GIẢM"
    audience = ["Taylor", "DollarBill"] if tier == "ALERT" else ["Taylor"]
    is_3mo_watch = any("3 tháng" in r for r in reasons)
    if tier == "ALERT":
        action = "Taylor rà mô hình/dự báo nhóm cao su; Bill cân nhắc kế hoạch hành động vị thế"
    elif is_3mo_watch:
        action = ("Taylor CHẠY LẠI mô hình 8L xem có đổi đánh giá nhóm cao su không "
                  "(xu hướng 3 tháng vượt ±18%)")
    else:
        action = "Taylor rà xem input giá đã lệch giả định mô hình chưa (nhóm cao su)"
    payload = {"tier": tier, "direction": direction, "rss3_usdkg": round(m["latest"], 3),
               "date": str(m["latest_dt"].date()), "reasons": reasons, "audience": audience,
               "wow_pct": None if m["wow"] is None else round(m["wow"], 1),
               "cum4wk_pct": None if m["c4w"] is None else round(m["c4w"], 1),
               "cum3mo_pct": None if m["c3m"] is None else round(m["c3m"], 1),
               "stocks": STOCKS, "action": action}
    bus("finding", f"rubber {tier}: cao su {direction} {m['latest']:.2f} USD/kg", payload)

    if tier == "ALERT":
        emoji = "🔴"
        msg = (f"{emoji} <b>CAO SU — {tier} ({direction})</b>\n"
               f"RSS3 <b>{m['latest']:.2f} USD/kg</b> ({m['latest_dt'].date()})\n"
               f"{' · '.join(reasons)}\n"
               f"→ <b>Taylor</b>: rà mô hình/dự báo nhóm cao su\n"
               f"→ <b>Bill</b>: cân nhắc kế hoạch hành động vị thế\n"
               f"CP: {', '.join(STOCKS)}")
        telegram(msg)
        print(f"\n{'='*60}\n🔴 ALERT (gửi Telegram + bus → Taylor & Bill)\n{msg}\n{'='*60}")
    else:
        print(f"\n🟡 WATCH (bus → Taylor): {' · '.join(reasons)}")
    record_fire(tier, m)


# ------------------------------------------------------------------ note --------
def render_note(m, tier, reasons, today):
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
         "",
         "| Tuần (giá đóng) | RSS3 USD/kg |", "|---|---|"]
    for _, r in wk.iterrows():
        L.append(f"| {r['date'].date()} | {r['p']:.2f} |")
    L += ["",
          "## Ngưỡng cảnh báo (đã duyệt)",
          f"- 🟡 **WATCH → Taylor**: |WoW| ≥ {WATCH_WOW:.0f}% hoặc |4 tuần| ≥ {WATCH_4WK:.0f}% — rà mô hình/dự báo nhóm cao su.",
          f"- 🟡 **WATCH 3-tháng → Taylor**: |3 tháng| ≥ {WATCH_3MO:.0f}% (xu hướng trườn) → **chạy lại mô hình 8L** xem có đổi đánh giá nhóm cao su không.",
          f"- 🔴 **ALERT → Bill + Taylor** (+Telegram): |WoW| ≥ {ALERT_WOW:.0f}% hoặc |3 tháng| ≥ {ALERT_3MO:.0f}% hoặc phá biên 52 tuần — Bill quyết kế hoạch vị thế.",
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
    today = str(m["latest_dt"].date())
    render_note(m, tier, reasons, today)
    print(f"RSS3 {m['latest']:.2f} USD/kg  WoW={m['wow'] and round(m['wow'],1)}  "
          f"4wk={m['c4w'] and round(m['c4w'],1)}  3mo={m['c3m'] and round(m['c3m'],1)}  -> {tier}")

    if should_fire(tier, m):
        fire(tier, reasons, m)
    else:
        print(f"  ({tier}: không bắn — đã cảnh báo tuần này hoặc dưới ngưỡng)")
    print(f"-> {CSV} ({len(df)} rows)\n-> {NOTE}")


if __name__ == "__main__":
    main()
