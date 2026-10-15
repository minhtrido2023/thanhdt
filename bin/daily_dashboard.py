#!/usr/bin/env python3
"""Khối dashboard toàn cảnh (E–I) cho bản tin 08:00 — `daily_decision_topic.py` import `build_sections()`.

Xác định, không LLM, chỉ ĐỌC. Mỗi khối chạy độc lập: lỗi ⇒ in nguyên lỗi thật (coding_guidelines §29),
không bỏ mục im lặng và không giết cả bản tin. Số nào không đo được ⇒ "n/a + lý do".

  E. Thị trường        — DT5G gate + Value Radar (dna_report), VN-Index từ cache BQ
  F. Hiệu suất TK      — nav_period_returns.py (số chính thức, chain-link theo giá đơn vị quỹ)
  G. 8L mùa BCTC       — snapshot data/rating_8l_daily + ticker_financial (tiến độ công bố BCTC quý gần nhất, suy từ ngày)
  H. Mốc đến hạn/paper — kb/paper_programs_registry.json + kb/dashboard_watchlist.json
  I. Research gợi ý    — kb/dashboard_watchlist.json research_backlog + mã funnel vừa công bố BCTC

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
RECENT_DAYS = 7
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
    """Chạy `code` dưới môi trường WC (wc_env.sh: BQ creds, TZ, PATH gcloud). Trả (stdout, stderr).
    Lưu ý: `python3` ở đây là interpreter hệ thống (pandas 2.x), KHÔNG phải $DNA_PYEXE — chỉ dùng cho
    đọc parquet/dna_report, không dùng cho phép tính cần pandas 3. stderr trả về cả khi rc=0 vì
    dna_report nuốt lỗi (ghi stderr, trả None) — caller phải hiển thị khi thiếu dữ liệu."""
    cmd = (f"cd {WC} && source wc_env.sh >/dev/null 2>&1 || {{ echo 'source wc_env.sh thất bại' >&2; exit 97; }}; "
           "python3 -W ignore -c \"$CODE\"")
    r = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, "CODE": code})
    if r.returncode != 0:
        raise RuntimeError((r.stderr.strip() or "stderr rỗng")[-300:])
    return r.stdout.strip(), r.stderr.strip()


# ------------------------------------------------------------------ E. thị trường
_DNA_LINES = (("build_dt_gate_line", True), ("build_value_radar_line", True), ("build_neutral_base_line", False))


def market_block():
    out = ["**E. Thị trường**"]
    code = ("import dna_report as d\n"
            + "".join(f"v=d.{n}(html=False)\nprint('##{n}')\nprint('' if v is None else v)\n" for n, _ in _DNA_LINES))
    try:
        stdout, stderr = _wc_python(code)
        got = {}
        for chunk in stdout.split("##")[1:]:
            name, _, body = chunk.partition("\n")
            got[name.strip()] = [ln.strip() for ln in body.splitlines()
                                 if ln.strip() and not ln.lstrip().startswith("↳ ⓘ")]
        for name, required in _DNA_LINES:
            if got.get(name):
                out += got[name]
            elif required:      # None ⇒ dna_report đã nuốt lỗi vào stderr — nói thẳng, không bỏ im lặng
                out.append(f"⚠️ {name}: không có dòng — stderr: {(stderr or 'rỗng')[-200:]}")
            # build_neutral_base_line trả None theo hợp đồng khi state không NEUTRAL ⇒ bỏ dòng, không phải lỗi
    except Exception as e:
        out.append(f"⚠️ dna_report lỗi: {e}")
    try:
        out.insert(1, _vnindex_line())
    except Exception as e:
        out.insert(1, f"⚠️ VN-Index (cache BQ) lỗi: {e}")
    return "\n".join(out)


def _vnindex_line():
    """Đọc cache `ticker/<năm>.parquet` (cùng nguồn preflight; ticker_1m.parquet trễ hơn 1 phiên)."""
    import pyarrow.dataset as ds
    import pandas as pd
    year = datetime.now(ICT).year
    frames = []
    for y in (year - 1, year):
        path = os.path.join(WC, f"data/bq_cache/ticker/{y}.parquet")
        if os.path.exists(path):
            frames.append(ds.dataset(path).to_table(columns=["time", "Close", "Trading_Value"],
                                                    filter=ds.field("ticker") == "VNINDEX").to_pandas())
    t = pd.concat(frames).sort_values("time").drop_duplicates("time")
    if len(t) < 21:
        return f"VN-Index: n/a — cache chỉ có {len(t)} phiên"
    c = t["Close"].tolist()
    tv_ratio = t["Trading_Value"].iloc[-1] / t["Trading_Value"].tail(20).mean()
    last = str(t["time"].iloc[-1])
    line = (f"VN-Index {_n(c[-1], ',.2f')} ({last}): {_pct((c[-1] / c[-2] - 1) * 100)} 1 phiên · "
            f"{_pct((c[-1] / c[-6] - 1) * 100)} 5 phiên · {_pct((c[-1] / c[-21] - 1) * 100)} 20 phiên · "
            f"GTGD {_n(tv_ratio, '.2f')}× TB20 phiên")
    try:
        nav_last = _last_nav_date("SpaceX")[0]
        if last < nav_last:
            line += f"\n⚠️ cache BQ ticker cũ hơn NAV ({last} < {nav_last}) — số VN-Index trễ, kiểm sync_bq_cache_daily"
    except Exception as e:
        line += f"\n⚠️ không so được độ tươi cache với NAV: {e}"
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
    """Cửa sổ re-rate hằng ngày — CHÉP từ bin/fa_ratings_earnings_window_daily.sh (nguồn thật của gate)."""
    return (d.month in (1, 4, 7, 10) and d.day >= 10) or (d.month in (2, 5, 8, 11) and d.day <= 10)


def season(today):
    """Quý báo cáo gần nhất đã kết thúc + cửa sổ re-rate của nó. Suy từ `today`, không hardcode quý."""
    q = (today.month - 1) // 3
    year, qn = (today.year - 1, 4) if q == 0 else (today.year, q)
    first_m = qn * 3 + 1                                    # tháng đầu của quý kế tiếp
    wy, wm = (year + 1, 1) if qn == 4 else (year, first_m)
    start = date(wy, wm, 10)
    end = date(wy, wm + 1, 10)
    pq = (year - 1, 4) if qn == 1 else (year, qn - 1)
    return {"q": f"{year}Q{qn}", "label": f"Q{qn}/{year}", "prev_q": f"{pq[0]}Q{pq[1]}", "start": start, "end": end}


def _rating_snapshots():
    return sorted(glob.glob(os.path.join(WC, "data/rating_8l_daily/rating_8l_*.csv")))


def _read_ratings(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {r["ticker"]: int(float(r["rating"])) for r in csv.DictReader(f) if r.get("rating")}


def eightl_block(today):
    se = season(today)
    out = ["**G. Hệ thống 8L — mùa BCTC**"]
    state = "ĐANG MỞ" if se["start"] <= today <= se["end"] else ("chưa mở" if today < se["start"] else "đã đóng")
    out.append(f"Cửa sổ re-rate hằng ngày cho {se['label']} ({se['start']:%d/%m}→{se['end']:%d/%m}): {state}")
    snaps = _rating_snapshots()
    if len(snaps) < 2:
        out.append("⚠️ chưa đủ snapshot rating_8l_daily để so sánh")
    else:
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
        rel = _releasers(se)
        n, den = len(rel["released"]), rel["universe"]
        out.append(f"Tiến độ công bố BCTC {se['label']}: {n}/{den} mã đã công bố quý trước "
                   f"({_n(100 * n / max(den, 1), '.1f')}%), công bố mới nhất {rel['max_known']}")
        out.append(f"  (mã chưa công bố {se['label']} vẫn chấm 8L theo số liệu quý trước)")
    except Exception as e:
        out.append(f"⚠️ tiến độ công bố {se['label']} lỗi: {e}")
    return "\n".join(out)


def _releasers(se):
    """{'released': {ticker: Release_Date}, 'universe': #mã đã công bố quý trước, 'max_known': ngày}."""
    code = ("import pandas as pd, json\n"
            "f=pd.read_parquet('data/bq_cache/ticker_financial.parquet',columns=['ticker','quarter','Release_Date'])\n"
            f"q=f[f.quarter=={se['q']!r}]\n"
            f"p=f[f.quarter=={se['prev_q']!r}]\n"
            "print(json.dumps({'released':{r.ticker:str(r.Release_Date) for r in q.itertuples()},"
            "'universe':int(p.ticker.nunique()),'max_known':str(q.Release_Date.max()) if len(q) else 'n/a'}))")
    return json.loads(_wc_python(code)[0])


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
        se = season(today)
        funnel = _load_json(os.path.join(WC, "data/discretionary_funnel_latest.json"))
        watched = {c["ticker"]: c.get("lane") for c in funnel.get("candidates", [])}
        rel = _releasers(se)["released"]
        cutoff = str(today - timedelta(days=RECENT_DAYS))
        hit = sorted(t for t in watched if t in rel and rel[t] >= cutoff)
        older = sum(1 for t in watched if t in rel and rel[t] < cutoff)
        if hit:
            out.append(f"• Mã trong funnel 8L công bố BCTC {se['label']} trong {RECENT_DAYS} ngày qua — cần đọc lại số liệu/rating: "
                       + ", ".join(f"{t} (làn {watched[t]})" for t in hit))
        else:
            out.append(f"• Không mã nào trong funnel 8L ({len(watched)} mã) công bố BCTC {se['label']} trong {RECENT_DAYS} ngày qua"
                       + (f" ({older} mã đã công bố trước đó)." if older else "."))
    except Exception as e:
        out.append(f"⚠️ đối chiếu funnel × BCTC lỗi: {e}")
    for it in sorted(watch.get("research_backlog", []), key=lambda x: x.get("priority", 99)):
        out.append(f"• {it.get('idea', '⚠️ mục backlog thiếu `idea`: ' + str(it.get('id')))}  _(nguồn: {it.get('source', 'n/a')})_")
    return "\n".join(out)


def _safe(name, fn, *args):
    try:
        return fn(*args)
    except Exception as e:      # §29: in lỗi thật, các khối khác vẫn đi
        return f"**{name}**: ⚠️ khối lỗi {type(e).__name__}: {e}"


def build_sections(now=None):
    now = now or datetime.now(ICT)
    today = now.date()
    return "\n\n".join([
        _safe("E. Thị trường", market_block),
        _safe("F. Hiệu suất tài khoản", perf_block),
        _safe("G. 8L mùa BCTC", eightl_block, today),
        _safe("H. Mốc đến hạn", due_block, today),
        _safe("I. Research", research_block, today)])


if __name__ == "__main__":
    print(build_sections())
