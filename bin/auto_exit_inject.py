#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""auto_exit_inject.py — chèn TỰ ĐỘNG đề xuất SELL vào plan_<account>_<T+1>.json khi sleeve
LAG/BAL/CAPIT tới mốc exit cố định (`auto_exit_rules.py`) — chỉ đạo user qua Mike 2026-09-30
(job Taylor_20260930_080814), sau khi phát hiện lệch backtest-pin/live: `capit_episode.py` tự
ghi rõ từ 07-31 rằng đường LIVE KHÔNG có dòng code nào bán CAPIT; `portfolio_status.py` trước
bản vá này hiển thị cửa LAG T+14..T+20 — không khớp số nào trong backtest đã pin.

Cơ chế (mirror `discretionary_accumulation_inject.py` / `merge_park_orders.py`):
  - Chạy SAU khi DollarBill ghi plan T+1 (~19:0x), TRƯỚC send_plan_report 21:00 — user duyệt
    plan ĐÃ có sẵn đề xuất bán. KHÔNG đặt lệnh ra sàn — chỉ chèn ĐỀ XUẤT vào bản nháp; Mafee chỉ
    thực thi plan-bound SAU khi user duyệt (human-in-the-loop giữ nguyên, không bị bỏ qua).
  - REFUSE (rc=1, không ghi gì) nếu plan đã có `approved_by` — không mutate plan đã ký.
  - FAIL-SAFE: thiếu broker/journal/giá ⇒ KHÔNG chèn lệnh cho ticker đó (không đoán giá/qty).
  - IDEMPOTENT: dedup theo (ticker, book, side=sell) đã có trong orders[]; nhắc CAPIT T+55 dedup
    qua field `reminder_55_sent_at` ghi thẳng vào `data/capit_episode.json` (gửi MỘT LẦN/episode).
  - Từ chối chạy GIỮA phiên (chỉ PRE/CLOSED) — vị thế/KL broker giữa phiên chưa chốt.

Nguồn số exit: `auto_exit_rules.py` (đọc trước khi sửa số ở đây — cùng hằng số dùng bởi
`portfolio_status.py` để hiển thị cảnh báo, tránh 2 bản chép tay lệch nhau).

Usage:
  auto_exit_inject.py --account SpaceX [--plan-date YYYY-MM-DD] [--dry-run]
"""
import argparse
import dataclasses
import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)

import auto_exit_rules as rules  # noqa: E402
import capit_episode  # noqa: E402
from portfolio_status import (  # noqa: E402
    account_no_for, broker_positions_with_cost, count_trading_days,
    lag_entry_dates, _first_fill_dates,
)
from trading_bot.plan import PlannedOrder  # noqa: E402
from trading_bot.vn_market import now_ict, next_trading_day, session_phase, is_holiday  # noqa: E402

_ICT_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
PLAN_DIR = os.path.join(WC_ROOT, "data", "trade_plans")


def _atomic_write_json(path, obj):
    """tmp + os.replace — kill giữa chừng không để lại file dở (coding_guidelines §5)."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _session_ok(now=None):
    """PRE/CLOSED (hoặc ngoài ngày giao dịch) mới an toàn đọc vị thế broker làm bằng chứng
    'đã giữ đủ N phiên' — giữa phiên KL/qty còn dở dang (mirror discretionary injector)."""
    now = now or now_ict()
    if now.weekday() >= 5 or is_holiday(now.date()):
        return True
    return session_phase(now)[0] in ("PRE", "CLOSED")


def _already_has_sell(plan, ticker, book):
    for o in plan.get("orders", []):
        if o.get("ticker") == ticker and o.get("book") == book and o.get("side") == "sell":
            return o.get("id")
    return None


def _make_order(order_id, ticker, qty, ref_price, book, play_type, note):
    o = PlannedOrder(id=order_id, ticker=ticker, side="sell", qty=int(qty),
                      ref_price=float(ref_price), book=book, play_type=play_type,
                      priority=1, note=note)
    return dataclasses.asdict(o)


def _lag_bal_candidates(asof_date, positions, book, entry_dates, threshold_fn):
    """[(ticker, qty, ref_price, sessions_held)] cho `book` (LAG/BAL) đã tới mốc exit.
    FAIL-SAFE: thiếu ref_price/entry hợp lệ/không tính được phiên ⇒ bỏ qua ticker đó, in lý do."""
    out = []
    for tk, entry_str in entry_dates.items():
        pos = positions.get(tk)
        if not pos or pos.get("qty", 0) <= 0:
            continue  # không còn nắm giữ — đã thoát hoặc chưa từng khớp, không phải fail-safe
        try:
            entry = dt.date.fromisoformat(entry_str)
        except ValueError:
            print(f"  [FAILSAFE] {book} {tk}: entry_date lỗi ({entry_str!r}) — bỏ qua")
            continue
        sessions = count_trading_days(entry, asof_date)
        if sessions is None:
            print(f"  [FAILSAFE] {book} {tk}: không tính được sessions_held (vn_market import lỗi)")
            continue
        if not threshold_fn(sessions):
            continue
        ref_price = pos.get("marketPrice") or pos.get("avg_cost")
        if not ref_price or ref_price <= 0:
            print(f"  [FAILSAFE] {book} {tk}: thiếu ref_price (marketPrice/avg_cost) — KHÔNG chèn")
            continue
        out.append((tk, int(pos["qty"]), float(ref_price), sessions))
    return out


def _send_capit_reminder(ep, sessions_held):
    """Post reminder lên bus — GUARD test-mode (coding_guidelines §5b): selfcheck/pytest set
    `AUTO_EXIT_TEST_MODE=1` để KHÔNG ghi lên bus thật (sự cố thật 2026-09-30: selfcheck lần đầu
    của chính file này ghi nhầm episode giả `CAPIT-TEST2` vào `mike/bus/inbox/Taylor.jsonl`)."""
    remaining = rules.CAPIT_EXIT_SESSIONS - sessions_held
    payload = json.dumps({
        "episode_id": ep["episode_id"], "sessions_held": sessions_held,
        "remaining_sessions_to_auto_exit": remaining,
        "message": (f"Episode CAPIT {ep['episode_id']} đã giữ {sessions_held} phiên, còn "
                    f"{remaining} phiên tới mốc auto-exit cố định {rules.CAPIT_EXIT_SESSIONS} "
                    f"phiên. PM can thiệp trước nếu muốn giữ tiếp — nếu không, lệnh bán TOÀN BỘ "
                    f"rổ sẽ tự chèn vào plan nháp khi tới mốc."),
    }, ensure_ascii=False)
    if os.environ.get("AUTO_EXIT_TEST_MODE") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        print(f"  [TEST-MODE] bỏ qua post bus thật, payload={payload}")
        return
    try:
        subprocess.run([os.path.join(WC_ROOT, "mike", "bin", "append_event.sh"), "Taylor",
                        "status", "capit-episode-approaching-auto-exit", payload], check=False)
    except OSError as exc:
        print(f"  [WARN] không post được reminder lên bus: {exc}")


def process_account(account, plan_date, signal_date, dry_run):
    account_no = account_no_for(account)
    if not account_no:
        print(f"[ERR] không tìm được account_no cho {account}")
        return 1

    plan_path = os.path.join(PLAN_DIR, f"plan_{account}_{plan_date}.json")
    if not os.path.exists(plan_path):
        print(f"[auto-exit] {account} {plan_date}: CHƯA có plan file — no-op (retry lần sau).")
        return 0
    plan = json.load(open(plan_path, encoding="utf-8"))
    if str(plan.get("plan_date")) != plan_date:
        print(f"[auto-exit] {account}: plan_date file ({plan.get('plan_date')}) ≠ {plan_date} "
              f"— KHÔNG chèn (tránh ghi nhầm ngày).")
        return 1
    if plan.get("approved_by"):
        print(f"[auto-exit] {account}: plan ĐÃ DUYỆT (approved_by={plan['approved_by']!r}) "
              f"— REFUSE, không mutate plan đã ký.")
        return 1
    plan.setdefault("orders", [])

    positions = broker_positions_with_cost(account_no, signal_date) or {}
    now_iso = dt.datetime.now(_ICT_TZ).isoformat(timespec="seconds")
    injected = []

    # ---- LAG: T+25 cố định (pt_v23_audit_2014.py:2060,2062) ----
    for tk, qty, ref_price, sessions in _lag_bal_candidates(
            dt.date.fromisoformat(signal_date), positions, "LAG",
            lag_entry_dates(account), rules.lag_should_exit):
        existing = _already_has_sell(plan, tk, "LAG")
        if existing:
            print(f"  [skip] {tk}: đã có sell LAG trong plan (id={existing})")
            continue
        note = (f"AUTO-EXIT LAG: giữ {sessions} phiên ≥ mốc cố định {rules.LAG_EXIT_SESSIONS} "
                f"(pt_v23_audit_2014.py:2060) — đề xuất thoát toàn bộ")
        plan["orders"].append(_make_order(f"SELL-{tk}-AUTOEXIT-LAG", tk, qty, ref_price,
                                          "LAG", "LAG_AUTO_EXIT", note))
        injected.append((tk, "LAG", sessions))
        print(f"  [inject] SELL {tk} qty={qty} book=LAG ({note})")

    # ---- BAL: T+45 cố định (pt_v23_audit_2014.py:2008) ----
    for tk, qty, ref_price, sessions in _lag_bal_candidates(
            dt.date.fromisoformat(signal_date), positions, "BAL",
            _first_fill_dates(account, "BAL"), rules.bal_should_exit):
        existing = _already_has_sell(plan, tk, "BAL")
        if existing:
            print(f"  [skip] {tk}: đã có sell BAL trong plan (id={existing})")
            continue
        note = (f"AUTO-EXIT BAL: giữ {sessions} phiên ≥ mốc cố định {rules.BAL_EXIT_SESSIONS} "
                f"(pt_v23_audit_2014.py:2008) — đề xuất thoát toàn bộ")
        plan["orders"].append(_make_order(f"SELL-{tk}-AUTOEXIT-BAL", tk, qty, ref_price,
                                          "BAL", "BAL_AUTO_EXIT", note))
        injected.append((tk, "BAL", sessions))
        print(f"  [inject] SELL {tk} qty={qty} book=BAL ({note})")

    # ---- CAPIT: T+60 cố định (CAPIT_HOLD, pt_v22_dt5g.py:123) + nhắc T+55 ----
    ledger = capit_episode._load(capit_episode.LEDGER_PATH)
    ep = capit_episode._open_episode(ledger)
    if ep is not None:
        sessions_held = ep.get("sessions_held")
        if rules.capit_should_exit(sessions_held):
            qty_map = (ep.get("qty_per_account") or {}).get(account, {})
            for tk, planned_qty in qty_map.items():
                pos = positions.get(tk)
                qty = int(pos["qty"]) if pos and pos.get("qty", 0) > 0 else int(planned_qty or 0)
                if qty <= 0:
                    continue
                existing = _already_has_sell(plan, tk, "CAPIT")
                if existing:
                    print(f"  [skip] {tk}: đã có sell CAPIT trong plan (id={existing})")
                    continue
                ref_price = (pos or {}).get("marketPrice") or (pos or {}).get("avg_cost")
                if not ref_price or ref_price <= 0:
                    print(f"  [FAILSAFE] CAPIT {tk}: thiếu ref_price — KHÔNG chèn")
                    continue
                note = (f"AUTO-EXIT CAPIT: episode {ep['episode_id']} giữ {sessions_held} phiên "
                        f"≥ mốc cố định {rules.CAPIT_EXIT_SESSIONS} (CAPIT_HOLD, "
                        f"pt_v22_dt5g.py:123) — đề xuất thoát TOÀN BỘ rổ")
                plan["orders"].append(_make_order(f"SELL-{tk}-AUTOEXIT-CAPIT", tk, qty, ref_price,
                                                  "CAPIT", "CAPIT_AUTO_EXIT", note))
                injected.append((tk, "CAPIT", sessions_held))
                print(f"  [inject] SELL {tk} qty={qty} book=CAPIT ({note})")
        elif rules.capit_should_remind(sessions_held) and not ep.get("reminder_55_sent_at"):
            print(f"  [reminder] episode {ep['episode_id']}: {sessions_held} phiên ≥ "
                  f"{rules.CAPIT_REMINDER_SESSIONS} — gửi nhắc trước lên bus")
            if not dry_run:
                _send_capit_reminder(ep, sessions_held)
                ep["reminder_55_sent_at"] = now_iso
                capit_episode._save(capit_episode.LEDGER_PATH, ledger)

    if injected:
        notes = plan.setdefault("auto_exit_inject_notes", [])
        notes.append({"at": now_iso, "injected": [
            {"ticker": t, "book": b, "sessions_held": s} for t, b, s in injected]})
        if not dry_run:
            _atomic_write_json(plan_path, plan)
            print(f"[auto-exit] {account}: đã ghi {len(injected)} lệnh SELL vào {plan_path}")
        else:
            print(f"[auto-exit] {account}: DRY-RUN — {len(injected)} lệnh SELL sẽ chèn, KHÔNG ghi.")
    else:
        print(f"[auto-exit] {account} {plan_date}: không có candidate tới mốc exit.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--plan-date", default=None, help="mặc định = phiên giao dịch kế tiếp")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    today = now_ict().date()
    signal_date = today.isoformat()
    plan_date = args.plan_date or str(next_trading_day(today))

    if not _session_ok():
        print("[auto-exit] đang trong phiên giao dịch — vị thế/KL chưa chốt, từ chối chạy "
              "giữa phiên. Chạy lại sau 14:45 ICT.")
        return 1

    return process_account(args.account, plan_date, signal_date, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
