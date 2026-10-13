#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bctc_q3_chain_wiring_selfcheck.py — kiểm 2 khối nối vào chuỗi 19:00 (bin/bq_freshness_check.sh)
ngày 2026-10-13 (job Taylor_20261013_125149):
  · [pipeline-1d] refresh_earnings_surprise_pkl — WARN-only, có timeout, chạy TRƯỚC golive
  · PNJ BCTC Q3 review-trigger watch            — WARN-only, không đếm WARNED, không chặn

Trích NGUYÊN VĂN 2 khối từ file thật (theo mốc comment) rồi chạy trong sandbox với stub
`refresh_earnings_surprise_pkl.py` / `pnj_q3_review_watch.py` / `notify_thread.sh` — không BQ,
không Discord, không đụng pkl thật. `CHAIN_TARGET=<file>` cho mutation test.
"""
import os
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.environ.get("CHAIN_TARGET") or os.path.join(HERE, "bq_freshness_check.sh"))
SRC = open(TARGET, encoding="utf-8").read()
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  PASS  {name}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  {detail}")


def cut(a, b):
    i = SRC.find(a); j = SRC.find(b, i + 1) if i >= 0 else -1
    return SRC[i:j] if 0 <= i < j else None


A_PKL, B_PKL = "# [pipeline-1d] làm mới data/earnings_surprise_data.pkl", '_run_pipeline "[pipeline-2] golive_recommend_v23"'
A_PNJ, B_PNJ = "# --- PNJ BCTC Q3 review-trigger watch", '[ "$WARNED" -gt 0 ] && echo "NOTE:'
PKL, PNJ = cut(A_PKL, B_PKL), cut(A_PNJ, B_PNJ)
check("0a trích được khối [pipeline-1d]", PKL is not None)
check("0b trích được khối PNJ watch", PNJ is not None)
if PKL is None or PNJ is None:
    print(f"  TỔNG: {PASS} PASS / {FAIL + 1} FAIL — file đã đổi cấu trúc, selfcheck này lỗi thời"); sys.exit(1)


def sandbox():
    d = tempfile.mkdtemp(prefix="chainw_")
    os.makedirs(os.path.join(d, "root", "bin")); os.makedirs(os.path.join(d, "work"))
    def put(rel, body):
        p = os.path.join(d, rel)
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR)
    put("root/bin/notify_thread.sh", '#!/usr/bin/env bash\nprintf "%s\\t%s\\n" "$2" "$1" >> "$SINK"\n')
    put("work/refresh_earnings_surprise_pkl.py",
        'import os, sys, time\ntime.sleep(float(os.environ.get("STUB_SLEEP", "0")))\n'
        'print(os.environ.get("STUB_OUT", "refresh_earnings_surprise_pkl: updated"))\nsys.exit(int(os.environ.get("STUB_RC", "0")))\n')
    put("root/bin/pnj_q3_review_watch.py",
        'import os, sys\nopen(os.environ["ARGS_SINK"], "a").write(" ".join(sys.argv[1:]) + "\\n")\n'
        'o = os.environ.get("STUB_OUT", "")\nif o: print(o)\nsys.exit(int(os.environ.get("STUB_RC", "0")))\n')
    return d


def run_block(block, env_extra, quiet="--quiet", pre=""):
    d = sandbox(); sink, args = os.path.join(d, "sink"), os.path.join(d, "args")
    script = (f'set -uo pipefail\nROOT="{d}/root"; PY="python3"; TODAY="2026-10-13"; NOW_ICT="19:00 ICT"\n'
              f'DISCORD_STALE_CHANNEL="trading_daily"; WARNED=0; FAILED=0; QUIET="{quiet}"\n'
              f'_run_pipeline() {{ echo "RAN $1"; }}\ncd "{d}/work"\n{pre}\n{block}\n'
              f'echo "AFTER_BLOCK WARNED=$WARNED FAILED=$FAILED"\n')
    env = dict(os.environ, SINK=sink, ARGS_SINK=args, **env_extra)
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=env, timeout=60)
    rd = lambda p: open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    return r, rd(sink), rd(args)


print("=" * 78); print("  1. [pipeline-1d] refresh_earnings_surprise_pkl"); print("=" * 78)
r, sink, _ = run_block(PKL, {"STUB_RC": "0", "STUB_OUT": "refresh_earnings_surprise_pkl: updated — 58233 → 58234 dòng"})
check("1a thành công → [ok], in dòng tóm tắt của script, KHÔNG notify, chuỗi đi tiếp",
      r.returncode == 0 and "[ok] [pipeline-1d]" in r.stdout and "58233 → 58234" in r.stdout and sink == ""
      and "AFTER_BLOCK" in r.stdout, r.stdout + r.stderr)
r, sink, _ = run_block(PKL, {"STUB_RC": "1", "STUB_OUT": "refresh_earnings_surprise_pkl: kept_old — co lại 58,233 → 100 dòng"})
check("1b script exit 1 → [WARN exit 1], chuỗi VẪN đi tiếp (không exit), FAILED không đổi",
      r.returncode == 0 and "[WARN exit 1] [pipeline-1d]" in r.stdout and "AFTER_BLOCK WARNED=0 FAILED=0" in r.stdout, r.stdout + r.stderr)
check("1c … đúng 1 notify tới trading_daily, mang LÝ DO THẬT từ output script (§29)",
      sink.count("\n") == 1 and sink.startswith("trading_daily\t") and "co lại 58,233 → 100 dòng" in sink
      and "exit 1" in sink and "Không chặn plan" in sink, sink)
r, sink, _ = run_block(PKL, {"STUB_SLEEP": "5", "LAG_PKL_REFRESH_TIMEOUT_S": "1"})
check("1d treo quá timeout → bị kill (rc 124), WARN nêu 'timeout 1s', chuỗi đi tiếp",
      r.returncode == 0 and "[WARN exit 124]" in r.stdout and "timeout 1s" in sink and "AFTER_BLOCK" in r.stdout, r.stdout + sink)
r, sink, _ = run_block(PKL, {"STUB_RC": "0"}, pre="unset LAG_PKL_REFRESH_TIMEOUT_S")
check("1e timeout mặc định = 90s khi không override", 'LAG_PKL_REFRESH_TIMEOUT_S="${LAG_PKL_REFRESH_TIMEOUT_S:-90}"' in PKL and r.returncode == 0)
check("1f chạy bằng $PY (= $DNA_PYEXE, pandas 3), không phải python3 hệ thống",
      'timeout "$LAG_PKL_REFRESH_TIMEOUT_S" $PY refresh_earnings_surprise_pkl.py' in PKL and 'PY="${DNA_PYEXE:-python3}"' in SRC)
i1c, i1d, i2 = SRC.find("[pipeline-1c] build_universe_pit_quality"), SRC.find(A_PKL), SRC.find(B_PKL)
i_gate = SRC.find('echo "=== ALL FRESH — chạy EOD pipeline ==="')
check("1g thứ tự: sau cổng ALL FRESH và pipeline-1c, NGAY TRƯỚC pipeline-2 golive", 0 < i_gate < i1c < i1d < i2
      and not [l for l in SRC[i1d:i2].splitlines() if l.startswith("_run_pipeline ")], f"{i_gate} {i1c} {i1d} {i2}")
check("1h khối không chứa `exit` (không thể chặn plan)", "exit 1" not in PKL and "\nexit" not in PKL)

print("=" * 78); print("  2. PNJ BCTC Q3 review-trigger watch"); print("=" * 78)
r, sink, args = run_block(PNJ, {"STUB_RC": "0", "STUB_OUT": ""})
check("2a im lặng (script không in gì) → khối không in gì, WARNED không đổi, không notify từ wrapper",
      r.returncode == 0 and r.stdout.strip() == "AFTER_BLOCK WARNED=0 FAILED=0" and sink == "", r.stdout + r.stderr)
check("2b QUIET=--quiet được chuyển xuống script", args.strip() == "--quiet", args)
r, sink, args = run_block(PNJ, {"STUB_RC": "0", "STUB_OUT": "FIRED pnj-q3-watch: PNJ 2026Q3"}, quiet="")
check("2c script in FIRED → wrapper in lại nguyên văn; không --quiet khi QUIET rỗng",
      "FIRED pnj-q3-watch: PNJ 2026Q3" in r.stdout and args.strip() == "" and "AFTER_BLOCK WARNED=0" in r.stdout, r.stdout + args)
r, sink, _ = run_block(PNJ, {"STUB_RC": "3", "STUB_OUT": "Traceback: boom"})
check("2d script exit≠0 → [WARN] kèm output thật, chuỗi đi tiếp, WARNED/FAILED không đổi",
      r.returncode == 0 and "[WARN] pnj_q3_review_watch.py exit=3" in r.stdout and "Traceback: boom" in r.stdout
      and "AFTER_BLOCK WARNED=0 FAILED=0" in r.stdout, r.stdout + r.stderr)
check("2e có timeout, không có `exit`, không đụng WARNED/FAILED/excluded_tickers",
      "timeout 60 python3 bin/pnj_q3_review_watch.py" in PNJ and "exit 1" not in PNJ
      and PNJ.count("WARNED=$((") == 1 and PNJ.index("WARNED=$((") > PNJ.index("^ALERT pnj-q3-watch:")
      and "FAILED=" not in PNJ and "trading_bot_accounts" not in PNJ)
r, sink, _ = run_block(PNJ, {"STUB_RC": "0", "STUB_OUT": "WARN pnj-q3-watch: KHÔNG đọc được state — lỗi thật: boom\nALERT pnj-q3-watch: state_unreadable — watcher KHÔNG hoạt động đúng"})
check("2g dòng ALERT (state/bus hỏng) → notify Discord trading_daily mang lỗi thật + WARNED=1, vẫn không chặn chuỗi",
      r.returncode == 0 and sink.startswith("trading_daily\t") and "boom" in sink and "AFTER_BLOCK WARNED=1 FAILED=0" in r.stdout, r.stdout + sink)
r, sink, _ = run_block(PNJ, {"STUB_RC": "0", "STUB_OUT": "OK   pnj-q3-watch: not_yet (PNJ 2026Q3)"})
check("2h không ALERT → KHÔNG notify, WARNED=0", sink == "" and "AFTER_BLOCK WARNED=0 FAILED=0" in r.stdout, r.stdout + sink)
i_pnj, i_failed = SRC.find(A_PNJ), SRC.find('if [ "$FAILED" -ne 0 ]; then')
check("2f đặt TRƯỚC cổng FAILED/exit (ngày BQ stale vẫn canh được PNJ)", 0 < i_pnj < i_failed, f"{i_pnj} {i_failed}")

print("=" * 78)
print(f"  TỔNG: {PASS} PASS / {FAIL} FAIL   (target={TARGET})")
sys.exit(1 if FAIL else 0)
