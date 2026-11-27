#!/usr/bin/env python3
"""repo_hygiene_gate.py — pre-commit gate chan rac, binary/CSV lon va file lac cho.

Chay tren cac file moi/sua trong staged index (`git diff --cached --name-only --no-renames --diff-filter=AM -z`).
Modes (env MIKE_HYGIENE_GATE):
  block (mac dinh) — chan commit khi vi pham.
  warn             — in canh bao, cho qua (rc=0).
  off              — tat gate.
"""
import os
import subprocess
import sys

MAX_BYTES = 1024 * 1024  # 1 MB

ROOT_ALLOWLIST = {
    "MIKE.md",
    "MIKE_ext.md",
    "CHILD_TEMPLATE.md",
    "SETUP.md",
    ".gitignore",
    ".pre-commit-config.yaml",
    "bin",
    "hooks",
    "config",
    "kb",
    "agents",
    "agents_native",
    "reports",
    "data",
    "tests",
    "systemd",
    "templates",
    "decision_templates",
    "webui_work_tree",
    "backups",
    "docs",
    "research",
    ".claude",
}

LARGE_ALLOWLIST = {
    "kb/dd_price_zones.json",
    "kb/production_manifest.json",
    "kb/paper_programs_registry.json",
    "kb/cron_registry.md",
    "kb/events_buffer.md",
}

BINARY_EXTS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".parquet",
    ".pkl",
    ".zip",
    ".xlsx",
    ".xls",
    ".bin",
    ".gz",
}


def _git_size(spec):
    """Return byte size of git object spec (':path' or 'HEAD:path'), or None if absent."""
    r = subprocess.run(["git", "cat-file", "-s", spec], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return int(r.stdout.strip())
    except ValueError:
        return None


def _staged_files():
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--no-renames", "--diff-filter=AM", "-z"],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode(errors="replace").strip() or "git diff --cached failed")
    raw = r.stdout.decode("utf-8", errors="surrogateescape")
    return [p for p in raw.split("\0") if p]


def check_path(path, staged_size, head_size):
    """Return list of violation messages for one staged path."""
    errs = []
    parts = path.split("/")
    top = parts[0]
    base = parts[-1]
    lower = base.lower()
    ext = ("." + lower.rsplit(".", 1)[1]) if "." in base else ""

    if top not in ROOT_ALLOWLIST:
        errs.append(f"root entry ngoai allowlist: {top}")

    # Allow reports/*.md.bak_sent_* intentionally (used by fund_restatement.py)
    if ".bak_sent_" in base:
        return errs

    if base == "=" or top == "MagicMock":
        errs.append("file/dir rac thu nghiem (= hoac MagicMock)")
    if lower.endswith((".lock", ".tmp")) or ".retired-" in lower:
        errs.append("file tam/khoa (.lock/.tmp/.retired-*)")
    if top.startswith("wt-") or (top == "agents" and len(parts) >= 3 and parts[2].startswith("wt-")):
        errs.append("worktree dir khong duoc commit")
    if path.startswith("reports/v2/draft/"):
        errs.append("ban nhap reports/v2/draft/ khong duoc commit")
    if lower.endswith(".diff") and (
        len(parts) == 1
        or top == "bin"
        or (top == "agents" and len(parts) == 3)
    ):
        errs.append("file .diff rac o root/bin/agents/<Name>/")

    if staged_size is not None and staged_size > MAX_BYTES and path not in LARGE_ALLOWLIST:
        errs.append(f"vuot nguong {MAX_BYTES // 1024}KB ({staged_size // 1024}KB)")

    if top in ("kb", "agents"):
        if ext in BINARY_EXTS:
            errs.append(f"duoi binary/raw ({ext}) bi cam trong {top}/")
        elif ext == ".csv":
            if head_size is None:
                errs.append(f"file .csv moi bi cam trong {top}/ (hay dat trong data/ ngoai repo)")
            elif staged_size is not None and staged_size > head_size:
                errs.append(f"file .csv trong {top}/ tang size ({head_size} -> {staged_size}B)")

    return errs


def main():
    mode = os.environ.get("MIKE_HYGIENE_GATE", "block")
    if mode == "off":
        return 0
    try:
        paths = _staged_files()
    except Exception as exc:
        print(f"⚠️  repo-hygiene-gate ERRORED (commit allowed): {exc}", file=sys.stderr)
        return 0

    if not paths:
        return 0

    violations = []
    for path in paths:
        try:
            st_sz = _git_size(":" + path)
            hd_sz = _git_size("HEAD:" + path)
            errs = check_path(path, st_sz, hd_sz)
            for e in errs:
                violations.append((path, e))
        except Exception as exc:
            print(f"⚠️  repo-hygiene-gate WARN skipping {path}: {exc}", file=sys.stderr)

    if not violations:
        return 0

    lines = [
        f"⛔ repo-hygiene-gate: phat hien {len(violations)} vi pham ve sinh repo:",
    ]
    for p, reason in violations[:20]:
        lines.append(f"  - {p}: {reason}")
    if len(violations) > 20:
        lines.append(f"  ... va {len(violations) - 20} muc khac")
    lines.append("Bo qua khan (chi khi co ly do): MIKE_HYGIENE_GATE=warn git commit ...")
    msg = "\n".join(lines)
    if mode == "warn":
        print(msg.replace("⛔", "⚠️  (warn, khong chan)"))
        return 0
    print(msg, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
