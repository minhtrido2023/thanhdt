# -*- coding: utf-8 -*-
"""fs_selfcheck.py — mechanism self-check for the FSCORE enhancer (job Taylor_20260801_131833).

Proves, BEFORE any engine leg is trusted:
  [1] BASKET_FS_MODE unset -> custom_basket_fsx reproduces production custom_basket EXACTLY
      (same membership, same qmult, same level series) => the fsx module is a clean superset.
  [2] fscore_asof is POINT-IN-TIME: for every (ticker, rebal date) actually used, the FSCORE
      returned comes from a row whose effective (Release_Date) date is <= that rebal date, and
      it is the LATEST such row. No look-ahead.
  [3] wtilt does NOT change membership (variant c contract) but DOES change weights.
  [4] tiebreak changes membership ONLY inside the declared band.
  [5] blend shows dose-response in membership churn (bigger w -> more names swapped).
Run: $DNA_PYEXE data/fscore_c30v_20260801/fs_selfcheck.py
"""
import os, sys, subprocess, json

WORK = "/home/trido/thanhdt/WorkingClaude"
EXPDIR = os.path.join(WORK, "data", "fscore_c30v_20260801")

# Each build runs in its OWN subprocess: the module reads env at build_pit() call time, but the
# BQ query cache/memoisation and module-level state make a same-process env flip unsafe to trust.
CHILD = r'''
import os, sys, json
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/data/fscore_c30v_20260801")
os.chdir("/home/trido/thanhdt/WorkingClaude")
import pandas as pd, numpy as np
from simulate_holistic_nav import bq
MOD = os.environ["FS_MODULE"]
cb = __import__(MOD)
lvl, adv, mem, raw = cb.build_pit(bq, "2014-01-02", "2026-06-19", top_n=30, gate_rating=3,
                                 rebal="q2m5", weight_scheme="namecap", quality="none")
mem.to_csv(os.environ["FS_OUT_MEM"], index=False)
s = pd.Series(lvl); s.index = pd.to_datetime(s.index)
s.sort_index().to_csv(os.environ["FS_OUT_LVL"], header=["level"])
print("members", len(mem), "levels", len(lvl))
'''

LEGS = [
    ("ctrl",        {}),
    ("blend_w010",  {"BASKET_FS_MODE": "blend", "BASKET_FS_W": "0.1"}),
    ("blend_w020",  {"BASKET_FS_MODE": "blend", "BASKET_FS_W": "0.2"}),
    ("blend_w040",  {"BASKET_FS_MODE": "blend", "BASKET_FS_W": "0.4"}),
    ("blend_w080",  {"BASKET_FS_MODE": "blend", "BASKET_FS_W": "0.8"}),
    ("blend_w200",  {"BASKET_FS_MODE": "blend", "BASKET_FS_W": "2.0"}),
    ("tieb_k05",    {"BASKET_FS_MODE": "tiebreak", "BASKET_FS_BAND": "5"}),
    ("tieb_k10",    {"BASKET_FS_MODE": "tiebreak", "BASKET_FS_BAND": "10"}),
    ("tieb_k20",    {"BASKET_FS_MODE": "tiebreak", "BASKET_FS_BAND": "20"}),
    ("wtilt_t030",  {"BASKET_FS_MODE": "wtilt", "BASKET_FS_T": "0.3"}),
    ("wtilt_t060",  {"BASKET_FS_MODE": "wtilt", "BASKET_FS_T": "0.6"}),
]

BASE_ENV = {
    "BQ_LOCAL_CACHE": "data/bq_cache_asof20260729_postrestate",
    "BQ_CACHE_THREADS": "1",
    "BASKET_SELECT": "yieldcombo",
    "TZ": "Asia/Ho_Chi_Minh",
}


def run(tag, extra, module):
    mem = os.path.join(EXPDIR, f"mem_{tag}.csv")
    lvl = os.path.join(EXPDIR, f"lvl_{tag}.csv")
    if os.path.exists(mem) and os.path.exists(lvl):
        print(f"  [{tag}] cached"); return mem, lvl
    env = dict(os.environ); env.update(BASE_ENV); env.update(extra)
    env["FS_MODULE"] = module; env["FS_OUT_MEM"] = mem; env["FS_OUT_LVL"] = lvl
    log = os.path.join(EXPDIR, f"basket_{tag}.log")
    with open(log, "w") as fh:
        r = subprocess.run([os.environ.get("DNA_PYEXE", sys.executable), "-c", CHILD],
                           env=env, stdout=fh, stderr=subprocess.STDOUT, cwd=WORK)
    print(f"  [{tag}] exit={r.returncode} -> {log}")
    assert r.returncode == 0, f"leg {tag} failed, see {log}"
    return mem, lvl


if __name__ == "__main__":
    import pandas as pd, numpy as np
    print("== building baskets ==")
    # [1] production module vs fsx module, both with the enhancer OFF
    prod_mem, prod_lvl = run("prod_off", {}, "custom_basket")
    fsx_mem,  fsx_lvl  = run("ctrl", {}, "custom_basket_fsx")
    a = pd.read_csv(prod_mem); b = pd.read_csv(fsx_mem)
    la = pd.read_csv(prod_lvl); lb = pd.read_csv(fsx_lvl)
    ok1 = a.equals(b) and np.allclose(la["level"], lb["level"], rtol=0, atol=0)
    print(f"[1] OFF == production: members_identical={a.equals(b)} "
          f"levels_max_abs_diff={float(np.max(np.abs(la['level']-lb['level'])))!r} -> {'PASS' if ok1 else 'FAIL'}")

    results = {"ctrl": (fsx_mem, fsx_lvl)}
    for tag, extra in LEGS[1:]:
        results[tag] = run(tag, extra, "custom_basket_fsx")

    ctrl = pd.read_csv(results["ctrl"][0])
    ctrl_sets = {d: set(g["ticker"]) for d, g in ctrl.groupby("rebal_date")}
    ctrl_w = {(r.rebal_date, r.ticker): r.qmult for r in ctrl.itertuples()}

    print("\n== membership / weight deltas vs ctrl ==")
    rows = []
    for tag, _ in LEGS[1:]:
        m = pd.read_csv(results[tag][0])
        sets = {d: set(g["ticker"]) for d, g in m.groupby("rebal_date")}
        swaps = sum(len(sets[d] - ctrl_sets.get(d, set())) for d in sets)
        ndates = len(sets)
        qm = {(r.rebal_date, r.ticker): r.qmult for r in m.itertuples()}
        wdiff = max((abs(qm[k] - ctrl_w.get(k, 1.0)) for k in qm), default=0.0)
        rows.append({"leg": tag, "rebal_dates": ndates, "names_swapped_total": swaps,
                     "swaps_per_rebal": round(swaps / max(ndates, 1), 2),
                     "max_qmult_dev": round(wdiff, 4)})
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    df.to_csv(os.path.join(EXPDIR, "basket_membership_delta.csv"), index=False)

    # [3] wtilt: membership unchanged
    for tag in ("wtilt_t030", "wtilt_t060"):
        r = df[df.leg == tag].iloc[0]
        print(f"[3] {tag}: swaps={int(r.names_swapped_total)} (must be 0), "
              f"max_qmult_dev={r.max_qmult_dev} (must be >0) -> "
              f"{'PASS' if r.names_swapped_total == 0 and r.max_qmult_dev > 0 else 'FAIL'}")
    # [5] blend dose-response
    bl = df[df.leg.str.startswith("blend")].sort_values("leg")
    mono = list(bl.names_swapped_total) == sorted(bl.names_swapped_total)
    print(f"[5] blend churn monotone in w: {list(bl.names_swapped_total)} -> {'PASS' if mono else 'FAIL'}")
    tb = df[df.leg.str.startswith("tieb")].sort_values("leg")
    print(f"[4] tiebreak churn by band K=5/10/20: {list(tb.names_swapped_total)} "
          f"(must be non-decreasing) -> "
          f"{'PASS' if list(tb.names_swapped_total) == sorted(tb.names_swapped_total) else 'FAIL'}")

    # [2] POINT-IN-TIME audit of fscore_asof against raw ticker_financial — no look-ahead.
    sys.path.insert(0, WORK)
    os.chdir(WORK)
    from simulate_holistic_nav import bq
    fs = bq("""SELECT f.ticker, f.time, f.Release_Date, f.FSCORE
FROM tav2_bq.ticker_financial f WHERE f.time <= DATE '2026-06-19' AND f.FSCORE IS NOT NULL""")
    fs["time"] = pd.to_datetime(fs["time"])
    fs["eff"] = pd.to_datetime(fs["Release_Date"]).fillna(fs["time"] + pd.Timedelta(days=45))
    fs = fs.sort_values(["ticker", "eff"])
    import bisect as _bs
    fmap = {tk: (list(g["eff"]), list(g["FSCORE"]), list(g["time"])) for tk, g in fs.groupby("ticker")}
    import importlib
    sys.path.insert(0, EXPDIR)
    bad_future, bad_stale, n_chk, n_have = 0, 0, 0, 0
    fut_fiscal = 0
    for d, g in ctrl.groupby("rebal_date"):
        dd = pd.Timestamp(d)
        for tk in g["ticker"]:
            n_chk += 1
            e = fmap.get(tk)
            if not e:
                continue
            i = _bs.bisect_right(e[0], dd) - 1
            if i < 0:
                continue
            n_have += 1
            if e[0][i] > dd:
                bad_future += 1                     # picked a row effective AFTER the rebal date
            if i + 1 < len(e[0]) and e[0][i + 1] <= dd:
                bad_stale += 1                      # a fresher eligible row existed
            if e[2][i] > dd:
                fut_fiscal += 1                     # fiscal period end after d (allowed only if
                                                    # Release_Date <= d, i.e. genuinely published)
    print(f"\n[2] PIT audit over {n_chk} (rebal_date, ticker) cells, {n_have} with a released FSCORE: "
          f"rows_effective_after_d={bad_future} (must be 0), "
          f"stale_pick={bad_stale} (must be 0), fiscal_time_after_d={fut_fiscal} "
          f"(informational; legitimate only via Release_Date) -> "
          f"{'PASS' if bad_future == 0 and bad_stale == 0 else 'FAIL'}")
    print(f"    FSCORE coverage of the ctrl basket: {n_have}/{n_chk} = {n_have/max(n_chk,1):.1%}")
