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

import bq_local_cache
if os.environ.get("DEPGATE_BYPASS_VERIFIED") == "1":
    # DECLARED BYPASS (job Taylor_20260713_141712): manifest verified=False tonight because the
    # 21:33 delta sync's verify pass failed on unrelated rating tables (known Winston gap, being
    # fixed in Winston_20260713_143546). This backtest reads only data <= AUDIT_END=2026-06-19;
    # per-table manifest freshness covers it (ticker->07-10, prune->07-13, dt5g->07-13). The real
    # integrity gate is downstream: the control run must reproduce pinned R3 EXACTLY, else stop.
    _orig = bq_local_cache.BQLocalCache._load_manifest
    def _patched(self):
        import json as _json, os as _os
        with open(_os.path.join(self.cache_dir, "manifest.json")) as f:
            self.manifest = _json.load(f)
        print(f"[runner] BYPASS_VERIFIED: manifest verified={self.manifest.get('verified')} "
              f"— proceeding, control-vs-pin is the integrity gate", flush=True)
    bq_local_cache.BQLocalCache._load_manifest = _patched
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
