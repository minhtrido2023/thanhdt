#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
strategy_fit_dashboard.py — dashboard HTML "Độ phù hợp của chiến lược với thị trường hiện hành"
==============================================================================================
User duyệt 2026-10-11 20:53 ICT, job Taylor_20261011_135520.

ĐÂY LÀ LỚP HIỂN THỊ CHẨN ĐOÁN trên các artifact ĐÃ CÓ. Không backtest, không tính lại IC, không
phát tín hiệu, không ghi BigQuery, không sửa file nguồn nào. Ba bài học của
`kb/projects/amh-adaptivity-review-20260910.md` được đóng vào thiết kế:
  (a) 4 lần thử biến số đo thành luật tự điều chỉnh đều NO-GO/REFUTED (§7 change-point, §8 BAL
      edge-gate, §9 t_eff, ecology §1) ⇒ trang này KHÔNG có "điểm phù hợp" tổng hợp nào;
  (b) IC đo trên lợi suất 3 tháng tới nên trễ ~3 tháng; nhãn 12 tháng từng treo FLIPPED khi IC
      tháng đã dương lại (§6.3) ⇒ luôn in 3 giá trị IC tháng gần nhất cạnh nhãn;
  (c) composite kiểu ecology đã REFUTED ⇒ mỗi ô đứng riêng, không cộng gộp.

LUẬT CHO MỌI Ô (validate_html() cưỡng chế, selfcheck có ca đột biến):
  1. có ngày dữ liệu (as_of) + tên nguồn + huy hiệu CŨ khi già hơn nhịp cập nhật kỳ vọng;
  2. có dòng "Ngưỡng hành động" — CHỈ ngưỡng đang tồn tại trong code/KB, kèm file:dòng được ĐỊNH
     VỊ LÚC CHẠY bằng neo regex (cite()) nên không trôi khi file nguồn thêm/bớt dòng; ô không có
     ngưỡng thật ghi đúng câu DESCRIPTIVE;
  3. màu chỉ phản ánh nhãn/điều kiện đã có trong code nguồn;
  4. nguồn thiếu/hỏng ⇒ ô VẪN hiện "KHÔNG CÓ DỮ LIỆU" kèm lỗi thật (coding_guidelines §29).

TẦNG 3 (bản hẹp, user duyệt 2026-10-12 11:01 ICT, job Taylor_20261012_040250) — "thực tế so với kỳ
vọng", ĐÚNG 2 nhóm ô: drawdown thật từng tài khoản live, và trượt giá khớp lệnh. Ô "NAV thật so dải
backtest" bị HOÃN có chủ đích (69 phiên live quá ngắn, chưa có ngưỡng chốt trước) — đừng thêm.
  · Drawdown tính trên GIÁ ĐƠN VỊ QUỸ do `nav_unit_ledger.build_ledger` dựng (đã loại nạp/rút —
    cùng công thức với `nav_period_returns.py`), KHÔNG tính từ cột nav thô.
  · Trang KHÔNG tự đo trượt giá: hiện chưa có nguồn định kỳ nào, ô chỉ hiện trạng thái thật.

Chạy:  /home/trido/thanhdt/wc_venv/bin/python mike/bin/strategy_fit_dashboard.py
Ra:    mike/reports/dashboard/strategy_fit_<YYYY-MM-DD>.html (ngày ICT); dòng cuối stdout = đường dẫn.
Thoát: 0 = có ít nhất 1 ô DỮ LIỆU dựng được · 1 = không ô dữ liệu nào dựng được (ô book_map chỉ đọc
       code nên không tính) · 4 = vi phạm bất biến của chính trang (thiếu as_of / thiếu dòng ngưỡng /
       neo trích dẫn mất — lỗi code, không phải lỗi dữ liệu; không ghi file).
"""
import contextlib
import html as _html
import io
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from html.parser import HTMLParser
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
WC_ROOT = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude")

DESCRIPTIVE = "Chỉ để mô tả — không có ngưỡng hành động"
NO_DATA = "KHÔNG CÓ DỮ LIỆU"
UNKNOWN_ASOF = "không xác định"
LAG_NOTE = "số trễ khoảng 3 tháng vì đo trên lợi suất 3 tháng tới"
MAX_BYTES = 1_000_000

STATE_NAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
# Số dòng ngưỡng (có trích file:dòng) mỗi ô PHẢI mang; 0 = ô "chỉ để mô tả". validate_html() so đúng
# con số này, nên xoá/ thêm một dòng ngưỡng mà không sửa bảng dưới đây là selfcheck đỏ.
THR_COUNT = {"edge_ic": 3, "edge_lag": 3, "edge_capit": 2, "book_map": 0, "env_dt5g": 6,
             "env_breadth": 0, "env_value": 0, "env_rates": 2, "env_structural": 1,
             "live_dd_spacex": 2, "live_dd_zalopay": 2, "live_slippage": 1}
CELL_KEYS = ["edge_ic", "edge_lag", "edge_capit", "book_map",
             "env_dt5g", "env_breadth", "env_value", "env_rates", "env_structural",
             "live_dd_spacex", "live_dd_zalopay", "live_slippage"]
# File chỉ được TRÍCH DẪN (đọc dòng để in file:dòng), trang không chạy/không import nó. Để trong dict vì
# `production_manifest.py` (path_context) không coi chuỗi trong dict là cạnh phụ thuộc — viết thành biến
# gán thẳng sẽ kéo công cụ chạy tay này vào danh sách production tầng T0 (đo 2026-10-12).
CITE_ONLY = {"eqr": "execution_quality_review.py"}
LIVE_ACCOUNTS = ["SpaceX", "ZaloPay"]      # nhãn tài khoản; trang KHÔNG in số tài khoản hay số dư bằng tiền


# ───────────────────────────────────────────────────────────────── định dạng số kiểu VN
def _isnum(x):
    try:
        return x is not None and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def vn(x, nd=2, sign=False):
    """Số kiểu VN: dấu phẩy thập phân, dấu trừ U+2212. None/NaN/inf → '—'."""
    if not _isnum(x):
        return "—"
    s = f"{float(x):{'+' if sign else ''}.{nd}f}"
    return s.replace(".", ",").replace("-", "−")


def esc(s):
    return _html.escape("" if s is None else str(s), quote=True)


# ───────────────────────────────────────────────────────────────── trích dẫn file:dòng
class Citer:
    """Định vị file:dòng LÚC CHẠY bằng neo regex — số dòng không viết cứng nên không trôi.
    Neo không tìm thấy ⇒ in rõ "KHÔNG ĐỊNH VỊ ĐƯỢC" (không lặng lẽ bỏ) và ghi vào self.misses."""

    def __init__(self, root):
        self.root = root
        self.misses = []
        self._lines = {}

    def lines(self, rel):
        if rel not in self._lines:
            try:
                with open(os.path.join(self.root, rel), encoding="utf-8", errors="replace") as f:
                    self._lines[rel] = f.read().split("\n")
            except OSError as e:
                self._lines[rel] = e
        return self._lines[rel]

    def find(self, rel, pattern):
        """→ (lineno|None, match|None)."""
        ls = self.lines(rel)
        if isinstance(ls, Exception):
            self.misses.append(f"{rel}: {ls}")
            return None, None
        rx = re.compile(pattern)
        for i, ln in enumerate(ls, 1):
            m = rx.search(ln)
            if m:
                return i, m
        self.misses.append(f"{rel}: không thấy neo /{pattern}/")
        return None, None

    def cite(self, rel, pattern):
        n, _ = self.find(rel, pattern)
        if n is None:
            return f'<code class="cite miss">{esc(rel)}:KHÔNG ĐỊNH VỊ ĐƯỢC</code>'
        return f'<code class="cite">{esc(rel)}:{n}</code>'

    def const(self, rel, pattern):
        """Đọc hằng số THẬT từ code (group 1 của pattern) → (float|None, cite_html)."""
        n, m = self.find(rel, pattern)
        if n is None:
            return None, f'<code class="cite miss">{esc(rel)}:KHÔNG ĐỊNH VỊ ĐƯỢC</code>'
        try:
            val = float(m.group(1))
        except (ValueError, IndexError):
            val = None
        return val, f'<code class="cite">{esc(rel)}:{n}</code>'


# ───────────────────────────────────────────────────────────────── độ tươi
def bdays_after(d0, d1):
    """Số ngày Thứ 2-6 nằm SAU d0 và ≤ d1 (không trừ nghỉ lễ — ghi rõ ở chân trang)."""
    n, d = 0, d0
    while d < d1:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def file_mtime_ict(path):
    return datetime.fromtimestamp(os.path.getmtime(path), ICT)


def session_stale(as_of_date, today, limit=1):
    """Nguồn theo PHIÊN (BQ sync 23:45 ⇒ bình thường là T-1): CŨ khi thiếu > `limit` ngày làm việc."""
    gap = bdays_after(as_of_date, today)
    return gap > limit, f"thiếu {gap} ngày làm việc so với hôm nay (cho phép {limit})"


# ───────────────────────────────────────────────────────────────── SVG (inline, không xmlns ngoài)
def sparkline(values, label, w=320, h=60, dots=3):
    """Đường 1 chuỗi + đường 0. values: list float (None/NaN = đứt đoạn)."""
    pts = [(i, float(v)) for i, v in enumerate(values) if _isnum(v)]
    if len(pts) < 2:
        return '<p class="muted">(không đủ điểm để vẽ)</p>'
    lo = min(min(v for _, v in pts), 0.0)
    hi = max(max(v for _, v in pts), 0.0)
    span = (hi - lo) or 1.0
    n = max(len(values) - 1, 1)
    X = lambda i: 4 + i * (w - 8) / n
    Y = lambda v: 4 + (hi - v) * (h - 8) / span
    segs, cur, prev = [], [], None
    for i, v in pts:
        if prev is not None and i != prev + 1:
            segs.append(cur); cur = []
        cur.append(f"{X(i):.1f},{Y(v):.1f}"); prev = i
    segs.append(cur)
    paths = "".join(f'<polyline class="sl" points="{" ".join(s)}"/>' for s in segs if len(s) > 1)
    dts = "".join(f'<circle class="sd" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3"/>' for i, v in pts[-dots:])
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f'<title>{esc(label)}</title>'
            f'<line class="zero" x1="4" x2="{w - 4}" y1="{Y(0):.1f}" y2="{Y(0):.1f}"/>'
            f'{paths}{dts}</svg>')


def state_strip(states, w=320, h=26):
    """Dải trạng thái theo phiên (gộp đoạn liên tiếp). states: list int 1..5."""
    if not states:
        return ""
    n = len(states)
    runs, s0 = [], 0
    for i in range(1, n + 1):
        if i == n or states[i] != states[s0]:
            runs.append((s0, i, states[s0])); s0 = i
    bw = w / n
    rects = "".join(f'<rect class="st{s}" x="{a * bw:.2f}" y="0" width="{max((b - a) * bw - 0.6, 0.6):.2f}" '
                    f'height="{h}"><title>{STATE_NAME.get(s, s)}: {b - a} phiên</title></rect>'
                    for a, b, s in runs)
    return (f'<svg class="strip" viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" '
            f'aria-label="Dải trạng thái {n} phiên gần nhất">{rects}</svg>')


# ───────────────────────────────────────────────────────────────── mô hình ô
@dataclass
class Cell:
    key: str
    title: str
    tier: int
    source: str                 # tên nguồn (hiện ở mọi ô, kể cả khi lỗi)
    cadence: str                # nhịp cập nhật kỳ vọng + quy tắc gắn huy hiệu CŨ
    thr: list = field(default_factory=list)      # các dòng ngưỡng (HTML); rỗng ⇒ DESCRIPTIVE
    as_of: str = UNKNOWN_ASOF
    stale: object = None        # True / False / None (nguồn không có nhịp định kỳ)
    stale_why: str = ""
    body: str = ""
    error: str = None
    touched: list = field(default_factory=list)  # ngưỡng THẬT đang chạm (text thuần)


def render_cell(c):
    badges = ""
    if c.error is not None:
        badges += '<span class="bdg nodata">KHÔNG CÓ DỮ LIỆU</span>'
    if c.stale is True:
        badges += f'<span class="bdg stale" title="{esc(c.stale_why)}">CŨ</span>'
    if c.touched:
        badges += '<span class="bdg touch">CHẠM NGƯỠNG</span>'
    stale_txt = f' · <b>CŨ</b>: {esc(c.stale_why)}' if c.stale is True else ""
    body = c.body
    if c.error is not None:
        body = (f'<p class="nodata-msg"><b>{NO_DATA}</b> — lỗi thật đọc được: '
                f'<code>{esc(c.error)}</code></p>') + body
    if c.thr:
        thr = ('<div class="thr"><b>Ngưỡng hành động:</b><ul>'
               + "".join(f"<li>{t}</li>" for t in c.thr) + "</ul></div>")
    else:
        thr = f'<div class="thr"><b>Ngưỡng hành động:</b> {DESCRIPTIVE}.</div>'
    return (f'<section class="cell" id="{esc(c.key)}" data-asof="{esc(c.as_of)}">'
            f'<h3>{esc(c.title)} {badges}</h3>'
            f'<p class="meta">Dữ liệu tới: <b>{esc(c.as_of)}</b> · Nguồn: {c.source}<br>'
            f'Nhịp kỳ vọng: {esc(c.cadence)}{stale_txt}</p>'
            f'{body}{thr}</section>')


def _table(headers, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def _err(e):
    return f"{type(e).__name__}: {e}"


# ───────────────────────────────────────────────────────────────── TẦNG 1 — edge
# Nhãn → lớp màu: CHỈ 3 nhãn mà edge_health_monitor.py tự gắn màu (🔴 FLIPPED / 🟠 DECAYED /
# 🟢 STRENGTHENING, khối in "=== RED / ORANGE / STRENGTHENING ==="). Nhãn khác để trung tính.
VERDICT_CLASS = {"FLIPPED": "v-red", "DECAYED": "v-orange", "STRENGTH": "v-green"}

SIGNAL_ORDER = ["PE", "PB", "pb_z", "ROIC5Y", "ROE_Min5Y", "FSCORE", "mom_200", "D_RSI", "D_CMF", "C_L1M"]


def signal_books(ct):
    """Tín hiệu IC → book production. Chỉ ghi điều ĐỌC ĐƯỢC trong code; còn lại 'chưa xác định'."""
    v11 = "signal_v11_sql.py"
    return {
        "D_RSI": "BAL — điểm <code>ta</code> cộng 25 khi D_RSI&gt;0,50 "
                 + ct.cite(v11, r"WHEN t\.D_RSI > 0\.50 THEN 25"),
        "mom_200": "BAL — <i>liên quan nhưng KHÁC định nghĩa</i>: <code>ta</code> dùng "
                   "Close&gt;MA50&gt;MA200 " + ct.cite(v11, r"t\.Close > t\.MA50 AND t\.MA50 > t\.MA200")
                   + ", còn tín hiệu IC là Close/MA200−1 "
                   + ct.cite("edge_health_monitor.py", r"AS mom_200"),
        "FSCORE": "BAL — <code>ta</code> cộng 10 khi FSCORE≥8 " + ct.cite(v11, r"t\.FSCORE >= 8 THEN 10"),
        "PE": "custom30V — xếp hạng theo rank(1/PE)+rank(1/PCF) "
              + ct.cite("custom_basket.py", r"custom30V: liquidity is GATE only")
              + "; BAL dùng PE so với trung bình 5 năm của CHÍNH mã (khác định nghĩa) "
              + ct.cite(v11, r"t\.PE < t\.PE_MA5Y - 0\.5\*t\.PE_SD5Y"),
    }


def cell_edge_ic(data_dir, ct, now):
    import pandas as pd
    c = Cell("edge_ic", "Edge theo tín hiệu × nhóm ngành (IC)", 1,
             source="<code>data/edge_health_matrix.csv</code> + <code>data/edge_health_ic.csv</code> "
                    "(do <code>edge_health_monitor.py</code> ghi; registry: research-caches/edge_panel_csv)",
             cadence="chạy hằng ngày; CŨ khi file không được ghi lại quá 1 ngày làm việc")
    mon = "edge_health_monitor.py"
    c.thr = [
        "Không luật giao dịch nào đọc bảng này. Thử khoá BAL vào IC đã <b>NO-GO</b> (placebo thắng) — "
        + ct.cite("mike/kb/projects/amh-adaptivity-review-20260910.md", r"^## 8\. Kết quả job A"),
        "Nhãn do <code>classify()</code> gắn: |t|&lt;2 → WEAK; IC 12T trái dấu IC toàn kỳ và |IC 12T|≥0,015 → "
        "FLIPPED; tỷ lệ |12T|/|toàn kỳ| &lt;0,33 DECAYED · &lt;0,66 FADING · &gt;1,30 STRENGTH · còn lại HEALTHY — "
        + ct.cite(mon, r"^def classify\("),
        "Cảnh báo bằng chữ duy nhất: <code>mom_200</code>·ALL mang nhãn FLIPPED → «không nới slot/size "
        "momentum» (chỉ là dòng chữ trong báo cáo ngày, không có code thực thi) — "
        + ct.cite(mon, r'if mom_v == "FLIPPED"'),
    ]
    try:
        mpath = os.path.join(data_dir, "edge_health_matrix.csv")
        ipath = os.path.join(data_dir, "edge_health_ic.csv")
        m = pd.read_csv(mpath)
        ic = pd.read_csv(ipath, index_col=0)
        if m.empty or ic.empty:
            raise ValueError(f"file rỗng (matrix {len(m)} dòng, ic {len(ic)} dòng)")
        need = {"signal", "scope", "full", "recent", "tstat", "verdict"}
        if need - set(m.columns):
            raise ValueError(f"matrix thiếu cột {sorted(need - set(m.columns))}")
        ic.index = pd.to_datetime(ic.index)
        ic = ic.sort_index()
        as_of_month = ic.index[-1].strftime("%Y-%m")
        mt = min(file_mtime_ict(mpath), file_mtime_ict(ipath))
        c.as_of = f"tháng {as_of_month} (file ghi {mt:%Y-%m-%d %H:%M} ICT)"
        gap = bdays_after(mt.date(), now.date())
        c.stale, c.stale_why = gap > 1, f"file ghi lần cuối {mt:%Y-%m-%d}, đã {gap} ngày làm việc không cập nhật"
        books = signal_books(ct)
        last3 = ic.tail(3)
        blocks = []
        sigs = [s for s in SIGNAL_ORDER if s in set(m["signal"])] + \
               [s for s in m["signal"].unique() if s not in SIGNAL_ORDER]
        for s in sigs:
            sub = m[m["signal"] == s]
            label = sub["label"].iloc[0] if "label" in sub.columns else s
            rows = []
            for _, r in sub.iterrows():
                v = str(r["verdict"])
                rows.append([esc(r["scope"]), vn(r["full"], 3, True), vn(r["recent"], 3, True),
                             vn(r["tstat"], 2, True),
                             f'<span class="vd {VERDICT_CLASS.get(v, "")}">{esc(v)}</span>'])
            if s in ic.columns:
                l3 = " · ".join(f"{d:%m/%Y} <b>{vn(x, 3, True)}</b>" for d, x in last3[s].items())
                sp = sparkline(list(ic[s].tail(48)), f"IC tháng của {s}, 48 tháng gần nhất, phạm vi ALL")
                series = (f'{sp}<p class="l3">IC 3 tháng gần nhất (ALL): {l3}</p>')
            else:
                series = '<p class="muted">Không có chuỗi IC tháng cho tín hiệu này trong file.</p>'
            blocks.append(
                f'<div class="sig"><h4>{esc(label)} <code>{esc(s)}</code></h4>'
                f'<p class="bk">Book: {books.get(s, "chưa xác định")}</p>{series}'
                + _table(["Phạm vi", "IC toàn kỳ", "IC 12T", "t", "Nhãn 12T"], rows) + "</div>")
        c.body = (
            f'<p class="lagnote">Tháng as_of: <b>{as_of_month}</b> — {LAG_NOTE}. '
            f'Nhãn 12T có thể <b>trễ pha</b>: so nó với 3 giá trị IC tháng gần nhất ngay dưới mỗi biểu đồ. '
            f'Chuỗi tháng chỉ có cho phạm vi ALL (file nguồn không lưu chuỗi theo ngành). '
            f't tính trên n danh nghĩa, chuỗi chồng lấn 3 tháng nên |t| bị phóng đại.</p>'
            + "".join(blocks))
        al = m[(m["signal"] == "mom_200") & (m["scope"] == "ALL")]
        if len(al) and str(al["verdict"].iloc[0]) == "FLIPPED":
            c.touched.append("mom_200·ALL đang mang nhãn FLIPPED → cảnh báo chữ «không nới slot/size momentum»")
    except Exception as e:
        c.error = _err(e)
    return c


def cell_edge_lag(data_dir, ct, now, prov):
    import pandas as pd
    c = Cell("edge_lag", "Edge LAG thực tế (PEAD, lợi suất 25 phiên sau vào lệnh)", 1,
             source="<code>data/lag_edge_health.csv</code>, mốc <code>known_date</code> "
                    "(do <code>edge_health_monitor.lag_edge_health()</code> ghi)",
             cadence="chạy hằng ngày; CŨ khi file không được ghi lại quá 1 ngày làm việc. "
                     "Chuỗi tự trễ ~5 tuần vì một sự kiện chỉ hoàn tất sau 25 phiên")
    g = "deploy_golive_dt5g_v4/golive_recommend_v23.py"
    mon = "edge_health_monitor.py"
    thr_val, thr_cite = ct.const(g, r"^EDGE_THR\s*=\s*([0-9.]+)")
    thr_txt = vn(thr_val, 1) if thr_val is not None else "KHÔNG ĐỌC ĐƯỢC"
    c.thr = [
        f"<b>Đang thực thi (đường live):</b> ở NEUTRAL/BULL/EX-BULL, w_LAG mục tiêu = 0,65 CHỈ khi "
        f"mean12 ≥ {thr_txt}%; ngược lại 0,50; file hỏng/thiếu → fail-safe 0,50 — hằng số {thr_cite}, "
        f"hàm " + ct.cite(g, r"^def w_lag_target\(") + "; bản backtest tương ứng "
        + ct.cite("pt_v22_dt5g.py", r"^\s*EDGE_THR = 4\.0"),
        "Dải nhãn (báo cáo ngày): n12&lt;8 THIN · mean12 ≥4 HEALTHY · ≥1 NEUTRAL · ≥0 TROUGH · &lt;0 NEGATIVE — "
        + ct.cite(mon, r'if n12 < 8:\s+verdict, act = "THIN"'),
        "NEGATIVE kéo dài ≥3 tháng liên tiếp (mốc known_date) → dòng khuyến nghị «hạ w_LAG .65→.50 + treo "
        "entry LAG mới». Phần «treo entry» là CHỮ trong báo cáo; chưa xác định có code nào thực thi — "
        + ct.cite(mon, r"if neg_streak >= 3 else"),
    ]
    try:
        path = os.path.join(data_dir, "lag_edge_health.csv")
        d = pd.read_csv(path)
        if d.empty:
            raise ValueError("file rỗng (0 dòng)")
        if "known_date" not in d.columns:
            raise ValueError("thiếu cột known_date — không đọc theo mốc entry vì đó là nhìn trước ~25 phiên")
        d["known_date"] = pd.to_datetime(d["known_date"])
        d = d.sort_values("known_date")
        last = d.iloc[-1]
        m12, w12, n12 = last.get("mean12"), last.get("win12"), last.get("n12")
        mt = file_mtime_ict(path)
        c.as_of = f"{last['known_date']:%Y-%m-%d} (file ghi {mt:%Y-%m-%d %H:%M} ICT)"
        gap = bdays_after(mt.date(), now.date())
        c.stale, c.stale_why = gap > 1, f"file ghi lần cuối {mt:%Y-%m-%d}, đã {gap} ngày làm việc không cập nhật"
        try:
            ns, mo = prov["neg_streak"](d)
            ns_txt = str(ns) if ns is not None else "—"
            sp = sparkline(list(mo.tail(48)), "mean12 cuối tháng của LAG, 48 tháng gần nhất (mốc known_date)")
        except Exception as e:
            ns, ns_txt = None, f"không tính được ({_err(e)})"
            sp = ""
        rows = [["mean12 (trung bình 12 tháng, %)", f"<b>{vn(m12, 2, True)}</b>"],
                ["win12 (tỷ lệ thắng 12 tháng, %)", vn(w12, 1)],
                ["n12 (số sự kiện trong cửa sổ)", vn(n12, 0)],
                ["neg_streak (số tháng liên tiếp mean12&lt;0)", ns_txt]]
        pub = ""
        try:
            with open(os.path.join(data_dir, "golive_v23_status.json"), encoding="utf-8") as f:
                st = json.load(f)
            pub = (f'<p class="muted">Đối chiếu: engine công bố <code>w_lag_target</code> = '
                   f'<b>{vn(st.get("w_lag_target"), 2)}</b> (data/golive_v23_status.json, ngày {esc(st.get("date"))}).</p>')
        except Exception as e:
            pub = f'<p class="muted">Đối chiếu w_lag_target: không đọc được golive_v23_status.json ({esc(_err(e))}).</p>'
        c.body = sp + _table(["Chỉ số", "Giá trị hiện tại"], rows) + pub
        if thr_val is not None:
            if not _isnum(m12):
                c.touched.append("LAG mean12 không đọc được (NaN) → luật live rơi về w_LAG 0,50")
            elif float(m12) < thr_val:
                c.touched.append(f"LAG mean12 {vn(m12, 2, True)}% < {vn(thr_val, 1)}% → w_LAG mục tiêu 0,50 "
                                 f"thay vì 0,65 ở NEUTRAL/BULL/EX-BULL")
        if _isnum(m12) and float(m12) < 0 and ns is not None and ns >= 3:
            c.touched.append(f"LAG mean12 âm {ns} tháng liên tiếp (≥3) → báo cáo ngày khuyến nghị treo entry LAG mới")
    except Exception as e:
        c.error = _err(e)
    return c


def cell_edge_capit(data_dir, ct, now, prov):
    c = Cell("edge_capit", "Edge CAPIT (rổ mua sau washout)", 1,
             source="<code>edge_health_monitor.capit_edge_health()</code> đọc "
                    "<code>data/bt_capitulation_STRONG.csv</code> (cột FIX60_ret) — file CHƯA có mục trong data_registry",
             cadence="không có nhịp định kỳ — file backtest theo sự kiện, chỉ đổi khi có người chạy lại; "
                     "vì vậy không gắn được huy hiệu CŨ, xem ngày ghi file")
    mon = "edge_health_monitor.py"
    c.thr = [
        "Có trong code nhưng <b>KHÔNG nối vào production V2.4</b> (chỉ <code>pt_sleeve_allocator.py</code> "
        "và <code>amh_cockpit.py</code> của nhánh V6 đọc): trần carve CAPIT theo nhãn HEALTHY 70% / FADING 45% / "
        "NEGATIVE 20% — " + ct.cite(mon, r"^CARVE_BY_HEALTH\s*="),
        "Điều kiện nhãn: HEALTHY khi trung bình 4 sự kiện gần nhất ≥ 0,5× trung bình toàn kỳ, tỷ lệ thắng ≥50% "
        "và sự kiện cuối &gt; −5%; FADING khi trung bình gần &gt;0 và thắng ≥50%; còn lại NEGATIVE — "
        + ct.cite(mon, r"if rec_mean >= 0\.5 \* full_mean and rec_hit >= 0\.5 and last > -5"),
    ]
    try:
        path = os.path.join(data_dir, "bt_capitulation_STRONG.csv")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ce = prov["capit"]()
        if not ce:
            raise RuntimeError(buf.getvalue().strip() or "capit_edge_health() trả None, không in lý do")
        last_evt = "?"
        try:
            import pandas as pd
            last_evt = str(pd.read_csv(path)["date"].iloc[-1])
        except Exception:
            pass
        try:
            mt = f"{file_mtime_ict(path):%Y-%m-%d}"
        except OSError:
            mt = "?"
        c.as_of = f"sự kiện cuối {last_evt} (file ghi {mt})"
        v = str(ce.get("verdict"))
        rows = [["Nhãn", f'<span class="vd">{esc(v)}</span>'],
                ["Số sự kiện", vn(ce.get("n"), 0)],
                ["4 sự kiện gần nhất: trung bình / tỷ lệ thắng",
                 f'{vn(ce.get("rec_mean"), 1, True)}% / {vn(100 * ce.get("rec_hit"), 0) if _isnum(ce.get("rec_hit")) else "—"}%'],
                ["Toàn kỳ: trung bình / tỷ lệ thắng",
                 f'{vn(ce.get("full_mean"), 1, True)}% / {vn(100 * ce.get("full_hit"), 0) if _isnum(ce.get("full_hit")) else "—"}%'],
                ["Sự kiện cuối", f'{vn(ce.get("last"), 1, True)}%'],
                ["Trần carve theo nhãn (V6, không phải V2.4)", f'{vn(100 * ce.get("max_carve"), 0) if _isnum(ce.get("max_carve")) else "—"}%']]
        c.body = _table(["Chỉ số", "Giá trị"], rows)
    except Exception as e:
        c.error = _err(e)
    return c


def cell_book_map(ct, now, wc_root):
    c = Cell("book_map", "Chiến lược nào đang đứng trên edge nào", 1,
             source="đọc thẳng code production lúc sinh trang (file:dòng ở từng hàng)",
             cadence="theo commit của repo WorkingClaude — không có khái niệm CŨ")
    try:
        r = subprocess.run(["git", "-C", wc_root, "log", "-1", "--format=%h %cs"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip() or f"git rc={r.returncode}")
        c.as_of = "commit WorkingClaude " + r.stdout.strip()
    except Exception as e:
        c.as_of = f"{now:%Y-%m-%d} (không đọc được commit: {_err(e)})"
    v11, cb, g, mon = "signal_v11_sql.py", "custom_basket.py", "deploy_golive_dt5g_v4/golive_recommend_v23.py", "edge_health_monitor.py"
    rows = [
        ["<b>BAL</b> (SIGNAL_V11)",
         "Điểm <code>ta</code> trộn RSI ngày, xu hướng MA50/MA200, khối lượng, MACD, PE so với 5 năm của chính mã, "
         "FSCORE, tăng trưởng lợi nhuận " + ct.cite(v11, r"\(CASE WHEN t\.D_RSI > 0\.50 THEN 25")
         + ". Các tier mua chính đòi BULL/EX-BULL " + ct.cite(v11, r"WHEN ta >= 170 AND state5 IN \(4,5\) AND fa_tier")
         + "; momentum bị chặn ở EX-BULL " + ct.cite("pt_v22_dt5g.py", r"^mp4 = \(sig_f\[\"state\"\] == 5\)")
         + ". ⚠ IC ở ô trên đo trên TOÀN universe mọi tháng, BAL chỉ giao dịch tập con ⇒ IC lật dấu KHÔNG kéo theo BAL lỗ "
         + ct.cite("mike/kb/projects/amh-adaptivity-review-20260910.md", r"Cơ chế: \*\*lệch quần thể\*\*"),
         "Ô IC: D_RSI, FSCORE (trùng định nghĩa); mom_200, PE (liên quan, khác định nghĩa)"],
        ["<b>LAG</b> (PEAD)",
         "Cohort công bố lợi nhuận: NP_R≥15, prior_n_good≥4, pa_HL3≥5 "
         + ct.cite("lag_live_schedule.py", r"^NP_R_MIN, PRIOR_N_MIN, PA_HL3_MIN\s*=")
         + ". Không đứng trên tín hiệu IC nào trong bảng.",
         "Ô «Edge LAG thực tế»"],
        ["<b>custom30V</b> (parking NEUTRAL)",
         "Code ghi custom30V = <code>yieldcombo</code>: rank(1/PE)+rank(1/PCF), thanh khoản chỉ là cổng "
         + ct.cite(cb, r"custom30V: liquidity is GATE only")
         + ". Mặc định của biến chọn là <code>blend</code> " + ct.cite(cb, r'SELECT_MODE = os\.environ\.get\("BASKET_SELECT"')
         + " và có nhánh <code>eyonly</code> " + ct.cite(cb, r'elif SELECT_MODE == "eyonly"')
         + " — job publish rổ LIVE đang đặt giá trị nào: <b>chưa xác định</b>.",
         "Ô IC: PE (chắc); phần PCF không có trong bảng IC"],
        ["<b>CAPIT</b> (washout)",
         "Sự kiện washout, đo lợi suất rổ 60 phiên " + ct.cite(mon, r'r = ev\["FIX60_ret"\]')
         + ". Không đứng trên tín hiệu IC nào. Phân bổ CAPIT nằm trong NAV book LAG "
         + ct.cite(g, r'"formula": "slot = active_nav × w_lag_target × capit_size'),
         "Ô «Edge CAPIT» + ô lãi suất (cổng margin)"],
        ["Các tín hiệu IC còn lại (pb_z, PB, ROIC5Y, ROE_Min5Y, D_CMF, C_L1M)",
         "<b>chưa xác định</b> — chưa tìm được dòng code production nào dùng đúng định nghĩa này.", "—"],
    ]
    c.body = _table(["Book", "Đứng trên gì (trích code)", "Ô theo dõi"], rows, cls="wide")
    return c


# ───────────────────────────────────────────────────────────────── TẦNG 2 — môi trường
def cell_env_dt5g(ct, now, prov):
    import pandas as pd
    msl, dna, g = "macro_state_live.py", "dna_report.py", "deploy_golive_dt5g_v4/golive_recommend_v23.py"
    c = Cell("env_dt5g", "DT5G — trạng thái thị trường + đồng hồ cổng", 2,
             source="<code>macro_state_live.get_gated_state()</code> (cột <code>state</code>) + "
                    "<code>dna_report.get_dt_gate_clock()</code>. Không đọc bảng <code>vnindex_5state</code> trống hậu tố",
             cadence="theo phiên (BigQuery đồng bộ 23:45 ⇒ bình thường là T-1); CŨ khi thiếu quá 1 ngày làm việc")
    md, md_c = ct.const(dna, r"^BADZONE_REVIEW_MIN_DAYS, BADZONE_REVIEW_MAX_RET\s*=\s*(\d+)")
    c.thr = [
        "Cổng fail-safe: chỉ trả DT5G khi <code>data/macro_health.json</code> đọc được, tuổi ≤1440 phút và khuyến nghị "
        "DT5G_macro; ngược lại rơi về <b>DT4_only</b> (mất trần macro) — " + ct.cite(msl, r"^def get_gated_state\("),
        "Cam kết trạng thái: 10 phiên liên tiếp cho bước thường và để RA CRISIS/EX-BULL, 25 phiên để VÀO "
        "CRISIS/EX-BULL — " + ct.cite(msl, r"^def _dt_4gate\("),
        "w_LAG theo trạng thái: CRISIS 0,50 · BEAR 0,00 · NEUTRAL/BULL/EX-BULL 0,65 (còn phụ thuộc edge LAG, xem ô LAG) — "
        + ct.cite(g, r"^STATE_LAG_WEIGHT\s*="),
        f"Ngưỡng XEM LẠI luật đếm (không phải lệnh giao dịch): nền BEAR/CRISIS liền ≥{vn(md, 0)} phiên VÀ VNINDEX "
        f"≤−5% từ đầu đợt → báo Mike giao Taylor kiểm — {md_c}",
        "Mức chú ý của đồng hồ: tiến độ ≥70% «THEO DÕI», ≥85% «CHÚ Ý CAO» (chỉ là nhãn hiển thị) — "
        + ct.cite(dna, r"if progress >= 0\.85"),
        "Breadth guard trên trụ Mỹ: chỉ chặn cap khi breadth ≥0,50 và universe ≥100 mã — "
        + ct.cite(msl, r"breadth_th=0\.50"),
    ]
    try:
        start = (now - timedelta(days=420)).strftime("%Y-%m-%d")
        end = now.strftime("%Y-%m-%d")
        df, log = prov["gated_state"](start, end)
        if df is None or len(df) == 0:
            raise RuntimeError(f"get_gated_state trả rỗng cho [{start}, {end}]. Log: {log.strip()[-400:]}")
        df = df.sort_values("time")
        last = df.iloc[-1]
        d_last = pd.Timestamp(last["time"]).date()
        c.as_of = str(d_last)
        c.stale, c.stale_why = session_stale(d_last, now.date())
        st = int(last["state"])
        src = str(last.get("source", "?"))
        reason = ""
        for ln in log.splitlines():
            if ln.startswith("[get_gated_state]"):
                reason = re.sub(r"^(DT5G_macro|DT4_only|DT4_STALE):\s*", "", ln[len("[get_gated_state]"):].strip())
        tail = df.tail(250)
        states = [int(x) for x in tail["state"]]
        trans = []
        prev = None
        for t, s in zip(tail["time"], states):
            if prev is not None and s != prev:
                trans.append([f"{pd.Timestamp(t):%Y-%m-%d}", f"{STATE_NAME.get(prev, prev)} → {STATE_NAME.get(s, s)}"])
            prev = s
        legend = "".join(f'<span class="lg"><i class="sw st{k}"></i>{v}</span>' for k, v in STATE_NAME.items())
        base = int(last["base_state"]) if _isnum(last.get("base_state")) else None
        macro = int(last["macro_state"]) if _isnum(last.get("macro_state")) else None
        c.body = (
            f'<p class="big">{esc(STATE_NAME.get(st, st))} <span class="muted">(state={st})</span></p>'
            f'<p>Nguồn cổng trả về: <b>{esc(src)}</b>'
            + (f' — <code>{esc(reason)}</code>' if reason else "") + "</p>"
            f'<p class="muted">Cùng phiên: base (DT4) = {esc(STATE_NAME.get(base, "—"))}, '
            f'macro (DT5G) = {esc(STATE_NAME.get(macro, "—"))}.</p>'
            f'<p class="cap">Dải trạng thái {len(states)} phiên gần nhất (cũ → mới), theo đúng cột <code>state</code> cổng trả về:</p>'
            + state_strip(states) + f'<p class="legend">{legend}</p>'
            + (_table(["Ngày", "Chuyển trạng thái trong cửa sổ"], trans) if trans
               else '<p class="muted">Không có lần chuyển trạng thái nào trong cửa sổ.</p>'))
        if src != "DT5G_macro":
            c.touched.append(f"Cổng DT5G đang fail-safe về {src}: {reason or 'không đọc được lý do'}")
        try:
            clk = prov["dt_clock"]()
            line = prov["dt_line"]()
            if not clk or not line:
                raise RuntimeError("get_dt_gate_clock()/build_dt_gate_line() trả None (module tự nuốt lỗi, xem stderr)")
            c.body += (f'<p class="cap">Đồng hồ cổng (dữ liệu tới {esc(clk.get("asof"))}):</p>'
                       f'<pre class="wrap">{esc(line)}</pre>')
            if clk.get("active") and clk.get("need"):
                prog = clk["k"] / clk["need"]
                if prog >= 0.70:
                    c.touched.append(f"Đồng hồ DT5G: candidate {STATE_NAME.get(clk.get('cand'))} "
                                     f"{clk['k']}/{clk['need']} (≥70%)")
            bz = clk.get("badzone") or {}
            if bz.get("review"):
                c.touched.append(f"Nền xấu {bz.get('n')} phiên liền + VNINDEX {vn(100 * bz['ret'], 1, True)}% "
                                 f"→ chạm ngưỡng xem lại luật đếm DT")
        except Exception as e:
            c.body += (f'<p class="nodata-msg"><b>Đồng hồ cổng: {NO_DATA}</b> — <code>{esc(_err(e))}</code></p>')
    except Exception as e:
        c.error = _err(e)
    return c


def breadth_tercile(vals):
    """Tercile theo định nghĩa chuẩn (kb/projects/breadth-tercile-axis-20260822.md):
    pct = (# trong 252 phiên TRƯỚC < breadth_t) / 253, ngưỡng tường minh (pct==0 thuộc LOW).
    → (pct, nhãn) hoặc (None, None) khi chưa đủ 252 phiên trước."""
    if len(vals) < 253 or not _isnum(vals[-1]):
        return None, None
    prior = [v for v in vals[-253:-1] if _isnum(v)]
    if len(prior) < 252:
        return None, None
    pct = sum(1 for v in prior if v < vals[-1]) / 253.0
    return pct, ("LOW" if pct < 1 / 3 else "MID" if pct < 2 / 3 else "HIGH")


def cell_env_breadth(ct, now, prov):
    import pandas as pd
    c = Cell("env_breadth", "Breadth PIT — tỷ lệ mã trên MA200", 2,
             source="<code>tav2_mike.universe_pit</code> (CANONICAL, point-in-time) nối <code>tav2_bq.ticker</code>, "
                    "qua đúng câu SQL của <code>macro_state_live._breadth_sql()</code>; mẫu số chỉ đếm mã có MA200",
             cadence="theo phiên (universe_pit dựng 19:00 ICT); CŨ khi thiếu quá 1 ngày làm việc")
    try:
        start = (now - timedelta(days=640)).strftime("%Y-%m-%d")
        df = prov["breadth"](start, now.strftime("%Y-%m-%d"))
        if df is None or len(df) == 0:
            raise RuntimeError("truy vấn breadth trả 0 dòng")
        df = df.sort_values("time")
        d_last = pd.Timestamp(df["time"].iloc[-1]).date()
        c.as_of = str(d_last)
        c.stale, c.stale_why = session_stale(d_last, now.date())
        vals = [float(x) if _isnum(x) else float("nan") for x in df["b200"]]
        pct, lab = breadth_tercile(vals)
        univ = df["univ"].iloc[-1]
        terc = (f"<b>{lab}</b> (phân vị {vn(100 * pct, 1)} trong 252 phiên trước)" if lab
                else f"chưa xếp được — cần 252 phiên trước, đang có {len(vals) - 1}")
        c.body = (
            sparkline(vals[-250:], "Breadth trên MA200, 250 phiên gần nhất")
            + _table(["Chỉ số", "Giá trị"], [
                ["Breadth phiên cuối (% mã trên MA200)", f"<b>{vn(100 * vals[-1], 1)}%</b>"],
                ["Số mã trong universe (có MA200)", vn(univ, 0)],
                ["Tercile của breadth phiên cuối", terc]])
            + '<p class="muted">Theo quy ước PIT, phiên giao dịch KẾ TIẾP mới được xếp theo breadth này '
              '(dùng breadth của phiên liền trước). Trục này đã đo 0/27 ô và 0/4 qua kiểm định — chỉ để mô tả. '
              'Ngưỡng 0,50 của breadth guard DT5G là thứ khác, xem ô DT5G.</p>')
    except Exception as e:
        c.error = _err(e)
    return c


def cell_env_value(ct, now, prov):
    c = Cell("env_value", "Value Radar — định giá thị trường", 2,
             source="<code>value_radar.value_radar_now(update=False)</code> đọc cache "
                    "<code>data/value_radar_series.csv</code> (CANONICAL, DISPLAY-ONLY). Không tự tính phân vị",
             cadence="theo phiên; CŨ khi thiếu quá 1 ngày làm việc. Trang này chỉ ĐỌC cache, không tự cập nhật")
    try:
        from datetime import date as _date
        v = prov["value_radar"]()
        if not v:
            raise RuntimeError("value_radar_now() trả None (module tự nuốt lỗi, xem stderr)")
        d_last = _date.fromisoformat(str(v["asof"]))
        c.as_of = str(d_last)
        c.stale, c.stale_why = session_stale(d_last, now.date())
        lab = {"CHEAP": "RẺ", "FAIR": "TRUNG TÍNH", "EXPENSIVE": "ĐẮT"}.get(v.get("label"), v.get("label"))
        dep = "CCTG 6T" if v.get("deposit_rate_source") == "cctg_6m" else "Big-4 12T"
        c.body = (
            f'<p class="big">{vn(v.get("score"), 1)} <span class="vd">{esc(lab)}</span></p>'
            + _table(["Thành phần", "Giá trị", "Phân vị 10 năm"], [
                ["P/E capped-10%", vn(v.get("pe_cap10"), 2), "p" + vn(v.get("p_pe"), 0)],
                ["P/B capped-10%", vn(v.get("pb_cap10"), 2), "p" + vn(v.get("p_pb"), 0)],
                [f"Spread EY − {dep} (pp)", vn(v.get("spread"), 2, True), "p" + vn(v.get("p_sp"), 0)],
                ["Bản expanding từ 2008 (đối chiếu)", vn(v.get("score_expanding"), 1), "—"]])
            + '<p class="muted">Nhãn theo ngưỡng cố định của module: RẺ &lt;33 · TRUNG TÍNH 33–67 · ĐẮT &gt;67. '
              'Chưa qua kiểm định đủ mạnh (0/17 lăng kính qua đa kiểm định), đầu RẺ không đơn điệu — '
              'không phải tín hiệu mua/bán.</p>')
    except Exception as e:
        c.error = _err(e)
    return c


def cell_env_rates(data_dir, ct, now, prov):
    dep, g = "deposit_rate_vn.py", "deploy_golive_dt5g_v4/golive_recommend_v23.py"
    c = Cell("env_rates", "Lãi suất huy động — khoảng cách tới hai ngưỡng", 2,
             source="<code>deposit_rate_vn.macro_killswitch_a_status()</code> (effective = max(Big-4 12T, CCTG 6T)) + "
                    "<code>current_deposit_rate()</code> (Big-4 12T); registry: CANONICAL-PROXY",
             cadence="xác nhận thủ công hằng tháng; CŨ theo đúng luật của nguồn: quá 45 ngày chưa xác nhận lại")
    a_thr, a_cite = ct.const(dep, r"^\s*THRESHOLD\s*=\s*([0-9.]+)")
    m_thr, m_cite = ct.const(g, r"^CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD\s*=\s*([0-9.]+)")
    c.thr = [
        f"Kill-switch A: lãi effective &gt; {vn(100 * a_thr, 1) if a_thr is not None else 'KHÔNG ĐỌC ĐƯỢC'}% → "
        f"SUSPEND triển khai recovery mới; nguồn cũ/lỗi → coi như đã kích hoạt — {a_cite}, khai báo "
        + ct.cite("data/trading_rules.json", r'"A_sbv_rate_suspend"')
        + ". Hiện là <b>hiển thị/giám sát</b>: sleeve nó chặn chưa có đường lệnh live — "
        + ct.cite(dep, r"DISPLAY/MONITORING ONLY as of this commit"),
        f"Cổng CAPIT margin: Big-4 12T ≥ {vn(m_thr, 1) if m_thr is not None else 'KHÔNG ĐỌC ĐƯỢC'}%/năm → coi là khủng "
        f"hoảng cơ cấu (Loại 1), KHÔNG áp đòn bẩy dù dd52 đã đạt cổng — {m_cite}, điều kiện "
        + ct.cite(g, r"elif _pit_deposit_rate >= CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD")
        + ". Cùng cổng còn điều kiện CPI YoY ≥ 6,0% (không hiển thị ở bản này) — "
        + ct.cite(g, r"^CAPIT_LEVER_PIT_CPI_THRESHOLD\s*="),
    ]
    try:
        ks = prov["killswitch"]()
        if not isinstance(ks, dict):
            raise RuntimeError(f"macro_killswitch_a_status() trả {type(ks).__name__}")
        c.as_of = str(ks.get("last_update") or UNKNOWN_ASOF)
        c.stale = bool(ks.get("stale"))
        c.stale_why = str(ks.get("reason", ""))
        rate = ks.get("rate")
        rate_pct = 100 * rate if _isnum(rate) else None
        rows = [["Lãi effective", f"<b>{vn(rate_pct, 2)}%</b>", esc(ks.get("rate_source") or "—")],
                ["Ngưỡng kill-switch A", f"{vn(100 * a_thr, 1) if a_thr is not None else '—'}%", "—"],
                ["Khoảng cách tới ngưỡng A",
                 f"{vn(100 * a_thr - rate_pct, 2)} điểm %" if (rate_pct is not None and a_thr is not None) else "—", "—"],
                ["Trạng thái code trả về", "ARMED" if ks.get("armed") else "CLEAR", esc(ks.get("reason"))]]
        big4 = None
        try:
            big4 = prov["big4_rate"]()
            rows += [["Big-4 12T", f"<b>{vn(big4, 2)}%</b>", "current_deposit_rate()"],
                     ["Ngưỡng cổng CAPIT margin", f"{vn(m_thr, 1)}%", "—"],
                     ["Khoảng cách tới ngưỡng margin",
                      f"{vn(m_thr - big4, 2)} điểm %" if (m_thr is not None and _isnum(big4)) else "—", "—"]]
        except Exception as e:
            rows += [["Big-4 12T", NO_DATA, esc(_err(e))]]
        try:
            with open(os.path.join(data_dir, "trading_rules.json"), encoding="utf-8") as f:
                en = json.load(f).get("capit_margin_lever", {}).get("enabled")
            rows += [["capit_margin_lever.enabled (trading_rules.json)", esc(en), "—"]]
        except Exception as e:
            rows += [["capit_margin_lever.enabled", NO_DATA, esc(_err(e))]]
        c.body = _table(["Chỉ số", "Giá trị", "Ghi chú nguồn"], rows)
        if ks.get("armed"):
            c.touched.append(f"Kill-switch A lãi suất đang ARMED: {ks.get('reason')}")
        if m_thr is not None and _isnum(big4) and float(big4) >= m_thr:
            c.touched.append(f"Big-4 12T {vn(big4, 2)}% ≥ {vn(m_thr, 1)}% → cổng CAPIT margin chặn đòn bẩy")
    except Exception as e:
        c.error = _err(e)
    return c


def cell_env_structural(kb_dir, ct, now):
    from datetime import date as _date
    proto = "mike/kb/projects/amh-structural-break-protocol-20260910.md"
    c = Cell("env_structural", "Sự kiện cấu trúc đang theo dõi", 2,
             source="<code>mike/kb/structural_break_watch.json</code> (Mike giữ; CHƯA có mục trong data_registry)",
             cadence="rà mỗi quý cùng review của Bobby; CŨ khi đã quá ngày next_review ghi trong file")
    c.thr = ["Sự kiện có hiệu lực ⇒ BẮT BUỘC re-validate các tầng liệt kê ở cột cuối; protocol KHÔNG cho phép đổi "
             "tham số — " + ct.cite(proto, r"Protocol KHÔNG cho phép đổi tham số")]
    try:
        path = os.path.join(kb_dir, "structural_break_watch.json")
        with open(path, encoding="utf-8") as f:
            j = json.load(f)
        ev = j.get("events")
        if not ev:
            raise ValueError("file không có sự kiện nào (events rỗng)")
        nr = j.get("next_review")
        c.as_of = f"file ghi {file_mtime_ict(path):%Y-%m-%d}, mở {j.get('opened', '?')}, rà tiếp {nr or '?'}"
        try:
            over = now.date() > _date.fromisoformat(str(nr))
            c.stale, c.stale_why = over, f"đã quá ngày rà soát {nr}"
        except (TypeError, ValueError):
            c.stale, c.stale_why = True, f"next_review không đọc được ({nr!r})"
        rows = [[esc(e.get("label")), f'<span class="vd">{esc(e.get("status"))}</span>',
                 esc(e.get("effective_date") or "—"), esc(", ".join(e.get("revalidate") or []))] for e in ev]
        c.body = (f"<p>{len(ev)} sự kiện · rà soát kế tiếp: <b>{esc(nr)}</b></p>"
                  + _table(["Sự kiện", "Trạng thái", "Ngày hiệu lực", "Phải re-validate"], rows, cls="wide"))
        for e in ev:
            if str(e.get("status")) != "watching":
                c.touched.append(f"Sự kiện cấu trúc «{e.get('label')}» ở trạng thái {e.get('status')} → bắt buộc re-validate")
    except Exception as e:
        c.error = _err(e)
    return c


# ───────────────────────────────────────────────────────────────── TẦNG 3 — thực tế so với kỳ vọng
def drawdown_stats(ledger):
    """Drawdown trên GIÁ ĐƠN VỊ QUỸ. `ledger` = đầu ra `nav_unit_ledger.build_ledger` (dòng 0 = mốc
    khởi điểm, mỗi dòng sau = một phiên có NAV chốt). N = số PHIÊN (sự kiện độc lập), không phải số dòng file."""
    if len(ledger) < 2:
        raise ValueError(f"sổ đơn vị chỉ có {len(ledger)} dòng — chưa có phiên nào sau mốc khởi điểm")
    for r in ledger:
        if not _isnum(r["unit_price"]) or float(r["unit_price"]) <= 0:
            raise ValueError(f"giá đơn vị ngày {r['date']} không hợp lệ: {r['unit_price']!r}")
    peak, max_dd, max_peak, max_trough = ledger[0], 0.0, ledger[0], ledger[0]
    worst_day, worst_row = None, None
    for prev, row in zip(ledger, ledger[1:]):
        day = row["unit_price"] / prev["unit_price"] - 1
        if worst_day is None or day < worst_day:
            worst_day, worst_row = day, row
        if row["unit_price"] > peak["unit_price"]:
            peak = row
        dd = row["unit_price"] / peak["unit_price"] - 1
        if dd < max_dd:
            max_dd, max_peak, max_trough = dd, peak, row
    last = ledger[-1]
    missing, d = [], ledger[0]["date"]
    have = {r["date"] for r in ledger}
    while d < last["date"]:
        d += timedelta(days=1)
        if d.weekday() < 5 and d not in have:
            missing.append(d)
    return dict(n=len(ledger) - 1, first=ledger[0], last=last, peak=peak,
                cur_dd=last["unit_price"] / peak["unit_price"] - 1,
                since_peak=sum(1 for r in ledger if r["date"] > peak["date"]),
                max_dd=max_dd, max_peak=max_peak, max_trough=max_trough,
                day_ret=last["unit_price"] / ledger[-2]["unit_price"] - 1,
                worst_day=worst_day, worst_row=worst_row,
                total=last["unit_price"] / ledger[0]["unit_price"] - 1,
                est=[r for r in ledger[1:] if r.get("nav_is_estimate")], missing=missing)


def _d(row):
    return f'{row["date"]}' + (" <i>(NAV ước tính)</i>" if row.get("nav_is_estimate") else "")


def cell_live_dd(account, data_dir, ct, now, prov):
    c = Cell(f"live_dd_{account.lower()}", f"Drawdown thật — tài khoản {account}", 3,
             source="giá đơn vị quỹ dựng trong bộ nhớ bởi <code>mike/bin/nav_unit_ledger.build_ledger</code> từ "
                    f"<code>nav_history_{esc(account)}.csv</code> + <code>account_cash_flows.json</code> + "
                    "<code>account_inception.json</code> (đã loại nạp/rút; cùng công thức với "
                    "<code>nav_period_returns.py</code>). Sổ đơn vị trên đĩa CHƯA chốt (chính sách bước 3)",
             cadence="mỗi phiên, sau lượt chụp NAV 19:10 ICT; CŨ khi thiếu quá 1 ngày làm việc")
    lim, lim_cite = ct.const("data/trading_rules.json", r'"daily_loss_limit_pct":\s*(-?[0-9.]+)')
    epi, epi_cite = ct.const("data/trading_rules.json", r"recovery episode's entry point > (-[0-9.]+)")
    epi_on = os.path.exists(os.path.join(data_dir, "recovery_episode_state.json"))
    c.thr = [
        f"Phanh lỗ TRONG NGÀY (không phải drawdown từ đỉnh): NAV trong phiên giảm ≤ "
        f"{vn(100 * lim, 1) if lim is not None else 'KHÔNG ĐỌC ĐƯỢC'}% → HALT (dừng lệnh mới, huỷ lệnh chờ, "
        f"BOT_STOP) — khai báo {lim_cite}. Ô này chỉ có giá CHỐT cuối ngày nên chỉ bắt được ca phiên đóng cửa "
        "đã ở dưới ngưỡng; không thấy được ca chạm trong phiên rồi hồi",
        f"Phanh episode recovery: NAV giảm quá {vn(100 * epi, 0) if epi is not None else 'KHÔNG ĐỌC ĐƯỢC'}% tính "
        f"từ điểm vào episode (KHÔNG tính từ đỉnh tài khoản) → HALT — khai báo {epi_cite}. File trạng thái "
        f"episode <code>data/recovery_episode_state.json</code>: <b>{'có' if epi_on else 'không tồn tại'}</b>"
        + ("" if epi_on else " ⇒ không có episode nào đang được theo dõi, ô này không đánh giá luật đó"),
    ]
    anchor_cite = ct.cite("CLAUDE.md", r"Neo sizing DD lấy ĐẦU SÀN")
    try:
        got = prov["unit_ledger"](account)
        if got["jumps"]:
            j = got["jumps"][0]
            raise RuntimeError(
                f"cổng NAV-jump {got.get('block_pct')}% CHẶN: {len(got['jumps'])} bước nhảy NAV không có bản ghi dòng "
                f"tiền (đầu tiên {j['prev_date']}→{j['date']}: {j['change_pct']:+.2f}%) — có thể là nạp/rút chưa "
                f"khai, nên KHÔNG công bố drawdown")
        s = drawdown_stats(got["ledger"])
        c.as_of = str(s["last"]["date"])
        c.stale, c.stale_why = session_stale(s["last"]["date"], now.date())
        _, m = ct.find("CLAUDE.md", r"Neo sizing DD lấy ĐẦU SÀN (−[0-9]+,[0-9]+)%")
        anchor = m.group(1) if m else "KHÔNG ĐỌC ĐƯỢC"
        rows = [
            ["Số phiên live (N)", f"<b>{s['n']}</b>", f"từ mốc khởi điểm {s['first']['date']} tới {_d(s['last'])}"],
            ["Drawdown hiện tại từ đỉnh", f"<b>{vn(100 * s['cur_dd'], 2)}%</b>",
             f"đỉnh giá đơn vị ngày {_d(s['peak'])}; {s['since_peak']} phiên kể từ đỉnh"],
            ["Drawdown lớn nhất từ khi live", f"<b>{vn(100 * s['max_dd'], 2)}%</b>",
             f"đỉnh {_d(s['max_peak'])} → đáy {_d(s['max_trough'])}" if s["max_dd"] < 0 else "chưa có phiên nào dưới đỉnh"],
            ["Tỉ suất từ khi live (gia quyền thời gian)", f"{vn(100 * s['total'], 2, True)}%", "tỉ số hai giá đơn vị"],
            ["Phiên gần nhất so với phiên trước", f"{vn(100 * s['day_ret'], 2, True)}%", "giá chốt → giá chốt"],
            ["Phiên giảm mạnh nhất", f"{vn(100 * s['worst_day'], 2, True)}%", f"{_d(s['worst_row'])}; giá chốt → giá chốt"],
            ["Mốc tham chiếu (KHÔNG phải ngưỡng)", f"{esc(anchor)}%",
             f"neo sizing: phân vị 5 của bootstrap trên backtest, quy ước pin0% — {anchor_cite}"],
        ]
        c.body = (
            _table(["Chỉ số", "Giá trị", "Ghi chú"], rows)
            + sparkline([100 * (r["unit_price"] / got["ledger"][0]["unit_price"] - 1) for r in got["ledger"]],
                        f"Tỉ suất luỹ kế {account} theo giá đơn vị quỹ, {s['n']} phiên")
            + f'<p class="cap">Tỉ suất luỹ kế theo giá đơn vị quỹ (%), {s["n"]} phiên; đường ngang = mốc khởi điểm.</p>'
            + '<p class="muted"><b>Drawdown từ đỉnh không có luật hành động nào trong code/KB</b> — hai dòng ngưỡng '
              'bên dưới là hai luật KHÁC đại lượng (lỗ trong ngày; lỗ từ điểm vào episode). Mốc tham chiếu là con số '
              f'của backtest nhiều năm; {s["n"]} phiên live chưa đủ để nói drawdown thật «khớp» hay «lệch» mốc đó.</p>')
        if account == "ZaloPay":
            c.body += ('<p class="muted">Đây là chuỗi <b>TOÀN tài khoản</b>, gồm cả DGC và vị thế có sẵn nằm ngoài '
                       'phạm vi bot; chuỗi «phần bot quản lý» chưa được dựng — '
                       + ct.cite("mike/kb/projects/fund-unit-performance-policy-20261010.md", r"ZaloPay hai chuỗi")
                       + '. Không so thẳng với SpaceX hay backtest.</p>')
        if s["est"]:
            c.body += (f'<p class="muted">{len(s["est"])}/{s["n"]} phiên có NAV <b>ước tính</b> '
                       f'(<code>nav_is_estimate</code>), giữ nguyên không sửa: '
                       + ", ".join(str(r["date"]) for r in s["est"][:12]) + ("…" if len(s["est"]) > 12 else "") + ".</p>")
        if s["missing"]:
            c.body += (f'<p class="muted">{len(s["missing"])} ngày Thứ 2–6 không có dòng NAV (gồm cả nghỉ lễ), '
                       f'KHÔNG nội suy: ' + ", ".join(str(d) for d in s["missing"][:8])
                       + ("…" if len(s["missing"]) > 8 else "") + ".</p>")
        for key, label in (("pending", "TREO — chưa nằm trong tỉ suất nào"), ("dropped", "bị loại vì ≤ mốc khởi điểm")):
            if got.get(key):
                c.body += (f'<p class="nodata-msg">{len(got[key])} dòng tiền {label}: '
                           + ", ".join(str(f.get("date")) for f in got[key]) + ".</p>")
        if lim is not None and s["day_ret"] <= lim:
            c.touched.append(f"{account}: phiên {s['last']['date']} đóng cửa {vn(100 * s['day_ret'], 2, True)}% so với "
                             f"phiên trước, ≤ phanh lỗ trong ngày {vn(100 * lim, 1)}%")
    except Exception as e:
        c.error = _err(e)
    return c


def live_buy_sessions(data_dir, account, since):
    """Ngày (chuỗi) có ≥1 lệnh MUA bot ĐẶT (journal PLACE) từ `since`, trừ corp-action. Journal là file
    RIÊNG từng tài khoản (tên file mang nhãn) — không đọc file dùng chung nào (§12). Đây là bộ ĐẾM
    phiên, không phải số đo giá."""
    import csv
    import glob
    out = []
    for f in sorted(glob.glob(os.path.join(data_dir, "execution_logs", f"exec_{account}_2*_journal.csv"))):
        d = os.path.basename(f)[len(f"exec_{account}_"):][:10]
        if d < since:
            continue
        with open(f, encoding="utf-8", newline="") as fh:
            if any(r.get("event") == "PLACE" and str(r.get("side", "")).lower() == "buy"
                   and r.get("book") != "CORP_ACTION" for r in csv.DictReader(fh)):
                out.append(d)
    return out


def cell_live_slippage(data_dir, kb_dir, ct, now):
    reg, ops, eqr = "mike/kb/paper_programs_registry.json", "mike/kb/current_ops.md", CITE_ONLY["eqr"]
    c = Cell("live_slippage", "Trượt giá khớp lệnh MUA — giá khớp so với giá mở cửa", 3,
             source="<code>mike/kb/paper_programs_registry.json</code> (chương trình <code>fill_timing</code>, khối "
                    "<code>progress.live_monitoring</code>) + bộ đếm phiên từ journal từng tài khoản "
                    "<code>data/execution_logs/exec_&lt;tài khoản&gt;_*_journal.csv</code>. Trang KHÔNG tự đo trượt giá",
             cadence="theo luật: đo lại sau mỗi ~10 phiên live có lệnh MUA hybrid. CHƯA có cron nào sinh số này; "
                     "CŨ khi bộ đếm ghi trong registry lệch số phiên đếm được từ journal")
    thr_bps, thr_cite = ct.const(ops, r"rollback nếu mean >\+([0-9]+)bps")
    c.thr = [f"Trung bình giá khớp MUA so với giá mở cửa &gt; +{vn(thr_bps, 0) if thr_bps is not None else 'KHÔNG ĐỌC ĐƯỢC'} "
             f"bps (1 bước giá), bền ⇒ rollback fill_timing HYBRID; đo mỗi ~10 phiên live có lệnh MUA hybrid — "
             f"{thr_cite}, điều kiện ghi ở " + ct.cite(reg, r'"rollback_condition"')]
    try:
        with open(os.path.join(kb_dir, "paper_programs_registry.json"), encoding="utf-8") as f:
            j = json.load(f)
        progs = j.get("programs") if isinstance(j, dict) else j
        p = next((x for x in progs or [] if isinstance(x, dict) and x.get("id") == "fill_timing"), None)
        if p is None:
            raise ValueError("registry không có chương trình id=fill_timing")
        lm = (p.get("progress") or {}).get("live_monitoring")
        if not isinstance(lm, dict):
            raise ValueError("fill_timing.progress.live_monitoring không có trong registry")
        since, target, cnt = str(lm.get("since")), lm.get("target_sessions"), lm.get("count_current_measured")
        notes = sorted(k[5:] for k in lm if re.fullmatch(r"note_\d{4}-\d{2}-\d{2}", k))
        c.as_of = (f"bộ đếm registry ghi {notes[-1]}" if notes else f"bộ đếm registry mở {since}, chưa ghi lần đếm nào")
        per = {a: live_buy_sessions(data_dir, a, since) for a in LIVE_ACCOUNTS}
        union = sorted(set().union(*per.values()))
        c.stale = _isnum(cnt) and len(union) != int(cnt)
        c.stale_why = (f"registry ghi {cnt} phiên, journal đếm được {len(union)} phiên từ {since}"
                       + (f" — ĐÃ ĐỦ {target} phiên, đến hạn đo" if _isnum(target) and len(union) >= target else ""))
        m = re.search(r"fill-vs-open hybrid = ([+\-−]?[0-9]+,[0-9]+) bps \(se ([0-9]+,[0-9]+), n=(\d+)\)",
                      str(p.get("review_short", "")))
        md = re.search(r"\d{4}-\d{2}-\d{2}", str(p.get("status", "")))
        paper = (f"{esc(m.group(1))} bps (sai số chuẩn {esc(m.group(2))}; n = {esc(m.group(3))} phiên)" if m
                 else "không đọc được từ registry")
        rows = [["Số đo LIVE gần nhất", "<b>chưa có</b>" if not lm.get("measured_sessions") else
                 f"{len(lm['measured_sessions'])} phiên đã đo — xem registry", "chưa lần đo live nào được ghi vào registry"
                 if not lm.get("measured_sessions") else esc(", ".join(map(str, lm["measured_sessions"])))],
                ["Bộ đếm ghi trong registry", f"{esc(cnt)}/{esc(target)} phiên", f"từ {esc(since)}; lần đếm ghi gần nhất "
                 + (notes[-1] if notes else "—")]]
        for a in LIVE_ACCOUNTS:
            rows.append([f"Phiên live có lệnh MUA bot đặt — {a}", f"{len(per[a])}", esc(", ".join(per[a]) or "—")])
        rows += [["Hợp hai tài khoản (số phiên khác nhau)", f"<b>{len(union)}/{esc(target)}</b>", esc(", ".join(union) or "—")],
                 ["Số đo gần nhất trên PAPER (tài khoản main, không phải live)", paper,
                  f"ghi lúc tốt nghiệp {md.group(0) if md else '—'}; dương = mua ĐẮT hơn giá mở cửa"]]
        c.body = (
            '<p><b>Chưa có nguồn định kỳ</b> cho trượt giá của tài khoản live. '
            f'<code>{eqr}</code> là công cụ chạy tay; lượt chạy tự động hằng ngày gọi nó không kèm '
            f'<code>--account</code> nên LOẠI mọi tài khoản live — ' + ct.cite(eqr, r"EXCLUDE every configured LIVE account")
            + '.</p>' + _table(["Chỉ số", "Giá trị", "Ghi chú"], rows, cls="wide")
            + '<p class="muted">Bộ đếm phiên lấy từ journal (lệnh bot ĐẶT, trừ corp-action) — là số phiên, không phải '
              'giá khớp. Số trượt giá khi đo phải lấy giá khớp từ xác nhận của broker, lọc theo từng tài khoản.</p>')
    except Exception as e:
        c.error = _err(e)
    return c


# ───────────────────────────────────────────────────────────────── nguồn sống (tiêm được để test)
def default_providers(wc_root):
    """Mọi lời gọi module production nằm ở đây — CHỈ import/đọc. Import trễ để một module hỏng
    chỉ làm hỏng đúng ô của nó."""
    if wc_root not in sys.path:
        sys.path.insert(0, wc_root)

    def gated_state(start, end):
        import macro_state_live as m
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            df = m.get_gated_state(start, end, alert=False)   # alert=False: không bắn Telegram
        return df, buf.getvalue()

    def dt_clock():
        import dna_report
        return dna_report.get_dt_gate_clock()

    def dt_line():
        import dna_report
        return dna_report.build_dt_gate_line(html=False)

    def value_radar():
        import value_radar as vr
        return vr.value_radar_now(update=False)               # update=False: không ghi đè cache

    def killswitch():
        import deposit_rate_vn
        return deposit_rate_vn.macro_killswitch_a_status()

    def big4_rate():
        import deposit_rate_vn
        return deposit_rate_vn.current_deposit_rate()

    def breadth(start, end):
        import macro_state_live as m
        from simulate_holistic_nav import bq
        if m.BREADTH_SOURCE != "pit":
            raise RuntimeError(f"macro_state_live.BREADTH_SOURCE={m.BREADTH_SOURCE!r} — ô này chỉ nhận 'pit'")
        with contextlib.redirect_stdout(io.StringIO()):
            return bq(m._breadth_sql(start, end))

    def capit():
        import edge_health_monitor
        return edge_health_monitor.capit_edge_health()

    def neg_streak(d):
        import edge_health_monitor
        return edge_health_monitor.neg_month_streak(d, "known_date")

    def unit_ledger(account):
        bin_dir = os.path.dirname(os.path.abspath(__file__))
        if bin_dir not in sys.path:
            sys.path.insert(0, bin_dir)
        import account_cash_flows as acf
        import nav_unit_ledger as nul
        rows = nul.load_nav_history(account)
        flows = acf.load_flows(account, require_file=True)     # thiếu sổ dòng tiền ⇒ TỪ CHỐI, không đoán []
        ledger, info = nul.build_ledger(rows, flows, *nul._inception_baseline(rows, nul.load_inception(account)))
        return dict(ledger=ledger, pending=info["pending"], dropped=info["dropped"],
                    jumps=acf.unexplained_nav_jumps(rows, flows), block_pct=acf.NAV_JUMP_BLOCK_PCT)

    return dict(gated_state=gated_state, dt_clock=dt_clock, dt_line=dt_line, value_radar=value_radar,
                killswitch=killswitch, big4_rate=big4_rate, breadth=breadth, capit=capit,
                neg_streak=neg_streak, unit_ledger=unit_ledger)


# ───────────────────────────────────────────────────────────────── trang
CSS = """
:root{color-scheme:light dark;--bg:#f9f9f7;--card:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--mut:#898781;
--line:#e1e0d9;--axis:#c3c2b7;--s1:#2a78d6;--good:#0ca30c;--serious:#ec835a;--crit:#d03b3b;--warn:#fab219;
--st1:#d03b3b;--st2:#ec835a;--st3:#b5b4ab;--st4:#86b6ef;--st5:#256abf}
@media (prefers-color-scheme:dark){:root{--bg:#0d0d0d;--card:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mut:#898781;
--line:#2c2c2a;--axis:#383835;--s1:#3987e5;--st3:#6b6a65;--st4:#6da7ec;--st5:#3987e5}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
-webkit-text-size-adjust:100%}
main{max-width:720px;margin:0 auto;padding:12px}
h1{font-size:1.3rem;line-height:1.3;margin:.4em 0}
h2{font-size:1.1rem;margin:1.6em 0 .2em;padding-top:.6em;border-top:2px solid var(--axis)}
h3{font-size:1.02rem;margin:0 0 .3em}
h4{font-size:.98rem;margin:.2em 0}
p{margin:.45em 0}
code{font:.86em ui-monospace,Menlo,Consolas,monospace;overflow-wrap:anywhere}
.cell,.top{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;margin:12px 0}
.meta,.muted,.cap,.bk,.legend{color:var(--ink2);font-size:.9rem}
.big{font-size:1.5rem;font-weight:700;margin:.2em 0}
.lagnote{border-left:4px solid var(--axis);padding-left:10px}
.thr{margin-top:10px;padding:10px;border:1px dashed var(--axis);border-radius:8px;font-size:.93rem}
.thr ul{margin:.3em 0 0;padding-left:1.15em}.thr li{margin:.35em 0}
.cite{color:var(--ink2)}.cite.miss{color:var(--crit);font-weight:700}
.bdg{display:inline-block;font-size:.72rem;font-weight:700;padding:1px 7px;border-radius:99px;
border:1.5px solid var(--ink2);margin-left:4px;vertical-align:middle;white-space:nowrap}
.bdg.stale{border-style:dashed}.bdg.nodata{background:var(--ink);color:var(--card);border-color:var(--ink)}
.nodata-msg{border:1.5px solid var(--ink2);border-radius:8px;padding:8px}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:.5em 0;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:.9rem;font-variant-numeric:tabular-nums}
table.wide{min-width:640px}
th,td{padding:6px 8px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--ink2);font-weight:600;white-space:nowrap}
tr:last-child td{border-bottom:0}
.sig{border-top:1px solid var(--line);padding-top:10px;margin-top:12px}
.vd{display:inline-block;padding:0 6px;border-radius:6px;border:1px solid var(--axis);font-size:.82rem;font-weight:600;white-space:nowrap}
.vd.v-red{border:2px solid var(--crit)}.vd.v-red::before{content:"● ";color:var(--crit)}
.vd.v-orange{border:2px solid var(--serious)}.vd.v-orange::before{content:"● ";color:var(--serious)}
.vd.v-green{border:2px solid var(--good)}.vd.v-green::before{content:"● ";color:var(--good)}
svg.spark{display:block;width:100%;height:auto;max-height:90px}
.sl{fill:none;stroke:var(--s1);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.sd{fill:var(--s1);stroke:var(--card);stroke-width:2}.zero{stroke:var(--axis);stroke-width:1}
svg.strip{display:block;width:100%;height:26px;border-radius:4px}
.st1{fill:var(--st1)}.st2{fill:var(--st2)}.st3{fill:var(--st3)}.st4{fill:var(--st4)}.st5{fill:var(--st5)}
.lg{display:inline-block;margin-right:10px;white-space:nowrap}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:4px;vertical-align:-1px}
i.sw.st1{background:var(--st1)}i.sw.st2{background:var(--st2)}i.sw.st3{background:var(--st3)}
i.sw.st4{background:var(--st4)}i.sw.st5{background:var(--st5)}
pre.wrap{white-space:pre-wrap;overflow-wrap:anywhere;font:.86rem/1.45 ui-monospace,Menlo,Consolas,monospace;
background:var(--bg);border-radius:8px;padding:8px;margin:.4em 0}
.top ul{margin:.3em 0;padding-left:1.15em}.top li{margin:.3em 0}
footer{color:var(--ink2);font-size:.85rem;margin:20px 0}
"""


def build_cells(now, wc_root=WC_ROOT, data_dir=None, kb_dir=None, providers=None, citer=None):
    data_dir = data_dir or os.path.join(wc_root, "data")
    kb_dir = kb_dir or os.path.join(wc_root, "mike", "kb")
    ct = citer or Citer(wc_root)
    prov = providers if providers is not None else default_providers(wc_root)
    cells = [
        cell_edge_ic(data_dir, ct, now),
        cell_edge_lag(data_dir, ct, now, prov),
        cell_edge_capit(data_dir, ct, now, prov),
        cell_book_map(ct, now, wc_root),
        cell_env_dt5g(ct, now, prov),
        cell_env_breadth(ct, now, prov),
        cell_env_value(ct, now, prov),
        cell_env_rates(data_dir, ct, now, prov),
        cell_env_structural(kb_dir, ct, now),
    ]
    dd = [cell_live_dd(a, data_dir, ct, now, prov) for a in LIVE_ACCOUNTS]
    # §12: hai tài khoản mà ra BẢNG SỐ giống hệt nhau = gần như chắc chắn đọc chung một nguồn không lọc.
    ok = [c for c in dd if c.error is None]
    if len(ok) > 1 and len({re.search(r"<table.*?</table>", c.body, re.S).group(0) for c in ok}) == 1:
        for c in ok:
            c.error = "hai tài khoản ra số giống hệt nhau — nghi đọc chung một nguồn không lọc tài khoản; không công bố"
    cells += dd + [cell_live_slippage(data_dir, kb_dir, ct, now)]
    return cells, ct


def render_page(cells, now, cite_misses=()):
    items = []
    for c in cells:
        for t in c.touched:
            items.append(f"<li><b>Chạm ngưỡng</b> — {esc(c.title)}: {esc(t)}</li>")
    for c in cells:
        if c.error is not None:
            items.append(f"<li><b>{NO_DATA}</b> — {esc(c.title)}</li>")
        elif c.stale is True:
            items.append(f"<li><b>Nguồn CŨ</b> — {esc(c.title)}: {esc(c.stale_why)}</li>")
    top = ("<ul>" + "".join(items) + "</ul>") if items else "<p>Không ô nào chạm ngưỡng.</p>"
    t1 = "".join(render_cell(c) for c in cells if c.tier == 1)
    t2 = "".join(render_cell(c) for c in cells if c.tier == 2)
    t3 = "".join(render_cell(c) for c in cells if c.tier == 3)
    miss = ""
    if cite_misses:
        miss = ("<p><b>Trích dẫn không định vị được</b> (file nguồn đã đổi — cần cập nhật neo): "
                + "; ".join(esc(m) for m in cite_misses) + "</p>")
    return (
        '<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Độ phù hợp của chiến lược với thị trường — {now:%Y-%m-%d}</title>'
        f'<style>{CSS}</style></head><body><main>'
        '<h1>Độ phù hợp của chiến lược với thị trường hiện hành</h1>'
        f'<p class="meta">Sinh lúc <b>{now:%Y-%m-%d %H:%M} ICT</b> (múi giờ Asia/Ho_Chi_Minh). '
        'Trang CHẨN ĐOÁN: không có điểm tổng hợp, không phát tín hiệu, không in số tài khoản hay số dư bằng tiền. '
        'Bốn lần thử biến các số đo này thành luật tự điều chỉnh đều đã bị bác.</p>'
        f'<div class="top"><h3>Hôm nay có gì đáng chú ý</h3>{top}'
        '<p class="muted">Chỉ liệt kê ô có ngưỡng thật trong code/KB đang bị chạm, hoặc nguồn đang cũ/thiếu.</p></div>'
        f'<h2>Tầng 1 — Độ khớp của edge</h2>{t1}'
        f'<h2>Tầng 2 — Môi trường</h2>{t2}'
        f'<h2>Tầng 3 — Thực tế so với kỳ vọng</h2>{t3}'
        f'<footer>{miss}<p>Huy hiệu CŨ đếm ngày Thứ 2–6, <b>không trừ nghỉ lễ</b> — sau kỳ nghỉ dài có thể báo CŨ giả. '
        'Màu ở nhãn edge chỉ theo ba nhãn mà <code>edge_health_monitor.py</code> tự gắn màu (FLIPPED / DECAYED / STRENGTH); '
        'màu dải DT5G chỉ để phân biệt năm trạng thái. Sinh bởi <code>mike/bin/strategy_fit_dashboard.py</code>.</p></footer>'
        '</main></body></html>')


# ───────────────────────────────────────────────────────────────── bất biến của trang
_VOID = {"meta", "br", "line", "polyline", "circle", "img", "hr", "input", "link"}


class _Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems, self.cells = [], [], {}
        self._cell, self._in_thr, self._in_meta = None, 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag == "section" and "cell" in cls:
            self._cell = a.get("id") or "?"
            self.cells[self._cell] = {"asof": a.get("data-asof") or "", "thr": "", "meta": "", "thr_cite": 0, "thr_li": 0, "li_cite": []}
        if self._cell:
            if self._in_thr:
                self._in_thr += tag not in _VOID
                d = self.cells[self._cell]
                if tag == "li":
                    d["thr_li"] += 1; d["li_cite"].append(0)
                if tag == "code" and "cite" in cls and "miss" not in cls:
                    d["thr_cite"] += 1
                    if d["li_cite"]:
                        d["li_cite"][-1] += 1
            elif tag == "div" and "thr" in cls:
                self._in_thr = 1
            if self._in_meta:
                self._in_meta += tag not in _VOID
            elif tag == "p" and "meta" in cls:
                self._in_meta = 1
        if tag not in _VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        if tag not in _VOID:
            self.handle_starttag(tag, attrs); self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in _VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.problems.append(f"thẻ đóng </{tag}> không khớp (đang mở: {self.stack[-1] if self.stack else 'rỗng'})")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()
        if self._in_thr:
            self._in_thr -= 1
        if self._in_meta:
            self._in_meta -= 1
        if tag == "section":
            self._cell = None

    def handle_data(self, data):
        if self._cell and self._in_thr:
            self.cells[self._cell]["thr"] += data
        if self._cell and self._in_meta:
            self.cells[self._cell]["meta"] += data


def validate_html(page, expected=CELL_KEYS):
    """Bất biến của trang → list vi phạm (rỗng = đạt)."""
    p = _Audit()
    p.feed(page); p.close()
    out = list(p.problems)
    if p.stack:
        out.append(f"thẻ chưa đóng: {p.stack}")
    if re.search(r"https?://", page):
        out.append("có chuỗi http(s):// — trang phải tự chứa")
    if "profit_" in page:
        out.append("xuất hiện chuỗi profit_ (cột nhìn trước)")
    n = len(page.encode("utf-8"))
    if n >= MAX_BYTES:
        out.append(f"file {n} byte ≥ {MAX_BYTES}")
    for k in expected:
        c = p.cells.get(k)
        if c is None:
            out.append(f"thiếu ô {k}"); continue
        if not c["asof"].strip():
            out.append(f"ô {k}: thiếu as_of")
        if "Nguồn:" not in c["meta"] or "Dữ liệu tới:" not in c["meta"]:
            out.append(f"ô {k}: thiếu dòng nguồn / ngày dữ liệu")
        want = THR_COUNT.get(k)
        if "Ngưỡng hành động" not in c["thr"]:
            out.append(f"ô {k}: thiếu dòng «Ngưỡng hành động»")
        elif want == 0:
            if DESCRIPTIVE not in c["thr"] or c["thr_li"]:
                out.append(f"ô {k}: ô mô tả phải ghi đúng câu «{DESCRIPTIVE}»")
        else:
            if DESCRIPTIVE in c["thr"]:
                out.append(f"ô {k}: ô có ngưỡng thật lại ghi «{DESCRIPTIVE}»")
            if want is not None and c["thr_li"] != want:
                out.append(f"ô {k}: có {c['thr_li']} dòng ngưỡng, bảng THR_COUNT khai {want}")
            if any(n == 0 for n in c["li_cite"]) or c["thr_cite"] == 0:
                out.append(f"ô {k}: có dòng ngưỡng không trích được file:dòng")
    return out


def out_path(now, out_dir):
    return os.path.join(out_dir, f"strategy_fit_{now:%Y-%m-%d}.html")


def run(now, out_dir, **build_kw):
    """Dựng + kiểm bất biến + ghi file. → (rc, path|None)."""
    cells, ct = build_cells(now, **build_kw)
    page = render_page(cells, now, ct.misses)
    for c in cells:
        print(f"[ô] {c.key:15s} {'LỖI: ' + c.error if c.error is not None else 'ok'}"
              f"{' | CŨ' if c.stale is True else ''}{' | CHẠM: ' + str(len(c.touched)) if c.touched else ''}")
    for m in ct.misses:
        print(f"[trích dẫn] KHÔNG ĐỊNH VỊ ĐƯỢC: {m}", file=sys.stderr)
    bad = validate_html(page)
    if bad:
        for b in bad:
            print(f"[BẤT BIẾN VỠ] {b}", file=sys.stderr)
        return 4, None
    # book_map chỉ đọc code (không có nguồn dữ liệu để hỏng) nên không tính là "dựng được ô".
    if all(c.error is not None for c in cells if c.key != "book_map"):
        print("Không dựng được ô dữ liệu nào — không ghi file.", file=sys.stderr)
        return 1, None
    os.makedirs(out_dir, exist_ok=True)
    path = out_path(now, out_dir)
    tmp = f"{path}.{os.getpid()}.tmp"      # riêng từng tiến trình: hai lượt sinh song song không giẫm nhau
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(page)
    os.replace(tmp, path)
    print(f"{len(page.encode('utf-8'))} byte")
    print(path)
    return 0, path


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out_dir = os.path.join(WC_ROOT, "mike", "reports", "dashboard")
    if "--out-dir" in argv:
        out_dir = argv[argv.index("--out-dir") + 1]
    return run(datetime.now(ICT), out_dir)[0]


if __name__ == "__main__":
    sys.exit(main())
