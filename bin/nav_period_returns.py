#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tính lợi nhuận theo kỳ (WTD/MTD/từ khi bắt đầu hoạt động) cho MỘT account, từ
`nav_history_{account}.csv` + baseline khởi điểm ở `data/account_inception.json`.

Nguồn chuẩn tắc DUY NHẤT cho hàng "Hiệu suất lũy kế" trong báo cáo SpaceX weekly/monthly
(coding_guidelines §6/§9 — không tự tính lại từ nav_history raw). Lý do cần script riêng: dòng
đầu tiên trong `nav_history_SpaceX.csv` (07-02) là snapshot SAU phiên giao dịch đầu tiên, không
phải vốn khởi điểm thật (1.000.000.000đ nạp ngày 01/07) — dùng thẳng dòng đầu làm baseline sẽ ra
return sai lệch so với thực tế (đã xảy ra thật trong báo cáo tuần 09-14→09-18: báo -1,66% thay vì
-2,177%). ZaloPay không bị lỗi này (không có `starting_capital` ⇒ dùng dòng đầu, vì tài khoản có
vị thế legacy trước khi bot go-live, không có mốc "vốn nạp ngày 1" sạch).

TỈ SUẤT = TỈ SỐ HAI GIÁ ĐƠN VỊ QUỸ (chính sách "tài khoản = quỹ mở", user duyệt 2026-10-10 —
`kb/projects/fund-unit-performance-policy-20261010.md`). `return_pct` của một kỳ là
`giá_đơn_vị[to_date] / giá_đơn_vị[from_date] − 1`, hai giá lấy từ sổ đơn vị do
`nav_unit_ledger.build_ledger` dựng — đó là công thức DUY NHẤT; file này không còn tự chain-link.
Đây là tỉ suất GIA QUYỀN THỜI GIAN: nạp/rút phát hành/huỷ đơn vị ở giá chốt nên không làm đổi giá.
(Bản đầu tiên tính `nav1/nav0 − 1`: nạp 200tr vào SpaceX ⇒ công bố "+20% lợi nhuận" — FAIL-H,
audit measurement-integrity 2026-09-27.)

  - Nguồn dòng tiền: `data/account_cash_flows.json` (thủ công — DNSE OpenAPI KHÔNG có sổ nạp/rút;
    xem `account_cash_flows.py`). Kỳ không có dòng tiền: số đơn vị không đổi ⇒ tỉ số giá =
    `nav1/nav0`, đúng số đã công bố trước khi có sổ đơn vị.
  - Quy tắc chốt (`timing` của bản ghi dòng tiền; chi tiết + công thức: `nav_unit_ledger.py`):
      * `"eod"` (MẶC ĐỊNH từ 2026-10-10): tiền ngày T giao dịch ở giá chốt CUỐI ngày T ⇒
        `r_t = (nav_t − flow_t) / nav_{t-1} − 1`.
      * `"bod"` (khai tường minh kèm `time_ict`): giao dịch ở giá chốt phiên liền trước ⇒
        `r_t = nav_t / (nav_{t-1} + flow_t) − 1`.
  - Vốn KHỞI ĐIỂM không phải flow: flow có `date <= inception_date` bị BỎ (nó đã nằm trong
    `starting_capital`). Nạp thêm ĐÚNG ngày inception phải gộp vào `starting_capital`, đừng ghi
    thành flow — nếu không sẽ tính hai lần.

HAI SỐ CỦA CHỦ TÀI KHOẢN, tách khỏi tỉ suất gia quyền thời gian (không trộn):
  - `pnl_vnd` = nav1 − nav0 − dòng tiền ròng của kỳ — lãi/lỗ bằng tiền.
  - `mwr_pct` = tỉ suất gia quyền THEO TIỀN (IRR) của CẢ KỲ, không quy năm: nghiệm R của
    `nav0·(1+R) + Σ flow_i·(1+R)^{w_i} = nav1`, `w_i` = phần kỳ còn lại sau dòng tiền i (theo
    ngày lịch). Không có nghiệm duy nhất ⇒ `null` kèm `mwr_note`.
QUY NĂM: kỳ < 365 ngày lịch ⇒ `annualized_return_pct` và `mwr_annualized_pct` là `null` kèm
`annualized_note` (`annualize_or_null` là cửa duy nhất).

Dùng: python3 mike/bin/nav_period_returns.py --account SpaceX --report-date 2026-09-18
Selfcheck: python3 mike/bin/nav_period_returns.py --selfcheck
         python3 mike/bin/nav_flow_term_selfcheck.py   (số hạng dòng tiền + cổng NAV-jump)
"""
import argparse
import datetime
import json
import os
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_cash_flows import CashFlowError, load_flows  # noqa: E402
from nav_unit_ledger import (INCEPTION_PATH, NAV_HISTORY_DIR, LedgerDriftError,  # noqa: E402,F401
                             _inception_baseline, _parse_date, build_ledger,
                             diff_against_sealed, ledger_path, load_inception,
                             load_nav_history, read_sealed)

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

ANNUALIZE_MIN_DAYS = 365


def _last_on_or_before(rows: list, d: datetime.date):
    """Row cuối cùng có date <= d, hoặc None."""
    found = None
    for rd, nav in rows:
        if rd <= d:
            found = (rd, nav)
        else:
            break
    return found


def annualize_or_null(factor: float, days: int) -> tuple:
    """Cửa DUY NHẤT cho số quy năm của tài khoản thật. Trả `(pct | None, lý_do | None)`:
    kỳ < 365 ngày lịch ⇒ `(None, lý do)` — không quy năm (chính sách 2026-10-10)."""
    if days < ANNUALIZE_MIN_DAYS:
        return None, (f"kỳ {days} ngày lịch < {ANNUALIZE_MIN_DAYS} — không quy năm "
                      f"(chính sách đo hiệu suất 2026-10-10)")
    if factor <= 0:
        return None, f"hệ số tăng trưởng {factor} <= 0 — không quy năm được"
    return round((factor ** (365.0 / days) - 1) * 100, 3), None


def money_weighted_return(nav0: float, nav1: float, flows: list) -> tuple:
    """Tỉ suất gia quyền theo tiền của CẢ KỲ (không quy năm). `flows` = [(w, amount_vnd), ...],
    `w` ∈ [0, 1] = phần kỳ CÒN LẠI sau dòng tiền. Nghiệm x = 1 + R của
        nav0·x + Σ amount·x^w − nav1 = 0.
    Trả `(R | None, ghi_chú | None)`. Có rút tiền thì phương trình có thể có 0 hoặc nhiều nghiệm
    ⇒ `None` + ghi chú, không chọn hộ một nghiệm."""
    flows = [(w, a) for w, a in flows if a]
    if not flows:
        return nav1 / nav0 - 1, None

    def f(x):
        return nav0 * x + sum(a * x ** w for w, a in flows) - nav1

    grid = [10 ** (-3 + 6 * i / 6000) for i in range(6001)]       # x ∈ [0,001; 1000]
    roots = []
    for lo, hi in zip(grid, grid[1:]):
        f_lo, f_hi = f(lo), f(hi)
        if f_lo == 0:
            roots.append(lo)
        elif f_lo * f_hi < 0:
            for _ in range(200):
                mid = (lo + hi) / 2
                if f_lo * f(mid) <= 0:
                    hi = mid
                else:
                    lo, f_lo = mid, f(mid)
            roots.append((lo + hi) / 2)
    if len(roots) != 1:
        return None, (f"IRR không xác định duy nhất: {len(roots)} nghiệm trong khoảng "
                      f"−99,9%…+99.900% (dòng tiền đổi dấu nhiều lần)")
    return roots[0] - 1, None


def _period_result(ledger: list, i0: int, i1: int) -> dict:
    """Khối kết quả kỳ `ledger[i0] → ledger[i1]`. `net_flow_vnd`/`cash_flows` chỉ xuất hiện KHI
    kỳ đó có dòng tiền (giữ nguyên hợp đồng cũ)."""
    a, b = ledger[i0], ledger[i1]
    factor = b["unit_price"] / a["unit_price"]
    days = (b["date"] - a["date"]).days
    used, weighted = [], []
    for row in ledger[i0 + 1:i1 + 1]:
        for f in row["flows"]:
            used.append(f)
            # eod: tiền vào cuối ngày `row`; bod: có mặt từ đầu ngày `row` = cuối ngày lịch trước.
            at = row["date"] if f["timing"] == "eod" else row["date"] - datetime.timedelta(days=1)
            weighted.append((min(1.0, (b["date"] - at).days / days), f["amount_vnd"]))
    net_flow = sum(f["amount_vnd"] for f in used)
    mwr, mwr_note = money_weighted_return(a["nav"], b["nav"], weighted)
    ann, ann_note = annualize_or_null(factor, days)
    mwr_ann = annualize_or_null(1 + mwr, days)[0] if mwr is not None else None
    out = {
        "from_date": a["date"].isoformat(),
        "to_date": b["date"].isoformat(),
        "nav0": a["nav"],
        "nav1": b["nav"],
        "return_pct": round((factor - 1) * 100, 3),
    }
    if used:
        out["net_flow_vnd"] = net_flow
        out["cash_flows"] = [{"date": f["date"].isoformat(), "amount_vnd": f["amount_vnd"],
                              "kind": f["kind"], "timing": f["timing"],
                              "evidence": f["evidence"]} for f in used]
    out.update({
        "days": days,
        "unit_price0": round(a["unit_price"], 4),
        "unit_price1": round(b["unit_price"], 4),
        "pnl_vnd": b["nav"] - a["nav"] - net_flow,
        "mwr_pct": round(mwr * 100, 3) if mwr is not None else None,
        "annualized_return_pct": ann,
        "mwr_annualized_pct": mwr_ann,
    })
    if mwr_note:
        out["mwr_note"] = mwr_note
    if ann_note:
        out["annualized_note"] = ann_note
    return out


def _period(ledger: list, period_start_exclusive: datetime.date, i1: int) -> dict:
    """Baseline = dòng sổ cuối < period_start_exclusive; không có (kỳ bắt đầu trước/đúng lúc
    inception) thì lùi về chính mốc khởi điểm (dòng 0) — không có dữ liệu nào trước điểm đó."""
    i0 = 0
    for i, row in enumerate(ledger[:i1 + 1]):
        if row["date"] < period_start_exclusive:
            i0 = i
    return _period_result(ledger, i0, i1)


def compute_period_returns(account: str, report_date: datetime.date, rows: list, inception: dict,
                            flows: list = None, sealed_path: str = None) -> dict:
    """`sealed_path`: đường dẫn sổ đơn vị đã chốt để ĐỐI CHIẾU (đường CLI truyền vào). Sổ có mà
    chuỗi dựng lại lệch dòng đã chốt ⇒ LedgerDriftError — không công bố một số khác sổ."""
    nav1_row = _last_on_or_before(rows, report_date)
    if nav1_row is None:
        raise ValueError(f"không có dòng nav_history nào <= {report_date} cho {account}")
    nav1_date = nav1_row[0]

    inception_from, inception_nav0 = _inception_baseline(rows, inception)
    if nav1_date < inception_from:
        raise ValueError(f"report-date {report_date} có nav1_date {nav1_date} trước inception "
                          f"{inception_from} cho {account}")

    if flows is None:
        # require_file=True: day la duong CONG BO SO (§21/§31). Thieu so dong tien ⇒ TU CHOI,
        # khong duoc doan `[]` (mot lan NAP thanh LAI — sai theo huong co loi cho minh).
        flows = load_flows(account, require_file=True)
    # Vốn khởi điểm KHÔNG phải flow, flow sau dòng nav_history cuối nằm ngoài mọi kỳ đo — cả hai
    # do build_ledger loại.
    ledger, _ = build_ledger(rows, flows, inception_from, inception_nav0)
    i1 = max(i for i, row in enumerate(ledger) if row["date"] <= report_date)

    monday = report_date - datetime.timedelta(days=report_date.weekday())
    month_start = report_date.replace(day=1)

    out = {
        "account": account,
        "report_date": report_date.isoformat(),
        "inception": _period_result(ledger, 0, i1),
        "wtd": _period(ledger, monday, i1),
        "mtd": _period(ledger, month_start, i1),
    }
    if sealed_path is not None:
        sealed = read_sealed(sealed_path)
        diffs = diff_against_sealed(ledger, sealed)
        if diffs:
            raise LedgerDriftError(sealed_path, diffs)
        out["unit_ledger"] = {"path": sealed_path,
                              "sealed_through": sealed[-1]["date"].isoformat() if sealed else None}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account", choices=["SpaceX", "ZaloPay"])
    ap.add_argument("--report-date", help="YYYY-MM-DD (giờ ICT); mặc định hôm nay ICT")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()

    if args.selfcheck:
        return _selfcheck()

    if not args.account:
        ap.error("cần --account (hoặc --selfcheck)")

    try:
        report_date = (_parse_date(args.report_date) if args.report_date
                        else datetime.datetime.now(ICT).date())
        rows = load_nav_history(args.account)
        inception = load_inception(args.account)
        result = compute_period_returns(args.account, report_date, rows, inception,
                                        sealed_path=ledger_path(args.account))
    except (FileNotFoundError, ValueError, KeyError, CashFlowError) as e:
        print(f"LỖI nav_period_returns: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _selfcheck() -> int:
    """5+ assertion trên data thật (nav_history_SpaceX/ZaloPay.csv, account_inception.json)."""
    n = 0

    spacex_rows = load_nav_history("SpaceX")
    spacex_inception = load_inception("SpaceX")
    assert spacex_inception["starting_capital"] == 1_000_000_000, "SpaceX starting_capital phải 1B"
    n += 1

    first_date, first_nav = spacex_rows[0]
    assert first_date == datetime.date(2026, 7, 2), f"dòng đầu SpaceX phải 07-02, được {first_date}"
    n += 1

    # Ca thật đã cắn: báo cáo tuần 09-14->09-18 dùng first-row baseline ra -1.66%; đúng phải -2.177%
    result = compute_period_returns("SpaceX", datetime.date(2026, 9, 18), spacex_rows, spacex_inception)
    assert result["inception"]["nav0"] == 1_000_000_000.0, "inception nav0 phải = starting_capital"
    assert result["inception"]["from_date"] == "2026-07-01", "inception from_date phải = inception_date"
    assert abs(result["inception"]["return_pct"] - (-2.177)) < 0.01, \
        f"inception return_pct sai: {result['inception']['return_pct']} (kỳ vọng ~-2.177)"
    n += 1

    # ZaloPay: baseline = starting_capital 987.865.567 tại 2026-07-06 (user duyệt 2026-09-27,
    # Option A) — assertion cũ "starting_capital phải null" đã lỗi thời từ ngày đó.
    zalopay_rows = load_nav_history("ZaloPay")
    zalopay_inception = load_inception("ZaloPay")
    assert zalopay_inception["starting_capital"] == 987_865_567, "ZaloPay starting_capital phải 987.865.567"
    zresult = compute_period_returns("ZaloPay", datetime.date(2026, 9, 18), zalopay_rows, zalopay_inception)
    assert zresult["inception"]["nav0"] == 987_865_567.0, "ZaloPay inception nav0 phải = starting_capital"
    assert zresult["inception"]["from_date"] == "2026-07-06"
    n += 1

    # Không có starting_capital ⇒ baseline lùi về dòng đầu nav_history (nhánh dự phòng còn sống).
    legacy = compute_period_returns("ZaloPay", datetime.date(2026, 9, 18), zalopay_rows,
                                    {"inception_date": "2026-07-06", "starting_capital": None}, [])
    assert legacy["inception"]["nav0"] == zalopay_rows[0][1], "thiếu starting_capital ⇒ nav0 = dòng đầu"
    assert legacy["inception"]["from_date"] == zalopay_rows[0][0].isoformat()
    n += 1

    # WTD: baseline phải là dòng cuối TRƯỚC thứ Hai của tuần chứa report_date (tuần 09-14..09-18,
    # thứ Hai = 09-14, nên baseline = dòng cuối trước 09-14 = 09-11 nếu tồn tại).
    monday = datetime.date(2026, 9, 14) - datetime.timedelta(days=datetime.date(2026, 9, 14).weekday())
    assert monday == datetime.date(2026, 9, 14), "sanity: 2026-09-14 phải là thứ Hai"
    wtd = result["wtd"]
    assert datetime.datetime.strptime(wtd["from_date"], "%Y-%m-%d").date() < monday, \
        "wtd from_date phải trước thứ Hai của tuần report_date"
    n += 1

    # MTD: baseline phải trước 2026-09-01
    mtd = result["mtd"]
    assert datetime.datetime.strptime(mtd["from_date"], "%Y-%m-%d").date() < datetime.date(2026, 9, 1), \
        "mtd from_date phải trước đầu tháng 9"
    n += 1

    # Edge case: report_date == inception_date-adjacent (kỳ WTD/MTD lùi về trước cả inception)
    # -> baseline phải fallback về chính inception, không lỗi/không âm vô hạn.
    early = compute_period_returns("SpaceX", datetime.date(2026, 7, 3), spacex_rows, spacex_inception)
    assert early["wtd"]["from_date"] == "2026-07-01", \
        f"wtd đầu kỳ phải fallback về inception_date, được {early['wtd']['from_date']}"
    n += 1

    # Fail path: account không tồn tại trong inception config
    try:
        load_inception("NoSuchAccount")
        raise AssertionError("load_inception phải raise cho account không tồn tại")
    except ValueError:
        pass
    n += 1

    print(f"OK — {n} assertion PASS (nav_period_returns.py)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
