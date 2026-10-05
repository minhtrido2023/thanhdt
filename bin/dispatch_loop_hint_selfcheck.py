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


def seed(jobs_dir, name, summary, age_s=600, status="done"):
    started = int(time.time()) - age_s
    p = Path(jobs_dir) / f"{name}.json"
    p.write_text(json.dumps({"job_id": name, "started_at": str(started), "prompt_summary": summary,
                             "status": status}))
    os.utime(p, (started, started))


BR = "fix/foo-bar-20261001"
with tempfile.TemporaryDirectory() as td:
    # 1. không có job trước ⇒ im
    rc, out = run(f"Vòng 1 branch {BR}", td, "high")
    check("no_prior_silent", rc == 0 and out == "", out)
    # 2. 1 job trước + tiếp nối + high ⇒ nhắc medium, KHÔNG nhắc cầu chì
    seed(td, "Taylor_a", f"Vòng 1 branch {BR} làm X", age_s=7200)
    rc, out = run(f"TIẾP TỤC vòng 2 test-only branch {BR}", td, "high")
    check("continue_high_nudges_medium", "medium" in out and "TOÀN BỘ" not in out, out)
    # 3. cùng prompt nhưng effort medium ⇒ im
    rc, out = run(f"TIẾP TỤC vòng 2 test-only branch {BR}", td, "medium")
    check("continue_medium_silent", out == "", out)
    # 4. việc mới (thiết kế) + high ⇒ KHÔNG nhắc medium
    rc, out = run(f"Thiết kế lại cổng, tiếp tục branch {BR}", td, "high")
    check("newwork_high_silent", out == "", out)
    # 5. 2 job trước ⇒ vòng 3 ⇒ nhắc cầu chì (kể cả effort medium)
    seed(td, "Taylor_b", f"Vòng 2 branch {BR} làm Y", age_s=3600)
    rc, out = run(f"Vòng 3 branch {BR}", td, "medium")
    check("round3_fuse", "2 dispatch trước" in out and "TOÀN BỘ" in out and "vòng 3" not in out, out)
    # 6. nhánh khác ⇒ im (không nhiễu chéo)
    rc, out = run("Vòng 3 branch fix/khac-hoan-toan-20261001", td, "high")
    check("other_branch_silent", out == "", out)
    # 7. job [RESUME không tính
    with tempfile.TemporaryDirectory() as td2:
        seed(td2, "Taylor_r1", f"[RESUME sau usage-limit #1] branch {BR}", age_s=7200)
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
        seed(td4, "Taylor_w1", "worktree agents/Taylor/wt-abc-1001 vòng 1", age_s=7200)
        seed(td4, "Taylor_w2", "worktree agents/Taylor/wt-abc-1001 vòng 2")
        rc, out = run("tiếp tục agents/Taylor/wt-abc-1001", td4, "medium")
        check("worktree_token_counts", "2 dispatch trước" in out, out)
    # 10. prompt không có token nhánh ⇒ im
    rc, out = run("Query PE hiện tại của VNM", td, "high")
    check("no_token_silent", out == "", out)
    # 11. FAIL-OPEN: thư mục job không tồn tại / file JSON hỏng ⇒ rc 0, không crash
    rc, out = run(f"branch {BR}", "/nonexistent/dir/xyz", "high")
    check("missing_dir_fail_open", rc == 0 and out == "", f"rc={rc} out={out}")
    (Path(td) / "bad.json").write_text("{not json")
    rc, out = run(f"Vòng 3 branch {BR}", td, "medium")
    check("corrupt_json_fail_open", rc == 0 and "2 dispatch trước" in out, f"rc={rc} out={out}")
    # 12. stdin rỗng ⇒ im, rc 0
    rc, out = run("", td, "high")
    check("empty_stdin_silent", rc == 0 and out == "")


    # --- ca bổ sung theo arch-review d6aaecc7 ---
    # A. cầu chì + effort high + "Vòng 3" ⇒ KHÔNG in lời khuyên medium (không mâu thuẫn B/A)
    rc, out = run(f"Vòng 3 tiếp tục branch {BR}", td, "high")
    check("fuse_high_no_contradiction", "TOÀN BỘ" in out and "medium" not in out, out)
    # B. job cancelled không tính; bản đúp <5 phút gộp 1
    with tempfile.TemporaryDirectory() as t6:
        seed(t6, "Taylor_c1", f"branch {BR}", age_s=7200, status="cancelled")
        seed(t6, "Taylor_c2", f"branch {BR}", age_s=3600, status="cancelled")
        rc, out = run(f"Vòng 3 branch {BR}", t6, "high")
        check("cancelled_ignored", out == "", out)
    with tempfile.TemporaryDirectory() as t7:
        seed(t7, "Taylor_d1", f"branch {BR}", age_s=7200)
        seed(t7, "Taylor_d2", f"branch {BR}", age_s=7200 - 40)     # bản đúp cách 40 giây
        seed(t7, "Taylor_d3", f"branch {BR}", age_s=7200 - 100)
        rc, out = run(f"Vòng 2 branch {BR}", t7, "medium")
        check("duplicates_within_5min_collapse", out == "", out)
    # C. job ~20h trước VẪN được đếm (ghim WINDOW_S ≥ 24h)
    with tempfile.TemporaryDirectory() as t8:
        seed(t8, "Taylor_e1", f"branch {BR}", age_s=20 * 3600)
        seed(t8, "Taylor_e2", f"branch {BR}", age_s=19 * 3600)
        rc, out = run(f"Vòng 3 branch {BR}", t8, "medium")
        check("jobs_20h_counted", "2 dispatch trước" in out, out)
    # D. token session/ + 2 token (wt bị cắt cụt + fix/…) ⇒ lấy max
    with tempfile.TemporaryDirectory() as t9:
        seed(t9, "Taylor_s1", "session/demo-sess-001 việc A", age_s=7200)
        seed(t9, "Taylor_s2", "session/demo-sess-001 việc B", age_s=3600)
        rc, out = run("tiếp session/demo-sess-001", t9, "medium")
        check("session_token_counts", "2 dispatch trước" in out, out)
    with tempfile.TemporaryDirectory() as t10:
        seed(t10, "Taylor_m1", f"wt-pri {BR}", age_s=7200)        # wt-… cắt cụt
        seed(t10, "Taylor_m2", f"wt-pri {BR}", age_s=3600)
        rc, out = run(f"Vòng 3 worktree wt-priceframe-cashleg-1001 branch {BR}", t10, "medium")
        check("two_tokens_takes_max", "2 dispatch trước" in out and BR in out, out)
    # E. _NEWWORK khác "thiết kế" cũng chặn nhắc medium; tiếp nối chữ hoa vẫn nhận (re.I)
    with tempfile.TemporaryDirectory() as t11:
        seed(t11, "Taylor_n1", f"branch {BR}", age_s=7200)
        rc, out = run(f"TIẾP TỤC điều tra tại sao hỏng branch {BR}", t11, "high")
        check("newwork_dieu_tra_silent", out == "", out)
        rc, out = run(f"POLISH branch {BR}", t11, "high")
        check("continue_case_insensitive", "medium" in out, out)
        rc, out = run(f"POLISH branch {BR}", t11, "xhigh")
        check("xhigh_not_nudged", out == "", out)

    # F. gap non-blocking arch-review vòng 2: từ khoá đơn lẻ + cận trên DEDUP_S
    with tempfile.TemporaryDirectory() as t12:
        seed(t12, "Taylor_k1", f"branch {BR}", age_s=7200)
        rc, out = run(f"TIẾP TỤC branch {BR}", t12, "high")
        check("bare_tiep_tuc_nudges", "medium" in out, out)
        rc, out = run(f"tiếp tục tại sao branch {BR}", t12, "high")
        check("newwork_tai_sao_alone", out == "", out)
        rc, out = run(f"tiếp tục điều tra branch {BR}", t12, "high")
        check("newwork_dieu_tra_alone", out == "", out)
    with tempfile.TemporaryDirectory() as t13:
        seed(t13, "Taylor_g1", f"branch {BR}", age_s=7200)
        seed(t13, "Taylor_g2", f"branch {BR}", age_s=7200 - 600)   # cách 10 phút = 2 vòng thật
        rc, out = run(f"Vòng 3 branch {BR}", t13, "medium")
        check("jobs_10min_apart_count_two", "2 dispatch trước" in out, out)

    # --- mutation: đổi ngưỡng vòng 2→99 phải làm check 5 chết ---
    src = HINT.read_text()
    mut = Path(td) / "mut_hint.py"
    mut.write_text(src.replace("LOOP_THRESHOLD = 2", "LOOP_THRESHOLD = 99"))
    r = subprocess.run([sys.executable, str(mut), "--to", "Taylor", "--effort", "medium"],
                       input=f"Vòng 3 branch {BR}", capture_output=True, text=True,
                       env=dict(os.environ, DISPATCH_LOOP_HINT_JOBS_DIR=str(td)))
    check("mutation_threshold_killed", "dispatch trước" not in r.stdout)
    _rf = "if s.lstrip().startswith(_AUTO_PREFIX):\n            continue"
    assert _rf in src, "mutation target trôi — cập nhật chuỗi _rf"
    mut.write_text(src.replace(_rf, "pass"))
    with tempfile.TemporaryDirectory() as td5:
        seed(td5, "Taylor_r1", f"[RESUME #1] branch {BR}", age_s=7200)
        seed(td5, "Taylor_r2", f"[RESUME #2] branch {BR}")
        r = subprocess.run([sys.executable, str(mut), "--to", "Taylor", "--effort", "medium"],
                           input=f"Vòng 3 branch {BR}", capture_output=True, text=True,
                           env=dict(os.environ, DISPATCH_LOOP_HINT_JOBS_DIR=str(td5)))
        check("mutation_resume_filter_killed", "dispatch trước" in r.stdout)

# --- wiring thật trong dispatch.sh ---
sh = (ROOT / "bin" / "dispatch.sh").read_text()
i = sh.find('python3 "$ROOT/bin/dispatch_loop_hint.py"')
line = sh[sh.rfind("\n", 0, i) + 1:sh.find("\n", i)]
check("wired_in_dispatch_sh", i > 0 and "|| true" in line)
check("wired_stderr_redirect", ">&2" in line, line)
check("wired_has_timeout", "timeout " in line, line)
check("wired_before_provider_bin", i < sh.find("CLI_BIN=\"$(\"$ROOT/bin/cli_provider.sh\" bin"))

print(f"\n{len(oks)} PASS / {len(fails)} FAIL")
sys.exit(1 if fails else 0)
