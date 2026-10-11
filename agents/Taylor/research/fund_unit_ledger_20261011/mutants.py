#!/usr/bin/env python3
"""Mutation test cho bước 1 "quỹ mở". Sửa TẠI CHỖ từng mutant trong worktree (khôi phục bằng
try/finally), chạy 4 selfcheck, phân loại:
  CHẾT-ASSERT  = có selfcheck rc≠0 VÀ lỗi là assertion (ASSERT-FAIL / AssertionError / dòng FAIL)
  CHẾT-SẬP     = rc≠0 nhưng chỉ có Traceback không phải assertion  (KHÔNG tính là chết)
  SỐNG         = cả 4 selfcheck rc=0
Dùng: python3 mutants.py <worktree>   (rc=0 ⇔ mọi mutant CHẾT-ASSERT)"""
import pathlib, subprocess, sys

WT = pathlib.Path(sys.argv[1])
ONLY = set(sys.argv[2:])
CHECKS = [["bin/nav_unit_ledger_selfcheck.py"], ["bin/nav_flow_term_selfcheck.py"],
          ["bin/nav_period_returns.py", "--selfcheck"], ["bin/nav_jump_flow_gate_selfcheck.py"]]
L, R, A = "bin/nav_unit_ledger.py", "bin/nav_period_returns.py", "bin/account_cash_flows.py"
M = [
 # ---- nav_unit_ledger.py: quy tắc chốt
 ("L01 giá khởi điểm 10.000→1.000", L, "UNIT_PRICE_0 = 10_000.0", "UNIT_PRICE_0 = 1_000.0"),
 ("L02 bod phát hành ở giá khởi điểm thay vì giá phiên trước", L, "units += f_bod / price ", "units += f_bod / UNIT_PRICE_0 "),
 ("L03 giá eod không trừ dòng tiền", L, "price = (nav - f_eod) / units ", "price = nav / units "),
 ("L04 giá eod CỘNG dòng tiền", L, "price = (nav - f_eod) / units ", "price = (nav + f_eod) / units "),
 ("L05 eod không phát hành đơn vị", L, "units += f_eod / price ", "units += 0 * f_eod / price "),
 ("L06 eod phát hành ở giá phiên trước", L, "        price = (nav - f_eod) / units               # giá chốt cuối ngày, CHƯA tính dòng tiền eod\n", "        _prev = price\n        price = (nav - f_eod) / units\n        units += f_eod / _prev - f_eod / price\n"),
 ("L07 tổng bod lấy nhầm bản ghi eod", L, 'f_bod = sum(f["amount_vnd"] for f in day if f["timing"] == "bod")', 'f_bod = sum(f["amount_vnd"] for f in day if f["timing"] == "eod")'),
 ("L08 tổng eod lấy mọi bản ghi", L, 'f_eod = sum(f["amount_vnd"] for f in day if f["timing"] == "eod")', 'f_eod = sum(f["amount_vnd"] for f in day)'),
 ("L09 dòng nav ngày inception lọt vào sổ", L, "nav_rows = [r for r in rows if r[0] > inception_from]", "nav_rows = [r for r in rows if r[0] >= inception_from]"),
 ("L10 flow ngày inception KHÔNG bị loại", L, 'by_date = attach_flows_to_rows(nav_rows, [f for f in flows if f["date"] > inception_from])', 'by_date = attach_flows_to_rows(nav_rows, [f for f in flows if f["date"] >= inception_from])'),
 ("L11 không báo flow bị loại", L, 'dropped = [f for f in flows if f["date"] <= inception_from]', 'dropped = [f for f in flows if f["date"] < inception_from]'),
 ("L12 không báo flow treo", L, "pending = by_date.pop(None, [])", "pending = []; by_date.pop(None, [])"),
 ("L13 bỏ kiểm rút hết đầu ngày", L, "        if units <= 0:\n            raise ValueError(f\"{d}: rút đầu ngày", "        if units < -1e18:\n            raise ValueError(f\"{d}: rút đầu ngày"),
 ("L14 bỏ kiểm giá <= 0", L, "        if price <= 0:\n", "        if price < -1e18:\n"),
 ("L15 bỏ kiểm rút hết cuối ngày", L, "        if units <= 0:\n            raise ValueError(f\"{d}: rút cuối ngày", "        if units < -1e18:\n            raise ValueError(f\"{d}: rút cuối ngày"),
 ("L16 không mang cờ nav_is_estimate", L, '"nav_is_estimate": bool(getattr(row, "is_estimate", False)),', '"nav_is_estimate": False,'),
 ("L17 units_issued sai dấu", L, '"units_issued": units - before,', '"units_issued": before - units,'),
 ("L18 eod sau snapshot: đảo chiều so giờ", L, 'flow["time_ict"] > snap.strftime("%H:%M")', 'flow["time_ict"] < snap.strftime("%H:%M")'),
 ("L19 eod sau snapshot: bỏ lời gọi kiểm", L, "                _check_eod_in_snapshot(f, row)", "                pass"),
 ("L20 không đọc balance_ts", L, 'balance_ts=(rec.get("balance_ts") or None)))', "balance_ts=None))"),
 ("L21 đọc ngược cờ nav_is_estimate", L, 'is_estimate=(rec.get("nav_is_estimate") == "True"),', 'is_estimate=(rec.get("nav_is_estimate") == "False"),'),
 # ---- nav_unit_ledger.py: sổ chỉ-ghi-thêm
 ("L30 nới dung sai cột suy ra 1e-10→1e-2", L, "DERIVED_REL_TOL = 1e-10", "DERIVED_REL_TOL = 1e-2"),
 ("L31 không so cột nav", L, 'for key in ("nav", "flow_bod_vnd", "flow_eod_vnd"):', 'for key in ("flow_bod_vnd", "flow_eod_vnd"):'),
 ("L32 không so cột dòng tiền", L, 'for key in ("nav", "flow_bod_vnd", "flow_eod_vnd"):', 'for key in ("nav",):'),
 ("L33 không so cờ ước tính", L, 'if bool(new["nav_is_estimate"]) != old["nav_is_estimate"]:', "if False:"),
 ("L34 không bắt dòng chen vào quá khứ", L, "for d in sorted(set(built) - have):", "for d in []:"),
 ("L35 không bắt dòng đã chốt bị xoá", L, "        if new is None:\n            diffs.append(", "        if new is None:\n            continue\n            diffs.append("),
 ("L36 không so cột suy ra", L, 'for key in ("units_issued", "units", "unit_price"):', "for key in ():"),
 ("L37 lệch sổ vẫn ghi", L, "    if diffs:\n        raise LedgerDriftError(path, diffs)\n    last = sealed", "    last = sealed"),
 ("L38 chốt lại cả dòng cuối đã chốt", L, 'new = [r for r in ledger if (last is None or r["date"] > last)', 'new = [r for r in ledger if (last is None or r["date"] >= last)'),
 ("L39 bỏ qua --asof", L, 'and (asof is None or r["date"] <= asof)]', "and True]"),
 ("L40 không --seal vẫn ghi", L, "    if not write or not new:", "    if not new:"),
 ("L41 ghi đè thay vì giữ byte cũ", L, "f.write(old_text + ", 'f.write(",".join(LEDGER_FIELDS) + "\\n" + '),
 ("L42 sổ ghi dở vẫn đọc", L, '    if text and not text.endswith("\\n"):', "    if False:"),
 ("L43 sai header vẫn đọc", L, '    if not lines or lines[0].split(",") != LEDGER_FIELDS:', "    if not lines:"),
 ("L44 ngày không tăng dần vẫn đọc", L, '        if out and rec["date"] <= out[-1]["date"]:', "        if False:"),
 ("L45 ghi cờ luôn False", L, 'str(bool(row["nav_is_estimate"]))]) + "\\n"', '"False"]) + "\\n"'),
 ("L46 CLI rc lệch sổ = 0", L, "        return 2\n", "        return 0\n"),
 # ---- nav_period_returns.py
 ("R01 tỉ suất = tỉ số NAV (lỗi FAIL-H cũ)", R, 'factor = b["unit_price"] / a["unit_price"]', 'factor = b["nav"] / a["nav"]'),
 ("R02 ngưỡng quy năm 365→30", R, "ANNUALIZE_MIN_DAYS = 365", "ANNUALIZE_MIN_DAYS = 30"),
 ("R03 ngưỡng quy năm 365→366", R, "ANNUALIZE_MIN_DAYS = 365", "ANNUALIZE_MIN_DAYS = 366"),
 ("R04 quy năm sai số mũ", R, "factor ** (365.0 / days)", "factor ** (days / 365.0)"),
 ("R05 pnl cộng dòng tiền", R, '"pnl_vnd": b["nav"] - a["nav"] - net_flow,', '"pnl_vnd": b["nav"] - a["nav"] + net_flow,'),
 ("R06 pnl bỏ dòng tiền", R, '"pnl_vnd": b["nav"] - a["nav"] - net_flow,', '"pnl_vnd": b["nav"] - a["nav"],'),
 ("R07 mwr: bod không lùi 1 ngày", R, 'row["date"] - datetime.timedelta(days=1)\n            weighted', 'row["date"] - datetime.timedelta(days=0)\n            weighted'),
 ("R08 mwr: trọng số ngược chiều", R, '(b["date"] - at).days / days', '(at - a["date"]).days / days'),
 ("R09 mwr quy năm không qua cửa chặn", R, "mwr_ann = annualize_or_null(1 + mwr, days)[0] if mwr is not None else None", "mwr_ann = round(((1 + mwr) ** (365.0 / max(days, 1)) - 1) * 100, 3) if mwr is not None else None"),
 ("R10 mwr: nhiều nghiệm vẫn trả nghiệm đầu", R, "    if len(roots) != 1:", "    if len(roots) < 1:"),
 ("R11 mwr: 0 nghiệm trả 0", R, "    if len(roots) != 1:", "    if len(roots) > 1:\n        pass\n    if not roots:\n        return 0.0, None\n    if len(roots) > 1:"),
 ("R12 mwr: không dòng tiền trả 0", R, "        return nav1 / nav0 - 1, None", "        return 0.0, None"),
 ("R13 mốc đầu kỳ lấy <= thay vì <", R, '        if row["date"] < period_start_exclusive:', '        if row["date"] <= period_start_exclusive:'),
 ("R14 dòng cuối kỳ lấy < report_date", R, 'i1 = max(i for i, row in enumerate(ledger) if row["date"] <= report_date)', 'i1 = max(i for i, row in enumerate(ledger) if row["date"] < report_date)'),
 ("R15 kỳ tính cả dòng tiền của ngày mốc đầu", R, "for row in ledger[i0 + 1:i1 + 1]:", "for row in ledger[i0:i1 + 1]:"),
 ("R16 sổ đã chốt lệch vẫn công bố", R, "        if diffs:\n            raise LedgerDriftError(sealed_path, diffs)", "        if False:\n            raise LedgerDriftError(sealed_path, diffs)"),
 ("R17 CLI không đối chiếu sổ đã chốt", R, "sealed_path=ledger_path(args.account))", "sealed_path=None)"),
 ("R18 quy năm: bỏ lý do", R, "    if ann_note:\n        out[\"annualized_note\"] = ann_note", "    if False:\n        out[\"annualized_note\"] = ann_note"),
 ("R19 net_flow_vnd sai dấu", R, 'out["net_flow_vnd"] = net_flow', 'out["net_flow_vnd"] = -net_flow'),
 ("R20 mwr dùng tỉ suất gia quyền thời gian", R, "mwr, mwr_note = money_weighted_return(a[\"nav\"], b[\"nav\"], weighted)", "mwr, mwr_note = factor - 1, None"),
 # ---- account_cash_flows.py
 ("A01 mặc định quay về bod", A, 'DEFAULT_TIMING = "eod"', 'DEFAULT_TIMING = "bod"'),
 ("A02 bod không cần giờ", A, '        if timing == "bod" and time_ict is None:', "        if False:"),
 ("A03 giờ sai định dạng vẫn nhận", A, '                raise CashFlowError(f"{where}: time_ict không phải HH:MM', '                time_ict = str(time_ict); continue; raise CashFlowError(f"{where}: time_ict không phải HH:MM'),
 ("A04 eod ngày thiếu NAV bị coi là treo", A, '            elif not dates or f["date"] > dates[-1]:\n                key = None\n            else:\n                raise CashFlowError(', '            elif not dates or f["date"] > dates[-1]:\n                key = None\n            else:\n                key = None\n                continue\n                raise CashFlowError('),
 ("A05 eod sau dòng NAV cuối bị từ chối", A, '            elif not dates or f["date"] > dates[-1]:\n                key = None', '            elif not dates:\n                key = None'),
 ("A06 eod ngày thiếu NAV trôi sang phiên sau", A, '            else:\n                raise CashFlowError(\n                    f"flow {f[\'date\']} timing=\'eod\' nhưng nav_history không có dòng ngày đó "', '            else:\n                key = next((d for d in dates if d >= f["date"]), None)\n                mapped.setdefault(key, []).append(f)\n                continue\n                raise CashFlowError(\n                    f"flow {f[\'date\']} timing=\'eod\' nhưng nav_history không có dòng ngày đó "'),
 ("A07 không trả time_ict", A, '"timing": timing, "time_ict": time_ict})', '"timing": timing, "time_ict": None})'),
]

def run_checks():
    res = []
    for c in CHECKS:
        p = subprocess.run([sys.executable, *c], cwd=WT, capture_output=True, text=True, timeout=600)
        out = p.stdout + p.stderr
        if p.returncode == 0:
            res.append("ok")
        elif "ASSERT-FAIL" in out or "AssertionError" in out or "\n  FAIL " in out or out.startswith("  FAIL "):
            res.append("assert")
        else:
            res.append("crash")
    return res

base = run_checks()
print("nền (chưa mutant):", base)
assert base == ["ok"] * 4, "selfcheck nền phải xanh"
tally = {"CHẾT-ASSERT": 0, "CHẾT-SẬP": 0, "SỐNG": 0}
bad = []
for name, rel, old, new in M:
    if ONLY and name.split()[0] not in ONLY:
        continue
    path = WT / rel
    src = path.read_text(encoding="utf-8")
    if src.count(old) != 1:
        print(f"HỎNG-NEO  {name}: chuỗi neo xuất hiện {src.count(old)} lần"); bad.append(name); continue
    try:
        path.write_text(src.replace(old, new), encoding="utf-8")
        res = run_checks()
    finally:
        path.write_text(src, encoding="utf-8")
    verdict = "CHẾT-ASSERT" if "assert" in res else ("CHẾT-SẬP" if "crash" in res else "SỐNG")
    tally[verdict] += 1
    if verdict != "CHẾT-ASSERT":
        bad.append(name)
    print(f"{verdict:11s} {name}  {res}")
print("TỔNG:", tally, "| không đạt:", bad)
assert run_checks() == ["ok"] * 4, "sau khi khôi phục selfcheck phải xanh lại"
sys.exit(1 if bad else 0)
