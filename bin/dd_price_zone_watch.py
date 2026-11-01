#!/usr/bin/env python3
"""dd_price_zone_watch.py — mỗi tối: mã DD đang ở đâu so với vùng giá hợp lý trong sổ DD.

User yêu cầu 2026-11-01 22:39 ICT: "Mã nào cuối ngày nằm dưới vùng của mức giá hợp lý 15% thì note vào
trong quá trình tạo plan buổi tối mỗi ngày để tôi biết có nên đưa vào plan không".

CHỈ GHI CHÚ — KHÔNG đặt lệnh, KHÔNG ghi plan, KHÔNG gọi bot/Notifier. DNSE chỉ-đọc qua
`intraday_price_watch.LiveMarket` (ReadOnlyDNSE: ohlc 1D + positions). Giá cùng ngày KHÔNG lấy từ BQ
(BQ sync 23:45 ICT); BQ chỉ dùng để phát hiện BCTC quý mới hơn DD (dữ liệu lịch sử, trễ ≤1 ngày).

Sổ: `kb/dd_price_zones.json` (append-only; bản dd_date mới nhất của mã thắng; selfcheck số↔nguồn:
`bin/dd_price_zones_selfcheck.py`).

Ngưỡng (MỘT hằng số THRESHOLD_PCT, đổi ở đầu file): VÀO cảnh báo khi giá ≤ tâm × (1 − 15%);
hysteresis: đang bật thì chỉ TẮT khi giá hồi lên > tâm × (1 − 10%). Trạng thái lưu theo (mã, dd_date):
DD mới ⇒ trạng thái trễ làm lại từ đầu.

Dùng:
  dd_price_zone_watch.py run [--asof YYYY-MM-DD] [--report-block] [--no-bq] [--no-positions]
                             [--price-csv F] [--no-state] [--out-dir D]
  --report-block : in khối ngắn cho báo cáo plan (stdout), bảng đầy đủ ghi file <out-dir>/<asof>.md
  --price-csv    : nguồn giá thay DNSE (ticker,date,close[,adv20_vnd]) — chỉ cho ngày quá khứ/khẩn cấp,
                   nguồn được ghi rõ trong khối.
rc: 0 = OK (kể cả có mã lỗi giá — ghi trong khối) · 1 = lỗi đọc sổ/không dựng được khối.
"""
import argparse
import csv
import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
MIKE = os.path.dirname(HERE)
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
sys.path.insert(0, HERE)

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
THRESHOLD_PCT = 15          # VÀO cảnh báo: giá ≤ tâm × (1 − 15%)  — hằng số DUY NHẤT của ngưỡng
RELEASE_PCT = 10            # hysteresis: chỉ TẮT khi giá > tâm × (1 − 10%)
CLOSE_READY = dt.time(15, 5)  # trước giờ này bar 1D của hôm nay chưa phải giá đóng cửa
LEDGER = os.path.join(MIKE, "kb", "dd_price_zones.json")
STATE = os.environ.get("DDZ_STATE") or os.path.join(WC, "data", "dd_price_zone_watch_state.json")
OUT_DIR = os.path.join(WC, "data", "dd_price_zone")
NOTE = "GHI CHÚ ĐỂ ANH CÂN NHẮC, không phải tín hiệu mua; không tự đưa vào plan."
ST_IN, ST_BELOW, ST_ABOVE = "TRONG vùng", "DƯỚI vùng", "TRÊN vùng"
ST_ALERT = f"DƯỚI TÂM ≥{THRESHOLD_PCT}% (NGƯỠNG CẢNH BÁO)"


# ------------------------------------------------------------------ logic thuần (selfcheck)
def latest_entries(ledger):
    """{ticker: entry} — bản dd_date mới nhất thắng; cùng ngày thì entry ghi sau thắng (append-only)."""
    out = {}
    for e in ledger["entries"]:
        t = e["ticker"].upper()
        if t not in out or e["dd_date"] >= out[t]["dd_date"]:
            out[t] = e
    return out


def _q_key(q):
    """'2026Q3' → (2026, 3); hỏng ⇒ None."""
    try:
        y, n = str(q).upper().split("Q")
        return int(y), int(n)
    except (ValueError, AttributeError):
        return None


def expiry_of(entry, asof, newer_releases):
    """→ (expired: bool, lý do). newer_releases = {ticker: [(quarter, release_date)]} đọc PIT;
    None = không kiểm được ⇒ chỉ dùng expires_on lưu trong sổ."""
    t = entry["ticker"].upper()
    base = _q_key(entry.get("bctc_quarter"))
    if newer_releases is not None and base is not None:
        for q, rd in newer_releases.get(t, []):
            k = _q_key(q)
            if k is not None and k > base and rd is not None and rd <= asof:
                return True, f"BCTC {q} đã công bố {rd:%d/%m/%Y} (mới hơn DD {entry['bctc_quarter']}) ⇒ cần DD lại"
    exp = dt.date.fromisoformat(entry["expires_on"])
    if asof >= exp:
        return True, f"quá hạn DD ({exp:%d/%m/%Y}) ⇒ cần DD lại"
    return False, ""


def classify(price, entry, prev_alert, thr=THRESHOLD_PCT, rel=RELEASE_PCT):
    """→ dict(zone_status, alert, new_alert, pct_center, pct_low). So sánh bằng số nguyên (×100)
    để biên −15,0% đúng tuyệt đối, không lệch vì float."""
    low, c, high = entry.get("zone_low"), entry.get("center"), entry.get("zone_high")
    p = int(round(price))
    if low is not None and p < low:
        zs = ST_BELOW
    elif high is not None and p > high:
        zs = ST_ABOVE
    elif low is not None and high is not None:
        zs = ST_IN
    else:
        zs = "— (sổ không có vùng)"
    alert = False
    if c is not None:
        if prev_alert:
            alert = p * 100 <= c * (100 - rel)          # giữ tới khi hồi > −10%
        else:
            alert = p * 100 <= c * (100 - thr)          # vào ở ≤ −15%
    return {"zone_status": zs, "alert": alert, "new_alert": alert and not prev_alert,
            "hold_band": alert and prev_alert and p * 100 > c * (100 - thr),
            "pct_center": (p / c - 1) * 100 if c else None,
            "pct_low": (p / low - 1) * 100 if low else None}


def prev_state(state, ticker, dd_date, asof):
    """Trạng thái cảnh báo của PHIÊN TRƯỚC asof (cùng dd_date). Không có ⇒ False."""
    days = sorted(d for d in (state.get("days") or {}) if d < asof.isoformat())
    for d in reversed(days):
        rec = state["days"][d].get(ticker)
        if rec is not None:
            return bool(rec.get("alert")) if rec.get("dd_date") == dd_date else False
    return False


def evaluate(ledger, asof, prices, flags, newer_releases, state, thr=THRESHOLD_PCT, rel=RELEASE_PCT):
    """prices = {ticker: {"close":, "adv20":, "err":}} ; flags = {ticker: [cờ]}.
    → (rows, expired, new_state_for_day)."""
    rows, expired, day = [], [], {}
    for t, e in sorted(latest_entries(ledger).items()):
        is_exp, why = expiry_of(e, asof, newer_releases)
        if is_exp:
            expired.append({"ticker": t, "dd_date": e["dd_date"], "why": why, "flags": flags.get(t, [])})
            continue
        pr = prices.get(t) or {}
        row = {"ticker": t, "entry": e, "close": pr.get("close"), "adv20": pr.get("adv20"),
               "err": pr.get("err"), "flags": flags.get(t, [])}
        if pr.get("close") is not None:
            pa = prev_state(state, t, e["dd_date"], asof)
            row.update(classify(pr["close"], e, pa, thr, rel))
            row["prev_alert"] = pa
            day[t] = {"dd_date": e["dd_date"], "alert": row["alert"], "close": int(round(pr["close"]))}
        rows.append(row)
    return rows, expired, day


def _f(x):
    return "—" if x is None else f"{x:,.0f}".replace(",", ".")


def _pct(x):
    return "—" if x is None else f"{x:+.1f}%".replace(".", ",")


def _adv(x):
    return "—" if x is None else f"{x / 1e9:.2f}".replace(".", ",")


def _label(r):
    if r.get("err"):
        return f"KHÔNG CÓ GIÁ ({r['err']})"
    if r.get("alert"):
        s = ST_ALERT + (" 🆕 VỪA VÀO" if r.get("new_alert") else "")
        return s + (" (giữ do trễ: chưa hồi > −10%)" if r.get("hold_band") else "")
    return r["zone_status"]


def render_table(rows, expired, asof, src):
    L = [f"# Mã DD so với vùng giá hợp lý — đóng cửa {asof:%d/%m/%Y}", "",
         f"> {NOTE}", f"> Giá: {src}. Ngưỡng: ≤ tâm×(1−{THRESHOLD_PCT}%) bật, tắt khi > tâm×(1−{RELEASE_PCT}%).", "",
         "| Mã | DD | Giá | Vùng | Tâm | % so tâm | % so đáy | Mức −15% tâm | Trạng thái | ADV20 (tỷ) | Cờ |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        e = r["entry"]
        lvl = int(e["center"] * (100 - THRESHOLD_PCT) / 100) if e.get("center") else None
        z = f"{_f(e.get('zone_low'))}–{_f(e.get('zone_high'))}" if e.get("zone_low") else "—"
        L.append(f"| {r['ticker']} | {e['dd_date']} | {_f(r.get('close'))} | {z} | {_f(e.get('center'))} | "
                 f"{_pct(r.get('pct_center'))} | {_pct(r.get('pct_low'))} | {_f(lvl)} | {_label(r)} | "
                 f"{_adv(r.get('adv20'))} | "
                 f"{', '.join(r['flags']) or ''} |")
    if expired:
        L += ["", "**DD hết hạn — cần DD lại (KHÔNG báo như mức giá hiện hành):**"]
        L += [f"- {x['ticker']} (DD {x['dd_date']}): {x['why']}" for x in expired]
    return "\n".join(L) + "\n"


def render_block(rows, expired, asof, src, table_path):
    """Khối NGẮN cho báo cáo plan / Discord."""
    L = [f"📌 **Mã DD dưới vùng giá hợp lý** (đóng cửa {asof:%d/%m}, {src}) — {NOTE}"]
    al = [r for r in rows if r.get("alert")]
    below = [r for r in rows if not r.get("alert") and r.get("zone_status") == ST_BELOW]

    def line(r):
        e = r["entry"]
        fl = f" · {', '.join(r['flags'])}" if r["flags"] else ""
        adv = "" if r.get("adv20") is None else f" · ADV20 {r['adv20'] / 1e9:.1f} tỷ".replace(".", ",")
        return (f"  • {r['ticker']} {_f(r['close'])} — {_label(r)}; tâm {_f(e.get('center'))} ({_pct(r.get('pct_center'))})"
                f", vùng {_f(e.get('zone_low'))}–{_f(e.get('zone_high'))} ({_pct(r.get('pct_low'))} so đáy)"
                f"{adv}{fl} · DD {e['dd_date']}")
    if al:
        L.append(f"  Dưới tâm ≥{THRESHOLD_PCT}%:")
        L += [line(r) for r in sorted(al, key=lambda r: (not r.get("new_alert"), r["pct_center"]))]
    else:
        L.append(f"  Không mã nào dưới tâm ≥{THRESHOLD_PCT}%.")
    if below:
        L.append("  Dưới đáy vùng (chưa tới ngưỡng):")
        L += [line(r) for r in below]
    rest = [r for r in rows if r not in al and r not in below]
    n_in = sum(r.get("zone_status") == ST_IN for r in rest)
    n_up = sum(r.get("zone_status") == ST_ABOVE for r in rest)
    n_nz = [r["ticker"] for r in rest if r.get("close") is not None and r.get("zone_status", "").startswith("—")]
    n_err = [r["ticker"] for r in rest if r.get("err")]
    tail = f"  Còn lại: {n_in} trong vùng, {n_up} trên vùng"
    if n_nz:
        tail += f", {len(n_nz)} sổ không có vùng ({', '.join(n_nz)})"
    if n_err:
        tail += f"; ⚠️ không lấy được giá: {', '.join(n_err)}"
    L.append(tail + ".")
    if expired:
        L.append("  Cần DD lại (BCTC mới hơn/quá hạn): " + ", ".join(x["ticker"] for x in expired) + ".")
    L.append(f"  Bảng đầy đủ: {table_path}")
    return "\n".join(L)


# ------------------------------------------------------------------ I/O
def _read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def dnse_prices(tickers, asof, market):
    """{t: {close, adv20, err}} — close = bar 1D có NGÀY == asof (không lấy phiên khác thay thế)."""
    out = {}
    a = int(dt.datetime.combine(asof - dt.timedelta(days=45), dt.time(0), _ICT).timestamp())
    b = int(dt.datetime.combine(asof + dt.timedelta(days=1), dt.time(0), _ICT).timestamp())
    for t in tickers:
        try:
            r = market.ro.ohlc(t, resolution="1D", **{"from": a, "to": b})
            bars = [(dt.datetime.fromtimestamp(x, _ICT).date(), r["c"][i] * 1000, r["v"][i])
                    for i, x in enumerate(r.get("t", []))]
            out[t] = bars_to_price(bars, asof)
        except Exception as e:  # noqa: BLE001 — một mã lỗi không làm hỏng cả khối
            out[t] = {"close": None, "adv20": None, "err": f"DNSE {type(e).__name__}"}
    return out


def bars_to_price(bars, asof):
    bars = sorted(b for b in bars if b[0] <= asof)
    if not bars or bars[-1][0] != asof:
        last = f"; bar cuối {bars[-1][0]:%d/%m}" if bars else ""
        return {"close": None, "adv20": None, "err": f"không có bar đóng cửa {asof:%d/%m}{last}"}
    win = bars[-20:]
    adv = sum(c * v for _, c, v in win) / len(win) if len(win) >= 10 else None
    return {"close": float(bars[-1][1]), "adv20": adv, "err": None}


def csv_prices(path, tickers, asof):
    out = {t: {"close": None, "adv20": None, "err": f"CSV không có dòng {asof:%d/%m}"} for t in tickers}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = r["ticker"].upper()
            if t in out and r["date"] == asof.isoformat():
                adv = r.get("adv20_vnd")
                out[t] = {"close": float(r["close"]), "adv20": float(adv) if adv not in (None, "") else None, "err": None}
    return out


def bq_newer_releases(tickers, quarters):
    """{t: [(quarter, release_date)]} cho quý > quý DD. Lỗi ⇒ None (không suy 'chưa có BCTC mới')."""
    lo = min(quarters)
    tl = ",".join(f"'{t}'" for t in tickers)
    sql = ("SELECT ticker, quarter, CAST(Release_Date AS STRING) rd FROM tav2_bq.ticker_financial AS f "
           f"WHERE ticker IN ({tl}) AND quarter > '{lo}' AND Release_Date IS NOT NULL")
    cmd = (f". {WC}/wc_env.sh && bq query --use_legacy_sql=false --format=json --max_rows=10000 "
           f"--project_id=lithe-record-440915-m9 \"{sql}\"")
    try:
        p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=40)
        rows = json.loads(p.stdout)
        out = {}
        for r in rows:
            out.setdefault(r["ticker"].upper(), []).append((r["quarter"], dt.date.fromisoformat(r["rd"][:10])))
        return out
    except Exception as e:  # noqa: BLE001
        print(f"[ddz] ⚠ BQ BCTC mới: {type(e).__name__}: {e} — chỉ dùng expires_on trong sổ", file=sys.stderr)
        return None


def static_flags(tickers, asof):
    """BANNED + forensic exclude (ngày cờ ≤ asof). Lỗi đọc ⇒ cờ '⚠️ không kiểm được …', không bỏ qua câm."""
    fl = {t: [] for t in tickers}
    try:
        from lag_forensic_filter import BANNED, _load_forensic_excludes
        for t in tickers:
            if t in BANNED:
                fl[t].append("BANNED")
        fx = _load_forensic_excludes(os.path.join(WC, "data", "forensic_flags.csv"))
        for t, d in fx.items():
            if t in fl and d.date() <= asof:
                fl[t].append(f"forensic exclude ({d.date():%d/%m/%Y})")
    except Exception as e:  # noqa: BLE001
        for t in tickers:
            fl[t].append(f"⚠️ không kiểm được BANNED/forensic ({type(e).__name__})")
    return fl


def account_flags(tickers, market, fl):
    """Đang giữ (DNSE positions, chỉ-đọc, lọc account §12 trong LiveMarket.positions) + excluded_tickers."""
    from intraday_price_watch import load_accounts
    for a in load_accounts():
        for t in tickers:
            if t in a["excluded"]:
                fl[t].append(f"excluded_tickers {a['label']}")
        try:
            pos = market.positions(a["account_id"])
            for t in tickers:
                if (pos.get(t) or {}).get("qty"):
                    fl[t].append(f"đang giữ {a['label']} {pos[t]['qty']:,}".replace(",", "."))
        except Exception as e:  # noqa: BLE001
            for t in tickers:
                fl[t].append(f"⚠️ không đọc được vị thế {a['label']} ({type(e).__name__})")
    return fl


def run(args, now=None):
    now = now or dt.datetime.now(_ICT)
    asof = dt.date.fromisoformat(args.asof) if args.asof else now.date()
    ledger = json.load(open(args.ledger, encoding="utf-8"))
    ents = latest_entries(ledger)
    tickers = sorted(ents)
    market = None
    if args.price_csv:
        prices, src = csv_prices(args.price_csv, tickers, asof), f"CSV {os.path.basename(args.price_csv)}"
    elif asof == now.date() and now.time() < CLOSE_READY:
        prices = {t: {"close": None, "adv20": None, "err": "chưa đóng cửa"} for t in tickers}
        src = "DNSE — chưa đóng cửa, chưa có giá"
    else:
        from intraday_price_watch import LiveMarket
        market = LiveMarket()
        prices, src = dnse_prices(tickers, asof, market), "DNSE ohlc 1D"
    flags = static_flags(tickers, asof)
    if not args.no_positions:
        try:
            if market is None:
                from intraday_price_watch import LiveMarket
                market = LiveMarket()
            account_flags(tickers, market, flags)
        except Exception as e:  # noqa: BLE001
            for t in tickers:
                flags[t].append(f"⚠️ không kiểm được vị thế/excluded ({type(e).__name__})")
    newer = None if args.no_bq else bq_newer_releases(tickers, [e["bctc_quarter"] for e in ents.values()])
    state = _read_json(args.state, {}) if not args.no_state else {}
    rows, expired, day = evaluate(ledger, asof, prices, flags, newer, state)
    if newer is None and not args.no_bq:
        src += "; ⚠️ chưa kiểm được BCTC mới (BQ lỗi) — hạn DD theo sổ"
    os.makedirs(args.out_dir, exist_ok=True)
    tpath = os.path.join(args.out_dir, f"{asof.isoformat()}.md")
    _atomic_write(tpath, render_table(rows, expired, asof, src))
    if not args.no_state and day:
        state.setdefault("days", {})[asof.isoformat()] = day
        for d in sorted(state["days"])[:-60]:          # giữ 60 phiên gần nhất
            del state["days"][d]
        _atomic_write(args.state, json.dumps(state, ensure_ascii=False, indent=1))
    print(render_block(rows, expired, asof, src, tpath) if args.report_block else open(tpath, encoding="utf-8").read())
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("run")
    rp.add_argument("--asof")
    rp.add_argument("--ledger", default=LEDGER)
    rp.add_argument("--state", default=STATE)
    rp.add_argument("--out-dir", default=OUT_DIR)
    rp.add_argument("--price-csv")
    rp.add_argument("--report-block", action="store_true")
    rp.add_argument("--no-bq", action="store_true")
    rp.add_argument("--no-positions", action="store_true")
    rp.add_argument("--no-state", action="store_true")
    a = ap.parse_args(argv)
    try:
        return run(a)
    except Exception as e:  # noqa: BLE001 — caller (send_plan_report) in 1 dòng cảnh báo, không chặn plan
        print(f"[ddz] LỖI: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
