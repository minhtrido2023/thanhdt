#!/usr/bin/env python3
"""Vòng 2 — 4 môi trường + bảng mutation + negative control cho macro_gate_health_tz_selfcheck.py.
Mọi thứ chạy trên BẢN SAO dưới /tmp; worktree chỉ được ĐỌC. argv[1] = thư mục WorkingClaude của worktree."""
import os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

SRC = Path(sys.argv[1]); OUT = Path(__file__).resolve().parent
VENV = "/home/trido/thanhdt/wc_venv/bin/python"; SYS = "/usr/bin/python3"
ENVS = [("venv312 TZ=Asia/Ho_Chi_Minh", VENV, "Asia/Ho_Chi_Minh"), ("venv312 env -u TZ", VENV, None),
        ("venv312 TZ=America/New_York", VENV, "America/New_York"), ("py3.10 env -u TZ", SYS, None)]
FILES = ["macro_state_live.py", "macro_gate_health_tz_selfcheck.py", "macro_healthcheck.py", "sbv_macro_overlay.py"]

NAIVE = '''        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=ict)
'''
FUT = '''        if age_min < -MAX_HEALTH_FUTURE_SKEW_MIN:
            reason = (f"health report ts={h['ts']} is {-age_min:.0f}min in the FUTURE "
                      f"(> {MAX_HEALTH_FUTURE_SKEW_MIN}min clock-skew allowance) -> DT4_only")
        elif age_min > max_health_age_min:
'''
MUTS = [  # (id, mô tả, old, new)
    ("M10", "luôn ts.replace(tzinfo=ict) — đè offset", NAIVE, "        ts = ts.replace(tzinfo=ict)\n"),
    ("M11", 'cắt h["ts"][:19] rồi parse', 'datetime.fromisoformat(h["ts"])', 'datetime.fromisoformat(h["ts"][:19])'),
    ("M09a", "mặc định max_health_age_min 1440→1400", "max_health_age_min=1440", "max_health_age_min=1400"),
    ("M09b", "mặc định max_health_age_min 1440→1490", "max_health_age_min=1440", "max_health_age_min=1490"),
    ("M13", "bỏ hẳn nhánh tương lai", FUT, "        if age_min > max_health_age_min:\n"),
    ("M13b", "đảo dấu điều kiện (< thành >)", "if age_min < -MAX_HEALTH_FUTURE_SKEW_MIN:", "if age_min > -MAX_HEALTH_FUTURE_SKEW_MIN:"),
    ("M13c*", "bỏ dấu trừ của ngưỡng (age_min < +5)", "if age_min < -MAX_HEALTH_FUTURE_SKEW_MIN:", "if age_min < MAX_HEALTH_FUTURE_SKEW_MIN:"),
    ("M13d*", "hằng số 5→200 phút", "MAX_HEALTH_FUTURE_SKEW_MIN = 5", "MAX_HEALTH_FUTURE_SKEW_MIN = 200"),
    ("M13e*", "hằng số 5→1 phút", "MAX_HEALTH_FUTURE_SKEW_MIN = 5", "MAX_HEALTH_FUTURE_SKEW_MIN = 1"),
    ("M14*", "reason tương lai không in ts thật (§29)", "health report ts={h['ts']} is", "health report is"),
]

def sandbox(root, name, msl_text):
    d = Path(root) / name; d.mkdir()
    for f in FILES:
        shutil.copy2(SRC / f, d / f)
    (d / "macro_state_live.py").write_text(msl_text, encoding="utf-8")
    return d

def run(d, exe, tz):
    env = {k: v for k, v in os.environ.items() if k != "TZ"}
    if tz: env["TZ"] = tz
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run([exe, "macro_gate_health_tz_selfcheck.py"], cwd=d, env=env, capture_output=True, text=True, timeout=300)
    out = p.stdout + p.stderr
    m = re.search(r"(\d+)/(\d+) PASS", out)
    return p.returncode, (m.group(0) if m else "NO-SUMMARY"), out

def main():
    base = (SRC / "macro_state_live.py").read_text(encoding="utf-8")
    root = tempfile.mkdtemp(prefix="dt5g_r2_")
    print("sandbox:", root)
    # 1) baseline 4 môi trường
    d = sandbox(root, "base", base)
    print("\n== 1. BASELINE (code nhánh, không mutate) ==")
    all_green = True
    for i, (lab, exe, tz) in enumerate(ENVS):
        rc, summ, out = run(d, exe, tz)
        (OUT / f"green_env{i+1}.txt").write_text(f"# {lab}\n{out}", encoding="utf-8")
        all_green &= rc == 0
        print(f"  {lab:32s} rc={rc} {summ}")
    # 2) mutation
    print("\n== 2. MUTATION (rc≠0 = ĐỎ = mutant CHẾT) ==")
    survivors = []
    for mid, desc, old, new in MUTS:
        assert base.count(old) == 1, f"{mid}: mẫu thay thế khớp {base.count(old)} lần (phải đúng 1)"
        d = sandbox(root, mid.strip("*"), base.replace(old, new))
        cells, killed, fails = [], False, set()
        for lab, exe, tz in ENVS:
            rc, summ, out = run(d, exe, tz)
            killed |= rc != 0
            cells.append(f"rc={rc} {summ}")
            fails |= {re.sub(r"^\[TZ=[^\]]*\] ", "", l.split("FAIL  ", 1)[1].split("  [")[0]) for l in out.splitlines() if "  FAIL  " in l}
        if not killed: survivors.append(mid)
        print(f"  {mid:6s} {'CHẾT' if killed else 'SỐNG'}  {desc}\n         " + " | ".join(cells))
        for f in sorted(fails): print(f"         ✗ {f}")
    # 3) negative control
    print("\n== 3. NEGATIVE CONTROL: selfcheck mới trên macro_state_live.py của 3538119f ==")
    old = subprocess.run(["git", "show", "3538119f:WorkingClaude/macro_state_live.py"], cwd=SRC, capture_output=True, text=True, check=True).stdout
    d = sandbox(root, "neg3538119f", old)
    neg_red = True
    for lab, exe, tz in ENVS:
        rc, summ, out = run(d, exe, tz)
        neg_red &= rc != 0
        print(f"  {lab:32s} rc={rc} {summ}")
    print(f"\nKẾT: baseline_all_green={all_green} survivors={survivors or 'KHÔNG'} negative_control_red_all_envs={neg_red}")
    shutil.rmtree(root)
    return 0 if (all_green and not survivors and neg_red) else 1

if __name__ == "__main__":
    sys.exit(main())
