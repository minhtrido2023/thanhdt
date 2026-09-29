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

SỐ HẠNG DÒNG TIỀN (FAIL-H audit measurement-integrity 2026-09-27) — tỉ suất ở đây là
TIME-WEIGHTED RETURN, không phải tỉ số NAV thuần. Bản trước tính `nav1/nav0 − 1`: user nạp 200tr
vào SpaceX ⇒ báo cáo công bố "+20% lợi nhuận", rút 100tr ⇒ "−10%", không cảnh báo, rc=0. Chưa nổ
vì tới 2026-09-25 chưa có lần nạp/rút nào sau inception; rủi ro là lần ĐẦU TIÊN.

  - Nguồn dòng tiền: `data/account_cash_flows.json` (thủ công — DNSE OpenAPI KHÔNG có sổ nạp/rút;
    xem `account_cash_flows.py` để biết đã quét những gì). File thiếu ⇒ không có flow ⇒ công thức
    thu về ĐÚNG `nav1/nav0 − 1` như cũ, bit-for-bit.
  - TWR = chain-link, tái định giá TẠI MỖI ngày có dòng tiền (định nghĩa sách giáo khoa, không
    phải xấp xỉ Dietz). Giữa 2 ngày có dòng tiền, tỉ số NAV telescope ⇒ chỉ cần MỘT phép chia cho
    mỗi đoạn, nên khi không có flow nào thì kết quả là CHÍNH `nav1/nav0` (không có sai số dồn của
    phép nhân nhiều tỉ số).
  - Quy ước thời điểm, `timing` trong bản ghi flow:
      * `"bod"` (MẶC ĐỊNH): `r_t = nav_t / (nav_{t-1} + flow_t) − 1`. Vì DNSE ghi tiền nạp vào
        `totalCash` ngay khi nhận, mà `nav_t` là snapshot CUỐI ngày ⇒ `nav_t` ĐÃ chứa tiền nạp;
        vốn cơ sở sinh lời của ngày t vì vậy là `nav_{t-1} + flow_t`. Rút tiền: flow âm, `nav_t`
        đã trừ ⇒ cùng công thức. Đây là quy ước mặc định vì nạp/rút trong giờ giao dịch (ca phổ
        biến với TK cá nhân) khớp với nó.
      * `"eod"`: `r_t = (nav_t − flow_t) / nav_{t-1} − 1`, cho tiền vào/ra SAU khi NAV ngày t đã
        chốt theo giá đóng cửa. Sai quy ước làm lệch đúng 1 ngày lợi nhuận của phần vốn đó —
        nhỏ, nhưng là lệch có hướng, nên bắt ghi rõ thay vì đoán.
  - Vốn KHỞI ĐIỂM không phải flow: flow có `date <= inception_date` bị BỎ (nó đã nằm trong
    `starting_capital`). Nạp thêm ĐÚNG ngày inception phải gộp vào `starting_capital`, đừng ghi
    thành flow — nếu không sẽ trừ hai lần.

Dùng: python3 mike/bin/nav_period_returns.py --account SpaceX --report-date 2026-09-18
Selfcheck: python3 mike/bin/nav_period_returns.py --selfcheck
         python3 mike/bin/nav_flow_term_selfcheck.py   (số hạng dòng tiền + cổng NAV-jump)
"""
import argparse
import csv
import datetime
import json
import os
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from account_cash_flows import (CashFlowError, attach_flows_to_rows,  # noqa: E402
                                load_flows)

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INCEPTION_PATH = os.path.join(WC_ROOT, "data", "account_inception.json")
NAV_HISTORY_DIR = os.path.join(WC_ROOT, "data", "execution_logs")


def _parse_date(s: str) -> datetime.date:
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def load_inception(account: str, inception_path: str = INCEPTION_PATH) -> dict:
    with open(inception_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if account not in cfg:
        raise ValueError(f"account '{account}' không có entry trong {inception_path}")
    return cfg[account]


def load_nav_history(account: str, nav_dir: str = NAV_HISTORY_DIR) -> list:
    """Trả list [(date, nav), ...] tăng dần theo ngày."""
    path = os.path.join(nav_dir, f"nav_history_{account}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"thiếu {path}")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            if not rec.get("date") or not rec.get("nav"):
                continue
            rows.append((_parse_date(rec["date"]), float(rec["nav"])))
    rows.sort(key=lambda r: r[0])
    if not rows:
        raise ValueError(f"{path} rỗng")
    return rows


def _last_on_or_before(rows: list, d: datetime.date):
    """Row cuối cùng có date <= d, hoặc None."""
    found = None
    for rd, nav in rows:
        if rd <= d:
            found = (rd, nav)
        else:
            break
    return found


def _last_before(rows: list, d: datetime.date):
    """Row cuối cùng có date < d, hoặc None."""
    found = None
    for rd, nav in rows:
        if rd < d:
            found = (rd, nav)
        else:
            break
    return found


def _inception_baseline(rows: list, inception: dict):
    """(from_date, nav0) khởi điểm thật: starting_capital nếu có, else dòng đầu tiên."""
    starting_capital = inception.get("starting_capital")
    if starting_capital is not None:
        return _parse_date(inception["inception_date"]), float(starting_capital)
    first_date, first_nav = rows[0]
    return first_date, first_nav


def _twr_factor(seq: list, flows_by_date: dict) -> tuple:
    """Time-weighted growth factor trên chuỗi quan sát `seq` = [(date, nav), ...] tăng dần.

    Chain-link tái định giá tại MỖI ngày có dòng tiền; giữa 2 ngày đó tỉ số NAV telescope nên chỉ
    cần MỘT phép chia cho cả đoạn ⇒ không có flow nào thì factor = seq[-1][1]/seq[0][1] ĐÚNG
    bit-for-bit (không phải "gần bằng"). Trả (factor, net_flow_vnd, flows_in_period).
    """
    factor = 1.0
    base = seq[0][1]
    net_flow = 0.0
    used = []
    for i in range(1, len(seq)):
        d, nav = seq[i]
        prev_nav = seq[i - 1][1]
        day_flows = flows_by_date.get(d, [])
        f_bod = sum(f["amount_vnd"] for f in day_flows if f["timing"] == "bod")
        f_eod = sum(f["amount_vnd"] for f in day_flows if f["timing"] == "eod")
        used.extend(day_flows)
        net_flow += f_bod + f_eod
        if f_bod:
            if base <= 0:
                raise ValueError(f"vốn cơ sở <= 0 tại {seq[i - 1][0]} — không tính được TWR")
            factor *= prev_nav / base
            base = prev_nav + f_bod
            if base <= 0:
                raise ValueError(f"vốn cơ sở sau dòng tiền {d} <= 0 ({base:.0f}) — không tính "
                                 f"được TWR; kỳ này cần chia nhỏ thủ công")
        if f_eod:
            if base <= 0:
                raise ValueError(f"vốn cơ sở <= 0 tại {d} — không tính được TWR")
            factor *= (nav - f_eod) / base
            base = nav
    if base <= 0:
        raise ValueError("vốn cơ sở cuối kỳ <= 0 — không tính được TWR")
    factor *= seq[-1][1] / base
    return factor, net_flow, used


def _observation_seq(rows: list, from_date: datetime.date, nav0: float,
                     nav1_date: datetime.date, nav1: float) -> list:
    """[(from_date, nav0)] + mọi dòng nav_history trong (from_date, nav1_date].

    `from_date` có thể KHÔNG phải một dòng nav_history (baseline inception của SpaceX =
    2026-07-01, dòng đầu tiên là 07-02) ⇒ phải nối tay, không lấy slice của rows.
    """
    seq = [(from_date, nav0)]
    seq.extend((d, n) for d, n in rows if from_date < d <= nav1_date)
    if seq[-1][0] != nav1_date:
        seq.append((nav1_date, nav1))
    return seq


def _period_result(rows: list, from_date: datetime.date, nav0: float,
                   nav1_date: datetime.date, nav1: float, flows_by_date: dict) -> dict:
    """Khối kết quả một kỳ. `net_flow_vnd`/`cash_flows` chỉ xuất hiện KHI kỳ đó có dòng tiền —
    cố ý, để output giữ nguyên byte-for-byte với mọi kỳ không có dòng tiền (toàn bộ lịch sử 2 TK
    tới 2026-09-25), tức bản vá này không thể làm lệch một con số đã công bố nào."""
    seq = _observation_seq(rows, from_date, nav0, nav1_date, nav1)
    factor, net_flow, used = _twr_factor(seq, flows_by_date)
    out = {
        "from_date": from_date.isoformat(),
        "to_date": nav1_date.isoformat(),
        "nav0": nav0,
        "nav1": nav1,
        "return_pct": round((factor - 1) * 100, 3),
    }
    if used:
        out["net_flow_vnd"] = net_flow
        out["cash_flows"] = [{"date": f["date"].isoformat(), "amount_vnd": f["amount_vnd"],
                              "kind": f["kind"], "timing": f["timing"],
                              "evidence": f["evidence"]} for f in used]
    return out


def _period(rows: list, report_date: datetime.date, period_start_exclusive: datetime.date,
            inception_from: datetime.date, inception_nav0: float, nav1_date: datetime.date,
            nav1: float, flows_by_date: dict) -> dict:
    """Baseline = row cuối < period_start_exclusive; nếu không có (kỳ bắt đầu trước/đúng lúc
    inception) thì lùi về chính baseline khởi điểm — không có dữ liệu nào trước điểm đó."""
    prior = _last_before(rows, period_start_exclusive)
    if prior is not None and prior[0] >= inception_from:
        from_date, nav0 = prior
    else:
        from_date, nav0 = inception_from, inception_nav0
    return _period_result(rows, from_date, nav0, nav1_date, nav1, flows_by_date)


def compute_period_returns(account: str, report_date: datetime.date, rows: list, inception: dict,
                            flows: list = None) -> dict:
    nav1_row = _last_on_or_before(rows, report_date)
    if nav1_row is None:
        raise ValueError(f"không có dòng nav_history nào <= {report_date} cho {account}")
    nav1_date, nav1 = nav1_row

    inception_from, inception_nav0 = _inception_baseline(rows, inception)
    if nav1_date < inception_from:
        raise ValueError(f"report-date {report_date} có nav1_date {nav1_date} trước inception "
                          f"{inception_from} cho {account}")

    if flows is None:
        # require_file=True: day la duong CONG BO SO (§21/§31). Thieu so dong tien ⇒ TU CHOI,
        # khong duoc doan `[]` (mot lan NAP thanh LAI — sai theo huong co loi cho minh).
        flows = load_flows(account, require_file=True)
    # Vốn khởi điểm KHÔNG phải flow — bỏ mọi bản ghi <= mốc baseline (nó đã nằm trong nav0).
    flows = [f for f in flows if f["date"] > inception_from]
    flows_by_date = attach_flows_to_rows(rows, flows)
    flows_by_date.pop(None, None)   # flow sau dòng nav_history cuối cùng: ngoài mọi kỳ đo

    monday = report_date - datetime.timedelta(days=report_date.weekday())
    month_start = report_date.replace(day=1)

    out = {
        "account": account,
        "report_date": report_date.isoformat(),
        "inception": _period_result(rows, inception_from, inception_nav0, nav1_date, nav1,
                                    flows_by_date),
        "wtd": _period(rows, report_date, monday, inception_from, inception_nav0, nav1_date, nav1,
                        flows_by_date),
        "mtd": _period(rows, report_date, month_start, inception_from, inception_nav0, nav1_date,
                        nav1, flows_by_date),
    }
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
        result = compute_period_returns(args.account, report_date, rows, inception)
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

    zalopay_rows = load_nav_history("ZaloPay")
    zalopay_inception = load_inception("ZaloPay")
    assert zalopay_inception["starting_capital"] is None, "ZaloPay starting_capital phải null"
    zfirst_date, zfirst_nav = zalopay_rows[0]
    zresult = compute_period_returns("ZaloPay", datetime.date(2026, 9, 18), zalopay_rows, zalopay_inception)
    assert zresult["inception"]["nav0"] == zfirst_nav, "ZaloPay inception nav0 phải = dòng đầu (không starting_capital)"
    assert zresult["inception"]["from_date"] == zfirst_date.isoformat()
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
