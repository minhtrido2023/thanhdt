#!/usr/bin/env python3
"""Nghiệm thu 5 + 6 (vòng 2): in NGUYÊN VĂN đầu ra thật của cổng và của đẳng thức trên dữ liệu giả
khép kín (dùng lại bộ dựng dữ liệu của cash_identity_selfcheck.py — không broker, không data/ thật).
Dùng: python3 56_demo.py <worktree_bin>"""
import contextlib
import datetime
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, sys.argv[1])
import cash_identity_selfcheck as sc  # noqa: E402  (đặt MIKE_BOT_TEST_MODE=1, vô hiệu đường dẫn mặc định)
import cash_identity as ci  # noqa: E402

with contextlib.redirect_stderr(io.StringIO()):
    import report_delivery_gate as g  # noqa: E402

tmp = tempfile.mkdtemp(prefix="fcf_r2_demo_")
D = datetime.date

print("=" * 20, "NGHIỆM THU 5a — ô số 'Từ khi bắt đầu hoạt động' hỏng ⇒ BLOCK kèm nguyên ô")
report = Path(tmp) / "SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"
called = []


class Proc:
    stdout = '{"inception": {"return_pct": -1.33}}'


def fake_run(cmd, **kw):
    called.append(cmd)
    return Proc()


real_run, g.subprocess.run = g.subprocess.run, fake_run
try:
    for cell in ("+nan%", "n/a", "—", "−1,33%"):
        report.write_text(f"### 3.2 Hiệu suất lũy kế\n| Từ khi bắt đầu hoạt động (01/07 → 09/10) | {cell} | x |\n", encoding="utf-8")
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                g._check_period_returns(report)
            print(f"ô {cell!r}: QUA — {out.getvalue().strip()}")
        except RuntimeError as exc:
            print(f"ô {cell!r}: BLOCK — {exc}")
finally:
    g.subprocess.run = real_run
print(f"(số lần gọi CLI số chuẩn: {len(called)} — chỉ ô đọc được mới gọi)")

print("=" * 20, "NGHIỆM THU 5b — cash_identity không import được ⇒ deliver() VẪN giao, lỗi ở stderr")
wd = sc.internal_only(sc.World(tmp, "demo5")).add("SpaceX", sc.at(10, "10:30"), "external", 5_000_000).build()
day10 = Path(tmp) / "ZaloPay_daily_report_2026-03-10.md"
day10.write_text("báo cáo giả\n", encoding="utf-8")
delivered = []
saved = (g.run_checked, g.LEGACY_EMAIL_STATE, g._check_nav_flow_records, g.cash_flow_warnings)
g.run_checked = lambda cmd: delivered.append(Path(cmd[1] if cmd[0] == sys.executable else cmd[0]).name)
g.LEGACY_EMAIL_STATE = Path(tmp) / "legacy_email.json"
g._check_nav_flow_records = lambda r: None
g.cash_flow_warnings = lambda r: saved[3](r, **wd.paths)
sys.modules["cash_identity"] = None
err, out = io.StringIO(), io.StringIO()
try:
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
        rc = g.deliver(day10, Path(tmp) / "state.json", "trading_report", Path(tmp) / "notify", Path(tmp) / "email")
finally:
    sys.modules["cash_identity"] = ci
    g.run_checked, g.LEGACY_EMAIL_STATE, g._check_nav_flow_records, g.cash_flow_warnings = saved
print(f"deliver() rc={rc}; các bước đã chạy: {delivered}")
print("stdout:", out.getvalue().strip())
print("stderr:", err.getvalue().strip())

print("=" * 20, "NGHIỆM THU 6 — một bản ghi dnse_raw sai kiểu ở ngày 05/03 (có khoản rút 5tr chưa khai ngày 11/03)")
no = sc.ACCOUNTS["SpaceX"]
bad = {
    "payload là list": json.dumps({"ts": "2026-03-05T10:00:00", "kind": "orders", "account_no": no, "payload": [1, 2]}),
    "fillQuantity 'abc'": json.dumps({"ts": "2026-03-05T10:00:00", "kind": "orders", "account_no": no, "payload": {"orders": [
        {"id": 9, "accountNo": no, "symbol": "AAA", "side": "NS", "fillQuantity": "abc", "averagePrice": 10000.0,
         "modifiedDate": "2026-03-05T03:00:00.000000000Z"}]}}),
    "dòng JSON hỏng": '{"ts": "2026-03-05T10:00:00", "kind": "orders", "account_no": "' + no + '", "payload": {',
}
for label, line in bad.items():
    w = sc.World(tmp, "demo6").add("SpaceX", sc.at(11, "10:00"), "external", -5_000_000)
    w.raw_lines[D(2026, 3, 5)] = [line]
    w.build()
    res = w.check("SpaceX")
    print(f"--- {label}")
    print(f"    cửa sổ kiểm được: {sum(1 for x in res['windows'] if x['checkable'])}/{len(res['windows'])}; "
          f"không kiểm được (kết thúc ngày): {[x['date1'].isoformat() for x in res['windows'] if not x['checkable']]}; "
          f"cửa sổ mở: {[x['date1'].isoformat() for x in res['suspects']]}")
    for text in ci.warning_lines("SpaceX", **w.paths):
        if "không kiểm được" in text:
            print("    " + text.replace(str(w.dir), "<tmp>"))
