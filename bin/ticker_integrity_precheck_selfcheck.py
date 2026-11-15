#!/usr/bin/env python3
"""Selfcheck cho ticker_integrity_precheck.py + khối [0b] của daily_refresh_v34b_linux.sh.
Không chạm BQ thật (bq giả qua TI_BQ_BIN), không notify thật. Có mutant: mỗi mutant PHẢI làm
ít nhất 1 case đỏ, nếu không selfcheck tự đỏ (bằng chứng test thật sự cắn).
Chạy: env -u TZ python3 ...; TZ=Pacific/Kiritimati python3 ...  (không dùng đồng hồ máy)."""
import importlib.util, os, re, stat, subprocess, sys, tempfile
from pathlib import Path

BIN = Path(__file__).resolve().parent
SRC = BIN / "ticker_integrity_precheck.py"
SH = Path(os.environ.get("TI_SH", "/home/trido/thanhdt/WorkingClaude/daily_refresh_v34b_linux.sh"))
OK = BAD = 0

def chk(name, cond, detail=""):
    global OK, BAD
    if cond: OK += 1
    else:
        BAD += 1; print("  FAIL:", name, detail)

def load(path):
    spec = importlib.util.spec_from_file_location("ti_" + path.stem, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def pure_cases(m):
    """Trả list (name, passed) cho hàm lõi evaluate()."""
    D = ["2026-11-09","2026-11-10","2026-11-11","2026-11-12","2026-11-13"]
    n1m = {d: 800 for d in D}
    good = {d: (800, 1) for d in D}
    r = []
    r.append(("good=PASS", m.evaluate(n1m, good, {d: 1 for d in D}, {d: 0 for d in D}) == []))
    # incident 13/11: VNINDEX mất 4 phiên cuối, W-Y thiếu 13/11 (~503 dòng/5 phiên)
    inc = dict(good); inc["2026-11-13"] = (700, 1)
    for d in D[:4]: inc[d] = (700, 0)
    f = m.evaluate(n1m, inc, {d: 1 for d in D})
    r.append(("incident=FAIL", len(f) >= 5 and any("VNINDEX" in x for x in f)))
    # VNINDEX thủng Ở PHIÊN GIỮA, đếm đủ, MAX đúng: chỉ luật (c) bắt được
    mid = dict(good); mid["2026-11-11"] = (800, 0)
    vn1 = {d: 1 for d in D}
    r.append(("mid-hole-invisible-without-c", m.evaluate(n1m, mid) == []))
    r.append(("vnindex-mid-hole=FAIL", any("2026-11-11" in x and "VNINDEX" in x for x in m.evaluate(n1m, mid, vn1))))
    r.append(("vn1m-none-skips-c", m.evaluate(n1m, mid, None) == []))
    r.append(("vn-absent-both=PASS", m.evaluate(n1m, mid, {**vn1, "2026-11-11": 0}) == []))
    # chỉ VNINDEX thủng, đếm đủ
    vn = {d: (800, 0 if d == "2026-11-13" else 1) for d in D}
    r.append(("vnindex-lag-only=FAIL", any("VNINDEX" in x for x in m.evaluate(n1m, vn))))
    # chỉ đếm thủng 1 phiên (96% ⇒ FAIL), 97% đúng ngưỡng ⇒ PASS, VNINDEX còn
    c85 = dict(good); c85["2026-11-11"] = (680, 1)   # 85%
    c90 = dict(good); c90["2026-11-11"] = (720, 1)   # đúng 90,0% = biên PASS
    c899 = dict(good); c899["2026-11-11"] = (719, 1)
    r.append(("count-85pct=FAIL", len(m.evaluate(n1m, c85)) == 1))
    r.append(("count-90pct-boundary=PASS", m.evaluate(n1m, c90) == []))
    r.append(("count-89.9pct=FAIL", len(m.evaluate(n1m, c899)) == 1))
    # hồi quy hình dạng thật 10-26: thiếu ~5% đuôi kém thanh khoản, 0 mã prune thiếu ⇒ PASS
    nat = dict(good); nat["2026-11-11"] = (760, 1)    # 95,0%
    r.append(("natural-tail-5pct-liq0=PASS", m.evaluate(n1m, nat, {d: 1 for d in D}, {d: 0 for d in D}) == []))
    L = {d: 0 for d in D}
    r.append(("liq-missing-2=PASS", m.evaluate(n1m, good, None, {**L, "2026-11-11": 2}) == []))
    r.append(("liq-missing-3=FAIL", len(m.evaluate(n1m, good, None, {**L, "2026-11-11": 3})) == 1))
    # phiên vắng hẳn trong ticker ⇒ FAIL
    miss = {d: v for d, v in good.items() if d != "2026-11-12"}
    r.append(("session-absent=FAIL", any("2026-11-12" in x for x in m.evaluate(n1m, miss))))
    # ticker nhiều hơn (dòng trùng VNH) ⇒ không FAIL
    dup = dict(good); dup["2026-11-13"] = (801, 1)
    r.append(("extra-dup-rows=PASS", m.evaluate(n1m, dup) == []))
    # ticker trống
    r.append(("raw-empty=FAIL", len(m.evaluate(n1m, {})) >= 1))
    try:
        m.evaluate({}, good); r.append(("empty-1m=raises", False))
    except m.MeasureError:
        r.append(("empty-1m=raises", True))
    return r

def unexpected_rc(m):
    """measure() nổ RuntimeError (lỗi của chính precheck) ⇒ main() phải trả 2, không phải traceback rc1."""
    def boom(): raise RuntimeError("injected")
    m.measure = boom
    return m.main()

def stub_bq(d, mode):
    """bq giả: dry_run ⇒ dòng ước phí; query ⇒ CSV theo mode."""
    p = Path(d) / "bq"
    p.write_text(f'''#!/usr/bin/env bash
mode="{mode}"
for a in "$@"; do [ "$a" = "--dry_run" ] && {{ echo "validated, upper bound 1 bytes"; [ "$mode" = dryfail ] && {{ echo boom >&2; exit 1; }}; exit 0; }}; done
[ "$mode" = fail ] && {{ echo "Access Denied" >&2; exit 1; }}
[ "$mode" = garbage ] && {{ echo "not,csv,at,all"; echo "x"; exit 0; }}
[ "$mode" = crashtext ] && {{ echo ""; exit 0; }}
q="${{@: -1}}"
if [[ "$q" == *ticker_prune* ]]; then
  [ "$mode" = holed ] && {{ echo "d,n"; for d in 2026-11-09 2026-11-10 2026-11-11 2026-11-12 2026-11-13; do echo "$d,120"; done; }}
  [ "$mode" = liqnone ] && exit 0
  exit 0
elif [[ "$q" == *ticker_1m* ]]; then
  echo "d,n,v"; for d in 2026-11-13 2026-11-12 2026-11-11 2026-11-10 2026-11-09; do echo "$d,800,1"; done
else
  [ "$mode" = emptyraw ] && exit 0
  echo "d,n,v"
  for d in 2026-11-09 2026-11-10 2026-11-11 2026-11-12 2026-11-13; do
    if [ "$mode" = holed ]; then echo "$d,700,0"; else echo "$d,800,1"; fi
  done
fi
''')
    p.chmod(p.stat().st_mode | stat.S_IEXEC); return p

def run_cli(mode):
    with tempfile.TemporaryDirectory() as d:
        stub_bq(d, mode)
        env = dict(os.environ, TI_BQ_BIN=str(Path(d) / "bq"))
        return subprocess.run([sys.executable, str(SRC)], env=env, capture_output=True, text=True).returncode

def extract_block():
    s = SH.read_text()
    m = re.search(r"# TI-PRECHECK-BEGIN\n(.*?)# TI-PRECHECK-END", s, re.S)
    assert m, "không thấy marker TI-PRECHECK trong daily_refresh"
    return m.group(1)

def run_block(block, seq):
    """seq = list rc trả lần lượt của precheck giả. Trả (rc_shell, stdout, sleeps, notified, events)."""
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "n").write_text("0")
        (d / "pre.sh").write_text('#!/usr/bin/env bash\nn=$(cat "%s/n"); echo $((n+1)) > "%s/n"\nrcs=(%s)\necho "stub precheck call $((n+1))"\n[ "${rcs[$n]:-${rcs[-1]}}" = 1 ] && echo "  - phiên X: ly do gia"\nexit ${rcs[$n]:-${rcs[-1]}}\n' % (d, d, " ".join(map(str, seq))))
        for nm in ("notify", "thread", "event"):
            (d / (nm + ".sh")).write_text('#!/usr/bin/env bash\necho "$@" >> "%s/%s.log"\n' % (d, nm))
        (d / "sleep").write_text('#!/usr/bin/env bash\necho "$@" >> "%s/sleep.log"\n' % d)
        for f in d.iterdir(): f.chmod(0o755)
        # pre.sh là bash, block gọi `python3 "$_TI_BIN"` ⇒ shim python3 để chạy stub
        (d / "python3").write_text('#!/usr/bin/env bash\nexec bash "$@"\n'); (d / "python3").chmod(0o755)
        harness = ('set -uo pipefail\nstep(){ echo "--- $* ---"; }\ndie(){ echo "DIE: $*"; exit 1; }\nLOG=data/x.log\n' + block + '\necho CHAIN_CONTINUES\n')
        env = dict(os.environ, PATH=f"{d}:{os.environ['PATH']}", TI_PRECHECK_BIN=str(d / "pre.sh"),
                   TI_NOTIFY_BIN=str(d / "notify.sh"), TI_NOTIFY_THREAD_BIN=str(d / "thread.sh"),
                   TI_EVENT_BIN=str(d / "event.sh"), TI_RETRY_SLEEP="600")
        r = subprocess.run(["bash", "-c", harness], env=env, capture_output=True, text=True)
        rd = lambda n: (d / n).read_text() if (d / n).exists() else ""
        return r.returncode, r.stdout, rd("sleep.log"), rd("notify.log") + rd("thread.log"), rd("event.log"), int(rd("n"))

def block_cases(block):
    r = []
    rc, out, sl, nt, ev, n = run_block(block, [0])
    r.append(("blk rc0: chạy 1 lần, chain tiếp tục", rc == 0 and n == 1 and "CHAIN_CONTINUES" in out and nt == ""))
    rc, out, sl, nt, ev, n = run_block(block, [1, 1, 1])
    r.append(("blk rc1 x3: 3 lần, 2 sleep 600, die, notify+thread+event, KHÔNG chain",
              rc == 1 and n == 3 and sl.count("600") == 2 and "DIE:" in out and "CHAIN_CONTINUES" not in out
              and nt.count("THỦNG") == 2 and "ticker-integrity-precheck-fail" in ev))
    rc, out, sl, nt, ev, n = run_block(block, [1, 0])
    r.append(("blk rc1 rồi 0: hồi phục, 1 sleep, không notify, chain tiếp tục", rc == 0 and n == 2 and sl.count("600") == 1 and nt == "" and "CHAIN_CONTINUES" in out))
    for bad in (2, 127, 3):
        rc, out, sl, nt, ev, n = run_block(block, [bad])
        r.append((f"blk rc{bad}: fail-open, WARN, không retry, không notify, CÓ bus status, chain tiếp tục",
                  rc == 0 and n == 1 and "WARN" in out and nt == "" and "ticker-integrity-precheck-unmeasurable" in ev and "CHAIN_CONTINUES" in out))
    rc, out, sl, nt, ev, n = run_block(block, [1, 1, 1])
    r.append(("blk FAIL: LOG tuyệt đối trong alert+payload, kèm lý do", "/x.log" in nt and '"log":"/' in ev and "LÝ DO" in nt))
    return r

def mutate(src, a, b):
    assert src.count(a) == 1, f"mutant anchor không duy nhất: {a!r}"
    return src.replace(a, b)

def main():
    real = load(SRC)
    for n, ok in pure_cases(real): chk("pure " + n, ok)
    chk("unexpected exception ⇒ rc2", unexpected_rc(load(SRC)) == 2)
    chk("cli PASS rc0", run_cli("good") == 0)
    chk("cli hole rc1", run_cli("holed") == 1)
    chk("cli ticker trống cả cửa sổ ⇒ rc1 (FAIL, không fail-open)", run_cli("emptyraw") == 1)
    for mode in ("fail", "garbage", "dryfail", "crashtext"):
        chk(f"cli bq={mode} rc2 (fail-open)", run_cli(mode) == 2)
    with tempfile.TemporaryDirectory() as d:  # bq không tồn tại ⇒ 2
        env = dict(os.environ, TI_BQ_BIN=str(Path(d) / "nope"))
        chk("cli bq-missing rc2", subprocess.run([sys.executable, str(SRC)], env=env, capture_output=True).returncode == 2)
    block = extract_block()
    for n, ok in block_cases(block): chk(n, ok)

    # ---- mutants ----
    src = SRC.read_text()
    py_mutants = {
        "M1 ngưỡng 0.90→0.50": ("MIN_RATIO = 0.90 ", "MIN_RATIO = 0.50 "),
        "M7 MAX_LIQ_MISSING 2→200": ("MAX_LIQ_MISSING = 2 ", "MAX_LIQ_MISSING = 200 "),
        "M8 bỏ nhánh liq_missing": ("if liq_missing[d] > MAX_LIQ_MISSING:", "if False:"),
        "M9 MIN_RATIO về 0.97 (FP thật 10-26)": ("MIN_RATIO = 0.90 ", "MIN_RATIO = 0.97 "),
        "M2 bỏ check VNINDEX (vn_max<raw_max→False)": ("elif vn_max is None or vn_max < raw_max:", "elif False:"),
        "M3 so < thành <= (biên 90% đúng)": ("if n_raw < MIN_RATIO * n1m[d]:", "if n_raw <= MIN_RATIO * n1m[d]:"),
        "M6 bỏ luật (c)": ("if vn1m[d] > 0 and raw.get(d, (0, 0))[1] == 0:", "if False:"),
        "M5 except Exception bị thu hẹp": ("    except Exception as e:", "    except KeyError as e:"),
        "M4 phiên vắng không tính (.get default = n1m)": ("raw.get(d, (0, 0))[0]\n        if n_raw", "raw.get(d, (n1m[d], 0))[0]\n        if n_raw"),
    }
    for name, (a, b) in py_mutants.items():
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ticker_integrity_precheck.py"; p.write_text(mutate(src, a, b))
            mm = load(p)
            try: u = unexpected_rc(mm) == 2
            except RuntimeError: u = False
            killed = (not u) or any(not ok for _, ok in pure_cases(mm))
        chk("mutant killed: " + name, killed)
    # Mutant bash
    bmut = {
        "B1 rc1 không retry (break luôn)": ('[ "$_ti_rc" = 1 ] || break', 'break'),
        "B2 FAIL không die": ('  die "ticker integrity precheck FAILED', '  true "ticker integrity precheck FAILED'),
        "B3 rc lạ bị coi FAIL (fail-closed)": ('if [ "$_ti_rc" != 0 ] && [ "$_ti_rc" != 1 ]; then', 'if false; then'),
        "B4 mặc định _ti_rc=2→0 vô nghĩa nhưng retry=1 lần": ("for _ti_try in 1 2 3; do", "for _ti_try in 1; do"),
    }
    for name, (a, b) in bmut.items():
        mb = mutate(block, a, b)
        killed = any(not ok for _, ok in block_cases(mb))
        chk("mutant killed: " + name, killed)

    print(f"ticker_integrity_precheck selfcheck: {OK} PASS, {BAD} FAIL, TZ={os.environ.get('TZ','<unset>')}")
    return 1 if BAD else 0

if __name__ == "__main__":
    sys.exit(main())
