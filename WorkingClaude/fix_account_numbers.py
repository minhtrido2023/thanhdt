#!/usr/bin/env python3
"""Script một lần: xóa hardcoded DNSE account numbers khỏi git-tracked files.

Chạy: python3 fix_account_numbers.py
"""
import re, os, json, shutil

BASE = os.path.dirname(os.path.abspath(__file__))

SPACEX = "0002023347"
ZALOPAY = "0001743768"

IMPORT_LINE = "from trading_bot.account_ids import SPACEX as SPACEX_ACCOUNT, ZALOPAY as ZALOPAY_ACCOUNT\n"

# ── Python files: inject import + replace literals ────────────────────────────
PY_FILES = [
    "capit_lever_selfcheck.py",
    "cash_only_loan_package_selfcheck.py",
    "dnse_api_full_test.py",
    "exdate_price_frame_selfcheck.py",
    "loan_package_resolution_selfcheck.py",
    "order_book_shadow_selfcheck.py",
    "plan_buying_power_shadow_replay.py",
    "quote_l2_logging_selfcheck.py",
    "verify_broker_readonly.py",
]

def inject_import_and_replace(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if "account_ids" in content:
        print(f"  SKIP (already imported): {os.path.basename(path)}")
    else:
        lines = content.split("\n")
        # Find last import line
        last_import = -1
        for i, line in enumerate(lines):
            if re.match(r"^(import|from)\s", line):
                last_import = i
        if last_import >= 0:
            lines.insert(last_import + 1, IMPORT_LINE.rstrip())
        else:
            # No imports found — insert after shebang/encoding comment block
            insert_at = 0
            in_docstring = False
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("#"):
                    insert_at = i + 1
                elif stripped.startswith('"""') or stripped.startswith("'''"):
                    if not in_docstring:
                        in_docstring = True
                        insert_at = i + 1
                    else:
                        in_docstring = False
                        insert_at = i + 1
                elif in_docstring:
                    insert_at = i + 1
                elif stripped == "" and i < 5:
                    insert_at = i + 1
                else:
                    break
            lines.insert(insert_at, IMPORT_LINE.rstrip())
        content = "\n".join(lines)
        print(f"  + import injected: {os.path.basename(path)}")

    # Replace string literals (quoted)
    content = re.sub(r'(["\'])' + SPACEX + r'\1', r'\1SPACEX_ACCOUNT\1', content)
    content = re.sub(r'(["\'])' + ZALOPAY + r'\1', r'\1ZALOPAY_ACCOUNT\1', content)

    # After inject, fix the quoted constants that now look like "SPACEX_ACCOUNT" → bare name
    # The replacement above turns "0002023347" → "SPACEX_ACCOUNT" (still quoted)
    # We want the unquoted variable name for Python identifiers
    content = content.replace('"SPACEX_ACCOUNT"', "SPACEX_ACCOUNT")
    content = content.replace("'SPACEX_ACCOUNT'", "SPACEX_ACCOUNT")
    content = content.replace('"ZALOPAY_ACCOUNT"', "ZALOPAY_ACCOUNT")
    content = content.replace("'ZALOPAY_ACCOUNT'", "ZALOPAY_ACCOUNT")

    # Replace remaining bare occurrences (in comments, strings-in-data)
    content = content.replace(SPACEX, "[SPACEX-ACCOUNT]")
    content = content.replace(ZALOPAY, "[ZALOPAY-ACCOUNT]")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ {os.path.basename(path)}")


for rel in PY_FILES:
    path = os.path.join(BASE, rel)
    if os.path.exists(path):
        print(f"Processing {rel}:")
        inject_import_and_replace(path)
    else:
        print(f"  NOT FOUND: {rel}")

# ── Markdown/text docs: mask account numbers ─────────────────────────────────
DOC_FILES = [
    "trading_bot/README.md",
    "data/results_registry.md",
]

for rel in DOC_FILES:
    path = os.path.join(BASE, rel)
    if not os.path.exists(path):
        print(f"NOT FOUND: {rel}")
        continue
    with open(path, encoding="utf-8") as f:
        content = f.read()
    content = content.replace(SPACEX, "[SPACEX-ACCOUNT]")
    content = content.replace(ZALOPAY, "[ZALOPAY-ACCOUNT]")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ {rel}")

# ── JSON fixtures: replace account_no values ─────────────────────────────────
FIXTURE_FILES = [
    "data/fixtures/state_TV1_SpaceX_active_20260728.json",
    "data/fixtures/state_TV1_SpaceX_pct_20260812.json",
    "data/fixtures/state_TV1_ZaloPay_pct_20260812.json",
]

for rel in FIXTURE_FILES:
    path = os.path.join(BASE, rel)
    if not os.path.exists(path):
        print(f"NOT FOUND: {rel}")
        continue
    with open(path, encoding="utf-8") as f:
        content = f.read()
    content = content.replace(SPACEX, "[SPACEX-ACCOUNT]")
    content = content.replace(ZALOPAY, "[ZALOPAY-ACCOUNT]")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ {rel}")

print("\nDone. Verify: grep -r '0002023347\\|0001743768' . --include='*.py' --include='*.md' --include='*.json' | grep -v __pycache__")
