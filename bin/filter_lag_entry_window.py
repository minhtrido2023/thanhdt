#!/usr/bin/env python3
"""Lọc CỬA SỔ ENTRY của book LAG — quyết định CƠ HỌC, không còn để LLM tự nhớ luật.

⚠️ CHỈ ĐỌC. Không đặt lệnh, không ghi vào bất kỳ file plan nào, không gọi BQ, không gọi DNSE.
   Đầu vào duy nhất là CSV khuyến nghị mà engine đã sinh ra; đầu ra là 3 rổ đã phân loại.

VÌ SAO CÓ FILE NÀY (sự cố thật 2026-08-04): `golive_v23_recommendations_<signal>.csv` gắn sẵn
`status` đúng cho từng mã (`UPCOMING T+1 phiên tới` / `T+2` / `T+3` / `WINDOW_PASSED <ngày>`),
nhưng KHÔNG script nào biến nó thành danh sách ứng viên — mỗi phiên DollarBill tự đọc CSV và
tự lọc bằng tay. Cùng 1 CSV (signal 2026-08-03), plan SpaceX lọc ĐÚNG (chỉ T+1) còn plan
ZaloPay đưa nhầm DCM (T+2) + DRI/POW (T+3) vào `deferred_orders` của hôm nay ĐỒNG THỜI bỏ sót
APF/MAC/TV3 (đều T+1). 0 lệnh thật nên không mất tiền, nhưng đây là lỗi dữ liệu thuần cơ học:
không có phán đoán nào ở đây cả, chỉ là đọc 1 cột chuỗi. Cùng khuôn với `park_holdings.py`
(book_note) — chuyển việc "LLM phải nhớ luật" thành "script trả lời sẵn".

QUY TẮC (nguyên văn `kb/context_planning_mini.md` §"LAG entry window", chốt 2026-08-03):
  1. CHỈ mã `status` chứa `T+1` mới là ứng viên của plan HÔM NAY  → `due_today`.
  2. `T+2`/`T+3`/... → CHỈ được nằm ở `lag_upcoming_for_next_plans` → `upcoming_next_plans`.
  3. `WINDOW_PASSED` → cửa sổ đã mở/đã qua, không phải ứng viên mới → `window_passed`.
  Số lượng `due_today` PHẢI BẰNG NHAU giữa 2 account (cùng 1 CSV nguồn) — script này account-
  agnostic đúng vì vậy: chạy cho account nào cũng ra cùng danh sách, lệch = bug ở người dùng.

CỔNG LỊCH (fail-closed, lý do có `--plan-date`): "T+1" là T+1 SO VỚI `signal_date` của CSV.
Nếu `plan_date` không phải phiên giao dịch ngay sau `signal_date` (CSV cũ, lập lại plan trễ,
nghỉ lễ), thì "T+1" KHÔNG còn trỏ vào plan_date nữa — script TỪ CHỐI phân loại `due_today` và
trả `calendar_check.ok=false` thay vì đoán. Đây là kiểu sai mà đọc CSV bằng mắt không thấy.

KHÔNG suy ra ngày từ lịch giao dịch cho đường quyết định: `T+1` ⇔ `plan_date` theo định nghĩa
(khi cổng lịch PASS), nên nhánh chính không phụ thuộc bảng ngày nghỉ. Chỉ `entry_date_est` của
nhóm T+2 trở đi mới dùng `vn_market.next_trading_day` và được gắn nhãn "_est" vì `_VARIABLE_
HOLIDAYS` (Tết ÂL/giỗ Tổ) hiện rỗng — số đó chỉ để hiển thị, không dùng để quyết định gì.

    python3 mike/bin/filter_lag_entry_window.py --account SpaceX --plan-date 2026-08-04 \
        [--signal-date 2026-08-03] [--csv <path>] [--out <file.json>] [--json]
"""
import argparse
import csv
import datetime as dt
import glob
import json
import os
import re
import sys

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WC_ROOT)

from trading_bot.vn_market import next_trading_day, today_ict   # noqa: E402

RECS_DIR = os.path.join(WC_ROOT, "deploy_golive_dt5g_v4", "out")
LAG_BOOKS = ("LAG",)

# `status` do engine sinh (golive_recommend_v23.py §4, biến `item["entry"]`):
#   "UPCOMING T+<n> phiên tới"  — entry rơi n phiên SAU phiên cuối cùng đã biết (signal_date)
#   "UPCOMING <YYYY-MM-DD>"     — entry là một ngày giao dịch đã biết, > signal_date
#   "WINDOW_PASSED <YYYY-MM-DD>"— entry đã tới/đã qua trong ~5 ngày gần đây
_RE_TPLUS = re.compile(r"^UPCOMING\s+T\+(\d+)\b")
_RE_UPCOMING_DATE = re.compile(r"^UPCOMING\s+(\d{4}-\d{2}-\d{2})\s*$")
_RE_PASSED = re.compile(r"^WINDOW_PASSED\s+(\d{4}-\d{2}-\d{2})")

# Cờ đỏ DD đã được due_diligence.py sinh TẠI CHỖ và in vào cột `due_diligence` — ở đây chỉ ECHO
# lại, KHÔNG tự chấm điểm. Marker khớp đúng chuỗi `format_dd_check()` phát ra.
_RE_DD_RED = re.compile(r"🔴 DD cờ đỏ:\s*([^|⚠]+)")


def _d(x):
    """'YYYY-MM-DD' | date | datetime → date."""
    if isinstance(x, dt.datetime):
        return x.date()
    if isinstance(x, dt.date):
        return x
    return dt.date.fromisoformat(str(x)[:10])


def latest_recs_csv():
    """(path, signal_date) của CSV khuyến nghị mới nhất. (None, None) nếu không có file nào."""
    cands = sorted(glob.glob(os.path.join(RECS_DIR, "golive_v23_recommendations_*.csv")))
    if not cands:
        return None, None
    p = cands[-1]
    return p, os.path.basename(p)[len("golive_v23_recommendations_"):-len(".csv")]


def classify_status(status):
    """'UPCOMING T+2 phiên tới' → ('upcoming', 2, None). Không parse được → ('unparsed', ...)."""
    s = (status or "").strip()
    m = _RE_TPLUS.match(s)
    if m:
        return "tplus", int(m.group(1)), None
    m = _RE_UPCOMING_DATE.match(s)
    if m:
        return "date", None, _d(m.group(1))
    m = _RE_PASSED.match(s)
    if m:
        return "passed", None, _d(m.group(1))
    return "unparsed", None, None


def _dd_red_flags(dd_text):
    m = _RE_DD_RED.search(dd_text or "")
    if not m:
        return []
    return [x.strip() for x in m.group(1).split(",") if x.strip()]


def filter_window(plan_date, signal_date=None, csv_path=None):
    """Phân loại mọi dòng LAG của CSV thành due_today / upcoming_next_plans / window_passed."""
    plan_date = _d(plan_date)
    if csv_path is None:
        if signal_date is None:
            csv_path, signal_date = latest_recs_csv()
        else:
            csv_path = os.path.join(
                RECS_DIR, f"golive_v23_recommendations_{_d(signal_date)}.csv")
    if signal_date is None:
        signal_date = os.path.basename(csv_path or "")[
            len("golive_v23_recommendations_"):-len(".csv")] or None

    out = {
        "script": "mike/bin/filter_lag_entry_window.py",
        "plan_date": str(plan_date),
        "signal_date": str(_d(signal_date)) if signal_date else None,
        "csv": os.path.relpath(csv_path, WC_ROOT) if csv_path else None,
        "calendar_check": {}, "due_today": [], "upcoming_next_plans": [],
        "window_passed": [], "unparsed": [], "counts": {}, "notes": [],
    }
    if not csv_path or not os.path.exists(csv_path):
        out["error"] = f"không thấy CSV khuyến nghị: {csv_path}"
        out["calendar_check"] = {"ok": False, "reason": "thiếu CSV"}
        return out

    sig = _d(signal_date)
    expected = next_trading_day(sig)
    ok = (expected == plan_date)
    out["calendar_check"] = {
        "ok": ok, "signal_date": str(sig), "plan_date": str(plan_date),
        "expected_plan_date": str(expected),
        "reason": None if ok else (
            f"plan_date {plan_date} KHÔNG phải phiên ngay sau signal_date {sig} "
            f"(kỳ vọng {expected}) ⇒ nhãn 'T+1' của CSV không còn trỏ vào plan_date. "
            f"KHÔNG dùng danh sách này; lấy CSV đúng signal_date rồi chạy lại."),
    }

    with open(csv_path, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("book") or "").strip() in LAG_BOOKS]

    for r in rows:
        kind, off, date = classify_status(r.get("status"))
        item = {
            "ticker": (r.get("ticker") or "").strip(),
            "tier": (r.get("play_type") or "").strip(),
            "status_raw": (r.get("status") or "").strip(),
            "weight_pct": r.get("weight_pct"),
            "weight_base": r.get("weight_base"),
            "dd_red_flags": _dd_red_flags(r.get("due_diligence")),
            "floor_fail": "FLOOR_FAIL" in (r.get("due_diligence") or ""),
            "due_diligence": (r.get("due_diligence") or "").strip(),
        }
        if kind == "unparsed":
            item["reason"] = "status không khớp mẫu engine — cần người xem"
            out["unparsed"].append(item)
        elif kind == "passed":
            item["entry_date"] = str(date)
            out["window_passed"].append(item)
        elif kind == "tplus":
            item["entry_offset"] = off
            if not ok:
                item["reason"] = "cổng lịch FAIL — không phân loại được"
                out["unparsed"].append(item)
            elif off == 1:
                item["entry_date"] = str(plan_date)
                out["due_today"].append(item)
            else:
                d = sig
                for _ in range(off):
                    d = next_trading_day(d)
                item["entry_date_est"] = str(d)
                out["upcoming_next_plans"].append(item)
        else:                                    # kind == "date"
            item["entry_date"] = str(date)
            if date == plan_date:
                out["due_today"].append(item)
            elif date > plan_date:
                item["entry_offset"] = None
                out["upcoming_next_plans"].append(item)
            else:
                out["window_passed"].append(item)

    for k in ("due_today", "upcoming_next_plans", "window_passed", "unparsed"):
        out[k].sort(key=lambda x: x["ticker"])
        out["counts"][k] = len(out[k])

    out["notes"].append(
        "due_today = danh sách ứng viên LAG DUY NHẤT được xét vào orders[]/deferred_orders[] "
        "của plan hôm nay. Mọi mã ở upcoming_next_plans CHỈ được nằm ở "
        "`lag_upcoming_for_next_plans`, dù due-diligence sạch tới đâu.")
    out["notes"].append(
        "Script account-agnostic: 2 account đọc cùng CSV PHẢI ra cùng due_today. Khác nhau = "
        "một bên đọc nhầm CSV/ngày, không phải khác khẩu vị rủi ro.")
    out["notes"].append(
        "`entry_date_est` (T+2 trở đi) suy từ vn_market.next_trading_day — CHỈ để hiển thị; "
        "bảng ngày nghỉ biến động (Tết ÂL) chưa khai báo nên có thể lệch quanh kỳ nghỉ.")
    if not ok:
        out["notes"].insert(0, "⚠ CỔNG LỊCH FAIL — " + out["calendar_check"]["reason"])
    if out["unparsed"]:
        out["notes"].append(
            f"⚠ {len(out['unparsed'])} dòng không phân loại được — KHÔNG tự bỏ qua, báo lên bus.")
    return out


def _print_human(res):
    print(f"LAG entry window — plan {res['plan_date']} (signal {res['signal_date']})")
    print(f"  CSV: {res['csv']}")
    cc = res.get("calendar_check") or {}
    print(f"  Cổng lịch: {'PASS' if cc.get('ok') else 'FAIL — ' + str(cc.get('reason'))}")
    if res.get("error"):
        print(f"  LỖI: {res['error']}")
        return
    for key, title in (("due_today", "DUE TODAY (T+1) — ứng viên của plan hôm nay"),
                       ("upcoming_next_plans", "UPCOMING (T+2 trở đi) — để dành plan sau"),
                       ("window_passed", "WINDOW_PASSED — cửa sổ đã qua"),
                       ("unparsed", "KHÔNG PHÂN LOẠI ĐƯỢC")):
        items = res.get(key) or []
        print(f"\n  {title}: {len(items)}")
        for it in items:
            extra = []
            if it.get("floor_fail"):
                extra.append("FLOOR_FAIL")
            if it.get("dd_red_flags"):
                extra.append("🔴 " + ",".join(it["dd_red_flags"]))
            ed = it.get("entry_date") or it.get("entry_date_est") or "?"
            print(f"    - {it['ticker']:<5} {it['tier']:<7} entry {ed:<12} "
                  f"[{it['status_raw']}]" + (("  " + " · ".join(extra)) if extra else ""))
    for n in res.get("notes") or []:
        print(f"  · {n}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--account", default=None,
                    help="chỉ để ghi nhãn/đối chiếu — kết quả KHÔNG phụ thuộc account")
    ap.add_argument("--plan-date", default=None,
                    help="mặc định = phiên giao dịch kế tiếp tính từ hôm nay (ICT)")
    ap.add_argument("--signal-date", default=None, help="mặc định = CSV mới nhất trong out/")
    ap.add_argument("--csv", default=None, help="đè hẳn đường dẫn CSV")
    ap.add_argument("--out", default=None, help="ghi JSON ra file")
    ap.add_argument("--json", action="store_true", help="in JSON ra stdout thay vì bảng người đọc")
    a = ap.parse_args()

    plan_date = _d(a.plan_date) if a.plan_date else next_trading_day(today_ict())
    res = filter_window(plan_date, a.signal_date, a.csv)
    res["account"] = a.account
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        if not a.json:
            print(f"→ {a.out}")
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        _print_human(res)
    return 0 if (res.get("calendar_check") or {}).get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
