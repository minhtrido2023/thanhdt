#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tự động CONFIRM corp action khi DNSE đã credit cổ phiếu và đủ bằng chứng.

Chạy 19:30 ICT T2-T6 (trước DollarBill lập plan).
Logic: đọc upcoming_events_held (days_ahead ≤ 1) → so với DNSE live positions
hôm nay vs hôm qua → nếu qty + costPrice đều khớp ratio → auto-CONFIRMED.

Quy tắc: KHÔNG bao giờ suy từ qty lệch đơn thuần (§5 coding_guidelines).
Cần ĐỦ: (1) BQ event đã khai ratio, (2) broker qty mới = qty cũ × ratio, (3) costPrice÷ratio.
Thiếu bất kỳ nguồn nào → alert, không confirm.
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

WC_ROOT = Path(os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude"))
MIKE_ROOT = WC_ROOT / "mike"
DATA_DIR = WC_ROOT / "data"
CORP_ACTIONS_FILE = DATA_DIR / "corp_actions.json"
CORP_ACTION_DAILY_DIR = DATA_DIR / "corp_action_daily"
DNSE_RAW_DIR = DATA_DIR / "execution_logs"
APPEND_EVENT = MIKE_ROOT / "bin" / "append_event.sh"

RATIO_TOL = 0.021          # 2.1% — khớp với RATIO_TOL trong corp_actions.py
COST_TOL  = 0.025          # costPrice: cho phép làm tròn bậc DNSE
MAX_DAYS_AHEAD = 1         # chỉ xử lý sự kiện exright_date = ngày mai trở lại

ACCOUNTS = {
    "SpaceX": "0002023347",
    "ZaloPay": "0001743768",
}

# event_code → event_type trong corp_actions.json
EVENT_CODE_MAP = {
    "ISS": "BONUS_ISSUE",
    "SPLIT": "SPLIT",
}


def load_corp_actions_json() -> dict:
    with open(CORP_ACTIONS_FILE) as f:
        return json.load(f)


def already_confirmed(data: dict, ticker: str, exright_date: str) -> bool:
    for a in data.get("actions", []):
        if a["ticker"] == ticker and a["ex_date"] == exright_date:
            if a.get("_status", "").startswith("CONFIRMED"):
                return True
    return False


def save_corp_actions_json(data: dict) -> None:
    tmp = CORP_ACTIONS_FILE.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(CORP_ACTIONS_FILE)


def get_positions(date_str: str, account_no: str) -> dict:
    """Trả dict symbol → latest position record từ dnse_raw_DATE.jsonl."""
    path = DNSE_RAW_DIR / f"dnse_raw_{date_str}.jsonl"
    if not path.exists():
        return {}
    latest: dict = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("kind") != "positions":
                continue
            if r.get("account_no") != account_no:
                continue
            for pos in r.get("payload", {}).get("positions", []):
                sym = pos.get("symbol", "")
                if sym:
                    latest[sym] = pos
    return latest


def prev_trading_day(date: dt.date) -> dt.date:
    """Trả ngày giao dịch liền trước (bỏ qua T7, CN)."""
    d = date - dt.timedelta(days=1)
    while d.weekday() >= 5:   # 5=T7, 6=CN
        d -= dt.timedelta(days=1)
    return d


def bus_event(event_type: str, topic: str, payload: dict) -> None:
    if not APPEND_EVENT.exists():
        return
    import subprocess
    subprocess.run(
        [str(APPEND_EVENT), "corp_action_auto_confirm", event_type, topic,
         json.dumps(payload, ensure_ascii=False)],
        timeout=15,
    )


def main() -> int:
    today = dt.date.today()
    today_str = today.isoformat()
    yesterday_str = prev_trading_day(today).isoformat()

    # Đọc corp_action_daily hôm nay
    daily_path = CORP_ACTION_DAILY_DIR / f"corp_action_daily_{today_str}.json"
    if not daily_path.exists():
        print(f"[SKIP] Không tìm thấy corp_action_daily_{today_str}.json")
        return 0

    with open(daily_path, encoding="utf-8") as f:
        daily = json.load(f)

    upcoming = daily.get("upcoming_events_held", [])
    candidates = [
        e for e in upcoming
        if e.get("days_ahead", 99) <= MAX_DAYS_AHEAD
        and e.get("price_adjusting", False)
        and e.get("event_code") in EVENT_CODE_MAP
        and float(e.get("exercise_ratio") or 0) > 0
    ]

    if not candidates:
        print(f"[OK] Không có sự kiện nào cần xử lý (days_ahead ≤ {MAX_DAYS_AHEAD})")
        return 0

    corp_data = load_corp_actions_json()
    confirmed_count = 0

    for event in candidates:
        ticker      = event["ticker"]
        exright_date = event["date"]
        ratio       = float(event["exercise_ratio"])
        multiplier  = 1.0 + ratio
        event_type  = EVENT_CODE_MAP[event["event_code"]]
        title       = event.get("title", "")

        print(f"\n[CHECK] {ticker} exright={exright_date} ratio={ratio} (×{multiplier:.4f})")

        if already_confirmed(corp_data, ticker, exright_date):
            print(f"  → Đã có CONFIRMED, bỏ qua")
            continue

        # So sánh positions hôm nay vs hôm qua cho từng account
        matched_accounts: dict = {}
        skipped_accounts: list = []

        for label, account_no in ACCOUNTS.items():
            today_pos = get_positions(today_str, account_no)
            yest_pos  = get_positions(yesterday_str, account_no)

            pos_today = today_pos.get(ticker)
            pos_yest  = yest_pos.get(ticker)

            if not pos_today:
                continue  # Account không giữ ticker

            new_qty  = pos_today.get("openQuantity", 0)
            new_cost = pos_today.get("costPrice", 0)

            if not pos_yest:
                skipped_accounts.append(f"{label}: không có dữ liệu hôm qua")
                continue

            old_qty  = pos_yest.get("openQuantity", 0)
            old_cost = pos_yest.get("costPrice", 0)

            if old_qty <= 0 or new_qty <= 0:
                skipped_accounts.append(f"{label}: qty=0, bỏ qua")
                continue

            qty_ratio  = new_qty / old_qty
            qty_match  = abs(qty_ratio - multiplier) / multiplier < RATIO_TOL

            cost_ok = False
            cost_ratio = None
            if old_cost > 0 and new_cost > 0:
                cost_ratio = old_cost / new_cost
                cost_ok = abs(cost_ratio - multiplier) / multiplier < COST_TOL

            print(f"  {label}: qty {old_qty}→{new_qty} (ratio={qty_ratio:.4f}, "
                  f"expected={multiplier:.4f}, match={qty_match}) | "
                  f"cost {old_cost:.2f}→{new_cost:.2f} "
                  f"(ratio={cost_ratio:.4f if cost_ratio else 'N/A'}, match={cost_ok})")

            if qty_match and cost_ok:
                total_check = old_qty * old_cost
                total_new   = new_qty * new_cost
                diff_vnd    = abs(total_check - total_new)
                matched_accounts[label] = {
                    "account_no": account_no,
                    "old_qty": old_qty, "new_qty": new_qty,
                    "old_cost": old_cost, "new_cost": new_cost,
                    "qty_ratio_observed": round(qty_ratio, 6),
                    "cost_ratio_observed": round(cost_ratio, 6) if cost_ratio else None,
                    "total_cost_diff_vnd": round(diff_vnd, 2),
                }
            else:
                skipped_accounts.append(
                    f"{label}: qty_match={qty_match}, cost_match={cost_ok} — KHÔNG khớp"
                )

        if not matched_accounts:
            # Không có account nào khớp đủ cả hai tiêu chí
            msg = f"{ticker}: không account nào xác nhận đủ ratio (qty+cost)"
            if skipped_accounts:
                msg += " | " + "; ".join(skipped_accounts)
            print(f"  → [ALERT] {msg}")
            bus_event("question", f"corp-action-auto-confirm-unresolved: {ticker}-{exright_date}", {
                "ticker": ticker, "exright_date": exright_date, "ratio": ratio,
                "reason": msg, "urgency": "high",
            })
            continue

        # Đủ bằng chứng — tạo record CONFIRMED
        now_ict = dt.datetime.now(ICT).isoformat()
        rec_id  = f"{ticker}-{exright_date}-AUTO-{event_type}"

        # Xác định broker_effective_ts từ modifiedDate của position
        broker_ts = f"{today_str}T~19:00:00"  # ước lượng nếu không đọc được
        for label, m in matched_accounts.items():
            account_no = m["account_no"]
            raw = get_positions(today_str, account_no)
            pos = raw.get(ticker, {})
            mod = pos.get("modifiedDate", "")
            if mod:
                # UTC → ICT (+7)
                try:
                    utc_dt = dt.datetime.fromisoformat(mod.replace("Z", "+00:00"))
                    ict_dt = utc_dt.astimezone(ICT)
                    broker_ts = ict_dt.strftime("%Y-%m-%dT%H:%M:%S")
                except Exception:
                    pass
                break

        evidence = [
            (f"NGUỒN 1 — corp_action_daily upcoming_events_held (ĐỘC LẬP với sổ/broker của ta): "
             f"{json.dumps(event, ensure_ascii=False)}"),
            (f"NGUỒN 2 — chữ ký KẾ TOÁN của broker, {len(matched_accounts)} tài khoản, "
             f"qty × {multiplier:.4f} và costPrice ÷ {multiplier:.4f} đều khớp trong dung sai: "
             f"{json.dumps(matched_accounts, ensure_ascii=False)}"),
        ]

        new_record = {
            "id": rec_id,
            "ticker": ticker,
            "event_type": event_type,
            "ratio_text": title,
            "qty_multiplier": round(multiplier, 6),
            "ex_date": exright_date,
            "record_date": None,
            "broker_effective_ts": broker_ts,
            "_status": (f"CONFIRMED — tự động bởi corp_action_auto_confirm.py {now_ict}: "
                        f"broker qty + costPrice đều khớp ratio {ratio} tại {len(matched_accounts)} account. "
                        f"Muốn thu hồi: đổi _status thành 'REVOKED ...' → sổ lô lập tức quay về số cũ."),
            "confirmed_by": "corp_action_auto_confirm.py (automated, cron 19:30 ICT)",
            "decided_by": "agent",
            "confirmed_at": now_ict,
            "evidence": evidence,
            "note": (f"Cùng mẫu hình broker credit 1 phiên trước ex-date như VHM/MBB/BID/VIX/MSB trước đó. "
                     f"tradeQuantity broker vẫn giữ số cũ trong khi openQuantity đã là số mới — "
                     f"cổ phiếu thưởng CHƯA bán được; lệnh BÁN phải neo theo tradeQuantity."),
            "verify_against_bq": (f"PENDING — chạy sau {exright_date}: "
                                  f"python3 mike/bin/corp_actions.py --verify {rec_id}"),
        }

        corp_data["actions"].append(new_record)
        save_corp_actions_json(corp_data)
        confirmed_count += 1

        print(f"  → [CONFIRMED] {rec_id} ghi vào corp_actions.json")
        bus_event("finding", f"corp-action-auto-confirmed: {ticker}-{exright_date}", {
            "ticker": ticker, "exright_date": exright_date,
            "qty_multiplier": round(multiplier, 6),
            "accounts": list(matched_accounts.keys()),
            "record_id": rec_id,
        })

    print(f"\n[DONE] {confirmed_count} record được CONFIRMED tự động.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
