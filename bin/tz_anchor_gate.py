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

ESCAPE HATCH — 3 đường, cố ý khác nhau về HỆ QUẢ:
  - `SKIP=tz-anchor-gate git commit …` — pre-commit hỗ trợ sẵn; dùng khi bị chặn vì LỆCH NHÁNH
    (baseline neo theo checkout canonical; worktree đang ở commit cũ có thể đếm ra nhiều hơn ở
    file mình không hề sửa — arch-review 2026-08-30 F6).
  - `MIKE_TZ_GATE=warn` — qua ĐÚNG lần này, và cố ý **KHÔNG nâng baseline** (khác
    bin/code_quality_gate.sh, nơi warn ghi nợ mới thành hợp lệ vĩnh viễn). Lần commit sau vẫn
    chặn. Lách không được phép âm thầm biến thành chấp nhận (F3).
  - `--update-baseline` — mặc định CHỈ hạ được baseline (siết). Nâng phải nói ra bằng
    `--accept-new-debt` (F4).
  - `MIKE_TZ_GATE=off` — tắt hẳn. Thắng MỌI thứ khác, kể cả guard env knob ở dưới.

CÒN HỞ (ghi ở đây, đừng để ai tưởng gate phủ cả họ lỗi):
  - `pd.Timestamp.now()` / `pd.Timestamp.today()` naive-host-local Y HỆT về ngữ nghĩa (đo được
    75 + 46 call trong WorkingClaude hôm nay) nhưng KHÔNG bị chặn — phạm vi user duyệt là
    `datetime.now()`/`date.today()`. Muốn mở rộng thì phải rebuild baseline trước, không chỉ
    nới điều kiện (b).
  - `datetime.utcnow()` (288 call) cũng trả naive nhưng là naive-UTC, không phụ thuộc TZ host ⇒
    KHÔNG thuộc lớp lỗi §16 này. Cố ý không chặn.
  - `datetime.fromtimestamp(t)` / `date.fromtimestamp(t)` không có tz — naive-host-local y hệt,
    CHƯA canh (arch-review 2026-08-30 F8).
  - Dạng tham chiếu rồi gọi: `n = datetime.now; n()` — AST không nối được 2 câu lệnh. CHƯA canh;
    selfcheck ghi nó ở mục KNOWN GAP chứ KHÔNG phải control "đúng".
  - `datetime.now(*args)` / `now(**kw)` — có argument nên qua điều kiện (c). CHƯA canh.
  - Bash `date` không neo TZ: ngoài phạm vi (bin/utc_text_gate.sh canh nửa văn bản gửi người).
  - File .py NGOÀI `WC_ROOT` và ngoài mọi checkout mike (vd 20 worktree của repo ngoài ở
    /home/trido/thanhdt/wt-*) không có baseline-key ⇒ KHÔNG gate được. Từ 2026-08-30 gate KÊU
    ra stderr thay vì im (F2), nhưng vẫn không chặn.

⚠️ `pre-commit run --all-files` TRONG repo mike sẽ chạy tới nhánh auto-update và GHI + `git add`
baseline production NGOÀI mọi commit (không có cơ chế stash của commit thật che). Không script
nào trong fleet làm việc này hôm nay; nếu chạy tay thì kiểm `git status kb/` sau đó.

Escape hatch (cùng khuôn MIKE_CQ_GATE / MIKE_DIAG_GATE / MIKE_COMMIT_GATE):
env MIKE_TZ_GATE=warn hạ BLOCK xuống cảnh báo không chặn; =off tắt hẳn.
"""
import ast
import json
import os
import subprocess
import sys

MIKE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# MIKE_TZ_GATE_ROOT / _BASELINE / _ROOTS: override CHỈ dành cho sandbox của
# bin/tz_anchor_gate_selfcheck.py. CHỈ có hiệu lực khi ĐI KÈM MIKE_TZ_GATE_SELFCHECK=1 — một
# biến sót lại trong môi trường (shell còn export, cron kế thừa, wrapper quên unset) mà đổi được
# WC_ROOT là đủ biến gate production thành no-op im lặng: mọi file thành "ngoài WC_ROOT" ⇒
# không có baseline-key ⇒ rc=0 (đã repro, arch-review vòng 2 R4). Cùng khuôn với
# `_resolve_target()` ở phía selfcheck, vốn đã từ chối MIKE_TZ_GATE_TARGET không có cờ.
_SELFCHECK = os.environ.get("MIKE_TZ_GATE_SELFCHECK") == "1"
# CHỈ TÍNH ở module scope, KHÔNG raise ở đây: `MIKE_TZ_GATE=off` là công tắc tắt hẳn được
# docstring và tz_anchor_gate_shim.sh quảng cáo là lối thoát cuối; raise ở module scope chạy
# TRƯỚC khi main() đọc `mode` ⇒ một biến sót lại làm rc=1 trên file SẠCH mà KHÔNG lối thoát nào
# gỡ được — đúng hình dạng F1 mà cả bản vá này sinh ra để diệt (arch-review vòng 3).
_STRAY = [
    k for k in ("MIKE_TZ_GATE_ROOT", "MIKE_TZ_GATE_BASELINE", "MIKE_TZ_GATE_ROOTS")
    if os.environ.get(k) and not _SELFCHECK
]

WC_ROOT = (os.environ.get("MIKE_TZ_GATE_ROOT") if _SELFCHECK else None) or "/home/trido/thanhdt/WorkingClaude"
BASELINE = (os.environ.get("MIKE_TZ_GATE_BASELINE") if _SELFCHECK else None) or os.path.join(
    MIKE_ROOT, "kb", "tz_anchor_baseline.json"
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


def _alias_receivers(tree):
    """Tên cục bộ trỏ tới `datetime.datetime` / `datetime.date` trong CHÍNH file này.

    `from datetime import datetime as dtm` rồi `dtm.now()` là cùng một lỗi nhưng receiver không
    còn tên `datetime` ⇒ điều kiện (b) trượt. Đọc import của file thì bịt được, không cần đoán.
    (arch-review 2026-08-30 F8 — đo được 0 ca sống trong 2 repo, nhưng bịt là MIỄN PHÍ.)
    """
    names = set(DATETIME_RECEIVERS)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "datetime":
            for a in node.names:
                if a.name in DATETIME_RECEIVERS and a.asname:
                    names.add(a.asname)
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "datetime" and a.asname:
                    names.add(a.asname)  # `import datetime as dt` -> dt.datetime.now / dt.date.today
    return names


def _tz_arg_is_none(node):
    """`datetime.now(None)` / `datetime.now(tz=None)` — CÓ argument nhưng vô hiệu, naive y hệt."""
    for a in list(node.args) + [k.value for k in node.keywords]:
        if not (isinstance(a, ast.Constant) and a.value is None):
            return False
    return bool(node.args or node.keywords)


def violations(path):
    """-> [(lineno, 'datetime.now()' | 'date.today()')]; file không parse được -> []."""
    try:
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError, ValueError, UnicodeDecodeError):
        return []
    receivers = _alias_receivers(tree)
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr not in BAD_ATTRS:
            continue
        recv = _render(func.value)
        if recv.split(".")[-1] not in receivers:
            continue
        if (node.args or node.keywords) and not _tz_arg_is_none(node):
            continue
        hits.append((func.lineno, f"{recv}.{func.attr}()"))
    return sorted(hits)


# Không phải code của fleet (thư viện vendor / bản sao repo cũ đã chết) hoặc là artifact R&D —
# không gate, không tính vào baseline. `mike_paseo/` là bản SAO cũ của repo mike (git repo riêng,
# worktree đã hỏng, không repo nào track); gate nó = nuôi vi phạm ma trong baseline.
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
if _SELFCHECK and os.environ.get("MIKE_TZ_GATE_ROOTS"):  # selfcheck kiểm nhánh kiểm-kê-thiếu (F5)
    TRACKED_ROOTS = tuple(
        (spec.split("|", 1)[0], spec.split("|", 1)[1] if "|" in spec else "*.py")
        for spec in os.environ["MIKE_TZ_GATE_ROOTS"].split(":")
    )


def enumerate_tracked():
    """-> (paths, ok). ok=False khi BẤT KỲ root nào không đọc được — caller PHẢI không ghi đè
    baseline bằng một kiểm kê thiếu (arch-review 2026-08-30 F5: một root sai đường dẫn cho ra
    15 file/29 vi phạm thay vì 87/157, rc=0, commit được — 72 key biến mất thành ngầm-định-0 và
    mọi commit sau chạm chúng đều hard-block)."""
    paths = []
    ok = True
    for repo, pattern in TRACKED_ROOTS:
        r = subprocess.run(["git", "-C", repo, "ls-files", "-z", pattern],
                           capture_output=True, text=True, check=False)
        if r.returncode != 0:
            print(f"⚠️  không đọc được `git ls-files` ở {repo} — BỎ QUA cây này, kiểm kê sẽ THIẾU.",
                  file=sys.stderr)
            ok = False
            continue
        for rel in r.stdout.split("\0"):
            if rel.endswith(".py"):
                paths.append(os.path.join(repo, rel))
    return paths, ok


def scan_tree():
    """Kiểm kê toàn bộ vi phạm còn sót -> ({baseline_key: [(line, expr)]}, complete)."""
    found = {}
    paths, complete = enumerate_tracked()
    for p in paths:
        key = baseline_key(p)
        if key is None or is_excluded(key) or not os.path.isfile(p):
            continue
        hits = violations(p)
        if hits:
            found[key] = hits
    return found, complete


def in_mike_repo():
    """Top của checkout đang commit, NẾU top ĐÚNG LÀ checkout sở hữu BASELINE đang dùng.

    ⚠️ Điều kiện phải là `samefile(top/kb/tz_anchor_baseline.json, BASELINE)`, KHÔNG được viết
    thành "BASELINE nằm dưới top": repo lồng nằm BÊN TRONG cây thư mục của repo ngoài, nên
    `abspath(BASELINE).startswith(top + "/")` ĐÚNG cho cả top=/home/trido/thanhdt ⇒ commit từ
    repo NGOÀI sẽ ghi vào baseline của repo lồng rồi `git add` thất bại (path bị gitignore ở đó)
    và để lại dirt trong cây mà consolidate cron `git add -A` mỗi ~15 phút. Đó chính là lỗi
    arch-review vòng 2 (R1) tìm ra trong bản vá F7 của tôi — bản vòng 1 không có lỗ này.

    Vẫn neo theo BASELINE (không phải một tên file cứng) để selfcheck dựng được sandbox repo
    thật mà kiểm nhánh auto-update; điều kiện samefile giữ đúng cả hai tính chất.
    """
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
    except OSError:
        return None
    if not top:
        return None
    cand = os.path.join(top, "kb", "tz_anchor_baseline.json")
    try:
        return top if os.path.isfile(cand) and os.path.samefile(cand, BASELINE) else None
    except OSError:
        return None


def main(argv):
    mode = os.environ.get("MIKE_TZ_GATE", "block")
    if mode == "off":
        return 0

    if _STRAY:
        raise SystemExit(
            f"❌ tz_anchor_gate: {', '.join(_STRAY)} được đặt mà KHÔNG có MIKE_TZ_GATE_SELFCHECK=1 — "
            "biến này chỉ dành cho sandbox selfcheck; để nguyên sẽ gate SAI baseline hoặc no-op im "
            "lặng. Bỏ biến, chạy qua bin/tz_anchor_gate_selfcheck.py, hoặc MIKE_TZ_GATE=off."
        )

    args = list(argv)
    if args and args[0] == "--scan":
        found, _ = scan_tree()
        total = sum(len(v) for v in found.values())
        for key in sorted(found):
            for line, expr in found[key]:
                print(f"{key}:{line}: {expr}")
        print(f"\n{total} vi phạm / {len(found)} file", file=sys.stderr)
        return 0

    if args and args[0] == "--seed-baseline":
        # Kiểm kê lại toàn bộ nợ cũ và GHI ĐÈ baseline. Chỉ chạy tay khi cố ý re-seed (vd mở
        # rộng phạm vi gate); vận hành thường ngày dùng ratchet auto-update ở cuối hàm này.
        found, complete = scan_tree()
        if not complete:
            print("❌ kiểm kê KHÔNG đầy đủ (xem cảnh báo ở trên) — KHÔNG ghi đè baseline.",
                  file=sys.stderr)
            return 1
        data = {
            "_note": "Kiểm kê `datetime.now()` trần / `date.today()` (coding_guidelines §16) tại "
                     "thời điểm bật bin/tz_anchor_gate.py. Ratchet per-file: nợ cũ không bắt sửa "
                     "ngay, chỉ không được TĂNG. Re-seed: bin/tz_anchor_gate.py --seed-baseline",
            "files": {k: len(v) for k, v in found.items()},
        }
        write_baseline(data)
        print(f"✓ {BASELINE}: {sum(data['files'].values())} vi phạm / {len(data['files'])} file")
        return 0

    update_only = "--update-baseline" in args
    accept_new_debt = "--accept-new-debt" in args
    args = [a for a in args if not a.startswith("--")]

    baseline = load_baseline()
    files_baseline = baseline.setdefault("files", {})

    counts = {}
    detail = {}
    for f in args:
        if not os.path.isfile(f):
            continue
        key = baseline_key(f)
        if key is None:
            # KHÔNG được im (arch-review 2026-08-30 F2): 20 worktree của repo ngoài nằm ở
            # /home/trido/thanhdt/wt-*, ngoài WC_ROOT ⇒ trước bản này gate trả rc=0 không một
            # chữ, trong khi dna_report.py:69 `date.today()` vẫn sống nguyên ở đó. Cùng khuôn
            # cảnh báo với bin/code_quality_gate.sh:87.
            print(
                f"⚠️  tz_anchor_gate: {os.path.abspath(f)} nằm ngoài {WC_ROOT} và ngoài mọi "
                "checkout mike — KHÔNG có baseline-key, file này KHÔNG ĐƯỢC GATE.",
                file=sys.stderr,
            )
            continue
        if is_excluded(key):
            continue
        hits = violations(f)
        counts[key] = len(hits)
        detail[key] = hits

    if not counts:
        return 0

    if update_only:
        # NÂNG baseline = chấp nhận nợ MỚI vĩnh viễn. Config repo ngoài quảng cáo cờ này là cách
        # "siết bằng tay", nên mặc định nó chỉ được phép SIẾT (hạ) — muốn nới phải nói ra
        # (arch-review 2026-08-30 F4).
        raises = {k: n for k, n in counts.items() if n > files_baseline.get(k, 0)}
        if raises and not accept_new_debt:
            for k, n in sorted(raises.items()):
                print(f"  🔴 {k}: baseline {files_baseline.get(k, 0)} → {n} là NÂNG, không phải siết")
            print("--update-baseline mặc định CHỈ siết (hạ) baseline. Chấp nhận nợ mới thì nói rõ:")
            print("  bin/tz_anchor_gate.py --update-baseline --accept-new-debt <file.py>")
            return 1
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
        print("  Baseline neo theo checkout CANONICAL (master). Đang commit từ worktree/nhánh cũ và")
        print("  KHÔNG hề sửa chỗ đó? Đó là lệch nhánh, không phải nợ mới — rebase, hoặc")
        print("  SKIP=tz-anchor-gate git commit ... (bỏ qua đúng hook này, pre-commit hỗ trợ sẵn).")
        print("  Escape hatch: MIKE_TZ_GATE=warn git commit ...  (qua 1 lần, KHÔNG nâng baseline")
        print("  ⇒ lần commit sau vẫn chặn. Chấp nhận nợ mới thật thì:")
        print("  bin/tz_anchor_gate.py --update-baseline --accept-new-debt <file.py>)")
        if mode == "block":
            return 1
        # CỐ Ý KHÁC bin/code_quality_gate.sh: ở đó warn NÂNG baseline (nợ mới thành hợp lệ vĩnh
        # viễn chỉ vì một lần lách). Ở đây warn cho qua ĐÚNG lần này và dừng luôn — không ghi
        # baseline — nên "lách" không bao giờ âm thầm biến thành "chấp nhận"
        # (arch-review 2026-08-30 F3).
        print("⚠️  downgraded — MIKE_TZ_GATE=warn, commit vẫn qua. Baseline KHÔNG được nâng:")
        for key, old, new in blocked:
            print(f"    {key}: baseline giữ nguyên {old} (file đang {new}) ⇒ commit sau vẫn chặn.")
        return 0

    mike_top = in_mike_repo()
    if mike_top is None:
        # Commit từ repo NGOÀI: không ghi vào repo lồng rồi bỏ đó unstaged.
        return 0

    # Guard này chỉ có tác dụng khi chạy TAY: dưới pre-commit, staged_files_only.py (bản
    # ~/.local/lib/python3.10/site-packages/pre_commit/staged_files_only.py:80-82) đã stash mọi
    # thay đổi chưa stage + `git checkout -- .` TRƯỚC khi hook chạy, nên cây luôn sạch ở đó.
    # Giữ lại vì `--update-baseline`/chạy tay không đi qua cơ chế stash đó (arch-review F7).
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
