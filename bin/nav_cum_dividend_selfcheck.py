#!/usr/bin/env python3
"""nav_cum_dividend_selfcheck.py — kiểm `daily_nav_snapshot.cum_dividend_double_count`
trên DỮ LIỆU VẬN HÀNH THẬT (dnse_raw + BigQuery), không phải fixture tự bịa.

VÌ SAO: bug đếm-2-lần cổ tức (coding_guidelines §21, báo cáo tuần 27–31/07/2026 Mục 11.5)
sống sót được vì MỌI phép đối soát NAV đều PASS — NAV tổng vẫn đúng, chỉ lệch thời điểm ghi
nhận đúng 1 phiên. Nên bài kiểm phải nhắm thẳng vào con số "cổ tức phải thu chưa qua ex-date",
với CẢ ca dương (phải trừ) LẪN ca âm (đã qua ex-date, KHÔNG được trừ).

Ca âm quan trọng nhất: SpaceX 09/07/2026 — `cashDividendReceiving` tăng 2.400.000đ (MBB) đúng
trong ngày, nhưng 09/07 CHÍNH LÀ ex-date (giá đã rơi) ⇒ trừ là SAI. Một bản cài đặt ngây thơ
kiểu "hễ tăng thì trừ" sẽ FAIL đúng ca này.

HAI CHẾ ĐỘ, chạy cùng bộ ca:
  A. "rerun"  — có BQ đầy đủ (tra lại quá khứ): ex-date do tỉ số Close/Price quyết định.
  B. "live"   — mô phỏng lúc 19:10 ngày T, BQ chưa có phiên T ⇒ chỉ còn quy tắc thời điểm
                (bản ghi balance phiên trước có phải bản cuối ngày không).
Hai chế độ PHẢI ra cùng kết quả — nếu lệch, một trong hai đường suy luận sai.

Phụ: kiểm bất biến nav == mtm_stock + cash − margin_debt + offbook_assets + egg_assets trên TOÀN BỘ
nav_history_{account}.csv.

    python3 mike/bin/nav_cum_dividend_selfcheck.py
    env -u TZ python3 mike/bin/nav_cum_dividend_selfcheck.py    # §16: không tin TZ của host
"""
import csv
import glob
import json
import os
import sys

MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MIKE_BIN)
WC_ROOT = os.path.dirname(os.path.dirname(MIKE_BIN))
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")

from daily_nav_snapshot import (  # noqa: E402
    cum_dividend_double_count, latest_balance, previous_balance,
)

ACCOUNT_NO = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}

# (account, date, kỳ vọng số tiền phải LOẠI khỏi tiền mặt, ghi chú)
CASES = [
    ("SpaceX", "2026-07-08", 0, "trước khi cổ tức MBB được ghi nhận — không có gì để trừ"),
    ("SpaceX", "2026-07-09", 0, "CA ÂM: cashDivRecv +2.400.000 (MBB) nhưng 09/07 CHÍNH LÀ ex-date"),
    ("SpaceX", "2026-07-16", 855_000, "BID 1.900cp × 450 — ex-date 17/07"),
    ("SpaceX", "2026-07-23", 0, "CA ÂM: 23/07 là ex-date CTG+VCB, khoản đã ghi từ 22/07"),
    ("SpaceX", "2026-07-24", 4_000_000, "NCT 500cp × 8.000 — ex-date 27/07 (thứ Hai)"),
    ("SpaceX", "2026-07-27", 3_300_000, "SAB 1.100cp × 3.000 — ex-date 28/07"),
    ("SpaceX", "2026-07-28", 0, "CA ÂM: 28/07 là ex-date SAB"),
    ("SpaceX", "2026-07-31", 0, "CA ÂM: không có sự kiện quyền nào"),
    ("ZaloPay", "2026-07-16", 405_000, "BID 900cp × 450 — ex-date 17/07"),
    ("ZaloPay", "2026-07-22", 832_500, "CTG 1.050 + VCB 800, × 450 — ex-date 23/07"),
    ("ZaloPay", "2026-07-24", 2_984_000, "NCT 373cp × 8.000 — ex-date 27/07"),
    ("ZaloPay", "2026-07-31", 0, "CA ÂM: không có sự kiện quyền nào"),
    # ZaloPay 27/07 CỐ Ý không có trong danh sách: bản ghi balances hôm đó TOÀN SỐ 0 (lỗi API
    # DNSE) nên daily_nav_snapshot.py từ chối tính; dòng NAV 27/07 đã được sửa tay bằng bản đọc
    # 28/07 09:15 và ĐÃ trừ đúng 2.232.000đ cổ tức SAB (fix_nav_zalopay_20260727.py).
]


def positions_on(account_no, date):
    """Vị thế ĐÚNG THỜI ĐIỂM ngày `date` (point-in-time) từ dnse_raw — KHÔNG hỏi broker.

    daily_nav_snapshot.py chạy live lấy vị thế hiện tại từ API; tra lại quá khứ mà dùng vị thế
    hôm nay là sai point-in-time (giới hạn đã biết, xem nav_scripts_2account_selfcheck.py).
    """
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date}.jsonl")
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("kind") != "positions" or str(rec.get("account_no")) != str(account_no):
                continue
            for it in rec.get("payload", {}).get("positions", []):
                if str(it.get("accountNo")) != str(account_no):
                    continue
                if (it.get("openQuantity") or 0) > 0:
                    out[it["symbol"]] = it["openQuantity"]
    return out


def run_cases():
    passed = failed = 0
    for account, date, want, note in CASES:
        acc = ACCOUNT_NO[account]
        cur = latest_balance(os.path.join(EXEC_DIR, f"dnse_raw_{date}.jsonl"), account_no=acc)
        if cur is None:
            print(f"  [FAIL] {account} {date}: không có bản ghi balances để kiểm")
            failed += 1
            continue
        pos = positions_on(acc, date)
        prev = previous_balance(acc, date)
        got = {}
        # A. rerun: BQ đầy đủ (mặc định — hàm tự tra detect_adjustments_batch)
        got["rerun"] = cum_dividend_double_count(acc, date, pos, cur, prev)
        # B. live: mô phỏng BQ chưa có phiên nào sau `date` ⇒ không kết luận được từ giá
        got["live"] = cum_dividend_double_count(acc, date, pos, cur, prev,
                                                events={}, bq_max_date=date)
        for mode, res in got.items():
            ok = abs(res["amount"] - want) < 1
            print(f"  [{'PASS' if ok else 'FAIL'}] {account} {date} [{mode}]: "
                  f"loại {res['amount']:,.0f} (kỳ vọng {want:,.0f}) — {note}")
            if res["note"]:
                print(f"           ↳ {res['note']}")
            for w in res["warnings"]:
                print(f"           ⚠️ {w}")
            passed, failed = passed + ok, failed + (not ok)
        if abs(got["rerun"]["amount"] - got["live"]["amount"]) >= 1:
            print(f"  [FAIL] {account} {date}: hai chế độ rerun/live KHÔNG khớp nhau")
            failed += 1
        else:
            passed += 1
    return passed, failed


def run_invariant():
    """nav == mtm_stock + cash − margin_debt + offbook_assets + egg_assets trên TOÀN BỘ file lịch sử.

    `egg_assets` (Trứng vàng, field `egg.totalValue`) thêm vào CSV từ 2026-08-18/19 (§25
    coding_guidelines) — cột có thể RỖNG ở các dòng cũ hơn (chưa wire), `num()` coi rỗng = 0 nên
    không ảnh hưởng lịch sử trước đó.
    """
    passed = failed = 0
    for account in ACCOUNT_NO:
        path = os.path.join(EXEC_DIR, f"nav_history_{account}.csv")
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        bad = []
        for r in rows:
            def num(k):
                return float(r.get(k) or 0)
            lhs = num("nav")
            rhs = num("mtm_stock") + num("cash") - num("margin_debt") + num("offbook_assets") \
                + num("egg_assets")
            if abs(lhs - rhs) >= 1:
                bad.append((r["date"], lhs, rhs))
        ok = not bad
        print(f"  [{'PASS' if ok else 'FAIL'}] {account}: bất biến NAV trên {len(rows)} dòng")
        for d, lhs, rhs in bad:
            print(f"           ✗ {d}: nav={lhs:,.0f} nhưng mtm+cash−nợ+offbook+egg={rhs:,.0f}")
        passed, failed = passed + ok, failed + (not ok)
    return passed, failed


def main():
    print("=== 1) Cổ tức phải thu chưa qua ex-date (dữ liệu thật, 2 chế độ) ===")
    p1, f1 = run_cases()
    print("\n=== 2) Bất biến nav = mtm_stock + cash − margin_debt + offbook_assets + egg_assets ===")
    p2, f2 = run_invariant()
    print(f"\n=== SELFCHECK: {p1 + p2} PASS / {f1 + f2} FAIL ===")
    return 1 if (f1 + f2) else 0


if __name__ == "__main__":
    sys.exit(main())
