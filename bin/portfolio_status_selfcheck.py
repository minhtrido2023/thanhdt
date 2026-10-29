#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho portfolio_status.py — chạy: python3 portfolio_status_selfcheck.py

Không mock DNSE/BQ — đọc trực tiếp file thật trên đĩa (dnse_raw, nav_history, journal),
giống production. Vì vậy assertion phải fail-soft khi input hôm nay không có (report ngày
lễ/cuối tuần) thay vì crash CI.
"""
import os
import re
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


def _no_lots(account, date):
    """Thay sổ lô LAG (park_holdings gọi broker LIVE khi date = hôm nay) cho các ca chỉ kiểm KHUNG
    của build_output — đường sổ lô thật kiểm ở 12/12b/12c + chạy tay portfolio_status."""
    return {}, {}, "selfcheck: bỏ qua sổ lô"


def _no_ledger(account, date):
    """Thay sổ lô (park_holdings gọi broker LIVE) — các ca KHUNG cũ chạy đường fallback nhãn FILL."""
    return None, set(), "selfcheck: bỏ qua sổ lô"


def _no_tool(account, date):
    """Thay công cụ §21 (BQ + ~2 phút) cho các ca chỉ kiểm KHUNG của build_output."""
    return {}


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
        out_sx = ps.build_output("SpaceX", date_spacex, returns_fn=_no_tool, lag_lots_fn=_no_lots)
        check(f"build_output SpaceX ({date_spacex}) không None", out_sx is not None)
        check("build_output SpaceX: có header TÌNH TRẠNG DANH MỤC",
              out_sx is not None and "TÌNH TRẠNG DANH MỤC" in out_sx)
        check("build_output SpaceX: có bảng Cơ cấu danh mục",
              out_sx is not None and "Cơ cấu danh mục" in out_sx)
    else:
        print("[SKIP] build_output SpaceX — không có nav_history_SpaceX.csv")

    if date_zalopay:
        out_zp = ps.build_output("ZaloPay", date_zalopay, returns_fn=_no_tool, lag_lots_fn=_no_lots)
        check(f"build_output ZaloPay ({date_zalopay}) không None", out_zp is not None)
    else:
        print("[SKIP] build_output ZaloPay — không có nav_history_ZaloPay.csv")

    # 7: §12 sanity — 2 account cho output khác nhau (không đọc chung không lọc)
    if date_spacex and date_zalopay:
        out_sx = ps.build_output("SpaceX", date_spacex, returns_fn=_no_tool, lag_lots_fn=_no_lots)
        out_zp = ps.build_output("ZaloPay", date_zalopay, returns_fn=_no_tool, lag_lots_fn=_no_lots)
        check("§12: SpaceX và ZaloPay cho output KHÁC nhau (không lẫn account)",
              out_sx != out_zp)

    # 8: ngày TRƯỚC mọi dòng nav_history (không có "gần nhất trước") → None, không crash.
    # Lưu ý: load_nav_row() CỐ Ý fallback về dòng gần nhất TRƯỚC ngày yêu cầu (xử lý report
    # chạy vào ngày chưa có NAV hôm đó) — nên test None phải dùng ngày TRƯỚC lịch sử, không
    # phải ngày tương lai (tương lai vẫn có "gần nhất trước" = dòng cuối cùng).
    check("build_output ngày TRƯỚC mọi lịch sử NAV → None",
          ps.build_output("SpaceX", "2000-01-01", returns_fn=_no_tool, lag_lots_fn=_no_lots) is None)

    # 10: count_trading_days — dùng next_trading_day thật (§16 RULE 2), không đếm lịch tay
    import datetime as _dt
    n = ps.count_trading_days(_dt.date(2026, 8, 10), _dt.date(2026, 9, 29))
    check("count_trading_days(2026-08-10 → 2026-09-29) == 33 (bao gồm bù lễ Quốc khánh)",
          n == 33, str(n))
    check("count_trading_days: asof <= start → 0",
          ps.count_trading_days(_dt.date(2026, 9, 29), _dt.date(2026, 9, 29)) == 0)

    # 11: _first_fill_dates (nay chỉ còn disc_entry_dates dùng) — quét journal, lấy FILL mua ĐẦU
    # TIÊN của book, bỏ qua sell + book khác. LAG KHÔNG còn đi đường này (xem 12: sổ lô từng lô).
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
            entries = ps._first_fill_dates("TESTACC", "LAG")
        finally:
            ps.EXEC_DIR = old_exec_dir
        check("_first_fill_dates: XYZ entry = FILL mua LAG SỚM NHẤT across nhiều file (01-05, không phải 01-10)",
              entries.get("XYZ") == "2026-01-05", str(entries))
        check("_first_fill_dates: bỏ qua book khác (ABC/BAL không xuất hiện)",
              "ABC" not in entries, str(entries))

    # 12: lag_exit_hint — đọc SỔ LÔ từng lô (`book_lot_snapshot` lots), không phải FILL đầu tiên
    def _lots(*pairs):
        return {"qty": sum(q for q, _ in pairs), "entry_date": min(d for _, d in pairs),
                "lots": [{"qty": q, "entry_date": d} for q, d in pairs]}
    h_in_window = ps.lag_exit_hint("SCL", {"SCL": _lots((100, "2026-09-08"))}, "2026-09-29")  # 15 phiên
    # Mốc CỐ ĐỊNH T+25 (khớp backtest pin `hold_days=25`, user xác nhận 2026-10-06) — kỳ vọng
    # cũ "T+14/T+20, 'còn ~'" là khoảng đã bỏ từ 2026-09-30, không có nguồn backtest.
    check("lag_exit_hint: 15 phiên → còn 10 phiên tới hạn cố định T+25",
          h_in_window is not None and "còn 10 phiên tới hạn cố định T+25" in h_in_window,
          str(h_in_window))
    h_past = ps.lag_exit_hint("SCL", {"SCL": _lots((100, "2026-08-10"))}, "2026-09-29")
    check("lag_exit_hint: đã qua T+25 → 'ĐÃ QUA hạn cố định T+25'",
          h_past is not None and "ĐÃ QUA hạn cố định T+25" in h_past, str(h_past))
    check("lag_exit_hint: không có entry date → None",
          ps.lag_exit_hint("ZZZ", {}, "2026-09-29") is None)
    # 12b (job Taylor_20261028_162413) — ca THẬT ZaloPay 28/10: VPB lô 282cp @07-27 + 900cp @10-26/27
    # (sổ lô park_holdings đo 28/10), SCL thoát hẳn 30/09-02/10 rồi vào lại 10-26 (+10-28).
    vpb = _lots((282, "2026-07-27"), (100, "2026-10-26"), (200, "2026-10-26"), (200, "2026-10-26"),
                (200, "2026-10-26"), (100, "2026-10-27"), (100, "2026-10-27"))
    h_vpb = ps.lag_exit_hint("VPB", {"VPB": vpb}, "2026-10-28")
    n_vpb = ps.count_trading_days(_dt.date(2026, 7, 27), _dt.date(2026, 10, 28))
    check("lag_exit_hint VPB: nhóm lô — 282cp ĐÃ QUA T+25 (từ 07-27) + 900cp chưa tới hạn (10-26, 10-27)",
          h_vpb == (f"282cp ĐÃ QUA hạn cố định T+25 ({n_vpb} phiên từ 2026-07-27) — tới hạn thoát; "
                    f"900cp vào 2026-10-26, 2026-10-27, lô sớm nhất còn 23 phiên tới hạn cố định T+25"),
          str(h_vpb))
    scl = _lots((100, "2026-10-26"), (100, "2026-10-26"), (100, "2026-10-26"), (200, "2026-10-26"),
                (100, "2026-10-28"), (100, "2026-10-28"))
    h_scl = ps.lag_exit_hint("SCL", {"SCL": scl}, "2026-10-28")
    check("lag_exit_hint SCL vào lại 10-26 sau khi thoát hẳn: KHÔNG báo 'từ 2026-08-10', không 'ĐÃ QUA'",
          h_scl is not None and "2026-10-26" in h_scl and "2026-08-10" not in h_scl and "ĐÃ QUA" not in h_scl,
          str(h_scl))
    check("lag_exit_hint lỗi entry_date lô ⇒ cảnh báo ⚠️, không đoán phiên",
          (ps.lag_exit_hint("BAD", {"BAD": {"qty": 1, "entry_date": "x", "lots": [{"qty": 1, "entry_date": "x"}]}},
                            "2026-10-28") or "").startswith("⚠️ ngày vào lô lỗi"))
    # 12c book_lot_snapshot THẬT (park_holdings sandbox broker=) — API ADDITIVE: `lots` từng lô +
    # `qty`/`entry_date` gộp y cũ.
    import park_holdings as _ph
    _orig_snap = _ph.park_holdings
    def _fake_ph(account, asof=None, need_price=False, **kw):
        lot = lambda q, d, **x: dict({"ticker": "VPB", "book": "LAG", "qty": q, "entry_date": d}, **x)
        return {"lots": [lot(282, "2026-07-27"), lot(1100, "2025-11-20", book="PARK"), lot(900, "2026-10-26")],
                "reconcile": {"mismatches": []}, "unverified_tickers": [], "warnings": []}
    _ph.park_holdings = _fake_ph
    try:
        snap, ok_s, _r, _b = ps.book_lot_snapshot("TESTACC", "LAG", asof="2026-10-28")
    finally:
        _ph.park_holdings = _orig_snap
    check("book_lot_snapshot: qty/entry_date gộp GIỮ NGUYÊN + thêm `lots` từng lô (PARK không lẫn)",
          ok_s and snap.get("VPB") == {"qty": 1182, "entry_date": "2026-07-27",
                                       "lots": [{"qty": 282, "entry_date": "2026-07-27"},
                                                {"qty": 900, "entry_date": "2026-10-26"}]}, str(snap))

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
    # LAG MIỄN stop-loss theo drawdown (backtest pin `stop_loss=-0.99`, user xác nhận
    # 2026-10-06) — exit chỉ theo mốc T+25 ⇒ không bao giờ cảnh báo gần ngưỡng, kể cả lỗ sâu.
    for _pp in (-15.0, -19.5, -50.0):
        check(f"risk_warning: LAG {_pp}% → None (LAG không có ngưỡng stop-loss)",
              ps.risk_warning("LAG", _pp) is None, str(ps.risk_warning("LAG", _pp)))

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

    # 17: NAV STALE — user 2026-09-30 phát hiện thật: `date` yêu cầu chưa có dòng nav_history
    # (đúng tình huống eod_trading_report.sh gọi portfolio_status.py TRƯỚC daily_nav_snapshot.py
    # cùng lượt chạy) ⇒ PHẢI cảnh báo tường minh, KHÔNG được dán nhãn "Hôm nay" cho NAV/% đổi của
    # ngày khác. Dùng ngày tương lai xa (chưa có + không thể có) để chắc chắn tái lập fallback.
    if date_zalopay:
        _future = "2099-12-31"
        out_stale = ps.build_output("ZaloPay", _future, returns_fn=_no_tool, lag_lots_fn=_no_lots)
        check("NAV stale: build_output không None (vẫn fallback dòng gần nhất, không crash)",
              out_stale is not None)
        if out_stale is not None:
            check("NAV stale: có cảnh báo ⚠️ NAV hôm nay CHƯA có + nêu đúng ngày yêu cầu",
                  f"⚠️ NAV hôm nay ({_future}) CHƯA có" in out_stale, out_stale.splitlines()[2:4])
            check("NAV stale: KHÔNG còn dán nhãn 'Hôm nay:' cho số của ngày khác (dòng cũ đã bị thay)",
                  "| Hôm nay: **" not in out_stale)
            check("NAV stale: có nêu ngày THẬT của số đang hiện (today_row['date'])",
                  f"({date_zalopay})" in out_stale, date_zalopay)
    else:
        check("NAV stale: bỏ qua (không có nav_history_ZaloPay.csv nào để test fallback)", True)

    # 17b (N11, 2026-10-11): "Hôm nay" và "Từ khi bắt đầu hoạt động" là tỉ suất GIÁ ĐƠN VỊ (đã
    # khử nạp/rút), lấy từ nav_period_returns — không phải tỉ số NAV thô. 1.000 → nạp 200 lúc
    # 10:00 → +2% ⇒ NAV 1.224: phải in +2.00%, không phải +22.40%.
    with tempfile.TemporaryDirectory() as td:
        hdr = "date,nav,mtm_stock,cash,margin_debt,offbook_assets,egg_assets,balance_ts,cum_dividend_excl,nav_is_estimate,nav_source"
        with open(os.path.join(td, "nav_history_SpaceX.csv"), "w", encoding="utf-8") as f:
            f.write(hdr + "\n2026-07-02,1000000000,0,0,0,0,0,2026-07-02T19:10:00,0,False,live\n"
                    "2026-07-03,1224000000,0,0,0,0,0,2026-07-03T19:10:00,0,False,live\n")
        flows = os.path.join(td, "flows.json")
        old_exec_dir, old_env = ps.EXEC_DIR, os.environ.get("ACCOUNT_CASH_FLOWS_PATH")
        ps.EXEC_DIR = td
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows
        try:
            import contextlib as _ctx
            import io as _io

            def header(records, date="2026-07-03"):
                with open(flows, "w", encoding="utf-8") as fh:
                    _json.dump({"SpaceX": records}, fh)
                err = _io.StringIO()
                with _ctx.redirect_stderr(err):
                    out = ps.build_output("SpaceX", date, returns_fn=_no_tool, lag_lots_fn=_no_lots)
                line = next((ln for ln in (out or "").splitlines() if ln.startswith("NAV: **")), "")
                return line, err.getvalue()

            dep = {"date": "2026-07-03", "time_ict": "10:00", "amount_vnd": 200_000_000,
                   "kind": "deposit", "evidence": "sao kê"}
            line, err = header([dep])
            check("N11: ngày có nạp 200tr — 'Hôm nay' = +2.00% (giá đơn vị), không phải +22.40% (NAV thô)",
                  "| Hôm nay: **+2.00%** |" in line and "22.40" not in line, line)
            check("N11: 'Từ khi bắt đầu hoạt động' cùng nguồn = +2.00%",
                  line.endswith("Từ khi bắt đầu hoạt động: **+2.00%**"), line)
            line, err = header([])
            check("N11: không có dòng tiền — hai số = tỉ số NAV (+22.40%)",
                  "| Hôm nay: **+22.40%** |" in line and line.endswith("**+22.40%**"), line)
            line, err = header([dict(dep, date="2026-07-04")])
            check("N11: dòng tiền treo ⇒ báo ra stderr (không vô hình)",
                  "chưa nằm trong tỉ suất nào" in err and "2026-07-04" in err, err)
            bad = dict(dep)
            del bad["time_ict"]
            line, err = header([bad])
            check("N11: nguồn tỉ suất lỗi ⇒ in '?' cho CẢ HAI phần trăm, không lùi về tỉ số NAV thô",
                  "| Hôm nay: **?** |" in line and line.endswith("**?**") and "%" not in line, line)
            check("N11: nguồn tỉ suất lỗi ⇒ nói lý do thật ra stderr (không còn `except: pass`)",
                  "KHÔNG tính được tỉ suất NAV" in err and "thiếu time_ict" in err, err)
            # Nhiều phiên, vắt qua tuần + tháng ⇒ bốn kỳ ra bốn số khác nhau: "Hôm nay" phải là kỳ
            # NGÀY (không phải WTD), "Từ khi bắt đầu" phải là kỳ từ mốc khởi điểm (không phải MTD).
            #   07-02 1.010 · 07-31 (thứ Sáu) 1.020 · 08-03 (thứ Hai) 1.030 · 08-04 1.050 (tr)
            #   ngày 1.050/1.030 = +1,94% · WTD = MTD 1.050/1.020 = +2,94% · từ mốc 1 tỷ = +5,00%
            with open(os.path.join(td, "nav_history_SpaceX.csv"), "w", encoding="utf-8") as f:
                f.write(hdr + "".join(f"\n{d},{v},0,0,0,0,0,{d}T19:10:00,0,False,live" for d, v in (
                    ("2026-07-02", 1010000000), ("2026-07-31", 1020000000), ("2026-08-03", 1030000000),
                    ("2026-08-04", 1050000000))) + "\n")
            line, err = header([], date="2026-08-04")
            check("N11: nhiều phiên — 'Hôm nay' = kỳ NGÀY +1.94% (không phải WTD/MTD +2.94%)",
                  "| Hôm nay: **+1.94%** |" in line, line)
            check("N11: nhiều phiên — 'Từ khi bắt đầu hoạt động' = từ mốc khởi điểm +5.00% (không phải MTD +2.94%)",
                  line.endswith("Từ khi bắt đầu hoạt động: **+5.00%**"), line)
        finally:
            ps.EXEC_DIR = old_exec_dir
            if old_env is None:
                os.environ.pop("ACCOUNT_CASH_FLOWS_PATH", None)
            else:
                os.environ["ACCOUNT_CASH_FLOWS_PATH"] = old_env

    # 18: value_per_share dạng CHUỖI từ producer (ca thật TV1 DIV '1500.0', ex 07/10) — trước đây
    # f"{vps:,.0f}" ném ValueError, mất cả khối danh mục trong báo cáo ngày 05-06/10.
    check("cash_div_impact: chuỗi '1500.0' → 1,500đ/cp",
          ps._cash_div_impact("1500.0") == "1,500đ/cp cổ tức tiền mặt", ps._cash_div_impact("1500.0"))
    check("cash_div_impact: float 3000.0 → 3,000đ/cp",
          ps._cash_div_impact(3000.0) == "3,000đ/cp cổ tức tiền mặt")
    for _bad in (None, "", "abc"):
        check(f"cash_div_impact: {_bad!r} → chưa rõ mức (không crash)",
              ps._cash_div_impact(_bad) == "cổ tức tiền mặt (chưa rõ mức)")

    # 19+: K1 (2026-10-10) — tỉ suất từng mã lấy từ CÔNG CỤ §21, không tự tính trên costPrice.
    # Vòng 2 (arch-review 53b48b76): F2 cờ gần ngưỡng của sleeve có lệnh cắt lỗ tự động đo trên cơ
    # sở sổ broker · F3 chú thích hai giá · F5 fixture `cost_price ≠ raw_cost`, đủ mọi `code`.
    import contextlib
    import datetime as _dt2
    import io
    import tempfile
    import report_return_gate as rrg
    keep = {k: getattr(ps, k) for k in ("broker_positions_with_cost", "load_nav_row",
                                        "sleeve_map_from_journal", "current_park_basket",
                                        "section21_returns")}
    keep_rrg = rrg.position_returns
    pos = {"QQ0": {"qty": 100.0, "marketPrice": None, "avg_cost": 10000.0, "sellable": 100},
           "QQ1": {"qty": 1000.0, "marketPrice": 12000.0, "avg_cost": 10000.0, "sellable": 1000},
           "QQ2": {"qty": 500.0, "marketPrice": 10000.0, "avg_cost": 8000.0, "sellable": 500},
           "QQ3": {"qty": 100.0, "marketPrice": 30000.0, "avg_cost": 25000.0, "sellable": 100},
           "QQ4": {"qty": 200.0, "marketPrice": 8000.0, "avg_cost": 10000.0, "sellable": 200},
           "QQ5": {"qty": 100.0, "marketPrice": 9000.0, "avg_cost": 10000.0, "sellable": 100},
           "QQ6": {"qty": 200.0, "marketPrice": 8300.0, "avg_cost": 10000.0, "sellable": 200},
           "QQ7": {"qty": 100.0, "marketPrice": 8100.0, "avg_cost": 10000.0, "sellable": 100},
           "QQ8": {"qty": 100.0, "marketPrice": 20000.0, "avg_cost": None, "sellable": 100},
           "QQ9": {"qty": 100.0, "marketPrice": 5000.0, "avg_cost": None, "sellable": 100}}
    journal = {"QQ5": "CAPIT", "QQ6": "DISCRETIONARY_SPECIAL", "QQ8": "LAG"}     # còn lại: BAL / PARK

    def row(qty, raw, pct, **kw):
        # `cost_price` (giá vốn broker, ĐÃ trừ cổ tức) KHÁC `raw_cost` (giá vốn thô): mẫu số tổng
        # sleeve dùng nhầm `cost_price` phải ra số khác (đúng lớp lỗi K1 ở cột "Lãi/Lỗ CK").
        return {"qty": qty, "cost_price": raw - 1000.0, "market": 0.0, "excluded": False, "why": [],
                "code": "", "pct": pct, "pl": qty * raw * pct / 100.0, "raw_cost": raw,
                "gross": 0.0, **kw}

    def no(code, why, **kw):
        return {"qty": 1.0, "cost_price": 1.0, "market": 1.0, "excluded": False, "why": [why],
                "code": code, **kw}
    tool = {"QQ0": row(100.0, 10500.0, 1.0),
            "QQ1": row(1000.0, 11000.0, 12.34),
            # `why` thắng kể cả khi dòng có lọt một `pct`: có lý do thì KHÔNG in số
            "QQ2": no("blocked", "sự kiện ex 2026-09-22 [UNVERIFIED] CHƯA giải", pct=25.0, pl=1e6,
                      raw_cost=8000.0),
            "QQ4": row(200.0, 10300.0, -19.2),          # QQ3: công cụ không trả dòng nào
            "QQ5": no("ma_ly_do_moi", "một lý do công cụ chưa từng có"),
            "QQ6": row(200.0, 10000.0, -18.5),
            "QQ7": no("no_price", "giá đóng cửa phiên 2026-10-09 CHƯA có trên BQ"),
            "QQ8": no("no_cost", "sổ broker không có giá vốn (costPrice ≤ 0) cho vị thế này"),
            "QQ9": row(100.0, 5100.0, 2.0)}

    def safe(fn, *a):
        """Kết quả của `fn(*a)`; SẬP ⇒ NaN (so sánh nào cũng sai ⇒ ca ĐỎ, không cắt ngang)."""
        try:
            return fn(*a)
        except Exception:                                       # noqa: BLE001
            return float("nan")

    def build(returns_fn=None, **kw):
        """`build_output` trên fixture; SẬP = chuỗi "EXC:…" (một ca ĐỎ có tên, không cắt ngang)."""
        err = io.StringIO()
        kw.setdefault("lag_lots_fn", _no_lots)
        kw.setdefault("ledger_split_fn", _no_ledger)
        try:
            with contextlib.redirect_stderr(err):
                out_ = ps.build_output("ZaloPay", "2026-10-09", **(
                    {"returns_fn": returns_fn} if returns_fn else {}), **kw) or ""
        except Exception as exc:                                # noqa: BLE001
            out_ = f"EXC:{type(exc).__name__}: {exc}"
        return out_, err.getvalue()
    try:
        ps.broker_positions_with_cost = lambda no_, d: {k: dict(v) for k, v in pos.items()}
        ps.load_nav_row = lambda a, d: ({"date": _dt2.date.fromisoformat(d), "nav": 1e9,
                                         "cash": 1e8, "egg_assets": 0.0}, None)
        ps.sleeve_map_from_journal = lambda a: dict(journal)
        ps.current_park_basket = lambda: ({"QQ0"}, None)
        out, err = build(lambda a, d: tool)
        check("K1: mã CÓ tỉ suất công cụ ⇒ in đúng số đó, 2 chữ số, dạng 'MÃ <giá trị>M, ±x.xx%'",
              "QQ1 12.0M, +12.34%" in out and "QQ4 1.6M, -19.20%" in out
              and "QQ6 1.7M, -18.50%" in out, out)
        check("K1: KHÔNG còn số tự tính trên costPrice (QQ1 +20.0%, QQ2 +25.0%, QQ3 +20.0%)",
              "+20.0" not in out and "+25.0" not in out, out)
        check("K1: mã công cụ KHÔNG cấp tỉ suất ⇒ không in tỉ suất (kể cả khi dòng lọt một `pct` cạnh "
              "`why`), in lý do ngắn ĐÚNG theo từng `code`; `code` lạ ⇒ câu 'blocked'",
              all(x in out for x in (
                  "QQ2 5.0M (chưa có tỉ suất)", "QQ3 3.0M (chưa có tỉ suất)",
                  f"ⓘ Chưa có tỉ suất (QQ2): {ps.RETURN_UNAVAILABLE['blocked']}",
                  f"ⓘ Chưa có tỉ suất (QQ3): {ps.RETURN_UNAVAILABLE['absent']}",
                  f"ⓘ Chưa có tỉ suất (QQ7): {ps.RETURN_UNAVAILABLE['no_price']}",
                  f"ⓘ Chưa có tỉ suất (QQ8): {ps.RETURN_UNAVAILABLE['no_cost']}",
                  f"ⓘ Chưa có tỉ suất (QQ5): {ps.RETURN_UNAVAILABLE['blocked']}"))
              and len(set(ps.RETURN_UNAVAILABLE.values())) == 5, out)
        check("K1: lý do THẬT của từng mã không có tỉ suất đi ra stderr (⇒ log cron), không vào báo cáo",
              "portfolio_status: QQ2 (ZaloPay 2026-10-09) không có tỉ suất §21: sự kiện ex 2026-09-22 "
              "[UNVERIFIED] CHƯA giải" in err
              and "portfolio_status: QQ7 (ZaloPay 2026-10-09) không có tỉ suất §21: giá đóng cửa phiên "
                  "2026-10-09 CHƯA có trên BQ" in err
              and "UNVERIFIED" not in out and "CHƯA có trên BQ" not in out, err)
        check("K1: tổng sleeve thiếu một mã ⇒ '—' (không cộng phần còn lại rồi gọi là cả sleeve)",
              "| BAL (6 mã) | 22.9M | 2.3% | — |" in out, out)

        # ---- F2: khoảng cách tới ngưỡng cắt lỗ TỰ ĐỘNG đo trên cơ sở của chính lệnh đó
        check("F2: BAL đo trên cơ sở sổ broker (QQ4: 8.000/10.000 − 1 = −20,0% ⇒ còn 0,0pp, lệnh bán "
              "đã tự chèn) — KHÔNG trên tỉ suất §21 −19,20% (bản 53b48b76 in 'còn 0.8pp')",
              "QQ4 1.6M, -19.20% — " in out
              and "🔴 còn 0.0pp đến ngưỡng cắt lỗ tự động (lỗ 20% trên giá vốn sổ công ty chứng khoán; "
                  "hiện lỗ 20.0%)" in out and "còn 0.8pp" not in out, out)
        check("F2: cờ đó CÒN khi công cụ §21 không cấp tỉ suất (QQ7 no_price, sổ broker −19,0% ⇒ còn "
              "1,0pp) — bản 53b48b76: cờ biến mất hẳn",
              "QQ7 0.8M (chưa có tỉ suất) — " in out
              and "🔴 QQ7 (BAL): lỗ 19.0% trên giá vốn sổ công ty chứng khoán, còn 1.0pp đến ngưỡng cắt "
                  "lỗ tự động — cân nhắc xử lý sớm" in out
              and "🔴 QQ4 (BAL): lỗ 20.0% trên giá vốn sổ công ty chứng khoán, còn 0.0pp đến ngưỡng cắt "
                  "lỗ tự động — cân nhắc xử lý sớm" in out, out)
        check("F2: sleeve KHÔNG có lệnh tự động (Discretionary) vẫn đo trên tỉ suất công bố, dòng cờ "
              "giữ dạng 'MÃ ±x.xx%' cổng kiểm được (QQ6 −18,50% ⇒ còn 1,5pp; sổ broker của nó −17,0% "
              "⇒ nếu đo nhầm cơ sở sẽ ra 3,0pp và không vào vùng đỏ)",
              "🔴 QQ6 -18.50% (Discretionary): còn 1.5pp → ngưỡng" in out
              and "🔴 còn 1.5pp đến ngưỡng xử lý (−20%)" in out, out)
        flag_lines = [ln for ln in out.splitlines() if "KHÔNG đánh giá được khoảng cách" in ln]
        check("F2: 'không đánh giá được' nói đúng TỪNG lý do: sleeve không lệnh tự động thiếu tỉ suất "
              "(QQ5 CAPIT) — không kể BAL (đã đo trên sổ broker) hay LAG (không ngưỡng); BAL thiếu giá "
              "vốn trên sổ broker (QQ9)",
              flag_lines == [
                  "- ⚠️ Chưa có tỉ suất nên KHÔNG đánh giá được khoảng cách tới ngưỡng xử lý: QQ5.",
                  "- ⚠️ Sổ công ty chứng khoán thiếu giá vốn hoặc giá nên KHÔNG đánh giá được khoảng "
                  "cách tới ngưỡng cắt lỗ tự động: QQ9."], str(flag_lines))
        os.environ.setdefault("AUTO_EXIT_TEST_MODE", "1")
        import auto_exit_inject as aei
        aei_pos = {"QQ4": dict(pos["QQ4"], marketPrice=7900.0), "QQ7": dict(pos["QQ7"]),
                   "QQ9": dict(pos["QQ9"])}
        lots = {tk: {"qty": int(p["qty"]), "entry_date": "2026-06-01",
                     "lots": [{"qty": int(p["qty"]), "entry_date": "2026-06-01"}]} for tk, p in aei_pos.items()}
        with contextlib.redirect_stdout(io.StringIO()):
            hit, _blocked = aei._bal_stop_loss_candidates(_dt2.date(2026, 10, 9), aei_pos, lots)
        check("F2: `broker_basis_pct` = ĐÚNG phép tính của lệnh cắt lỗ tự động "
              "(`auto_exit_inject._bal_stop_loss_candidates`): cùng số trên mã lệnh đó chèn (−21,0%), "
              "mã chưa tới ngưỡng không bị chèn, thiếu giá vốn ⇒ lệnh bỏ qua và ở đây None",
              [tk for tk, *_ in hit] == ["QQ4"]
              and abs(hit[0][3] * 100.0 - safe(ps.broker_basis_pct, aei_pos["QQ4"])) < 1e-9
              and round(safe(ps.broker_basis_pct, aei_pos["QQ7"]), 6) == -19.0
              and [safe(ps.broker_basis_pct, x) for x in (
                  aei_pos["QQ9"], {"avg_cost": 0.0, "marketPrice": 5.0},
                  {"avg_cost": 5.0, "marketPrice": None}, {"avg_cost": 5.0, "marketPrice": 0},
                  {"avg_cost": -5.0, "marketPrice": 5.0}, {"avg_cost": 5.0, "marketPrice": -5.0})]
              == [None] * 6, str(hit))

        # ---- F3: một dòng chú thích hai giá
        check("F3: khối danh mục có ĐÚNG MỘT dòng chú thích 'tỉ suất theo giá đóng cửa — giá trị theo "
              "giá công ty chứng khoán', đứng trước mục chi tiết đầu tiên; không tên hệ thống nội bộ",
              out.count(ps.PRICE_BASIS_NOTE) == 1
              and out.index(ps.PRICE_BASIS_NOTE) < out.index("**Chi tiết ")
              and "giá đóng cửa" in ps.PRICE_BASIS_NOTE and "công ty chứng khoán" in ps.PRICE_BASIS_NOTE
              and not any(x in ps.PRICE_BASIS_NOTE for x in ("BQ", "DNSE", "marketPrice", "§21")), out)

        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write(out)
            tmp = fh.name
        try:
            bits = [(tk, pct) for tk, pct, _ln in rrg.parse_position_bits(tmp)]
            prose = [(tk, pct) for tk, pct, _ln in rrg.parse_prose_pcts(tmp)]
            mention = rrg.ticker_mentions(tmp, {"QQ2", "QQ3", "QQ5", "QQ7", "QQ8"})
            gaps = rrg.position_line_gaps(tmp)
        finally:
            os.unlink(tmp)
        check("HỢP ĐỒNG với cổng: `parse_position_bits` đọc lại ĐÚNG và ĐỦ các dòng có tỉ suất, kể cả "
              "dòng giá trị '?' (đổi định dạng dòng mà cổng không đọc được = PASS trên 0 dòng, lỗi K1)",
              sorted(bits) == [("QQ0", 1.0), ("QQ1", 12.34), ("QQ4", -19.2), ("QQ6", -18.5),
                               ("QQ9", 2.0)] and "QQ0 ?, +1.00%" in out, str(bits))
        check("HỢP ĐỒNG với cổng: mỗi mục 'Chi tiết … (n mã)' có đủ n vị thế cổng đọc được hoặc ghi "
              "'(chưa có tỉ suất)' (dây bẫy `position_line_gaps` không nổ trên báo cáo đúng dạng)",
              gaps == [] and ps.RETURN_UNAVAILABLE and rrg.NO_RETURN_MARK in out, str(gaps))
        check("HỢP ĐỒNG với cổng: văn xuôi chỉ có MỘT tỉ suất 'MÃ ±x%' — dòng cờ Discretionary (số §21). "
              "Cờ của BAL (số đo trên sổ broker) và dòng chú thích KHÔNG bị đọc thành tỉ suất của mã",
              prose == [("QQ6", -18.5)], str(prose))
        check("HỢP ĐỒNG với cổng: mã không có tỉ suất KHÔNG bị cổng thấy 'có tỉ suất đứng cạnh' — kể cả "
              "QQ7 đang mang cờ gần ngưỡng (nếu thấy, cổng sẽ chặn oan báo cáo đã cố ý không in số)",
              all(mention[tk]["pub"] == [] for tk in mention), str(mention))

        full = dict(tool, QQ2=row(500.0, 8000.0, 25.0), QQ3=row(100.0, 25000.0, 20.0),
                    QQ5=row(100.0, 10000.0, -10.0), QQ7=row(100.0, 10000.0, -19.0),
                    QQ8=row(100.0, 19000.0, 5.0))
        out2, _ = build(lambda a, d: full)
        bal = [full[tk] for tk in ("QQ1", "QQ2", "QQ3", "QQ4", "QQ7", "QQ9")]
        pl = sum(r["pl"] for r in bal)
        cost = sum(r["qty"] * r["raw_cost"] for r in bal)
        cost_broker = sum(r["qty"] * r["cost_price"] for r in bal)
        check("K1: đủ mọi mã ⇒ tổng sleeve = Σ lãi/lỗ ròng ÷ Σ giá vốn THÔ của chính các số công cụ — "
              "KHÔNG phải ÷ Σ giá vốn broker (fixture: hai mẫu số ra hai số khác nhau)",
              f"| BAL (6 mã) | 22.9M | 2.3% | {pl / cost * 100:+.1f}% |" in out2
              and f"{pl / cost * 100:+.1f}" != f"{pl / cost_broker * 100:+.1f}"
              and "Chưa có tỉ suất" not in out2, out2)

        def boom(a, d):
            raise ValueError("không lấy được giá thô 2026-10-09 từ BQ: quota — CHẶN")
        out3, err3 = build(boom)
        check("K1: công cụ LỖI ⇒ vẫn ra khối danh mục, KHÔNG mã nào có tỉ suất, lý do nói đúng là "
              "công cụ không chạy được (không rơi về costPrice); lỗi THẬT ra stderr; cờ gần ngưỡng "
              "cắt lỗ tự động (đo trên sổ broker) VẪN còn",
              "TÌNH TRẠNG DANH MỤC" in out3 and rrg.POSBIT_RE.findall(out3) == []
              and f"(QQ1, QQ2, QQ3, QQ4, QQ7, QQ9): {ps.RETURN_UNAVAILABLE['error']}" in out3
              and "🔴 QQ4 (BAL): lỗ 20.0%" in out3 and "quota" not in out3
              and "portfolio_status: công cụ tỉ suất §21 lỗi (ZaloPay 2026-10-09) — không in tỉ suất mã "
                  "nào: ValueError: không lấy được giá thô 2026-10-09 từ BQ: quota — CHẶN" in err3,
              out3 + err3)

        # ---- G3-hygiene (2026-10-29): sleeve theo SỔ LÔ, không bầu chọn nhãn FILL; mã lẫn sổ tách đúng
        import report_return_gate as _rrg
        pos_g = {"MX1": {"qty": 1786.0, "marketPrice": 20000.0, "avg_cost": 19000.0, "sellable": 1786},  # lẫn LAG+PARK
                 "ON1": {"qty": 500.0, "marketPrice": 10000.0, "avg_cost": 9000.0, "sellable": 500},     # 1 sổ (LAG)
                 "TR1": {"qty": 400.0, "marketPrice": 10000.0, "avg_cost": 9000.0, "sellable": 400},     # lô BOOK_TRANSFER → LAG
                 "UV1": {"qty": 300.0, "marketPrice": 10000.0, "avg_cost": 9000.0, "sellable": 300},     # unverified
                 "MM1": {"qty": 300.0, "marketPrice": 10000.0, "avg_cost": 9000.0, "sellable": 300},     # lệch broker
                 "TE1": {"qty": 100.0, "marketPrice": 10000.0, "avg_cost": 9000.0, "sellable": 100}}     # book kỹ thuật
        ps.broker_positions_with_cost = lambda no_, d: {k: dict(v) for k, v in pos_g.items()}
        # nhãn FILL "phổ biến nhất" của MX1/TR1/UV1/MM1 đều là PARK ⇒ cách cũ xếp trọn mã vào PARK
        ps.sleeve_map_from_journal = lambda a: {k: "PARK" for k in pos_g}
        ps.current_park_basket = lambda: (set(pos_g), None)
        tool_g = {k: row(v["qty"], 10000.0, 5.0) for k, v in pos_g.items()}
        tool_g["MX1"] = row(1786.0, 10000.0, 10.0)   # khác 5% của mã khác ⇒ đếm 2 lần/sai phần sẽ lộ ở tổng sleeve

        def ledger_ok(a, d):
            return ({"MX1": {"LAG": 1500, "PARK": 286}, "ON1": {"LAG": 500},
                     "TR1": {"LAG": 400},                       # BOOK_TRANSFER đã ghi ⇒ lô mang nhãn đích
                     "UV1": {"LAG": 300}, "MM1": {"LAG": 250},   # UV1 unverified; MM1 sổ 250 ≠ broker 300
                     "TE1": {"CORP_ACTION": 100}},
                    {"UV1"}, None)
        out_g, err_g = build(lambda a, d: tool_g, ledger_split_fn=ledger_ok)
        check("G3 sleeve: mã lẫn sổ ⇒ MỖI sổ đúng phần (MX1: LAG 1.500cp + PARK 286cp), không bầu chọn",
              "MX1 30.0M, +10.00% — phần 1,500cp trong sổ này" in out_g
              and "MX1 5.7M, +10.00% — phần 286cp trong sổ này" in out_g, out_g)
        check("G3 sleeve: mã 1 sổ + lô BOOK_TRANSFER ⇒ theo nhãn sổ lô (LAG), dù FILL toàn PARK",
              "ON1 5.0M, +5.00%" in out_g.split("**Chi tiết LAG")[1].split("**Chi tiết")[0]
              and "TR1 4.0M, +5.00%" in out_g.split("**Chi tiết LAG")[1].split("**Chi tiết")[0], out_g)
        check("G3 sleeve: unverified / lệch broker ⇒ fallback cách cũ (PARK) + lý do thật ở stderr, "
              "KHÔNG nói trong báo cáo (nội dung công bố)",
              "UV1 3.0M" in out_g.split("**Chi tiết PARK")[1].split("**Chi tiết")[0]
              and "MM1 3.0M" in out_g.split("**Chi tiết PARK")[1].split("**Chi tiết")[0]
              and "UV1 (ZaloPay 2026-10-09) phân loại sleeve theo nhãn FILL (cách cũ): sổ lô đánh dấu unverified" in err_g
              and "MM1 (ZaloPay 2026-10-09) phân loại sleeve theo nhãn FILL (cách cũ): sổ lô 250cp ≠ broker 300cp" in err_g
              and "unverified" not in out_g, err_g)
        check("G3 sleeve: book kỹ thuật (CORP_ACTION) ⇒ giữ cách phân loại cũ (PARK), không crash",
              "TE1 1.0M" in out_g.split("**Chi tiết PARK")[1].split("**Chi tiết")[0], out_g)
        tot_g = sum(v["qty"] * v["marketPrice"] for v in pos_g.values()) / 1e6
        got_g = sum(float(m.group(1)) for m in re.finditer(r"^\| (?:PARK|LAG|BAL)[^|]*\| ([\d.,]+)M \|", out_g, re.M))
        check("G3 sleeve: TỔNG giá trị các sleeve = tổng vị thế broker (chỉ đổi cách xếp, không đổi tiền)",
              abs(got_g - tot_g) < 0.15, f"{got_g} vs {tot_g}")
        lag_row = next((ln for ln in out_g.splitlines() if ln.startswith("| LAG (")), "")
        check("G3 sleeve: dòng LAG = 3 mã (MX1 chỉ phần 1.500cp, ON1, TR1) 39,0M, lãi/lỗ +8,1% (= (1,5M+0,25M+0,2M)/24M) — mã lẫn sổ "
              "không bị đếm 2 lần ở giá trị lẫn lãi/lỗ",
              lag_row.startswith("| LAG (3 mã) | 39.0M | ") and "| +8.1% |" in lag_row, lag_row)
        bits_g = [(m[0], float(m[1])) for m in _rrg.POSBIT_RE.findall(out_g)]
        tmp_g = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        tmp_g.write(out_g); tmp_g.close()
        try:
            gaps_g = _rrg.position_line_gaps(tmp_g.name)
        finally:
            os.unlink(tmp_g.name)
        check("G3 sleeve: HỢP ĐỒNG cổng tỉ suất — dòng vị thế mã lẫn sổ vẫn đọc được, mỗi mục đủ n vị thế",
              gaps_g == [] and sum(1 for t, _ in bits_g if t == "MX1") == 2, str(gaps_g))
        out_n, err_n = build(lambda a, d: tool_g)       # sổ lô không dựng được (stub mặc định)
        check("G3 sleeve: sổ lô LỖI ⇒ fallback cách cũ (cả 6 mã PARK) + cảnh báo stderr nêu lý do thật + "
              "báo cáo nói rõ (không số mới)",
              all(f"{k} " in out_n.split("**Chi tiết PARK")[1].split("**Chi tiết")[0] for k in pos_g)
              and "sổ lô không dựng được (ZaloPay 2026-10-09)" in err_n and "selfcheck: bỏ qua sổ lô" in err_n
              and "ⓘ Chưa dựng được sổ lô" in out_n and "ⓘ Chưa dựng được sổ lô" not in out_g, err_n)
        parts_ok = ps.sleeve_parts("MX1", 1786.0, {"MX1": {"LAG": 1500, "PARK": 286}}, set(), None, {}, set(), set())
        check("G3 sleeve: sleeve_parts trả đúng phần theo thứ tự SLEEVE_ORDER, không fallback",
              parts_ok == ([("PARK", 286), ("LAG", 1500)], None), str(parts_ok))
        ps.broker_positions_with_cost = lambda no_, d: {k: dict(v) for k, v in pos.items()}
        ps.sleeve_map_from_journal = lambda a: dict(journal)
        ps.current_park_basket = lambda: ({"QQ0"}, None)
        ps.section21_returns = lambda a, d: full
        out4, _ = build()
        check("K1: không truyền `returns_fn` ⇒ mặc định gọi `section21_returns` (công cụ thật)",
              "QQ3 3.0M, +20.00%" in out4, out4)
        ps.section21_returns = keep["section21_returns"]
        seen = []

        def fake_pr(label, asof):
            seen.append((label, asof))
            print("dòng công cụ in ra stdout")
            return {"positions": tool}
        rrg.position_returns = fake_pr
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            got = ps.section21_returns("ZaloPay", "2026-10-09")
        check("`section21_returns` = `report_return_gate.position_returns(...)['positions']` — đúng "
              "hàm cổng dùng; stdout của công cụ KHÔNG lẫn vào nội dung báo cáo",
              got is tool and seen == [("ZaloPay", "2026-10-09")] and buf.getvalue() == ""
              and "dòng công cụ" in err.getvalue(), repr((seen, buf.getvalue())))
    finally:
        for k, v in keep.items():
            setattr(ps, k, v)
        rrg.position_returns = keep_rrg

    print()
    if FAILS:
        print(f"SELFCHECK FAILED: {len(FAILS)} assertion — {FAILS}")
        return 1
    print("SELFCHECK PASSED — mọi assertion OK.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
