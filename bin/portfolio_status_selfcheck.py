#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho portfolio_status.py — chạy: python3 portfolio_status_selfcheck.py

Không mock DNSE/BQ — đọc trực tiếp file thật trên đĩa (dnse_raw, nav_history, journal),
giống production. Vì vậy assertion phải fail-soft khi input hôm nay không có (report ngày
lễ/cuối tuần) thay vì crash CI.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)

import portfolio_status as ps  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def _latest_date_with_nav(account):
    path = os.path.join(ps.EXEC_DIR, f"nav_history_{account}.csv")
    if not os.path.exists(path):
        return None
    import csv
    last = None
    with open(path, encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            if rec.get("date") and rec.get("nav"):
                last = rec["date"]
    return last


def run():
    date_spacex = _latest_date_with_nav("SpaceX")
    date_zalopay = _latest_date_with_nav("ZaloPay")

    # 1-2: module cơ bản load được, hằng số có mặt
    check("import module OK", ps is not None)
    check("SLEEVE_ORDER có 5 sleeve", len(ps.SLEEVE_ORDER) == 5, str(ps.SLEEVE_ORDER))

    # 3: account_no_for trả đúng map tĩnh tối thiểu
    check("account_no_for('SpaceX') == 0002023347",
          ps.account_no_for("SpaceX") == "0002023347", ps.account_no_for("SpaceX"))
    check("account_no_for('ZaloPay') == 0001743768",
          ps.account_no_for("ZaloPay") == "0001743768", ps.account_no_for("ZaloPay"))

    # 4: classify_sleeve — journal book thắng, kể cả khi ticker cũng nằm trong PARK/CAPIT
    check("classify_sleeve: journal LAG thắng dù ticker cũng trong PARK",
          ps.classify_sleeve("AAA", {"AAA": "LAG"}, {"AAA"}, set()) == "LAG")
    check("classify_sleeve: CORP_ACTION book bỏ qua, rơi về nhánh tiếp theo",
          ps.classify_sleeve("AAA", {"AAA": "CORP_ACTION"}, set(), {"AAA"}) == "CAPIT")
    check("classify_sleeve: không có journal, có trong PARK → PARK",
          ps.classify_sleeve("BBB", {}, {"BBB"}, set()) == "PARK")
    check("classify_sleeve: không có bằng chứng nào → mặc định BAL",
          ps.classify_sleeve("CCC", {}, set(), set()) == "BAL")

    # 5: broker_positions_with_cost — gộp nhiều loan-package cùng mã đúng cách (qty cộng dồn,
    # avg_cost = bình quân gia quyền)
    import tempfile, json as _json
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "dnse_raw_2099-01-01.jsonl")
        with open(raw, "w", encoding="utf-8") as f:
            f.write(_json.dumps({
                "kind": "positions", "account_no": "TESTACC",
                "payload": {"positions": [
                    {"symbol": "XYZ", "openQuantity": 100, "costPrice": 10.0, "marketPrice": 12.0},
                    {"symbol": "XYZ", "openQuantity": 200, "costPrice": 13.0, "marketPrice": 12.0},
                    {"symbol": "OTHERACC", "openQuantity": 999, "costPrice": 1.0},
                ]},
            }) + "\n")
            f.write(_json.dumps({
                "kind": "positions", "account_no": "WRONGACC",
                "payload": {"positions": [{"symbol": "XYZ", "openQuantity": 5000, "costPrice": 1.0}]},
            }) + "\n")
        old_exec_dir = ps.EXEC_DIR
        ps.EXEC_DIR = td
        try:
            pos = ps.broker_positions_with_cost("TESTACC", "2099-01-01")
        finally:
            ps.EXEC_DIR = old_exec_dir
        check("broker_positions_with_cost: qty cộng dồn 2 lô = 300",
              pos is not None and pos.get("XYZ", {}).get("qty") == 300.0,
              str(pos))
        expected_avg = (100 * 10.0 + 200 * 13.0) / 300
        check("broker_positions_with_cost: avg_cost bình quân gia quyền đúng",
              pos is not None and abs(pos["XYZ"]["avg_cost"] - expected_avg) < 1e-6,
              str(pos.get("XYZ")))
        check("broker_positions_with_cost: §12 lọc account — record 'WRONGACC'/'OTHERACC' không lẫn vào",
              pos is not None and pos["XYZ"]["qty"] == 300.0)

    # 6: build_output SpaceX/ZaloPay — chỉ chạy khi có NAV hôm nay (fail-soft weekend/holiday)
    if date_spacex:
        out_sx = ps.build_output("SpaceX", date_spacex)
        check(f"build_output SpaceX ({date_spacex}) không None", out_sx is not None)
        check("build_output SpaceX: có header TÌNH TRẠNG DANH MỤC",
              out_sx is not None and "TÌNH TRẠNG DANH MỤC" in out_sx)
        check("build_output SpaceX: có bảng Cơ cấu danh mục",
              out_sx is not None and "Cơ cấu danh mục" in out_sx)
    else:
        print("[SKIP] build_output SpaceX — không có nav_history_SpaceX.csv")

    if date_zalopay:
        out_zp = ps.build_output("ZaloPay", date_zalopay)
        check(f"build_output ZaloPay ({date_zalopay}) không None", out_zp is not None)
    else:
        print("[SKIP] build_output ZaloPay — không có nav_history_ZaloPay.csv")

    # 7: §12 sanity — 2 account cho output khác nhau (không đọc chung không lọc)
    if date_spacex and date_zalopay:
        out_sx = ps.build_output("SpaceX", date_spacex)
        out_zp = ps.build_output("ZaloPay", date_zalopay)
        check("§12: SpaceX và ZaloPay cho output KHÁC nhau (không lẫn account)",
              out_sx != out_zp)

    # 8: ngày TRƯỚC mọi dòng nav_history (không có "gần nhất trước") → None, không crash.
    # Lưu ý: load_nav_row() CỐ Ý fallback về dòng gần nhất TRƯỚC ngày yêu cầu (xử lý report
    # chạy vào ngày chưa có NAV hôm đó) — nên test None phải dùng ngày TRƯỚC lịch sử, không
    # phải ngày tương lai (tương lai vẫn có "gần nhất trước" = dòng cuối cùng).
    check("build_output ngày TRƯỚC mọi lịch sử NAV → None",
          ps.build_output("SpaceX", "2000-01-01") is None)

    # 9: main() trả 1 khi build_output None (không crash, không sys.exit lỗi khác)
    old_argv = sys.argv
    sys.argv = ["portfolio_status.py", "--account", "SpaceX", "--date", "2000-01-01"]
    try:
        rc = ps.main()
    finally:
        sys.argv = old_argv
    check("main() trả rc=1 khi không có NAV cho ngày đó", rc == 1, str(rc))

    print()
    if FAILS:
        print(f"SELFCHECK FAILED: {len(FAILS)} assertion — {FAILS}")
        return 1
    print("SELFCHECK PASSED — mọi assertion OK.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
