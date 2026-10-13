#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pnj_q3_review_watch.py — canh trigger review PNJ: "khi PNJ công bố BCTC Quý 3/2026".

VÌ SAO CÓ FILE NÀY (audit sẵn sàng BCTC Q3, finding L2, job Taylor_20261013_123622; user duyệt
2026-10-13, job Taylor_20261013_125149): PNJ bị loại khỏi cả 2 account từ 2026-09-30
(`kb/current_ops.md`), điều kiện xét lại = "khi PNJ công bố BCTC Q3" — nhưng đó chỉ là văn xuôi,
không cơ chế nào canh. File này là cơ chế đó.

LÀM GÌ: `tav2_bq.ticker_financial` có dòng PNJ `quarter='2026Q3'` ⇒ ĐÚNG MỘT LẦN:
  (1) bus `question` topic `pnj-bctc-q3-review-trigger` (target Mike), rồi
  (2) 1 tin Discord Trading Daily.
KHÔNG làm gì khác: không đụng `excluded_tickers`, không khôi phục PNJ, không chặn pipeline
(WARN-only; mọi nhánh đều exit 0).

Nhãn quý: cột `quarter` của `ticker_financial` = quý TÀI CHÍNH của báo cáo (đo 2026-10-13: KBC
`2026Q3` có Release_Date 2026-10-12; PNJ mới tới `2026Q2`) — xem
`kb/data_registry/fundamentals/ticker_financial.md`.

CHỐNG LẶP (§5 idempotent): state file ghi NGUYÊN TỬ (tmp + os.replace) sau TỪNG hành động ngoài.
  · bus: nếu bị kill sau khi post mà trước khi ghi state, lượt sau hỏi lại CHÍNH bus (nguồn sự
    thật) trước khi post ⇒ không lặp.
  · Discord: không hỏi lại được Discord ⇒ ghi dấu "đã thử gửi" TRƯỚC khi gửi (tối-đa-một-lần).
    Bị kill giữa chừng thì có thể MẤT tin Discord, nhưng question trên bus vẫn còn.
FAIL-CLOSED khi lỗi đọc: state hỏng / BQ lỗi / bus không đọc được ⇒ KHÔNG bắn gì, in lỗi thật
(§29), exit 0. Thà chậm 1 ngày còn hơn spam.

Dùng:  pnj_q3_review_watch.py            (chuỗi 19:00, bq_freshness_check.sh)
       pnj_q3_review_watch.py --dry-run  (đọc BQ thật, không post, không ghi state)
Self-check: bin/pnj_q3_review_watch_selfcheck.py
"""
import argparse
import glob
import gzip
import json
import os
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # mike/
WORKDIR = os.path.dirname(ROOT)                                       # WorkingClaude/

TICKER = "PNJ"
QUARTER = "2026Q3"
TOPIC = "pnj-bctc-q3-review-trigger"
BUS_AGENT = "Taylor"            # chủ luồng due-diligence PNJ (question gốc 2026-09-28)
DISCORD_CHANNEL = "trading_daily"
PROJECT = "lithe-record-440915-m9"
STATE_PATH = os.path.join(WORKDIR, "data", "pnj_q3_review_watch_state.json")
BQ_TIMEOUT_S = 120


def now_ict():
    return datetime.now(_ICT)


# ── state ────────────────────────────────────────────────────────────────────────────────
def load_state(path):
    """Trả (state dict, lỗi|None). File chưa có = {} hợp lệ. File có mà không đọc được / sai
    hình dạng / của mã-quý khác = LỖI (caller fail-closed)."""
    if not os.path.exists(path):
        return {}, None
    try:
        with open(path, encoding="utf-8") as f:
            st = json.load(f)
    except Exception as ex:
        return None, f"{type(ex).__name__}: {ex}"
    if not isinstance(st, dict):
        return None, f"state không phải object JSON (kiểu {type(st).__name__})"
    if st and (st.get("ticker") != TICKER or st.get("quarter") != QUARTER):
        return None, f"state của {st.get('ticker')}/{st.get('quarter')}, không phải {TICKER}/{QUARTER}"
    return st, None


def save_state(path, st):
    """Ghi nguyên tử: kill giữa chừng không bao giờ để lại file nửa vời cho lượt sau tin."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


# ── phụ thuộc ngoài (thay được trong selfcheck) ──────────────────────────────────────────
def build_sql():
    """SQL đếm BCTC thật của PNJ quý đích. Loại dòng GIỮ CHỖ (BQ có dòng mang nhãn quý nhưng
    Release_Date/NP_P0 NULL — arch-review 13/10: 893/7.534 dòng từ 2025Q1): watcher chỉ bắn MỘT
    lần nên dòng giữ chỗ không được phép đốt trigger. Cùng bộ lọc với pkl LAG."""
    return (f"SELECT COUNT(*) AS n, CAST(MIN(t.Release_Date) AS STRING) AS release_date, "
            f"CAST(MIN(t.time) AS STRING) AS fin_time "
            f"FROM `{PROJECT}.tav2_bq.ticker_financial` AS t "
            f"WHERE t.ticker = '{TICKER}' AND t.quarter = '{QUARTER}' "
            f"AND t.Release_Date IS NOT NULL AND t.NP_P0 IS NOT NULL")


def query_bq():
    """Trả dict {"n", "release_date", "time"} của PNJ quý đích. Raise khi không đọc được."""
    sql = build_sql()
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
                        "--format=json", "--quiet", sql],
                       capture_output=True, text=True, timeout=BQ_TIMEOUT_S)
    if r.returncode != 0:
        raise RuntimeError(f"bq exit={r.returncode}: {(r.stderr or r.stdout).strip()[:300]}")
    rows = json.loads(r.stdout)
    if not isinstance(rows, list) or len(rows) != 1:
        raise RuntimeError(f"bq trả hình dạng lạ: {r.stdout.strip()[:200]}")
    row = rows[0]
    return {"n": int(row["n"]), "release_date": row.get("release_date"), "time": row.get("fin_time")}


def bus_has_question(bus_dir=None):
    """True nếu bus ĐÃ có question đúng topic của agent này. Quét mọi tầng .jsonl VÀ .jsonl.gz dưới bus/
    (inbox + batches + inbox/archive đã nén…, §17). Khớp theo TRƯỜNG JSON, không theo chuỗi con: finding khác
    có thể nhắc tên topic trong payload. Raise khi không quét được."""
    bus_dir = bus_dir or os.path.join(ROOT, "bus")
    if not os.path.isdir(bus_dir):
        raise RuntimeError(f"không thấy thư mục bus: {bus_dir}")
    paths = (glob.glob(os.path.join(bus_dir, "**", "*.jsonl"), recursive=True)
             + glob.glob(os.path.join(bus_dir, "**", "*.jsonl.gz"), recursive=True))
    for path in paths:
        opener = (lambda p: gzip.open(p, "rt", encoding="utf-8", errors="replace")) if path.endswith(".gz") \
            else (lambda p: open(p, encoding="utf-8", errors="replace"))
        with opener(path) as f:
            for line in f:
                if TOPIC not in line:
                    continue
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                if isinstance(ev, dict) and ev.get("topic") == TOPIC and ev.get("event_type") == "question":
                    return True
    return False


def post_bus(payload):
    r = subprocess.run([os.path.join(ROOT, "bin", "append_event.sh"), BUS_AGENT, "question", TOPIC,
                        json.dumps(payload, ensure_ascii=False)],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"append_event.sh exit={r.returncode}: {(r.stderr or r.stdout).strip()[:300]}")


def post_discord(msg):
    r = subprocess.run([os.path.join(ROOT, "bin", "notify_thread.sh"), msg, DISCORD_CHANNEL],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"notify_thread.sh exit={r.returncode}: {(r.stderr or r.stdout).strip()[:300]}")


# ── nội dung ─────────────────────────────────────────────────────────────────────────────
def build_payload(det):
    return {
        "target": "Mike",
        "urgency": "normal",
        "question": (f"{TICKER} đã có BCTC {QUARTER} trong ticker_financial (Release_Date "
                     f"{det.get('release_date')}). Đây là REVIEW TRIGGER của việc loại {TICKER} "
                     f"khỏi 2 account từ 2026-09-30 (kb/current_ops.md: '{TICKER} EXCLUDED cả 2 "
                     f"account … REVIEW TRIGGER = khi {TICKER} công bố BCTC Quý 3/2026'). Cần chạy "
                     f"lại due-diligence ĐẦY ĐỦ kiểu fundamental-skeptic trên số Q3 rồi mới quyết "
                     f"giữ loại hay cho trở lại candidate custom30V."),
        "do_not": (f"KHÔNG tự khôi phục {TICKER}; KHÔNG sửa excluded_tickers trong "
                   f"secrets/trading_bot_accounts.json trước khi user duyệt kết quả review."),
        "options": ["Dispatch due-diligence đầy đủ (fundamental-skeptic) rồi trình user",
                    "Giữ loại, hoãn review (ghi lý do)"],
        "evidence": {"table": "tav2_bq.ticker_financial", "ticker": TICKER, "quarter": QUARTER,
                     "n_rows": det.get("n"), "release_date": det.get("release_date"),
                     "time": det.get("time")},
        "source": "bin/pnj_q3_review_watch.py (chuỗi 19:00, bắn MỘT LẦN)",
    }


def build_discord(det):
    return (f"🔔 {TICKER} đã công bố BCTC {QUARTER} (ticker_financial, Release_Date "
            f"{det.get('release_date')}) — đây là REVIEW TRIGGER của việc loại {TICKER} khỏi 2 "
            f"account từ 09-30. Cần chạy lại due-diligence đầy đủ (kiểu fundamental-skeptic) trước "
            f"khi quyết; KHÔNG tự khôi phục, excluded_tickers giữ nguyên. Bus question: {TOPIC}. "
            f"(Tin này chỉ gửi một lần.)")


ALERT_RESULTS = ("state_unreadable", "bus_unreadable", "bus_post_failed")


# ── lõi ──────────────────────────────────────────────────────────────────────────────────
def run(state_path=STATE_PATH, query_fn=query_bq, bus_has_fn=bus_has_question, post_bus_fn=post_bus,
        post_discord_fn=post_discord, now_fn=now_ict, dry_run=False, out=print):
    """Trả mã kết quả (chuỗi) để selfcheck khẳng định. Lỗi đọc/post được nuốt thành mã kết quả;
    chỉ lỗi GHI state mới raise (main() bắt, in WARN, exit 0)."""
    st, err = load_state(state_path)
    if err:
        out(f"WARN pnj-q3-watch: KHÔNG đọc được state {state_path} — fail-closed, không bắn gì. Lỗi thật: {err}")
        return "state_unreadable"
    if st.get("bus_posted_at") and st.get("discord_attempted_at"):
        return "already_fired"

    det = st.get("detected")
    if not det:
        try:
            det = query_fn()
        except Exception as ex:
            out(f"WARN pnj-q3-watch: không truy vấn được ticker_financial — fail-closed, thử lại lượt sau. "
                f"Lỗi thật: {type(ex).__name__}: {ex}")
            return "query_failed"
        if not isinstance(det, dict) or not isinstance(det.get("n"), int):
            out(f"WARN pnj-q3-watch: kết quả truy vấn sai hình dạng ({det!r}) — fail-closed.")
            return "query_failed"
        if det["n"] <= 0:
            return "not_yet"

    if dry_run:
        out(f"DRY-RUN pnj-q3-watch: {TICKER} {QUARTER} ĐÃ có ({det}) — sẽ post bus question '{TOPIC}' + Discord.")
        return "would_fire"

    stamp = lambda: now_fn().isoformat(timespec="seconds")  # noqa: E731
    if not st.get("bus_posted_at"):
        try:
            on_bus = bool(bus_has_fn())
        except Exception as ex:
            out(f"WARN pnj-q3-watch: không quét được bus để chống lặp — fail-closed, không post. "
                f"Lỗi thật: {type(ex).__name__}: {ex}")
            return "bus_unreadable"
        if not on_bus:
            try:
                post_bus_fn(build_payload(det))
            except Exception as ex:
                out(f"WARN pnj-q3-watch: post bus question lỗi — chưa ghi state, lượt sau thử lại. "
                    f"Lỗi thật: {type(ex).__name__}: {ex}")
                return "bus_post_failed"
        st = {"ticker": TICKER, "quarter": QUARTER, "topic": TOPIC, "detected": det,
              "bus_posted_at": stamp(), "bus_found_existing": on_bus}
        save_state(state_path, st)

    if not st.get("discord_attempted_at"):
        st["discord_attempted_at"] = stamp()
        save_state(state_path, st)          # dấu "đã thử" TRƯỚC khi gửi ⇒ tối đa một lần
        try:
            post_discord_fn(build_discord(det))
            st["discord_ok"] = True
        except Exception as ex:
            st["discord_ok"] = False
            st["discord_error"] = f"{type(ex).__name__}: {ex}"
            out(f"WARN pnj-q3-watch: gửi Discord lỗi (KHÔNG gửi lại — question trên bus vẫn còn). "
                f"Lỗi thật: {st['discord_error']}")
        save_state(state_path, st)
    out(f"FIRED pnj-q3-watch: {TICKER} {QUARTER} (Release_Date {det.get('release_date')}) — bus question "
        f"'{TOPIC}' + Discord {'OK' if st.get('discord_ok') else 'LỖI'}.")
    return "fired"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="đọc BQ thật, không post, không ghi state")
    ap.add_argument("--quiet", action="store_true", help="không in dòng OK khi chưa có gì")
    args = ap.parse_args()
    try:
        res = run(dry_run=args.dry_run)
    except Exception as ex:   # WARN-only: tuyệt đối không làm đổ chuỗi 19:00
        print(f"WARN pnj-q3-watch: lỗi không lường trước — {type(ex).__name__}: {ex}")
        return 0
    if res in ALERT_RESULTS:
        # bq_freshness_check.sh grep tiền tố này ⇒ notify Discord (không chỉ nằm trong log, §29)
        print(f"ALERT pnj-q3-watch: {res} — watcher KHÔNG hoạt động đúng, trigger review PNJ Q3 có thể "
              f"bị bỏ lỡ; xem dòng WARN phía trên (lỗi thật), sửa tay rồi chạy lại bin/pnj_q3_review_watch.py.")
    if not args.quiet and res in ("not_yet", "already_fired"):
        print(f"OK   pnj-q3-watch: {res} ({TICKER} {QUARTER})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
