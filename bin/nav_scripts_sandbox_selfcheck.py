#!/usr/bin/env python3
"""nav_scripts_sandbox_selfcheck.py [--e2e]

Selfcheck cho phần AN TOÀN của nav_scripts_2account_selfcheck.py (prevention (a), retro
2026-10-24): backup tên duy nhất, flock, sandbox không rò ra data/ thật.
Mặc định chạy các ca nhanh (hợp nhất, không đụng broker/BQ). `--e2e` chạy thêm selfcheck
thật dưới `env -u TZ`-tương đương và chứng minh data/ thật không đổi.
"""
import os
import subprocess
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nav_scripts_2account_selfcheck as sc  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(name)


def t_backup_unique():
    d = tempfile.mkdtemp()
    try:
        f = os.path.join(d, "nav_history_X.csv")
        open(f, "w").write("a\n")
        b1, b2 = sc._backup(f), sc._backup(f)
        check("backup: 2 lần gọi ra 2 tên khác nhau", b1 != b2 and os.path.isfile(b1) and os.path.isfile(b2),
              f"{b1} vs {b2}")
        check("backup: tên chứa pid", str(os.getpid()) in os.path.basename(b1))
    finally:
        shutil.rmtree(d)


def t_lock():
    d = tempfile.mkdtemp()
    try:
        lp = os.path.join(d, "l.lock")
        h = sc._acquire_lock(lp)
        check("flock: lần 1 lấy được", h is not None)
        check("flock: lần 2 (khi còn giữ) bị từ chối", sc._acquire_lock(lp) is None)
        h.close()
        h2 = sc._acquire_lock(lp)
        check("flock: nhả rồi lấy lại được", h2 is not None)
        h2 and h2.close()
    finally:
        shutil.rmtree(d)


def t_sandbox_isolated():
    real = tempfile.mkdtemp()
    sb = None
    try:
        os.makedirs(os.path.join(real, "data", "execution_logs"))
        os.makedirs(os.path.join(real, "trading_bot"))
        open(os.path.join(real, "wc_env.sh"), "w").close()
        hist = os.path.join(real, "data", "execution_logs", "nav_history_SpaceX.csv")
        open(hist, "w").write("2026-01-01,100\n")
        open(os.path.join(real, "data", "account_inception.json"), "w").write("{}")
        sb = sc._make_sandbox(real)
        shist = os.path.join(sb, "data", "execution_logs", "nav_history_SpaceX.csv")
        check("sandbox: có marker wc_env.sh", os.path.isfile(os.path.join(sb, "wc_env.sh")))
        check("sandbox: nav_history là bản sao, không symlink",
              os.path.isfile(shist) and not os.path.islink(shist))
        open(shist, "a").write("2026-01-02,999\n")
        check("sandbox: ghi vào bản sao KHÔNG đổi file thật", open(hist).read() == "2026-01-01,100\n")
        check("sandbox: entry khác symlink về cây thật",
              os.path.islink(os.path.join(sb, "trading_bot"))
              and os.path.islink(os.path.join(sb, "data", "account_inception.json")))
    finally:
        shutil.rmtree(real)
        if sb:
            shutil.rmtree(sb, ignore_errors=True)


def t_fingerprint():
    d = tempfile.mkdtemp()
    try:
        open(os.path.join(d, "nav_history_A.csv"), "w").write("x")
        f1 = sc._real_fingerprint(d)
        open(os.path.join(d, "nav_history_A.csv"), "a").write("y")
        check("fingerprint: đổi nav_history thì khác", sc._real_fingerprint(d) != f1)
        f2 = sc._real_fingerprint(d)
        open(os.path.join(d, "dnse_raw_2026-01-01.jsonl"), "w").write("z")
        check("fingerprint: file không liên quan không làm đổi", sc._real_fingerprint(d) == f2)
        open(os.path.join(d, "nav_snapshot_A_2026-01-01.json"), "w").write("z")
        check("fingerprint: nav_snapshot mới làm đổi", sc._real_fingerprint(d) != f2)
    finally:
        shutil.rmtree(d)


def t_e2e():
    real_exec = sc.EXEC_DIR
    before = sc._real_fingerprint(real_exec)
    env = {k: v for k, v in os.environ.items() if k != "TZ"}
    r = subprocess.run([sys.executable, sc.__file__], capture_output=True, text=True, env=env, timeout=900)
    print(r.stdout[-1500:], r.stderr[-500:])
    check("e2e: selfcheck rc=0", r.returncode == 0, f"rc={r.returncode}")
    check("e2e: data/ thật không đổi", sc._real_fingerprint(real_exec) == before)
    left = [n for n in os.listdir(real_exec) if ".selfcheck_bak" in n]
    check("e2e: không còn file .selfcheck_bak", not left, str(left))


if __name__ == "__main__":
    t_backup_unique(); t_lock(); t_sandbox_isolated(); t_fingerprint()
    if "--e2e" in sys.argv:
        t_e2e()
    print("\nALL PASS" if not fails else f"\n{len(fails)} FAIL: {fails}")
    sys.exit(1 if fails else 0)
