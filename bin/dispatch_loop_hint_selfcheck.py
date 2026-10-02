#!/usr/bin/env python3
"""Selfcheck cho bin/dispatch_loop_hint.py — pin CẢ HAI phía (kêu đúng / im đúng).

Chạy trên thư mục job GIẢ (DISPATCH_LOOP_HINT_JOBS_DIR), không đụng bus thật.
  python3 bin/dispatch_loop_hint_selfcheck.py
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HINT = ROOT / "bin" / "dispatch_loop_hint.py"
fails, oks = [], []


def check(name, cond, detail=""):
    (oks if cond else fails).append(name)
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))


def run(prompt, jobs_dir, effort="medium", extra_env=None):
    env = dict(os.environ, DISPATCH_LOOP_HINT_JOBS_DIR=str(jobs_dir))
    env.update(extra_env or {})
    r = subprocess.run([sys.executable, str(HINT), "--to", "Taylor", "--effort", effort],
                       input=prompt, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


def seed(jobs_dir, name, summary, age_s=600):
    started = int(time.time()) - age_s
    p = Path(jobs_dir) / f"{name}.json"
    p.write_text(json.dumps({"job_id": name, "started_at": str(started), "prompt_summary": summary}))
    os.utime(p, (started, started))


BR = "fix/foo-bar-20261001"
with tempfile.TemporaryDirectory() as td:
    # 1. không có job trước ⇒ im
    rc, out = run(f"Vòng 1 branch {BR}", td, "high")
    check("no_prior_silent", rc == 0 and out == "", out)
    # 2. 1 job trước + tiếp nối + high ⇒ nhắc medium, KHÔNG nhắc cầu chì
    seed(td, "Taylor_a", f"Vòng 1 branch {BR} làm X")
    rc, out = run(f"TIẾP TỤC vòng 2 test-only branch {BR}", td, "high")
    check("continue_high_nudges_medium", "medium" in out and "vòng 3" not in out and "vòng 2" not in out.split("medium")[0], out)
    # 3. cùng prompt nhưng effort medium ⇒ im
    rc, out = run(f"TIẾP TỤC vòng 2 test-only branch {BR}", td, "medium")
    check("continue_medium_silent", out == "", out)
    # 4. việc mới (thiết kế) + high ⇒ KHÔNG nhắc medium
    rc, out = run(f"Thiết kế lại cổng, tiếp tục branch {BR}", td, "high")
    check("newwork_high_silent", out == "", out)
    # 5. 2 job trước ⇒ vòng 3 ⇒ nhắc cầu chì (kể cả effort medium)
    seed(td, "Taylor_b", f"Vòng 2 branch {BR} làm Y")
    rc, out = run(f"Vòng 3 branch {BR}", td, "medium")
    check("round3_fuse", "vòng 3" in out and "TOÀN BỘ" in out, out)
    # 6. nhánh khác ⇒ im (không nhiễu chéo)
    rc, out = run("Vòng 3 branch fix/khac-hoan-toan-20261001", td, "high")
    check("other_branch_silent", out == "", out)
    # 7. job [RESUME không tính
    with tempfile.TemporaryDirectory() as td2:
        seed(td2, "Taylor_r1", f"[RESUME sau usage-limit #1] branch {BR}")
        seed(td2, "Taylor_r2", f"[RESUME sau usage-limit #2] branch {BR}")
        rc, out = run(f"Vòng 2 branch {BR}", td2, "high")
        check("resume_jobs_ignored", out == "", out)
    # 8. job quá 24h không tính
    with tempfile.TemporaryDirectory() as td3:
        seed(td3, "Taylor_o1", f"branch {BR}", age_s=90000)
        seed(td3, "Taylor_o2", f"branch {BR}", age_s=95000)
        rc, out = run(f"Vòng 3 branch {BR}", td3, "high")
        check("old_jobs_ignored", out == "", out)
    # 9. worktree token wt-… cũng được nhận
    with tempfile.TemporaryDirectory() as td4:
        seed(td4, "Taylor_w1", "worktree agents/Taylor/wt-abc-1001 vòng 1")
        seed(td4, "Taylor_w2", "worktree agents/Taylor/wt-abc-1001 vòng 2")
        rc, out = run("tiếp tục agents/Taylor/wt-abc-1001", td4, "medium")
        check("worktree_token_counts", "vòng 3" in out, out)
    # 10. prompt không có token nhánh ⇒ im
    rc, out = run("Query PE hiện tại của VNM", td, "high")
    check("no_token_silent", out == "", out)
    # 11. FAIL-OPEN: thư mục job không tồn tại / file JSON hỏng ⇒ rc 0, không crash
    rc, out = run(f"branch {BR}", "/nonexistent/dir/xyz", "high")
    check("missing_dir_fail_open", rc == 0 and out == "", f"rc={rc} out={out}")
    (Path(td) / "bad.json").write_text("{not json")
    rc, out = run(f"Vòng 3 branch {BR}", td, "medium")
    check("corrupt_json_fail_open", rc == 0 and "vòng 3" in out, f"rc={rc} out={out}")
    # 12. stdin rỗng ⇒ im, rc 0
    rc, out = run("", td, "high")
    check("empty_stdin_silent", rc == 0 and out == "")

    # --- mutation: đổi ngưỡng vòng 2→99 phải làm check 5 chết ---
    src = HINT.read_text()
    mut = Path(td) / "mut_hint.py"
    mut.write_text(src.replace("LOOP_THRESHOLD = 2", "LOOP_THRESHOLD = 99"))
    r = subprocess.run([sys.executable, str(mut), "--to", "Taylor", "--effort", "medium"],
                       input=f"Vòng 3 branch {BR}", capture_output=True, text=True,
                       env=dict(os.environ, DISPATCH_LOOP_HINT_JOBS_DIR=str(td)))
    check("mutation_threshold_killed", "vòng 3" not in r.stdout)
    mut.write_text(src.replace("if s.lstrip().startswith(\"[RESUME\"):\n            continue", "pass"))
    with tempfile.TemporaryDirectory() as td5:
        seed(td5, "Taylor_r1", f"[RESUME #1] branch {BR}")
        seed(td5, "Taylor_r2", f"[RESUME #2] branch {BR}")
        r = subprocess.run([sys.executable, str(mut), "--to", "Taylor", "--effort", "medium"],
                           input=f"Vòng 3 branch {BR}", capture_output=True, text=True,
                           env=dict(os.environ, DISPATCH_LOOP_HINT_JOBS_DIR=str(td5)))
        check("mutation_resume_filter_killed", "vòng 3" in r.stdout)

# --- wiring thật trong dispatch.sh ---
sh = (ROOT / "bin" / "dispatch.sh").read_text()
i = sh.find("dispatch_loop_hint.py")
check("wired_in_dispatch_sh", i > 0 and "|| true" in sh[i:i + 200])
check("wired_before_provider_bin", i < sh.find("CLI_BIN=\"$(\"$ROOT/bin/cli_provider.sh\" bin"))

print(f"\n{len(oks)} PASS / {len(fails)} FAIL")
sys.exit(1 if fails else 0)
