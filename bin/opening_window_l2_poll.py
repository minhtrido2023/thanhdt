#!/usr/bin/env python3
"""Poll L2 (10 mức bid/ask) tần suất cao CHỈ trong cửa sổ đầu phiên MORNING (mặc định
09:14:30-09:20:00 ICT), cho các mã có lệnh THẬT (account live) dự kiến đặt ở chu kỳ đầu tiên.

Nhánh quan sát RIÊNG cho chương trình paper `order_book_execution_shadow` (charter
`kb/paper_programs_charter/order_book_execution_shadow.md`), theo đề xuất §4
`agents/Taylor/research/opening_window_limit_20260926/FINDINGS.md` — dispatch Mike
job=Taylor_20260925_174424, user duyệt 2026-09-26.

BỐI CẢNH: `orderbook_shadow_*.jsonl` (schema `orderbook_execution_v1`, ghi bởi
`Executor._order_book_shadow`) chỉ chụp 1 snapshot / lần ĐẶT LỆNH thật — không đủ để dựng
quỹ đạo spread theo thời gian trong vài phút đầu phiên. Script này KHÔNG sửa executor, KHÔNG
đường gọi broker mới (dùng lại `Broker.get_quote()` — cơ chế snapshot L2 sẵn có, xem
`trading_bot/brokers.py::DNSEBroker._log_l2`), KHÔNG đặt lệnh: `quote_only=True`,
`account_id=None` ⇒ mọi bản ghi phụ nó tạo ra trong `dnse_raw_<date>.jsonl` (kind=quote_l2,
throttle riêng theo instance) mang `account_no=None`/`account_label="opening_window_probe"` —
không khớp account_no thật nào nên §12 (mọi consumer lọc theo account_no) tự bỏ qua, không cần
sửa consumer nào.

Ghi ra file RIÊNG `data/execution_logs/orderbook_opening_<date>.jsonl` (schema
`orderbook_l2_opening_v1`, field `stratum="opening_cycle"`) — TÁCH khỏi nhánh toàn-phiên hiện
có, đúng bài học §3a/§28 (coding_guidelines/FINDINGS.md): không trộn 2 tầng dữ liệu khác quy mô
mẫu/quy luật thống kê vào chung 1 stream.

behavior_contract = LOG_ONLY_NO_BROKER_PATH (giống chương trình mẹ): không field nào ở đây
được đọc lại bởi `_decide_cross`, `_decide_cross_adaptive`, `_child_qty`, hay bất kỳ đường đặt
lệnh nào — chỉ đọc quote, không có đường gọi khác của broker.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402

WC_ROOT = os.environ.get("ORDER_BOOK_OPENING_WC_ROOT") or wc_paths.find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)

from trading_bot.vn_market import now_ict  # noqa: E402
from trading_bot.plan import load_plan  # noqa: E402

EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
ACCOUNTS_FILE = os.environ.get(
    "ORDER_BOOK_OPENING_ACCOUNTS_FILE",
    os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json"),
)
PROBE_LABEL = "opening_window_probe"  # account_label riêng, KHÔNG khớp account_no thật nào
SCHEMA_VERSION = "orderbook_l2_opening_v1"


def load_live_accounts(path=ACCOUNTS_FILE):
    """Account THẬT (mode="live", broker DNSE, không bị tắt) — nguồn lệnh cần quan sát.

    Fail-safe: file thiếu/hỏng → [] (script gọi nơi này tự coi là "không có gì để poll hôm
    nay", không raise — đây là job nền, lỗi đọc config không được làm treo cron).
    """
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []
    out = []
    for a in data.get("accounts", []):
        if a.get("mode") != "live":
            continue
        if a.get("enabled") is False:
            continue
        if (a.get("broker") or "").lower() != "dnse":
            continue
        out.append(a)
    return out


def collect_opening_tickers(accounts, plan_date, load_plan_fn=load_plan):
    """ticker -> sorted[account_label,...] có lệnh thật hôm nay (mọi order trong plan, không
    riêng cycle nào — §4 dispatch không hạn hẹp thêm theo cycle: mọi lệnh của account live có
    thể là ứng viên đặt ở chu kỳ ĐẦU MORNING). Account thiếu plan/HOLD hôm nay → bỏ qua
    (load_plan trả None, không raise) — 1 account lỗi plan không được chặn account khác."""
    by_ticker = {}
    for a in accounts:
        label = a.get("label")
        try:
            plan = load_plan_fn(plan_date, account=label)
        except Exception:
            continue
        if not plan or not getattr(plan, "orders", None):
            continue
        for o in plan.orders:
            by_ticker.setdefault(o.ticker, set()).add(label)
    return {t: sorted(labels) for t, labels in by_ticker.items()}


def snapshot_record(ticker, accounts_for_ticker, plan_date, poll_seq, q, now=None):
    """1 bản ghi từ `Quote` trả về bởi `Broker.get_quote()`. `q.l2_snapshot` có thể None
    (lỗi mạng/snapshot rỗng, xem `_log_l2`) — vẫn ghi 1 dòng `snapshot_valid=False`, THUẦN
    quan sát, không suy diễn nguyên nhân (§29): không rõ vì sao thì nói rõ là không rõ.

    `now` nhận từ caller (không tự gọi `now_ict()`) — để `poll_window()` tiêm cùng MỘT mốc
    giờ giả lập được cho selfcheck (§19 verify-before-done: thời gian là input, không phải
    side-effect ẩn trong hàm)."""
    snap = getattr(q, "l2_snapshot", None)
    rec = {
        "schema_version": SCHEMA_VERSION,
        "stratum": "opening_cycle",
        "plan_date": plan_date,
        "accounts": accounts_for_ticker,
        "ticker": ticker,
        "poll_seq": poll_seq,
        "polled_at": (now or now_ict()).isoformat(timespec="milliseconds"),
        "snapshot_valid": bool(snap),
    }
    if snap:
        rec["snapshot"] = snap
    return rec


def append_records(records, out_path):
    if not records:
        return
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def poll_window(tickers_map, broker, out_path, poll_sec, window_start, window_end,
                now_fn=now_ict, sleep_fn=time.sleep):
    """Vòng lặp poll tần suất cao, CHỈ chạy trong [window_start, window_end).

    Đã ở TRONG cửa sổ khi khởi động → bắt đầu ngay. Cửa sổ đã QUA (script khởi động trễ,
    vd cron trượt) → không lùi ngày/không đoán bù, thoát 0 (WATCH, không phải lỗi) — bù dữ
    liệu thiếu 1 phiên rẻ hơn poll SAI cửa sổ (giá đã chạy xa, quan sát vô nghĩa).
    """
    poll_seq = 0
    total_written = 0
    while True:
        now = now_fn()
        t = now.time()
        if t < window_start:
            sleep_fn(min(poll_sec, _seconds_until(now, window_start)))
            continue
        if t >= window_end:
            break
        round_start = time.monotonic()
        records = []
        for ticker, accounts_for_ticker in tickers_map.items():
            try:
                q = broker.get_quote(ticker)
            except Exception:
                # Nuốt lỗi mạng/API — telemetry KHÔNG được crash cron; mã tiếp theo vẫn poll.
                continue
            records.append(snapshot_record(ticker, accounts_for_ticker, str(now.date()),
                                            poll_seq, q, now=now))
        append_records(records, out_path)
        total_written += len(records)
        poll_seq += 1
        elapsed = time.monotonic() - round_start
        sleep_fn(max(0.0, poll_sec - elapsed))
    return total_written


def _seconds_until(now, target_time):
    target = dt.datetime.combine(now.date(), target_time)
    return max(0.0, (target - now).total_seconds())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, mặc định hôm nay ICT")
    ap.add_argument("--poll-sec", type=float, default=7.0)
    ap.add_argument("--window-start", default="09:14:30")
    ap.add_argument("--window-end", default="09:20:00")
    ap.add_argument("--dry-run", action="store_true",
                    help="chỉ in danh sách mã sẽ poll, không gọi broker/không ghi file")
    args = ap.parse_args()

    plan_date = args.date or str(now_ict().date())
    window_start = dt.datetime.strptime(args.window_start, "%H:%M:%S").time()
    window_end = dt.datetime.strptime(args.window_end, "%H:%M:%S").time()

    accounts = load_live_accounts()
    if not accounts:
        print("opening-window poll: không có account live nào (config trống/tắt) — bỏ qua hôm nay")
        return 0
    tickers_map = collect_opening_tickers(accounts, plan_date)
    if not tickers_map:
        print(f"opening-window poll {plan_date}: không có lệnh thật nào hôm nay — bỏ qua "
              f"(WATCH, không phải lỗi — account live có thể ở ngày HOLD)")
        return 0

    print(f"opening-window poll {plan_date}: {len(tickers_map)} mã · cửa sổ "
          f"{args.window_start}-{args.window_end} ICT · cadence {args.poll_sec}s")
    for t, accs in sorted(tickers_map.items()):
        print(f"  {t}: {','.join(accs)}")
    if args.dry_run:
        return 0

    from trading_bot.brokers import get_quote_source
    try:
        broker = get_quote_source("dnse", credentials_file=None)
        broker.label = PROBE_LABEL
        broker.account_id = None
        broker.connect()
    except Exception as e:
        print(f"opening-window poll: KHÔNG kết nối được broker quote-only: {e} — bỏ qua hôm nay")
        return 1

    out_path = os.environ.get(
        "ORDER_BOOK_OPENING_TEST_SINK",
        os.path.join(EXEC_DIR, f"orderbook_opening_{plan_date}.jsonl"),
    )
    n = poll_window(tickers_map, broker, out_path, args.poll_sec, window_start, window_end)
    print(f"opening-window poll {plan_date}: ghi {n} bản ghi vào {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
