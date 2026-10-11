A = "bin/account_cash_flows.py"; U = "bin/nav_unit_ledger.py"; P = "bin/nav_period_returns.py"
M = [
 ("A05x", A, '        if kind == "deposit" and amount <= 0:', "        if False:", "bỏ hẳn kiểm dấu deposit"),
 ("A06x", A, '        if kind == "withdraw" and amount >= 0:', "        if False:", "bỏ hẳn kiểm dấu withdraw"),
 ("A66", A, '        for key in ("date", "amount_vnd", "kind", "evidence"):', '        for key in ("date", "amount_vnd", "kind"):', "không bắt key evidence (⇒ KeyError)"),
 ("A67", A, "        if not isinstance(rec, dict):", "        if False:", "bản ghi không phải object"),
 ("A68", A, "    if not isinstance(raw, list):", "    if False:", "entry không phải list"),
 ("A69", A, '            raise CashFlowError(f"{where}: date không phải YYYY-MM-DD ({exc})") from exc', "            d = datetime.date(2026, 1, 1)", "date sai ⇒ mặc định"),
 ("A70", A, '            raise CashFlowError(f"{where}: time_ict {exc}") from exc', '            time_ict = "00:00"', "giờ sai dạng ⇒ 00:00"),
 ("A71", A, "    def __new__(cls, date, nav, is_estimate=False, balance_ts=None):", "    def __new__(cls, date, nav, is_estimate=False, balance_ts=None, **kw):", "noop"),
 ("U62", U, "    if account not in cfg:", "    if False:", "account lạ trong inception ⇒ KeyError"),
 ("U63", U, "    if starting_capital is not None:\n        return _parse_date(inception[\"inception_date\"]), float(starting_capital)", "    if starting_capital is not None:\n        return rows[0][0], float(starting_capital)", "mốc = ngày dòng đầu thay vì inception_date"),
 ("P54", P, "    if nav1_row is None:", "    if False:", "không dòng nào <= report_date"),
 ("P55", P, '        "nav1": b["nav"],', '        "nav1": a["nav"],', "nav1 sai"),
]
