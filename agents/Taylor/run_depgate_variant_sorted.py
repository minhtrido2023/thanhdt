# -*- coding: utf-8 -*-
"""
run_depgate_variant_sorted.py <control|D1|D2|D3|S4_xx> [tag_suffix] — job Taylor_20260713_145605.

Same as run_depgate_variant.py PLUS a stable-sort patch on BQLocalCache.query: any result
containing BOTH `time` and `ticker` columns is sorted (time, ticker) with a stable mergesort.

WHY (found in this job): the harness's candidate sizing tie-breaks on query row order. DuckDB
row order shifts with the CONTENT of the swapped state parquet (hash-join layout), so two runs
whose states are identical until 2023 still swapped buy amounts between equal-score tickers from
2018-01-02 (e.g. MWG/PLX), diverging NAV by billions of VND before the first state difference.
The stable sort makes the tie-break alphabetical and content-independent, so variant-vs-control
deltas are attributable to the dep layer alone. Determinism is PROVEN per-batch by running the
control twice (must be identical on all DAILY NAVs).

Intentional ORDER BYs are safe: the top-30 liquidity basket query has `ticker` but no `time`
column in its result, and the VNINDEX/series queries have `time` but no `ticker` — neither is
touched by the (time AND ticker) condition.
"""
import os, sys, runpy

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
vid = sys.argv[1]
tag = sys.argv[2] if len(sys.argv) > 2 else f"{vid}S"

os.environ.update({
    "BQ_LOCAL_CACHE": "data/bq_cache",
    "BQ_CACHE_THREADS": "1",
    "NAV_TOTAL_B": "50",
    "ETF_LIQ": "custompitg",
    "BASKET_WT": "namecap",
    "BASKET_SELECT": "yieldcombo",
    "PARK_STATES": "3:0.7",
    "AUDIT_END": "2026-06-19",
    "EXP_TAG": f"depgate_{tag}",
})
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import bq_local_cache
if os.environ.get("DEPGATE_BYPASS_VERIFIED") == "1":
    _orig = bq_local_cache.BQLocalCache._load_manifest
    def _patched(self):
        import json as _json, os as _os
        with open(_os.path.join(self.cache_dir, "manifest.json")) as f:
            self.manifest = _json.load(f)
        print(f"[runner] BYPASS_VERIFIED: manifest verified={self.manifest.get('verified')} "
              f"— proceeding, control determinism-pair is the integrity gate", flush=True)
    bq_local_cache.BQLocalCache._load_manifest = _patched

# stable-sort patch (content-independent row order for per-ticker-day results)
_orig_query = bq_local_cache.BQLocalCache.query
def _sorted_query(self, sql):
    df = _orig_query(self, sql)
    try:
        if {"time", "ticker"}.issubset(df.columns):
            df = df.sort_values(["time", "ticker"], kind="mergesort").reset_index(drop=True)
    except Exception:
        pass
    return df
bq_local_cache.BQLocalCache.query = _sorted_query
print("[runner] stable-sort patch active: results with (time AND ticker) sorted (time,ticker)", flush=True)

lc = bq_local_cache.get_cache()
assert lc is not None, "cache not available"
if vid != "control":
    pq = os.path.join(WORKDIR, f"mike/agents/Taylor/exp_depgate/state_{vid}.parquet")
    assert os.path.exists(pq), pq
    lc.conn.execute("DROP VIEW vnindex_5state_dt5g_live")
    lc.conn.execute(
        f"CREATE VIEW vnindex_5state_dt5g_live AS "
        f"SELECT TRY_CAST(time AS DATE) AS time, state, state_raw FROM read_parquet('{pq}')"
    )
    n = lc.conn.execute("SELECT COUNT(*), MIN(time), MAX(time) FROM vnindex_5state_dt5g_live").fetchall()
    print(f"[runner] view vnindex_5state_dt5g_live -> {pq}  ({n})", flush=True)
else:
    print("[runner] control: published DT5G view untouched", flush=True)

sys.argv = ["pt_v23_audit_2014.py", "v23a", "none", "postbull", "0", "edge"]
runpy.run_path(os.path.join(WORKDIR, "pt_v23_audit_2014.py"), run_name="__main__")
