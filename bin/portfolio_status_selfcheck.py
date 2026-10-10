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
        out_sx = ps.build_output("SpaceX", date_spacex, returns_fn=_no_tool)
        check(f"build_output SpaceX ({date_spacex}) không None", out_sx is not None)
        check("build_output SpaceX: có header TÌNH TRẠNG DANH MỤC",
              out_sx is not None and "TÌNH TRẠNG DANH MỤC" in out_sx)
        check("build_output SpaceX: có bảng Cơ cấu danh mục",
              out_sx is not None and "Cơ cấu danh mục" in out_sx)
    else:
        print("[SKIP] build_output SpaceX — không có nav_history_SpaceX.csv")

    if date_zalopay:
        out_zp = ps.build_output("ZaloPay", date_zalopay, returns_fn=_no_tool)
        check(f"build_output ZaloPay ({date_zalopay}) không None", out_zp is not None)
    else:
        print("[SKIP] build_output ZaloPay — không có nav_history_ZaloPay.csv")

    # 7: §12 sanity — 2 account cho output khác nhau (không đọc chung không lọc)
    if date_spacex and date_zalopay:
        out_sx = ps.build_output("SpaceX", date_spacex, returns_fn=_no_tool)
        out_zp = ps.build_output("ZaloPay", date_zalopay, returns_fn=_no_tool)
        check("§12: SpaceX và ZaloPay cho output KHÁC nhau (không lẫn account)",
              out_sx != out_zp)

    # 8: ngày TRƯỚC mọi dòng nav_history (không có "gần nhất trước") → None, không crash.
    # Lưu ý: load_nav_row() CỐ Ý fallback về dòng gần nhất TRƯỚC ngày yêu cầu (xử lý report
    # chạy vào ngày chưa có NAV hôm đó) — nên test None phải dùng ngày TRƯỚC lịch sử, không
    # phải ngày tương lai (tương lai vẫn có "gần nhất trước" = dòng cuối cùng).
    check("build_output ngày TRƯỚC mọi lịch sử NAV → None",
          ps.build_output("SpaceX", "2000-01-01", returns_fn=_no_tool) is None)

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
    # Mốc CỐ ĐỊNH T+25 (khớp backtest pin `hold_days=25`, user xác nhận 2026-10-06) — kỳ vọng
    # cũ "T+14/T+20, 'còn ~'" là khoảng đã bỏ từ 2026-09-30, không có nguồn backtest.
    check("lag_exit_hint: 15 phiên → còn 10 phiên tới hạn cố định T+25",
          h_in_window is not None and "còn 10 phiên tới hạn cố định T+25" in h_in_window,
          str(h_in_window))
    h_past = ps.lag_exit_hint("SCL", {"SCL": "2026-08-10"}, "2026-09-29")
    check("lag_exit_hint: đã qua T+25 → 'ĐÃ QUA hạn cố định T+25'",
          h_past is not None and "ĐÃ QUA hạn cố định T+25" in h_past, str(h_past))
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
        out_stale = ps.build_output("ZaloPay", _future, returns_fn=_no_tool)
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
        lots = {tk: {"qty": int(p["qty"]), "entry_date": "2026-06-01"} for tk, p in aei_pos.items()}
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
