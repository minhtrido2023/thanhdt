#!/usr/bin/env python3
"""Selfcheck khối HOLIDAY + PRUNE-GATE (step [0]) của daily_refresh_v34b_linux.sh (2026-11-25).

Trích khối THẬT bằng marker HOLIDAY-BEGIN … PRUNE-GATE-END + dòng `[ "$ready" = 1 ] || die`, chạy với
cổng THẬT mike/bin/prune_depth_gate.py + `bq` giả trên PATH, lịch THẬT trading_bot.vn_market.
Phủ: ngày nghỉ 24/11 ⇒ 'NGÀY NGHỈ, BỎ QUA' exit 0 (as_of khớp / as_of cũ kèm lệnh khôi phục) ·
ca 23/11 197 mã ⇒ ready · partial-write 150 ⇒ die · thiếu lịch sử ⇒ die (fail-closed) · bq lỗi ⇒ die.
Env: DR_SH (file .sh cần test), WORKDIR_8L (gốc chứa trading_bot), PRUNE_GATE (đường dẫn cổng).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SH = Path(os.environ.get("DR_SH", HERE / "daily_refresh_v34b_linux.sh"))
WC = os.environ.get("WORKDIR_8L_TEST", str(HERE))
GATE = os.environ.get("PRUNE_GATE", "/home/trido/thanhdt/WorkingClaude/mike/bin/prune_depth_gate.py")
PRIOR = [("2026-10-26", 206), ("2026-10-27", 205), ("2026-10-28", 204), ("2026-10-29", 204),
         ("2026-10-30", 203), ("2026-11-02", 204), ("2026-11-03", 204), ("2026-11-04", 203),
         ("2026-11-05", 203), ("2026-11-06", 202), ("2026-11-09", 203), ("2026-11-10", 201),
         ("2026-11-11", 201), ("2026-11-12", 203), ("2026-11-13", 202), ("2026-11-16", 202),
         ("2026-11-17", 201), ("2026-11-18", 201), ("2026-11-19", 201), ("2026-11-20", 200)]
FAILS = 0


def block():
    lines = SH.read_text().splitlines()
    b = next(i for i, l in enumerate(lines) if l.startswith("# HOLIDAY-BEGIN"))
    e = next(i for i, l in enumerate(lines) if l.startswith("# PRUNE-GATE-END"))
    d = next(i for i, l in enumerate(lines) if l.startswith('[ "$ready" = 1 ] || die'))
    assert b < e < d, "marker sai thứ tự"
    return "\n".join(lines[b:e + 1] + [lines[d], 'echo "REACHED_COMPUTE"'])


def run(today, rows, bq_rc=0, asof="2026-11-23"):
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        (t / "fakebin").mkdir()
        (t / "fakebin" / "bq.out").write_text("dt,n\n" + "".join(f"{d},{n}\n" for d, n in rows))
        (t / "fakebin" / "bq").write_text(f'#!/bin/bash\necho "$*" >> "{t}/bq.calls"\ncat "{t}/fakebin/bq.out"\nexit {bq_rc}\n')
        (t / "fakebin" / "bq").chmod(0o755)
        (t / "deploy_golive_dt5g_v4").mkdir()
        (t / "deploy_golive_dt5g_v4" / "golive_state_today.json").write_text(f'{{"as_of": "{asof}"}}')
        script = ('die() { echo "DIE: $*"; exit 1; }\n'
                  f'export PATH="{t}/fakebin:$PATH"; WORKDIR_8L="{WC}"; PRUNE_DEPTH_GATE_BIN="{GATE}"; '
                  f'PRUNE_GATE_SLEEP_S=0; TODAY_ICT="{today}"; cd "{t}"\n' + block())
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=120)
        calls = (t / "bq.calls").read_text().count("\n") if (t / "bq.calls").exists() else 0
        return r.returncode, r.stdout + r.stderr, calls


def chk(name, cond, out):
    global FAILS
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS += 1
        print("   output:", out[-600:].replace("\n", " | "))


rc, out, calls = run("2026-11-24", PRIOR)
chk("ngày nghỉ 24/11 (as_of=23/11) ⇒ 'NGÀY NGHỈ, BỎ QUA', exit 0, không gọi BQ, không tới bước tính",
    rc == 0 and "NGÀY NGHỈ, BỎ QUA" in out and "is_holiday=True" in out and calls == 0
    and "REACHED_COMPUTE" not in out and "DIE" not in out, out)
rc, out, _ = run("2026-11-24", PRIOR, asof="2026-11-20")
chk("ngày nghỉ 24/11 nhưng as_of=20/11 cũ ⇒ vẫn exit 0 nhưng nói THẬT ≠ phiên 23/11 + lệnh khôi phục",
    rc == 0 and "as_of=2026-11-20 ≠ phiên gần nhất 2026-11-23" in out and "MIKE_MORNING_RUN=1" in out, out)
rc, out, _ = run("2026-11-23", PRIOR + [("2026-11-23", 197)])
chk("CA THẬT 23/11: 197 mã (ngưỡng 183) ⇒ ready, tới bước tính",
    rc == 0 and "ready: PRUNE_DEPTH PASS" in out and "REACHED_COMPUTE" in out, out)
rc, out, _ = run("2026-11-23", PRIOR + [("2026-11-23", 150)])
chk("partial-write 150 ⇒ 6 lần not ready rồi DIE (không tính)",
    rc == 1 and out.count("not ready yet (rc=1)") == 6 and "DIE:" in out and "last: PRUNE_DEPTH FAIL" in out
    and "REACHED_COMPUTE" not in out, out)
rc, out, _ = run("2026-11-23", PRIOR[-3:] + [("2026-11-23", 197)])
chk("thiếu lịch sử (3 phiên) ⇒ UNMEASURABLE rc=2 ⇒ DIE fail-closed",
    rc == 1 and "not ready yet (rc=2)" in out and "UNMEASURABLE" in out and "REACHED_COMPUTE" not in out, out)
rc, out, _ = run("2026-11-23", [], bq_rc=1)
chk("bq lỗi ⇒ rc=2 ⇒ DIE fail-closed, log nguyên nhân bq", rc == 1 and "bq rc=1" in out and "DIE:" in out, out)
rc, out, _ = run("2026-11-25", PRIOR + [("2026-11-23", 197)])
chk("25/11 (ngày giao dịch) chưa ingest ⇒ n=0 ⇒ chờ rồi DIE (không nhầm là ngày nghỉ)",
    rc == 1 and "NGÀY NGHỈ" not in out and "n=0" in out, out)
print(f"daily_refresh_prune_gate_selfcheck: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
sys.exit(1 if FAILS else 0)
