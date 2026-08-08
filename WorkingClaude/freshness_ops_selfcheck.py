#!/usr/bin/env python3
"""freshness_ops_selfcheck.py — pin trọn gói fix freshness/ops job Winston_20260711_043611.

Bao 3 fix production (regression-catcher — revert bất kỳ fix nào là selfcheck này đỏ):
  (A) bq_freshness_check.sh mở rộng 8 bảng (commit mike/7cf6a82) + artifact-mtime gate
      (mike/2f0187e): chạy BẢN THẬT của script trong sandbox (copy vào tmp ROOT, stub
      bq/notify/dispatch/PY qua đúng các đường script vốn cho phép: $ROOT/bin/*, PATH,
      DNA_PYEXE, WORKDIR_8L) — kiểm tra TỪNG bảng đúng ngưỡng ở cả 2 phía boundary
      (lag==max PASS, lag==max+1 FAIL/WARN), WARN không chặn pipeline + không Telegram,
      BLOCK chặn dispatch DollarBill, artifact stale chặn dispatch.
      Giới hạn chủ đích: stub bq trả thẳng gap_days — selfcheck pin logic GATE (ngưỡng/
      mode/routing), không pin SQL đo lag (đã verify bằng BQ thật lúc calibrate 07-11).
  (B) pt_8l_daily.sh + papertrade_daily.sh alert-on-fail (thanhdt/3f23c41): extract
      run()/notify_fails() TỪ FILE THẬT (awk — drift là extract fail) rồi test: 1 step
      fail → 1 alert gộp Telegram+Discord đúng chain/label; 0 fail → im lặng; nhiều fail
      → đếm đủ; notify chết → chain vẫn rc=0. Kèm static check các increment inline
      [6b]/[8] và lời gọi notify_fails cuối chain còn nguyên.
  (C) risk_monitor provenance gate §6 (mike/540d04c): chạy suite --test-provenance
      có sẵn trong file (sandbox tmp, dry-run) — pin cả 2 nhánh fail-safe: provenance
      tốt → HALT thật vẫn nổ; provenance xấu → alert + gắn cờ nhưng KHÔNG fail-open,
      KHÔNG bao giờ chặn HALT.

Chạy: python3 freshness_ops_selfcheck.py   (rc=0 khi tất cả PASS)
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

WC = Path("/home/trido/thanhdt/WorkingClaude")
MIKE = WC / "mike"
FRESHNESS_SH = MIKE / "bin" / "bq_freshness_check.sh"
RISK_MONITOR = MIKE / "agents" / "Spyros" / "risk_monitor.py"
CHAIN_SCRIPTS = {"pt_8l_daily": WC / "pt_8l_daily.sh",
                 "papertrade_daily": WC / "papertrade_daily.sh"}

PASSED = 0
FAILED = 0


def check(name: str, cond: bool, detail: str = ""):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  PASS  {name}")
    else:
        FAILED += 1
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))


# ---------------------------------------------------------------------------
# (A) bq_freshness_check.sh — sandbox
# ---------------------------------------------------------------------------

# Bảng → (key stub, ngưỡng max, mode) — phải khớp 1-1 với hằng trong bq_freshness_check.sh.
# Đổi ngưỡng trong script mà quên đổi ở đây = selfcheck đỏ = đúng ý (ngưỡng là calibrated
# constant, không được trôi âm thầm).
BLOCK_TABLES = {  # key: (max_lag, unit-string in trong output)
    "ticker_prune": (2, "trading"),
    "vnindex_5state_dt5g_live": (0, "trading"),   # MAX_STATE_LAG=0 — pin fix bug -le no-op
    "ticker_financial": (90, "calendar"),
    "ticker_1m": (2, "trading"),
    "shares_outstanding_live": (2, "trading"),
    "custom30v_8l": (98, "calendar"),
    "custom30_8l": (98, "calendar"),
}
WARN_TABLE_RR = ("risk_rating", 135)   # WARN-only (orphan)
LASTMOD_MAX = 4                        # _check_lastmod custom30v_8l / custom30_8l
FA_LASTMOD_MAX = 9                     # MAX_R8L_MOD_AGE / MAX_FA_MOD_AGE (fa_ratings*)


def _lastmod(**over):
    """Tuổi last-modified cho MỌI bảng writer-alive script thật đang kiểm.

    Bỏ sót một bảng ⇒ stub trả None ⇒ script fail-safe age=999 ⇒ WARN GIẢ, và mọi assert đếm
    WARN đổ theo. `fa_ratings_8l`/`fa_ratings` được thêm vào script sau khi selfcheck này ra
    đời — đó chính là 2 WARN giả làm S1/S3 đỏ ngày 2026-08-08.
    """
    base = {"custom30v_8l": LASTMOD_MAX, "custom30_8l": LASTMOD_MAX,
            "fa_ratings_8l": FA_LASTMOD_MAX, "fa_ratings": FA_LASTMOD_MAX}
    base.update(over)
    return base


BQ_STUB = r'''#!/usr/bin/env python3
import json, os, sys, time
conf = json.load(open(os.environ["FAKE_BQ_CONF"]))
args = sys.argv[1:]
if args and args[0] == "show":
    tbl = args[-1].split("tav2_bq.")[-1]
    age = conf.get("lastmod", {}).get(tbl)
    if age is None:
        print("{}")                       # metadata unreadable -> script phai fail-safe WARN
    else:
        ms = int((time.time() - age * 86400 - 3600) * 1000)
        print(json.dumps({"lastModifiedTime": str(ms)}))
    sys.exit(0)
q = " ".join(args)
# --- probe queries KHÔNG phải lag-check: phải khớp TRƯỚC vòng lặp bảng, vì cùng nhắc tên bảng.
# (thêm 2026-08-08 — script thật đã mọc thêm 3 probe này; sandbox thiếu stub nên chúng rơi vào
#  nhánh "gap_days" và sinh alert CHẶN giả, xem docstring §sandbox-drift.)
if "COUNT(DISTINCT t.ticker)" in q and "ticker_prune" in q:
    print("f0_"); print(conf.get("prune_names", 250)); sys.exit(0)      # depth check
if "AS n_cur" in q:                                                     # fin-breadth cohort
    print("n_cur,n_prev"); print("%d,%d" % tuple(conf.get("fin_breadth", [240, 250]))); sys.exit(0)
if "MAX(t.Release_Date)" in q:                                          # lag-pkl BQ reference
    print("f0_"); print(conf.get("bq_release_max", "2026-08-06")); sys.exit(0)
order = ["vnindex_5state_dt5g_live", "shares_outstanding_live", "ticker_financial",
         "ticker_prune", "ticker_1m", "custom30v_8l", "custom30_8l", "risk_rating",
         "fa_ratings_8l", "fa_ratings"]
for t in order:
    if "tav2_bq." + t in q:
        print("gap_days"); print(conf["lag"].get(t, 0)); sys.exit(0)
print("gap_days"); print(999)
'''

DT5G_WATCH_STUB = "#!/usr/bin/env python3\nimport sys; sys.exit(0)\n"

FAKE_PY = r'''#!/usr/bin/env bash
# stub cho DNA_PYEXE: pipeline step "chay ok"; FAKE_PY_TOUCH=1 = gia lap step ghi artifact.
# `-c` = probe earnings_surprise_data.pkl doc bang $DNA_PYEXE (khong phai buoc pipeline) ->
# tra ve mot ngay hop le, neu khong probe se bao WARN "khong doc duoc pkl".
if [ "${1:-}" = "-c" ]; then
  echo "${FAKE_PKL_RELEASE_MAX:-2026-08-06}"
  exit 0
fi
if [ "${FAKE_PY_TOUCH:-0}" = "1" ]; then
  mkdir -p "$WORKDIR_8L/deploy_golive_dt5g_v4/out"
  touch "$WORKDIR_8L/deploy_golive_dt5g_v4/golive_state_today.json"
  touch "$WORKDIR_8L/deploy_golive_dt5g_v4/out/golive_v23_recommendations_20990101.csv"
fi
exit 0
'''


def build_sandbox(tmp: Path) -> dict:
    root = tmp / "root"
    (root / "bin").mkdir(parents=True)
    fakebin = tmp / "fakebin"
    fakebin.mkdir()
    logs = tmp / "logs"
    logs.mkdir()
    workdir = tmp / "workdir"
    (workdir / "trading_bot").mkdir(parents=True)

    shutil.copy(FRESHNESS_SH, root / "bin" / "bq_freshness_check.sh")

    def w(p: Path, body: str, exe=True):
        p.write_text(body)
        if exe:
            p.chmod(0o755)

    w(fakebin / "bq", BQ_STUB)
    w(fakebin / "fakepy", FAKE_PY)
    w(root / "bin" / "notify.sh",
      '#!/usr/bin/env bash\necho "$*" >> "$FAKE_LOG_DIR/notify.log"\n')
    w(root / "bin" / "notify_thread.sh",
      '#!/usr/bin/env bash\necho "$1 || ${2:-}" >> "$FAKE_LOG_DIR/notify_thread.log"\n')
    w(root / "bin" / "dispatch.sh",
      '#!/usr/bin/env bash\necho "$*" >> "$FAKE_LOG_DIR/dispatch.log"\n')

    w(root / "bin" / "dt5g_writer_watch.py", DT5G_WATCH_STUB)

    (workdir / "trading_bot" / "__init__.py").write_text("")
    (workdir / "trading_bot" / "vn_market.py").write_text(
        "import datetime as dt\n"
        "def is_holiday(d):\n"          # cổng DT5G publisher-evidence import hàm này
        "    return False\n"
        "def next_trading_day(d):\n"
        "    n = d + dt.timedelta(days=1)\n"
        "    while n.weekday() >= 5:\n"
        "        n += dt.timedelta(days=1)\n"
        "    return n\n")
    (workdir / "trading_bot" / "config.py").write_text(
        "def live_dnse_labels():\n    return ['TestAcct']\n"
        "def load_config():\n    return {}\n"
        "def load_accounts(cfg):\n    return [{'label': 'TestAcct'}]\n")

    # --- file phụ trợ mà bản THẬT của script đọc; thiếu là sinh alert giả (xem docstring) ----
    (workdir / "data").mkdir(parents=True, exist_ok=True)
    (workdir / "data" / "vnindex_5state_dt5g_live.csv").write_text("time,state\n")
    (workdir / "data" / "lag_edge_health.csv").write_text("date,edge\n")
    # corp-action scanner: script đọc $WC_ROOT/data/... = thư mục CHA của $ROOT trong sandbox
    (root.parent / "data").mkdir(parents=True, exist_ok=True)
    (root.parent / "data" / "corp_action_backlog.json").write_text(
        json.dumps({"checked_at": datetime.now().isoformat()}))
    return {"root": root, "fakebin": fakebin, "logs": logs, "workdir": workdir}


def _write_dt5g_evidence(workdir: Path):
    """Bằng chứng publisher CỦA TA (cổng DT5G, 2026-07-31). Ghi TRƯỚC khi chạy script nên mtime
    < PIPELINE_START_EPOCH: cổng DT5G (chỉ đòi mtime cùng NGÀY) PASS, còn cổng artifact-fresh
    (đòi mtime ≥ lúc gate bắt đầu) chỉ PASS khi bước pipeline giả thật sự touch lại — đúng
    kịch bản S1 vs S4."""
    d = datetime.now().date()
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    out = workdir / "deploy_golive_dt5g_v4" / "out"
    out.mkdir(parents=True, exist_ok=True)
    sj = workdir / "deploy_golive_dt5g_v4" / "golive_state_today.json"
    cs = out / "golive_v23_recommendations_20990101.csv"
    sj.write_text(json.dumps({"as_of": str(d), "bq_publish_ok": True}))
    cs.write_text("ticker\n")
    # Lùi mtime 30s: sandbox (bq bị stub) chạy xong trong chưa tới 1 giây, mà
    # `_assert_fresh_artifact` so `stat -c %Y` (nguyên giây) với PIPELINE_START_EPOCH. Ghi ở
    # "now" thì mtime == gate-start ⇒ `-lt` sai ⇒ kịch bản S4 (artifact KHÔNG được ghi lại)
    # lọt thành PASS. Lùi vài giây làm thứ tự thời gian rõ ràng, không phụ thuộc tốc độ máy.
    old = datetime.now().timestamp() - 30
    for p in (sj, cs):
        os.utime(p, (old, old))


def run_gate(sb: dict, lag: dict, lastmod: dict, py_touch: bool):
    """Chạy bản sandbox của bq_freshness_check.sh với stub-config cho trước."""
    for f in sb["logs"].glob("*.log"):
        f.unlink()
    _write_dt5g_evidence(sb["workdir"])
    conf = sb["logs"] / "fake_bq_conf.json"
    conf.write_text(json.dumps({"lag": lag, "lastmod": lastmod}))
    env = dict(os.environ,
               PATH=f"{sb['fakebin']}:{os.environ['PATH']}",
               FAKE_BQ_CONF=str(conf),
               FAKE_LOG_DIR=str(sb["logs"]),
               WORKDIR_8L=str(sb["workdir"]),
               DNA_PYEXE=str(sb["fakebin"] / "fakepy"),
               FAKE_PY_TOUCH="1" if py_touch else "0")
    r = subprocess.run(["bash", str(sb["root"] / "bin" / "bq_freshness_check.sh")],
                       capture_output=True, text=True, env=env, timeout=120)
    logread = lambda n: ((sb["logs"] / n).read_text()
                         if (sb["logs"] / n).exists() else "")
    return (r.returncode, r.stdout + r.stderr,
            logread("notify.log"), logread("notify_thread.log"), logread("dispatch.log"))


def part_a():
    print("\n=== (A) bq_freshness_check.sh — ngưỡng 8 bảng + artifact gate (sandbox) ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        sb = build_sandbox(Path(tmpdir))
        at_max = {t: mx for t, (mx, _) in BLOCK_TABLES.items()}
        at_max[WARN_TABLE_RR[0]] = WARN_TABLE_RR[1]

        # --- S1: mọi bảng đúng tại boundary (lag == max) → ALL FRESH, dispatch chạy ---
        rc, out, ntf, thr, dsp = run_gate(
            sb, at_max, _lastmod(), py_touch=True)
        for t, (mx, unit) in BLOCK_TABLES.items():
            check(f"S1 boundary-PASS {t} (lag={mx}{unit}d ≤ {mx})",
                  bool(re.search(rf"OK   [^\n]*lag={mx}{unit}d \(≤{mx}\)", out))
                  and t in out, out[-800:])
        check(f"S1 boundary-PASS risk_rating (lag={WARN_TABLE_RR[1]} WARN-table vẫn OK)",
              "risk_rating" in out and "WARN risk_rating" not in out)
        check(f"S1 boundary-PASS writer-alive x2 (last-modified {LASTMOD_MAX}d ≤ {LASTMOD_MAX})",
              out.count(f"last-modified {LASTMOD_MAX}d trước (≤{LASTMOD_MAX})") == 2, out[-800:])
        check("S1 ALL FRESH → pipeline chạy + artifact fresh-ok x2",
              "ALL FRESH" in out and out.count("[fresh-ok]") == 2, out[-800:])
        check("S1 dispatch DollarBill được gọi (TestAcct)", "TestAcct" in dsp, dsp)
        check("S1 rc=0, không alert nào", rc == 0 and ntf == "" and "🟡" not in thr,
              f"rc={rc} ntf={ntf!r}")

        # --- S2: mọi bảng lag = max+1 → BLOCK fail hết, WARN đúng mode, chặn dispatch ---
        over = {t: mx + 1 for t, (mx, _) in BLOCK_TABLES.items()}
        over[WARN_TABLE_RR[0]] = WARN_TABLE_RR[1] + 1
        rc, out, ntf, thr, dsp = run_gate(
            sb, over, _lastmod(custom30v_8l=LASTMOD_MAX + 1, custom30_8l=None), py_touch=True)
        for t, (mx, unit) in BLOCK_TABLES.items():
            check(f"S2 boundary-FAIL {t} (lag={mx+1}{unit}d > {mx})",
                  bool(re.search(rf"FAIL [^\n]*lag={mx+1}{unit}d \(>{mx}\)", out)), out[:1200])
        check("S2 risk_rating = WARN chứ không FAIL (orphan, non-blocking)",
              f"WARN risk_rating (research, orphan): lag={WARN_TABLE_RR[1]+1}" in out
              and "FAIL risk_rating" not in out, out[:1500])
        check(f"S2 writer-alive {LASTMOD_MAX+1}d → WARN nghi chết",
              f"last-modified {LASTMOD_MAX+1}d (>{LASTMOD_MAX})" in out, out[-1200:])
        check("S2 lastmod metadata unreadable → age=999 WARN (fail-safe, không im lặng)",
              "last-modified 999d" in out, out[-1200:])
        check("S2 rc=1 + ⛔ block DollarBill, KHÔNG dispatch",
              rc == 1 and "⛔" in thr and dsp == "", f"rc={rc} dsp={dsp!r}")
        check("S2 BLOCK có Telegram (notify.sh), WARN 🟡 CHỈ Discord",
              "⚠️ BQ STALE" in ntf and "🟡" not in ntf and "🟡" in thr,
              f"ntf={ntf[:300]!r}")

        # --- S3: chỉ WARN stale → không chặn gì, không Telegram ---
        warn_only = dict(at_max)
        warn_only[WARN_TABLE_RR[0]] = WARN_TABLE_RR[1] + 1
        rc, out, ntf, thr, dsp = run_gate(
            sb, warn_only, _lastmod(custom30v_8l=LASTMOD_MAX + 1, custom30_8l=None), py_touch=True)
        check("S3 WARN-only → pipeline vẫn chạy, dispatch vẫn đi, rc=0",
              rc == 0 and "ALL FRESH" in out and "TestAcct" in dsp
              and "NOTE: 3 WARN non-blocking" in out, f"rc={rc}\n{out[-800:]}")
        check("S3 WARN không Telegram, có 3 🟡 Discord",
              ntf == "" and thr.count("🟡") == 3, f"ntf={ntf!r} thr={thr!r}")

        # --- S4: all fresh nhưng pipeline step KHÔNG ghi artifact → chặn dispatch (F5) ---
        shutil.rmtree(sb["workdir"] / "deploy_golive_dt5g_v4", ignore_errors=True)
        rc, out, ntf, thr, dsp = run_gate(
            sb, at_max, _lastmod(), py_touch=False)
        check("S4 artifact stale → rc=1, ARTIFACT STALE alert, KHÔNG dispatch",
              rc == 1 and "ARTIFACT STALE" in thr and dsp == ""
              and "KHÔNG được dispatch" in out, f"rc={rc} dsp={dsp!r}\n{out[-600:]}")


# ---------------------------------------------------------------------------
# (B) chain 8L alert-on-fail — test hàm thật extract từ file
# ---------------------------------------------------------------------------

def extract_funcs(script: Path) -> str:
    """Lấy FAILS=0 + run() + notify_fails() từ file thật (drift → extract rỗng → FAIL)."""
    r = subprocess.run(
        ["awk", r'/^FAILS=0/{f=1} f{print} f&&/^notify_fails\(\)/{n=1} f&&n&&/^\}$/{exit}',
         str(script)], capture_output=True, text=True)
    return r.stdout


def run_chain_case(funcs: str, chain: str, fail_labels, ok_labels, notify_bin=None):
    """Harness bash: source hàm thật, giả lập step fail/ok, gọi notify_fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "funcs.sh").write_text(funcs)
        (tmp / "notify_stub.sh").write_text(
            '#!/usr/bin/env bash\necho "$*" >> "$LOGDIR/notify.log"\n')
        (tmp / "thread_stub.sh").write_text(
            '#!/usr/bin/env bash\necho "$1 || ${2:-}" >> "$LOGDIR/thread.log"\n')
        for f in ("notify_stub.sh", "thread_stub.sh"):
            (tmp / f).chmod(0o755)
        steps = "".join(f'PY=/bin/false; run "{l}" fake_step.py\n' for l in fail_labels)
        steps += "".join(f'PY=/bin/true; run "{l}" fake_step.py\n' for l in ok_labels)
        harness = (f'set -u\nexport LOGDIR="{tmp}"\nWORKDIR_8L=/fake LOG=fake.log\n'
                   f'source "{tmp}/funcs.sh"\n{steps}'
                   f'notify_fails "{chain}"\nrc=$?\necho "FAILS_COUNT=$FAILS rc=$rc"\n')
        env = dict(os.environ,
                   NOTIFY_BIN=notify_bin or str(tmp / "notify_stub.sh"),
                   NOTIFY_THREAD_BIN=str(tmp / "thread_stub.sh"))
        r = subprocess.run(["bash", "-c", harness], capture_output=True, text=True, env=env)
        logread = lambda n: ((tmp / n).read_text() if (tmp / n).exists() else "")
        return r.returncode, r.stdout, logread("notify.log"), logread("thread.log")


def part_b():
    print("\n=== (B) chain 8L (pt_8l_daily / papertrade_daily) — FAIL phải alert ===")
    for chain, script in CHAIN_SCRIPTS.items():
        funcs = extract_funcs(script)
        check(f"{chain}: extract được run()+notify_fails() từ file thật",
              "FAILS=0" in funcs and "notify_fails()" in funcs and "run()" in funcs,
              funcs[:200])
        if "notify_fails()" not in funcs:
            continue

        rc, out, ntf, thr = run_chain_case(funcs, chain, ["[1] fail_step"], ["[2] ok_step"])
        check(f"{chain}: 1 step FAIL → alert gộp đúng chain+count+label, Telegram+Discord",
              rc == 0 and f"⚠️ {chain}" in ntf and "1 step FAIL" in ntf
              and "[1] fail_step" in ntf and chain in thr,
              f"rc={rc} ntf={ntf!r} thr={thr!r}")
        check(f"{chain}: FAILS counter đếm đúng, chain không chết (rc=0)",
              "FAILS_COUNT=1 rc=0" in out, out)

        rc, out, ntf, thr = run_chain_case(funcs, chain, [], ["[1] ok_step"])
        check(f"{chain}: 0 FAIL → im lặng tuyệt đối (không notify)",
              rc == 0 and ntf == "" and thr == "" and "FAILS_COUNT=0" in out,
              f"ntf={ntf!r} thr={thr!r}")

        rc, out, ntf, thr = run_chain_case(
            funcs, chain, ["[1] fail_a", "[3] fail_b"], ["[2] ok"])
        check(f"{chain}: nhiều FAIL → đếm đủ 2 + đủ tên step trong 1 message",
              "2 step FAIL" in ntf and "[1] fail_a" in ntf and "[3] fail_b" in ntf, ntf)

        rc, out, ntf, thr = run_chain_case(
            funcs, chain, ["[1] fail_step"], [], notify_bin="/bin/false")
        check(f"{chain}: notify chết → chain vẫn rc=0 (alert không được giết chain)",
              "rc=0" in out, out)

    # static: các increment inline + lời gọi cuối chain còn nguyên trong file
    pt = CHAIN_SCRIPTS["pt_8l_daily"].read_text()
    pp = CHAIN_SCRIPTS["papertrade_daily"].read_text()
    check("pt_8l_daily: inline step [8] snapshot có tăng FAILS + gọi notify_fails cuối chain",
          'FAILED_STEPS="$FAILED_STEPS [8]"' in pt and 'notify_fails "pt_8l_daily"' in pt)
    check("papertrade_daily: inline step [6b] có tăng FAILS + gọi notify_fails cuối chain",
          'FAILED_STEPS="$FAILED_STEPS [6b]"' in pp
          and 'notify_fails "papertrade_daily"' in pp)


# ---------------------------------------------------------------------------
# (C) risk_monitor provenance gate — fail-safe cả 2 nhánh
# ---------------------------------------------------------------------------

def part_c():
    print("\n=== (C) risk_monitor --test-provenance (sandbox nội bộ, dry-run) ===")
    r = subprocess.run([sys.executable, str(RISK_MONITOR), "--test-provenance"],
                       capture_output=True, text=True, timeout=180)
    out = r.stdout + r.stderr
    check("suite provenance chạy PASS toàn bộ (rc=0 + 'Provenance test PASSED')",
          r.returncode == 0 and "Provenance test PASSED" in out, out[-1500:])
    # 2 nhánh fail-safe bắt buộc phải nằm trong những gì suite đã assert:
    check("nhánh 1: provenance TỐT + breach → HALT nổ (gate không chặn HALT)",
          "provenance TỐT + DD -30% → HALT nổ" in out, out[-1500:])
    check("nhánh 2: provenance XẤU + breach → VẪN HALT (không fail-open, không suppress)",
          "provenance XẤU + DD -30% → VẪN HALT" in out, out[-1500:])
    check("nhánh 2b: provenance XẤU + clean → không im lặng (alert + cờ suspect)",
          "CLEAN?(suspect)" in out or "CLEAN?(provenance-suspect)" in out, out[-1500:])


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    total = PASSED + FAILED
    print(f"\n===== freshness_ops_selfcheck: {PASSED}/{total} PASS =====")
    sys.exit(0 if FAILED == 0 else 1)
