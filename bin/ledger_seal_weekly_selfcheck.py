#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck ledger_seal_weekly.py — KHÔNG chạm data/ thật. Chạy dưới `env -u TZ` VÀ `TZ=Pacific/Kiritimati`.

Phần A — CLI giả (stub) + append_event giả: mọi nhánh của wrapper (chốt OK + mốc idempotent, cổng từ
chối ⇒ không mốc, TK2 lỗi sau TK1, NothingToSeal, rc=2 khác NothingToSeal, thiếu SEAL_MD5, đối số
CLI đúng & không có --accept-preclose/--restate/--force, WC_ROOT đã gỡ, khoá/khung giờ/tiến trình
ghi nav_history, code ngoài cây canonical), asof quanh lễ 2/9/2026 (lịch thật) và Tết 2027 (lịch tiêm).
Phần B — tích hợp: nav_unit_ledger.py THẬT của cây này trên BẢN SAO /tmp (nav_history copy từ cây
thật, chỉ đọc; thư mục có dnse_raw_* giả để cổng is_real_data_dir coi là "thật" ⇒ wrapper phải tự
truyền --real-data). Cuối cùng kiểm md5 sổ thật + file mốc thật KHÔNG đổi.
`LEDGER_SEAL_WRAPPER=<file>` để chạy trên bản đột biến (research/ledger_seal_weekly_20261016/mutants.py).
"""
import atexit
import datetime
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("LEDGER_SEAL_WRAPPER", os.path.join(HERE, "ledger_seal_weekly.py"))
REAL_WC = "/home/trido/thanhdt/WorkingClaude"
REAL_DATA = os.path.join(REAL_WC, "data", "execution_logs")
REAL_ANCHORS = os.path.join(REAL_WC, "mike", "kb", "fund_ledger_anchors.txt")
ACCTS = ("SpaceX", "ZaloPay")
# WC_ROOT MỒI (có wc_env.sh, không có dữ liệu) — wrapper phải gỡ nó; bản đột biến KHÔNG gỡ thì CLI neo
# vào cây mồi rỗng (lỗi), KHÔNG BAO GIỜ vào cây thật.
DECOY_WC = tempfile.mkdtemp(prefix="lsw_decoy_wc_", dir="/tmp")
open(os.path.join(DECOY_WC, "wc_env.sh"), "w").close()
atexit.register(shutil.rmtree, DECOY_WC, True)
fails = []


def check(name, cond, detail=""):
    print(("  OK   " if cond else "  FAIL ") + name + ("" if cond else f"\n        {detail[-900:]}"))
    if not cond:
        fails.append(name)


def md5(path):
    try:
        return hashlib.md5(open(path, "rb").read()).hexdigest()
    except OSError:
        return None


REAL_FILES = [os.path.join(REAL_DATA, f"nav_unit_ledger_{a}.csv{s}") for a in ACCTS
              for s in ("", ".manifest.jsonl")] + [REAL_ANCHORS]
REAL_BEFORE = {p: md5(p) for p in REAL_FILES}

# ------------------------------------------------------------------ phần A: stub
STUB_CLI = r'''
import json, os, sys
acct = sys.argv[sys.argv.index("--account") + 1]
with open(os.environ["STUB_LOG"], "a") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "wc_root": os.environ.get("WC_ROOT")}) + "\n")
plan = json.loads(os.environ["STUB_PLAN"])[acct]
sys.stdout.write(plan["out"])
sys.stdout.flush()
if plan.get("sleep"):
    import time; time.sleep(plan["sleep"])
sys.exit(plan["rc"])
'''
STUB_BUS = "#!/usr/bin/env bash\nprintf '%s\\t%s\\t%s\\t%s\\n' \"$@\" >> \"$STUB_BUS_LOG\"\nexit \"${STUB_BUS_RC:-0}\"\n"
HDR = "# header\nSEAL_MD5 SpaceX " + "0" * 32 + " " + "1" * 32 + "\n"


def ok_out(acct, h):
    return (f"nav_unit_ledger {acct}: 80 dòng dựng được\n"
            f"sổ đã chốt: /x/nav_unit_ledger_{acct}.csv — 80 dòng, tới 2026-10-16; vừa THÊM 5 dòng\n"
            f"kho bất biến: manifest #2 (seal) md5 {h * 32}\nSEAL_MD5 {acct} {h * 32} {'e' * 32}\n"
            f"date,nav\n2026-10-16,1\n")


NOTHING = lambda a: (f"TỪ CHỐI nav_unit_ledger ({a}) [NothingToSeal]: /x: không có dòng mới để chốt tới "
                     f"2026-10-16\n  ⇒ KHÔNG ghi gì vào sổ.\n")
GATE = lambda a: ("".join(f"info dòng {i}\n" for i in range(12)) +
                  f"TỪ CHỐI nav_unit_ledger ({a}) [SealGateError]: đoạn CHƯA đủ điều kiện chốt (1 chỗ):\n"
                  f"  2026-10-14: dòng chụp số dư lúc 2026-10-14T11:00 — TRƯỚC giờ đóng cửa\n"
                  f"  ⇒ KHÔNG ghi gì vào sổ.\n")


def run_stub(plan, anchors=HDR, now="2026-10-24T07:30", bus_rc=0, proc=None, extra_env=None,
             cli_dir=None):
    with tempfile.TemporaryDirectory() as d:
        cli = os.path.join(cli_dir or d, "stub_cli.py")
        open(cli, "w").write(STUB_CLI)
        bus = os.path.join(d, "bus.sh")
        open(bus, "w").write(STUB_BUS)
        os.chmod(bus, 0o755)
        ap = os.path.join(d, "anchors.txt")
        open(ap, "w").write(anchors)
        procd = os.path.join(d, "proc")
        os.makedirs(procd)
        for pid, argv in (proc or {}).items():
            os.makedirs(os.path.join(procd, pid))
            open(os.path.join(procd, pid, "cmdline"), "wb").write(b"\0".join(x.encode() for x in argv) + b"\0")
        env = dict(os.environ, NAV_UNIT_LEDGER_CLI=cli, LEDGER_ANCHORS_FILE=ap, APPEND_EVENT_CMD=bus,
                   LEDGER_SEAL_LOCK=os.path.join(d, "x.lock"), LEDGER_SEAL_PROC_DIR=procd,
                   LEDGER_SEAL_NOW_ICT=now, STUB_LOG=os.path.join(d, "cli.log"),
                   STUB_BUS_LOG=os.path.join(d, "bus.log"), STUB_BUS_RC=str(bus_rc),
                   STUB_PLAN=json.dumps(plan), WC_ROOT=DECOY_WC)
        env.update(extra_env or {})
        r = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True, env=env, timeout=120)
        rd = lambda n: open(os.path.join(d, n)).read() if os.path.exists(os.path.join(d, n)) else ""
        calls = [json.loads(x) for x in rd("cli.log").splitlines()]
        if cli_dir:
            os.unlink(cli)
        return r.returncode, r.stdout + r.stderr, open(ap).read(), calls, rd("bus.log").splitlines()


def anchors_of(text, acct):
    return [ln for ln in text.splitlines() if ln.startswith(f"SEAL_MD5 {acct} ")]


print("A. stub")
P_OK = {"SpaceX": {"rc": 0, "out": ok_out("SpaceX", "a")}, "ZaloPay": {"rc": 0, "out": ok_out("ZaloPay", "b")}}
rc, out, anc, calls, bus = run_stub(P_OK)
check("A1 chốt cả 2 ⇒ rc=0, mỗi TK đúng 1 mốc mới cuối file", rc == 0 and anc.startswith(HDR)
      and anc.rstrip().splitlines()[-1] == f"SEAL_MD5 ZaloPay {'b' * 32} {'e' * 32}"
      and anchors_of(anc, "SpaceX")[-1] == f"SEAL_MD5 SpaceX {'a' * 32} {'e' * 32}", out + anc)
check("A1 bus: 2 finding của Mike, topic fund-unit-ledger-seal-20261024, payload có SEAL_MD5",
      len(bus) == 2 and all(b.split("\t")[:3] == ["Mike", "finding", "fund-unit-ledger-seal-20261024"]
                            for b in bus)
      and json.loads(bus[1].split("\t")[3])["SEAL_MD5_ZaloPay"].startswith("SEAL_MD5 ZaloPay")
      and json.loads(bus[0].split("\t")[3])["rows"] == {"SpaceX": 80}, "\n".join(bus))
want = ["--account", "SpaceX", "--seal", "--real-data", "--asof", "2026-10-16"]
check("A1 CLI gọi ĐÚNG đối số (asof = thứ Sáu tuần trước), thứ tự SpaceX→ZaloPay",
      [c["argv"] for c in calls] == [want, want[:1] + ["ZaloPay"] + want[2:]], json.dumps(calls))
check("A1 CLI KHÔNG nhận --accept-preclose/--restate/--force/--immutable", not any(
    a.startswith(("--accept-preclose", "--restate", "--force", "--immutable")) for c in calls for a in c["argv"]),
    json.dumps(calls))
check("A1 env của CLI đã gỡ WC_ROOT", calls and all(c["wc_root"] is None for c in calls), json.dumps(calls))

rc2, out2, anc2, calls2, bus2 = run_stub(P_OK, anchors=anc)
check("A2 idempotent: chạy lại cùng SEAL_MD5 ⇒ rc=0, file mốc KHÔNG đổi, KHÔNG post bus lại",
      rc2 == 0 and anc2 == anc and bus2 == [], out2 + f"\nbus={bus2}")

rc, out, anc, calls, bus = run_stub({"SpaceX": {"rc": 2, "out": GATE("SpaceX")},
                                     "ZaloPay": {"rc": 0, "out": ok_out("ZaloPay", "b")}})
check("A3 cổng từ chối TK1 ⇒ rc≠0, KHÔNG mốc, KHÔNG bus, KHÔNG gọi ZaloPay",
      rc != 0 and anc == HDR and bus == [] and len(calls) == 1, out)
lines = out.rstrip().splitlines()
check("A3 in đúng 8 dòng cuối đầu ra thật của CLI (bằng chứng, §29)",
      lines[-8:] == GATE("SpaceX").rstrip().splitlines()[-8:] and "info dòng 3" not in out, out)

rc, out, anc, calls, bus = run_stub({"SpaceX": {"rc": 0, "out": ok_out("SpaceX", "a")},
                                     "ZaloPay": {"rc": 2, "out": GATE("ZaloPay")}})
check("A4 TK2 lỗi sau TK1 ⇒ rc≠0 nhưng mốc + bus của SpaceX ĐÃ ghi, ZaloPay không",
      rc != 0 and len(anchors_of(anc, "SpaceX")) == 2 and not anchors_of(anc, "ZaloPay") and len(bus) == 1
      and "SpaceX" in out.split("ZaloPay")[0], out)

rc, out, anc, calls, bus = run_stub({a: {"rc": 2, "out": NOTHING(a)} for a in ACCTS})
check("A5 NothingToSeal cả 2 ⇒ rc=0, không mốc, không bus, vẫn gọi cả 2 TK",
      rc == 0 and anc == HDR and bus == [] and len(calls) == 2, out)

rc, out, anc, calls, bus = run_stub({"SpaceX": {"rc": 2, "out": NOTHING("SpaceX")},
                                     "ZaloPay": {"rc": 0, "out": ok_out("ZaloPay", "b")}})
check("A6 TK1 NothingToSeal + TK2 chốt ⇒ rc=0, chỉ mốc ZaloPay", rc == 0 and len(anchors_of(anc, "ZaloPay")) == 1
      and len(anchors_of(anc, "SpaceX")) == 1 and len(bus) == 1, out)

rc, out, anc, calls, bus = run_stub({"SpaceX": {"rc": 2, "out": NOTHING("ZaloPay")},
                                     "ZaloPay": {"rc": 0, "out": ok_out("ZaloPay", "b")}})
check("A7 rc=2 mà dấu NothingToSeal của TK KHÁC ⇒ từ chối thật (rc≠0, dừng)", rc != 0 and len(calls) == 1, out)

rc, out, anc, calls, bus = run_stub({"SpaceX": {"rc": 1, "out": "LỖI nav_unit_ledger (SpaceX): x\n"},
                                     "ZaloPay": {"rc": 0, "out": ok_out("ZaloPay", "b")}})
check("A8 CLI rc=1 ⇒ rc≠0, dừng", rc != 0 and len(calls) == 1 and anc == HDR, out)

for tag, txt in (("không có", ok_out("SpaceX", "a").replace("SEAL_MD5 SpaceX", "XX")),
                 ("của TK khác", ok_out("SpaceX", "a").replace("SEAL_MD5 SpaceX", "SEAL_MD5 ZaloPay")),
                 ("hai dòng", ok_out("SpaceX", "a") + f"SEAL_MD5 SpaceX {'c' * 32} {'d' * 32}\n")):
    rc, out, anc, calls, bus = run_stub({"SpaceX": {"rc": 0, "out": txt},
                                         "ZaloPay": {"rc": 0, "out": ok_out("ZaloPay", "b")}})
    check(f"A9 rc=0 nhưng SEAL_MD5 {tag} ⇒ rc≠0, không mốc, dừng", rc != 0 and anc == HDR and len(calls) == 1, out)

rc, out, anc, calls, bus = run_stub(P_OK, bus_rc=1)
check("A10 bus lỗi ⇒ mốc SpaceX đã ghi, rc≠0, dừng trước ZaloPay",
      rc != 0 and len(anchors_of(anc, "SpaceX")) == 2 and len(calls) == 1, out)

rc, out, anc, calls, bus = run_stub({"SpaceX": {"rc": 0, "out": ok_out("SpaceX", "a"), "sleep": 5},
                                     "ZaloPay": {"rc": 0, "out": ok_out("ZaloPay", "b")}},
                                    extra_env={"LEDGER_SEAL_CLI_TIMEOUT": "1"})
check("A10b CLI treo quá trần ⇒ rc≠0, KHÔNG mốc (dù đã in SEAL_MD5), dừng, nói rõ timeout",
      rc != 0 and anc == HDR and len(calls) == 1 and "quá 1s" in out, out)

back = HDR + f"SEAL_MD5 SpaceX {'a' * 32} {'e' * 32}\nSEAL_MD5 SpaceX {'f' * 32} {'e' * 32}\n"
rc, out, anc, calls, bus = run_stub(P_OK, anchors=back)
check("A11 SEAL_MD5 trùng một mốc CŨ (không phải mới nhất) ⇒ không ghi, rc≠0", rc != 0 and anc == back, out)

rc, out, anc, calls, bus = run_stub(P_OK, now="2026-10-23T20:05")
check("A12 trong khung ghi nav_history 19:00–22:00 ⇒ rc=4, không gọi CLI", rc == 4 and calls == [], out)
rc, out, anc, calls, bus = run_stub(P_OK, proc={"4242": ["python3", "/w/mike/bin/daily_nav_snapshot.py", "--account", "SpaceX"]})
check("A13 có tiến trình daily_nav_snapshot.py ⇒ rc=4, không gọi CLI", rc == 4 and calls == [], out)
rc, out, anc, calls, bus = run_stub(P_OK, proc={"4243": ["bash", "/w/mike/bin/for_each_live_account.sh",
                                                         "/w/mike/bin/eod_trading_report.sh"]})
check("A14 có tiến trình eod_trading_report.sh ⇒ rc=4", rc == 4 and calls == [], out)
rc, out, anc, calls, bus = run_stub(P_OK, proc={"4244": ["/bin/sh", "-c", "cd /w && mike/bin/fund_bench_cron.sh "
                                                         "x ledger_seal_weekly.py # sau eod_trading_report.sh"]})
check("A15 dòng cron (sh -c) NHẮC tên writer trong comment ⇒ KHÔNG bị coi là writer", rc == 0, out)

with tempfile.TemporaryDirectory() as d:
    lk = os.path.join(d, "held.lock")
    holder = subprocess.Popen([sys.executable, "-c", "import fcntl,sys,time;f=open(sys.argv[1],'a');"
                               "fcntl.flock(f,fcntl.LOCK_EX);print('L',flush=True);time.sleep(30)", lk],
                              stdout=subprocess.PIPE, text=True)
    holder.stdout.readline()
    try:
        rc, out, anc, calls, bus = run_stub(P_OK, extra_env={"LEDGER_SEAL_LOCK": lk})
    finally:
        holder.kill()
check("A16 khoá đang bị giữ ⇒ rc=4, không gọi CLI", rc == 4 and calls == [], out)

guard_dir = tempfile.mkdtemp(prefix="lsw_guard_", dir=os.path.join(REAL_WC, "mike", "state"))
try:
    rc, out, anc, calls, bus = run_stub(P_OK, cli_dir=guard_dir)
finally:
    shutil.rmtree(guard_dir, ignore_errors=True)
check("A17 CLI nằm trong cây thật nhưng không phải mike/bin canonical ⇒ rc=64, không gọi CLI",
      rc == 64 and calls == [], out)

spec = importlib.util.spec_from_file_location("lsw", SCRIPT)
lsw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lsw)
D = datetime.date
real = [(D(2026, 10, 17), D(2026, 10, 9), "T7 thường"), (D(2026, 10, 24), D(2026, 10, 16), "T7 thường"),
        (D(2026, 10, 25), D(2026, 10, 16), "CN"), (D(2026, 10, 21), D(2026, 10, 13), "T4 chạy tay: thứ Sáu 16/10 mới 2 phiên ⇒ lùi đủ 5"),
        (D(2026, 9, 5), D(2026, 8, 25), "sau lễ 31/8–2/9 (3 phiên) ⇒ lùi tới đủ 5 phiên"),
        (D(2026, 9, 12), D(2026, 9, 4), "tuần sau lễ: thứ Sáu 4/9, có 5 phiên 7–11/9"),
        (D(2026, 5, 2), D(2026, 4, 22), "lễ 30/4+1/5: 24/4 mới 3 phiên ⇒ lùi đủ 5")]
for today, want_d, tag in real:
    got = lsw.seal_asof(today)
    check(f"A18 asof lịch thật {today} ({tag}) = {want_d}", got == want_d, f"got {got}")
TET = {D(2027, 2, 8) + datetime.timedelta(days=k) for k in range(5)}      # Tết 2027 GIẢ ĐỊNH (tiêm)
cal = lambda d: d.weekday() < 5 and d not in TET
for today, want_d, tag in ((D(2027, 2, 13), D(2027, 1, 29), "tuần Tết 0 phiên ⇒ lùi đủ 5 phiên"),
                           (D(2027, 2, 20), D(2027, 2, 5), "thứ Sáu 12/2 là Tết ⇒ phiên trước, 5 phiên 15–19/2")):
    got = lsw.seal_asof(today, is_session=cal)
    check(f"A19 asof Tết 2027 tiêm {today} ({tag}) = {want_d}", got == want_d, f"got {got}")
for today in (D(2026, 10, 24), D(2026, 9, 5), D(2027, 2, 13)):
    got = lsw.seal_asof(today, is_session=cal)
    lag = sum(1 for k in range(1, (today - got).days) if cal(got + datetime.timedelta(days=k)))
    check(f"A20 bất biến {today}: asof là phiên, < hôm nay, ≥5 phiên trễ", cal(got) and got < today and lag >= 5)

os.environ.pop("LEDGER_SEAL_NOW_ICT", None)
from zoneinfo import ZoneInfo  # noqa: E402
n = lsw.now_ict()
ref = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
check(f"A21 now_ict() neo ICT tường minh dưới TZ={os.environ.get('TZ', '<unset>')} (+07:00, lệch < 60s)",
      n.utcoffset() == datetime.timedelta(hours=7) and abs((n - ref).total_seconds()) < 60, repr(n))
r = subprocess.run([sys.executable, SCRIPT, "--print-asof"], capture_output=True, text=True,
                   env={k: v for k, v in os.environ.items() if k != "LEDGER_SEAL_NOW_ICT"})
check("A22 --print-asof (đồng hồ thật) == seal_asof(hôm nay ICT)",
      r.returncode == 0 and r.stdout.strip() == lsw.seal_asof(ref.date()).isoformat(), r.stdout + r.stderr)

# ------------------------------------------------------------------ phần B: tích hợp sandbox
print("B. tích hợp (nav_unit_ledger.py thật trên bản sao /tmp)")


def mk_sandbox(seal_to):
    s = tempfile.mkdtemp(prefix="lsw_sbx_", dir="/tmp")
    atexit.register(shutil.rmtree, s, True)
    open(os.path.join(s, "wc_env.sh"), "w").close()
    os.symlink(os.path.join(REAL_WC, "trading_bot"), os.path.join(s, "trading_bot"))
    shutil.copytree(HERE, os.path.join(s, "mike", "bin"), ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(SCRIPT, os.path.join(s, "mike", "bin", "ledger_seal_weekly.py"))
    os.makedirs(os.path.join(s, "mike", "kb"))
    os.makedirs(os.path.join(s, "mike", "state"))
    open(os.path.join(s, "mike", "kb", "fund_ledger_anchors.txt"), "w").write("# sandbox anchors\n")
    dl = os.path.join(s, "data", "execution_logs")
    os.makedirs(dl)
    for a in ACCTS:
        shutil.copy(os.path.join(REAL_DATA, f"nav_history_{a}.csv"), dl)
    open(os.path.join(dl, "dnse_raw_20990101.jsonl"), "w").close()   # ⇒ is_real_data_dir = True
    for f in ("account_inception.json", "account_cash_flows.json"):
        shutil.copy(os.path.join(REAL_WC, "data", f), os.path.join(s, "data", f))
    for a in ACCTS:     # dựng kho bất biến mới tới `seal_to` (bước DỰNG sandbox, không phải wrapper)
        r = subprocess.run([sys.executable, os.path.join(s, "mike", "bin", "nav_unit_ledger.py"), "--account", a,
                            "--seal", "--real-data", "--asof", seal_to,
                            "--accept-preclose", "2026-08-24=sandbox setup (giống lần chốt thật 16/10)"],
                           capture_output=True, text=True, env={k: v for k, v in os.environ.items() if k != "WC_ROOT"})
        assert r.returncode == 0, f"dựng sandbox {a} lỗi: {r.stdout}{r.stderr}"
    return s


def set_bts(s, acct, day, bts):
    p = os.path.join(s, "data", "execution_logs", f"nav_history_{acct}.csv")
    rows = open(p).read().splitlines(True)
    hit = [i for i, r in enumerate(rows) if r.startswith(day + ",")]
    assert len(hit) == 1, (acct, day)
    cols = rows[hit[0]].split(",")
    old = cols[7]
    cols[7] = bts
    rows[hit[0]] = ",".join(cols)
    open(p, "w").write("".join(rows))
    return old


def run_sbx(s, now):
    bl = os.path.join(s, "bus.log")
    bus = os.path.join(s, "bus.sh")
    open(bus, "w").write(STUB_BUS)
    os.chmod(bus, 0o755)
    env = {k: v for k, v in os.environ.items()
           if k not in ("NAV_UNIT_LEDGER_CLI", "LEDGER_ANCHORS_FILE", "LEDGER_SEAL_LOCK")}
    env.update(APPEND_EVENT_CMD=bus, STUB_BUS_LOG=bl, LEDGER_SEAL_NOW_ICT=now, WC_ROOT=DECOY_WC,
               LEDGER_SEAL_PROC_DIR=os.path.join(s, "noproc"))
    os.makedirs(env["LEDGER_SEAL_PROC_DIR"], exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(s, "mike", "bin", "ledger_seal_weekly.py")],
                       capture_output=True, text=True, env=env, timeout=600)
    anc = open(os.path.join(s, "mike", "kb", "fund_ledger_anchors.txt")).read()
    return r.returncode, r.stdout + r.stderr, anc, (open(bl).read().splitlines() if os.path.exists(bl) else [])


S = mk_sandbox("2026-10-02")
try:
    led = lambda a: md5(os.path.join(S, "data", "execution_logs", f"nav_unit_ledger_{a}.csv"))
    z0 = led("ZaloPay")
    old = set_bts(S, "ZaloPay", "2026-10-07", "2026-10-07T11:00:00")
    rc, out, anc, bus = run_sbx(S, "2026-10-17T07:30")
    check("B1 ZaloPay có dòng chụp trước đóng cửa ⇒ rc≠0; SpaceX ĐÃ chốt + mốc + bus, ZaloPay sổ không đổi",
          rc != 0 and len(anchors_of(anc, "SpaceX")) == 1 and not anchors_of(anc, "ZaloPay")
          and len(bus) == 1 and led("ZaloPay") == z0 and "[SealGateError]" in out, out)
    check("B1 mốc SpaceX == md5 thật của sổ + manifest sandbox", anchors_of(anc, "SpaceX")[0].split()[2:] == [
        led("SpaceX"), md5(os.path.join(S, "data", "execution_logs", "nav_unit_ledger_SpaceX.csv.manifest.jsonl"))],
        anc)
    set_bts(S, "ZaloPay", "2026-10-07", old)
    rc, out, anc2, bus = run_sbx(S, "2026-10-17T07:30")
    check("B2 sửa dòng ⇒ chạy lại: SpaceX NothingToSeal, ZaloPay chốt tới 2026-10-09, rc=0",
          rc == 0 and len(anchors_of(anc2, "SpaceX")) == 1 and len(anchors_of(anc2, "ZaloPay")) == 1
          and len(bus) == 2 and "SpaceX: NothingToSeal" in out
          and json.loads(bus[1].split("\t")[3])["through"] == "2026-10-09", out)
    rc, out, anc3, bus = run_sbx(S, "2026-10-17T07:30")
    check("B3 chạy lần 3 ⇒ rc=0, file mốc y nguyên, không bus mới", rc == 0 and anc3 == anc2 and len(bus) == 2, out)
    env = {k: v for k, v in os.environ.items() if k != "WC_ROOT"}
    env.update(LEDGER_ANCHORS_FILE=os.path.join(S, "mike", "kb", "fund_ledger_anchors.txt"),
               LEDGER_DIR=os.path.join(S, "data", "execution_logs"),
               NAV_UNIT_LEDGER_CLI=os.path.join(S, "mike", "bin", "nav_unit_ledger.py"))
    r = subprocess.run([sys.executable, os.path.join(S, "mike", "bin", "ledger_anchor_check.py")],
                       capture_output=True, text=True, env=env, timeout=300)
    check("B4 ledger_anchor_check đọc mốc wrapper vừa ghi ⇒ cả 2 TK KHỚP (rc=0)",
          r.returncode == 0 and r.stdout.count("OK ") == 2, r.stdout + r.stderr)
finally:
    shutil.rmtree(S, ignore_errors=True)

S = mk_sandbox("2026-09-25")
try:
    z0 = md5(os.path.join(S, "data", "execution_logs", "nav_unit_ledger_ZaloPay.csv"))
    set_bts(S, "SpaceX", "2026-10-01", "2026-10-01T10:00:00")
    rc, out, anc, bus = run_sbx(S, "2026-10-10T07:30")
    check("B5 cổng từ chối TK1 (SpaceX) ⇒ rc≠0, KHÔNG mốc, KHÔNG bus, ZaloPay không chạm",
          rc != 0 and anc == "# sandbox anchors\n" and bus == [] and "[SealGateError]" in out
          and md5(os.path.join(S, "data", "execution_logs", "nav_unit_ledger_ZaloPay.csv")) == z0, out)
finally:
    shutil.rmtree(S, ignore_errors=True)

check("Z dữ liệu thật KHÔNG đổi (md5 sổ + manifest 2 TK + file mốc canonical)",
      {p: md5(p) for p in REAL_FILES} == REAL_BEFORE, json.dumps({p: md5(p) for p in REAL_FILES}))
print(f"TZ={os.environ.get('TZ', '<unset>')} — {'PASS' if not fails else 'FAIL'}: "
      f"{len(fails)} lỗi" + ("" if not fails else ": " + "; ".join(fails)))
sys.exit(1 if fails else 0)
