#!/usr/bin/env python3
"""discretionary_accumulation_inject.py — chèn TỰ ĐỘNG lệnh gom low-liquidity discretionary
vào plan_<account>_<plan_date>.json (book=DISCRETIONARY_SPECIAL), thay cho việc chèn thủ công
từng tranche (case TV1 tranche 1 hiện phải chèn tay).

Cơ chế (playbook Taylor 2026-07-24, memo lowliq_execution_playbook_20260724.md):
  - Mỗi vị thế đang gom = 1 state file data/trade_plans/discretionary/state_<TICKER>_<account>.json.
  - Với mỗi state active: đọc VỊ THẾ THẬT từ broker (nguồn chân lý filled_qty) + giá/KL phiên
    gần nhất từ DNSE live (KHÔNG BQ — same-day, coding_guidelines §6), gọi engine
    trading_bot.discretionary_accumulation.compute_session_order → chèn lệnh vào plan.
  - IDEMPOTENT: chạy lại trong ngày KHÔNG chèn trùng, KHÔNG đếm 2 lần filled (filled luôn tính
    lại từ broker, ledger chỉ để audit).
  - FAIL-SAFE: thiếu broker/giá/KL → KHÔNG chèn lệnh (không mua bởi thiếu thông tin).
  - KHÔNG chạm kế toán V2.4 (chỉ chèn order book=DISCRETIONARY_SPECIAL, tách hẳn).

Chạy SAU khi DollarBill ghi plan (dispatch --bg ~19:0x) và TRƯỚC send_plan_report 21:00, để
user duyệt plan đã có sẵn lệnh gom. Plan vẫn requires_user_approval → Mafee chỉ execute sau khi
user duyệt (human gate giữ nguyên).

Usage:
  discretionary_accumulation_inject.py --account SpaceX [--plan-date YYYY-MM-DD] [--dry-run]
  (bỏ --plan-date → tự dùng next_trading_day())
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WC_ROOT)

from trading_bot.discretionary_accumulation import compute_session_order, validate_state, BOOK
from trading_bot.vn_market import session_phase, now_ict

# Phiên đang giao dịch (09:00–14:45 T2-T6) → day_volume của DNSE là KL DỞ DANG. Cơ chế
# opportunistic (compute_session_order) giả định day_volume là KHỐI LƯỢNG CẢ PHIÊN đã chốt để
# đo "người bán có xuất hiện không"; đọc giữa phiên = KL chưa đủ → quyết định opportunistic sai.
# → injector LIVE TỪ CHỐI chạy trong các phiên này (cron thật chạy 20:30 ICT = CLOSED). PRE
# (trước 09:00) và CLOSED (sau 14:45 / cuối tuần / lễ) đều an toàn: DNSE report phiên hoàn tất.
_SESSION_OPEN_PHASES = {"ATO", "MORNING", "LUNCH", "AFTERNOON", "ATC"}

DISC_DIR = os.path.join(WC_ROOT, "data", "trade_plans", "discretionary")
PLAN_DIR = os.path.join(WC_ROOT, "data", "trade_plans")


def _atomic_write_json(path, obj):
    """tmp + os.replace — kill giữa chừng không để lại file dở (coding_guidelines §5)."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def next_trading_day_str():
    from trading_bot.vn_market import next_trading_day
    return str(next_trading_day(dt.date.today()))


def load_active_states(account):
    """Đọc mọi state_*_<account>.json status=active. Trả list (path, state)."""
    out = []
    for path in sorted(glob.glob(os.path.join(DISC_DIR, f"state_*_{account}.json"))):
        try:
            state = json.load(open(path, encoding="utf-8"))
        except Exception as exc:
            print(f"  [WARN] state file lỗi đọc, bỏ qua: {path}: {exc}")
            continue
        state["_state_file"] = os.path.relpath(path, WC_ROOT)
        if state.get("account") != account:
            print(f"  [WARN] {path}: account={state.get('account')} ≠ {account}, bỏ qua")
            continue
        if state.get("status") != "active":
            print(f"  [skip] {os.path.basename(path)}: status={state.get('status')}")
            continue
        try:
            validate_state(state)
        except ValueError as exc:
            print(f"  [WARN] {path}: state không hợp lệ ({exc}) — bỏ qua, KHÔNG chèn")
            continue
        out.append((path, state))
    return out


def broker_filled_qty(account, account_id, ticker, baseline):
    """filled_qty của CHƯƠNG TRÌNH = broker_total(ticker) − baseline_qty_before_program.
    None nếu không đọc được broker (fail-safe)."""
    try:
        from trading_bot.brokers import DNSEBroker
        b = DNSEBroker(account_id=account_id, credentials_file=None, label=account)
        b.connect()
        positions = b.get_positions()
    except Exception as exc:
        print(f"  [FAILSAFE] không đọc được broker positions ({ticker}): {exc}")
        return None, None
    total = int((positions.get(ticker) or {}).get("total", 0) or 0)
    return max(0, total - int(baseline)), b


def prev_session_market(broker, ticker):
    """Giá + turnover phiên hoàn tất gần nhất từ DNSE live (day_volume × last).
    Trả (turnover_vnd, price_vnd) — (None, None) nếu thiếu (fail-safe)."""
    try:
        q = broker.get_quote(ticker)
    except Exception as exc:
        print(f"  [FAILSAFE] DNSE quote {ticker} lỗi: {exc}")
        return None, None
    price = getattr(q, "last", None)
    vol = getattr(q, "day_volume", None)
    if not price or not vol or price <= 0 or vol <= 0:
        print(f"  [FAILSAFE] {ticker}: thiếu giá ({price}) hoặc KL ({vol}) từ DNSE")
        return None, None
    return float(vol) * float(price), float(price)


def already_injected(plan, ticker):
    """Dedup: đã có order DISCRETIONARY_SPECIAL cho ticker này trong plan chưa?
    (bắt cả tranche chèn tay lẫn lần chạy trước — chống chèn trùng bất kể id scheme.)"""
    for o in plan.get("orders", []):
        if o.get("ticker") == ticker and o.get("book") == BOOK:
            return o.get("id")
    return None


def process_account(account, plan_date, dry_run):
    profile_path = os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json")
    accounts = json.load(open(profile_path, encoding="utf-8")).get("accounts", [])
    profile = next((a for a in accounts if a.get("label") == account), None)
    if not profile:
        print(f"[ERR] không tìm thấy account {account} trong trading_bot_accounts.json")
        return 1
    account_id = profile.get("account_id")  # key CHUẨN trong secrets (KHÔNG phải account_no)

    states = load_active_states(account)
    if not states:
        print(f"[inject] {account} {plan_date}: KHÔNG có state active — no-op.")
        return 0

    plan_path = os.path.join(PLAN_DIR, f"plan_{account}_{plan_date}.json")
    if not os.path.exists(plan_path):
        print(f"[inject] {account} {plan_date}: CHƯA có plan file ({plan_path}) — "
              "DollarBill chưa ghi xong? no-op (sẽ retry lần chạy sau).")
        return 0
    plan = json.load(open(plan_path, encoding="utf-8"))
    if str(plan.get("plan_date")) != plan_date:
        print(f"[inject] {account}: plan_date trong file ({plan.get('plan_date')}) ≠ "
              f"{plan_date} — KHÔNG chèn (tránh ghi nhầm ngày).")
        return 1
    plan.setdefault("orders", [])

    now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    n_injected = 0
    broker = None

    for state_path, state in states:
        ticker = state["ticker"]
        print(f"--- {ticker} ({os.path.basename(state_path)}) ---")

        # dedup 1: order đã có trong plan
        existing = already_injected(plan, ticker)
        if existing:
            print(f"  [skip] đã có order {BOOK} cho {ticker} trong plan (id={existing}) — không chèn trùng.")
            continue
        # dedup 2: ledger đã ghi plan_date này
        ledger = state.setdefault("ledger", [])
        if any(e.get("plan_date") == plan_date for e in ledger):
            print(f"  [skip] ledger đã có bản ghi cho {plan_date} — không chèn trùng.")
            continue

        baseline = int(state.get("baseline_qty_before_program", 0) or 0)
        filled, broker = broker_filled_qty(account, account_id, ticker, baseline)
        prev_turnover = prev_price = None
        if filled is not None and broker is not None:
            prev_turnover, prev_price = prev_session_market(broker, ticker)

        order, decision = compute_session_order(
            state, filled, prev_turnover, prev_price, plan_date, now_iso)
        print(f"  decision: {decision['action']} — {decision['reason']}")

        # đánh dấu completed vào state nếu engine báo (rule e: không mua quá)
        if decision.get("mark_completed") and state.get("status") == "active":
            state["status"] = "completed"
            state["completed_at"] = now_iso
            state["completed_reason"] = decision["reason"]
            if not dry_run:
                _atomic_write_json(state_path, {k: v for k, v in state.items()
                                                if not k.startswith("_")})
            print(f"  → state {ticker} đánh dấu COMPLETED.")
            continue

        if order is None:
            # skip/failsafe/halted/inactive: KHÔNG ghi ledger (để lần sau còn thử lại) —
            # trừ khi bạn muốn audit; ghi 1 dòng history không-inject nhẹ để trace.
            state.setdefault("history_noninject", []).append(
                {"plan_date": plan_date, "action": decision["action"],
                 "reason": decision["reason"], "at": now_iso})
            if not dry_run:
                _atomic_write_json(state_path, {k: v for k, v in state.items()
                                                if not k.startswith("_")})
            continue

        # chèn order + ghi ledger (audit — KHÔNG dùng để đếm filled)
        plan["orders"].append(order)
        ledger.append({
            "plan_date": plan_date, "injected_qty": order["qty"],
            "limit_price_vnd": order["limit_price_vnd"], "order_id": order["id"],
            "filled_before": decision.get("filled_qty"),
            "opportunistic": decision.get("opportunistic"), "at": now_iso})
        n_injected += 1
        print(f"  [INJECT] {ticker} {order['qty']}cp @ ≤{order['limit_price_vnd']:,} "
              f"(filled {decision['filled_qty']}/{decision.get('target')}, "
              f"opportunistic={decision.get('opportunistic')})")

        if not dry_run:
            _atomic_write_json(state_path, {k: v for k, v in state.items()
                                            if not k.startswith("_")})

    if n_injected and not dry_run:
        plan.setdefault("discretionary_inject_log", []).append(
            {"at": now_iso, "n_injected": n_injected, "by": "discretionary_accumulation_inject.py"})
        _atomic_write_json(plan_path, plan)
        print(f"[inject] {account} {plan_date}: ĐÃ chèn {n_injected} lệnh vào {plan_path}.")
    elif n_injected and dry_run:
        print(f"[inject] {account} {plan_date}: DRY-RUN — sẽ chèn {n_injected} lệnh (không ghi).")
    else:
        print(f"[inject] {account} {plan_date}: không chèn lệnh nào.")
    return 0


def session_guard_ok(dry_run):
    """Cổng phiên: LIVE inject chỉ được chạy khi phiên đã ĐÓNG (day_volume đã chốt).
    - Phiên đang mở (ATO/MORNING/LUNCH/AFTERNOON/ATC) + LIVE → TỪ CHỐI (return False).
    - Phiên đang mở + dry-run → CHO chạy nhưng in WARN (dry-run không ghi gì; số chỉ minh hoạ).
    - PRE/CLOSED/cuối tuần/lễ → CHO chạy.
    Đặt ở main() (điểm vào lệnh thật), KHÔNG ở process_account() — để selfcheck gọi thẳng
    process_account() bất kể giờ nào vẫn chạy được (FakeBroker, không đọc DNSE thật)."""
    phase, _ = session_phase()
    now_str = now_ict().strftime("%F %H:%M ICT")
    if phase not in _SESSION_OPEN_PHASES:
        return True
    if dry_run:
        print(f"  [WARN] {now_str} phiên {phase} ĐANG MỞ — dry-run vẫn chạy, nhưng day_volume "
              "là KL DỞ DANG → cờ opportunistic chỉ MINH HOẠ, KHÔNG dùng làm quyết định thật.")
        return True
    print(f"[GUARD] {now_str} phiên {phase} đang giao dịch (09:00–14:45 T2-T6) — injector LIVE "
          "TỪ CHỐI chạy giữa phiên: day_volume chưa chốt → opportunistic sai. Chỉ chạy SAU đóng "
          "cửa (cron 20:30 ICT) hoặc dùng --dry-run để test.")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--plan-date", default=None, help="YYYY-MM-DD; bỏ trống → next_trading_day()")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not session_guard_ok(args.dry_run):
        return 2   # phân biệt guard-block với lỗi thật (rc=1) và thành công (rc=0)
    plan_date = args.plan_date or next_trading_day_str()
    return process_account(args.account, plan_date, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
