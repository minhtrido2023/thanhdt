#!/usr/bin/env python3
"""Paper Programs Daily Report — báo cáo hợp nhất MỌI chương trình paper-trading active.

Registry-driven: danh sách chương trình ở mike/kb/paper_programs_registry.json — thêm sleeve
mới = thêm entry, không sửa code này.

Cấu trúc báo cáo (redesign 2026-07-31, chuẩn báo cáo đầu tư: executive summary → chi tiết →
methodology tách riêng):
  1. Header + dòng CẢNH BÁO tổng (nếu có chương trình cần chú ý)
  2. TỔNG QUAN — mỗi chương trình 1 dòng: badge · tên · số hôm nay · giao dịch hôm nay
  3. Chi tiết từng chương trình: headline (hôm nay/lũy kế/vs benchmark) · GIAO DỊCH HÔM NAY
     (bắt buộc, không im lặng) · gate badge · probe body · nguồn
  4. Charter (mục đích + phương pháp + tiêu chí nghiệm thu đầy đủ) KHÔNG paste vào report —
     tự sinh ra mike/kb/paper_programs_charter/<id>.md, report chỉ link tới.

Nguyên tắc trung thực: số nào không trace được về file thật → 'n/a + lý do'. Không bao giờ
ghi 'không có giao dịch' khi thực ra là 'không đo được' — hai câu đó khác nhau. Một sleeve lỗi
không giết cả report (section đó ghi lỗi, exit vẫn 0).

Usage: paper_programs_daily_report.py [--date YYYY-MM-DD] [--registry PATH] [--no-state]
In markdown ra stdout. Luôn exit 0 (trừ khi chính registry không đọc nổi — vẫn in report
tối thiểu nói rõ điều đó, vẫn exit 0 để cron không rơi im lặng).
"""
import argparse
import csv
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
DEFAULT_REGISTRY = os.path.join(WC_ROOT, "mike/kb/paper_programs_registry.json")
CHARTER_DIR = os.path.join(WC_ROOT, "mike/kb/paper_programs_charter")
CHARTER_REL = "mike/kb/paper_programs_charter"
STATE_PATH = os.path.join(WC_ROOT, "data/paper_report_state.json")
STATUS_EMOJI = {"pass": "✅", "fail": "❌", "pending": "⏳", "manual": "🔎"}
BADGE = {"green": "✅ GREEN", "watch": "⏳ WATCH", "red": "🔴 RED", "paused": "⏸ PAUSED"}


def weekdays_between(d0, d1):
    """Số ngày T2-T6 trong [d0, d1] (ước tính phiên, chưa trừ nghỉ lễ)."""
    if d1 < d0:
        return 0
    n, d = 0, d0
    while d <= d1:
        if d.weekday() < 5:
            n += 1
        d += dt.timedelta(days=1)
    return n


def _journal_has_real_activity(path):
    """True nếu journal có ít nhất 1 dòng PLACE/FILL/DONE — phân biệt phiên THẬT có đặt
    lệnh với phiên chỉ toàn GHOST_ORDER/WAIT_QUOTA/WAIT_CASH (executor chạy nhưng làm 0 việc,
    vd sự cố TZ 2026-07-08/09: journal tồn tại nhưng chỉ có GHOST_ORDER, 0 lệnh thật)."""
    try:
        with open(path, encoding="utf-8") as f:
            return any(r.get("event") in ("PLACE", "FILL", "DONE")
                       for r in csv.DictReader(f))
    except OSError:
        return False


def count_evidence_sessions(account, count_from=None):
    """Số phiên executor CÓ EVIDENCE = số file journal exec_<account>_<date>_journal.csv
    MÀ THẬT SỰ có hoạt động đặt lệnh (PLACE/FILL/DONE) — không chỉ file tồn tại (loại fixture
    2099; lọc date >= count_from nếu có). Một phiên bị ghost-guard/TZ-bug chặn hết (0 lệnh
    thật) không được tính, dù journal file có tồn tại — xem _journal_has_real_activity."""
    pattern = os.path.join(WC_ROOT, f"data/execution_logs/exec_{account}_*_journal.csv")
    dates = []
    for f in glob.glob(pattern):
        d = os.path.basename(f)[len(f"exec_{account}_"):-len("_journal.csv")]
        if d.startswith("2099"):
            continue
        if count_from and d < count_from:
            continue
        if not _journal_has_real_activity(f):
            continue
        dates.append(d)
    return sorted(dates)


def progress_short(prog, today):
    """Tiến độ NGẮN 1 mệnh đề (mốc nghiệm thu đầy đủ nằm ở charter, không lặp mỗi ngày)."""
    pr = prog.get("progress") or {}
    if pr.get("mode") == "evidence_sessions":
        dates = count_evidence_sessions(pr["account"], pr.get("count_from"))
        return f"{len(dates)}/{pr.get('target_sessions')} phiên evidence"
    start, end = prog.get("start"), prog.get("end")
    if not start:
        return "chưa xác định ngày start"
    n = weekdays_between(dt.date.fromisoformat(start), today)
    if end:
        m = weekdays_between(dt.date.fromisoformat(start), dt.date.fromisoformat(end))
        return f"phiên ~{n}/{m} ({start}→{end})"
    return f"phiên ~{n} từ {start}"


def review_short(prog):
    """Mốc nghiệm thu 1 dòng. Ưu tiên field review_short; nếu không có thì cắt end_or_trigger."""
    s = prog.get("review_short")
    if s:
        return s
    s = (prog.get("end_or_trigger") or "").strip()
    if not s:
        return "chưa khai báo mốc nghiệm thu (registry thiếu `end_or_trigger`)"
    return s if len(s) <= 90 else s[:88].rstrip() + "…"


# ---------------- probes ----------------

# Generic "did this probe's own output already say something is broken?" scan — added
# 2026-07-30 after a user report that paper reports "don't work" traced back to a real
# outage (PaperBroker.place_order crash, 386 FAIL/day) that WAS visible in the section 4 body
# the whole time as "journal FAIL/ERROR events: 431", just buried in a long wall of text no
# one was scanning for it. Matches the "<label>: <positive count>" convention several probe
# scripts already use (execution_quality_review.py's "rejected/failed orders: N" / "journal
# FAIL/ERROR events: N") plus a bare Python crash trace — NOT a semantic understanding of any
# one script, just a cheap textual tripwire so a real problem can't scroll by unnoticed.
_ATTENTION_RE = re.compile(r"^.*\b(FAIL|ERROR|Reject(?:ed)?)\b[^\n:]*:\s*([1-9]\d*)\s*$", re.MULTILINE)

# Probe scripts viết cho CLI riêng thường tự in checklist GO/NO-GO tiếng Anh của chúng —
# trùng nguyên khối với gate_criteria tiếng Việt của registry mà render này đã in. Cắt bản EN,
# giữ bản VI (thống nhất ngôn ngữ với phần còn lại của report).
_EN_CHECKLIST_RE = re.compile(r"^=+\s*GO/NO-GO CHECKLIST.*?(?=^=|\Z)", re.MULTILINE | re.DOTALL)


def _attention_flags(out, prog):
    """Danh sách cờ cảnh báo + ngữ cảnh mức độ nghiêm trọng (registry `attention_notes`).

    Con số cảnh báo KHÔNG BAO GIỜ được để trần: cờ nào không khớp note nào trong registry sẽ
    mang note=None và render bắt buộc in dòng 'CHƯA CÓ GIẢI THÍCH' + đẩy badge sang RED."""
    notes = prog.get("attention_notes") or []
    raw = []
    if "Traceback (most recent call last)" in out:
        raw.append("Python traceback trong output")
    for m in _ATTENTION_RE.finditer(out):
        raw.append(m.group(0).strip())
    return [_flag(text, notes) for text in raw]


def _flag(text, notes):
    """1 cờ cảnh báo + note giải thích khớp từ registry (không khớp ⇒ note=None ⇒ RED)."""
    hit = next((n for n in notes if n.get("match") and n["match"] in text), None)
    return {"text": text, "note": hit.get("note") if hit else None,
            "severity": (hit or {}).get("severity", "red")}


def probe_command(probe, prog):
    """Chạy 1 lệnh trong WC_ROOT, trả stdout (cắt max_chars). Non-zero exit vẫn trả output."""
    cmd = probe["cmd"]
    timeout = probe.get("timeout", 120)
    max_chars = probe.get("max_chars", 1400)
    r = subprocess.run(cmd, cwd=WC_ROOT, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout or "").strip()
    if not out:
        out = (r.stderr or "").strip()[:400] or "(không có output)"
    flags = _attention_flags(out, prog)  # quét cờ trên output GỐC, trước mọi cắt gọt
    raw_out = out
    trailer = []
    stripped = _EN_CHECKLIST_RE.sub("", out).rstrip()
    if stripped != out.rstrip():
        trailer.append("_(checklist GO/NO-GO tiếng Anh của probe đã lược — trùng gate tiếng Việt, "
                       "xem charter)_")
    # drop_regex: bỏ những dòng phụ lục dài của probe không thuộc "hôm nay thế nào" (vd khối
    # DCF informational của DC-book) — cắt ở tầng render, KHÔNG sửa probe script.
    drops = probe.get("drop_regex") or []
    if drops:
        src = stripped.splitlines()
        keep = [l for l in src if not any(re.search(d, l) for d in drops)]
        if len(keep) != len(src):
            trailer.append(f"_(lược {len(src) - len(keep)} dòng phụ lục của probe — xem nguồn nếu cần)_")
        # bỏ dòng giữa khối để lại chuỗi dòng trống — gộp lại, không để lỗ hổng trong report
        collapsed, prev_blank = [], False
        for l in keep:
            blank = not l.strip()
            if not (blank and prev_blank):
                collapsed.append(l)
            prev_blank = blank
        stripped = "\n".join(collapsed).strip()
    out = stripped
    if len(out) > max_chars:
        out = out[:max_chars] + f"\n… (cắt bớt, xem nguồn để đủ; exit={r.returncode})"
    if r.returncode != 0:
        trailer.append(f"⚠️ lệnh exit={r.returncode} — output ở trên có thể không đầy đủ")
    # `raw` = output GỐC trước mọi cắt gọt. headline() khớp regex trên đây (không phải body đã
    # cắt) vì một dòng có thể vừa là nguồn headline vừa bị drop_regex bỏ khỏi phần chi tiết cho
    # khỏi lặp — cùng lý do _attention_flags quét raw ở trên.
    return {"body": "\n".join([out] + trailer), "flags": flags, "raw": raw_out}


def probe_journal_scan(probe, prog, today):
    """Scan exec journal của 1 account: đếm phiên đã chạy + marker hits (tổng & hôm nay)."""
    account = probe["account"]
    markers = probe.get("markers", [])
    pattern = os.path.join(WC_ROOT, f"data/execution_logs/exec_{account}_*_journal.csv")
    files = [f for f in sorted(glob.glob(pattern)) if "2099" not in f]  # loại fixture selfcheck
    if not files:
        return {"headline": f"0 phiên journal trên `{account}` — chưa tích lũy evidence nào",
                "body": (f"- Không có file khớp `exec_{account}_*_journal.csv` → flag bật nhưng "
                         f"chỉ có tác dụng khi executor thực sự chạy phiên trên account này")}
    total_hits, today_hits, today_str = {m: 0 for m in markers}, {m: 0 for m in markers}, today.isoformat()
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                for m in markers:
                    if m in line:
                        total_hits[m] += 1
                        if line.startswith(today_str):
                            today_hits[m] += 1
    last = os.path.basename(files[-1])[len(f"exec_{account}_"):-len("_journal.csv")]
    head = f"{len(files)} phiên journal `{account}` (gần nhất {last})"
    body, flags = "", []
    if markers:
        head += f" · marker hôm nay **{sum(today_hits.values())}** / lũy kế **{sum(total_hits.values())}**"
        body = "- Marker: " + ", ".join(f"{m}={total_hits[m]}" for m in markers)
        # Marker bắn HÔM NAY = sự kiện cần người đọc, không phải con số trần: đẩy qua đúng cơ chế
        # attention_notes như probe_command (chưa có giải thích trong registry ⇒ badge RED).
        # Chỉ tính hits HÔM NAY — lũy kế sẽ kêu mãi mãi sau 1 lần bắn.
        notes = prog.get("attention_notes") or []
        flags = [_flag(f"marker {m}={today_hits[m]} bắn hôm nay", notes)
                 for m in markers if today_hits[m]]
    return {"headline": head, "body": body, "flags": flags}


def probe_alphalens(probe, prog, today):
    """Đọc alphalens_paper.json + giá close mới nhất từ BQ cache → return vs benchmark."""
    import duckdb  # sẵn trong env papertrade
    jpath = os.path.join(WC_ROOT, probe["json_path"])
    ppath = os.path.join(WC_ROOT, probe["prices_parquet"])
    with open(jpath, encoding="utf-8") as f:
        al = json.load(f)
    meta, positions = al["meta"], al["positions"]
    tickers = [p["ticker"] for p in positions]
    con = duckdb.connect()
    con.execute("PRAGMA threads=1")
    inlist = ",".join(f"'{t}'" for t in tickers)
    rows = con.execute(
        f"SELECT ticker, time, Close, VNINDEX FROM '{ppath}' WHERE ticker IN ({inlist}) "
        f"QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC)=1").fetchall()
    px = {r[0]: (r[1], r[2], r[3]) for r in rows}
    if not px:
        return {"body": f"n/a — không đọc được giá từ {probe['prices_parquet']}"}
    asof = max(r[0] for r in px.values())
    vnindex_now = next(r[2] for r in px.values() if r[2] is not None)
    bench_entry = meta["benchmark_entry"]
    bench_ret = (vnindex_now / bench_entry - 1) * 100
    lines, port_ret = [], 0.0
    for p in positions:
        t = p["ticker"]
        if t not in px:
            lines.append(f"  • {t}: n/a — thiếu giá trong cache")
            continue
        close = px[t][1]
        ret = (close / p["entry_price"] - 1) * 100
        port_ret += p.get("weight_paper", 1.0 / len(positions)) * ret
        lines.append(f"  • {t}: {p['entry_price']:,.0f} → {close:,.0f} = **{ret:+.2f}%** "
                     f"(entry {p['entry_date']}, {p['lens']})")
    excess = port_ret - bench_ret
    return {"headline": (f"EW **{port_ret:+.2f}%** vs VNINDEX {bench_ret:+.2f}% → "
                         f"**excess {excess:+.2f}pp** (MTM as-of {asof})"),
            "body": "- Vị thế (MTM as-of " + str(asof) + ", BQ cache close phiên gần nhất):\n"
                    + "\n".join(lines)
                    + f"\n- VNINDEX {bench_entry:,.2f} → {vnindex_now:,.2f}"}


PROBES = {
    "command": lambda probe, prog, today: probe_command(probe, prog),
    "journal_scan": probe_journal_scan,
    "alphalens": probe_alphalens,
}


# ---------------- giao dịch hôm nay ----------------

def _fmt_row(template, row):
    """Format 1 dòng CSV theo template registry; số chuyển float được thì chuyển (để .2f/.2%
    dùng được), không thì giữ nguyên chuỗi."""
    vals = {}
    for k, v in row.items():
        if k is None:
            continue
        try:
            vals[k] = float(v)
        except (TypeError, ValueError):
            vals[k] = v
    return template.format(**vals)


def _csv_rows(path):
    with open(os.path.join(WC_ROOT, path), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _journal_activity(spec, today):
    """Giao dịch hôm nay đọc thẳng exec journal (nguồn chuẩn tắc của account paper đó)."""
    account = spec["account"]
    path = os.path.join(WC_ROOT,
                        f"data/execution_logs/exec_{account}_{today.isoformat()}_journal.csv")
    rel = os.path.relpath(path, WC_ROOT)
    if not os.path.exists(path):
        return (f"**n/a — chưa đo được** (không có `{rel}`) ⇒ executor chưa chạy/chưa ghi phiên "
                f"hôm nay trên `{account}`, KHÔNG đồng nghĩa 'không có giao dịch'"), "data"
    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="replace")))
    ev = {}
    for r in rows:
        ev[r.get("event")] = ev.get(r.get("event"), 0) + 1
    fills = [r for r in rows if r.get("event") == "FILL"]
    bad = sum(v for k, v in ev.items() if k and ("FAIL" in k or "ERROR" in k))
    no_quote = ev.get("NO_QUOTE", 0)
    if not (ev.get("PLACE") or fills):
        if bad:
            # Phiên "chạy mà không làm được gì" (vd sự cố PaperBroker 2026-07-30: 431 lỗi, 0 lệnh)
            # KHÔNG được hiển thị như một ngày yên ả không có giao dịch.
            return (f"🔴 **0 lệnh đặt / {bad} sự kiện LỖI** — executor có chạy nhưng không đặt "
                    f"hay khớp được lệnh nào ⇒ MẤT phiên evidence, không phải 'ngày yên ả' · "
                    f"nguồn `{rel}`"), "error"
        if no_quote:
            # NO_QUOTE không mang chữ FAIL/ERROR nên lọt check `bad` ở trên, nhưng vẫn là "không
            # quan sát được", không phải "quan sát được và thấy yên ả" — 2 việc khác nhau
            # (quant-skeptic verify_20260731_051111, repro: mất quote toàn phiên trông giống hệt
            # ngày calm thật nếu không tách riêng).
            return (f"🔴 **0 lệnh đặt / {no_quote} lần thiếu quote (NO_QUOTE)** — executor chạy "
                    f"nhưng KHÔNG quan sát được giá để hành động ⇒ mất phiên evidence, không phải "
                    f"'ngày yên ả' · nguồn `{rel}`"), "error"
        return (f"**Không có giao dịch** — journal `{rel}` có {len(rows)} dòng nhưng 0 lệnh đặt "
                f"(0 PLACE / 0 FILL / 0 NO_QUOTE)"), None

    def _num(x):
        try:
            return f"{float(x):,.0f}"
        except (TypeError, ValueError):
            return str(x)
    detail = " · ".join(
        f"{(r.get('side') or '?').upper()} {r.get('ticker')} {_num(r.get('qty'))}@{_num(r.get('price'))}"
        for r in fills[:6])
    if len(fills) > 6:
        detail += f" · …(+{len(fills) - 6})"
    return (f"**{len(fills)} lệnh khớp** — {detail or '(chưa khớp)'} "
            f"[đặt {ev.get('PLACE', 0)} · khớp {len(fills)} · lỗi {bad}] · nguồn `{rel}`",
            "error" if bad else None)


def _prev_trading_day(d, n):
    """Lùi n phiên T2-T6 (KHÔNG trừ nghỉ lễ — ngày lễ sẽ hiện 'chưa có dòng', đúng tinh thần
    thà báo thừa còn hơn im lặng)."""
    while n > 0:
        d -= dt.timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def _csv_row_activity(spec, today):
    """Giao dịch hôm nay đọc 1 dòng CSV state của sleeve.

    `lag_days` = vintage CẤU TRÚC của sleeve đó (vd capitulation đọc BQ lúc 15:30 nên dòng mới
    nhất LUÔN là T-1) — khai báo tường minh để 'trễ theo thiết kế' không bị báo động mỗi ngày,
    mà 'trễ hơn thiết kế' vẫn bị bắt."""
    rows = _csv_rows(spec["path"])
    if not rows:
        return f"**n/a — chưa đo được**: `{spec['path']}` rỗng", "data"
    dcol = spec.get("date_col", "date")
    lag = spec.get("lag_days", 0)
    expect = _prev_trading_day(today, lag)
    ts = expect.isoformat()
    idx = next((i for i, r in enumerate(rows) if str(r.get(dcol, "")).startswith(ts)), None)
    stale = idx is None
    if stale:
        idx = len(rows) - 1
    row = rows[idx]
    vintage = f" (vintage T-{lag} theo thiết kế, phiên {ts})" if lag and not stale else ""
    lead = ""
    zw_gap = None
    zw = spec.get("zero_when")
    if zw:
        col = zw["col"]
        if "zero_value" in zw:
            try:
                lead = ("**Không có giao dịch** — " if float(row[col]) == float(zw["zero_value"])
                        else "**CÓ giao dịch** — ")
            except (TypeError, ValueError, KeyError):
                lead = ""
        elif zw.get("unchanged_vs_prev"):
            # idx==0: dòng ĐẦU TIÊN của chuỗi, KHÔNG có phiên trước để đối chiếu ⇒ không kết luận
            # được gì. Trước đây rơi vào nhánh else và tuyên bố "CÓ giao dịch" từ 0 bằng chứng
            # (ngày đầu của mọi sleeve mới dùng mode này).
            if idx == 0:
                lead, zw_gap = ("**n/a — chưa so sánh được** (dòng đầu tiên của `"
                                f"{spec['path']}`, không có phiên trước để đối chiếu `{col}`) — "), "data"
            else:
                lead = ("**Không có giao dịch** — "
                        if rows[idx - 1].get(col) == row.get(col) else "**CÓ giao dịch** — ")
    try:
        text = _fmt_row(spec["template"], row)
    except (KeyError, ValueError, IndexError) as e:
        return f"**n/a — template lỗi** ({type(e).__name__}: {e}); nguồn `{spec['path']}`", "config"
    if stale:
        # KHÔNG được lấy dòng cũ mà tuyên bố "hôm nay không có giao dịch" — hai việc khác nhau.
        return (f"**n/a — `{spec['path']}` CHƯA có dòng cho phiên {ts}** (pipeline sinh dữ liệu "
                f"chạy 15:05/15:30 ICT; nếu đã quá giờ đó ⇒ pipeline chưa chạy/lỗi) · dòng gần "
                f"nhất {str(row.get(dcol, '?'))[:10]}: {text}"), "data"
    return f"{lead}{text}{vintage} · nguồn `{spec['path']}`", zw_gap


def today_activity(prog, today):
    """Dòng 'Giao dịch hôm nay' — BẮT BUỘC có ở MỌI chương trình.

    Ba trạng thái phân biệt rạch ròi (không được nhập nhèm): CÓ giao dịch / Không có giao dịch /
    n/a chưa đo được. Chương trình không có nhật ký lệnh tách bạch phải khai báo tường minh
    `today_activity.mode = "none_available"` + lý do — thiếu khai báo = badge WATCH, không im lặng.
    """
    spec = prog.get("today_activity")
    if not spec:
        return ("**n/a — registry chưa khai báo `today_activity`** cho chương trình này ⇒ không "
                "biết hôm nay có giao dịch hay không (không được suy diễn là 'không có')"), "config"
    try:
        mode = spec.get("mode")
        if mode == "journal":
            return _journal_activity(spec, today)
        if mode == "csv_row":
            return _csv_row_activity(spec, today)
        if mode == "static":
            return spec["text"], None
        if mode == "none_available":
            return f"**n/a theo thiết kế** — {spec.get('reason', 'không khai báo lý do')}", None
        return f"**n/a — mode `{mode}` không hỗ trợ**", "config"
    except Exception as e:  # nguồn hỏng không được giả vờ là 'không có giao dịch'
        return f"**n/a — lỗi đọc nguồn giao dịch**: {type(e).__name__}: {e}", "error"


# ---------------- headline ----------------

def headline(prog, res, today):
    spec = prog.get("headline")
    try:
        if isinstance(spec, dict) and spec.get("mode") == "csv_row":
            rows = _csv_rows(spec["path"])
            return _fmt_row(spec["template"], rows[-1]) if rows else "n/a — CSV rỗng"
        if isinstance(spec, dict) and spec.get("regex"):
            # DOTALL chỉ khi registry xin (headline gộp nhiều dòng) — mặc định KHÔNG, để `$`
            # dừng ở cuối dòng thay vì nuốt cả khối output.
            fl = re.MULTILINE | (re.DOTALL if spec.get("dotall") else 0)
            m = re.search(spec["regex"], res.get("raw") or res.get("body", ""), fl)
            if m:
                g = m.groups() or (m.group(0),)
                t = spec.get("template")
                return t.format(*g) if t else " · ".join(x.strip() for x in g if x)
    except Exception as e:
        return f"n/a — headline lỗi: {type(e).__name__}: {e}"
    if res.get("headline"):
        return res["headline"]
    first = next((l.strip(" -*#") for l in (res.get("body") or "").splitlines() if l.strip()), "")
    return (first[:150] + "…") if len(first) > 150 else (first or "n/a — probe không có số liệu")


# ---------------- charter (mục đích/phương pháp — tách khỏi report ngày) ----------------

def charter_body(prog, reg_version):
    pid = prog.get("id", "?")
    L = [f"# Charter — {prog.get('name', pid)} (`{pid}`)", "",
         "> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi",
         "> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại",
         "> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng",
         f"> ngày chỉ link tới, không paste lại mỗi ngày. (registry v{reg_version})", "",
         f"- **Người phụ trách (owner):** {prog.get('owner', 'n/a')}",
         f"- **Trạng thái:** {prog.get('status') or 'active'}",
         f"- **Bắt đầu:** {prog.get('start', 'n/a')} · **Kết thúc dự kiến:** {prog.get('end') or 'mở (event-anchored)'}",
         "", "## 🎯 Mục đích", "", prog.get("objective", "n/a"), "",
         "## 📅 Nghiệm thu / mốc kết thúc", "", prog.get("end_or_trigger") or "n/a", ""]
    gates = prog.get("gate_criteria") or []
    if gates:
        L += ["## ✅ Tiêu chí GO/NO-GO", ""]
        for g in gates:
            note = f" — {g['note']}" if g.get("note") else ""
            L.append(f"- {STATUS_EMOJI.get(g.get('status', 'pending'), '⏳')} "
                     f"({g.get('status', 'pending')}) {g['text']}{note}")
        L.append("")
    if prog.get("notes"):
        L += ["## ℹ️ Ghi chú vận hành", "", prog["notes"], ""]
    srcs = prog.get("data_sources") or []
    if srcs:
        L += ["## 🔍 Nguồn dữ liệu kiểm chứng", ""] + [f"- `{s}`" for s in srcs] + [""]
    return "\n".join(L)


def sync_charter(prog, reg_version):
    """Ghi charter nếu nội dung đổi. Trả (đường dẫn tương đối, có_đổi_không)."""
    pid = prog.get("id", "unknown")
    path = os.path.join(CHARTER_DIR, f"{pid}.md")
    body = charter_body(prog, reg_version)
    old = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
    if old == body:
        return f"{CHARTER_REL}/{pid}.md", False
    os.makedirs(CHARTER_DIR, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(body)
    os.replace(tmp, path)
    # old is None = lần đầu sinh file (không phải "charter vừa đổi") — không báo động vô cớ.
    return f"{CHARTER_REL}/{pid}.md", old is not None


# ---------------- state (gate thay đổi từ lần trước?) ----------------

def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"programs": {}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, STATE_PATH)


def gate_block(prog, today, state, charter_rel):
    """Gate: ngày thường chỉ 1 dòng badge; in FULL khi lần đầu hoặc khi có status ĐỔI."""
    gates = prog.get("gate_criteria") or []
    pid = prog.get("id", "?")
    ps = state.setdefault("programs", {}).setdefault(pid, {})
    if not gates:
        return f"📊 Gate: chưa khai báo tiêu chí GO/NO-GO trong registry — charter: `{charter_rel}`"
    cur = {g["text"]: g.get("status", "pending") for g in gates}
    prev = ps.get("gates")
    first = prev is None
    changed = (not first) and prev != cur
    npass = sum(1 for v in cur.values() if v == "pass")
    nfail = sum(1 for v in cur.values() if v == "fail")
    if first or changed:
        ps["gates"], ps["last_change"] = cur, today.isoformat()
        head = ("📊 Gate **ĐỔI hôm nay** — bản đầy đủ:" if changed
                else "📊 Gate (bản đầy đủ, lần đầu ghi nhận):")
        lines = [head]
        for g in gates:
            st = g.get("status", "pending")
            mark = " 🔔" if (changed and prev.get(g["text"]) != st) else ""
            was = f" (trước: {prev.get(g['text'], 'chưa có')})" if mark else ""
            note = f" — {g['note']}" if g.get("note") else ""
            lines.append(f"  {STATUS_EMOJI.get(st, '⏳')} {g['text']}{note}{mark}{was}")
        lines.append(f"  ↳ charter đầy đủ: `{charter_rel}`")
        return "\n".join(lines)
    ps["gates"] = cur
    since = ps.get("last_change", "?")
    return (f"📊 Gate: **{npass}/{len(gates)} PASS**"
            + (f" · ❌ {nfail} FAIL" if nfail else "")
            + f" · không đổi từ {since} · chi tiết: `{charter_rel}`")


# ---------------- render ----------------

def badge_of(prog, res, activity_gap):
    """Quy tắc CƠ KHÍ, in ở footer report để người đọc kiểm chứng được — không phán đoán tuỳ nghi."""
    if prog.get("status") == "paused":
        return "paused"
    if res.get("error") or activity_gap == "error":
        return "red"
    flags = res.get("flags") or []
    if any(f.get("note") is None for f in flags):
        return "red"
    if any(f.get("severity") == "red" for f in flags):
        return "red"
    if any((g.get("status") == "fail") for g in prog.get("gate_criteria") or []):
        return "red"
    if flags or activity_gap:
        return "watch"
    return "green"


def render_section(idx, prog, today, state, reg_version):
    name = prog.get("name", prog.get("id", "?"))
    owner = prog.get("owner", "n/a")
    charter_rel, charter_changed = sync_charter(prog, reg_version)

    if prog.get("status") == "paused":
        return {"badge": "paused", "name": name,
                "summary": f"⏸ {prog.get('pause_reason', 'PAUSED')}",
                "activity": "— (tạm dừng)",
                "text": "\n".join([
                    f"── **{idx}) {name}** · 👤 {owner} · {BADGE['paused']}",
                    f"⏸ {prog.get('pause_reason', 'PAUSED')}",
                    f"🎯 Mục đích + tiêu chí nghiệm thu: `{charter_rel}`"])}

    res = {}
    probe = prog.get("probe") or {}
    try:
        handler = PROBES.get(probe.get("type"))
        if handler is None:
            raise ValueError(f"probe type không hỗ trợ: {probe.get('type')!r}")
        res = handler(probe, prog, today)
    except Exception as e:  # 1 sleeve lỗi không giết cả report
        res = {"error": f"{type(e).__name__}: {e}",
               "body": f"❌ Không đo được tự động: {type(e).__name__}: {e}\n"
                       f"→ số liệu sleeve này hôm nay = n/a; kiểm tra nguồn dữ liệu bên dưới."}

    head = headline(prog, res, today)
    act, activity_gap = today_activity(prog, today)
    b = badge_of(prog, res, activity_gap)

    lines = [f"── **{idx}) {name}** · 👤 {owner} · {BADGE[b]}",
             f"📈 {head} · 📅 {progress_short(prog, today)} · ⏱ nghiệm thu: {review_short(prog)}",
             f"💱 Giao dịch hôm nay: {act}"]
    for f in res.get("flags") or []:
        if f.get("note"):
            sev = {"info": "ℹ️ bình thường", "watch": "⏳ cần theo dõi"}.get(f["severity"], "🔴 nghiêm trọng")
            lines.append(f"⚠️ Cảnh báo: {f['text']} → {sev}: {f['note']}")
        else:
            lines.append(f"🔴 Cảnh báo: {f['text']} → **CHƯA CÓ GIẢI THÍCH** — {owner} phải rà nguồn "
                         f"bên dưới trong hôm nay rồi khai báo `attention_notes` trong registry "
                         f"(không để con số trần).")
    lines.append(gate_block(prog, today, state, charter_rel))
    if charter_changed:
        lines.append(f"📌 Charter vừa cập nhật hôm nay (mục đích/tiêu chí đổi trong registry) — `{charter_rel}`")
    body = (res.get("body") or "").strip()
    # Probe 1 dòng (ORB, capitulation) đã được dùng nguyên văn làm headline → đừng in lại lần 2.
    if body and not (len(body.splitlines()) == 1 and body.strip(" -*#")[:60] in head):
        lines.append(body)
    # Danh sách nguồn là METADATA TĨNH → nằm đủ ở charter; ngày thường chỉ nêu nguồn đầu để
    # người đọc có điểm bám kiểm chứng ngay, không dán lại cả khối mỗi ngày.
    srcs = prog.get("data_sources") or []
    if srcs:
        more = f" (+{len(srcs) - 1} nguồn, xem charter)" if len(srcs) > 1 else ""
        lines.append(f"🔍 Nguồn: `{srcs[0]}`{more}")
    return {"badge": b, "name": name, "summary": head, "activity": act,
            "text": "\n".join(lines)}


def _one_liner(idx, sec):
    """1 dòng tổng quan — cắt ngắn để quét trong <5 giây."""
    def cut(s, n):
        s = " ".join(s.split())
        return s if len(s) <= n else s[:n - 1].rstrip() + "…"
    return (f"{BADGE[sec['badge']].split()[0]} **{idx}) {sec['name']}** — {cut(sec['summary'], 95)}"
            f" | 💱 {cut(sec['activity'], 70)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (mặc định: hôm nay ICT)")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    ap.add_argument("--no-state", action="store_true",
                    help="không ghi data/paper_report_state.json (dùng khi chạy thử/backfill)")
    ap.add_argument("--force-state", action="store_true",
                    help="ghi state kể cả khi có --date (chỉ dùng cho selfcheck/fixture)")
    args = ap.parse_args()

    os.environ.setdefault("TZ", "Asia/Ho_Chi_Minh")
    now = dt.datetime.now()
    today = dt.date.fromisoformat(args.date) if args.date else now.date()
    # Chỉ ghi state ở lần chạy LIVE (không --date, không --no-state) — chạy lại quá khứ để
    # so sánh không được phép làm nhiễu mốc "gate đổi lần cuối" của bản production.
    write_state = (args.date is None or args.force_state) and not args.no_state

    state = load_state()
    sections, reg_version, programs = [], "?", []
    err = None
    try:
        with open(args.registry, encoding="utf-8") as f:
            reg = json.load(f)
        programs = reg.get("programs", [])
        reg_version = reg.get("version", "?")
        if not programs:
            err = "⚠️ Registry đọc được nhưng không có chương trình nào (`programs` rỗng)."
    except Exception as e:
        err = (f"❌ Không đọc được registry ({type(e).__name__}: {e}) — không render được section "
               f"nào. Sửa `{args.registry}` rồi chạy lại.")

    for i, prog in enumerate(programs, 1):
        try:
            sections.append(render_section(i, prog, today, state, reg_version))
        except Exception as e:  # entry hỏng cấu trúc cũng không giết report
            sections.append({"badge": "red", "name": prog.get("id", "?"),
                             "summary": f"entry registry hỏng: {type(e).__name__}: {e}",
                             "activity": "n/a",
                             "text": f"── **{i}) {prog.get('id', '?')}**\n❌ Entry registry hỏng: "
                                     f"{type(e).__name__}: {e}"})

    # ---- header + executive summary ----
    reds = [(i, s) for i, s in enumerate(sections, 1) if s["badge"] == "red"]
    watches = [(i, s) for i, s in enumerate(sections, 1) if s["badge"] == "watch"]
    out = [f"📋 **Paper Programs Daily Report — {today}**",
           f"Render {now.strftime('%H:%M')} ICT · registry v{reg_version} · {len(sections)} chương "
           f"trình · *vintage dữ liệu xem `asof`/nguồn từng mục (BQ chưa có close phiên T lúc 16:00)*"]
    if reds:
        out.append("🔴 **CẦN CHÚ Ý NGAY** (" + str(len(reds)) + "): "
                   + " · ".join(f"#{i} {s['name']}" for i, s in reds))
    elif watches:
        out.append("⏳ **Theo dõi** (" + str(len(watches)) + "): "
                   + " · ".join(f"#{i} {s['name']}" for i, s in watches))
    else:
        out.append("✅ Không có cảnh báo nghiêm trọng ở chương trình nào hôm nay.")
    if err:
        out.append(err)
    if sections:
        out += ["", "**TỔNG QUAN** — badge · chương trình · số hôm nay · giao dịch hôm nay:"]
        out += [_one_liner(i, s) for i, s in enumerate(sections, 1)]
    for s in sections:
        out += ["", s["text"]]
    out += ["",
            "───",
            "📎 *Badge: 🔴 RED = probe lỗi / cảnh báo chưa được giải thích / có gate FAIL · "
            "⏳ WATCH = có cảnh báo đã giải thích hoặc thiếu khai báo giao dịch · ✅ GREEN = còn lại. "
            f"Mục đích + phương pháp + tiêu chí nghiệm thu đầy đủ: `{CHARTER_REL}/<id>.md` "
            "(tự sinh từ registry). Gate chỉ in đầy đủ khi có thay đổi — trạng thái so sánh lưu ở "
            "`data/paper_report_state.json`.*",
            "⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, "
            "không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*"]
    if write_state:
        try:
            save_state(state)
        except Exception as e:
            out.append(f"⚠️ *không ghi được `{STATE_PATH}`: {type(e).__name__}: {e} — so sánh gate "
                       f"lần sau có thể in lại full.*")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
