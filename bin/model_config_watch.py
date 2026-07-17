#!/usr/bin/env python3
"""model_config_watch.py [--oneline]

Cost-optimization #4 (2026-07-17) — smoke-test for a class of bug that has caused
2 real incidents this week: the ccdb-mike Discord bridge resolves its model through
3 layers (thread override > global override in sessions.db > .env fallback), and a
malformed value at ANY layer (e.g. "Sonnet 5" with a space — invalid for the claude
CLI's --model flag) silently breaks session spawns until someone notices.

Input validation was added at the WRITE path (backend_command.py's /model command,
2026-07-17) to prevent new bad values — this script is the READ-side second layer:
periodically confirm the values actually sitting in .env and the DB are still valid,
catching anything that bypassed the validated command path (direct DB edit, a bug
in the validation itself, a future code path that also calls set_model()).

Cheap and read-only: no BQ, no network calls, just two local files.

  model_config_watch.py            -> human summary, exit 1 if any bad value found
  model_config_watch.py --oneline  -> "STATUS detail" for watchdog.sh (STATUS=ok|bad)
"""
import os
import re
import sqlite3
import sys

ENV_PATH = "/workspace/ccdb-mike/.env"
DB_PATH = "/workspace/ccdb-mike/data/sessions.db"

# Same rule as the write-side validation: no valid model id (alias like "sonnet",
# full name like "claude-sonnet-5", or a codex name like "gpt-5.4") ever contains
# whitespace. Kept intentionally simple/permissive beyond that — this check exists
# to catch the exact failure mode already seen twice, not to police every possible
# future model-naming convention.
def _is_bad(value: str) -> bool:
    return bool(value) and any(c.isspace() for c in value)


def _read_env_model() -> str | None:
    try:
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^CCDB_MODEL=(.*)$", line.strip())
                if m:
                    return m.group(1)
    except Exception:
        return None
    return None


def _read_db_settings() -> list[tuple[str, str]]:
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=2)
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM settings WHERE key LIKE '%model%'")
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def main():
    oneline = "--oneline" in sys.argv[1:]
    bad = []

    env_model = _read_env_model()
    if env_model is not None and _is_bad(env_model):
        bad.append(("CCDB_MODEL (.env)", env_model))

    for key, value in _read_db_settings():
        if _is_bad(value):
            bad.append((f"sessions.db:{key}", value))

    if oneline:
        if bad:
            detail = "; ".join(f"{k}={v!r}" for k, v in bad)
            print(f"bad {detail}")
        else:
            print("ok -")
        return

    print("ccdb-mike model config check")
    print(f"  .env CCDB_MODEL: {env_model!r}")
    for key, value in _read_db_settings():
        print(f"  {key}: {value!r}")
    if bad:
        print(f"  FAIL — {len(bad)} malformed value(s): {bad}")
        sys.exit(1)
    print("  OK — no whitespace-containing model ids found")


if __name__ == "__main__":
    main()
