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

    # 5b: FAIL-SAFE (quant-skeptic 2026-09-30) — 1 lô thiếu costPrice ⇒ avg_cost=None cho CẢ mã,
    # KHÔNG âm thầm tính thiếu-trọng-số trên phần qty còn lại (tránh hiểu nhầm mức lỗ thấp hơn
    # thực tế khi dùng làm input quyết định stop-loss).
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "dnse_raw_2099-01-02.jsonl")
        with open(raw, "w", encoding="utf-8") as f:
            f.write(_json.dumps({
                "kind": "positions", "account_no": "TESTACC",
                "payload": {"positions": [
                    {"symbol": "ABC", "openQuantity": 100, "costPrice": 10.0, "marketPrice": 12.0},
                    {"symbol": "ABC", "openQuantity": 200, "costPrice": None, "marketPrice": 12.0},
                ]},
            }) + "\n")
        old_exec_dir = ps.EXEC_DIR
        ps.EXEC_DIR = td
        try:
            pos = ps.broker_positions_with_cost("TESTACC", "2099-01-02")
        finally:
            ps.EXEC_DIR = old_exec_dir
        check("broker_positions_with_cost: qty vẫn cộng dồn đủ dù thiếu costPrice ở 1 lô",
              pos is not None and pos.get("ABC", {}).get("qty") == 300.0, str(pos))
        check("broker_positions_with_cost: avg_cost=None khi CÓ lô thiếu costPrice (fail-safe)",
              pos is not None and pos["ABC"]["avg_cost"] is None, str(pos.get("ABC")))

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

    # 10: count_trading_days — dùng next_trading_day thật (§16 RULE 2), không đếm lịch tay
    import datetime as _dt
    n = ps.count_trading_days(_dt.date(2026, 8, 10), _dt.date(2026, 9, 29))
    check("count_trading_days(2026-08-10 → 2026-09-29) == 33 (bao gồm bù lễ Quốc khánh)",
          n == 33, str(n))
    check("count_trading_days: asof <= start → 0",
          ps.count_trading_days(_dt.date(2026, 9, 29), _dt.date(2026, 9, 29)) == 0)

    # 11: lag_entry_dates — quét journal, lấy FILL mua LAG ĐẦU TIÊN, bỏ qua sell + book khác
    with tempfile.TemporaryDirectory() as td:
        old_exec_dir = ps.EXEC_DIR
        ps.EXEC_DIR = td
        try:
            with open(os.path.join(td, "exec_TESTACC_2026-01-05_journal.csv"), "w", encoding="utf-8") as f:
                f.write("ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")
                f.write("2026-01-05T09:30:00,FILL,p1,XYZ,buy,c1,100,10.0,100,LAG,TIER1,\n")
                f.write("2026-01-05T10:00:00,FILL,p2,XYZ,sell,c2,50,10.5,50,LAG,TIER1,\n")
                f.write("2026-01-05T10:05:00,FILL,p3,ABC,buy,c3,100,20.0,100,BAL,MOM,\n")
            with open(os.path.join(td, "exec_TESTACC_2026-01-10_journal.csv"), "w", encoding="utf-8") as f:
                f.write("ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")
                f.write("2026-01-10T09:30:00,FILL,p4,XYZ,buy,c4,100,11.0,200,LAG,TIER1,\n")
            entries = ps.lag_entry_dates("TESTACC")
        finally:
            ps.EXEC_DIR = old_exec_dir
        check("lag_entry_dates: XYZ entry = FILL mua LAG SỚM NHẤT across nhiều file (01-05, không phải 01-10)",
              entries.get("XYZ") == "2026-01-05", str(entries))
        check("lag_entry_dates: bỏ qua book khác (ABC/BAL không xuất hiện)",
              "ABC" not in entries, str(entries))

    # 12: lag_exit_hint — trong cửa, đã qua cửa, và None khi không có entry date
    h_in_window = ps.lag_exit_hint("SCL", {"SCL": "2026-09-08"}, "2026-09-29")  # 15 phiên
    check("lag_exit_hint: trong cửa T+14/T+20 → có text 'còn ~'",
          h_in_window is not None and "còn ~" in h_in_window, str(h_in_window))
    h_past = ps.lag_exit_hint("SCL", {"SCL": "2026-08-10"}, "2026-09-29")
    check("lag_exit_hint: đã qua T+20 → 'ĐÃ QUA'",
          h_past is not None and "ĐÃ QUA" in h_past, str(h_past))
    check("lag_exit_hint: không có entry date → None",
          ps.lag_exit_hint("ZZZ", {}, "2026-09-29") is None)

    # 13: latest_recs_csv chọn theo TÊN FILE (ngày signal), không phải mtime
    with tempfile.TemporaryDirectory() as td:
        old_recs_dir = ps.RECS_DIR
        ps.RECS_DIR = td
        try:
            older = os.path.join(td, "golive_v23_recommendations_2026-09-20.csv")
            newer = os.path.join(td, "golive_v23_recommendations_2026-09-25.csv")
            with open(newer, "w", encoding="utf-8") as f:
                f.write("book,ticker,status\nBAL,FPT,FULL\n")
            with open(older, "w", encoding="utf-8") as f:
                f.write("book,ticker,status\nBAL,MBB,FULL\n")
            os.utime(newer, (1000000000, 1000000000))  # mtime CŨ hơn 'older' dù tên ngày MỚI hơn
            recs_date, recs_path = ps.latest_recs_csv()
            recs_by_book = ps.load_recs(recs_path)
        finally:
            ps.RECS_DIR = old_recs_dir
        check("latest_recs_csv: chọn theo tên file (2026-09-25), bất kể mtime",
              recs_date == "2026-09-25", str(recs_date))
        check("load_recs: đọc đúng book BAL của file được chọn (FPT, không phải MBB)",
              recs_by_book.get("BAL", {}).get("FPT") == "FULL"
              and "MBB" not in recs_by_book.get("BAL", {}),
              str(recs_by_book))

    # 14: bal_exit_hint
    check("bal_exit_hint: có tín hiệu hôm nay → nêu status",
          ps.bal_exit_hint("FPT", {"FPT": "FULL"}) == "tín hiệu hôm nay: FULL")
    check("bal_exit_hint: không có tín hiệu mới hôm nay (KHÔNG suy ra 'đã kết thúc')",
          ps.bal_exit_hint("MBB", {"FPT": "FULL"}) == "không có tín hiệu mới hôm nay")
    check("bal_exit_hint: file recs rỗng/thiếu → None (không báo gì)",
          ps.bal_exit_hint("FPT", {}) is None)

    # 15: risk_warning — PARK không có ngưỡng; dưới sàn hiển thị → None; qua RED ZONE → 🔴
    check("risk_warning: PARK luôn None (không có stop-loss cứng)",
          ps.risk_warning("PARK", -25.0) is None)
    check("risk_warning: BAL -14% (dưới sàn 15%) → None",
          ps.risk_warning("BAL", -14.0) is None)
    rw_bal = ps.risk_warning("BAL", -19.5)
    check("risk_warning: BAL -19.5% (dưới RED_ZONE 18? actually >=18) → 🔴, còn 0.5pp",
          rw_bal is not None and rw_bal[0] == "🔴" and "0.5pp" in rw_bal[1], str(rw_bal))
    rw_lag = ps.risk_warning("LAG", -15.0)
    check("risk_warning: LAG -15% == ngưỡng chính nó → còn 0.0pp",
          rw_lag is not None and "0.0pp" in rw_lag[1], str(rw_lag))

    # 16: park_next_rebal_estimate — quý VN kế tiếp (3/6/9/12), đầu tuần né T7/CN
    est = ps.park_next_rebal_estimate("2026-09-29")
    check("park_next_rebal_estimate(2026-09-29) → Q4, tháng 12",
          est is not None and est[1] == 4 and est[0].startswith("2026-12"), str(est))
    est_wrap = ps.park_next_rebal_estimate("2026-12-15")
    check("park_next_rebal_estimate(2026-12-15) → sang năm sau, Q1 tháng 3",
          est_wrap is not None and est_wrap[1] == 1 and est_wrap[0].startswith("2027-03"), str(est_wrap))

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
