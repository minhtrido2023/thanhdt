#!/usr/bin/env python3
"""Selfcheck weekly_orphan_review: repo giả + /tmp giả; không đụng dữ liệu thật. Chạy: env -u TZ python3 ..."""
import os, subprocess, sys, tempfile, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weekly_orphan_review as w

fails = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)

def run(*c, cwd=None): return subprocess.run(c, cwd=cwd, capture_output=True, text=True, check=True)

with tempfile.TemporaryDirectory() as t:
    root = os.path.join(t, "mike"); os.makedirs(root)
    run("git", "init", "-q", cwd=root); run("git", "config", "user.email", "x@x", cwd=root); run("git", "config", "user.name", "x", cwd=root)
    R = os.path.join(root, "agents/Taylor/research")
    old = time.time() - 40 * 86400
    def mk(d, name, size, tracked=True):
        p = os.path.join(R, d, name); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(os.urandom(size)); os.utime(p, (old, old))
    mk("old_exp", "panel.csv", 5000); mk("old_exp", "REPORT.md", 100)
    mk("dd_X_1", "src/a.pdf", 5000)
    mk("ref_exp", "big.csv", 5000)
    mk("keep_exp", "big.csv", 5000)
    mk("orphan_all", "x.pkl", 5000)
    mk("young", "big.csv", 5000)
    os.utime(os.path.join(R, "young", "big.csv"), None)
    os.makedirs(os.path.join(root, "bin"), exist_ok=True)
    open(os.path.join(root, "bin/use.py"), "w").write("P='research/ref_exp/big.csv'\n")
    os.makedirs(os.path.join(root, "kb/projects"), exist_ok=True)
    open(os.path.join(root, "kb/projects/n.md"), "w").write("old_exp: NO-GO\n")
    open(os.path.join(root, "kb/cleanup_keep.txt"), "w").write("keep_exp  # lý do\n")
    # old_exp/panel.csv tracked; orphan_all/x.pkl untracked
    run("git", "add", "-f", "agents", "bin", "kb", cwd=root); run("git", "reset", "-q", "agents/Taylor/research/orphan_all", cwd=root)
    run("git", "commit", "-q", "-m", "init", cwd=root)
    tmp = os.path.join(t, "tmp"); os.makedirs(tmp)
    open(os.path.join(tmp, "old.bin"), "wb").write(os.urandom(3000)); os.utime(os.path.join(tmp, "old.bin"), (old, old))
    open(os.path.join(tmp, "new.bin"), "wb").write(os.urandom(3000))
    common = ["--root", root, "--tmp", tmp, "--min-heavy", "1000", "--min-tmp", "1000", "--no-notify", "--no-report-only"]
    now = time.time()
    # 1) dry-run: không xoá gì, nhận diện đúng
    w.main(common + ["--now", str(now)])
    st = json.load(open(os.path.join(root, "state/orphan_review_state.json")))
    ok("R:old_exp:TRIM" in st, "old_exp (KB nhắc, không code) = TRIM")
    ok("R:orphan_all:REMOVE_DIR" in st, "orphan_all (không md/KB/code) = REMOVE_DIR")
    ok(not any(k.startswith(("R:dd_X_1", "R:ref_exp", "R:keep_exp", "R:young")) for k in st), "dd_/code-ref/keep/young KHÔNG là ứng viên")
    ok("T:old.bin" in st and "T:new.bin" not in st, "/tmp: chỉ mục cũ")
    ok(os.path.exists(os.path.join(R, "old_exp/panel.csv")), "dry-run không xoá")
    # 2) --apply lần 1: grace chặn R, T xoá ngay
    w.main(common + ["--apply", "--now", str(now)])
    ok(os.path.exists(os.path.join(R, "old_exp/panel.csv")), "grace: R chưa xoá lần đầu")
    ok(not os.path.exists(os.path.join(tmp, "old.bin")) and os.path.exists(os.path.join(tmp, "new.bin")), "T xoá không grace, giữ mục mới")
    # 3) 8 ngày sau: R bị xoá
    w.main(common + ["--apply", "--now", str(now + 8 * 86400)])
    ok(not os.path.exists(os.path.join(R, "old_exp/panel.csv")) and os.path.exists(os.path.join(R, "old_exp/REPORT.md")), "TRIM xoá file nặng, GIỮ .md")
    ok(not os.path.exists(os.path.join(R, "orphan_all")), "REMOVE_DIR xoá cả thư mục")
    for d in ("dd_X_1/src/a.pdf", "ref_exp/big.csv", "keep_exp/big.csv", "young/big.csv"):
        ok(os.path.exists(os.path.join(R, d)), f"giữ nguyên {d}")
    log = run("git", "log", "--oneline", cwd=root).stdout
    ok("weekly-orphan-review" in log and run("git", "status", "--porcelain", "--", "agents", cwd=root).stdout.strip() == "", "xoá tracked được commit theo pathspec, tree sạch")
    # 4) md5 guard: file untracked trùng md5 trong corpus ⇒ giữ
    mk("guard_exp", "pin.csv", 4000); open(os.path.join(root, "bin/pinref.py"), "w").write("")
    import hashlib
    md = hashlib.md5(open(os.path.join(R, "guard_exp/pin.csv"), "rb").read()).hexdigest()[:8]
    open(os.path.join(root, "bin/pinref.py"), "w").write(f"# pin {md}\n")
    code = w.corpus(root)
    ok(w.md5_guard([os.path.join(R, "guard_exp/pin.csv")], code) == [], "md5_guard giữ file có md5 trong code/registry")
print("OK" if not fails else f"FAIL {len(fails)}")
sys.exit(1 if fails else 0)
