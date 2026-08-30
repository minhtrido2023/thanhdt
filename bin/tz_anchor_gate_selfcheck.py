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


TOTAL = []


def check(name, ok, detail=""):
    TOTAL.append(name)
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
    # arch-review 2026-08-30 F8 — 4 dạng trước bản vá LỌT qua điều kiện (b)/(c).
    ("alias import: from datetime import datetime as dtm", "from datetime import datetime as dtm\nx = dtm.now()\n"),
    ("alias import: from datetime import date as d", "from datetime import date as d\nx = d.today()\n"),
    ("datetime.now(None) — có arg nhưng vô hiệu", "from datetime import datetime\nx = datetime.now(None)\n"),
    ("datetime.now(tz=None)", "from datetime import datetime\nx = datetime.now(tz=None)\n"),
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
    ("receiver khác: okf.today()", "x = okf.today()\n"),
    ("ngoài phạm vi user duyệt: pd.Timestamp.now()", "import pandas as pd\nx = pd.Timestamp.now()\n"),
    ("ngoài phạm vi: datetime.utcnow() (naive UTC, không phụ thuộc TZ host)",
     "from datetime import datetime\nx = datetime.utcnow()\n"),
]


# ── 2b. KNOWN GAP — gate KHÔNG bắt, và điều đó được GHI NHẬN, không phải "đúng" ────────────
# arch-review 2026-08-30 F8: trước đây `f = datetime.now` nằm trong CONTROL, tức selfcheck
# khẳng định "im ở đây là hành vi đúng". Sai — nó là lỗ hổng. Ghi ở mục này để bản sau ai bịt
# được thì biết phải chuyển sang RED, và để không ai đọc nhầm im lặng thành bảo đảm.
KNOWN_GAPS = [
    ("tham chiếu rồi gọi: n = datetime.now; n()", "from datetime import datetime\nn = datetime.now\nx = n()\n"),
    ("datetime.fromtimestamp(t) — naive host-local, chưa canh", "from datetime import datetime\nx = datetime.fromtimestamp(0)\n"),
    ("date.fromtimestamp(t)", "from datetime import date\nx = date.fromtimestamp(0)\n"),
    ("datetime.now(*args) — có arg nên qua (c)", "from datetime import datetime\nx = datetime.now(*a)\n"),
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
    print("[2b] KNOWN GAP — gate còn hở, ghi nhận chứ không tuyên bố là đúng")
    for name, src in KNOWN_GAPS:
        p = _write(os.path.join(tmp, "det", "f.py"), src)
        state = "vẫn hở" if gate.violations(p) == [] else "ĐÃ BỊT — chuyển ca này sang RED_CASES"
        print(f"  · {name}: {state}")


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
def _run(sandbox, baseline, files, env_extra=None, prefix=None):
    env = dict(os.environ)
    env["MIKE_TZ_GATE_SELFCHECK"] = "1"
    env["MIKE_TZ_GATE_ROOT"] = sandbox
    env["MIKE_TZ_GATE_BASELINE"] = baseline
    env.pop("MIKE_TZ_GATE", None)
    env.pop("MIKE_TZ_GATE_ROOTS", None)
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, GATE_PATH] + (prefix or []) + files,
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
    check("thông điệp BLOCK nói baseline neo theo canonical + lối thoát SKIP (F6)",
          "CANONICAL" in out and "SKIP=tz-anchor-gate" in out, out[:400])

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


SHIM = "/home/trido/thanhdt/WorkingClaude/tz_anchor_gate_shim.sh"


def test_shim_missing_nested_repo(tmp):
    """F1 (killer objection) — repo ngoài .gitignore chính WorkingClaude/mike/, nên trong mọi
    worktree/clone mới đường dẫn gate KHÔNG tồn tại. Thiếu repo lồng phải là KHÔNG-GATE-ĐƯỢC
    (cảnh báo + rc=0), tuyệt đối không phải CHẶN — phạm vi hook gồm bot_execute.py và
    trading_bot/*.py."""
    print("[6] F1 — shim khi repo lồng WorkingClaude/mike/ KHÔNG có mặt")
    if not os.path.isfile(SHIM):
        check("shim tồn tại", False, SHIM)
        return
    fake = os.path.join(tmp, "fake_wc")          # KHÔNG có thư mục mike/ bên trong
    victim = _write(os.path.join(fake, "bot_execute.py"), BARE)
    shutil.copy2(SHIM, os.path.join(fake, "tz_anchor_gate_shim.sh"))
    r = subprocess.run([os.path.join(fake, "tz_anchor_gate_shim.sh"), victim],
                       capture_output=True, text=True, check=False)
    check("thiếu repo lồng → rc=0 (không chặn commit)", r.returncode == 0, f"rc={r.returncode}")
    check("thiếu repo lồng → CÓ cảnh báo, không im lặng",
          "KHÔNG ĐƯỢC GATE" in r.stderr, f"stderr={r.stderr[:160]!r}")

    real = os.path.join(tmp, "real_wc")
    os.makedirs(os.path.join(real, "mike", "bin"), exist_ok=True)
    shutil.copy2(GATE_PATH, os.path.join(real, "mike", "bin", "tz_anchor_gate.py"))
    shutil.copy2(SHIM, os.path.join(real, "tz_anchor_gate_shim.sh"))
    v2 = _write(os.path.join(real, "app.py"), BARE)
    env = dict(os.environ)
    env["MIKE_TZ_GATE_SELFCHECK"] = "1"
    env["MIKE_TZ_GATE_ROOT"] = real
    env["MIKE_TZ_GATE_BASELINE"] = _write(os.path.join(tmp, "bl_shim.json"), '{"files": {}}')
    r2 = subprocess.run([os.path.join(real, "tz_anchor_gate_shim.sh"), v2],
                        capture_output=True, text=True, env=env, check=False)
    check("có repo lồng → shim ủy quyền cho gate thật và gate CHẶN",
          r2.returncode == 1 and "app.py:2" in r2.stdout, f"rc={r2.returncode} out={r2.stdout[:160]}")


def test_key_none_is_loud(tmp):
    """F2 — 20 worktree của repo ngoài nằm ngoài WC_ROOT; trước bản vá gate trả rc=0 KHÔNG một
    chữ trong khi vi phạm còn sống nguyên ở đó."""
    print("[7] F2 — file ngoài WC_ROOT: phải KÊU, không im")
    sb = os.path.join(tmp, "sandbox")
    bl = _write(os.path.join(tmp, "bl_none.json"), '{"files": {}}')
    outside = _write(os.path.join(tmp, "outside_tree", "x.py"), BARE)
    rc, out = _run(sb, bl, [outside])
    check("không chặn (fail-open)", rc == 0, f"rc={rc}")
    check("nhưng CÓ cảnh báo nêu tên file + lý do",
          "KHÔNG ĐƯỢC GATE" in out and "x.py" in out, f"out={out[:200]!r}")


def test_warn_does_not_raise_baseline(tmp):
    """F3 — warn cho qua ĐÚNG lần này; nếu nó nâng baseline thì một lần lách = chấp nhận nợ
    vĩnh viễn (đúng cái code_quality_gate.sh làm và đã bị audit chỉ ra)."""
    print("[8] F3 — MIKE_TZ_GATE=warn KHÔNG được nâng baseline")
    sb = os.path.join(tmp, "sandbox_warn")
    bl = _write(os.path.join(tmp, "bl_warn.json"), '{"files": {}}')
    f = _write(os.path.join(sb, "app.py"), BARE2)
    rc, out = _run(sb, bl, [f], {"MIKE_TZ_GATE": "warn"})
    check("warn → rc=0", rc == 0, f"rc={rc}")
    check("warn → baseline VẪN rỗng", json.load(open(bl))["files"] == {},
          f"baseline={json.load(open(bl))['files']}")
    check("warn → nói rõ commit sau vẫn chặn", "commit sau vẫn chặn" in out, out[:200])
    rc2, _ = _run(sb, bl, [f])
    check("lần commit sau vẫn BLOCK", rc2 == 1, f"rc={rc2}")


def test_update_baseline_direction(tmp):
    """F4 — config repo ngoài quảng cáo --update-baseline là cách 'siết bằng tay'."""
    print("[9] F4 — --update-baseline mặc định chỉ SIẾT, nâng phải nói ra")
    sb = os.path.join(tmp, "sandbox_upd")
    bl = _write(os.path.join(tmp, "bl_upd.json"), '{"files": {}}')
    f = _write(os.path.join(sb, "app.py"), BARE2)
    rc, out = _run(sb, bl, [f], {}, prefix=["--update-baseline"])
    check("nâng 0→2 mà không có cờ → TỪ CHỐI (rc=1)", rc == 1, f"rc={rc} out={out[:160]}")
    check("baseline không đổi", json.load(open(bl))["files"] == {}, "baseline đã bị ghi")
    rc, out = _run(sb, bl, [f], {}, prefix=["--update-baseline", "--accept-new-debt"])
    check("có --accept-new-debt → nâng được", rc == 0 and json.load(open(bl))["files"].get("app.py") == 2,
          f"rc={rc} baseline={json.load(open(bl))['files']}")
    _write(os.path.join(sb, "app.py"), ANCHORED)
    rc, out = _run(sb, bl, [f], {}, prefix=["--update-baseline"])
    check("HẠ (siết) thì không cần cờ", rc == 0 and "app.py" not in json.load(open(bl))["files"],
          f"rc={rc} baseline={json.load(open(bl))['files']}")


def test_seed_refuses_partial(tmp):
    """F5 — một root không đọc được thì kiểm kê THIẾU; ghi đè bằng nó biến 72 key thành
    ngầm-định-0 ⇒ mọi commit sau chạm chúng đều hard-block."""
    print("[10] F5 — --seed-baseline từ chối ghi khi kiểm kê thiếu")
    bl = _write(os.path.join(tmp, "bl_seed.json"), '{"files": {"giu/nguyen.py": 9}}')
    before = open(bl).read()
    env = dict(os.environ)
    env["MIKE_TZ_GATE_SELFCHECK"] = "1"
    env["MIKE_TZ_GATE_BASELINE"] = bl
    env["MIKE_TZ_GATE_ROOTS"] = f"/nonexistent/repo|*.py:{ROOT}|*.py"
    r = subprocess.run([sys.executable, GATE_PATH, "--seed-baseline"],
                       capture_output=True, text=True, env=env, check=False)
    check("root hỏng → rc != 0", r.returncode != 0, f"rc={r.returncode}")
    check("root hỏng → baseline KHÔNG bị ghi đè", open(bl).read() == before, "baseline đã bị ghi")


def test_auto_update_in_repo(tmp):
    """F7 — nhánh auto-update + `git add` chỉ chạy khi commit TRONG repo chứa baseline. Trước
    bản này nhánh đó KHÔNG có test nào (mutation xoá guard dirty sống sót)."""
    print("[11] F7 — auto-update baseline trong repo thật + guard baseline bẩn")
    r = os.path.join(tmp, "fakerepo")
    os.makedirs(os.path.join(r, "bin"), exist_ok=True)
    os.makedirs(os.path.join(r, "kb"), exist_ok=True)
    for cmd in (["git", "init", "-q", r], ["git", "-C", r, "config", "user.email", "t@t"],
                ["git", "-C", r, "config", "user.name", "t"]):
        subprocess.run(cmd, capture_output=True, check=False)
    bl = os.path.join(r, "kb", "tz_anchor_baseline.json")
    _write(bl, json.dumps({"files": {"bin/app.py": 5}}))
    f = _write(os.path.join(r, "bin", "app.py"), ANCHORED)
    subprocess.run(["git", "-C", r, "add", "-A"], capture_output=True, check=False)
    subprocess.run(["git", "-C", r, "commit", "-qm", "init"], capture_output=True, check=False)

    env = dict(os.environ)
    env.update({"MIKE_TZ_GATE_SELFCHECK": "1", "MIKE_TZ_GATE_ROOT": r, "MIKE_TZ_GATE_BASELINE": bl})
    env.pop("MIKE_TZ_GATE", None)
    res = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                         env=env, cwd=r, check=False)
    check("trong repo + cây sạch → auto-update HẠ baseline",
          res.returncode == 0 and "bin/app.py" not in json.load(open(bl))["files"],
          f"rc={res.returncode} baseline={json.load(open(bl))['files']} out={res.stdout[:160]}")
    staged = subprocess.run(["git", "-C", r, "diff", "--cached", "--name-only"],
                            capture_output=True, text=True, check=False).stdout
    check("baseline được `git add` vào cùng commit", "kb/tz_anchor_baseline.json" in staged, staged)

    # F3 TRONG repo thật: đây là nơi DUY NHẤT nhánh ghi baseline chạy tới, nên warn phải được
    # kiểm ở đây chứ không phải trong sandbox không-git (ở đó in_mike_repo()=None nên không ghi
    # dù có lỗi hay không — assertion sẽ xanh giả).
    subprocess.run(["git", "-C", r, "reset", "-q", "--hard"], capture_output=True, check=False)
    _write(os.path.join(r, "bin", "app.py"), BARE2)
    _write(bl, json.dumps({"files": {}}))
    subprocess.run(["git", "-C", r, "add", "-A"], capture_output=True, check=False)
    subprocess.run(["git", "-C", r, "commit", "-qm", "warn-case"], capture_output=True, check=False)
    res = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                         env={**env, "MIKE_TZ_GATE": "warn"}, cwd=r, check=False)
    check("F3 trong repo thật: warn cho qua nhưng KHÔNG nâng baseline",
          res.returncode == 0 and json.load(open(bl))["files"] == {},
          f"rc={res.returncode} baseline={json.load(open(bl))['files']}")

    subprocess.run(["git", "-C", r, "reset", "-q", "--hard"], capture_output=True, check=False)
    _write(os.path.join(r, "bin", "app.py"), ANCHORED)
    _write(bl, json.dumps({"files": {"bin/app.py": 5, "dirty": 1}}))   # sửa CHƯA stage
    snapshot = open(bl).read()
    res = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                         env=env, cwd=r, check=False)
    check("baseline BẨN (chưa stage) → bỏ qua auto-update, không ghi đè",
          res.returncode == 0 and open(bl).read() == snapshot, f"rc={res.returncode}")


MIKE_CFG = os.path.join(ROOT, ".pre-commit-config.yaml")
OUTER_CFG = "/home/trido/thanhdt/.pre-commit-config.yaml"


def _git(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True, check=False)


def test_outer_repo_never_writes_nested_baseline(tmp):
    """R1 (arch-review vòng 2, killer) — repo lồng nằm BÊN TRONG cây của repo ngoài, nên điều
    kiện 'BASELINE nằm dưới git-toplevel' ĐÚNG cho cả hai ⇒ commit từ repo NGOÀI ghi vào
    baseline của repo lồng. Ca này dựng ĐÚNG layout thật, không phải tmpdir không-git — đó là
    lý do assertion cũ ('commit ngoài repo mike → KHÔNG tự ghi baseline') xanh giả: nó chạy ở
    thư mục không phải git repo nên nhánh cần canh không bao giờ chạy tới."""
    print("[12] R1 — commit từ repo NGOÀI không được ghi baseline của repo LỒNG")
    outer = os.path.join(tmp, "outer")
    nested = os.path.join(outer, "WorkingClaude", "mike")
    os.makedirs(os.path.join(nested, "kb"), exist_ok=True)
    os.makedirs(os.path.join(nested, "bin"), exist_ok=True)
    _write(os.path.join(outer, ".gitignore"), "WorkingClaude/mike/\n")
    # Key PHẢI đúng cái baseline_key() sinh ra cho victim ("app.py", vì WC_ROOT của sandbox là
    # <outer>/WorkingClaude) — nếu lệch key thì counts không khớp entry nào, `changed` = False,
    # và ca này xanh kể cả khi guard bị tháo (bản đầu của tôi đúng như vậy: mutation R1 SỐNG SÓT
    # dù test "PASS"). Đây là lý do harness phải tự chứng minh bằng mutation.
    bl = _write(os.path.join(nested, "kb", "tz_anchor_baseline.json"),
                json.dumps({"files": {"app.py": 9, "khac.py": 3}}))
    _write(os.path.join(nested, "bin", "dispatch.sh"), "#!/bin/sh\n")
    victim = _write(os.path.join(outer, "WorkingClaude", "app.py"), ANCHORED)  # ĐÃ VÁ ⇒ hạ 9→0
    for cmd in (["init", "-q", outer], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git"] + cmd if cmd[0] == "init" else ["git", "-C", outer] + cmd,
                       capture_output=True, check=False)
    _git(outer, "add", "-A")
    _git(outer, "commit", "-qm", "init")
    before = open(bl).read()
    env = dict(os.environ)
    env.update({"MIKE_TZ_GATE_SELFCHECK": "1",
                "MIKE_TZ_GATE_ROOT": os.path.join(outer, "WorkingClaude"),
                "MIKE_TZ_GATE_BASELINE": bl})
    env.pop("MIKE_TZ_GATE", None)
    r = subprocess.run([sys.executable, GATE_PATH, victim], capture_output=True, text=True,
                       env=env, cwd=outer, check=False)
    check("chạy từ repo NGOÀI → rc=0", r.returncode == 0, f"rc={r.returncode} out={r.stdout[:200]}")
    check("baseline của repo LỒNG byte-identical (không bị ghi đè)", open(bl).read() == before,
          f"đã bị ghi: {open(bl).read()[:160]}")


def test_baseline_key_worktree(tmp):
    """R4 — nhánh chuẩn hoá key của worktree (mike/agents/wt-*/bin/x.py → mike/bin/x.py) là bản
    vá của một sự cố hard-block CÓ THẬT (arch-review Wags_20260823_071251) mà trước ca này
    KHÔNG có test nào: mọi sandbox đều ở /tmp nên chỉ nhánh key=None được chạy."""
    print("[13] R4 — baseline_key chuẩn hoá worktree về key canonical")
    r = os.path.join(tmp, "mike")
    os.makedirs(os.path.join(r, "bin"), exist_ok=True)
    os.makedirs(os.path.join(r, "kb"), exist_ok=True)
    _write(os.path.join(r, "bin", "dispatch.sh"), "#!/bin/sh\n")
    _write(os.path.join(r, "kb", "tz_anchor_baseline.json"), '{"files": {}}')
    _write(os.path.join(r, "bin", "x.py"), ANCHORED)
    subprocess.run(["git", "init", "-q", r], capture_output=True, check=False)
    _git(r, "config", "user.email", "t@t"); _git(r, "config", "user.name", "t")
    _git(r, "add", "-A"); _git(r, "commit", "-qm", "init")
    wt = os.path.join(r, "agents", "wt-test")
    res = _git(r, "worktree", "add", "-q", "-b", "wtbranch", wt)
    if res.returncode != 0:
        check("dựng được git worktree", False, res.stderr[:160])
        return
    env = dict(os.environ)
    env.update({"MIKE_TZ_GATE_SELFCHECK": "1", "MIKE_TZ_GATE_ROOT": tmp})
    code = ("import importlib.util,sys;"
            "spec=importlib.util.spec_from_file_location('g', sys.argv[1]);"
            "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
            "print(m.baseline_key(sys.argv[2]))")
    k_canon = subprocess.run([sys.executable, "-c", code, GATE_PATH, os.path.join(r, "bin", "x.py")],
                             capture_output=True, text=True, env=env, check=False).stdout.strip()
    k_wt = subprocess.run([sys.executable, "-c", code, GATE_PATH, os.path.join(wt, "bin", "x.py")],
                          capture_output=True, text=True, env=env, check=False).stdout.strip()
    check("canonical → 'mike/bin/x.py'", k_canon == "mike/bin/x.py", f"got {k_canon!r}")
    check("worktree → CÙNG key (không phải mike/agents/wt-test/bin/x.py)", k_wt == k_canon,
          f"canon={k_canon!r} wt={k_wt!r}")


def test_hook_verbose(tmp):
    """R2 — pre_commit/commands/run.py:217 chỉ in output hook khi rc!=0 hoặc verbose. Gate này
    cố ý fail-open; không verbose thì mọi cảnh báo bị nuốt và fail-open thành FAIL-SILENT."""
    print("[14] R2 — hook phải có verbose:true, và verbose thật sự lộ stderr khi rc=0")
    try:
        import yaml
    except ImportError:
        check("đọc được YAML config", False, "thiếu module yaml")
        return
    for cfg in (MIKE_CFG, OUTER_CFG):
        try:
            hooks = [h for r in yaml.safe_load(open(cfg))["repos"] for h in r["hooks"]
                     if h.get("id") == "tz-anchor-gate"]
        except (OSError, KeyError, yaml.YAMLError) as e:
            check(f"{cfg}: đọc được hook", False, str(e)[:120])
            continue
        check(f"{os.path.basename(os.path.dirname(cfg))}/.pre-commit-config.yaml: verbose=true",
              bool(hooks) and hooks[0].get("verbose") is True,
              f"hooks={hooks}")
    pc = shutil.which("pre-commit") or os.path.expanduser("~/.local/bin/pre-commit")
    if not os.path.exists(pc):
        check("có pre-commit để chứng minh hành vi verbose", False, "không tìm thấy pre-commit")
        return
    demo = os.path.join(tmp, "verbdemo")
    os.makedirs(demo, exist_ok=True)
    _write(os.path.join(demo, "warn.sh"), '#!/bin/sh\necho "CANH-BAO-RC0" >&2\nexit 0\n')
    os.chmod(os.path.join(demo, "warn.sh"), 0o755)
    _write(os.path.join(demo, "f.py"), "x = 1\n")
    for verbose, want in ((False, False), (True, True)):
        _write(os.path.join(demo, ".pre-commit-config.yaml"),
               "repos:\n  - repo: local\n    hooks:\n      - id: w\n        name: w\n"
               "        entry: ./warn.sh\n        language: system\n        files: '\\.py$'\n"
               + ("        verbose: true\n" if verbose else ""))
        subprocess.run(["git", "init", "-q", demo], capture_output=True, check=False)
        _git(demo, "add", "-A")
        out = subprocess.run([pc, "run", "w", "--files", os.path.join(demo, "f.py")],
                             capture_output=True, text=True, cwd=demo, check=False)
        seen = "CANH-BAO-RC0" in (out.stdout + out.stderr)
        check(f"pre-commit {'verbose' if verbose else 'mặc định'} + rc=0 → cảnh báo "
              f"{'HIỆN' if want else 'BỊ NUỐT'}", seen == want,
              f"seen={seen}, out={out.stdout[-200:]!r}")


def test_env_knobs_guarded(tmp):
    """R5 — một biến sót lại đổi được WC_ROOT là đủ biến gate thành no-op im lặng."""
    print("[15] R5 — env knob sandbox phải bị từ chối nếu thiếu MIKE_TZ_GATE_SELFCHECK=1")
    f = _write(os.path.join(tmp, "knob", "app.py"), BARE)
    for knob in ("MIKE_TZ_GATE_ROOT", "MIKE_TZ_GATE_BASELINE", "MIKE_TZ_GATE_ROOTS"):
        env = dict(os.environ)
        env.pop("MIKE_TZ_GATE_SELFCHECK", None)
        for k in ("MIKE_TZ_GATE_ROOT", "MIKE_TZ_GATE_BASELINE", "MIKE_TZ_GATE_ROOTS"):
            env.pop(k, None)
        env[knob] = "/nonexistent"
        r = subprocess.run([sys.executable, GATE_PATH, f], capture_output=True, text=True,
                           env=env, check=False)
        check(f"{knob} không có cờ → TỪ CHỐI chạy", r.returncode != 0 and "MIKE_TZ_GATE_SELFCHECK" in r.stderr,
              f"rc={r.returncode} err={r.stderr[:160]!r}")


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
        test_shim_missing_nested_repo(tmp)
        test_key_none_is_loud(tmp)
        test_warn_does_not_raise_baseline(tmp)
        test_update_baseline_direction(tmp)
        test_seed_refuses_partial(tmp)
        test_auto_update_in_repo(tmp)
        test_outer_repo_never_writes_nested_baseline(tmp)
        test_baseline_key_worktree(tmp)
        test_hook_verbose(tmp)
        test_env_knobs_guarded(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    test_prod_baseline_untouched(sha_before)
    print()
    if FAILED:
        print(f"❌ {len(FAILED)}/{len(TOTAL)} FAIL: {FAILED}")
        return 1
    print(f"✅ ALL PASS — {len(TOTAL)}/{len(TOTAL)} assertion")
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
     "        if (node.args or node.keywords) and not _tz_arg_is_none(node):\n            continue\n", ""),
    ("nới receiver (b) sang mọi tên → okf.today()/pd.Timestamp.now() bị bắt",
     '        if recv.split(".")[-1] not in receivers:\n            continue\n', ""),
    ("bỏ 'today' khỏi (a) → date.today() lọt",
     'BAD_ATTRS = {"now", "today"}', 'BAD_ATTRS = {"now"}'),
    ("bỏ 'now' khỏi (a) → datetime.now() lọt",
     'BAD_ATTRS = {"now", "today"}', 'BAD_ATTRS = {"today"}'),
    ("ratchet luôn cho qua → nợ TĂNG không bị chặn",
     "        if n > old:\n            blocked.append((key, old, n))\n", "        pass\n"),
    # Mutation ĐÚNG cho F3 là bỏ `return 0` để warn RƠI XUỐNG nhánh auto-update — không phải
    # xoá dòng print (bản đầu làm vậy và SURVIVED: dòng print thứ hai trong vòng lặp vẫn chứa
    # chuỗi mà assertion tìm, nên assertion không hề canh hành vi GHI).
    ("warn-mode rơi xuống auto-update (F3) → lách 1 lần = chấp nhận nợ vĩnh viễn",
     "        return 0\n\n    mike_top = in_mike_repo()", "        pass\n\n    mike_top = in_mike_repo()"),
    ("bỏ guard baseline BẨN (F7) → ghi đè sửa đổi chưa stage",
     "    if dirty:\n", "    if False:\n"),
    ("--seed-baseline ghi cả khi kiểm kê THIẾU (F5)",
     "        if not complete:\n", "        if False:\n"),
    ("bỏ alias-aware receiver (F8) → `from datetime import datetime as dtm` lọt",
     "    names = set(DATETIME_RECEIVERS)\n", "    return set(DATETIME_RECEIVERS)\n    names = set(DATETIME_RECEIVERS)\n"),
    ("bỏ nhận diện now(None) (F8)",
     "        if (node.args or node.keywords) and not _tz_arg_is_none(node):\n",
     "        if node.args or node.keywords:\n"),
    ("key=None quay lại IM LẶNG (F2)",
     "                f\"⚠️  tz_anchor_gate: {os.path.abspath(f)} nằm ngoài {WC_ROOT} và ngoài mọi \"\n                \"checkout mike — KHÔNG có baseline-key, file này KHÔNG ĐƯỢC GATE.\",",
     '                "",'),
    ("--update-baseline nâng được mà không cần cờ (F4)",
     "        if raises and not accept_new_debt:\n", "        if False:\n"),
    ("in_mike_repo() nới về 'BASELINE nằm dưới top' (R1) → repo ngoài ghi baseline repo lồng",
     "        return top if os.path.isfile(cand) and os.path.samefile(cand, BASELINE) else None",
     "        return top"),
    ("baseline_key() mất nhánh chuẩn hoá worktree (R4) → hard-block oan như 2026-08-23",
     '    if top and os.path.isdir(os.path.join(top, "kb")) and os.path.isfile(os.path.join(top, "bin", "dispatch.sh")):\n        return "mike/" + os.path.relpath(abs_p, top)\n',
     ""),
    ("bỏ guard env knob (R5) → biến sót lại biến gate thành no-op im lặng",
     "if _STRAY:\n", "if False:\n"),
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
