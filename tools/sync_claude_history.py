#!/usr/bin/env python3
"""Sync Claude Code memory + SCRUBBED session transcripts into this repo.

For every Claude project dir under ~/.claude/projects that belongs to this
workspace, copies memory/ verbatim and copies *.jsonl transcripts with all
secret values redacted. Redaction set = every string value found in any
credential-like JSON in the repo, plus PEM/token regex patterns, plus short
high-entropy prefixes (in case a secret was referenced partially).

Re-run any time to refresh the backup before committing. Safe to track: it
contains no secrets (it reads them at runtime).
"""
import os, re, json, glob, shutil, sys

REPO = "/home/trido/thanhdt"
WORK = os.path.join(REPO, "WorkingClaude")
PROJ = os.path.expanduser("~/.claude/projects")
# project dirs to back up (slugs under ~/.claude/projects)
PROJECT_DIRS = [
    "-home-trido-thanhdt-WorkingClaude",
    "-home-trido-thanhdt",
    "-home-trido",
]
MAX_BYTES = 95 * 1024 * 1024  # stay under GitHub's 100MB/file

# ---- collect secret string values from all credential-like JSON ------
def walk_strings(obj, out):
    if isinstance(obj, str):
        out.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values(): walk_strings(v, out)
    elif isinstance(obj, list):
        for v in obj: walk_strings(v, out)

CRED_HINTS = ("credential", "token", "secret", "account", "sa-key",
              "gcp_credentials", "telegram_config", "phs_", "dnse_", "bot_paper")
secret_vals = set()
for dp, dns, fns in os.walk(WORK):
    dns[:] = [d for d in dns if d not in ("__pycache__", ".git")]
    for fn in fns:
        if fn.endswith(".json") and not fn.endswith(".template.json") \
           and any(h in fn.lower() for h in CRED_HINTS):
            try:
                with open(os.path.join(dp, fn), encoding="utf-8") as fh:
                    walk_strings(json.load(fh), secret_vals)
            except Exception:
                pass

redactions = set(v for v in secret_vals if len(v) >= 6)
# add short prefixes of high-entropy secrets (partial-reference safety)
for v in list(redactions):
    if len(v) >= 16 and re.search(r"[A-Z]", v) and re.search(r"[0-9a-z]", v):
        for ln in (8, 10, 12, 16):
            if len(v) > ln:
                redactions.add(v[:ln])
redactions = sorted(redactions, key=len, reverse=True)
print(f"redaction set: {len(redactions)} values/prefixes")

# ---- single-pass scrubber -------------------------------------------
PATTERNS = [
    # strip long base64 blobs (embedded chart/screenshot images, or any DER key
    # material) — tolerate JSON-escaped slashes; replace with a placeholder.
    (re.compile(r"(?:[A-Za-z0-9+/=]|\\/){64,}"), "[BINARY_STRIPPED]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "[REDACTED]"),
    (re.compile(r"\d{8,10}:[A-Za-z0-9_-]{35}"), "[REDACTED]"),  # telegram bot token (also placeholders)
    # discord bot token: <base64 id>.<timestamp>.<hmac> — lives in repo-root discord_bot/
    # config.json (outside this scrubber's WorkingClaude value-scan), so match it by shape.
    (re.compile(r"[A-Za-z0-9_-]{23,28}\.[A-Za-z0-9_-]{6,7}\.[A-Za-z0-9_-]{27,38}"), "[REDACTED]"),  # discord bot token
]
_alt = re.compile("|".join(re.escape(r) for r in redactions)) if redactions else None
_alt_esc = re.compile("|".join(re.escape(json.dumps(r)[1:-1]) for r in redactions
                               if json.dumps(r)[1:-1] != r)) if redactions else None

def scrub(text):
    n = 0
    for rgx, rep in PATTERNS:
        text, c = rgx.subn(rep, text); n += c
    if _alt:
        text, c = _alt.subn("[REDACTED]", text); n += c
    if _alt_esc:
        text, c = _alt_esc.subn("[REDACTED]", text); n += c
    return text, n

def verify(text):
    for r in redactions:
        if r in text or json.dumps(r)[1:-1] in text:
            return r[:12]
    for rgx, rep in PATTERNS:
        if rgx.search(text):
            return rgx.pattern[:24]
    return None

# ---- process each project dir ---------------------------------------
mem_root = os.path.join(REPO, "claude_memory")
ses_root = os.path.join(REPO, "claude_sessions")
total_red = 0; total_files = 0; leaks = 0; skipped = []
for pd_name in PROJECT_DIRS:
    src = os.path.join(PROJ, pd_name)
    if not os.path.isdir(src):
        continue
    slug = pd_name.lstrip("-")
    # memory (SCRUBBED — notes can accidentally record credentials)
    msrc = os.path.join(src, "memory")
    if os.path.isdir(msrc):
        mdst = os.path.join(mem_root, slug)
        shutil.rmtree(mdst, ignore_errors=True)
        for mdp, mdns, mfns in os.walk(msrc):
            rel = os.path.relpath(mdp, msrc)
            os.makedirs(os.path.join(mdst, rel), exist_ok=True)
            for mfn in mfns:
                sp = os.path.join(mdp, mfn); dpth = os.path.join(mdst, rel, mfn)
                try:
                    with open(sp, encoding="utf-8") as fh:
                        clean, _ = scrub(fh.read())
                    bad = verify(clean)
                    if bad:
                        print(f"  MEMORY LEAK {bad}... in {mfn}"); leaks += 1; continue
                    with open(dpth, "w", encoding="utf-8") as fh:
                        fh.write(clean)
                except (UnicodeDecodeError, OSError):
                    shutil.copy2(sp, dpth)
    # transcripts
    sdst = os.path.join(ses_root, slug)
    shutil.rmtree(sdst, ignore_errors=True)
    os.makedirs(sdst, exist_ok=True)
    for f in glob.glob(os.path.join(src, "*.jsonl")):
        with open(f, encoding="utf-8") as fh:
            clean, n = scrub(fh.read())
        if len(clean.encode()) > MAX_BYTES:
            skipped.append((os.path.basename(f), len(clean)))
            continue
        bad = verify(clean)
        if bad:
            leaks += 1; print(f"  LEAK {bad}... in {os.path.basename(f)}"); continue
        with open(os.path.join(sdst, os.path.basename(f)), "w", encoding="utf-8") as fh:
            fh.write(clean)
        total_red += n; total_files += 1
    print(f"  {slug}: {len(glob.glob(os.path.join(sdst,'*.jsonl')))} sessions")

print(f"\nfiles written: {total_files} | redactions: {total_red}")
if skipped:
    print(f"SKIPPED (>{MAX_BYTES//1048576}MB): {skipped}")
print("VERIFY:", "CLEAN ✅" if leaks == 0 else f"{leaks} LEAKS ❌")
sys.exit(1 if leaks else 0)
