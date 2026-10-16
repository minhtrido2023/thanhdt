#!/usr/bin/env python3
"""Nghiệm thu 4: CLI tỉ suất thoát rc≠0 ⇒ báo cáo có qua cổng tỉ suất không? Chạy với bin của master
(đỏ) rồi bin của nhánh (xanh). CLI được thay bằng hàm giả — không đọc dữ liệu nào.
Dùng: python3 4_gate_rc.py <bin>"""
import contextlib, io, pathlib, subprocess, sys, tempfile
sys.path.insert(0, sys.argv[1])
with contextlib.redirect_stderr(io.StringIO()):
    import report_delivery_gate as g
report = pathlib.Path(tempfile.mkdtemp()) / "SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"
report.write_text("### 3.2 Hiệu suất lũy kế\n| Từ khi bắt đầu hoạt động (01/07 → 09/10) | −1,33% | x |\n", encoding="utf-8")
def rc1(cmd, **kw):
    raise subprocess.CalledProcessError(1, cmd, output="", stderr="LỖI nav_period_returns: thiếu time_ict")
g.subprocess.run = rc1
err = io.StringIO()
try:
    with contextlib.redirect_stderr(err):
        g._check_period_returns(report)
    print(f"ĐỎ — báo cáo QUA cổng dù CLI rc=1 (fail-open). Cổng chỉ in: {err.getvalue().strip()[:200]}")
    sys.exit(1)
except RuntimeError as exc:
    print(f"XANH — báo cáo KHÔNG qua cổng khi CLI rc=1: {str(exc)[:260]}")
