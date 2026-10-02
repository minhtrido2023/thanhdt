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
  - REFUSE (rc=1, không ghi gì) nếu plan đã có `approved_by` HOẶC bí danh `approved_by_user`
    (trading_bot/plan.py:264-265 coi 2 field này tương đương — đọc raw JSON ở đây nên phải tự
    chuẩn hoá, không mutate plan đã ký qua đường sửa tay).
  - FAIL-SAFE: thiếu broker/journal/giá ⇒ KHÔNG chèn lệnh cho ticker đó (không đoán giá/qty).
    CAPIT: ticker trong `qty_per_account` mà KHÔNG còn vị thế broker (đã thoát qua đường khác)
    ⇒ bỏ qua, KHÔNG fallback về qty kế hoạch cũ (tránh SELL khống cổ phiếu không còn có).
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
    book_lot_snapshot,
)
from trading_bot.plan import PlannedOrder  # noqa: E402
from trading_bot.vn_market import now_ict, next_trading_day, session_phase, is_holiday  # noqa: E402

_ICT_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
PLAN_DIR = os.path.join(WC_ROOT, "data", "trade_plans")
BLOCK_ALERT_STATE_PATH = os.path.join(WC_ROOT, "data", "auto_exit_block_alert_state.json")


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


def _lag_bal_candidates(asof_date, positions, book, lots, threshold_fn):
    """([(ticker, qty, ref_price, sessions_held)], blocked) cho `book` (LAG/BAL) đã tới mốc exit.
    `lots` = `book_lot_snapshot(account, book, asof=...)[0]` — {ticker: {qty, entry_date}} đã
    TÁCH ĐÚNG phần thuộc `book` này qua bootstrap+FIFO lot tracking (`park_holdings()`), KHÔNG
    phải tổng vị thế broker của mã đó (mã nằm lẫn nhiều book — vd VPB LAG+PARK cùng mã — tổng
    broker sẽ CHO QUA sai số lượng, bán khống cả phần book khác).
    `blocked` = [{'ticker','reason'}] cho mã bị guard qty-mismatch chặn (§29 — phải hiện ra cho
    người, KHÔNG chỉ in stdout, vì guard này có thể đang ÉM một mã THẬT SỰ đã tới hạn exit).
    FAIL-SAFE khác (entry_date lỗi/không tính được phiên/thiếu ref_price) vẫn chỉ in — cực hiếm
    (entry_date luôn có dạng ISO từ FIFO replay, ref_price gần như luôn có từ broker)."""
    out, blocked = [], []
    for tk, lot in lots.items():
        pos = positions.get(tk)
        if not pos or pos.get("qty", 0) <= 0:
            continue  # không còn nắm giữ — đã thoát hoặc chưa từng khớp, không phải fail-safe
        qty = lot["qty"]
        if qty > pos["qty"]:
            # Sổ lô (riêng book này) KHÔNG THỂ vượt tổng vị thế broker của mã — hai nguồn (jsonl
            # snapshot của broker_positions_with_cost vs live query của park_holdings) lệch nhau
            # tại đúng lúc đọc. Không đoán cắt bớt — bỏ qua, chờ lượt sau.
            reason = f"qty sổ lô ({qty}) > qty broker ({pos['qty']}) — hai nguồn lệch nhau"
            print(f"  [FAILSAFE] {book} {tk}: {reason}, KHÔNG chèn")
            blocked.append({"ticker": tk, "reason": reason})
            continue
        try:
            entry = dt.date.fromisoformat(lot["entry_date"])
        except ValueError:
            print(f"  [FAILSAFE] {book} {tk}: entry_date lỗi ({lot['entry_date']!r}) — bỏ qua")
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
        out.append((tk, int(qty), float(ref_price), sessions))
    return out, blocked


def _bal_stop_loss_candidates(asof_date, positions, lots):
    """([(ticker, qty, ref_price, pnl_pct)], blocked) cho vị thế BAL lỗ ≥20% trên giá vốn
    broker-native (avg_cost/marketPrice — coding_guidelines §6, KHÔNG tự tính lại từ fill log),
    ĐÃ giữ ≥ `rules.BAL_STOP_LOSS_MIN_HOLD` phiên (mirror min_hold của pin). `lots` cùng dạng/
    nguồn với `_lag_bal_candidates` — qty đã TÁCH ĐÚNG phần BAL của mã (xem docstring ở trên).
    `blocked` = [{'ticker','reason'}] cho mã bị guard qty-mismatch chặn (§29, cùng tinh thần
    `_lag_bal_candidates`). FAIL-SAFE khác (thiếu avg_cost/marketPrice, entry_date lỗi, không
    tính được sessions_held) vẫn chỉ in."""
    out, blocked = [], []
    for tk, lot in lots.items():
        pos = positions.get(tk)
        if not pos or pos.get("qty", 0) <= 0:
            continue  # không còn nắm giữ — đã thoát hoặc chưa từng khớp, không phải fail-safe
        qty = lot["qty"]
        if qty > pos["qty"]:
            reason = f"qty sổ lô ({qty}) > qty broker ({pos['qty']}) — hai nguồn lệch nhau"
            print(f"  [FAILSAFE] BAL {tk}: {reason}, KHÔNG tính stop-loss")
            blocked.append({"ticker": tk, "reason": reason})
            continue
        avg_cost = pos.get("avg_cost")
        market_price = pos.get("marketPrice")
        if not avg_cost or avg_cost <= 0 or not market_price or market_price <= 0:
            print(f"  [FAILSAFE] BAL {tk}: thiếu avg_cost/marketPrice hợp lệ — "
                  f"KHÔNG tính stop-loss")
            continue
        try:
            entry = dt.date.fromisoformat(lot["entry_date"])
        except ValueError:
            print(f"  [FAILSAFE] BAL {tk}: entry_date lỗi ({lot['entry_date']!r}) — bỏ qua stop-loss")
            continue
        sessions = count_trading_days(entry, asof_date)
        if sessions is None:
            print(f"  [FAILSAFE] BAL {tk}: không tính được sessions_held — bỏ qua stop-loss")
            continue
        pnl_pct = market_price / avg_cost - 1.0
        if not rules.bal_stop_loss_hit(pnl_pct, sessions):
            continue
        out.append((tk, int(qty), float(market_price), pnl_pct))
    return out, blocked


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


def _load_block_alert_state():
    try:
        with open(BLOCK_ALERT_STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _new_block_alert_lines(account, blocked_notes, capped_notes, today):
    """Lọc blocked/capped theo KEY (ticker,book,reason/capped_qty) đã alert ĐÚNG NGÀY hôm nay —
    mã bị chặn/cắt nhiều ngày liên tiếp với CÙNG nội dung chỉ lên Discord 1 lần/ngày, KHÔNG phải
    1 lần/lượt chạy cron (§29, arch-review vòng 3). Khoá có `reason`/`capped_qty` (vòng 4) — mã
    cùng ticker+book nhưng NỘI DUNG đổi trong ngày (reason khác, hoặc cắt xuống số khác ở lượt
    chạy sau) vẫn phải báo lại, không bị khoá cũ (ghi lúc 9:05) che mất lúc 21:00. Trả
    `(lines, state_mới_để_ghi)`; `lines` rỗng ⇒ không có gì MỚI để gửi."""
    state = _load_block_alert_state()
    acct_state = dict(state.get(account) or {})
    lines = []
    for b in blocked_notes:
        reason_s = str(b.get("reason") or "")[:150]
        key = f"{b.get('ticker')}|{b.get('book')}|blocked|{reason_s}"
        if acct_state.get(key) == today:
            continue
        lines.append(f"⛔ {b.get('ticker') or '(book-level)'} ({b.get('book','?')}): {reason_s}")
        acct_state[key] = today
    for c in capped_notes:
        key = f"{c.get('ticker')}|{c.get('book')}|capped|{c.get('capped_qty')}"
        if acct_state.get(key) == today:
            continue
        lines.append(f"⚠️ {c.get('ticker','?')} ({c.get('book','?')}): "
                     f"{c.get('desired_qty','?')}cp → {c.get('capped_qty','?')}cp")
        acct_state[key] = today
    state[account] = acct_state
    return lines, state


def _send_block_alert(account, blocked_notes, capped_notes):
    """Post cảnh báo lên bus + Discord `trading_daily` khi có candidate exit bị CHẶN hoặc CẮT —
    GUARD test-mode §5b (mirror `_send_capit_reminder`), MỘT guard duy nhất che cả 2 kênh. §29:
    mọi exit bị bỏ qua/cắt bớt PHẢI hiện ra cho NGƯỜI duyệt plan, không chỉ nằm im trong KB/log
    stdout của cron (arch-review vòng 3: không ai đọc bus mỗi ngày để duyệt plan). Dedup THEO
    NGÀY qua `_new_block_alert_lines` — mã bị chặn liên tiếp nhiều ngày không spam Discord mỗi
    lượt chạy."""
    payload = json.dumps({"account": account, "blocked": blocked_notes, "capped": capped_notes},
                         ensure_ascii=False)
    if os.environ.get("AUTO_EXIT_TEST_MODE") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        print(f"  [TEST-MODE] bỏ qua post bus/Discord thật, payload={payload}")
        return
    try:
        subprocess.run([os.path.join(WC_ROOT, "mike", "bin", "append_event.sh"), "Taylor",
                        "status", "auto-exit-candidate-blocked-or-capped", payload], check=False)
    except OSError as exc:
        print(f"  [WARN] không post được cảnh báo blocked/capped lên bus: {exc}")
    today = now_ict().date().isoformat()
    lines, new_state = _new_block_alert_lines(account, blocked_notes, capped_notes, today)
    if not lines:
        return
    msg = (f"🚨 auto-exit {account}: {len(lines)} mã bị CHẶN/CẮT (LAG/BAL/CAPIT), KHÔNG tự chèn "
           f"đủ lệnh — kiểm plan trước khi duyệt:\n" + "\n".join(lines))
    # §29 vòng 4 (arch-review): state dedup PHẢI ghi SAU khi xác nhận gửi Discord thành công
    # (mirror vendor_mismatch_alert.sh) — bản cũ ghi state TRƯỚC + `check=False` bỏ qua
    # returncode ⇒ notify_thread.sh lỗi (ccdb chết/topic sai) vẫn bị coi "đã cảnh báo hôm nay",
    # lượt chạy lại cùng ngày sẽ KHÔNG gửi lại và KHÔNG có WARN nào — cảnh báo mất vĩnh viễn.
    try:
        proc = subprocess.run([os.path.join(WC_ROOT, "mike", "bin", "notify_thread.sh"), msg,
                               "trading_daily"], capture_output=True, text=True)
    except OSError as exc:
        print(f"  [WARN] không post được notify_thread (OSError, KHÔNG ghi de-dup, lượt sau sẽ "
              f"thử lại): {exc}")
        return
    if proc.returncode != 0:
        _err = (proc.stderr or proc.stdout or "").strip()
        print(f"  [WARN] notify_thread.sh THẤT BẠI (rc={proc.returncode}) — KHÔNG ghi de-dup, "
              f"lượt sau sẽ thử lại. Lỗi thật: {_err}")
        return
    _atomic_write_json(BLOCK_ALERT_STATE_PATH, new_state)


def _cap_sellable(plan, tk, desired_qty, positions, book_tag):
    """Trần Σ SELL mỗi mã trong CẢ plan KHÔNG được vượt `sellable` (tradeQuantity broker — phần
    ĐÃ SETTLE T+2, khớp được NGAY phiên tới) — lệnh ở book KHÁC trong CÙNG plan (vd PARKMERGE-SELL
    của L1/L2) cũng chiếm phần sellable của mã này. Trả `(qty_thực_dùng, cảnh_báo_hoặc_None)`;
    `qty_thực_dùng` có thể 0 (hết chỗ, KHÔNG chèn gì). Thiếu field `sellable` (nguồn selfcheck cũ
    không khai) ⇒ fail-open — không chặn khi KHÔNG CÓ bằng chứng (§29), chỉ cảnh báo khi dữ liệu
    THẬT cho thấy vượt trần."""
    sellable = positions.get(tk, {}).get("sellable")
    if sellable is None:
        return desired_qty, None
    already = sum(int(o.get("qty") or 0) for o in plan.get("orders", [])
                  if o.get("ticker") == tk and o.get("side") == "sell")
    remaining = sellable - already
    if desired_qty <= remaining:
        return desired_qty, None
    used = max(remaining, 0)
    warn = (f"{tk} book={book_tag}: Σ SELL kế hoạch ({already + desired_qty}cp) > sellable "
            f"{sellable}cp (tradeQuantity broker, gồm cả lệnh book khác trong plan) — cap còn "
            f"{used}cp, phần vượt KHÔNG khớp hết được phiên tới")
    return used, warn


def _inject_sell(plan, positions, tk, qty, ref_price, book, play_type, note, order_id_suffix,
                 injected, capped_notes, detail):
    """Chèn 1 lệnh SELL auto-exit vào `plan`, có ÁP TRẦN Σsell cross-book (`_cap_sellable`). Trả
    True nếu có chèn (kể cả bị cap xuống còn >0), False nếu bị cap về 0 — KHÔNG chèn gì, nhưng
    `capped_notes` vẫn ghi lại để hiện ra cho người (§29, không lặng lẽ bỏ qua)."""
    used_qty, warn = _cap_sellable(plan, tk, qty, positions, book)
    if warn:
        capped_notes.append({"ticker": tk, "book": book, "desired_qty": qty,
                             "capped_qty": used_qty, "reason": warn})
        print(f"  [CAP] {warn}")
    if used_qty <= 0:
        print(f"  [CAP] {tk} book={book}: hết chỗ sellable — KHÔNG chèn lệnh")
        return False
    full_note = note if used_qty == qty else f"{note} — [CAP sellable {qty}→{used_qty}cp]"
    plan["orders"].append(_make_order(f"SELL-{tk}-AUTOEXIT-{order_id_suffix}", tk, used_qty,
                                      ref_price, book, play_type, full_note))
    injected.append((tk, book, detail))
    print(f"  [inject] SELL {tk} qty={used_qty} book={book} ({full_note})")
    return True


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
    # `approved_by_user` là bí danh tương đương `approved_by` trong TOÀN bộ pipeline duyệt
    # plan hiện có (trading_bot/plan.py:264-265, preflight_check.sh, merge_park_orders.py,
    # close_plan_approval_questions.py, ops_health_check.sh) — 8/9 lần duyệt tháng 09 đi qua
    # sửa JSON tay nên ra field này thay vì `approved_by`. Đọc raw JSON (không qua load_plan())
    # nên phải tự chuẩn hoá ở đây, không được chỉ nhìn `approved_by` (quant-skeptic 2026-09-30).
    approved = plan.get("approved_by") or plan.get("approved_by_user")
    if approved:
        print(f"[auto-exit] {account}: plan ĐÃ DUYỆT (approved={approved!r}) "
              f"— REFUSE, không mutate plan đã ký.")
        return 1
    plan.setdefault("orders", [])

    positions = broker_positions_with_cost(account_no, signal_date) or {}
    now_iso = dt.datetime.now(_ICT_TZ).isoformat(timespec="seconds")
    injected = []
    blocked_notes = []   # [{'ticker','book','reason'}] — mọi exit bị bỏ/cắt phải hiện ra (§29)
    capped_notes = []    # [{'ticker','book','desired_qty','capped_qty','reason'}]
    skipped_existing = []  # [(ticker, book)] — đã có sell sẵn trong plan, không phải "không có candidate"

    def _add_blocked(tk, book, reason):
        # Dedup CHỈ khi (ticker,book,reason) giống hệt — mã BAL lệch reconcile có thể bị guard
        # qty-mismatch bắt ĐỘC LẬP ở CẢ đường T+45 lẫn đường stop-loss (cùng `bal_lots`), ra 2
        # reason KHÁC chữ (một có hậu tố " (stop-loss)") — đây là 2 PHÁT HIỆN ĐỘC LẬP đáng giữ
        # cả hai (người duyệt cần biết CẢ 2 đường cùng chặn), không phải 1 sự kiện ghi trùng.
        # Chỉ chặn trùng lặp THẬT (cùng câu chữ — vd gọi lại `_add_blocked` 2 lần cho cùng 1 lý
        # do, ca lag_blocked/bal_blocked nếu book_lot_snapshot() trả về mã trùng).
        if {"ticker": tk, "book": book, "reason": reason} in blocked_notes:
            return
        blocked_notes.append({"ticker": tk, "book": book, "reason": reason})

    # ---- LAG: T+25 cố định (pt_v23_audit_2014.py:2060,2062) ----
    # `book_lot_snapshot` (bootstrap ngày 0 + FIFO replay, park_holdings.py) thay cho
    # `lag_entry_dates` (chỉ quét journal — BỎ SÓT mọi lô mua TRƯỚC khi journal có cột `book`,
    # 2026-08-04, và KHÔNG tách được mã nằm lẫn nhiều book như VPB). `ok=False` ⇒ park_holdings()
    # lỗi KẾT CẤU (không phải 1 mã cụ thể) ⇒ fail-safe CẢ book (mirror compute_park_trim.py Cổng
    # 0). `ok=True` nhưng từng mã nằm trong `blocked` (unverified/reconcile lệch riêng mã đó) chỉ
    # chặn MÃ ĐÓ — các mã khác trong cùng book vẫn xét bình thường (arch-review vòng 2, §29: fail-
    # safe ở MỨC TỪNG MÃ, không phải cả book).
    lag_lots, lag_ok, lag_reason, lag_blocked = book_lot_snapshot(account, "LAG", asof=signal_date)
    if not lag_ok:
        print(f"  [FAILSAFE] LAG {account}: sổ lô KHÔNG dựng được ({lag_reason}) — "
              f"KHÔNG chèn lệnh LAG lượt này")
        _add_blocked(None, "LAG", f"sổ lô book LAG không dựng được (lỗi kết cấu): {lag_reason}")
    for tk, reason in lag_blocked.items():
        _add_blocked(tk, "LAG", reason)
    lag_candidates, lag_qty_blocked = (_lag_bal_candidates(
        dt.date.fromisoformat(signal_date), positions, "LAG", lag_lots, rules.lag_should_exit)
        if lag_ok else ([], []))
    for b in lag_qty_blocked:
        _add_blocked(b["ticker"], "LAG", b["reason"])
    for tk, qty, ref_price, sessions in lag_candidates:
        existing = _already_has_sell(plan, tk, "LAG")
        if existing:
            print(f"  [skip] {tk}: đã có sell LAG trong plan (id={existing})")
            skipped_existing.append((tk, "LAG"))
            continue
        note = (f"AUTO-EXIT LAG: giữ {sessions} phiên ≥ mốc cố định {rules.LAG_EXIT_SESSIONS} "
                f"(pt_v23_audit_2014.py:2060) — đề xuất thoát toàn bộ")
        _inject_sell(plan, positions, tk, qty, ref_price, "LAG", "LAG_AUTO_EXIT", note,
                     "LAG", injected, capped_notes, sessions)

    # ---- BAL: T+45 cố định (pt_v23_audit_2014.py:2008) ----
    bal_lots, bal_ok, bal_reason, bal_blocked = book_lot_snapshot(account, "BAL", asof=signal_date)
    if not bal_ok:
        print(f"  [FAILSAFE] BAL {account}: sổ lô KHÔNG dựng được ({bal_reason}) — "
              f"KHÔNG chèn lệnh BAL/stop-loss lượt này")
        _add_blocked(None, "BAL", f"sổ lô book BAL không dựng được (lỗi kết cấu): {bal_reason}")
    for tk, reason in bal_blocked.items():
        _add_blocked(tk, "BAL", reason)
    bal_candidates, bal_qty_blocked = (_lag_bal_candidates(
        dt.date.fromisoformat(signal_date), positions, "BAL", bal_lots, rules.bal_should_exit)
        if bal_ok else ([], []))
    for b in bal_qty_blocked:
        _add_blocked(b["ticker"], "BAL", b["reason"])
    for tk, qty, ref_price, sessions in bal_candidates:
        existing = _already_has_sell(plan, tk, "BAL")
        if existing:
            print(f"  [skip] {tk}: đã có sell BAL trong plan (id={existing})")
            skipped_existing.append((tk, "BAL"))
            continue
        note = (f"AUTO-EXIT BAL: giữ {sessions} phiên ≥ mốc cố định {rules.BAL_EXIT_SESSIONS} "
                f"(pt_v23_audit_2014.py:2008) — đề xuất thoát toàn bộ")
        _inject_sell(plan, positions, tk, qty, ref_price, "BAL", "BAL_AUTO_EXIT", note,
                     "BAL", injected, capped_notes, sessions)

    # ---- BAL: stop-loss -20% trên giá vốn (pt_v23_audit_2014.py:2008), ĐỘC LẬP mốc phiên ----
    stoploss_candidates, stoploss_qty_blocked = (_bal_stop_loss_candidates(
        dt.date.fromisoformat(signal_date), positions, bal_lots) if bal_ok else ([], []))
    for b in stoploss_qty_blocked:
        _add_blocked(b["ticker"], "BAL", b["reason"] + " (stop-loss)")
    for tk, qty, ref_price, pnl_pct in stoploss_candidates:
        existing = _already_has_sell(plan, tk, "BAL")
        if existing:
            print(f"  [skip] {tk}: đã có sell BAL trong plan (id={existing})")
            skipped_existing.append((tk, "BAL"))
            continue
        note = (f"AUTO-EXIT BAL STOP-LOSS: lỗ {pnl_pct:.1%} ≤ mốc {rules.BAL_STOP_LOSS_PCT:.0%} "
                f"trên giá vốn (pt_v23_audit_2014.py:2008) — đề xuất thoát toàn bộ")
        _inject_sell(plan, positions, tk, qty, ref_price, "BAL", "BAL_AUTO_EXIT", note,
                     "BAL-STOPLOSS", injected, capped_notes, f"stoploss={pnl_pct:.1%}")

    # ---- CAPIT: T+60 cố định (CAPIT_HOLD, pt_v22_dt5g.py:123) + nhắc T+55 ----
    ledger = capit_episode._load(capit_episode.LEDGER_PATH)
    ep = capit_episode._open_episode(ledger)
    if ep is not None:
        sessions_held = ep.get("sessions_held")
        if rules.capit_should_exit(sessions_held):
            qty_map = (ep.get("qty_per_account") or {}).get(account, {})
            for tk, planned_qty in qty_map.items():
                pos = positions.get(tk)
                if not pos or pos.get("qty", 0) <= 0:
                    # Không còn nắm giữ — đã thoát bằng đường khác (bán tay/stop-out/corp
                    # action). KHÔNG fallback về planned_qty: đó là số KẾ HOẠCH cũ, bán theo
                    # nó sẽ tạo lệnh SELL khống cho cổ phiếu không còn có (quant-skeptic
                    # 2026-09-30, bug phantom-sell — mirror guard của _lag_bal_candidates).
                    continue
                qty = int(pos["qty"])
                existing = _already_has_sell(plan, tk, "CAPIT")
                if existing:
                    print(f"  [skip] {tk}: đã có sell CAPIT trong plan (id={existing})")
                    skipped_existing.append((tk, "CAPIT"))
                    continue
                ref_price = (pos or {}).get("marketPrice") or (pos or {}).get("avg_cost")
                if not ref_price or ref_price <= 0:
                    print(f"  [FAILSAFE] CAPIT {tk}: thiếu ref_price — KHÔNG chèn")
                    continue
                note = (f"AUTO-EXIT CAPIT: episode {ep['episode_id']} giữ {sessions_held} phiên "
                        f"≥ mốc cố định {rules.CAPIT_EXIT_SESSIONS} (CAPIT_HOLD, "
                        f"pt_v22_dt5g.py:123) — đề xuất thoát TOÀN BỘ rổ")
                _inject_sell(plan, positions, tk, qty, ref_price, "CAPIT", "CAPIT_AUTO_EXIT",
                            note, "CAPIT", injected, capped_notes, sessions_held)
        elif rules.capit_should_remind(sessions_held) and not ep.get("reminder_55_sent_at"):
            print(f"  [reminder] episode {ep['episode_id']}: {sessions_held} phiên ≥ "
                  f"{rules.CAPIT_REMINDER_SESSIONS} — gửi nhắc trước lên bus")
            if not dry_run:
                _send_capit_reminder(ep, sessions_held)
                ep["reminder_55_sent_at"] = now_iso
                capit_episode._save(capit_episode.LEDGER_PATH, ledger)

    # §29: mọi exit bị CHẶN hoặc CẮT phải hiện ra cho người, không chỉ nằm trong log stdout —
    # KHÔNG ĐƯỢC in "không có candidate" khi thực ra có candidate bị chặn/cắt (arch-review vòng 2
    # mô phỏng đúng ca này: book ok=True + mọi mã unverified ⇒ lots rỗng ⇒ bản cũ im lặng).
    if injected or blocked_notes or capped_notes:
        notes = plan.setdefault("auto_exit_inject_notes", [])
        entry = {"at": now_iso, "source": "auto_exit_inject"}
        if injected:
            entry["injected"] = [{"ticker": t, "book": b, "sessions_held": s}
                                 for t, b, s in injected]
        if blocked_notes:
            entry["blocked"] = blocked_notes
        if capped_notes:
            entry["capped"] = capped_notes
        notes.append(entry)
        if not dry_run:
            _atomic_write_json(plan_path, plan)
            print(f"[auto-exit] {account}: đã ghi {len(injected)} lệnh SELL, "
                  f"{len(blocked_notes)} mã bị chặn, {len(capped_notes)} mã bị cắt vào {plan_path}")
            if blocked_notes or capped_notes:
                _send_block_alert(account, blocked_notes, capped_notes)
        else:
            print(f"[auto-exit] {account}: DRY-RUN — {len(injected)} lệnh SELL sẽ chèn, "
                  f"{len(blocked_notes)} mã bị chặn, {len(capped_notes)} mã bị cắt, KHÔNG ghi.")
    elif skipped_existing:
        print(f"[auto-exit] {account} {plan_date}: {len(skipped_existing)} mã đã có sẵn lệnh "
              f"sell trong plan (không chèn lại) — {skipped_existing}")
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
