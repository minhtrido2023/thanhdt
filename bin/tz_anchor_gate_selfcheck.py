#!/usr/bin/env python3
"""tz_anchor_gate_selfcheck.py — selfcheck cho bin/tz_anchor_gate.py (coding_guidelines §16).

Kiểm CẢ HAI CHIỀU, đúng yêu cầu khi bật gate:
  - RED   : code dùng `datetime.now()` trần / `date.today()` PHẢI bị chặn.
  - CONTROL: code đã neo TZ (`datetime.now(_ICT)`, `datetime.now(ZoneInfo(...))`,
             `datetime.now(timezone.utc)` — bước 1 của ICT-anchor pattern) PHẢI qua.

Ca ĐẮT NHẤT không phải fixture bịa: lấy NGUYÊN VĂN 4 file tại `20bf2f20^` / `b26008a6^` (bản
ĐÚNG LÚC 5 finding §16 của code-quality-weekly 2026-08-30 còn sống) và bản đã vá. Gate phải bắt
đúng SỐ DÒNG mà commit message nêu, và im ở những dòng đó sau khi vá. Không có git (sandbox) →
SKIP có báo, KHÔNG âm thầm PASS.

§16 tự áp lên chính nó: `--all-tz` chạy lại toàn bộ suite dưới `env -u TZ` và một TZ lạ
(America/New_York), đòi output GIỐNG HỆT — gate là phân tích tĩnh, kết quả không được đổi theo
đồng hồ của người chạy. Đây là đúng phép thử đã bắt được lớp lỗi này ngay từ đầu.

Sandbox: mọi ca end-to-end chạy trong mkdtemp qua MIKE_TZ_GATE_ROOT + MIKE_TZ_GATE_BASELINE —
KHÔNG file production nào bị ghi. Có assertion sha256 chứng minh việc đó (không dựa vào
`finally`, thứ không sống qua SIGKILL).
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE_PROD = os.path.join(ROOT, "bin", "tz_anchor_gate.py")
PROD_BASELINE = os.path.join(ROOT, "kb", "tz_anchor_baseline.json")


def _resolve_target(env_target, mutation_flag):
    """Từ chối override target nếu thiếu cờ mutation — nếu không 'ALL PASS' có thể là PASS GIẢ
    trên một bản sao, trong khi file production chưa hề được đọc."""
    if not env_target or env_target == GATE_PROD:
        return GATE_PROD
    if not mutation_flag:
        raise SystemExit(
            "❌ MIKE_TZ_GATE_TARGET được đặt mà KHÔNG có MIKE_TZ_GATE_MUTATION=1 — selfcheck sẽ "
            f"kiểm {env_target} chứ KHÔNG phải {GATE_PROD}. Bỏ biến này hoặc chạy qua --mutations."
        )
    return env_target


GATE_PATH = _resolve_target(
    os.environ.get("MIKE_TZ_GATE_TARGET"), os.environ.get("MIKE_TZ_GATE_MUTATION") == "1"
)

FAILED = []


def check(name, ok, detail=""):
    if ok:
        print(f"  ✓ {name}")
    else:
        FAILED.append(name)
        print(f"  ❌ {name}{('  — ' + detail) if detail else ''}")


def _load_gate():
    spec = importlib.util.spec_from_file_location("tz_gate", GATE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


# ── 1. Detector: RED — mọi cách viết KHÔNG neo TZ đang có thật trong 2 repo ────────────────
RED_CASES = [
    ("datetime.now() (from datetime import datetime)", "from datetime import datetime\nx = datetime.now()\n"),
    ("datetime.datetime.now() (import datetime)", "import datetime\nx = datetime.datetime.now()\n"),
    ("dt.datetime.now() (import datetime as dt)", "import datetime as dt\nx = dt.datetime.now()\n"),
    ("_dt.datetime.now() (alias _dt)", "import datetime as _dt\nx = _dt.datetime.now()\n"),
    ("date.today()", "from datetime import date\nx = date.today()\n"),
    ("datetime.date.today()", "import datetime\nx = datetime.date.today()\n"),
    ("_dt.date.today()", "import datetime as _dt\nx = _dt.date.today()\n"),
    ("datetime.today() (naive local, biến thể ít gặp)", "from datetime import datetime\nx = datetime.today()\n"),
    ("nằm trong f-string: f'{datetime.now():%H:%M}'", "from datetime import datetime\ns = f'{datetime.now():%H:%M}'\n"),
]

# ── 2. Detector: CONTROL — đã neo TZ, hoặc ngoài phạm vi §16 ⇒ PHẢI im ────────────────────
CONTROL_CASES = [
    ("datetime.now(_ICT)", "from datetime import datetime\nx = datetime.now(_ICT)\n"),
    ('datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))',
     'from datetime import datetime\nfrom zoneinfo import ZoneInfo\nx = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))\n'),
    ("datetime.now(tz=ICT) (keyword)", "from datetime import datetime\nx = datetime.now(tz=ICT)\n"),
    ("datetime.now(timezone.utc) — bước 1 của ICT-anchor, PHẢI cho qua",
     "from datetime import datetime, timezone\nx = datetime.now(timezone.utc)\n"),
    ("ICT-anchor đầy đủ: (now(utc)+7h).date()",
     "from datetime import datetime, timezone, timedelta\nx = (datetime.now(timezone.utc) + timedelta(hours=7)).date()\n"),
    ("call xuống dòng: now(\\n timezone.utc\\n) — regex đếm sai, AST đúng",
     "import datetime\nx = datetime.datetime.now(\n    datetime.timezone.utc,\n)\n"),
    ("tham chiếu không gọi: f = datetime.now", "from datetime import datetime\nf = datetime.now\n"),
    ("receiver khác: okf.today()", "x = okf.today()\n"),
    ("ngoài phạm vi user duyệt: pd.Timestamp.now()", "import pandas as pd\nx = pd.Timestamp.now()\n"),
    ("ngoài phạm vi: datetime.utcnow() (naive UTC, không phụ thuộc TZ host)",
     "from datetime import datetime\nx = datetime.utcnow()\n"),
]


def test_detector(gate, tmp):
    print("[1] Detector — RED (phải bị bắt)")
    for name, src in RED_CASES:
        p = _write(os.path.join(tmp, "det", "f.py"), src)
        check(name, len(gate.violations(p)) >= 1, f"violations={gate.violations(p)}")
    print("[2] Detector — CONTROL (phải im)")
    for name, src in CONTROL_CASES:
        p = _write(os.path.join(tmp, "det", "f.py"), src)
        check(name, gate.violations(p) == [], f"violations={gate.violations(p)}")


# ── 3. Ca THẬT: 5 finding §16 của code-quality-weekly 2026-08-30 ───────────────────────────
HIST = [
    # (repo_dir, commit, path_trong_commit, tên file tạm, các dòng commit message nêu)
    ("/home/trido/thanhdt", "20bf2f20", "WorkingClaude/deploy_golive_dt5g_v4/golive_recommend_v23.py",
     "golive_recommend_v23.py", [85, 1216]),
    ("/home/trido/thanhdt", "20bf2f20", "WorkingClaude/dna_report.py", "dna_report.py", [69]),
    (ROOT, "b26008a6", "agents/Taylor/anomaly_scan.py", "anomaly_scan.py", [379]),
    (ROOT, "b26008a6", "agents/Taylor/insider_flags.py", "insider_flags.py", [231]),
]


def _git_show(repo, rev, path, dest):
    r = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        return None
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(r.stdout)
    return dest


def test_historical(gate, tmp):
    print("[3] Ca THẬT — 5 finding §16 ngày 2026-08-30 (bản TRƯỚC vá phải bị bắt, SAU vá phải im)")
    d = os.path.join(tmp, "hist")
    os.makedirs(d, exist_ok=True)
    for repo, commit, path, fname, lines in HIST:
        before = _git_show(repo, commit + "^", path, os.path.join(d, "before_" + fname))
        after = _git_show(repo, commit, path, os.path.join(d, "after_" + fname))
        if before is None or after is None:
            check(f"{fname} — git không truy được {commit}", False, "SKIP-KHÔNG-ÂM-THẦM-PASS")
            continue
        hit_before = {ln for ln, _ in gate.violations(before)}
        hit_after = {ln for ln, _ in gate.violations(after)}
        check(f"{fname}: bắt được dòng {lines} ở bản TRƯỚC vá",
              set(lines).issubset(hit_before), f"bắt được {sorted(hit_before)}")
        check(f"{fname}: im ở dòng {lines} sau khi vá",
              not (set(lines) & hit_after), f"còn bắt {sorted(hit_after & set(lines))}")


# ── 4. End-to-end: ratchet + escape hatch + exclude, chạy qua CLI trong sandbox ────────────
def _run(sandbox, baseline, files, env_extra=None):
    env = dict(os.environ)
    env["MIKE_TZ_GATE_ROOT"] = sandbox
    env["MIKE_TZ_GATE_BASELINE"] = baseline
    env.pop("MIKE_TZ_GATE", None)
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, GATE_PATH] + files,
                       capture_output=True, text=True, env=env, cwd=sandbox, check=False)
    return r.returncode, r.stdout + r.stderr


BARE = "from datetime import datetime\nx = datetime.now()\n"
BARE2 = "from datetime import datetime, date\nx = datetime.now()\ny = date.today()\n"
ANCHORED = 'from datetime import datetime\nfrom zoneinfo import ZoneInfo\nx = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))\n'


def test_ratchet(tmp):
    print("[4] End-to-end — ratchet per-file + escape hatch + exclude")
    sb = os.path.join(tmp, "sandbox")
    bl = os.path.join(tmp, "sandbox_baseline.json")
    f = _write(os.path.join(sb, "app.py"), BARE)

    _write(bl, json.dumps({"files": {}}))
    rc, out = _run(sb, bl, [f])
    check("file MỚI có 1 vi phạm, baseline 0 → BLOCK (rc=1)", rc == 1, f"rc={rc} out={out[:200]}")
    check("thông điệp BLOCK có số dòng + biểu thức", "app.py:2" in out and "datetime.now()" in out, out[:200])

    _write(bl, json.dumps({"files": {"app.py": 1}}))
    rc, out = _run(sb, bl, [f])
    check("nợ CŨ đã trong baseline (1) → qua (rc=0)", rc == 0, f"rc={rc} out={out[:200]}")

    _write(os.path.join(sb, "app.py"), BARE2)
    rc, out = _run(sb, bl, [f])
    check("nợ TĂNG 1→2 → BLOCK", rc == 1, f"rc={rc}")

    _write(os.path.join(sb, "app.py"), ANCHORED)
    rc, out = _run(sb, bl, [f])
    check("đã vá (0 < baseline 1) → qua", rc == 0, f"rc={rc} out={out[:200]}")

    _write(os.path.join(sb, "app.py"), BARE)
    _write(bl, json.dumps({"files": {}}))
    rc, out = _run(sb, bl, [f], {"MIKE_TZ_GATE": "warn"})
    check("MIKE_TZ_GATE=warn → cảnh báo, không chặn", rc == 0 and "🔴" in out, f"rc={rc} out={out[:200]}")
    rc, out = _run(sb, bl, [f], {"MIKE_TZ_GATE": "off"})
    check("MIKE_TZ_GATE=off → im hoàn toàn", rc == 0 and out.strip() == "", f"rc={rc} out={out[:200]}")

    for rel in ("test_thing.py", "probe_x/run.py", "agents/T/research/r.py", "archive/old.py"):
        p = _write(os.path.join(sb, rel), BARE)
        rc, out = _run(sb, bl, [p])
        check(f"loại trừ R&D/vendor: {rel} không bị gate", rc == 0 and out.strip() == "",
              f"rc={rc} out={out[:160]}")

    # Sandbox KHÔNG phải checkout mike ⇒ tuyệt đối không auto-update baseline ở đó.
    _write(os.path.join(sb, "app.py"), ANCHORED)
    _write(bl, json.dumps({"files": {"app.py": 5}}))
    _run(sb, bl, [f])
    check("commit ngoài repo mike → KHÔNG tự ghi baseline",
          json.load(open(bl))["files"]["app.py"] == 5, "baseline đã bị ghi đè")


def test_prod_baseline_untouched(sha_before):
    print("[5] File production không bị selfcheck đụng")
    sha_after = hashlib.sha256(open(PROD_BASELINE, "rb").read()).hexdigest()
    check("kb/tz_anchor_baseline.json nguyên vẹn", sha_after == sha_before,
          f"{sha_before[:12]} → {sha_after[:12]}")


def main():
    print(f"tz_anchor_gate_selfcheck — gate={GATE_PATH}  TZ={os.environ.get('TZ', '(unset)')}")
    sha_before = hashlib.sha256(open(PROD_BASELINE, "rb").read()).hexdigest()
    gate = _load_gate()
    tmp = tempfile.mkdtemp(prefix="tz_anchor_selfcheck_")
    try:
        test_detector(gate, tmp)
        test_historical(gate, tmp)
        test_ratchet(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    test_prod_baseline_untouched(sha_before)
    print()
    if FAILED:
        print(f"❌ {len(FAILED)} FAIL: {FAILED}")
        return 1
    print("✅ ALL PASS")
    return 0


def run_all_tz():
    """§16 tự áp lên chính nó: cùng suite, 3 môi trường TZ, output phải GIỐNG HỆT."""
    variants = [("env -u TZ", ["env", "-u", "TZ"]),
                ("TZ=Asia/Ho_Chi_Minh", ["env", "TZ=Asia/Ho_Chi_Minh"]),
                ("TZ=America/New_York", ["env", "TZ=America/New_York"])]
    outs = {}
    rcs = {}
    for label, prefix in variants:
        r = subprocess.run(prefix + [sys.executable, os.path.abspath(__file__)],
                           capture_output=True, text=True, check=False)
        body = "\n".join(ln for ln in r.stdout.splitlines() if not ln.startswith("tz_anchor_gate_selfcheck"))
        outs[label] = body
        rcs[label] = r.returncode
        print(f"── {label}: rc={r.returncode}")
    ref = outs["env -u TZ"]
    bad = [k for k, v in outs.items() if v != ref] + [k for k, v in rcs.items() if v != 0]
    if bad:
        print(f"\n❌ khác nhau giữa các TZ hoặc FAIL: {sorted(set(bad))}")
        print(outs["TZ=America/New_York"])
        return 1
    print("\n✅ 3/3 môi trường TZ cho kết quả GIỐNG HỆT và đều PASS")
    return 0


MUTATIONS = [
    ("bỏ điều kiện 'không có argument' (c) → datetime.now(_ICT) cũng bị bắt",
     "        if node.args or node.keywords:\n            continue\n", ""),
    ("nới receiver (b) sang mọi tên → okf.today()/pd.Timestamp.now() bị bắt",
     '        if recv.split(".")[-1] not in DATETIME_RECEIVERS:\n            continue\n', ""),
    ("bỏ 'today' khỏi (a) → date.today() lọt",
     'BAD_ATTRS = {"now", "today"}', 'BAD_ATTRS = {"now"}'),
    ("bỏ 'now' khỏi (a) → datetime.now() lọt",
     'BAD_ATTRS = {"now", "today"}', 'BAD_ATTRS = {"today"}'),
    ("ratchet luôn cho qua → nợ TĂNG không bị chặn",
     "        if n > old:\n            blocked.append((key, old, n))\n", "        pass\n"),
]


def run_mutations():
    src = open(GATE_PROD, encoding="utf-8").read()
    sha_before = hashlib.sha256(src.encode()).hexdigest()
    tmpdir = tempfile.mkdtemp(prefix="tz_anchor_mut_")
    survived = []
    try:
        for desc, needle, repl in MUTATIONS:
            if needle not in src:
                survived.append(f"HARNESS-HỎNG: {desc}")
                print(f"  ❌ HARNESS  chuỗi cần thay KHÔNG có trong gate: {desc}")
                continue
            mutant = os.path.join(tmpdir, "mutant.py")
            with open(mutant, "w", encoding="utf-8") as fh:
                fh.write(src.replace(needle, repl, 1))
            shutil.rmtree(os.path.join(tmpdir, "__pycache__"), ignore_errors=True)
            env = dict(os.environ)
            env["MIKE_TZ_GATE_TARGET"] = mutant
            env["MIKE_TZ_GATE_MUTATION"] = "1"
            r = subprocess.run([sys.executable, os.path.abspath(__file__)],
                               capture_output=True, text=True, env=env, check=False)
            if r.returncode != 0:
                print(f"  KILLED    {desc}")
            else:
                survived.append(desc)
                print(f"  SURVIVED  {desc}  ← assertion tuyên bố canh nhánh này là GUARD GIẢ")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    sha_after = hashlib.sha256(open(GATE_PROD, "rb").read()).hexdigest()
    if sha_after != sha_before:
        survived.append("PRODUCTION-FILE-MODIFIED")
        print(f"  ❌ gate production BỊ THAY ĐỔI: {sha_before[:12]} → {sha_after[:12]}")
    else:
        print(f"  OK        gate production nguyên vẹn (sha256 {sha_before[:12]}…)")
    print()
    if survived:
        print(f"❌ {len(survived)} mutation sống sót: {survived}")
        return 1
    print(f"✅ {len(MUTATIONS)}/{len(MUTATIONS)} mutation bị giết")
    return 0


if __name__ == "__main__":
    if "--mutations" in sys.argv:
        sys.exit(run_mutations())
    if "--all-tz" in sys.argv:
        sys.exit(run_all_tz())
    sys.exit(main())
