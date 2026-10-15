#!/usr/bin/env python3
"""Khối dashboard toàn cảnh (E–I) cho bản tin 08:00 — `daily_decision_topic.py` import `build_sections()`.

Xác định, không LLM, chỉ ĐỌC. Mỗi khối chạy độc lập: lỗi ⇒ in nguyên lỗi thật (coding_guidelines §29),
không bỏ mục im lặng và không giết cả bản tin. Số nào không đo được ⇒ "n/a + lý do".

  E. Thị trường        — DT5G gate + Value Radar (dna_report), VN-Index từ cache BQ
  F. Hiệu suất TK      — nav_period_returns.py (số chính thức, chain-link theo giá đơn vị quỹ)
  G. 8L mùa BCTC       — snapshot data/rating_8l_daily + ticker_financial (tiến độ công bố Q3)
  H. Mốc đến hạn/paper — kb/paper_programs_registry.json + kb/dashboard_watchlist.json
  I. Research gợi ý    — kb/dashboard_watchlist.json research_backlog + mã funnel vừa công bố Q3

Usage: daily_dashboard.py            # in cả 5 khối (không đăng)
"""
import csv
import glob
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WC = "/home/trido/thanhdt/WorkingClaude"
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ACCOUNTS = ("SpaceX", "ZaloPay")
UPCOMING_DAYS = 21
CLOSED_RE = re.compile(r"^(closed|graduated|review-done)", re.I)


_VN = str.maketrans({",": ".", ".": ","})


def _n(v, spec):
    """Số kiểu VN: 1.719,42 (dấu chấm nghìn, phẩy thập phân)."""
    return format(v, spec).translate(_VN)


def _pct(v):
    return "n/a" if v is None else _n(v, "+.2f") + "%"


def _vnd_m(v):
    return _n(v / 1e6, ",.0f") + "tr"


def _wc_python(code, timeout=150):
    """Chạy `code` dưới môi trường WC (wc_env.sh: BQ creds + đúng interpreter)."""
    cmd = f"cd {WC} && source wc_env.sh >/dev/null 2>&1 && python3 -W ignore -c \"$CODE\""
    r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, "CODE": code})
    if r.returncode != 0:
        raise RuntimeError((r.stderr.strip() or "stderr rỗng")[-300:])
    return r.stdout.strip()


# ------------------------------------------------------------------ E. thị trường
def market_block():
    out = ["**E. Thị trường**"]
    code = ("from dna_report import build_dt_gate_line, build_value_radar_line, build_neutral_base_line\n"
            "for f in (build_dt_gate_line, build_value_radar_line, build_neutral_base_line):\n"
            "    print(f(html=False))")
    try:
        lines = [ln for ln in _wc_python(code).splitlines() if ln.strip() and not ln.lstrip().startswith("↳ ⓘ")]
        out += [f"{ln.strip()}" for ln in lines]
    except Exception as e:
        out.append(f"⚠️ dna_report lỗi: {e}")
    try:
        out.insert(1, _vnindex_line())
    except Exception as e:
        out.insert(1, f"⚠️ VN-Index (cache BQ) lỗi: {e}")
    return "\n".join(out)


def _vnindex_line():
    import pyarrow.dataset as ds
    d = ds.dataset(os.path.join(WC, "data/bq_cache/ticker_1m.parquet"))
    t = d.to_table(columns=["time", "Close", "Trading_Value", "VNINDEX_PE"],
                   filter=ds.field("ticker") == "VNINDEX").to_pandas().sort_values("time").drop_duplicates("time")
    if len(t) < 6:
        return f"VN-Index: n/a — cache chỉ có {len(t)} phiên"
    c = t["Close"].tolist()
    chg1, chg5 = c[-1] / c[-2] - 1, c[-1] / c[-6] - 1
    tv = t["Trading_Value"]
    tv_ratio = tv.iloc[-1] / tv.tail(20).mean()
    last = str(t["time"].iloc[-1])
    line = (f"VN-Index {_n(c[-1], ',.2f')} ({last}): {_pct(chg1 * 100)} 1 phiên · {_pct(chg5 * 100)} 5 phiên · "
            f"P/E {_n(t['VNINDEX_PE'].iloc[-1], '.2f')} · GTGD {_n(tv_ratio, '.2f')}× TB20 phiên")
    try:
        nav_last = _last_nav_date("SpaceX")[0]
        if last < nav_last:
            line += f"\n⚠️ cache BQ ticker_1m cũ hơn NAV ({last} < {nav_last}) — số VN-Index trễ, kiểm sync_bq_cache_daily"
    except Exception:
        pass
    return line


# ------------------------------------------------------------------ F. hiệu suất
def _nav_period(account, report_date, sleeve=None):
    cmd = [sys.executable, os.path.join(WC, "mike", "bin", "nav_period_returns.py"), "--account", account,
           "--report-date", report_date]
    if sleeve:
        cmd += ["--sleeve", sleeve]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=WC)
    if r.returncode != 0:
        raise RuntimeError((r.stderr.strip() or "stderr rỗng")[-300:])
    return json.loads(r.stdout)


def _last_nav_date(account):
    p = os.path.join(WC, "data", "execution_logs", f"nav_history_{account}.csv")
    with open(p, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[-1][next(k for k in rows[0] if k.lower() in ("date", "time", "ngay"))], rows[-1]


def _perf_line(label, d):
    parts = []
    for key, nm in (("day", "ngày"), ("wtd", "tuần"), ("mtd", "tháng"), ("inception", "từ đầu")):
        p = d.get(key) or {}
        parts.append(f"{nm} {_pct(p.get('return_pct'))}")
    inc = d["inception"]
    bm = inc.get("benchmark") or {}
    ex = bm.get("excess_vs_price_pp")
    nav = _vnd_m(inc["nav1"]) if inc.get("nav1") else "n/a"
    s = f"• **{label}** NAV {nav} · " + " · ".join(parts)
    if ex is not None:
        s += f"\n  vs VN-Index giá (từ đầu): {_pct(bm.get('vnindex_price_pct'))} → vượt {_n(ex, '+.2f')}pp"
    if bm.get("status") != "ok" and bm.get("reason"):
        s += f"\n  VN-Index có cổ tức: n/a — {str(bm['reason'])[:110]}"
    return s


def perf_block():
    out = ["**F. Hiệu suất tài khoản** (tỉ suất theo giá đơn vị quỹ; kỳ <12 tháng không quy năm)"]
    for acc in ACCOUNTS:
        try:
            rd, _ = _last_nav_date(acc)
        except Exception as e:
            out.append(f"• **{acc}**: ⚠️ không đọc được nav_history: {e}")
            continue
        try:
            out.append(_perf_line(f"{acc} (đến {rd})", _nav_period(acc, rd)))
            if acc == "ZaloPay":
                try:
                    out.append(_perf_line("ZaloPay — phần bot quản lý", _nav_period(acc, rd, "bot")))
                except Exception as e:
                    out.append(f"• **ZaloPay — phần bot quản lý**: n/a — {str(e)[:170]}")
        except Exception as e:
            out.append(f"• **{acc}**: ⚠️ nav_period_returns lỗi: {e}")
    return "\n".join(out)


# ------------------------------------------------------------------ G. 8L mùa BCTC
def _in_window(d):
    return (d.month in (1, 4, 7, 10) and d.day >= 10) or (d.month in (2, 5, 8, 11) and d.day <= 10)


def _rating_snapshots():
    return sorted(glob.glob(os.path.join(WC, "data/rating_8l_daily/rating_8l_*.csv")))


def _read_ratings(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {r["ticker"]: int(float(r["rating"])) for r in csv.DictReader(f) if r.get("rating")}


def eightl_block(today):
    out = ["**G. Hệ thống 8L — mùa BCTC**"]
    out.append(f"Cửa sổ re-rate hằng ngày (10/10→10/11): {'ĐANG MỞ' if _in_window(today) else 'đóng'}")
    snaps = _rating_snapshots()
    if len(snaps) < 2:
        out.append("⚠️ chưa đủ snapshot rating_8l_daily để so sánh")
        return "\n".join(out)
    cur_p, prev_p = snaps[-1], snaps[-6] if len(snaps) >= 6 else snaps[0]
    cur, prev = _read_ratings(cur_p), _read_ratings(prev_p)
    cur_d = os.path.basename(cur_p)[10:20]
    prev_d = os.path.basename(prev_p)[10:20]
    dist = {k: sum(1 for v in cur.values() if v == k) for k in range(1, 6)}
    out.append(f"Phân bố rating {cur_d} (1=tốt nhất): " + " · ".join(f"{k}:{n}" for k, n in dist.items())
               + f" · tổng {len(cur)} mã")
    common = sorted(set(cur) & set(prev))
    up = [(t, prev[t], cur[t]) for t in common if cur[t] < prev[t]]
    dn = [(t, prev[t], cur[t]) for t in common if cur[t] > prev[t]]
    out.append(f"So với {prev_d} ({len(common)} mã chung; universe đổi {len(prev)}→{len(cur)}): "
               f"nâng hạng {len(up)} · hạ hạng {len(dn)}")
    for nm, lst in (("Nâng", up), ("Hạ", dn)):
        if lst:
            out.append(f"  {nm}: " + ", ".join(f"{t} {a}→{b}" for t, a, b in lst[:12])
                       + (f" … +{len(lst) - 12}" if len(lst) > 12 else ""))
    try:
        rel = _q3_releasers()
        out.append(f"Tiến độ công bố BCTC Q3/2026: {len(rel['tickers'])}/{rel['universe']} mã "
                   f"({_n(100 * len(rel['tickers']) / max(rel['universe'], 1), '.1f')}%), công bố mới nhất {rel['max_known']}")
        out.append("  (hạn công bố quý 3: 30/10; rating mã chưa công bố vẫn là rating quý 2)")
    except Exception as e:
        out.append(f"⚠️ tiến độ công bố Q3 lỗi: {e}")
    return "\n".join(out)


def _q3_releasers():
    code = ("import pandas as pd\n"
            "f=pd.read_parquet('data/bq_cache/ticker_financial.parquet',columns=['ticker','quarter','Release_Date'])\n"
            "q=f[f.quarter=='2026Q3']\n"
            "import json\n"
            "print(json.dumps({'tickers':sorted(set(q.ticker)),'universe':int(f.ticker.nunique()),"
            "'max_known':str(q.Release_Date.max()) if len(q) else 'n/a'}))")
    return json.loads(_wc_python(code))


# ------------------------------------------------------------------ H. mốc đến hạn / paper
def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _iso(s):
    try:
        return date.fromisoformat(s)
    except Exception:
        return None


def due_items(today, registry, watch):
    """[(date, label, source)] — mốc quá hạn hoặc ≤ UPCOMING_DAYS ngày; + dict chương trình event-driven/chờ user."""
    horizon = today + timedelta(days=UPCOMING_DAYS)
    items, event_driven, waiting = [], [], []
    for p in registry.get("programs", []):
        st = str(p.get("status") or "")
        pid = p["id"]
        if "chờ user" in st.lower():
            waiting.append(pid)
        if CLOSED_RE.match(st) or p.get("reporting") is False and not p.get("end") and not p.get("review_date"):
            continue
        dates = [d for d in (_iso(p.get("end") or ""), _iso(p.get("review_date") or "")) if d]
        if not dates:
            event_driven.append(pid)
            continue
        for d in dates:
            if d <= horizon:
                items.append((d, f"paper `{pid}` — {'hết hạn/nghiệm thu' if d == _iso(p.get('end') or '') else 'review'}",
                              "kb/paper_programs_registry.json"))
    covered = {pid for m in watch.get("milestones", []) for pid in m.get("program_ids", [])}
    event_driven = [e for e in event_driven if e not in covered]
    for m in watch.get("milestones", []):
        d = _iso(m["date"])
        if d and d <= horizon:
            items.append((d, m["label"], m.get("source", "")))
    items.sort(key=lambda x: x[0])
    return items, event_driven, waiting


def due_block(today):
    out = ["**H. Mốc đến hạn & paper-trading** (quá hạn + trong 21 ngày tới)"]
    try:
        items, event_driven, waiting = due_items(today, _load_json(os.path.join(ROOT, "kb/paper_programs_registry.json")),
                                                 _load_json(os.path.join(ROOT, "kb/dashboard_watchlist.json")))
    except Exception as e:
        return "\n".join(out + [f"⚠️ đọc registry/watchlist lỗi: {e}"])
    if not items:
        out.append("Không có mốc nào trong 21 ngày tới.")
    for d, label, src in items:
        delta = (d - today).days
        tag = f"🔴 QUÁ HẠN {-delta} ngày" if delta < 0 else ("🟡 hôm nay" if delta == 0 else f"còn {delta} ngày")
        out.append(f"• {d:%d/%m} ({tag}) — {label}")
    if waiting:
        out.append("Chờ user quyết bước kế: " + ", ".join(f"`{w}`" for w in waiting))
    if event_driven:
        out.append("Theo sự kiện (không có ngày): " + ", ".join(f"`{w}`" for w in event_driven))
    out.append("Báo cáo chi tiết paper hằng ngày: `reports/paper_programs_daily_report_<ngày>.md`")
    return "\n".join(out)


# ------------------------------------------------------------------ I. research gợi ý
def research_block(today):
    out = ["**I. Research nên cân nhắc**"]
    try:
        watch = _load_json(os.path.join(ROOT, "kb/dashboard_watchlist.json"))
    except Exception as e:
        return "\n".join(out + [f"⚠️ đọc watchlist lỗi: {e}"])
    try:
        funnel = _load_json(os.path.join(WC, "data/discretionary_funnel_latest.json"))
        watched = {c["ticker"]: c.get("lane") for c in funnel.get("candidates", [])}
        hit = sorted(set(watched) & set(_q3_releasers()["tickers"]))
        if hit:
            out.append("• Mã trong funnel 8L VỪA công bố BCTC Q3 — cần đọc lại số liệu/rating: "
                       + ", ".join(f"{t} (làn {watched[t]})" for t in hit))
        else:
            out.append("• Chưa mã nào trong funnel 8L (%d mã) công bố BCTC Q3." % len(watched))
    except Exception as e:
        out.append(f"⚠️ đối chiếu funnel × Q3 lỗi: {e}")
    for it in sorted(watch.get("research_backlog", []), key=lambda x: x.get("priority", 99)):
        out.append(f"• {it['idea']}  _(nguồn: {it.get('source', 'n/a')})_")
    return "\n".join(out)


def build_sections(now=None):
    now = now or datetime.now(ICT)
    today = now.date()
    return "\n\n".join([market_block(), perf_block(), eightl_block(today), due_block(today), research_block(today)])


if __name__ == "__main__":
    print(build_sections())
