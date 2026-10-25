#!/usr/bin/env python3
"""Livermore REPORT_BLOCK — khối "Kỹ thuật (VN-Index ...)" của báo cáo weekly/monthly do Livermore viết.

User duyệt 2026-10-25 (job Taylor_20261025_092234). Thiết kế: agents/Taylor/research/livermore_report_block_20261025/.

Luồng `ensure --kind weekly|monthly --period-end D`:
  1. as_of = phiên cuối ≤ period_end; kỳ phải đã đóng (as_of ≤ expected_last_session) và có bar đúng as_of.
  2. SCRIPT tính mọi con số (FACTS) từ VNINDEX OHLCV + cột chỉ báo BQ (MA đối chiếu chéo với SMA tự tính)
     + độ rộng point-in-time (universe_pit). Livermore KHÔNG tự sinh số.
  3. Dự báo: lần đọc có forecast gần nhất (MỌI loại trigger, as_of ≤ as_of kỳ — mù về sau) cách < 20 phiên
     ⇒ chỉ NHẮC LẠI nguyên văn từ sổ; ≥ 20 phiên (hoặc chưa có) ⇒ gọi livermore_run.sh (ghi sổ như thường).
  4. Gọi agent livermore ĐỌC MÙ (chỉ FACTS, không DT5G) viết 5 gạch đầu dòng.
  5. Kiểm cơ học: đúng khung nhãn · mọi số/ngày ⊆ FACTS · không lộ DT5G/tên nội bộ. Lệch ⇒ FAIL (fail-closed):
     không có file .md PASS, agent soạn báo cáo dùng khối tự viết + cờ cảnh báo.
  6. Ghi data/livermore/report_block_<as_of>_<kind>.md rồi .json (json = dấu commit, có sha256 của .md).

Hook kiểm thử: LIVERMORE_CLAUDE_BIN, LIVERMORE_BARS_CSV, LIVERMORE_IND_CSV, LIVERMORE_BREADTH_CSV,
LIVERMORE_REGISTRY, LIVERMORE_DATA_DIR, LIVERMORE_STATE_DIR, LIVERMORE_RUN_BIN, LIVERMORE_NOW (+LIVERMORE_TEST=1).
rc: 0 PASS · 1 FAIL (đã ghi .FAILED.json kèm lý do) · 2 usage.
"""
import argparse
import calendar
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from decimal import Decimal, InvalidOperation

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import livermore_common as C  # noqa: E402

LATE_MAX = 5                 # phiên: báo cáo soạn trễ hơn mức này không được lập forecast mới (không còn là đọc sống)
MIN_GAP = C.HORIZON          # phiên giữa 2 lần đọc CÓ forecast (chân chấm điểm 20 phiên không chồng)
LABELS = ("Xu hướng", "Hỗ trợ/kháng cự", "Động lượng", "Thanh khoản", "Độ rộng")
MA_TOL = 0.001               # cột MA của BQ vs SMA tự tính từ bar: lệch > 0,1% ⇒ dữ liệu không nhất quán ⇒ FAIL
# Lộ thông tin bị cấm (Livermore mù DT5G) hoặc tên hệ thống nội bộ trong văn bản client-facing.
DENY = re.compile(r"DT5G|DT4|DT gate|5[- ]?state|vnindex_5state|EX-?BULL|CRISIS|Khủng hoảng|mô hình trạng thái|"
                  r"tav2|BigQuery|universe_pit|ticker_prune|DNSE|Livermore|nên mua|nên bán|khuyến nghị mua|"
                  r"khuyến nghị bán|chắc chắn", re.I)
RUN_BIN = os.environ.get("LIVERMORE_RUN_BIN") or os.path.join(C.ROOT, "bin", "livermore_run.sh")


class BlockError(RuntimeError):
    pass


# ───────────────────────── định dạng số kiểu VN ─────────────────────────
def vn(x, nd=2, sign=False):
    s = f"{abs(x):,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    if sign:
        return ("+" if x >= 0 else "−") + s
    return ("−" + s) if x < 0 else s


def dmy(d):
    return d.strftime("%d/%m/%Y")


# CHỈ đúng các định danh xuất hiện trong nhãn SỐ LIỆU (arch-review r1: regex rộng cho 'EMA 1800'/'RSI(70)' đi lậu ngưỡng).
_ID = re.compile(r"\bMA(?:20|50|200)\b|\bRSI\(14\)")
_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b")
_NUM = re.compile(r"(?:(?<=[\s(:;])|^)([+\u2212-])?(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)|(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)", re.M)


def tokens(text):
    """→ (tập ngày (dd,mm,yyyy|None), tập số). Định danh MA20/MA50/MA200/RSI(14) bị bỏ ở CẢ hai phía để '20'/'14'
    không thành số hợp lệ đi lậu. Số có dấu (+/−/- đứng sau khoảng trắng/đầu dòng) mang dấu: '+4' ≠ '-4'; số
    không dấu là độ lớn ('abs:4'). validate(): số có dấu trong khối phải khớp CẢ dấu; số không dấu khớp độ lớn."""
    t = _ID.sub(" ", text)
    dates = set()
    for m in _DATE.finditer(t):
        dates.add((int(m.group(1)), int(m.group(2)), int(m.group(3)) if m.group(3) else None))
    t = _DATE.sub(" ", t)
    nums = set()
    for m in _NUM.finditer(t):
        sign, raw = (m.group(1), m.group(2)) if m.group(2) else (None, m.group(3))
        try:
            v = format(Decimal(raw.replace(".", "").replace(",", ".")).normalize(), "f")
        except InvalidOperation:
            v = raw
        nums.add(f"abs:{v}")
        if sign:
            nums.add(("-" if sign in "\u2212-" else "+") + v)
    return dates, nums


# ───────────────────────── kỳ & lịch ─────────────────────────
def last_session_le(d):
    while not C.is_session(d):
        d -= dt.timedelta(days=1)
    return d


def period_bounds(kind, period_end):
    """→ (as_of, prev_as_of, period_start, prev_period_start). weekly: kỳ = 7 ngày lịch kết thúc period_end. monthly: tháng của period_end."""
    if kind == "weekly":
        start = period_end - dt.timedelta(days=6)
        prev_end = period_end - dt.timedelta(days=7)
        prev_start = start - dt.timedelta(days=7)
    else:
        last = calendar.monthrange(period_end.year, period_end.month)[1]
        if period_end.day != last:
            raise BlockError(f"monthly: period_end {period_end} không phải ngày cuối tháng ({last})")
        start = period_end.replace(day=1)
        prev_end = start - dt.timedelta(days=1)
        prev_start = prev_end.replace(day=1)
    return last_session_le(period_end), last_session_le(prev_end), start, prev_start


def sessions_between(a, b):
    """Số phiên từ a (loại) đến b (gồm); a ≤ b."""
    n, d = 0, a
    while d < b:
        d = C.next_session(d)
        n += 1
    return n


# ───────────────────────── dữ liệu ─────────────────────────
def _csv_rows(path):
    import csv
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def get_indicators(start, end):
    """Cột chỉ báo VNINDEX đã tính sẵn trong bảng ticker: MA20/50/200, D_RSI (0-1), D_MACDdiff, D_CMF."""
    p = os.environ.get("LIVERMORE_IND_CSV")
    rows = _csv_rows(p) if p else C.bq_rows(
        "SELECT t.time, t.MA20, t.MA50, t.MA200, t.D_RSI, t.D_MACDdiff, t.D_CMF FROM tav2_bq.ticker AS t "
        f"WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{start}' AND DATE '{end}' ORDER BY t.time")
    out = {}
    for r in rows:
        d = dt.date.fromisoformat(r["time"][:10])
        if start <= d <= end:
            out[d] = {k: float(r[k]) for k in ("MA20", "MA50", "MA200", "D_RSI", "D_MACDdiff", "D_CMF")}
    return out


def get_breadth(start, end):
    """% mã point-in-time đóng cửa > MA50 mỗi phiên (universe_pit, KHÔNG ticker_prune — §9b). {} nếu lỗi."""
    p = os.environ.get("LIVERMORE_BREADTH_CSV")
    rows = _csv_rows(p) if p else C.bq_rows(
        "SELECT t.time, 100*AVG(IF(t.Close > t.MA50, 1.0, 0.0)) AS pct, COUNT(*) AS n FROM tav2_bq.ticker AS t "
        "JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` AS u ON u.ticker = t.ticker AND u.time = t.time "
        f"AND u.in_universe WHERE t.MA50 IS NOT NULL AND t.time BETWEEN DATE '{start}' AND DATE '{end}' "
        "GROUP BY t.time ORDER BY t.time")
    out = {}
    for r in rows:
        d = dt.date.fromisoformat(r["time"][:10])
        if start <= d <= end:
            out[d] = (float(r["pct"]), int(float(r["n"])))
    return out


def build_facts(kind, period_end):
    as_of, prev, start, prev_start = period_bounds(kind, period_end)
    exp = C.expected_last_session()
    if as_of > exp:
        raise BlockError(f"kỳ chưa đóng: as_of {as_of} > phiên đã có dữ liệu kỳ vọng {exp}")
    bars = C.get_bars(as_of - dt.timedelta(days=C.PKG_BARS * 2), as_of)
    bars = [b for b in bars if b["time"] <= as_of]
    if not bars or bars[-1]["time"] != as_of:
        raise BlockError(f"as-of lệch: không có bar đúng {as_of} (bar cuối={bars[-1]['time'] if bars else None})")
    if len(bars) < 260:
        raise BlockError(f"thiếu lịch sử: {len(bars)} bar (<260)")
    by = {b["time"]: b for b in bars}
    if prev not in by:
        raise BlockError(f"không có bar phiên cuối kỳ trước {prev}")
    closes = [b["close"] for b in bars]
    ind = get_indicators(prev - dt.timedelta(days=10), as_of)
    for d in (as_of, prev):
        if d not in ind:
            raise BlockError(f"thiếu dòng chỉ báo VNINDEX ngày {d}")
    for n in (20, 50, 200):
        sma = sum(closes[-n:]) / n
        if abs(ind[as_of][f"MA{n}"] / sma - 1) > MA_TOL:
            raise BlockError(f"MA{n} BQ {ind[as_of][f'MA{n}']:.2f} ≠ SMA tự tính {sma:.2f} (>{MA_TOL:.1%})")
    period = [b for b in bars if start <= b["time"] <= as_of]
    cur, pv = by[as_of]["close"], by[prev]["close"]
    i_cur, i_prev = ind[as_of], ind[prev]
    F = []                      # (nhãn, chuỗi giá trị) — đúng chuỗi Livermore được phép chép

    def add(label, value):
        F.append((label, value))
    add(f"Đóng cửa {dmy(as_of)}", f"{vn(cur)} điểm")
    add(f"Đóng cửa {dmy(prev)} (cuối kỳ trước)", f"{vn(pv)} điểm")
    add("Thay đổi trong kỳ", f"{vn((cur / pv - 1) * 100, 2, True)}%")
    k, j = 0, len(bars) - 1
    up = bars[j]["close"] > bars[j - 1]["close"]
    while j > 0 and (bars[j]["close"] > bars[j - 1]["close"]) == up:
        k, j = k + 1, j - 1
    add(f"Chuỗi phiên {'tăng' if up else 'giảm'} liên tiếp tính đến {dmy(as_of)}", f"{k} phiên")
    for n in (20, 50, 200):
        add(f"MA{n} ngày {dmy(as_of)}", f"{vn(i_cur[f'MA{n}'])} (cuối kỳ trước {vn(i_prev[f'MA{n}'])})")
        add(f"Đóng cửa so với MA{n}", f"{vn((cur / i_cur[f'MA{n}'] - 1) * 100, 2, True)}%")
    add("RSI(14)", f"{vn(i_cur['D_RSI'] * 100, 1)} (cuối kỳ trước {vn(i_prev['D_RSI'] * 100, 1)})")
    add("MACD trừ đường tín hiệu", f"{vn(i_cur['D_MACDdiff'], 2, True)} (cuối kỳ trước {vn(i_prev['D_MACDdiff'], 2, True)})")
    flips = [d for d in sorted(ind) if start <= d <= as_of and d != min(ind)
             and (ind[d]["D_MACDdiff"] >= 0) != (ind[max(x for x in ind if x < d)]["D_MACDdiff"] >= 0)]
    if flips:
        add("Phiên MACD trừ tín hiệu đổi dấu gần nhất trong kỳ", f"{dmy(flips[-1])}")
    add("Dòng tiền CMF", f"{vn(i_cur['D_CMF'], 2, True)} (cuối kỳ trước {vn(i_prev['D_CMF'], 2, True)})")
    hi = max(period, key=lambda b: b["high"]); lo = min(period, key=lambda b: b["low"])
    lc = min(period, key=lambda b: b["close"])
    add("Cao nhất trong kỳ (giá trong phiên)", f"{vn(hi['high'])} ngày {dmy(hi['time'])}")
    add("Thấp nhất trong kỳ (giá trong phiên)", f"{vn(lo['low'])} ngày {dmy(lo['time'])}")
    add("Đóng cửa thấp nhất trong kỳ", f"{vn(lc['close'])} ngày {dmy(lc['time'])}")
    for n, nm in ((60, "60 phiên (~3 tháng)"), (250, "250 phiên (~1 năm)")):
        w = bars[-n:]
        h = max(w, key=lambda b: b["high"]); lw = min(w, key=lambda b: b["low"])
        add(f"Đỉnh {nm}", f"{vn(h['high'])} ngày {dmy(h['time'])}")
        add(f"Đáy {nm}", f"{vn(lw['low'])} ngày {dmy(lw['time'])}")
    prev_period = [b for b in bars if prev_start <= b["time"] <= prev]
    v_cur = sum(b["volume"] for b in period) / len(period)
    v_prev = sum(b["volume"] for b in prev_period) / len(prev_period)
    add(f"Khối lượng khớp trung bình phiên trong kỳ ({len(period)} phiên)", f"{vn(v_cur / 1e6, 0)} triệu cp")
    add(f"Khối lượng khớp trung bình phiên kỳ trước ({len(prev_period)} phiên)", f"{vn(v_prev / 1e6, 0)} triệu cp")
    add("Chênh lệch khối lượng trung bình so với kỳ trước", f"{vn((v_cur / v_prev - 1) * 100, 1, True)}%")
    vmax = max(period, key=lambda b: b["volume"])
    add("Phiên khối lượng lớn nhất trong kỳ", f"{dmy(vmax['time'])}: {vn(vmax['volume'] / 1e6, 0)} triệu cp, "
        f"đóng cửa {vn((vmax['close'] / by[max(x for x in by if x < vmax['time'])]['close'] - 1) * 100, 2, True)}%")
    v20 = sum(b["volume"] for b in bars[-20:]) / 20
    add("Khối lượng trung bình 20 phiên", f"{vn(v20 / 1e6, 0)} triệu cp")
    breadth_ok = False
    try:
        br = get_breadth(prev, as_of)
    except Exception as ex:                       # độ rộng là mục "nếu dữ liệu có" — thiếu thì ghi rõ, không chặn khối
        print(f"WARN độ rộng: {ex}", file=sys.stderr)
        br = {}
    if as_of in br and prev in br:
        breadth_ok = True
        add(f"Tỷ lệ cổ phiếu đóng cửa trên MA50 ngày {dmy(as_of)}", f"{vn(br[as_of][0], 1)}% ({br[as_of][1]} mã trong rổ)")
        add(f"Tỷ lệ cổ phiếu đóng cửa trên MA50 ngày {dmy(prev)}", f"{vn(br[prev][0], 1)}% ({br[prev][1]} mã trong rổ)")
        inp = {d: v for d, v in br.items() if start <= d <= as_of}
        bmax = max(inp, key=lambda d: inp[d][0]); bmin = min(inp, key=lambda d: inp[d][0])
        add("Tỷ lệ trên MA50 cao nhất trong kỳ", f"{vn(inp[bmax][0], 1)}% ngày {dmy(bmax)}")
        add("Tỷ lệ trên MA50 thấp nhất trong kỳ", f"{vn(inp[bmin][0], 1)}% ngày {dmy(bmin)}")
    return {"kind": kind, "period_end": str(period_end), "as_of": str(as_of), "prev_as_of": str(prev),
            "period_start": str(start), "facts": F, "breadth": breadth_ok}


def facts_text(facts):
    return "\n".join(f"- {k}: {v}" for k, v in facts["facts"])


# ───────────────────────── dự báo ─────────────────────────
def forecast_entry_text(as_of):
    """Khối FORECAST nguyên văn của entry LVR-<as_of> trong sổ (dòng thụt 4 dưới '- forecast:')."""
    txt = C.read_registry()
    m = re.search(rf"^### LVR-{as_of}\s*$(.*?)(?=^### LVR-|\Z)", txt, re.S | re.M)
    if not m:
        raise BlockError(f"không thấy entry LVR-{as_of} trong sổ")
    fm = re.search(r"^- forecast:\n((?: {4}.*\n?)+)", m.group(1), re.M)
    if not fm:
        raise BlockError(f"entry LVR-{as_of} không có khối forecast")
    out = {}
    for ln in fm.group(1).splitlines():
        mm = re.match(r"^\s+- (H20_DIR|H20_P_UP|LEVEL|INVALIDATION):\s*(.*)$", ln)
        if mm:
            out[mm.group(1)] = mm.group(2).strip()
    if set(out) != {"H20_DIR", "H20_P_UP", "LEVEL", "INVALIDATION"}:
        raise BlockError(f"entry LVR-{as_of}: khối forecast thiếu trường ({sorted(out)})")
    return out


def resolve_forecast(as_of, kind, run_new=True):
    """→ dict {mode, entry_as_of, due, gap, fields}. Mù về sau: chỉ xét entry có as_of ≤ as_of kỳ."""
    all_e = C.parse_entries(C.read_registry())
    ents = [e for e in all_e if e["as_of"] <= as_of]
    last = max(ents, key=lambda e: e["as_of"]) if ents else None
    gap = sessions_between(last["as_of"], as_of) if last else None
    if last is not None and gap < MIN_GAP:
        mode, ent = "REPEAT", last
    else:
        # arch-review r1 #3: KHÔNG lập forecast lùi ngày. (a) báo cáo trễ (as_of cách phiên mới nhất > LATE_MAX) thì
        # lần đọc không còn là đọc sống; (b) sổ đã có entry SAU as_of trong vòng 20 phiên ⇒ chân sẽ chồng. Cả hai ⇒
        # 'không có dự báo mở', KHÔNG nhắc lại entry tương lai (lộ thông tin sau as_of).
        late = sessions_between(as_of, C.expected_last_session())
        fut = [e for e in all_e if e["as_of"] > as_of and sessions_between(as_of, e["as_of"]) <= MIN_GAP]
        if late > LATE_MAX or fut:
            why = (f"báo cáo trễ {late} phiên (> {LATE_MAX})" if late > LATE_MAX
                   else f"sổ đã có lần đọc sau as-of trong vòng {MIN_GAP} phiên")
            return {"mode": "NONE", "entry_as_of": None, "due": None, "gap": gap, "fields": None,
                    "result": None, "why": why}
        if not run_new:
            raise BlockError("cần forecast MỚI nhưng run_new=False")
        env = dict(os.environ, LIVERMORE_ALLOW_PAST="1")   # as_of đã được kiểm ≤ phiên kỳ vọng ở build_facts
        r = subprocess.run(["bash", RUN_BIN, "--as-of", str(as_of), "--triggers", f"REPORT_BLOCK_{kind.upper()}"],
                           capture_output=True, text=True, env=env, timeout=int(os.environ.get("LIVERMORE_RUN_TIMEOUT", 3000)))   # > lock-wait 1800 + claude 900
        if r.returncode != 0:
            raise BlockError(f"livermore_run.sh rc={r.returncode}: {(r.stderr or r.stdout).strip()[-400:]}")
        ent = next((e for e in C.parse_entries(C.read_registry()) if e["as_of"] == as_of), None)
        if ent is None:
            raise BlockError(f"livermore_run.sh rc=0 nhưng sổ không có entry LVR-{as_of} parse được")
        mode = "NEW"
    return {"mode": mode, "entry_as_of": str(ent["as_of"]), "due": str(ent["due"]), "gap": gap,
            "fields": forecast_entry_text(ent["as_of"]), "result": [ent["dir"], ent["p_up"], ent["level"]]}


def forecast_line(fc):
    if fc["mode"] == "NONE":
        return "- *Dự báo đang mở:* không có dự báo được lập cho kỳ này."
    f = fc["fields"]
    d = {"UP": "TĂNG", "DOWN": "GIẢM"}[f["H20_DIR"].split()[0]]
    lvl = f["LEVEL"].split()
    lv_num, lv_kind = lvl[0], (lvl[1] if len(lvl) > 1 else "")
    lv_txt = {"HOLD": "giữ được", "BREAK": "bị phá"}.get(lv_kind, lv_kind)
    e = dt.date.fromisoformat(fc["entry_as_of"]); due = dt.date.fromisoformat(fc["due"])
    lead = ("lập mới tại kỳ này" if fc["mode"] == "NEW" or fc.get("gap") == 0
            else "nhắc lại nguyên văn từ lần lập trước, chưa đáo hạn")
    return (f"- *Dự báo đang mở ({lead}; lập ngày {dmy(e)}, chấm điểm ngày {dmy(due)}):* hướng VN-Index sau 20 phiên "
            f"so với đóng cửa ngày lập: **{d}** (xác suất tự đánh giá {f['H20_P_UP']}); mức {lv_num}: {lv_txt} trong "
            f"20 phiên; điều kiện vô hiệu: {f['INVALIDATION']}")


def n_scored():
    return len(C.parse_scores(C.read_registry()))


# ───────────────────────── gọi Livermore ─────────────────────────
def build_prompt(facts, feedback=None):
    br = ("" if facts["breadth"] else
          "\nKHÔNG có số liệu độ rộng đã đối soát: dòng '- *Độ rộng:*' chỉ ghi đúng câu 'không có số liệu đã đối soát cho kỳ này.'")
    fb = f"\n\nLẦN TRƯỚC BỊ TỪ CHỐI vì: {feedback}. Sửa đúng các lỗi đó." if feedback else ""
    return f"""AS_OF = {facts['as_of']}. CHẾ ĐỘ REPORT_BLOCK (không phải lần đọc có forecast; KHÔNG viết FORECAST/RESULT).
Viết khối "Kỹ thuật" cho thư gửi nhà đầu tư, tiếng Việt, văn phong chuyên nghiệp, khách quan. Dữ liệu DUY NHẤT của bạn
là bảng SỐ LIỆU dưới đây (do script tính từ dữ liệu đóng cửa đã đối soát, kỳ {facts['period_start']} → {facts['as_of']}).
ĐỌC MÙ: không đọc file nào, không tra web, không dùng gì sau {facts['as_of']}, không nói về mô hình trạng thái thị trường.

SỐ LIỆU:
{facts_text(facts)}

LUẬT CỨNG (máy kiểm, sai một lỗi là cả khối bị loại):
1. Mọi con số và ngày tháng bạn viết phải CHÉP ĐÚNG NGUYÊN chuỗi có trong SỐ LIỆU (cùng số chữ số thập phân, dấu '.'
   phân cách nghìn, ',' thập phân). KHÔNG làm tròn, KHÔNG tự tính hiệu số/tỷ lệ mới, KHÔNG viết số bằng chữ, KHÔNG đưa
   ngưỡng tự đặt (vd '40%', '1.800'). Tên chỉ báo MA20/MA50/MA200/RSI(14) dùng được.
2. Diễn giải cấu trúc giá/khối lượng theo cách đọc của bạn (pha xu hướng, vùng mà đám đông bị neo/kẹt, khối lượng tại
   điểm xoay), nhưng chỉ bằng các số trên. Không khuyến nghị mua/bán, không hứa hẹn, không nói 'chắc chắn'.
3. Không nhắc tên hệ thống/bảng dữ liệu, không tự xưng tên.{br}
4. Trả về ĐÚNG 5 dòng giữa hai dấu mốc, theo thứ tự, mỗi dòng 1-3 câu, không thêm gì khác:

<<<BLOCK
- *Xu hướng:* ...
- *Hỗ trợ/kháng cự:* ...
- *Động lượng:* ...
- *Thanh khoản:* ...
- *Độ rộng:* ...
BLOCK>>>{fb}"""


def call_livermore(prompt):
    claude = os.environ.get("LIVERMORE_CLAUDE_BIN", "claude")
    work = tempfile.mkdtemp(prefix="livermore_block.")   # NGOÀI repo: không nạp CLAUDE.md (chứa DT5G)
    try:
        r = subprocess.run([claude, "-p", "--agent", "livermore", "--tools", "Read", "--setting-sources", "user",
                            "--no-session-persistence", "--strict-mcp-config", "--permission-prompts", "none",
                            "--max-budget-usd", os.environ.get("LIVERMORE_MAX_BUDGET", "3"),
                            "--disallowedTools", "Read(//home/trido/thanhdt/**)", "Read(//home/trido/.claude/projects/**)",
                            "--", prompt], cwd=work, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=int(os.environ.get("LIVERMORE_TIMEOUT", 900)))
    finally:
        subprocess.run(["rm", "-rf", work])
    if r.returncode != 0:
        raise BlockError(f"claude rc={r.returncode}: {r.stderr.strip()[:300]}")
    return r.stdout


def validate(raw, facts):
    """→ (5 dòng, []) hoặc (None, [lỗi...]). Thuần cơ học."""
    errs = []
    blocks = re.findall(r"<<<BLOCK\n(.*?)\nBLOCK>>>", raw, re.S)
    if len(blocks) != 1:
        return None, [f"cần đúng 1 khối <<<BLOCK...BLOCK>>>, thấy {len(blocks)}"]
    lines = [ln.rstrip() for ln in blocks[0].strip().splitlines() if ln.strip()]
    if len(lines) != len(LABELS):
        return None, [f"cần đúng {len(LABELS)} dòng, thấy {len(lines)}"]
    for ln, lab in zip(lines, LABELS):
        if not ln.startswith(f"- *{lab}:* ") or len(ln) < len(lab) + 12:
            errs.append(f"dòng sai nhãn/rỗng: cần '- *{lab}:* ...', thấy {ln[:40]!r}")
    if not facts["breadth"] and lines[-1].strip() != "- *Độ rộng:* không có số liệu đã đối soát cho kỳ này.":
        errs.append("không có số liệu độ rộng nhưng dòng Độ rộng không đúng câu quy định")
    body = "\n".join(lines)
    m = DENY.search(body)
    if m:
        errs.append(f"từ bị cấm: {m.group(0)!r}")
    f_dates, f_nums = tokens(facts_text(facts) + "\n" + "\n".join(LABELS))
    allowed_dm = {(d, mth) for d, mth, _ in f_dates}
    b_dates, b_nums = tokens(body)
    bad_d = sorted(f"{d}/{m_}" + (f"/{y}" if y else "") for d, m_, y in b_dates
                   if (d, m_, y) not in f_dates and not (y is None and (d, m_) in allowed_dm))
    if bad_d:
        errs.append(f"ngày lạ (không có trong SỐ LIỆU): {bad_d}")
    bad_n = sorted(b_nums - f_nums)
    if bad_n:
        errs.append(f"số lạ (không có trong SỐ LIỆU): {bad_n}")
    return (lines if not errs else None), errs


# ───────────────────────── lắp & ghi ─────────────────────────
def paths(as_of, kind):
    base = os.path.join(C.DATA_DIR, f"report_block_{as_of}_{kind}")
    return base + ".md", base + ".json", base + ".FAILED.json"


def assemble(facts, lines, fc):
    as_of = dt.date.fromisoformat(facts["as_of"])
    ns = n_scored()
    return "\n".join([
        f"**Kỹ thuật (VN-Index, dữ liệu đóng cửa {dmy(as_of)}) — {MARKER}:**",
        *lines,
        forecast_line(fc),
        "",
        f"*Nguồn số liệu: HOSE, tính toán nội bộ; mọi con số do hệ thống tính và được kiểm tra tự động trước khi đưa "
        f"vào nhận định. Dự báo được ghi lại trước và chấm điểm sau 20 phiên; số dự báo đã chấm điểm: {ns} — chưa đủ "
        f"để đánh giá độ chính xác, và kiểm thử trên dữ liệu lịch sử chưa cho thấy dự báo này tốt hơn giả định đơn "
        f"giản 'thị trường tăng'. Đây là nhận định tham khảo, không phải khuyến nghị đầu tư.*",
    ]) + "\n"


def verify_pass(as_of, kind):
    """PASS hợp lệ = .json status PASS + sha256 khớp .md hiện có + as_of/kind khớp. → (ok, json|lý do)."""
    md, js, _ = paths(as_of, kind)
    if not (os.path.exists(md) and os.path.exists(js)):
        return False, "chưa có khối PASS"
    meta = json.load(open(js, encoding="utf-8"))
    sha = hashlib.sha256(open(md, "rb").read()).hexdigest()
    if meta.get("status") != "PASS" or meta.get("sha256") != sha or meta.get("as_of") != str(as_of) \
            or meta.get("kind") != kind:
        return False, f"json/md không nhất quán (status={meta.get('status')}, sha khớp={meta.get('sha256') == sha})"
    return True, meta


def ensure(kind, period_end, run_new=True):
    """Khoá theo (period_end, kind): lượt song song (cadence chạy lại / composer gọi 2 lần) xếp hàng rồi thấy EXISTS."""
    import fcntl
    with open(C.lock_file(f"report_block_{period_end}_{kind}.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        return _ensure(kind, period_end, run_new)


def _ensure(kind, period_end, run_new=True):
    facts = build_facts(kind, period_end)
    as_of = dt.date.fromisoformat(facts["as_of"])
    ok, meta = verify_pass(as_of, kind)
    if ok:
        return 0, dict(meta, note="EXISTS")
    md, js, fj = paths(as_of, kind)
    attempts, fb, lines, errs, raws = 0, None, None, [], []
    fc = None
    try:
        fc = resolve_forecast(as_of, kind, run_new)
        for attempts in (1, 2):
            raw = call_livermore(build_prompt(facts, fb))
            raws.append(raw)
            lines, errs = validate(raw, facts)
            if lines:
                break
            fb = "; ".join(errs)
        if not lines:
            raise BlockError("kiểm cơ học thất bại sau 2 lần: " + "; ".join(errs))
    except Exception as ex:                                     # MỌI lỗi ⇒ FAILED.json (r1: KeyError/ValueError từng lọt)
        C.atomic_write(fj, json.dumps({"status": "FAIL", "kind": kind, "as_of": str(as_of), "reason": str(ex),
                                       "forecast": fc, "facts": facts["facts"], "raw": raws,
                                       "created": C.now_ict().isoformat(timespec="seconds")},
                                      ensure_ascii=False, indent=1) + "\n")
        return 1, {"status": "FAIL", "reason": str(ex), "failed_json": fj}
    text = assemble(facts, lines, fc)
    m = DENY.search(forecast_line(fc).replace("Livermore", ""))   # dòng dự báo chép nguyên văn sổ cũng không được lộ DT5G
    if m:
        C.atomic_write(fj, json.dumps({"status": "FAIL", "kind": kind, "as_of": str(as_of),
                                       "reason": f"dòng dự báo từ sổ chứa từ cấm {m.group(0)!r}"}, ensure_ascii=False) + "\n")
        return 1, {"status": "FAIL", "reason": f"dòng dự báo chứa từ cấm {m.group(0)!r}", "failed_json": fj}
    C.atomic_write(md, text)                                   # .md TRƯỚC, .json (dấu commit) SAU
    meta = {"status": "PASS", "kind": kind, "period_end": str(period_end), "as_of": str(as_of),
            "md": md, "sha256": hashlib.sha256(text.encode()).hexdigest(), "forecast": fc,
            "attempts": attempts, "facts": facts["facts"], "created": C.now_ict().isoformat(timespec="seconds")}
    C.atomic_write(js, json.dumps(meta, ensure_ascii=False, indent=1) + "\n")
    if os.path.exists(fj):
        os.remove(fj)
    return 0, meta


MARKER = "nhận định độc lập của Livermore"


def gate_report(text, kind, period_end):
    """Cổng cứng cho report_delivery_gate (arch-review r1 #2). → None (qua) hoặc chuỗi lý do CHẶN.
    - có khối PASS cho kỳ ⇒ báo cáo PHẢI chứa nguyên văn khối đó;
    - không có PASS ⇒ báo cáo KHÔNG được gắn tên Livermore (khối tự viết của người soạn là đường fallback hợp lệ)."""
    as_of = period_bounds(kind, period_end)[0]
    ok, meta = verify_pass(as_of, kind)
    if ok:
        block = open(meta["md"], encoding="utf-8").read().strip()
        return None if block in text else f"có khối Livermore PASS ({meta['md']}) nhưng báo cáo không chứa NGUYÊN VĂN khối"
    if MARKER in text:
        return f"báo cáo gắn nguồn Livermore nhưng không có khối PASS hợp lệ cho {kind} as_of {as_of} ({meta})"
    return None


def verify_report(report_path, kind, period_end):
    """Báo cáo đã soạn có chứa NGUYÊN VĂN khối PASS không. rc 0 có · 1 không/không có khối PASS."""
    as_of = period_bounds(kind, period_end)[0]
    ok, meta = verify_pass(as_of, kind)
    if not ok:
        return 1, {"status": "NO_PASS_BLOCK", "reason": meta}
    block = open(meta["md"], encoding="utf-8").read().strip()
    rep = open(report_path, encoding="utf-8").read()
    return (0, {"status": "VERBATIM"}) if block in rep else (1, {"status": "NOT_VERBATIM", "md": meta["md"]})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("ensure", "facts", "verify-report"):
        p = sub.add_parser(name)
        p.add_argument("--kind", choices=("weekly", "monthly"), required=True)
        p.add_argument("--period-end", required=True, type=dt.date.fromisoformat)
        if name == "verify-report":
            p.add_argument("report")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "facts":
            f = build_facts(a.kind, a.period_end)
            print(json.dumps({k: v for k, v in f.items() if k != "facts"}, ensure_ascii=False))
            print(facts_text(f))
            return 0
        if a.cmd == "verify-report":
            rc, out = verify_report(a.report, a.kind, a.period_end)
        else:
            rc, out = ensure(a.kind, a.period_end)
    except BlockError as ex:
        rc, out = 1, {"status": "FAIL", "reason": str(ex)}
    print(json.dumps({k: v for k, v in out.items() if k not in ("facts", "raw")}, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
