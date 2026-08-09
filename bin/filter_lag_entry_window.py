#!/usr/bin/env python3
"""Lọc CỬA SỔ ENTRY của book LAG — quyết định CƠ HỌC, không còn để LLM tự nhớ luật.

⚠️ CHỈ ĐỌC. Không đặt lệnh, không ghi vào bất kỳ file plan nào, không gọi DNSE.
   Đầu vào chính là CSV khuyến nghị mà engine đã sinh ra; đầu ra là các rổ đã phân loại.
   `filter_window()` VẪN THUẦN OFFLINE. Chỉ đường CLI — và chỉ khi có ứng viên phiên 2/3 — mới
   gọi `lag_entry_anchor.py` → 1 truy vấn BQ lấy giá THÔ LỊCH SỬ của phiên chuẩn. Giá TRONG
   NGÀY vẫn tuyệt đối không lấy từ BQ (§6): việc so anchor với giá live là của tầng đặt lệnh.

VÌ SAO CÓ FILE NÀY (sự cố thật 2026-08-04): `golive_v23_recommendations_<signal>.csv` gắn sẵn
`status` đúng cho từng mã (`UPCOMING T+1 phiên tới` / `T+2` / `T+3` / `WINDOW_PASSED <ngày>`),
nhưng KHÔNG script nào biến nó thành danh sách ứng viên — mỗi phiên DollarBill tự đọc CSV và
tự lọc bằng tay. Cùng 1 CSV (signal 2026-08-03), plan SpaceX lọc ĐÚNG (chỉ T+1) còn plan
ZaloPay đưa nhầm DCM (T+2) + DRI/POW (T+3) vào `deferred_orders` của hôm nay ĐỒNG THỜI bỏ sót
APF/MAC/TV3 (đều T+1). 0 lệnh thật nên không mất tiền, nhưng đây là lỗi dữ liệu thuần cơ học:
không có phán đoán nào ở đây cả, chỉ là đọc 1 cột chuỗi. Cùng khuôn với `park_holdings.py`
(book_note) — chuyển việc "LLM phải nhớ luật" thành "script trả lời sẵn".

QUY TẮC V2.4 (user-approved 2026-08-09):
  1. Cửa sổ entry = phiên chuẩn T+5 và HAI phiên kế tiếp (tối đa 3 phiên).
  2. Trong phiên 2/3, chỉ được hoàn tất residual chưa khớp hoặc mở vị thế chưa khớp
     nếu giá live không vượt `entry_anchor_price` đã lưu ở phiên chuẩn. Không average-up.
  3. Hết phiên 3, `WINDOW_PASSED` và không catch-up. Sizing, %ADV, 8L/DD/governance
     giữ nguyên; ngày thoát vẫn neo theo lịch entry chuẩn.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lag_entry_anchor as anchor_mod                           # noqa: E402

RECS_DIR = os.path.join(WC_ROOT, "deploy_golive_dt5g_v4", "out")
LAG_BOOKS = ("LAG",)
LATE_WINDOW_SESSIONS = 2   # scheduled entry + this many following trading sessions

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


def _sessions_after(entry_date, plan_date, cap=LATE_WINDOW_SESSIONS):
    """Trading sessions elapsed after scheduled entry, capped for a fail-closed window.
    Returns 0 on the scheduled date, 1/2 inside V2.4, or None outside it."""
    d = _d(entry_date)
    plan = _d(plan_date)
    for n in range(cap + 1):
        if d == plan:
            return n
        d = next_trading_day(d)
    return None


def _apply_anchor_gate(out, plan_date, anchor_fetcher):
    """CHỐT CỬA của luật V2.4: ứng viên phiên 2/3 chỉ được ở lại `due_today` khi có
    `entry_anchor_price` THẬT (một con số), vì điều kiện an toàn của luật là "giá live không
    vượt anchor" — không có anchor thì điều kiện đó không kiểm được, và một ứng viên không
    kiểm được KHÔNG PHẢI là một ứng viên hợp lệ.

    FAIL-CLOSED ở mọi nhánh hỏng: thiếu nguồn tra, BQ lỗi, mã không có dữ liệu ngày đó, giá
    <= 0 ⇒ mã bị CHUYỂN sang `anchor_unavailable` kèm `drop_reason`, KHÔNG đoán giá thay thế
    và KHÔNG im lặng thả vào orders. Phiên 1 (entry chuẩn) không cần anchor — chính nó là
    phiên đặt ra anchor."""
    late = [it for it in out["due_today"] if (it.get("entry_window_day") or 1) >= 2]
    if not late:
        return
    if anchor_fetcher is None:
        prices, err = {}, ("không có nguồn tra anchor được truyền vào (anchor_fetcher=None) — "
                           "chạy CLI không có --no-anchor để bật tra BQ")
    else:
        try:
            prices = anchor_fetcher([(it["ticker"], it["entry_date"]) for it in late], plan_date)
            err = None
        except Exception as e:                               # noqa: BLE001
            prices, err = {}, f"tra anchor thất bại: {e}"

    keep = []
    for it in out["due_today"]:
        if (it.get("entry_window_day") or 1) < 2:
            keep.append(it)
            continue
        px = prices.get((it["ticker"], it["entry_date"]))
        if px is None or px <= 0:
            it["drop_reason"] = err or (
                f"không tra được giá thô phiên chuẩn {it['entry_date']} của {it['ticker']} "
                f"⇒ không kiểm được điều kiện 'giá live <= anchor'")
            out["anchor_unavailable"].append(it)
        else:
            it["entry_anchor_price"] = float(px)
            it["entry_anchor_date"] = it["entry_date"]
            it["entry_anchor_source"] = anchor_mod.ANCHOR_SOURCE
            keep.append(it)
    out["due_today"] = keep


def filter_window(plan_date, signal_date=None, csv_path=None, anchor_fetcher=None):
    """Classify LAG rows; due_today includes eligible V2.4 window days 1..3.

    `anchor_fetcher` [(ticker, entry_date)], plan_date → {(ticker, date): giá thô}. Mặc định
    None = KHÔNG tra ⇒ mọi ứng viên phiên 2/3 rơi vào `anchor_unavailable` (fail-closed). Giữ
    hàm này thuần offline được là có chủ đích: selfcheck tiêm fetcher giả, không đụng mạng."""
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
        "window_passed": [], "anchor_unavailable": [], "unparsed": [],
        "counts": {}, "notes": [],
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
            elapsed = _sessions_after(date, plan_date)
            if ok and elapsed is not None:
                item["entry_window_day"] = elapsed + 1
                item["execution_mode"] = "RESIDUAL_OR_NEW_AT_OR_BELOW_ANCHOR"
                item["requires_anchor_price"] = True
                out["due_today"].append(item)
            else:
                out["window_passed"].append(item)
        elif kind == "tplus":
            item["entry_offset"] = off
            if not ok:
                item["reason"] = "cổng lịch FAIL — không phân loại được"
                out["unparsed"].append(item)
            elif off == 1:
                item["entry_date"] = str(plan_date)
                item["entry_window_day"] = 1
                item["execution_mode"] = "SCHEDULED_ENTRY"
                out["due_today"].append(item)
            else:
                d = sig
                for _ in range(off):
                    d = next_trading_day(d)
                item["entry_date_est"] = str(d)
                out["upcoming_next_plans"].append(item)
        else:                                    # kind == "date"
            item["entry_date"] = str(date)
            elapsed = _sessions_after(date, plan_date)
            if ok and elapsed is not None:
                item["entry_window_day"] = elapsed + 1
                item["execution_mode"] = ("SCHEDULED_ENTRY" if elapsed == 0 else
                                          "RESIDUAL_OR_NEW_AT_OR_BELOW_ANCHOR")
                item["requires_anchor_price"] = bool(elapsed)
                out["due_today"].append(item)
            elif date > plan_date:
                item["entry_offset"] = None
                out["upcoming_next_plans"].append(item)
            else:
                out["window_passed"].append(item)

    _apply_anchor_gate(out, plan_date, anchor_fetcher)

    for k in ("due_today", "upcoming_next_plans", "window_passed", "anchor_unavailable",
              "unparsed"):
        out[k].sort(key=lambda x: x["ticker"])
        out["counts"][k] = len(out[k])

    out["notes"].append(
        "due_today = ứng viên trong entry window V2.4. entry_window_day=2/3 chỉ được đặt "
        "cho residual hoặc vị thế chưa khớp, sau khi broker xác nhận target/fill và giá live "
        "<= entry_anchor_price đã lưu ở ngày chuẩn; không được mua đuổi.")
    out["notes"].append(
        "entry_anchor_price = giá THÔ (`Price`) của phiên chuẩn, KHÔNG phải `Close` (đã điều "
        "chỉnh cổ tức ⇒ khác hệ quy chiếu với giá live). Đây là TRẦN để so, không phải giá đặt "
        "lệnh; giá live để so PHẢI lấy DNSE (§6), không lấy BQ.")
    if out["anchor_unavailable"]:
        out["notes"].append(
            f"⚠ {len(out['anchor_unavailable'])} mã phiên 2/3 BỊ LOẠI vì không có anchor thật — "
            f"fail-closed, xem `drop_reason`. KHÔNG được đưa vào orders[] bằng giá tự suy.")
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
    for key, title in (("due_today", "ENTRY WINDOW ACTIVE — ứng viên của plan hôm nay"),
                       ("upcoming_next_plans", "UPCOMING (T+2 trở đi) — để dành plan sau"),
                       ("window_passed", "WINDOW_PASSED — cửa sổ đã qua"),
                       ("anchor_unavailable", "BỊ LOẠI — phiên 2/3 không có anchor thật"),
                       ("unparsed", "KHÔNG PHÂN LOẠI ĐƯỢC")):
        items = res.get(key) or []
        print(f"\n  {title}: {len(items)}")
        for it in items:
            extra = []
            if it.get("floor_fail"):
                extra.append("FLOOR_FAIL")
            if it.get("dd_red_flags"):
                extra.append("🔴 " + ",".join(it["dd_red_flags"]))
            if it.get("entry_anchor_price"):
                extra.append(f"anchor {it['entry_anchor_price']:,.0f}")
            if it.get("drop_reason"):
                extra.append("⛔ " + it["drop_reason"])
            ed = it.get("entry_date") or it.get("entry_date_est") or "?"
            print(f"    - {it['ticker']:<5} {it['tier']:<7} entry {ed:<12} "
                  f"[day {it.get('entry_window_day', '?')}: {it['status_raw']}]" +
                  (("  " + " · ".join(extra)) if extra else ""))
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
    ap.add_argument("--no-anchor", action="store_true",
                    help="KHÔNG tra anchor từ BQ (xem phân loại offline). Mọi ứng viên phiên "
                         "2/3 sẽ bị loại sang anchor_unavailable — đừng dùng để lập plan.")
    a = ap.parse_args()

    plan_date = _d(a.plan_date) if a.plan_date else next_trading_day(today_ict())
    res = filter_window(plan_date, a.signal_date, a.csv,
                        anchor_fetcher=None if a.no_anchor else anchor_mod.fetch_anchor_prices)
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
