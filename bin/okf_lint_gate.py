#!/usr/bin/env python3
"""okf_lint_gate.py — pre-commit gate cho chuẩn OKF trong `kb/**/*.md`.

Chặn:
1. Thiếu YAML frontmatter (`kind`, `owner`, `status`, `updated`) trong các cây OKF.
2. File `kb/**/*.md` vượt ngưỡng 40 KB (ratchet cho file cũ >40 KB: chỉ chặn nếu tăng size).
3. Liên kết tương đối `.md` bị gãy trong file vừa sửa/tạo.

Escape hatch (MIKE_OKF_GATE): block (mặc định) | warn | off.
"""
import os
import re
import subprocess
import sys

LIMIT_BYTES = 40 * 1024  # 40 KB

OKF_TREES = (
    "kb/data_registry/",
    "kb/incidents/",
    "kb/projects/",
    "kb/research_notes/",
    "kb/coding_guidelines_topics/",
    "kb/ops_runbook_playbooks/",
)

REQUIRED_KEYS = ("kind", "owner", "status", "updated")

SIZE_EXEMPT = {
    "kb/context_pack.md",
    "kb/events_buffer.md",
}

SIZE_EXEMPT_PREFIXES = (
    "kb/archive/",
    "kb/memory/",
)


def _staged_kb_mds():
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--no-renames", "--diff-filter=AM", "-z"],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode(errors="replace").strip() or "git diff --cached failed")
    raw = r.stdout.decode("utf-8", errors="surrogateescape")
    return [p for p in raw.split("\0") if p.startswith("kb/") and p.endswith(".md")]


def _git_size(spec):
    r = subprocess.run(["git", "cat-file", "-s", spec], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return int(r.stdout.strip())
    except ValueError:
        return None


def _git_text(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        return ""
    return r.stdout.decode("utf-8", errors="replace")


def _strip_code(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", "", text)
    return text


def _is_exempt_fm(path):
    base = os.path.basename(path)
    return base in ("CHANGELOG.md", "README.md", "INDEX.md") or base.startswith("_")


def check_file(path, text, staged_sz, head_sz, repo_root):
    errs = []

    # 1. Size check (<= 40 KB, ratchet for pre-existing >40 KB files)
    if path not in SIZE_EXEMPT and not path.startswith(SIZE_EXEMPT_PREFIXES):
        if staged_sz is not None and staged_sz > LIMIT_BYTES:
            if head_sz is None or staged_sz > head_sz:
                errs.append(f"vuot nguong 40KB ({staged_sz // 1024}KB; head={head_sz})")

    # 2. Frontmatter check in OKF trees
    if path.startswith(OKF_TREES) and not _is_exempt_fm(path):
        m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
        if not m:
            errs.append("thieu YAML frontmatter (--- ... ---)")
        else:
            fm = m.group(1)
            # Legacy grandfathered files in kb/data_registry/ edited from HEAD only require `kind`
            if path.startswith("kb/data_registry/") and head_sz is not None:
                req = ("kind",)
            else:
                req = REQUIRED_KEYS
            missing = [k for k in req if not re.search(rf"^{k}:", fm, re.M)]
            if missing:
                errs.append(f"frontmatter thieu truong: {', '.join(missing)}")

    # 3. Relative .md link check (skip fenced/inline code and template tokens)
    cleaned = _strip_code(text)
    file_dir = os.path.dirname(os.path.join(repo_root, path))
    for lm in re.finditer(r"\[[^\]]+\]\(([^)\s]+)\)", cleaned):
        target = lm.group(1).split("#", 1)[0]
        if not target or not target.endswith(".md"):
            continue
        if target.startswith(("http://", "https://", "file://", "mailto:")):
            continue
        if any(ch in target for ch in ("<", ">", "*", "{", "}")):
            continue
        # Only check relative paths (not repo-root-relative paths like kb/foo.md)
        if target.startswith(("kb/", "mike/")):
            continue
        resolved = os.path.normpath(os.path.join(file_dir, target))
        if not os.path.exists(resolved):
            # Also check if the link target is staged in the same commit
            rel_repo = os.path.relpath(resolved, repo_root).replace("\\", "/")
            if _git_size(":" + rel_repo) is None:
                errs.append(f"broken link: {target}")

    return errs


def main():
    mode = os.environ.get("MIKE_OKF_GATE", "block")
    if mode == "off":
        return 0
    try:
        paths = _staged_kb_mds()
    except Exception as exc:
        print(f"⚠️  okf-lint-gate ERRORED (commit allowed): {exc}", file=sys.stderr)
        return 0

    if not paths:
        return 0

    repo_root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    ).stdout.strip() or os.getcwd()

    violations = []
    for p in paths:
        st_sz = _git_size(":" + p)
        hd_sz = _git_size("HEAD:" + p)
        txt = _git_text(":" + p)
        for e in check_file(p, txt, st_sz, hd_sz, repo_root):
            violations.append((p, e))

    if not violations:
        return 0

    lines = [f"⛔ okf-lint-gate: phat hien {len(violations)} vi pham chuan OKF:"]
    for p, reason in violations[:20]:
        lines.append(f"  - {p}: {reason}")
    if len(violations) > 20:
        lines.append(f"  ... va {len(violations) - 20} muc khac")
    lines.append("Bo qua khan: MIKE_OKF_GATE=warn git commit ...")
    msg = "\n".join(lines)
    if mode == "warn":
        print(msg.replace("⛔", "⚠️  (warn, khong chan)"))
        return 0
    print(msg, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
