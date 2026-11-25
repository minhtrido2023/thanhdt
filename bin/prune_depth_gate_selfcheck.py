#!/usr/bin/env python3
"""Selfcheck bin/prune_depth_gate.py (arch-review vòng 2 việc B #6 + mutation, 25/11/2026).
Không gọi BQ thật: decide() trực tiếp + main() với `bq` giả trên PATH (đường query_counts).
Mỗi ca ghi rõ mutation nó giết."""
import datetime as dt
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = Path(os.environ.get("PDG_TARGET", HERE / "prune_depth_gate.py"))
sys.path.insert(0, str(TARGET.parent))
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("pdg", TARGET)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

FAILS = 0
# 20 phiên THẬT trước 23/11/2026 (BQ ticker_prune, đo 25/11) — trung vị 203 ⇒ ngưỡng 183.
REAL = [205, 205, 205, 204, 204, 204, 204, 203, 203, 203, 203, 203, 202, 202, 202, 202, 201, 201, 201, 197]


def chk(cond, name, out=""):
    global FAILS
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS += 1
        print("   output:", out)


def v(n, prior):
    verdict, info = P.decide(n, prior)
    return verdict, info


def run_cli(rows, date_arg=None):
    """rows=[(date, n)] ⇒ bq giả in CSV; chạy main() thật qua subprocess."""
    td = Path(tempfile.mkdtemp(prefix="pdg_sc_"))
    csv = "dt,n\\n" + "".join(f"{d},{n}\\n" for d, n in rows)
    (td / "bq").write_text(f'#!/bin/bash\nprintf "{csv}"\n')
    (td / "bq").chmod(0o755)
    args = ["--date", date_arg] if date_arg else ["--latest"]
    r = subprocess.run([sys.executable, str(TARGET)] + args, capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, PATH=f"{td}:{os.environ['PATH']}"))
    return r.returncode, r.stdout + r.stderr


def days(n, start="2026-08-01"):
    d0 = dt.date.fromisoformat(start)
    return [str(d0 + dt.timedelta(days=i)) for i in range(n)]


def main():
    vd, info = v(197, REAL)
    chk(vd == "PASS" and info["threshold"] == 183, "T1 ca thật 23/11: 197 vs trung vị 203 ⇒ ngưỡng 183, QUA", info)
    vd, info = v(183, REAL)
    chk(vd == "PASS", "T2 biên n == ngưỡng (183) ⇒ QUA  [giết: >= → >]", info)
    vd, info = v(182, REAL)
    chk(vd == "FAIL", "T2b 182 = ngưỡng−1 ⇒ CHẶN", info)
    # T3 (#6): universe 202 rồi chuỗi ghi thiếu 170 kéo dài — MỌI phiên trong chuỗi 1..40 PHẢI vẫn chặn
    base = [202] * 30
    bad = [k for k in range(1, 41) if v(170, base + [170] * (k - 1))[0] != "FAIL"]
    chk(not bad, "T3 chuỗi ghi thiếu 170 sau universe 202: phiên thứ 1..40 của chuỗi ĐỀU chặn (trước: phiên 11 tự qua)",
        f"phiên tự qua: {bad[:5]}")
    vd, info = v(170, base + [170] * 14)
    chk(vd == "FAIL" and info["threshold"] == 182 and info["dropped"] == 14,
        "T3b phiên thứ 15: ngưỡng vẫn 182 (trung vị 202), 14 phiên FAIL bị loại khỏi trung vị, dòng in nêu rõ", info)
    chk("loại_khỏi_trung_vị=14" in P.fmt(vd, "x", info), "T3c fmt nêu số phiên bị loại", P.fmt(vd, "x", info))
    vd, info = v(201, base + [170] * 14)
    chk(vd == "PASS", "T3d hết chuỗi, số mã về 201 ⇒ QUA (không kẹt vĩnh viễn khi dữ liệu hồi)", info)
    # T4 phân bố lệch: 15×200 + 5×400 ⇒ trung vị 200 (ngưỡng 180) ≠ trung bình 250 (ngưỡng 225)
    vd, info = v(200, [200] * 8 + [400] * 5 + [200] * 7)
    chk(vd == "PASS" and info["threshold"] == 180, "T4 phân bố lệch: trung vị (không phải trung bình)  [giết: median → mean]", info)
    # T5 >20 phiên lịch sử, trôi chậm: 20×260 rồi 20×240 ⇒ cửa sổ = 20 phiên GẦN NHẤT (ngưỡng 216), không phải 20 đầu (234)
    vd, info = v(220, [260] * 20 + [240] * 20)
    chk(vd == "PASS" and info["threshold"] == 216, "T5 cửa sổ = 20 phiên mới nhất  [giết: [-window:] → [:window]]", info)
    # T6 lọc sàn hạt giống (thay lọc >0): 12 phiên 0/thiếu + 19 phiên thật ⇒ chỉ 19 hợp lệ ⇒ KHÔNG ĐO ĐƯỢC
    vd, info = v(200, [0] * 12 + [200] * 19)
    chk(vd == "UNMEASURABLE", "T6 phiên 0 mã không tính là lịch sử  [giết: bỏ lọc sàn/>0 hạt giống]", info)
    vd, info = v(200, [0] * 12 + [200] * 20)
    chk(vd == "PASS", "T6b đủ 20 phiên thật ⇒ đo được", info)
    # T7 đường query_counts: 19 phiên trước + chính ngày xét ⇒ ngày xét KHÔNG được tính vào lịch sử
    ds = days(20)
    rc, out = run_cli([(d, 200) for d in ds[:19]] + [(ds[19], 200)])
    chk(rc == 2 and "UNMEASURABLE" in out and "19/20" in out,
        "T7 --latest: 19 phiên trước + ngày xét ⇒ KHÔNG ĐO ĐƯỢC (ngày xét không vào prior)  [giết: d < date → <=]", out)
    rc, out = run_cli([(d, 203) for d in days(21)[:20]] + [(days(21)[20], 183)])
    chk(rc == 0 and "PRUNE_DEPTH PASS" in out and "threshold=183" in out, "T7b --latest 20 phiên trước ⇒ QUA rc=0", out)
    rc, out = run_cli([(d, 203) for d in days(20)], date_arg="2026-08-21")
    chk(rc == 1 and "n=0" in out, "T7c --date ngày CHƯA ingest ⇒ n=0 ⇒ CHẶN rc=1", out)
    rc, out = run_cli([(d, 202) for d in days(30)] + [(d, 170) for d in days(45)[30:]])
    chk(rc == 1 and "PRUNE_DEPTH FAIL" in out and "n=170" in out,
        "T7d --latest chuỗi 15 phiên ghi thiếu qua đường BQ ⇒ vẫn CHẶN rc=1", out)


if __name__ == "__main__":
    main()
    print(f"prune_depth_gate_selfcheck: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
    sys.exit(1 if FAILS else 0)
