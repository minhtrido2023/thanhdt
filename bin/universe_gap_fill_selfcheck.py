#!/usr/bin/env python3
"""universe_gap_fill_selfcheck.py — selfcheck cho bin/universe_gap_fill.py (+ wiring trong bq_freshness_check.sh).

Ca gốc: 2026-10-15 universe_pit thiếu phiên 14/10 ⇒ golive assert_universe_covers dừng cả plan.
Không chạm BQ: `_load`/`_run` được thay bằng stub. Chạy dưới `env -u TZ` và TZ lạ — chỉ dùng date.
"""
import datetime as dt
import importlib.util
import io
import os
import re
import sys
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ugf", os.path.join(HERE, "universe_gap_fill.py"))
ugf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ugf)

D = dt.date
PASS = FAIL = 0


def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} {extra}")


def sessions(start, n, rows=750):
    out, d = {}, start
    while len(out) < n:
        if d.weekday() < 5:
            out[d] = rows
        d += dt.timedelta(days=1)
    return out


# ── hàm thuần ───────────────────────────────────────────────────────────────
today = D(2026, 10, 15)
src = sessions(D(2026, 9, 21), 18)            # 21/9 .. 14/10 (18 phiên T2-T6)
src[today] = 781
pit = {d for d in src if d != D(2026, 10, 14)}
g, s = ugf.find_gap_dates(src, pit, today)
check("ca 15/10: thiếu đúng 14/10", g == [D(2026, 10, 14)] and s == [], f"got {g} {s}")
check("hôm nay KHÔNG bao giờ nằm trong gaps", today not in ugf.find_gap_dates(src, set(), today)[0])

g, _ = ugf.find_gap_dates(src, set(src), today)
check("đủ phiên ⇒ không gap", g == [])
check("src rỗng ⇒ không gap", ugf.find_gap_dates({}, set(), today) == ([], []))

pit2 = {d for d in src if d not in (D(2026, 10, 12), D(2026, 10, 14))}
g, _ = ugf.find_gap_dates(src, pit2, today)
check("nhiều gap trả TĂNG DẦN", g == [D(2026, 10, 12), D(2026, 10, 14)], f"got {g}")

stub_src = dict(src)
stub_src[D(2026, 10, 14)] = 1                 # stub 1 dòng như 2026-07-22 (DRL)
g, s = ugf.find_gap_dates(stub_src, {d for d in stub_src if d != D(2026, 10, 14)}, today)
check("stub 1 dòng KHÔNG vào gaps, vào stubs", g == [] and s == [D(2026, 10, 14)], f"got {g} {s}")

old = dict(src)
old[D(2026, 8, 3)] = 750                      # ngoài cửa sổ 30 ngày
g, _ = ugf.find_gap_dates(old, set(src), today)
check("phiên thiếu NGOÀI cửa sổ lookback bị bỏ qua", D(2026, 8, 3) not in g)

# ── orchestration (stub _load/_run) ─────────────────────────────────────────
calls = []


def run_main(argv, load, rc_map=None):
    calls.clear()
    ugf._load = lambda t: load
    ugf._run = lambda script, day: (calls.append((script, day)) or (rc_map or {}).get((script, day), 0))
    old_argv = sys.argv
    sys.argv = ["x"] + argv
    out, err = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(out), redirect_stderr(err):
            rc = ugf.main()
    finally:
        sys.argv = old_argv
    return rc, out.getvalue(), err.getvalue()


load = (src, pit)
rc, out, _ = run_main(["--today", "2026-10-15"], load)
check("lấp 14/10: rc=0 + gọi pit rồi quality đúng thứ tự",
      rc == 0 and calls == [("build_universe_pit.py", D(2026, 10, 14)),
                            ("build_universe_pit_quality.py", D(2026, 10, 14))], f"{rc} {calls}")

rc, _, _ = run_main(["--today", "2026-10-15", "--dry-run"], load)
check("dry-run: rc=0 và KHÔNG gọi builder", rc == 0 and calls == [], f"{rc} {calls}")

rc, _, _ = run_main(["--today", "2026-10-15"], (src, set(src)))
check("không thiếu: rc=0 không gọi builder", rc == 0 and calls == [])

many = {d for d in src if d < D(2026, 10, 1)}   # thiếu từ 1/10 → 14/10 = 10 phiên > MAX_GAPS
rc, _, err = run_main(["--today", "2026-10-15"], (src, many))
check("thiếu > MAX_GAPS: rc=4, KHÔNG build gì", rc == 4 and calls == [], f"{rc} {calls}")

pit3 = {d for d in src if d not in (D(2026, 10, 13), D(2026, 10, 14))}
rc, _, err = run_main(["--today", "2026-10-15"], (src, pit3),
                      {("build_universe_pit.py", D(2026, 10, 13)): 1})
check("build lỗi: rc=1 và DỪNG, không build phiên sau (giữ thứ tự)",
      rc == 1 and calls == [("build_universe_pit.py", D(2026, 10, 13))], f"{rc} {calls}")

rc, _, _ = run_main(["--today", "2026-10-15"], (src, pit3),
                    {("build_universe_pit_quality.py", D(2026, 10, 13)): 1})
check("quality lỗi cũng rc=1 và dừng",
      rc == 1 and ("build_universe_pit.py", D(2026, 10, 14)) not in calls, f"{rc} {calls}")


# N3: dict đầu vào XÁO THỨ TỰ — production _load GROUP BY không ORDER BY ⇒ phải tự sort
shuf = dict(reversed(list(src.items())))
g, _ = ugf.find_gap_dates(shuf, pit2, today)
check("input dict đảo thứ tự vẫn trả gaps TĂNG DẦN (bắt thiếu sorted)",
      g == [D(2026, 10, 12), D(2026, 10, 14)], f"got {g}")

# N3: biên len == MAX_GAPS (build hết) và MAX_GAPS+1 (từ chối)
five = sorted(d for d in src if d < today)[-ugf.MAX_GAPS:]
rc, _, _ = run_main(["--today", "2026-10-15"], (src, set(src) - set(five)))
check("đúng MAX_GAPS phiên: rc=0 và build đủ 2×MAX_GAPS lần",
      rc == 0 and len(calls) == 2 * ugf.MAX_GAPS, f"{rc} {len(calls)}")
six = sorted(d for d in src if d < today)[-(ugf.MAX_GAPS + 1):]
rc, _, _ = run_main(["--today", "2026-10-15"], (src, set(src) - set(six)))
check("MAX_GAPS+1 phiên: rc=4, không build", rc == 4 and calls == [], f"{rc} {calls}")

# N1: _load ném exception ⇒ rc=3 + nguyên nhân thật trên stderr (không nhập nhằng với build lỗi)
def boom(t):
    raise RuntimeError("403 quota exceeded")
calls.clear()
ugf._load = boom
ugf._run = lambda s_, d_: calls.append((s_, d_)) or 0
sys.argv = ["x", "--today", "2026-10-15"]
e = io.StringIO()
with redirect_stdout(io.StringIO()), redirect_stderr(e):
    rc = ugf.main()
check("_load lỗi ⇒ rc=3, stderr nêu nguyên nhân thật, không build",
      rc == 3 and "RuntimeError" in e.getvalue() and "403 quota exceeded" in e.getvalue() and calls == [],
      f"{rc} {e.getvalue()!r}")

# N6: ngưỡng stub không trôi so với builder (chép tay ⇒ phải có guard)
try:
    import build_universe_pit as _bup
    check("B8_RAW_DEPTH khớp build_universe_pit", ugf.B8_RAW_DEPTH == _bup.B8_RAW_DEPTH,
          f"{ugf.B8_RAW_DEPTH} != {_bup.B8_RAW_DEPTH}")
except ImportError as _ie:
    print(f"  SKIP B8_RAW_DEPTH drift guard (không import được builder: {_ie})")

# ── wiring trong bq_freshness_check.sh ──────────────────────────────────────
sh = open(os.path.join(HERE, "bq_freshness_check.sh"), encoding="utf-8").read()
i1a = sh.find("[pipeline-1a] universe gap-fill")
i1b = sh.find('echo; echo "--- [pipeline-1b] build_universe_pit')
ipub = sh.find('_run_pipeline "[pipeline-1] publish_gated_state"')
check("1a nằm SAU publish_gated_state và TRƯỚC 1b", 0 < ipub < i1a < i1b, f"{ipub} {i1a} {i1b}")
blk = sh[i1a:sh.find("# [pipeline-1b] build universe_pit")]
check("1a gọi universe_gap_fill.py --today \"$TODAY\" qua timeout",
      re.search(r'timeout "\$\{UNIVERSE_GAP_FILL_TIMEOUT_S:-\d+\}" \$PY mike/bin/universe_gap_fill\.py --today "\$TODAY"', blk) is not None)
check("N5: _gap_rc=$? đứng NGAY sau lệnh gọi (bắt '|| true' nuốt rc)",
      re.search(r'universe_gap_fill\.py --today "\$TODAY" 2>&1\)"\n_gap_rc=\$\?\n', blk) is not None)
check("không có '|| true' trên lệnh gọi gap-fill", "gap_fill.py --today \"$TODAY\" 2>&1)\" ||" not in blk)
check("1a WARN-only: không có exit/FAILED=1 trong khối", "exit 1" not in blk and "FAILED=1" not in blk)

print(f"\n{PASS} pass / {FAIL} fail")
sys.exit(1 if FAIL else 0)
