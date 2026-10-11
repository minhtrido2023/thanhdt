#!/usr/bin/env python3
"""Vá một lần cho N11 (job Taylor_20261010_182122): chỉnh chữ ký 2 hàm mới của
daily_nav_snapshot.py + thêm case/mutation vào nav_jump_flow_gate_selfcheck.py + case vào
portfolio_status_selfcheck.py. Chạy: python3 patch_n11_tests.py <thư mục bin>"""
import sys

BIN = sys.argv[1]


def patch(name, pairs):
    p = f"{BIN}/{name}"
    s = open(p, encoding="utf-8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (name, s.count(old), old[:80])
        s = s.replace(old, new)
    open(p, "w", encoding="utf-8").write(s)
    print("patched", name)


patch("daily_nav_snapshot.py", [
    ('''def unit_price_performance(account, date, hist_rows):''',
     '''def unit_price_performance(account, date, hist_rows, inception=None, flows=None):'''),
    ('''    `hist_rows`: nav_history ĐÃ gồm dòng `date`. Không tính được ⇒ trả lỗi thật để in ra (§29),
    KHÔNG lùi về công thức cũ.
    """''',
     '''    `hist_rows`: nav_history ĐÃ gồm dòng `date`. Không tính được ⇒ trả lỗi thật để in ra (§29),
    KHÔNG lùi về công thức cũ. `inception`/`flows` bỏ trống = đọc file thật (flows: bắt buộc có
    sổ dòng tiền, như đường công bố); truyền vào chỉ để selfcheck chạy offline.
    """'''),
    ('''        return compute_period_returns(account, datetime.date.fromisoformat(date), rows,
                                      load_inception(account)), None''',
     '''        return compute_period_returns(account, datetime.date.fromisoformat(date), rows,
                                      inception or load_inception(account), flows), None'''),
    ('''def nav_performance_lines(nav, day_change, perf, perf_err):''',
     '''def nav_performance_lines(day_change, perf, perf_err):'''),
    ('''    paren, perf_lines = nav_performance_lines(nav, day_change, perf, perf_err)''',
     '''    paren, perf_lines = nav_performance_lines(day_change, perf, perf_err)'''),
])

patch("portfolio_status.py", [
    ('''    today_row, prior_row = load_nav_row(account, date)
    if today_row is None:''',
     '''    today_row, _prior_row = load_nav_row(account, date)
    if today_row is None:'''),
])

NEW_CASES = r'''    case("chay-lai-cung-ngay", c19)

    # ======================= N11: phần trăm của dòng 💰 NAV lấy từ giá đơn vị quỹ =============
    import csv as _csv
    import datetime as _dtm
    import daily_nav_snapshot as _dns
    FIX = os.path.join(HERE, "fixtures", "nav_unit_ledger_asof_20261009")
    FIX_INC = json.load(open(os.path.join(FIX, "account_inception.json"), encoding="utf-8"))

    def fix_hist(account):
        with open(os.path.join(FIX, f"nav_history_{account}.csv"), encoding="utf-8") as fh:
            return list(_csv.DictReader(fh))

    def loaded(records):
        from account_cash_flows import load_flows as _lf
        p = flows_file(records)
        try:
            return _lf("SpaceX", p)
        finally:
            os.remove(p)

    SYN_INC = {"inception_date": "2026-07-01", "starting_capital": 1_000_000_000}
    SYN = [{"date": "2026-07-02", "nav": "1000000000", "balance_ts": "2026-07-02T19:10:00"},
           {"date": "2026-07-03", "nav": "1224000000", "balance_ts": "2026-07-03T19:10:00"}]

    # ---- 20. fixture thật asof 2026-10-09: ZaloPay phải ra mốc 987.865.567 (−4,91%), không phải
    # mốc 1 tỷ (−6,06%); SpaceX (vốn 1 tỷ) giữ NGUYÊN TỪNG KÝ TỰ dòng đã gửi.
    def c20():
        f = []
        for account, want_paren, want_line, old_wrong in (
                ("ZaloPay", "+12,614,629 VND, +1.36% so với hôm trước",
                 "   Từ go-live: -48,470,726 VND (-4.91%)", "(-6.06%)"),
                ("SpaceX", "-642,970 VND, -0.07% so với hôm trước",
                 "   Từ go-live: -13,301,426 VND (-1.33%)", None)):
            hist = fix_hist(account)
            perf, err = _dns.unit_price_performance(account, "2026-10-09", hist, FIX_INC[account], [])
            if err or perf is None:
                f.append(f"{account}: phải tính được, được lỗi {err!r}")
                continue
            day_change = float(hist[-1]["nav"]) - float(hist[-2]["nav"])
            paren, lines = _dns.nav_performance_lines(day_change, perf, err)
            if paren != want_paren:
                f.append(f"{account}: đoạn trong ngoặc phải là {want_paren!r}, được {paren!r}")
            if lines != [want_line]:
                f.append(f"{account}: dòng go-live phải là {[want_line]!r}, được {lines!r}")
            if old_wrong and any(old_wrong in ln for ln in lines):
                f.append(f"{account}: vẫn in số theo mốc 1 tỷ {old_wrong}")
            if perf["inception"]["nav0"] != float(FIX_INC[account]["starting_capital"]):
                f.append(f"{account}: mốc khởi điểm phải lấy từ account_inception.json, được "
                         f"{perf['inception']['nav0']}")
        return f
    case("N11-fixture-2026-10-09-dung-moc-khoi-diem", c20)

    # ---- 21. toàn bộ lịch sử fixture (chưa có dòng tiền): hai dòng mới == công thức tham chiếu
    # (thay đổi NAV / NAV phiên trước; NAV / vốn khởi điểm) từng ngày, từng ký tự.
    def c21():
        f, n = [], 0
        for account in ("SpaceX", "ZaloPay"):
            hist = fix_hist(account)
            cap = float(FIX_INC[account]["starting_capital"])
            inc_date = FIX_INC[account]["inception_date"]
            for i, row in enumerate(hist):
                if row["date"] <= inc_date:
                    continue
                nav = float(row["nav"])
                prev = float(hist[i - 1]["nav"]) if i and hist[i - 1]["date"] > inc_date else cap
                perf, err = _dns.unit_price_performance(account, row["date"], hist[:i + 1],
                                                        FIX_INC[account], [])
                paren, lines = _dns.nav_performance_lines(nav - prev, perf, err)
                want_p = f"{nav - prev:+,.0f} VND, {round((nav / prev - 1) * 100, 3):+.2f}% so với hôm trước"
                want_l = [f"   Từ go-live: {nav - cap:+,.0f} VND ({round((nav / cap - 1) * 100, 3):+.2f}%)"]
                n += 1
                if (paren, lines) != (want_p, want_l):
                    f.append(f"{account} {row['date']}: được {(paren, lines)!r}, tham chiếu {(want_p, want_l)!r}")
        if n < 130:
            f.append(f"phải kiểm >= 130 (account, ngày) của fixture, chỉ có {n}")
        return f[:5]
    case("N11-toan-lich-su-khong-dong-tien", c21)

    # ---- 22. CÓ dòng tiền: % là tỉ suất giá đơn vị, số VND tách lãi/lỗ với nạp/rút ròng.
    #   1.000 → nạp 200 lúc 10:00 → +2% ⇒ NAV 1.224: lãi 24tr = +2,00% (không phải +22,40%).
    def c22():
        f = []
        fl = loaded([{"date": "2026-07-03", "time_ict": "10:00", "amount_vnd": 200_000_000,
                      "kind": "deposit", "evidence": "sao kê"}])
        perf, err = _dns.unit_price_performance("SpaceX", "2026-07-03", SYN, SYN_INC, fl)
        paren, lines = _dns.nav_performance_lines(224_000_000.0, perf, err)
        want_p = ("+24,000,000 VND lãi/lỗ, +2.00% so với hôm trước; NAV đổi +224,000,000 VND, "
                  "trong đó nạp/rút ròng +200,000,000 VND")
        want_l = ["   Từ go-live: +24,000,000 VND lãi/lỗ (+2.00%); NAV đổi +224,000,000 VND, "
                  "trong đó nạp/rút ròng +200,000,000 VND"]
        if paren != want_p:
            f.append(f"ngày có nạp: ngoặc phải là {want_p!r}, được {paren!r}")
        if lines != want_l:
            f.append(f"ngày có nạp: dòng go-live phải là {want_l!r}, được {lines!r}")
        if "22.40" in paren + "".join(lines):
            f.append("vẫn in +22,40% (tính nạp tiền thành lãi)")
        # rút 100tr sau đóng cửa ngày thị trường −1%: 1.000 → 990 − 100 = 890
        syn_w = [SYN[0], {"date": "2026-07-03", "nav": "890000000", "balance_ts": "2026-07-03T19:10:00"}]
        fl = loaded([{"date": "2026-07-03", "time_ict": "16:00", "amount_vnd": -100_000_000,
                      "kind": "withdraw", "evidence": "sao kê"}])
        perf, err = _dns.unit_price_performance("SpaceX", "2026-07-03", syn_w, SYN_INC, fl)
        paren, lines = _dns.nav_performance_lines(-110_000_000.0, perf, err)
        if paren != ("-10,000,000 VND lãi/lỗ, -1.00% so với hôm trước; NAV đổi -110,000,000 VND, "
                     "trong đó nạp/rút ròng -100,000,000 VND"):
            f.append(f"ngày có rút: ngoặc sai: {paren!r}")
        return f
    case("N11-co-dong-tien-tach-lai-lo-voi-nap-rut", c22)

    # ---- 23. dòng tiền của NGÀY TRƯỚC: hôm nay không nạp ⇒ dòng ngày giữ dạng cũ, dòng go-live
    # tách; dòng tiền TREO thì hiện cảnh báo riêng.
    def c23():
        f = []
        syn3 = SYN + [{"date": "2026-07-06", "nav": "1236240000", "balance_ts": "2026-07-06T19:10:00"}]
        fl = loaded([{"date": "2026-07-03", "time_ict": "10:00", "amount_vnd": 200_000_000,
                      "kind": "deposit", "evidence": "sao kê"},
                     {"date": "2026-07-06", "time_ict": "21:00", "amount_vnd": 50_000_000,
                      "kind": "deposit", "evidence": "nạp tối nay"}])
        perf, err = _dns.unit_price_performance("SpaceX", "2026-07-06", syn3, SYN_INC, fl)
        paren, lines = _dns.nav_performance_lines(12_240_000.0, perf, err)
        if paren != "+12,240,000 VND, +1.00% so với hôm trước":
            f.append(f"ngày KHÔNG nạp phải giữ dạng dòng cũ, được {paren!r}")
        if lines[:1] != ["   Từ go-live: +36,240,000 VND lãi/lỗ (+3.02%); NAV đổi +236,240,000 VND, "
                         "trong đó nạp/rút ròng +200,000,000 VND"]:
            f.append(f"dòng go-live phải tách lãi/lỗ với nạp/rút, được {lines[:1]!r}")
        if len(lines) != 2 or not all(x in lines[1] for x in ("⚠️", "2026-07-06 21:00", "+50,000,000",
                                                              "CHƯA nằm trong số nào", "TREO")):
            f.append(f"dòng tiền treo phải có cảnh báo riêng, được {lines[1:]!r}")
        return f
    case("N11-dong-tien-ngay-truoc-va-treo", c23)

    # ---- 24. không tính được ⇒ nói thẳng + lỗi thật, KHÔNG lùi về công thức mốc 1 tỷ.
    def c24():
        f = []
        for label, kw, need in (
                ("account không có mốc khởi điểm", {"account": "NoSuchAccount"}, "NoSuchAccount"),
                ("bản ghi dòng tiền thiếu giờ", {"account": "SpaceX", "inception": SYN_INC, "flows": [
                    {"date": _dtm.date(2026, 7, 3), "amount_vnd": 2e8, "kind": "deposit",
                     "evidence": "x", "timing": None, "time_ict": None}]}, "không có time_ict")):
            perf, err = _dns.unit_price_performance(kw.pop("account"), "2026-07-03", SYN, **kw)
            if perf is not None or not err or need not in err:
                f.append(f"{label}: phải trả (None, lỗi có {need!r}), được {(perf, err)!r}")
                continue
            paren, lines = _dns.nav_performance_lines(224_000_000.0, perf, err)
            if "%" in paren.replace("tỉ suất", "") or "KHÔNG tính được" not in paren:
                f.append(f"{label}: ngoặc không được in phần trăm nào, được {paren!r}")
            if len(lines) != 1 or "KHÔNG tính được" not in lines[0] or need not in lines[0] or "%)" in lines[0]:
                f.append(f"{label}: dòng go-live phải nêu lỗi thật, không in %, được {lines!r}")
        # ngày chưa có phiên nào sau mốc khởi điểm: không có "hôm trước" để so
        perf, err = _dns.unit_price_performance(
            "SpaceX", "2026-07-01", [{"date": "2026-07-01", "nav": "1000000000", "balance_ts": ""}],
            SYN_INC, [])
        paren, lines = _dns.nav_performance_lines(0.0, perf, err)
        if err or "chưa có phiên nào sau mốc khởi điểm" not in paren or lines != ["   Từ go-live: +0 VND (+0.00%)"]:
            f.append(f"ngày mốc khởi điểm: được {(paren, lines, err)!r}")
        return f
    case("N11-khong-tinh-duoc-thi-noi-thang", c24)

    # ---- 25. main() PHẢI in bằng hai hàm trên, không còn công thức `/ args.starting_capital`.
    def c25():
        src = open(TARGET, encoding="utf-8").read().split("def main(")[1]
        f = []
        for need in ("unit_price_performance(args.account, args.date, hist_rows)",
                     "nav_performance_lines(day_change, perf, perf_err)",
                     'f"💰 **NAV {args.date}: {nav:,.0f} VND** ({paren})"', "] + perf_lines"):
            if need not in src:
                f.append(f"main() thiếu {need!r}")
        if "/ args.starting_capital" in src or "day_change_pct:+.2f" in src:
            f.append("main() vẫn còn công thức phần trăm cũ (mốc --starting-capital / tỉ số NAV thô)")
        return f
    case("N11-main-dung-mot-nguon", c25)
'''

NEW_MUT = r'''    ("main-bo-balance_ts", lambda t: t.replace(
        '"egg": egg_value, "offbook": offbook}, balance_ts=bal["ts"])',
        '"egg": egg_value, "offbook": offbook})')),
    # ---- N11
    ("n11-moc-khoi-diem-1-ty", lambda t: t.replace(
        "inception or load_inception(account), flows), None",
        '{"inception_date": (inception or load_inception(account))["inception_date"], '
        '"starting_capital": 1_000_000_000}, flows), None')),
    ("n11-bo-dong-tien", lambda t: t.replace(
        "inception or load_inception(account), flows), None",
        "inception or load_inception(account), []), None")),
    ("n11-nuot-loi-thanh-so", lambda t: t.replace(
        '        return None, f"{type(exc).__name__}: {exc}"\n\n\ndef nav_performance_lines',
        '        return None, ""\n\n\ndef nav_performance_lines')),
    ("n11-luon-dang-cu", lambda t: t.replace("        if not flow:\n            return f\"{period['pnl_vnd']:+,.0f} VND{tail}\"",
                                             "        if True:\n            return f\"{period['pnl_vnd']:+,.0f} VND{tail}\"")),
    ("n11-vnd-la-thay-doi-nav", lambda t: t.replace(
        "            return f\"{period['pnl_vnd']:+,.0f} VND{tail}\"",
        "            return f\"{period['nav1'] - period['nav0']:+,.0f} VND{tail}\"").replace(
        "        return (f\"{period['pnl_vnd']:+,.0f} VND lãi/lỗ{tail}; NAV đổi \"",
        "        return (f\"{period['nav1'] - period['nav0']:+,.0f} VND lãi/lỗ{tail}; NAV đổi \"")),
    ("n11-ngay-lay-pct-go-live", lambda t: t.replace(
        "paren = vnd(day, f\", {day['return_pct']:+.2f}% so với hôm trước\")",
        "paren = vnd(day, f\", {inc['return_pct']:+.2f}% so với hôm trước\")")),
    ("n11-go-live-lay-pct-ngay", lambda t: t.replace(
        "lines = [\"   Từ go-live: \" + vnd(inc, f\" ({inc['return_pct']:+.2f}%)\")]",
        "lines = [\"   Từ go-live: \" + vnd(inc, f\" ({day['return_pct']:+.2f}%)\")]")),
    ("n11-go-live-lay-vnd-ngay", lambda t: t.replace(
        "lines = [\"   Từ go-live: \" + vnd(inc, f\" ({inc['return_pct']:+.2f}%)\")]",
        "lines = [\"   Từ go-live: \" + vnd(day, f\" ({inc['return_pct']:+.2f}%)\")]")),
    ("n11-bo-canh-bao-treo", lambda t: t.replace(
        '    for f in perf["pending_flows"]:\n        lines.append(f"   ⚠️ Dòng tiền đã khai',
        '    for f in []:\n        lines.append(f"   ⚠️ Dòng tiền đã khai')),
    ("n11-dong-tien-rong-dao-dau", lambda t: t.replace(
        "trong đó nạp/rút ròng {flow:+,.0f} VND\")", "trong đó nạp/rút ròng {-flow:+,.0f} VND\")")),
    ("n11-main-in-cong-thuc-cu", lambda t: t.replace(
        'f"💰 **NAV {args.date}: {nav:,.0f} VND** ({paren})"',
        'f"💰 **NAV {args.date}: {nav:,.0f} VND** ({day_change:+,.0f} VND, {day_change_pct:+.2f}% so với hôm trước)"')),
    ("n11-main-bo-dong-go-live", lambda t: t.replace("    ] + perf_lines\n", "    ]\n")),'''

patch("nav_jump_flow_gate_selfcheck.py", [
    ('''    case("chay-lai-cung-ngay", c19)
''', NEW_CASES),
    ('''    ("main-bo-balance_ts", lambda t: t.replace(
        '"egg": egg_value, "offbook": offbook}, balance_ts=bal["ts"])',
        '"egg": egg_value, "offbook": offbook})')),''', NEW_MUT),
])

PS_CASE = r'''    # 17b (N11, 2026-10-11): "Hôm nay" và "Từ khi bắt đầu hoạt động" là tỉ suất GIÁ ĐƠN VỊ (đã
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
                    out = ps.build_output("SpaceX", date, returns_fn=_no_tool)
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
        finally:
            ps.EXEC_DIR = old_exec_dir
            if old_env is None:
                os.environ.pop("ACCOUNT_CASH_FLOWS_PATH", None)
            else:
                os.environ["ACCOUNT_CASH_FLOWS_PATH"] = old_env

    # 18: value_per_share dạng CHUỖI từ producer'''
patch("portfolio_status_selfcheck.py", [
    ('''    # 18: value_per_share dạng CHUỖI từ producer''', PS_CASE),
])
