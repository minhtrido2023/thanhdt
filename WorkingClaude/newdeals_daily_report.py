#!/usr/bin/env python3
"""newdeals_daily_report.py — daily "New deals" Discord report.

Combines TWO already-built, reusable data sources into ONE Discord message posted to the
"New deals" topic (thread 1523612826260734112):

  1. AlphaLens Paper Portfolio  — reuses alphalens_report.generate_section()
     (FPT/ACB/MBB/HDB paper book P&L vs entry + vs VNINDEX benchmark).
  2. Golden/Strong Watchlist    — reuses sector_lens_monitor.compute_status() +
     build_telegram_message() + load_ratings(): the Group-A 6-state sector lens with the
     8L-rating DOUBLE-CONFIRM cross-check (rating<=2 AND sector-lens BUY = two independent
     systems agreeing) and same-day state transitions.

RESEARCH / MONITOR ONLY — touches no production trading file (custom30V / BAL / LAG /
rating_8l.py unchanged). This is an ADDITIONAL channel; it does not replace the pt_8l_daily
Telegram digest or the AlphaLens block in DollarBill's plan report. A BUY surfaced here still
routes through Taylor-validate -> DollarBill-plan -> user-approve -> Mafee.

Fail-safe (dispatch req): if the BQ local cache is not fresh/readable (e.g. the overnight sync
has not finished by 06:00 ICT), compute_status() raises -> we LOG the error and exit non-zero
WITHOUT sending, so a malformed/empty message never reaches the channel.

Job Taylor_20260706_091624.
"""
import os
import sys
import subprocess
import tempfile
import datetime as dt

ROOT = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "mike", "bin"))
os.environ.setdefault("WORKDIR", ROOT)
os.environ.setdefault("WORKDIR_8L", ROOT)

from discord_channels import resolve as _resolve_channel

THREAD_ID = _resolve_channel("new_deals")                 # Discord "New deals" topic
TRADING_DAILY_THREAD = _resolve_channel("trading_daily")  # ops-alert topic (return-gate BLOCKED alert)
NOTIFY = os.path.join(ROOT, "mike", "bin", "notify_thread.sh")


def _log(msg: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] newdeals: {msg}", flush=True)


def _html_to_discord(s: str) -> str:
    """build_telegram_message() emits Telegram HTML (<b>/<i>); Discord renders markdown, not
    HTML, so convert bold/italic. Both HTML tags map cleanly onto Discord's ** / * markers."""
    return (s.replace("<b>", "**").replace("</b>", "**")
             .replace("<i>", "*").replace("</i>", "*"))


def build_message():
    """Assemble the combined Discord message + a change-detection flag.

    User mandate 2026-07-07: "nếu có deal mới trong alpha lens hoặc golden strong, hoặc có
    sự biến động mạnh về thứ hạng thì báo lại; nếu không thì mỗi ngày báo không có gì thay
    đổi, để biết hệ thống vẫn vận hành bình thường." Every underlying section ALREADY
    computes its own day-over-day diff (they were built for exactly this) — this function
    only reads those existing signals instead of duplicating diff logic:
      - Golden/Strong (sector lens): `transitions` list (empty prior = baseline, ALSO
        treated as change-worthy so the user sees the first-ever snapshot).
      - AlphaLens: an "EXIT ALERT" line in generate_section()'s own output (an entry
        condition breach IS the "new deal" event for a buy-and-hold book).
      - DC Book: "ENTER"/"EXIT" markers in converge_report's own live-vs-seed diff.

    Returns (message: str, changed: bool). Raises if the sector-lens evaluation cannot
    read the cache (fatal -> caller aborts without sending, unchanged from before).
    """
    today = dt.date.today().isoformat()

    # ---- Section 2 first: sector lens is the hard dependency (raises on cache failure) ----
    import sector_lens_monitor as slm
    r = slm.compute_status()                      # raises on cache-read failure -> abort upstream
    ratings = slm.load_ratings()
    if not ratings:
        _log("rating_8l.csv missing/unreadable — sending sector lens without 8L cross-check (R? shown).")
    sector_tg = slm.build_telegram_message(
        r["df"], r["transitions"], r["prior"], r["state"],
        r["spread_yoy"], r["feed_ok"], r["feed_asof"], ratings)
    sector_md = _html_to_discord(sector_tg)
    sector_changed = bool(r["transitions"]) or not r["prior"]   # baseline run also shown once

    # ---- Section 1: AlphaLens (returns a string; degrades to a ⚠️ line, never raises) ----
    from alphalens_report import generate_section
    alphalens_md = generate_section(as_of_date=today)
    alphalens_changed = "EXIT ALERT" in alphalens_md

    # ---- Section 3: ConvergePort paper book (double-confirm converge, job Taylor_20260706_093329).
    # Reuse the sector-lens set already computed above (r["df"] + ratings) so we don't run
    # compute_status() twice; degrades to a ⚠️ line, never raises.
    from converge_report import generate_section as converge_section
    live_dc = {}
    for _, row in r["df"][r["df"]["status"] == "BUY"].iterrows():
        rt = ratings.get(row["ticker"])
        if rt is not None and int(rt) <= 2:
            live_dc[row["ticker"]] = row["buy_mode"] or "ACCUMULATE"
    converge_md = converge_section(as_of_date=today, live_set=live_dc)
    # Literal emoji markers converge_report.py itself uses for its live-vs-seed diff
    # (see "🟢 ENTER"/"🔴 EXIT" in converge_report.generate_section) — not the bare
    # words, to avoid false positives from unrelated text containing "enter"/"exit".
    converge_changed = ("🟢 ENTER" in converge_md) or ("🔴 EXIT" in converge_md)

    changed = sector_changed or alphalens_changed or converge_changed

    if changed:
        header = f"🆕 **NEW DEALS — {today}**  ·  *research/monitor, not an order*"
        parts = [
            header,
            "## AlphaLens Paper Portfolio\n" + alphalens_md,
            "## Golden/Strong Watchlist (8L + Sector Lens)\n" + sector_md,
            "## DC Book Paper Portfolio\n" + converge_md,
        ]
        return "\n\n".join(parts), True

    # Không đổi gì hôm nay — 1 dòng "vẫn sống", KHÔNG phải im lặng (user: "để biết hệ
    # thống vẫn vận hành bình thường" — phân biệt "không có tin" với "hệ thống chết").
    quiet = (f"🆕 **NEW DEALS — {today}** — Không có deal mới / thay đổi thứ hạng đáng chú ý "
             f"trong AlphaLens, Golden/Strong Watchlist, DC Book hôm nay. Hệ thống vẫn giám "
             f"sát bình thường.")
    return quiet, False


def send(message: str) -> None:
    subprocess.run([NOTIFY, message, THREAD_ID], check=True)


def _check_return_gate(message: str) -> bool:
    """CỔNG CHẶN CỨNG (coding_guidelines §21/§22, T1 corp-action crosscheck) — trước khi post,
    chạy `report_return_gate.run_gate()` trên đúng nội dung sắp lên Discord.

    Đây là kênh duy nhất đăng "AlphaLens Paper Portfolio" / "DC Book Paper Portfolio" mà
    KHÔNG BAO GIỜ ghi ra file .md — `run_gate()` chỉ có 1 caller (`send_report_email.py`), nên
    trước bản vá này cổng không hề chạy trên message thật user đọc mỗi sáng. Không ghi vĩnh
    viễn ra `mike/reports/`: chỉ cần 1 file tạm mang TÊN có ngày (`accounts_asof_from_name()`
    suy ngày chốt từ regex `\\d{4}-\\d{2}-\\d{2}` trong tên file, không đọc nội dung để suy ngày).

    Fail-closed: gate lỗi/import lỗi/CHẶN ⇒ trả False, KHÔNG post gì (giống hệt cách
    `send_report_email.py` chặn toàn bộ email khi gate fail — ít xâm lấn nhất, không cần tách
    mục paper ra khỏi phần còn lại của message).
    """
    import report_return_gate as rrg
    today = dt.date.today().isoformat()
    fd, tmp_path = tempfile.mkstemp(prefix="newdeals_gate_", suffix=f"_{today}.md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(message)
        rc = rrg.run_gate(tmp_path, out=sys.stderr)
        return rc == 0
    finally:
        os.unlink(tmp_path)


def _alert_gate_blocked(kind: str, detail: str = "") -> None:
    """rc=3 (CHẶN) trước bản vá này chỉ có 1 dòng stderr không ai đọc — 1 ngày bị chặn không
    phân biệt được với 1 ngày yên ả bình thường (quant-skeptic vòng 3, Taylor_20260813_073404).

    `kind`: "blocked" khi run_gate() TRẢ VỀ rc!=0 thật (chặn do corp-action/cổ tức chưa khớp) vs
    "crash" khi CHÍNH _check_return_gate() ném exception (import lỗi, hoặc gate chạm parquet
    cache đang ghi dở lúc overnight sync 06:00 ICT) — quant-skeptic vòng 4 chỉ ra nhánh crash
    trước bản vá này vẫn im lặng vì alert cũ nằm TRONG _check_return_gate(), không bọc except ở
    main(). Hai nội dung khác nhau để người đọc phân biệt được 2 nguyên nhân rc=3.
    Best-effort: lỗi ở đây không được che mất việc CHẶN (đã _log + return 3 ở caller)."""
    if kind == "crash":
        msg = ("⚠️ newdeals_daily_report: cổng tỉ suất (report_return_gate) TỰ CRASH khi kiểm "
               f"tra — KHÔNG gửi Discord New deals hôm nay ({detail}). Xem stderr/log của job "
               "để biết chi tiết.")
    else:
        msg = ("⚠️ newdeals_daily_report: report BLOCKED by return gate (report_return_gate) — "
               "KHÔNG gửi Discord New deals hôm nay. Xem stderr/log của job để biết mã/vấn đề cụ thể.")
    try:
        subprocess.run([NOTIFY, msg, TRADING_DAILY_THREAD], check=False, timeout=30)
    except Exception:
        pass


def main() -> int:
    try:
        message, changed = build_message()
    except Exception as e:
        _log(f"FATAL — could not build report (BQ cache not ready?): {e}. NOT sending.")
        return 1

    try:
        gate_ok = _check_return_gate(message)
    except Exception as e:
        _log(f"FATAL — cổng tỉ suất (report_return_gate) KHÔNG chạy được ({e}) — CHẶN "
             f"(fail-closed). NOT sending.")
        _alert_gate_blocked("crash", detail=str(e))
        return 3
    if not gate_ok:
        _log("FATAL — cổng tỉ suất (report_return_gate) CHẶN: tỉ suất sổ paper chưa khớp "
             "corporate_action / cổ tức. NOT sending. Xem stderr phía trên để biết chi tiết.")
        _alert_gate_blocked("blocked")
        return 3

    try:
        send(message)
    except Exception as e:
        _log(f"FATAL — notify_thread.sh failed: {e}")
        return 2

    _log(f"changed={changed}")

    _log(f"sent OK ({len(message)} chars) to thread {THREAD_ID}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
