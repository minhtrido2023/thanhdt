#!/usr/bin/env python3
"""tz_anchor_gate.py <file.py> [...]   |   --scan   |   --seed-baseline   |   --update-baseline <file.py>

Pre-commit gate — CHẶN `datetime.now()` TRẦN và `date.today()` (không neo timezone), tức
coding_guidelines.md §16 biến thành điều kiện CƠ HỌC để commit.

WHY (không phải một đoạn văn nữa — §16 đã có từ 2026-07 và VẪN lọt):
code-quality-weekly 2026-08-30 tìm ra **5 finding cùng một lớp lỗi trong 1 tuần**, ở 2 repo:
  - WorkingClaude `20bf2f20`: golive_recommend_v23.py:85 (END/START/START_BR/START_VNI) +
    :1216 (`Generated {datetime.now():…}`) + dna_report.py:69 (`date.today()` tính stale-flag DT5G).
  - mike `b26008a6`: agents/Taylor/anomaly_scan.py:379 + insider_flags.py:231 (default `asof`).
Cả 5 đều LATENT trên host này (host ở +07 và crontab có `TZ=Asia/Ho_Chi_Minh` che mất), chỉ nổ
khi chạy tay/dispatch dưới env khác — đúng cái mà §16 dặn và đúng cái mà con-người-phải-nhớ
không chặn được. User duyệt biến thành lint rule 2026-08-30.

CHỮ KÝ (AST, không regex — `datetime.now(tz)` và `datetime.now()` chỉ khác nhau ở số ARG, thứ
regex không đếm được qua xuống dòng):
  một `ast.Call` là VI PHẠM khi ĐỦ 3 điều kiện —
    (a) `func` là Attribute có `attr` ∈ {`now`, `today`};
    (b) receiver render ra tên có thành phần CUỐI ∈ {`datetime`, `date`} — bắt mọi cách import
        đang dùng thật trong 2 repo: `datetime.now`, `datetime.datetime.now`, `dt.datetime.now`,
        `_dt.datetime.now`, `_d.datetime.now`, `date.today`, `datetime.date.today`,
        `dt.date.today`, `_dt.date.today`. Điều kiện này là cái tách khỏi `okf.today()`,
        `pd.Timestamp.now()` (xem CÒN HỞ) và mọi `.now()` của thư viện khác;
    (c) KHÔNG có argument nào (`len(args) == 0 and len(keywords) == 0`).
  (c) chính là điều CHO PHÉP: `datetime.now(_ICT)`, `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))`,
  `datetime.now(tz=...)`, và `datetime.now(timezone.utc)` — bước đầu của ICT-anchor pattern
  `datetime.now(timezone.utc) + timedelta(hours=7)` mà chính 2 commit fix hôm nay đã dùng.

RATCHET, không phải chặn tuyệt đối (cùng khuôn bin/code_quality_gate.sh): chỉ BLOCK khi số vi
phạm của CHÍNH file đó TĂNG so với kb/tz_anchor_baseline.json. File không có trong baseline →
baseline ngầm định 0. Nợ cũ (đã kiểm kê, xem baseline) không bị bắt sửa ngay.

BASELINE-KEY: chuẩn hoá về đường dẫn tương đối so với `/home/trido/thanhdt/WorkingClaude` —
"mike/bin/x.py", "dna_report.py", "trading_bot/y.py". Đúng quy ước kb/code_quality_baseline.json
đang dùng, và ổn định qua mọi worktree của mike (mike/agents/wt-<thread>/... map về "mike/...").

HAI REPO, MỘT BASELINE: gate được wire vào cả `mike/.pre-commit-config.yaml` (repo mike) lẫn
`/home/trido/thanhdt/.pre-commit-config.yaml` (repo ngoài, chứa WorkingClaude/) vì lớp lỗi này
đã nổ ở CẢ HAI. Baseline sống trong repo mike (kb/). Auto-update baseline (+ `git add` để nó
nằm cùng commit) CHỈ chạy khi đang commit TRONG repo mike — commit từ repo ngoài không được
phép ghi vào repo lồng rồi bỏ đó unstaged. Từ repo ngoài gate chỉ CƯỠNG CHẾ (đọc baseline), và
in ra lệnh `--update-baseline` nếu cần siết lại bằng tay.

CÒN HỞ (ghi ở đây, đừng để ai tưởng gate phủ cả họ lỗi):
  - `pd.Timestamp.now()` / `pd.Timestamp.today()` naive-host-local Y HỆT về ngữ nghĩa (đo được
    75 + 46 call trong WorkingClaude hôm nay) nhưng KHÔNG bị chặn — phạm vi user duyệt là
    `datetime.now()`/`date.today()`. Muốn mở rộng thì phải rebuild baseline trước, không chỉ
    nới điều kiện (b).
  - `datetime.utcnow()` (288 call) cũng trả naive nhưng là naive-UTC, không phụ thuộc TZ host ⇒
    KHÔNG thuộc lớp lỗi §16 này. Cố ý không chặn.
  - Bash `date` không neo TZ: ngoài phạm vi (bin/utc_text_gate.sh canh nửa văn bản gửi người).

Escape hatch (cùng khuôn MIKE_CQ_GATE / MIKE_DIAG_GATE / MIKE_COMMIT_GATE):
env MIKE_TZ_GATE=warn hạ BLOCK xuống cảnh báo không chặn; =off tắt hẳn.
"""
import ast
import json
import os
import subprocess
import sys

# MIKE_TZ_GATE_ROOT / MIKE_TZ_GATE_BASELINE: override CHỈ để selfcheck chạy trong sandbox
# (bin/tz_anchor_gate_selfcheck.py) — không dùng trong vận hành, mặc định là 2 đường dẫn thật.
WC_ROOT = os.environ.get("MIKE_TZ_GATE_ROOT", "/home/trido/thanhdt/WorkingClaude")
MIKE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.environ.get(
    "MIKE_TZ_GATE_BASELINE", os.path.join(MIKE_ROOT, "kb", "tz_anchor_baseline.json")
)

BAD_ATTRS = {"now", "today"}
DATETIME_RECEIVERS = {"datetime", "date"}


def _render(node):
    """Attribute/Name chain -> dotted string; '?' cho mắt xích không phải tên."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _render(node.value) + "." + node.attr
    return "?"


def violations(path):
    """-> [(lineno, 'datetime.now()' | 'date.today()')]; file không parse được -> []."""
    try:
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError, ValueError, UnicodeDecodeError):
        return []
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr not in BAD_ATTRS:
            continue
        recv = _render(func.value)
        if recv.split(".")[-1] not in DATETIME_RECEIVERS:
            continue
        if node.args or node.keywords:
            continue
        hits.append((func.lineno, f"{recv}.{func.attr}()"))
    return sorted(hits)


# Không phải code của fleet (thư viện vendor / bản sao repo cũ đã chết) hoặc là artifact R&D —
# không gate, không tính vào baseline. `mike_paseo/` là bản SAO cũ của repo mike (git repo riêng,
# worktree đã hỏng, không repo nào track); gate nó = nuôi 47 vi phạm ma trong baseline.
EXCLUDED_DIRS = frozenset((
    "research", "archive", "wc_venv", "__pycache__", ".git", "node_modules", "site-packages",
    "vendor", "stockquery", "mike_paseo",
))
RND_PREFIXES = ("test_", "exp_", "probe_", "stress_")


def is_excluded(rel):
    """rel = baseline-key. Đồng bộ exclude của bin/code_quality_gate.sh, cộng 3 nhóm ở trên.

    Tiền tố R&D kiểm trên MỌI thành phần đường dẫn, không chỉ basename — repo có cả THƯ MỤC
    R&D (`agents/Taylor/probe_golive_live_20260715/`, 20 vi phạm) mà bản chỉ-xét-basename của
    code_quality_gate.sh bỏ lọt (ở đó vô hại vì scope regex hẹp hơn; ở đây thì không).
    """
    parts = rel.split("/")
    for part in parts:
        if part in EXCLUDED_DIRS:
            return True
        if part.startswith(RND_PREFIXES):
            return True
    return False


_TOP_CACHE = {}


def _git_top(directory):
    """Toplevel của checkout chứa `directory` (cache theo thư mục). None nếu không phải git."""
    if directory not in _TOP_CACHE:
        try:
            out = subprocess.run(
                ["git", "-C", directory, "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=False,
            ).stdout.strip()
        except OSError:
            out = ""
        _TOP_CACHE[directory] = out or None
    return _TOP_CACHE[directory]


def baseline_key(path):
    """abs path -> key tương đối WC_ROOT.

    Worktree của mike (mike/agents/wt-<thread>/bin/x.py) PHẢI map về "mike/bin/x.py", nếu không
    cùng một file logic sẽ khớp 2 key khác nhau tuỳ commit từ checkout nào ⇒ baseline ngầm 0 ⇒
    hard-block oan (đã xảy ra thật với code_quality_gate.sh, arch-review Wags_20260823_071251).
    Vì vậy key suy từ `git rev-parse --show-toplevel` của CHÍNH file, KHÔNG cắt chuỗi đường dẫn.
    """
    abs_p = os.path.abspath(path)
    top = _git_top(os.path.dirname(abs_p) or ".")
    if top and os.path.isdir(os.path.join(top, "kb")) and os.path.isfile(os.path.join(top, "bin", "dispatch.sh")):
        return "mike/" + os.path.relpath(abs_p, top)
    if abs_p.startswith(WC_ROOT + "/"):
        return os.path.relpath(abs_p, WC_ROOT)
    return None


def _set_count(files_baseline, key, n):
    """Ghi số vi phạm; n == 0 thì XOÁ key thay vì lưu 0 — baseline ngầm định đã là 0, lưu vào
    chỉ phình file bằng rác (mọi file .py sạch từng đi qua gate sẽ nằm lại đó vĩnh viễn)."""
    if n:
        files_baseline[key] = n
    else:
        files_baseline.pop(key, None)


def load_baseline():
    try:
        with open(BASELINE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"files": {}}


def write_baseline(data):
    tmp = BASELINE + ".tmp.%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, BASELINE)


# Hai checkout CANONICAL được gate phủ. Liệt kê file bằng `git ls-files` chứ KHÔNG đi bộ cây
# thư mục: repo này có **36 bản sao** của cùng một file logic (worktree `mike/agents/wt-*`,
# `WorkingClaude/wt-*`, `mike/.claude/worktrees/*`, cộng bản sao chết `mike_paseo/`) và
# baseline_key chuẩn hoá tất cả về CÙNG một key ⇒ đi bộ cây thì bản nào thắng là ngẫu nhiên
# theo thứ tự os.walk. Đã cắn thật lúc seed 2026-08-30: anomaly_scan.py vào baseline với 2 vi
# phạm — số của một worktree CŨ chưa có commit b26008a6 — trong khi canonical chỉ còn 1.
# git ls-files còn tự loại untracked/gitignored (mike_paseo là repo lồng, không repo nào track).
TRACKED_ROOTS = (
    ("/home/trido/thanhdt/WorkingClaude/mike", "*.py"),   # repo mike
    ("/home/trido/thanhdt", "WorkingClaude/*.py"),        # repo ngoài, chỉ phần WorkingClaude/
)


def enumerate_tracked():
    """-> [abs_path] mọi .py được git track ở 2 checkout canonical. Repo thiếu → bỏ qua, có báo."""
    paths = []
    for repo, pattern in TRACKED_ROOTS:
        r = subprocess.run(["git", "-C", repo, "ls-files", "-z", pattern],
                           capture_output=True, text=True, check=False)
        if r.returncode != 0:
            print(f"⚠️  không đọc được `git ls-files` ở {repo} — BỎ QUA cây này, kiểm kê sẽ THIẾU.",
                  file=sys.stderr)
            continue
        for rel in r.stdout.split("\0"):
            if rel.endswith(".py"):
                paths.append(os.path.join(repo, rel))
    return paths


def scan_tree():
    """Kiểm kê toàn bộ vi phạm còn sót -> {baseline_key: [(line, expr)]}."""
    found = {}
    for p in enumerate_tracked():
        key = baseline_key(p)
        if key is None or is_excluded(key) or not os.path.isfile(p):
            continue
        hits = violations(p)
        if hits:
            found[key] = hits
    return found


def in_mike_repo():
    """True khi CWD nằm trong repo mike (nơi baseline sống và stage được cùng commit)."""
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
    except OSError:
        return None
    if not top:
        return None
    return top if os.path.isfile(os.path.join(top, "kb", "tz_anchor_baseline.json")) else None


def main(argv):
    mode = os.environ.get("MIKE_TZ_GATE", "block")
    if mode == "off":
        return 0

    args = list(argv)
    if args and args[0] == "--scan":
        found = scan_tree()
        total = sum(len(v) for v in found.values())
        for key in sorted(found):
            for line, expr in found[key]:
                print(f"{key}:{line}: {expr}")
        print(f"\n{total} vi phạm / {len(found)} file", file=sys.stderr)
        return 0

    if args and args[0] == "--seed-baseline":
        # Kiểm kê lại toàn bộ nợ cũ và GHI ĐÈ baseline. Chỉ chạy tay khi cố ý re-seed (vd mở
        # rộng phạm vi gate); vận hành thường ngày dùng ratchet auto-update ở cuối hàm này.
        found = scan_tree()
        data = {
            "_note": "Kiểm kê `datetime.now()` trần / `date.today()` (coding_guidelines §16) tại "
                     "thời điểm bật bin/tz_anchor_gate.py. Ratchet per-file: nợ cũ không bắt sửa "
                     "ngay, chỉ không được TĂNG. Re-seed: bin/tz_anchor_gate.py --seed-baseline",
            "files": {k: len(v) for k, v in found.items()},
        }
        write_baseline(data)
        print(f"✓ {BASELINE}: {sum(data['files'].values())} vi phạm / {len(data['files'])} file")
        return 0

    update_only = False
    if args and args[0] == "--update-baseline":
        update_only = True
        args = args[1:]

    baseline = load_baseline()
    files_baseline = baseline.setdefault("files", {})

    counts = {}
    detail = {}
    for f in args:
        if not os.path.isfile(f):
            continue
        key = baseline_key(f)
        if key is None or is_excluded(key):
            continue
        hits = violations(f)
        counts[key] = len(hits)
        detail[key] = hits

    if not counts:
        return 0

    if update_only:
        changed = False
        for key, n in counts.items():
            if files_baseline.get(key, 0) != n:
                _set_count(files_baseline, key, n)
                changed = True
                print(f"  baseline: {key} -> {n}")
        if changed:
            write_baseline(baseline)
            print(f"  ✓ {BASELINE}")
        return 0

    blocked = []
    for key, n in sorted(counts.items()):
        old = files_baseline.get(key, 0)
        if n > old:
            blocked.append((key, old, n))

    if blocked:
        for key, old, new in blocked:
            print(f"  🔴 {key}: {new} lần dùng giờ KHÔNG neo TZ (baseline {old}) — TĂNG [HARD-BLOCK] (tz_anchor_gate.py, §16)")
            for line, expr in detail[key]:
                print(f"       {key}:{line}: {expr}")
        print()
        print("coding_guidelines.md §16 — neo timezone tường minh, đừng tin TZ của host:")
        print('  datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))   # hoặc datetime.now(_ICT)')
        print("  (datetime.now(timezone.utc) + timedelta(hours=7)).date()   # thay date.today()")
        print("  Escape hatch (nếu chắc chắn false-block): MIKE_TZ_GATE=warn git commit ...")
        if mode == "block":
            return 1
        print("⚠️  downgraded — MIKE_TZ_GATE=warn, commit vẫn qua.")

    mike_top = in_mike_repo()
    if mike_top is None:
        # Commit từ repo NGOÀI: không ghi vào repo lồng rồi bỏ đó unstaged.
        return 0

    dirty = subprocess.run(
        ["git", "-C", mike_top, "diff", "--name-only", "--", BASELINE],
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    if dirty:
        print("⚠️  tz_anchor_gate: kb/tz_anchor_baseline.json có sửa đổi chưa stage — bỏ qua auto-update lần này.", file=sys.stderr)
        return 0

    changed = False
    for key, n in counts.items():
        if files_baseline.get(key, 0) != n:
            _set_count(files_baseline, key, n)
            changed = True
    if changed:
        write_baseline(baseline)
        print(f"  ✓ baseline updated: {BASELINE}")
        r = subprocess.run(["git", "-C", mike_top, "add", BASELINE], capture_output=True, text=True, check=False)
        if r.returncode != 0:
            print("⚠️  tz_anchor_gate: git add baseline thất bại — baseline đã ghi nhưng CHƯA stage.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
