#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tự động xác nhận sự kiện doanh nghiệp (BONUS_ISSUE / SPLIT) khi DNSE credit cổ phiếu.

VÒNG LẶP 5 LẦN (VHM, MBB, BID, VIX, MSB) đều cùng mẫu:
  corp_action_daily biết sự kiện từ sáng (07:30) qua upcoming_events_held (days_ahead=1),
  nhưng DNSE credit trước ex_date 1 phiên (~18:30–19:00 ICT), trong khi DollarBill xây plan
  tại 19:00–19:10. Kết quả: sổ lô ≠ broker → BLOCKED_RECONCILE cho mã đó.

Script này chạy lúc 19:30 ICT (sau khi DNSE credit, trước DollarBill) và tự CONFIRMED khi
đủ bằng chứng 2 nguồn ĐỘC LẬP:
  (1) upcoming_events_held có event trong cửa sổ days_ahead ≤ 1
  (2) Broker: openQuantity và costPrice đổi đúng hệ số trong ngày

⚠️ CHỈ xác nhận sự kiện LÀM TĂNG số lượng (BONUS_ISSUE / SPLIT). Cổ tức tiền mặt không đi qua
đây. Gộp cổ phiếu (reverse split) chưa thiết kế (qty_multiplier > 1 là điều kiện cứng trong corp_actions.py).

Chạy: python3 mike/bin/corp_action_auto_confirm.py [--dry-run] [--date YYYY-MM-DD]
"""
import argparse
import datetime as dt
import json
import os
import sys

# ── Paths ──────────────────────────────────────────────────────────────────
MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
MIKE_ROOT = os.path.dirname(MIKE_BIN)
WC_ROOT = os.path.dirname(MIKE_ROOT)

CORP_ACTIONS_FILE  = os.path.join(WC_ROOT, "data", "corp_actions.json")
CA_DAILY_DIR       = os.path.join(WC_ROOT, "data", "corp_action_daily")
EXEC_DIR           = os.path.join(WC_ROOT, "data", "execution_logs")

sys.path.insert(0, MIKE_BIN)
sys.path.insert(0, MIKE_ROOT)

# ── Constants ──────────────────────────────────────────────────────────────
RATIO_TOL       = 0.02   # ±2% chấp nhận giữa hệ số khai báo và hệ số suy từ broker
DAYS_AHEAD_MAX  = 1      # chỉ xét sự kiện broker có thể credit trong hôm nay
CONFIRMED_CODES = {"ISS", "SPLIT"}

APPEND_EVENT = os.path.join(MIKE_BIN, "append_event.sh")
NOTIFY_SH    = os.path.join(MIKE_BIN, "notify_thread.sh")


# ── Helpers ────────────────────────────────────────────────────────────────

def today_ict():
    from zoneinfo import ZoneInfo
    return dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()


def load_corp_actions_raw():
    """Đọc toàn bộ corp_actions.json, trả list thô. [] nếu file không tồn tại."""
    if not os.path.exists(CORP_ACTIONS_FILE):
        return []
    with open(CORP_ACTIONS_FILE, encoding="utf-8") as f:
        return json.load(f).get("actions") or []


def already_confirmed_set():
    """Tập (ticker.upper(), ex_date) đã có _status bắt đầu CONFIRMED."""
    out = set()
    for r in load_corp_actions_raw():
        if str(r.get("_status", "")).upper().startswith("CONFIRMED"):
            out.add((str(r.get("ticker", "")).upper(), str(r.get("ex_date", ""))[:10]))
    return out


def get_candidate_events(date_str):
    """Từ corp_action_daily_{date}.json → upcoming_events_held khớp điều kiện."""
    path = os.path.join(CA_DAILY_DIR, f"corp_action_daily_{date_str}.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    held = d.get("upcoming_events_held") or []
    out = []
    for ev in held:
        if (ev.get("price_adjusting") and
                ev.get("event_code") in CONFIRMED_CODES and
                int(ev.get("days_ahead") or 999) <= DAYS_AHEAD_MAX):
            out.append(ev)
    return out


def _get_ticker_snapshots(account_no, ticker, date_str):
    """Đọc tất cả bản ghi positions cho (account_no, ticker) từ dnse_raw_{date}.jsonl.

    Trả (first_rec, last_rec) — rec là dict position của DNSE, có openQuantity / costPrice.
    Trả (None, None) nếu không có bản ghi nào.
    """
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date_str}.jsonl")
    if not os.path.exists(path):
        return None, None

    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(d.get("account_no")) != str(account_no):  # §12
                continue
            if d.get("kind") != "positions":
                continue
            ts = d.get("ts") or ""
            positions = d.get("payload", {}).get("positions") or []
            for p in positions:
                if p.get("symbol") == ticker and str(p.get("accountNo")) == str(account_no):
                    records.append((ts, p))
                    break  # chỉ 1 bản ghi / snapshot / ticker

    if not records:
        return None, None
    records.sort(key=lambda x: x[0])
    return records[0][1], records[-1][1]


def _get_account_nos(date_str):
    """Đọc danh sách account_no từ dnse_raw_{date}.jsonl."""
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date_str}.jsonl")
    if not os.path.exists(path):
        return []
    seen = {}  # account_no → account_label
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ano = d.get("account_no")
            lbl = d.get("account_label") or ano
            if ano and ano not in seen:
                seen[ano] = lbl
    return list(seen.items())  # [(account_no, label), ...]


def check_ratio(first_rec, last_rec, expected_mult, tol=RATIO_TOL):
    """So hệ số thực tế với hệ số khai báo. Trả (ok, actual_qty_ratio, actual_cost_ratio).

    expected_mult = 1.2 với tỉ lệ thưởng 20%.
    """
    qty_before = int(first_rec.get("openQuantity") or 0)
    qty_after  = int(last_rec.get("openQuantity") or 0)
    cost_before = float(first_rec.get("costPrice") or 0)
    cost_after  = float(last_rec.get("costPrice") or 0)

    if qty_before <= 0 or qty_after <= qty_before or cost_after <= 0:
        return False, None, None

    actual_qty  = qty_after / qty_before
    actual_cost = cost_before / cost_after if cost_after > 0 else 0

    qty_ok  = abs(actual_qty  - expected_mult) <= tol * expected_mult
    cost_ok = abs(actual_cost - expected_mult) <= tol * expected_mult
    return (qty_ok and cost_ok), round(actual_qty, 4), round(actual_cost, 4)


def broker_modified_today(last_rec, today_str):
    """True nếu modifiedDate của record là hôm nay ICT (broker credit hôm nay)."""
    md = str(last_rec.get("modifiedDate") or "")
    # modifiedDate là UTC (Z suffix), quy về ICT (+7)
    if not md:
        return False
    try:
        from zoneinfo import ZoneInfo
        ts_utc = dt.datetime.fromisoformat(md.replace("Z", "+00:00"))
        ts_ict = ts_utc.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
        return ts_ict.date().isoformat() == today_str
    except Exception:
        # fallback: so chuỗi thô (UTC date)
        return md[:10] == today_str


def write_corp_actions(actions_list, dry_run=False):
    """Ghi lại corp_actions.json với list actions mới. Atomic tmp+rename."""
    data = {"actions": actions_list}
    if dry_run:
        print(f"[DRY-RUN] would write {len(actions_list)} records to {CORP_ACTIONS_FILE}")
        return
    tmp = CORP_ACTIONS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, CORP_ACTIONS_FILE)


def post_bus(ticker, event_id, ex_date, multiplier, acct_evidence, dry_run=False):
    """Ghi bus finding và notify Discord."""
    import subprocess
    summary = (f"AUTO-CONFIRMED {ticker} {event_id}: ×{multiplier} (ex {ex_date}), "
               f"broker evidence: {acct_evidence}")
    payload = json.dumps({
        "status": "AUTO_CONFIRMED",
        "event_id": event_id,
        "ticker": ticker,
        "qty_multiplier": multiplier,
        "ex_date": ex_date,
        "broker_evidence": acct_evidence,
        "decided_by": "agent",
        "note": "auto-confirmed by corp_action_auto_confirm.py (2-source rule)"
    }, ensure_ascii=False)
    if dry_run:
        print(f"[DRY-RUN] bus finding: {summary}")
        return

    # Append bus event
    subprocess.run(
        [APPEND_EVENT, "Mike", "finding", f"corp-action-auto-confirm-{ticker}", payload],
        check=False
    )

    # Discord notify
    thread_id = os.environ.get("DISCORD_THREAD_ID", "")
    if thread_id and os.path.exists(NOTIFY_SH):
        msg = (f"✅ **Corp Action AUTO-CONFIRMED** — **{ticker}** ×{multiplier} "
               f"(ex {ex_date}): broker credit xác nhận, sổ lô tự đồng bộ, "
               f"DollarBill sẽ build plan sạch.")
        subprocess.run([NOTIFY_SH, msg, thread_id], check=False)


# ── Main ───────────────────────────────────────────────────────────────────

def run(date_str, dry_run=False):
    print(f"[corp_action_auto_confirm] date={date_str} dry_run={dry_run}")

    candidates = get_candidate_events(date_str)
    if not candidates:
        print("  → không có sự kiện nào trong upcoming_events_held cần kiểm.")
        return 0

    confirmed_set = already_confirmed_set()
    accounts = _get_account_nos(date_str)
    if not accounts:
        print(f"  → không đọc được account_no từ dnse_raw_{date_str}.jsonl.")
        return 1

    print(f"  {len(candidates)} candidate event(s), {len(accounts)} account(s): "
          f"{[a for _, a in accounts]}")

    new_confirms = []
    actions_raw = load_corp_actions_raw()

    for ev in candidates:
        ticker   = ev.get("ticker", "").upper()
        ex_date  = str(ev.get("date") or "")[:10]
        ratio    = float(ev.get("exercise_ratio") or 0)
        if ratio <= 0:
            print(f"  [{ticker}] skip: exercise_ratio={ratio} không hợp lệ")
            continue
        mult = 1.0 + ratio

        if (ticker, ex_date) in confirmed_set:
            print(f"  [{ticker}] đã CONFIRMED rồi — bỏ qua.")
            continue

        print(f"  [{ticker}] ex_date={ex_date}, ratio={ratio} (×{mult}) — kiểm broker ...")

        acct_results = {}
        for acct_no, acct_lbl in accounts:
            first, last = _get_ticker_snapshots(acct_no, ticker, date_str)
            if first is None:
                # account không giữ ticker này
                continue
            if not broker_modified_today(last, date_str):
                # broker chưa credit hôm nay cho ticker này
                acct_results[acct_lbl] = {
                    "verdict": "NOT_MODIFIED_TODAY",
                    "qty_before": first.get("openQuantity"),
                    "qty_after": last.get("openQuantity"),
                }
                continue
            ok, qty_r, cost_r = check_ratio(first, last, mult)
            acct_results[acct_lbl] = {
                "verdict": "MATCH" if ok else "MISMATCH",
                "qty_before": int(first.get("openQuantity") or 0),
                "qty_after":  int(last.get("openQuantity") or 0),
                "qty_ratio":  qty_r,
                "cost_ratio": cost_r,
                "modified_today": True,
            }

        print(f"  [{ticker}] broker results: {acct_results}")

        if not acct_results:
            print(f"  [{ticker}] không account nào giữ mã này → CANNOT_VERIFY, bỏ qua.")
            continue

        any_mismatch = any(v["verdict"] == "MISMATCH" for v in acct_results.values())
        has_match    = any(v["verdict"] == "MATCH"    for v in acct_results.values())

        if any_mismatch:
            print(f"  [{ticker}] ❌ MISMATCH — không tự xác nhận, cần người kiểm.")
            continue
        if not has_match:
            print(f"  [{ticker}] broker chưa credit hôm nay → bỏ qua.")
            continue

        # ── ĐỦ ĐIỀU KIỆN: tự CONFIRMED ─────────────────────────────────
        event_id = f"{ticker}-{ex_date}-BONUS-ISSUE"
        from zoneinfo import ZoneInfo
        now_ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%dT%H:%M:%S+07:00")

        ev_code = ev.get("event_code", "ISS")
        ev_type = "BONUS_ISSUE" if ev_code == "ISS" else "SPLIT"

        new_rec = {
            "id": event_id,
            "ticker": ticker,
            "event_type": ev_type,
            "ratio_text": ev.get("title", f"tỉ lệ {ratio*100:.0f}%"),
            "qty_multiplier": mult,
            "ex_date": ex_date,
            "record_date": ev.get("record_date"),
            "broker_effective_ts": f"{date_str}T00:00:00",  # placeholder; refined below
            "_status": (f"CONFIRMED — corp_action_auto_confirm.py {now_ict} "
                        f"(2-source: upcoming_events_held + broker qty/cost ratio match). "
                        f"Thu hồi: đổi _status thành 'REVOKED ...'"),
            "confirmed_by": "corp_action_auto_confirm.py (agent)",
            "decided_by": "agent",
            "confirmed_at": now_ict,
            "evidence": [
                (f"NGUỒN 1 — corp_action_daily {date_str} upcoming_events_held: "
                 f"ticker={ticker}, event_code={ev_code}, date={ex_date}, "
                 f"exercise_ratio={ratio}, price_adjusting=True, days_ahead={ev.get('days_ahead')}"),
            ] + [
                (f"NGUỒN 2 — broker {lbl}: qty {r['qty_before']}→{r['qty_after']} "
                 f"(×{r.get('qty_ratio')}), costPrice ratio ×{r.get('cost_ratio')}, "
                 f"modified_today=True")
                for lbl, r in acct_results.items() if r["verdict"] == "MATCH"
            ],
            "verify_against_bq": f"PENDING — chạy sau {ex_date}: "
                                  f"python3 mike/bin/corp_actions.py --verify {event_id}",
            "note": "Cùng mẫu broker credit 1 phiên trước ex_date như VHM/MBB/BID/VIX/MSB.",
        }

        # Refine broker_effective_ts từ modifiedDate account khớp đầu tiên
        for lbl, r in acct_results.items():
            if r["verdict"] == "MATCH":
                for acct_no, albl in accounts:
                    if albl == lbl:
                        _, last = _get_ticker_snapshots(acct_no, ticker, date_str)
                        if last and last.get("modifiedDate"):
                            # modifiedDate là UTC → bỏ .Z suffix
                            new_rec["broker_effective_ts"] = last["modifiedDate"].replace("Z", "")
                        break
                break

        print(f"  [{ticker}] ✅ AUTO-CONFIRMED ×{mult} (ex {ex_date})")
        if dry_run:
            print(f"  [DRY-RUN] new record: {json.dumps(new_rec, ensure_ascii=False)[:300]}")

        actions_raw.append(new_rec)
        new_confirms.append((ticker, event_id))
        post_bus(ticker, event_id, ex_date, mult, acct_results, dry_run=dry_run)

    if new_confirms:
        write_corp_actions(actions_raw, dry_run=dry_run)
        print(f"\nXong: {len(new_confirms)} event(s) AUTO-CONFIRMED: "
              f"{[t for t, _ in new_confirms]}")
    else:
        print("Xong: không có event mới nào đủ điều kiện tự xác nhận.")

    return 0


def main():
    ap = argparse.ArgumentParser(description="Tự động xác nhận corp action khi broker credit")
    ap.add_argument("--dry-run", action="store_true",
                    help="In kết quả nhưng KHÔNG ghi file / gửi bus")
    ap.add_argument("--date", default=None,
                    help="Ngày cần kiểm (mặc định: hôm nay ICT)")
    a = ap.parse_args()
    date_str = a.date or today_ict()
    sys.exit(run(date_str, dry_run=a.dry_run))


if __name__ == "__main__":
    main()
