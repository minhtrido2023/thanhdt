#!/usr/bin/env python3
"""Download BQ tables to local parquet cache + verify integrity once daily.

Usage:
  python3 sync_bq_cache.py              # full sync + verify
  python3 sync_bq_cache.py --delta      # delta only (append today's rows)
  python3 sync_bq_cache.py --verify     # verify only (no download)
  python3 sync_bq_cache.py --tables ticker ticker_financial   # sync specific tables

Cache dir: data/bq_cache/ (relative to WORKDIR).
Manifest: data/bq_cache/manifest.json — records row counts, max dates, verification.
"""
import argparse
import io
import json
import os
import subprocess
import sys
import time

import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"

# Columns that must be stored as date32 (not VARCHAR) in parquet.
# quarter is intentionally excluded — it's a string like "2025Q3".
DATE_COLS = {"time", "Release_Date", "rebal_date", "effective_from", "effective_to"}


def _apply_date_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Cast known date columns from string → datetime.date so parquet stores date32."""
    for col in DATE_COLS:
        if col in df.columns and df[col].dtype == object:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df
CACHE_DIR = os.path.join(WORKDIR, "data", "bq_cache")
PROJECT = "lithe-record-440915-m9"
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.json")

# Use bq CLI (gcloud auth login creds) — no ADC/Application-Default required
BQ_BIN = os.environ.get("BQ_BIN", "/home/trido/google-cloud-sdk/bin/bq")
# bq internally calls gcloud (same SDK dir); ensure it's on PATH for subprocess calls
_SDK_BIN = os.path.dirname(BQ_BIN)
_SUBPROCESS_ENV = {**os.environ, "PATH": os.environ.get("PATH", "") + ":" + _SDK_BIN}

# ── Table definitions ────────────────────────────────────────────────────────
# Each table: full SQL for initial download, partition column for delta,
# and optional WHERE filter for the initial load.
TABLES = {
    "ticker": {
        "sql": """
            SELECT *
            FROM `{project}.tav2_bq.ticker` AS t
            WHERE t.time >= '2013-01-01'
        """,
        "partition_col": "time",
        "chunk_years": list(range(2013, 2028)),
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.ticker` AS t
            WHERE t.time >= '2013-01-01'
        """,
    },
    "ticker_prune": {
        "sql": """
            SELECT *
            FROM `{project}.tav2_bq.ticker_prune` AS t
            WHERE t.time >= '2013-01-01'
        """,
        "partition_col": "time",
        "chunk_years": list(range(2013, 2028)),
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.ticker_prune` AS t
            WHERE t.time >= '2013-01-01'
        """,
    },
    "ticker_financial": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.ticker_financial` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.ticker_financial` AS t
        """,
    },
    "ticker_1m": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.ticker_1m` AS t
        """,
        "partition_col": None,  # always full re-download (rolling snapshot)
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.ticker_1m` AS t
        """,
    },
    "vnindex_5state_dt5g_live": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.vnindex_5state_dt5g_live` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.vnindex_5state_dt5g_live` AS t
        """,
    },
    "vnindex_5state": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.vnindex_5state` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.vnindex_5state` AS t
        """,
    },
    "vnindex_5state_tam_quan_v34b_clean": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.vnindex_5state_tam_quan_v34b_clean` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.vnindex_5state_tam_quan_v34b_clean` AS t
        """,
    },
    "vnindex_5state_dt_4gate": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.vnindex_5state_dt_4gate` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.vnindex_5state_dt_4gate` AS t
        """,
    },
    "fa_ratings": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.fa_ratings` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.fa_ratings` AS t
        """,
    },
    "fa_ratings_8l": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.fa_ratings_8l` AS t
        """,
        "partition_col": "time",
        "verify_sql": """
            SELECT COUNT(*) AS cnt, MAX(t.time) AS max_time
            FROM `{project}.tav2_bq.fa_ratings_8l` AS t
        """,
    },
    "custom30v_8l": {
        "sql": """
            SELECT * FROM `{project}.tav2_bq.custom30v_8l` AS t
        """,
        "partition_col": None,  # no time column — always full
        "verify_sql": """
            SELECT COUNT(*) AS cnt
            FROM `{project}.tav2_bq.custom30v_8l` AS t
        """,
    },
    "risk_rating": {
        "sql": """
            SELECT DISTINCT * FROM `{project}.tav2_bq.risk_rating` AS t
        """,
        "partition_col": None,
        "verify_sql": """
            SELECT COUNT(*) AS cnt FROM (
                SELECT DISTINCT * FROM `{project}.tav2_bq.risk_rating` AS t
            )
        """,
    },
}


def log(msg: str):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"{ts} {msg}", flush=True)


def bq_query_to_df(sql: str, max_rows: int = 10_000_000) -> pd.DataFrame:
    """Run a BQ query via bq CLI subprocess, return DataFrame.

    Uses gcloud auth login credentials (no ADC/Application-Default required).
    """
    sql = sql.format(project=PROJECT)
    result = subprocess.run(
        [
            BQ_BIN, "query",
            "--use_legacy_sql=false",
            f"--project_id={PROJECT}",
            "--format=csv",
            f"--max_rows={max_rows}",
        ],
        input=sql,
        capture_output=True,
        text=True,
        timeout=300,
        env=_SUBPROCESS_ENV,
    )
    if result.returncode != 0:
        raise RuntimeError(f"bq CLI error: {result.stderr.strip()}")
    stdout = result.stdout.strip()
    if not stdout:
        return pd.DataFrame()
    df = pd.read_csv(io.StringIO(stdout))
    return _apply_date_dtypes(df)


def load_manifest() -> dict:
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {"tables": {}, "verified": False}


def save_manifest(manifest: dict):
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2, default=str)


def download_table(name: str, config: dict, manifest: dict, delta: bool):
    """Download a table to parquet. Delta mode appends only new rows."""
    pq_path = os.path.join(CACHE_DIR, f"{name}.parquet")
    table_info = manifest["tables"].get(name, {})

    chunk_years = config.get("chunk_years")

    if delta and config["partition_col"] and chunk_years:
        chunk_dir = os.path.join(CACHE_DIR, name)
        max_cached = table_info.get("max_time")
        if max_cached and os.path.isdir(chunk_dir):
            max_year = int(max_cached[:4])
            log(f"  {name}: delta — re-downloading {max_year}+ ...")
            col = config["partition_col"]
            total_rows = 0
            max_time_val = None
            for yr in chunk_years:
                yr_path = os.path.join(chunk_dir, f"{yr}.parquet")
                if yr < max_year and os.path.exists(yr_path):
                    yr_rows = len(pd.read_parquet(yr_path, columns=[col]))
                    total_rows += yr_rows
                    continue
                yr_sql = (
                    config["sql"]
                    + f" AND t.{col} >= '{yr}-01-01' AND t.{col} < '{yr + 1}-01-01'"
                )
                yr_df = bq_query_to_df(yr_sql)
                if not yr_df.empty:
                    yr_df.to_parquet(yr_path, index=False)
                    total_rows += len(yr_df)
                    yr_max = pd.to_datetime(yr_df[col]).max()
                    if max_time_val is None or yr_max > max_time_val:
                        max_time_val = yr_max
                    log(f"    {yr}: {len(yr_df)} rows")
            table_info["rows"] = total_rows
            if max_time_val is not None:
                table_info["max_time"] = str(max_time_val.date())
            manifest["tables"][name] = table_info
            log(f"  {name}: {total_rows} total rows")
            return

    if delta and config["partition_col"] and os.path.exists(pq_path):
        max_cached = table_info.get("max_time")
        if max_cached:
            log(f"  {name}: delta from {max_cached}")
            col = config["partition_col"]
            delta_sql = config["sql"] + f" AND t.{col} > '{max_cached}'"
            new_df = bq_query_to_df(delta_sql)
            if new_df.empty:
                log(f"  {name}: no new rows")
                return
            existing = pd.read_parquet(pq_path)
            combined = pd.concat([existing, new_df], ignore_index=True)
            combined.to_parquet(pq_path, index=False)
            table_info["rows"] = len(combined)
            if col in combined.columns:
                table_info["max_time"] = str(
                    pd.to_datetime(combined[col]).max().date()
                )
            log(f"  {name}: +{len(new_df)} rows → {len(combined)} total")
            manifest["tables"][name] = table_info
            return

    # Full download — chunk by year for large partitioned tables to avoid token expiry
    chunk_years = config.get("chunk_years")
    if chunk_years:
        log(f"  {name}: chunked download ({chunk_years[0]}–{chunk_years[-1]})...")
        col = config["partition_col"]
        chunk_dir = os.path.join(CACHE_DIR, name)
        os.makedirs(chunk_dir, exist_ok=True)
        total_rows = 0
        max_time_val = None
        for yr in chunk_years:
            yr_sql = (
                config["sql"]
                + f" AND t.{col} >= '{yr}-01-01' AND t.{col} < '{yr + 1}-01-01'"
            )
            yr_df = bq_query_to_df(yr_sql)
            if not yr_df.empty:
                yr_path = os.path.join(chunk_dir, f"{yr}.parquet")
                yr_df.to_parquet(yr_path, index=False)
                total_rows += len(yr_df)
                yr_max = pd.to_datetime(yr_df[col]).max()
                if max_time_val is None or yr_max > max_time_val:
                    max_time_val = yr_max
                log(f"    {yr}: {len(yr_df)} rows")
        if total_rows == 0:
            log(f"  {name}: 0 rows (empty)")
            return
        total_size = sum(
            os.path.getsize(os.path.join(chunk_dir, f))
            for f in os.listdir(chunk_dir) if f.endswith(".parquet")
        ) / 1e6
        table_info = {
            "file": f"{name}/",
            "rows": total_rows,
            "size_mb": round(total_size, 1),
        }
        if max_time_val is not None:
            table_info["max_time"] = str(max_time_val.date())
        manifest["tables"][name] = table_info
        log(f"  {name}: {total_rows} rows, {total_size:.1f} MB")
        return

    log(f"  {name}: full download...")
    df = bq_query_to_df(config["sql"])

    if df.empty:
        log(f"  {name}: 0 rows (empty)")
        return

    df.to_parquet(pq_path, index=False)
    size_mb = os.path.getsize(pq_path) / 1e6
    table_info = {
        "file": f"{name}.parquet",
        "rows": len(df),
        "size_mb": round(size_mb, 1),
    }
    if config["partition_col"] and config["partition_col"] in df.columns:
        table_info["max_time"] = str(
            pd.to_datetime(df[config["partition_col"]]).max().date()
        )
    manifest["tables"][name] = table_info
    log(f"  {name}: {len(df)} rows, {size_mb:.1f} MB")


def _check_parquet_date_dtypes(pq_path: str) -> list:
    """Return list of 'col:type' for DATE_COLS stored as non-date in parquet schema."""
    try:
        import pyarrow.parquet as pq
        path = pq_path.rstrip("/")
        if pq_path.endswith("/"):
            files = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if f.endswith(".parquet")
            ]
            if not files:
                return []
            schema = pq.read_schema(files[0])
        else:
            schema = pq.read_schema(path)
        bad = []
        for field in schema:
            if field.name in DATE_COLS:
                t = str(field.type)
                if "date" not in t.lower():
                    bad.append(f"{field.name}:{t}")
        return bad
    except Exception as e:
        return [f"schema_read_error:{e}"]


def verify_all(manifest: dict) -> bool:
    """Compare local cache against BQ row counts, max dates, and date column dtypes."""
    log("Verifying cache against BigQuery...")
    all_ok = True
    for name, config in TABLES.items():
        table_info = manifest["tables"].get(name)
        if not table_info:
            log(f"  {name}: MISSING from cache")
            all_ok = False
            continue

        file_ref = table_info.get("file", f"{name}.parquet")
        pq_path = os.path.join(CACHE_DIR, file_ref)
        # chunked tables store a trailing slash dir; single tables store .parquet
        if not os.path.exists(pq_path.rstrip("/")):
            log(f"  {name}: parquet file/dir missing ({pq_path})")
            all_ok = False
            continue

        verify_sql = config.get("verify_sql")
        if not verify_sql:
            continue

        try:
            bq_stats = bq_query_to_df(verify_sql)
        except Exception as e:
            log(f"  {name}: BQ verify query failed: {e}")
            all_ok = False
            continue

        bq_cnt = int(bq_stats["cnt"].iloc[0])
        local_cnt = table_info["rows"]

        # Allow small tolerance for tables that might have concurrent writes
        tolerance = max(50, int(bq_cnt * 0.001))
        cnt_ok = abs(bq_cnt - local_cnt) <= tolerance

        if "max_time" in bq_stats.columns and "max_time" in table_info:
            bq_max = str(pd.to_datetime(bq_stats["max_time"].iloc[0]).date())
            local_max = table_info["max_time"]
            date_ok = bq_max == local_max
        else:
            bq_max = "n/a"
            local_max = "n/a"
            date_ok = True

        # dtype check: date columns must NOT be stored as VARCHAR/string in parquet
        dtype_bad = _check_parquet_date_dtypes(pq_path)

        if cnt_ok and date_ok and not dtype_bad:
            log(f"  {name}: OK ({local_cnt} rows, max={local_max})")
        else:
            issues = []
            if not cnt_ok:
                issues.append(f"count local={local_cnt} vs BQ={bq_cnt}")
            if not date_ok:
                issues.append(f"max_time local={local_max} vs BQ={bq_max}")
            if dtype_bad:
                issues.append(f"DTYPE_MISMATCH {dtype_bad}")
            log(f"  {name}: FAIL — {'; '.join(issues)}")
            all_ok = False

    manifest["verified"] = all_ok
    manifest["verified_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["verified_at_epoch"] = time.time()
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Sync BQ tables to local cache")
    parser.add_argument(
        "--delta", action="store_true",
        help="Delta mode: only download new rows since last sync"
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Verify only, no download"
    )
    parser.add_argument(
        "--tables", nargs="+",
        help="Sync specific tables (default: all)"
    )
    parser.add_argument(
        "--skip-verify", action="store_true",
        help="Skip verification after download"
    )
    args = parser.parse_args()

    os.makedirs(CACHE_DIR, exist_ok=True)
    manifest = load_manifest()

    if not args.verify:
        target_tables = args.tables or list(TABLES.keys())
        # Sort: small tables first (fast feedback), big tables last
        size_order = {
            "custom30v_8l": 0, "risk_rating": 1,
            "vnindex_5state": 2, "vnindex_5state_dt5g_live": 2,
            "vnindex_5state_tam_quan_v34b_clean": 2,
            "vnindex_5state_dt_4gate": 2,
            "fa_ratings": 3, "fa_ratings_8l": 3,
            "ticker_financial": 4, "ticker_1m": 5,
            "ticker_prune": 6, "ticker": 7,
        }
        target_tables.sort(key=lambda t: size_order.get(t, 99))

        log(f"Syncing {len(target_tables)} tables ({'delta' if args.delta else 'full'})...")
        for name in target_tables:
            if name not in TABLES:
                log(f"  {name}: unknown table, skipping")
                continue
            try:
                download_table(name, TABLES[name], manifest, args.delta)
            except Exception as e:
                log(f"  {name}: FAILED — {e}")
                import traceback
                traceback.print_exc()
        save_manifest(manifest)

    # Verify
    if not args.skip_verify:
        ok = verify_all(manifest)
        save_manifest(manifest)
        if ok:
            log("Cache verified OK — ready for local queries")
        else:
            log("Cache verification FAILED — some tables are stale or missing")
            sys.exit(1)
    else:
        log("Verification skipped (--skip-verify)")


if __name__ == "__main__":
    main()
