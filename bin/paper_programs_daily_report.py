#!/usr/bin/env python3
"""Paper Programs Daily Report — báo cáo hợp nhất MỌI chương trình paper-trading active.

Registry-driven: danh sách chương trình ở mike/kb/paper_programs_registry.json — thêm sleeve
mới = thêm entry, không sửa code này. Mỗi section: mục tiêu / tiến độ / hoạt động hôm nay /
lũy kế / gate GO-NO-GO / nguồn dữ liệu kiểm tra lại.

Nguyên tắc trung thực: số nào không trace được về file thật → 'n/a + lý do'. Một sleeve lỗi
không giết cả report (section đó ghi lỗi, exit vẫn 0).

Usage: paper_programs_daily_report.py [--date YYYY-MM-DD] [--registry PATH]
In markdown ra stdout. Luôn exit 0 (trừ khi chính registry không đọc nổi — vẫn in report
tối thiểu nói rõ điều đó, vẫn exit 0 để cron không rơi im lặng).
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
DEFAULT_REGISTRY = os.path.join(WC_ROOT, "mike/kb/paper_programs_registry.json")
STATUS_EMOJI = {"pass": "✅", "fail": "❌", "pending": "⏳", "manual": "🔎"}


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
    import csv
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


def progress_line(prog, today):
    pr = prog.get("progress") or {}
    if pr.get("mode") == "evidence_sessions":
        # Đếm phiên executor THẬT (file journal), không đếm ngày lịch — 1 ngày flag bật
        # nhưng bot không chạy = 0 evidence, không được tính.
        dates = count_evidence_sessions(pr["account"], pr.get("count_from"))
        tgt = pr.get("target_sessions")
        last = f", gần nhất {dates[-1]}" if dates else ""
        return (f"📅 Tiến độ: **{len(dates)}/{tgt} phiên evidence** (đếm phiên executor "
                f"thật có journal trên `{pr['account']}`, từ {pr.get('count_from', '?')}{last}) "
                f"— {prog.get('end_or_trigger') or ''}")
    start = prog.get("start")
    end = prog.get("end")
    trigger = prog.get("end_or_trigger") or ""
    if not start:
        return f"📅 Tiến độ: chưa bắt đầu / chưa xác định ngày start — {trigger}"
    d0 = dt.date.fromisoformat(start)
    n = weekdays_between(d0, today)
    if end:
        d1 = dt.date.fromisoformat(end)
        m = weekdays_between(d0, d1)
        return (f"📅 Tiến độ: phiên ~{n}/{m} (từ {start} → {end}, lịch T2-T6 ước tính) — {trigger}")
    return f"📅 Tiến độ: phiên ~{n} từ {start} — mốc review: {trigger}"


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


def _attention_flags(out):
    flags = []
    if "Traceback (most recent call last)" in out:
        flags.append("Python traceback trong output")
    for m in _ATTENTION_RE.finditer(out):
        flags.append(m.group(0).strip())
    return flags


def probe_command(probe):
    """Chạy 1 lệnh trong WC_ROOT, trả stdout (cắt max_chars). Non-zero exit vẫn trả output."""
    cmd = probe["cmd"]
    timeout = probe.get("timeout", 120)
    max_chars = probe.get("max_chars", 1400)
    r = subprocess.run(cmd, cwd=WC_ROOT, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout or "").strip()
    if not out:
        out = (r.stderr or "").strip()[:400] or "(không có output)"
    flags = _attention_flags(out)
    if len(out) > max_chars:
        out = out[:max_chars] + f"\n… (cắt bớt, xem nguồn để đủ; exit={r.returncode})"
    lines = []
    if flags:
        lines.append("⚠️ **CẦN CHÚ Ý** — " + " | ".join(flags))
    lines.append(out)
    if r.returncode != 0:
        lines.append(f"⚠️ lệnh exit={r.returncode} — output ở trên có thể không đầy đủ")
    return {"body": "\n".join(lines)}


def probe_journal_scan(probe, today):
    """Scan exec journal của 1 account: đếm phiên đã chạy + marker hits (tổng & hôm nay)."""
    account = probe["account"]
    markers = probe.get("markers", [])
    pattern = os.path.join(WC_ROOT, f"data/execution_logs/exec_{account}_*_journal.csv")
    files = sorted(glob.glob(pattern))
    # loại fixture selfcheck ngày 2099
    files = [f for f in files if "2099" not in f]
    if not files:
        return {"body": (f"- Phiên executor đã chạy trên account `{account}`: **0** "
                         f"(không có file khớp `exec_{account}_*_journal.csv`)\n"
                         f"- → chưa tích lũy được evidence nào; flag bật nhưng chỉ có tác dụng "
                         f"khi executor thực sự chạy phiên trên account này")}
    total_hits, today_hits, today_str = {m: 0 for m in markers}, {m: 0 for m in markers}, today.isoformat()
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                for m in markers:
                    if m in line:
                        total_hits[m] += 1
                        if line.startswith(today_str):
                            today_hits[m] += 1
    lines = [f"- Phiên executor account `{account}`: **{len(files)}** file journal "
             f"(gần nhất: {os.path.basename(files[-1])})"]
    if markers:
        tot = sum(total_hits.values())
        tod = sum(today_hits.values())
        detail = ", ".join(f"{m}={total_hits[m]}" for m in markers)
        lines.append(f"- Marker hits: hôm nay **{tod}**, lũy kế **{tot}** ({detail})")
    return {"body": "\n".join(lines)}


def probe_alphalens(probe, today):
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
    head = (f"- MTM as-of **{asof}** (BQ cache, close phiên gần nhất đã sync):\n"
            + "\n".join(lines)
            + f"\n- Portfolio EW: **{port_ret:+.2f}%** | VNINDEX {bench_entry:,.2f} → "
              f"{vnindex_now:,.2f} = {bench_ret:+.2f}% | **Excess {excess:+.2f}pp**"
            + "\n- Hôm nay: không có giao dịch (buy-and-hold, quan sát đến "
            + f"{meta['end_date']})")
    return {"body": head}


PROBES = {
    "command": lambda probe, today: probe_command(probe),
    "journal_scan": probe_journal_scan,
    "alphalens": probe_alphalens,
}


# ---------------- render ----------------

def render_section(idx, prog, today):
    lines = [f"── **{idx}) {prog.get('name', prog.get('id', '?'))}** — owner: {prog.get('owner', 'n/a')}"]
    if prog.get("status") == "paused":
        lines.append(f"⏸ {prog.get('pause_reason', 'PAUSED')}")
        lines.append(f"🎯 (mục tiêu gốc) {prog.get('objective', 'n/a')}")
        srcs = prog.get("data_sources") or []
        if srcs:
            lines.append("🔍 Nguồn: " + " · ".join(f"`{s}`" for s in srcs))
        return "\n".join(lines)
    lines.append(f"🎯 {prog.get('objective', 'n/a')}")
    lines.append(progress_line(prog, today))
    probe = prog.get("probe") or {}
    ptype = probe.get("type")
    try:
        handler = PROBES.get(ptype)
        if handler is None:
            raise ValueError(f"probe type không hỗ trợ: {ptype!r}")
        result = handler(probe, today)
        lines.append(result["body"])
    except Exception as e:  # 1 sleeve lỗi không giết cả report
        lines.append(f"❌ Không đo được tự động: {type(e).__name__}: {e}\n"
                     f"→ số liệu sleeve này hôm nay = n/a; kiểm tra nguồn dữ liệu bên dưới.")
    gates = prog.get("gate_criteria") or []
    if gates:
        lines.append("Gate GO/NO-GO:")
        for g in gates:
            emoji = STATUS_EMOJI.get(g.get("status", "pending"), "⏳")
            note = f" — {g['note']}" if g.get("note") else ""
            lines.append(f"  {emoji} {g['text']}{note}")
    if prog.get("notes"):
        lines.append(f"ℹ️ {prog['notes']}")
    srcs = prog.get("data_sources") or []
    if srcs:
        lines.append("🔍 Nguồn: " + " · ".join(f"`{s}`" for s in srcs))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (mặc định: hôm nay ICT)")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    args = ap.parse_args()

    os.environ.setdefault("TZ", "Asia/Ho_Chi_Minh")
    now = dt.datetime.now()
    today = dt.date.fromisoformat(args.date) if args.date else now.date()

    # "Render lúc" ≠ vintage dữ liệu — nhãn cũ "Data as-of: <giờ chạy>" khiến người đọc tưởng
    # mọi số là của HÔM NAY, trong khi mục đọc BQ chỉ có tới T-1 (BQ chưa có close same-day lúc
    # 15:30-16:00; sync 23:45). Vintage thật của từng mục nằm ở dòng `asof`/cửa sổ trong mục đó.
    out = [f"📋 **Paper Programs Daily Report — {today}**",
           f"Render lúc: {now.strftime('%Y-%m-%d %H:%M')} ICT — *vintage dữ liệu xem `asof` "
           f"từng mục* | registry: `mike/kb/paper_programs_registry.json`"]
    try:
        with open(args.registry, encoding="utf-8") as f:
            reg = json.load(f)
        programs = reg.get("programs", [])
        if not programs:
            out.append("⚠️ Registry đọc được nhưng không có chương trình nào (`programs` rỗng).")
        out[1] += f" v{reg.get('version', '?')} ({len(programs)} chương trình)"
    except Exception as e:
        out.append(f"❌ Không đọc được registry ({type(e).__name__}: {e}) — không render được "
                   f"section nào. Sửa `{args.registry}` rồi chạy lại.")
        programs = []
    for i, prog in enumerate(programs, 1):
        out.append("")
        try:
            out.append(render_section(i, prog, today))
        except Exception as e:  # entry hỏng cấu trúc cũng không giết report
            out.append(f"── **{i}) {prog.get('id', '?')}**\n❌ Entry registry hỏng: "
                       f"{type(e).__name__}: {e}")
    out.append("")
    out.append("⚠️ *PAPER TRADING — không phải tiền thật; toàn bộ số liệu là mô phỏng/quan sát, "
               "không phải khuyến nghị đầu tư. Số không trace được về file nguồn = n/a.*")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
