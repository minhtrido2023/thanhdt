#!/usr/bin/env python3
"""Preflight check for BQ local cache — run daily after sync, before any work.

Checks:
  1. Manifest exists, verified=true, age < 24h
  2. All 12 parquet files present and non-empty
  3. DuckDB can read every table (schema OK, no corrupt files)
  4. Smoke query: cross-table JOIN returns plausible data
  5. Spot check: latest VNINDEX close matches BQ (within tolerance)

Exit 0 = cache ready. Exit 1 = problem (details on stderr).
Designed to run from cron (after sync) or from dispatch.sh (before agent work).

Usage:
  python3 preflight_bq_cache.py              # full check (includes BQ spot check)
  python3 preflight_bq_cache.py --offline     # skip BQ spot check (no network needed)
"""
import json
import os
import sys
import time

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
CACHE_DIR = os.path.join(WORKDIR, "data", "bq_cache")
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.json")

EXPECTED_TABLES = [
    "ticker", "ticker_prune", "ticker_financial", "ticker_1m",
    "vnindex_5state_dt5g_live", "vnindex_5state",
    "vnindex_5state_tam_quan_v34b_clean", "vnindex_5state_dt_4gate",
    "fa_ratings", "fa_ratings_8l", "custom30v_8l", "risk_rating",
]

errors = []


def err(msg):
    errors.append(msg)
    print(f"FAIL: {msg}", file=sys.stderr, flush=True)


def ok(msg):
    print(f"  OK: {msg}", flush=True)


def check_manifest():
    if not os.path.exists(MANIFEST_PATH):
        err("manifest.json not found")
        return None
    with open(MANIFEST_PATH) as f:
        m = json.load(f)
    if not m.get("verified"):
        err("manifest verified=false — run sync_bq_cache.py --verify")
        return None
    age_h = (time.time() - m.get("verified_at_epoch", 0)) / 3600
    if age_h > 24:
        err(f"manifest verified {age_h:.0f}h ago (>24h) — re-run sync")
        return None
    ok(f"manifest verified {age_h:.1f}h ago")
    return m


def check_files(manifest):
    for name in EXPECTED_TABLES:
        info = manifest["tables"].get(name)
        if not info:
            err(f"table '{name}' missing from manifest")
            continue
        f = info["file"]
        path = os.path.join(CACHE_DIR, f)
        if f.endswith("/"):
            if not os.path.isdir(path):
                err(f"directory {path} missing for '{name}'")
                continue
            pq_files = [x for x in os.listdir(path) if x.endswith(".parquet")]
            if not pq_files:
                err(f"no parquet files in {path} for '{name}'")
                continue
        else:
            if not os.path.exists(path):
                err(f"file {path} missing for '{name}'")
                continue
            if os.path.getsize(path) == 0:
                err(f"file {path} is empty for '{name}'")
                continue
    if not errors:
        ok(f"all {len(EXPECTED_TABLES)} table files present")


def check_duckdb(manifest):
    try:
        import duckdb
    except ImportError:
        err("duckdb not installed")
        return None

    conn = duckdb.connect(":memory:")
    for name in EXPECTED_TABLES:
        info = manifest["tables"].get(name)
        if not info:
            continue
        f = info["file"]
        path = os.path.join(CACHE_DIR, f)
        if f.endswith("/"):
            path = os.path.join(path, "*.parquet")
        try:
            cnt = conn.execute(
                f"SELECT COUNT(*) FROM read_parquet('{path}')"
            ).fetchone()[0]
            expected = info["rows"]
            if abs(cnt - expected) > max(10, expected * 0.001):
                err(f"'{name}' row count {cnt} != manifest {expected}")
        except Exception as e:
            err(f"'{name}' DuckDB read failed: {e}")
    if not errors:
        ok("all tables readable by DuckDB")
    return conn


def check_smoke_query():
    os.environ["BQ_LOCAL_CACHE"] = CACHE_DIR
    try:
        from bq_local_cache import BQLocalCache
        cache = BQLocalCache(CACHE_DIR)
        df = cache.query("""
            SELECT p.time, p.ticker, p.Close, s.state
            FROM tav2_bq.ticker_prune AS p
            JOIN tav2_bq.vnindex_5state_dt5g_live AS s ON p.time = s.time
            WHERE p.ticker = 'FPT'
            ORDER BY p.time DESC
            LIMIT 5
        """)
        if len(df) == 0:
            err("smoke query returned 0 rows")
            return
        if "Close" not in df.columns or "state" not in df.columns:
            err(f"smoke query missing columns: {list(df.columns)}")
            return
        latest = df.iloc[0]
        if latest["Close"] <= 0:
            err(f"smoke query: FPT Close={latest['Close']} (<=0)")
            return
        ok(f"smoke query OK — FPT Close={latest['Close']}, state={latest['state']}, date={latest['time']}")
    except Exception as e:
        err(f"smoke query failed: {e}")


def check_spot_bq():
    """Spot check: compare latest VNINDEX close from cache vs BQ."""
    try:
        from bq_local_cache import BQLocalCache
        cache = BQLocalCache(CACHE_DIR)
        local = cache.query("""
            SELECT t.time, t.Close
            FROM tav2_bq.ticker AS t
            WHERE t.ticker = 'VNINDEX'
            ORDER BY t.time DESC
            LIMIT 1
        """)
        if local.empty:
            err("spot check: no VNINDEX data in cache")
            return

        import subprocess
        _bq_bin = os.environ.get("BQ_BIN", "/home/trido/google-cloud-sdk/bin/bq")
        _sdk_bin = os.path.dirname(_bq_bin)
        _env = {**os.environ, "PATH": os.environ.get("PATH", "") + ":" + _sdk_bin}
        result = subprocess.run(
            [_bq_bin, "query", "--use_legacy_sql=false", "--format=json",
             "--project_id=lithe-record-440915-m9",
             "SELECT t.time, t.Close FROM tav2_bq.ticker AS t "
             "WHERE t.ticker='VNINDEX' ORDER BY t.time DESC LIMIT 1"],
            capture_output=True, text=True, timeout=30, env=_env,
        )
        if result.returncode != 0:
            err(f"spot check: bq CLI failed — {result.stderr[:200]}")
            return

        bq_rows = json.loads(result.stdout)
        if not bq_rows:
            err("spot check: BQ returned no VNINDEX rows")
            return

        local_close = float(local.iloc[0]["Close"])
        bq_close = float(bq_rows[0]["Close"])
        local_date = str(local.iloc[0]["time"])[:10]
        bq_date = str(bq_rows[0]["time"])[:10]

        if local_date != bq_date:
            err(f"spot check: date mismatch — cache={local_date} vs BQ={bq_date}")
            return
        if abs(local_close - bq_close) > 1.0:
            err(f"spot check: VNINDEX close mismatch — cache={local_close} vs BQ={bq_close}")
            return
        ok(f"spot check: VNINDEX {local_date} Close={local_close} matches BQ")

    except Exception as e:
        err(f"spot check failed: {e}")


def main():
    offline = "--offline" in sys.argv
    print("=== BQ Cache Preflight Check ===", flush=True)

    manifest = check_manifest()
    if manifest is None:
        print(f"\nRESULT: FAIL ({len(errors)} error(s))", flush=True)
        sys.exit(1)

    check_files(manifest)
    if errors:
        print(f"\nRESULT: FAIL ({len(errors)} error(s))", flush=True)
        sys.exit(1)

    check_duckdb(manifest)
    if errors:
        print(f"\nRESULT: FAIL ({len(errors)} error(s))", flush=True)
        sys.exit(1)

    check_smoke_query()
    if errors:
        print(f"\nRESULT: FAIL ({len(errors)} error(s))", flush=True)
        sys.exit(1)

    if not offline:
        check_spot_bq()
        if errors:
            print(f"\nRESULT: FAIL ({len(errors)} error(s))", flush=True)
            sys.exit(1)

    print(f"\nRESULT: PASS — cache ready for local queries", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
