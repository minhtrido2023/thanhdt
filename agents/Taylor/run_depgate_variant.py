# -*- coding: utf-8 -*-
"""
run_depgate_variant.py <control|D0|D1|D2|D3|S4_xx> — job Taylor_20260713_131230.
Runs the pinned R3 harness command with the DT5G state view swapped (in-process DuckDB view
override, zero touch to the real cache) to the experiment state series. Output CSVs carry
EXP_TAG=depgate_<id> so canonical filenames can never be overwritten (guideline §8).
Pinned command mirrored from data/results_registry.md (R3 re-pin 2026-07-12).
"""
import os, sys, runpy

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
vid = sys.argv[1]

os.environ.update({
    "BQ_LOCAL_CACHE": "data/bq_cache",
    "BQ_CACHE_THREADS": "1",
    "NAV_TOTAL_B": "50",
    "ETF_LIQ": "custompitg",
    "BASKET_WT": "namecap",
    "BASKET_SELECT": "yieldcombo",
    "PARK_STATES": "3:0.7",
    "AUDIT_END": "2026-06-19",
    "EXP_TAG": f"depgate_{vid}",
})
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

from bq_local_cache import get_cache
lc = get_cache()
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
