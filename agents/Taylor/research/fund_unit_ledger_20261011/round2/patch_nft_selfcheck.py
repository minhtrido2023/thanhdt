#!/usr/bin/env python3
"""Vá một lần `bin/nav_flow_term_selfcheck.py` cho luật gán D1 (job Taylor_20261010_182122).
Chạy: python3 patch_nft_selfcheck.py <đường dẫn file selfcheck>"""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)


rep('''def rows_only(seq):
    """nav_history thật KHÔNG có dòng ngày inception (07-01) — baseline đến từ starting_capital."""
    return [r for r in seq if r[0] != D(2026, 7, 1)]
''', '''def rows_only(seq):
    """nav_history thật KHÔNG có dòng ngày inception (07-01) — baseline đến từ starting_capital.
    Mỗi dòng mang `balance_ts` 19:10 cùng ngày (luật gán dòng tiền so với mốc này)."""
    return [acf.NavRow(d, nav, balance_ts=f"{d}T19:10:00") for d, nav in seq if d != D(2026, 7, 1)]


def must(fn, label):
    """`fn()` KHÔNG được raise — đầu vào hợp lệ mà bị từ chối phải thành ASSERTION, không sập."""
    try:
        return fn()
    except AssertionError:
        raise
    except Exception as exc:                                    # noqa: BLE001
        raise AssertionError(f"{label}: không được raise, được {type(exc).__name__}: {exc}") from exc
''')

# 3. rút sau đóng cửa
rep('''    fl = [{"date": "2026-07-03", "amount_vnd": -100_000_000, "kind": "withdraw",
           "evidence": "selfcheck fixture", "timing": "eod"}]''',
    '''    fl = [{"date": "2026-07-03", "amount_vnd": -100_000_000, "kind": "withdraw",
           "evidence": "selfcheck fixture", "timing": "eod", "time_ict": "16:00"}]''')
rep('''    # ---- 4. Hai quy ước timing KHÔNG tương đương (nên phải bắt ghi rõ, không đoán).''',
    '''    # ---- 4. Hai thời điểm tiền vào KHÔNG tương đương (nên phải khai GIỜ, code không đoán).''')
rep('''       "dùng SAI quy ước timing phải ra số KHÁC — nếu bằng nhau thì quy ước là vô nghĩa")''',
    '''       "khai SAI giờ tiền vào phải ra số KHÁC — nếu bằng nhau thì giờ khai là vô nghĩa")''')
rep('''        {"date": "2026-07-01", "amount_vnd": 1_000_000_000, "kind": "deposit",
         "evidence": "vốn khởi điểm — KHÔNG được tính lần hai"}])))''',
    '''        {"date": "2026-07-01", "amount_vnd": 1_000_000_000, "kind": "deposit",
         "time_ict": "09:00", "evidence": "vốn khởi điểm — KHÔNG được tính lần hai"}])))''')
rep('''    ok(r_inc["inception"]["return_pct"] == 3.0,
       f"flow ngày inception phải bị bỏ, được {r_inc['inception']['return_pct']}")
''', '''    ok(r_inc["inception"]["return_pct"] == 3.0,
       f"flow ngày inception phải bị bỏ, được {r_inc['inception']['return_pct']}")
    ok(len(r_inc["dropped_flows"]) == 1 and r_inc["pending_flows"] == [],
       f"flow bị bỏ phải HIỆN ở dropped_flows, được {r_inc['dropped_flows']}")
''')
rep('''    # ---- 6. Flow sau dòng nav_history cuối cùng: bỏ, không crash.
    r_after = ret(base_rows, acf.load_flows("SpaceX", flows_file(tmp, [
        {"date": "2026-12-31", "amount_vnd": 500_000_000, "kind": "deposit", "evidence": "x"}])))
    ok(r_after["inception"]["return_pct"] == 3.0, "flow ngoài kỳ đo phải bị bỏ")
''', '''    # ---- 6. Flow sau lần chụp NAV cuối cùng: TREO — không vào số nào, không crash, và HIỆN ra.
    r_after = ret(base_rows, acf.load_flows("SpaceX", flows_file(tmp, [
        {"date": "2026-12-31", "amount_vnd": 500_000_000, "kind": "deposit", "evidence": "x",
         "time_ict": "10:00"}])))
    ok(r_after["inception"]["return_pct"] == 3.0, "flow treo không được đổi tỉ suất")
    ok(len(r_after["pending_flows"]) == 1 and r_after["pending_flows"][0]["amount_vnd"] == 500e6
       and "net_flow_vnd" not in r_after["inception"],
       f"flow treo phải HIỆN ở pending_flows (không vô hình), được {r_after['pending_flows']}")
''')
rep('''    # ---- 7. Flow ngày KHÔNG có phiên (bod) rơi vào phiên kế tiếp.''',
    '''    # ---- 7. Flow ngày KHÔNG có phiên rơi vào phiên kế tiếp (dòng NAV đầu tiên chụp sau nó).''')
rep('''    ok(D(2026, 7, 6) in mapped, f"flow thứ Bảy 07-04 phải gán vào phiên 07-06, được {list(mapped)}")''',
    '''    ok(list(mapped) == [D(2026, 7, 6)] and mapped[D(2026, 7, 6)][0]["timing"] == "bod"
       and mapped[D(2026, 7, 6)][0]["session_date"] == D(2026, 7, 6),
       f"flow thứ Bảy 07-04 phải gán vào phiên 07-06 (bod), được {mapped}")''')
rep('''        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
         "timing": "bod"},                                              # bod không khai giờ''',
    '''        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
         "timing": "bod"},                                              # không khai giờ
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x"},  # không giờ, không timing''')
rep('''    # ---- 8. Schema fail-closed: 9 bản ghi hỏng, tất cả phải raise CashFlowError.''',
    '''    # ---- 8. Schema fail-closed: 10 bản ghi hỏng, tất cả phải raise CashFlowError.''')
a = s.index('    # Mặc định (không khai timing) là eod, và bod hợp lệ khi có giờ.')
b = s.index('    # ---- 9. Cổng NAV-jump: nạp mà KHÔNG ghi nhận ⇒ CHẶN; ghi nhận ⇒ mở.')
s = s[:a] + '''    # KHÔNG có mặc định timing: không khai ⇒ None (code suy khi gán); giờ được chuẩn hoá.
    dflt = acf.load_flows("SpaceX", flows_file(tmp, [
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
         "time_ict": "16:00"},
        {"date": "2026-07-03", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
         "timing": "bod", "time_ict": "9:05"}]))
    ok([f["timing"] for f in dflt] == ["bod", None] and not hasattr(acf, "DEFAULT_TIMING"),
       f"không khai timing phải là None (không mặc định), được {[f['timing'] for f in dflt]}")
    ok([f["time_ict"] for f in dflt] == ["09:05", "16:00"],
       f"time_ict phải chuẩn hoá HH:MM và sắp theo giờ, được {[f['time_ict'] for f in dflt]}")
    got = must(lambda: acf.attach_flows_to_rows(base_rows, dflt), "gán 2 bản ghi cùng ngày")
    ok([f["timing"] for f in got[D(2026, 7, 3)]] == ["bod", "eod"],
       f"09:05 ⇒ bod, 16:00 ⇒ eod trên cùng phiên 07-03, được {got}")
    # khai timing KHÁC kết quả suy ra ⇒ raise, nêu cả hai (không âm thầm chọn một bên)
    try:
        acf.attach_flows_to_rows(base_rows, acf.load_flows("SpaceX", flows_file(tmp, [
            {"date": "2026-07-04", "amount_vnd": 1, "kind": "deposit", "evidence": "x",
             "timing": "eod", "time_ict": "10:00"}])))
        raise AssertionError("khai eod cho tiền thứ Bảy (suy ra bod trên 07-06) phải raise")
    except acf.CashFlowError as exc:
        ok("timing='eod'" in str(exc) and "'bod'" in str(exc) and "2026-07-06" in str(exc),
           f"thông điệp phải nêu cả quy ước khai lẫn quy ước suy ra, được: {exc}")

''' + s[b:]
rep('''    jump_rows = rows_only(BASE) + [(D(2026, 7, 7), 1_240_000_000.0)]   # +20,4% trong 1 phiên''',
    '''    jump_rows = rows_only(BASE + [(D(2026, 7, 7), 1_240_000_000.0)])   # +20,4% trong 1 phiên''')
rep('''            {"date": "2026-07-07", "amount_vnd": 200_000_000, "kind": "deposit",
             "evidence": "sao kê DNSE"}])
        gate._check_nav_flow_records(report)
        ok(True, "")''', '''            {"date": "2026-07-07", "amount_vnd": 200_000_000, "kind": "deposit",
             "time_ict": "10:00", "evidence": "sao kê DNSE"}])
        must(lambda: gate._check_nav_flow_records(report), "cổng với deposit đã ghi nhận")
        ok(True, "")
        # nạp thứ Bảy 07-04 KHÔNG giải thích bước nhảy thứ Ba 07-07 (nó được gán vào thứ Hai 07-06)
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [
            {"date": "2026-07-04", "amount_vnd": 200_000_000, "kind": "deposit",
             "time_ict": "10:00", "evidence": "sao kê DNSE"}])
        try:
            gate._check_nav_flow_records(report)
            raise AssertionError("bản ghi gán vào phiên KHÁC không được mở cổng cho bước nhảy 07-07")
        except RuntimeError as exc:
            ok("nav-flow BLOCK" in str(exc) and "2026-07-07" in str(exc), f"sai thông điệp: {exc}")
        # ...còn nạp 20:00 thứ Hai 07-06 (sau lần chụp 19:10) thì ĐÚNG là của phiên 07-07
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [
            {"date": "2026-07-06", "amount_vnd": 200_000_000, "kind": "deposit",
             "time_ict": "20:00", "evidence": "sao kê DNSE"}])
        must(lambda: gate._check_nav_flow_records(report), "cổng với nạp tối hôm trước")
        ok(True, "")
        # bản ghi thiếu giờ ⇒ cổng CHẶN (fail-closed), không sập và không cho qua
        os.environ["ACCOUNT_CASH_FLOWS_PATH"] = flows_file(tmp, [
            {"date": "2026-07-07", "amount_vnd": 200_000_000, "kind": "deposit", "evidence": "x"}])
        try:
            gate._check_nav_flow_records(report)
            raise AssertionError("bản ghi thiếu time_ict phải làm cổng CHẶN")
        except RuntimeError as exc:
            ok("nav-flow BLOCK" in str(exc) and "thiếu time_ict" in str(exc), f"sai thông điệp: {exc}")''')
rep('''             "evidence": "đối soát fill: toàn bộ biến động từ giá"}])
        gate._check_nav_flow_records(report)
        ok(True, "")''', '''             "evidence": "đối soát fill: toàn bộ biến động từ giá"}])
        must(lambda: gate._check_nav_flow_records(report), "cổng với market_only")
        ok(True, "")''')
rep('''        gate._check_nav_flow_records(Path("spend_report_weekly_2026-09-27.md"))
        ok(True, "")''', '''        must(lambda: gate._check_nav_flow_records(Path("spend_report_weekly_2026-09-27.md")),
             "cổng với báo cáo không phải của account")
        ok(True, "")''')
open(p, "w", encoding="utf-8").write(s)
print("patched", p)
