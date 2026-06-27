"""Local BQ cache — DuckDB-backed drop-in replacement for bq() BigQuery calls.

Set BQ_LOCAL_CACHE=data/bq_cache (relative to WORKDIR or absolute) to enable.
When enabled, bq() in simulate_holistic_nav.py routes ALL queries through DuckDB
on local parquet files instead of hitting BigQuery over the network.

Run sync_bq_cache.py to populate/refresh the cache (once-daily after BQ ingest).
The manifest must show verified=true before the cache is used.
"""
import json
import os
import re
import time

import pandas as pd

_cache_instance = None


class BQLocalCache:
    def __init__(self, cache_dir: str):
        import duckdb

        self.cache_dir = cache_dir
        self.conn = duckdb.connect(":memory:")
        # threads=1 by default: DuckDB multi-thread returns rows in non-deterministic order without
        # ORDER BY; order-dependent ops (drop_duplicates keep-first) cause ~0.2pp CAGR run-to-run
        # variance in backtests — hidden by self-check 0 VND. Cost: ~5% (scan-bound queries).
        # Override: BQ_CACHE_THREADS=4 for interactive exploration where reproducibility is not needed.
        # (Taylor 2026-06-25, reproducibility audit; Winston decision 2026-06-25.)
        import os as _os
        self.conn.execute(f"SET threads = {int(_os.environ.get('BQ_CACHE_THREADS', '1'))}")
        self._load_manifest()
        self._register_macros()
        self._register_tables()

    def _load_manifest(self):
        with open(os.path.join(self.cache_dir, "manifest.json")) as f:
            self.manifest = json.load(f)
        if not self.manifest.get("verified"):
            raise RuntimeError(
                "BQ local cache not verified — run sync_bq_cache.py first"
            )
        age_h = (time.time() - self.manifest.get("verified_at_epoch", 0)) / 3600
        if age_h > 36:
            print(
                f"[BQ_LOCAL_CACHE] WARNING: cache verified {age_h:.0f}h ago "
                f"(>{36}h) — consider re-running sync_bq_cache.py",
                flush=True,
            )

    def _register_macros(self):
        self.conn.execute(
            "CREATE MACRO SAFE_DIVIDE(a, b) AS (a) / NULLIF(b, 0)"
        )

    _DATE_COLS = {
        "time", "Release_Date", "rebal_date",
        "effective_from", "effective_to",
    }

    def _register_tables(self):
        for table_name, info in self.manifest["tables"].items():
            pq_path = os.path.join(self.cache_dir, info["file"])
            if info["file"].endswith("/"):
                glob_path = os.path.join(pq_path, "*.parquet")
                if not os.path.isdir(pq_path):
                    print(
                        f"[BQ_LOCAL_CACHE] WARNING: {pq_path} missing, "
                        f"queries hitting {table_name} will fail",
                        flush=True,
                    )
                    continue
                raw = f"read_parquet('{glob_path}')"
            elif not os.path.exists(pq_path):
                print(
                    f"[BQ_LOCAL_CACHE] WARNING: {pq_path} missing, "
                    f"queries hitting {table_name} will fail",
                    flush=True,
                )
                continue
            else:
                raw = f"read_parquet('{pq_path}')"
            self.conn.execute(
                f"CREATE VIEW {table_name} AS SELECT * FROM {raw}"
            )
            cols = self.conn.execute(
                f"DESCRIBE {table_name}"
            ).fetchall()
            to_cast = [
                c[0] for c in cols
                if c[0] in self._DATE_COLS and c[1] == "VARCHAR"
            ]
            if to_cast:
                print(
                    f"[BQ_LOCAL_CACHE] {table_name}: casting VARCHAR→DATE "
                    f"for {to_cast} (parquet has wrong dtype — re-run sync_bq_cache.py)",
                    flush=True,
                )
                self.conn.execute(f"DROP VIEW {table_name}")
                parts = []
                cast_set = set(to_cast)
                for c in cols:
                    if c[0] in cast_set:
                        parts.append(f"TRY_CAST({c[0]} AS DATE) AS {c[0]}")
                    else:
                        parts.append(c[0])
                self.conn.execute(
                    f"CREATE VIEW {table_name} AS "
                    f"SELECT {', '.join(parts)} FROM {raw}"
                )

    # ── public API ───────────────────────────────────────────────────────────

    def query(self, sql: str) -> pd.DataFrame:
        local_sql = self._translate(sql)
        t0 = time.monotonic()
        try:
            result = self.conn.execute(local_sql).fetchdf()
        except Exception as e:
            print(f"[BQ_LOCAL_CACHE] DuckDB error: {e}", flush=True)
            print(
                f"[BQ_LOCAL_CACHE] Translated SQL (first 500 chars):\n"
                f"{local_sql[:500]}",
                flush=True,
            )
            raise
        elapsed = time.monotonic() - t0
        if elapsed > 2:
            print(
                f"[BQ_LOCAL_CACHE] query took {elapsed:.1f}s "
                f"({len(result)} rows)",
                flush=True,
            )
        return result

    # ── BQ → DuckDB SQL translation ─────────────────────────────────────────

    def _translate(self, sql: str) -> str:
        # 1. Strip dataset prefix
        sql = sql.replace("tav2_bq.", "")

        # 2. Type names
        sql = re.sub(r"\bINT64\b", "BIGINT", sql)
        sql = re.sub(r"\bFLOAT64\b", "DOUBLE", sql)

        # 3. ARRAY_AGG(expr ORDER BY col DESC LIMIT 1)[OFFSET(0)] → ARG_MAX
        sql = re.sub(
            r"ARRAY_AGG\s*\(\s*(\S+?)\s+ORDER\s+BY\s+(\S+?)\s+DESC"
            r"\s+LIMIT\s+1\s*\)\s*\[\s*OFFSET\s*\(\s*0\s*\)\s*\]",
            r"ARG_MAX(\1, \2)",
            sql,
            flags=re.IGNORECASE,
        )

        # 4. DATE_DIFF(end, start, DAY) → DATEDIFF('day', start, end)
        sql = re.sub(
            r"DATE_DIFF\s*\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*DAY\s*\)",
            r"DATEDIFF('day', \2, \1)",
            sql,
            flags=re.IGNORECASE,
        )

        # 5. APPROX_QUANTILES(expr, n)[OFFSET(k)] → QUANTILE_CONT(expr, k/n)
        def _replace_approx_q(m):
            expr, n, k = m.group(1).strip(), m.group(2), m.group(3)
            frac = int(k) / int(n)
            return f"QUANTILE_CONT({expr}, {frac})"

        sql = re.sub(
            r"APPROX_QUANTILES\s*\(\s*(.+?)\s*,\s*(\d+)\s*\)"
            r"\s*\[\s*OFFSET\s*\(\s*(\d+)\s*\)\s*\]",
            _replace_approx_q,
            sql,
            flags=re.IGNORECASE,
        )

        # 6. FORMAT_DATE(fmt, date) → strftime(date, fmt)
        sql = re.sub(
            r"FORMAT_DATE\s*\(\s*('[^']+?')\s*,\s*([^)]+?)\s*\)",
            r"strftime(\2, \1)",
            sql,
            flags=re.IGNORECASE,
        )

        # 7. DATE_TRUNC(date, QUARTER|MONTH|...) → DATE_TRUNC('quarter', date)
        def _replace_date_trunc(m):
            date_expr = m.group(1).strip()
            part = m.group(2).lower()
            return f"DATE_TRUNC('{part}', {date_expr})"

        sql = re.sub(
            r"DATE_TRUNC\s*\(\s*([^,]+?)\s*,\s*"
            r"(QUARTER|MONTH|YEAR|WEEK|DAY)\s*\)",
            _replace_date_trunc,
            sql,
            flags=re.IGNORECASE,
        )

        # 8. DATE_SUB(date, INTERVAL N DAY) → date - INTERVAL 'N' DAY
        sql = re.sub(
            r"DATE_SUB\s*\(\s*([^,]+?)\s*,\s*INTERVAL\s+(\d+)\s+DAY\s*\)",
            r"\1 - INTERVAL '\2' DAY",
            sql,
            flags=re.IGNORECASE,
        )

        # 9. DATE_ADD(date, INTERVAL N DAY) → date + INTERVAL 'N' DAY
        sql = re.sub(
            r"DATE_ADD\s*\(\s*([^,]+?)\s*,\s*INTERVAL\s+(\d+)\s+DAY\s*\)",
            r"\1 + INTERVAL '\2' DAY",
            sql,
            flags=re.IGNORECASE,
        )

        return sql


def get_cache(cache_dir: str | None = None) -> BQLocalCache | None:
    """Singleton accessor. Returns None if cache is unavailable or unverified."""
    global _cache_instance
    if _cache_instance is not None:
        return _cache_instance

    if cache_dir is None:
        cache_dir = os.environ.get("BQ_LOCAL_CACHE", "").strip()
    if not cache_dir:
        return None

    workdir = os.environ.get(
        "WORKDIR", "/home/trido/thanhdt/WorkingClaude"
    )
    if not os.path.isabs(cache_dir):
        cache_dir = os.path.join(workdir, cache_dir)

    manifest_path = os.path.join(cache_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        print(
            f"[BQ_LOCAL_CACHE] no manifest at {manifest_path} — "
            f"run sync_bq_cache.py first",
            flush=True,
        )
        return None

    try:
        _cache_instance = BQLocalCache(cache_dir)
        n = len(_cache_instance.manifest.get("tables", {}))
        print(f"[BQ_LOCAL_CACHE] ready — {n} tables from {cache_dir}", flush=True)
        return _cache_instance
    except (ImportError, ModuleNotFoundError) as e:
        print(
            f"[BQ_LOCAL_CACHE] WARNING: BQ_LOCAL_CACHE is set but duckdb import failed "
            f"({e}) — FALLING BACK TO REAL BQ (non-deterministic, slow, costs money). "
            f"Fix: pip install duckdb==1.5.4",
            flush=True,
        )
        return None
    except Exception as e:
        print(f"[BQ_LOCAL_CACHE] init failed: {e} — falling back to real BQ", flush=True)
        return None
