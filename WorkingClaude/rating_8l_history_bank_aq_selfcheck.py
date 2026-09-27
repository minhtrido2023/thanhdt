#!/usr/bin/env python3
"""rating_8l_history_bank_aq_selfcheck.py — selfcheck for the H1 wire (job Taylor_20260927_022319):
rating_8l_history.py::rate_bank_hist() (AQ-aware, FiinPro NPL/LLR) replacing rate_bank_proxy() (ROE-only)
on the BANK route, plus the fail-closed fix in override_current_bank_aq().

THE INVARIANT UNDER TEST (the GO condition of finding `fiinprox-H1-bank-route-8l`, quant-skeptic
CONFIRMED high 2026-09-26T17:35:21Z): every V2.4 consumer of fa_ratings_8l reads the rating as the
BINARY gate rating<=3. So the wire is legitimate data hygiene only if the <=3 / >=4 partition of the
2014-2026 history is BYTE-IDENTICAL before and after. A single flip = a strategy change in disguise
=> this selfcheck FAILS and the wire must not be merged.

ENVIRONMENT DEPENDENCIES (verify-before-done skill — name them, then break them on purpose):
  - TZ: none by construction (all dates are tz-naive pd.Timestamp from CSV/BQ strings, no now()).
    Run under `env -u TZ` and a foreign TZ anyway; --all-tz does it for you.
  - WORKDIR_8L: where data/ and mike/data/ live. Defaults to the canonical checkout, because the git
    WORKTREE has no mike/ (nested repo, hidden by .gitignore:107) — a worktree-relative default would
    silently make the FiinPro file "missing" and the whole A/B a no-op that PASSES.
  - H1_FIN_CACHE: cached BQ pull of HIST_SQL/ICB_SQL (avoids 3 identical 37s BQ round-trips under
    --all-tz). Absent -> pulls from BQ live.

Usage:  python3 rating_8l_history_bank_aq_selfcheck.py [--all-tz]
"""
import os, subprocess, sys, tempfile

# Default to the CANONICAL checkout: the worktree has no mike/ (nested repo), and a missing FiinPro
# file makes rate_bank_hist() fall back to the proxy -> the A/B would pass vacuously.
os.environ.setdefault("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
WORKDIR = os.environ["WORKDIR_8L"]
os.environ.setdefault("BANK_AQ_CSV",
                      os.path.join(WORKDIR, "mike", "data", "fiinprox_bank_ratios_quarterly_20260914.csv"))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import rating_8l_history as H

N_OK = 0
FAILS = []


def ok(cond, label, detail=""):
    global N_OK
    if cond:
        N_OK += 1
    else:
        FAILS.append(f"{label}" + (f" -- {detail}" if detail else ""))


def row(**kw):
    """A financial row as rate_row() sees it (plain dict; .get() semantics match a pandas Series)."""
    base = dict(ticker="ZZZ", q_time="2020-03-31", Release_Date="2020-05-20",
                ROE_Trailing=np.nan, ROE5Y=np.nan, ROE3Y=np.nan)
    base.update(kw)
    return base


# =====================================================================================
# 1. THRESHOLD ALGEBRA — exhaustive grid: the <=3 partition cannot depend on NPL/coverage
# =====================================================================================
def test_grid():
    H.BANK_AQ, H.BANK_AQ_BY_TK = {}, {}
    grid_roe = [x / 1000.0 for x in range(0, 501)]                     # ROE 0..50%, step 0.1pp
    grid_npl = [None, 0.0, 0.005, 0.012, 0.0121, 0.020, 0.0201, 0.050, 0.359]
    grid_cov = [None, 0.0, 0.5, 0.899, 0.900, 1.4999, 1.500, 2.80]
    flips, out_of_range, n = 0, 0, 0
    for npl in grid_npl:
        for cov in grid_cov:
            if npl is None and cov is None:
                continue                                              # = no AQ row at all, tested below
            H.BANK_AQ = {("ZZZ", "2020Q1"): dict(npl=npl, cov=cov)}
            H.BANK_AQ_BY_TK = {"ZZZ": [(H.bank_aq_avail_date("2020Q1"), "2020Q1")]}
            for roe in grid_roe:
                r = row(ROE_Trailing=roe)
                a = H.rate_bank_hist(r)
                p = H.rate_bank_proxy(r)
                n += 1
                if (a <= 3) != (p <= 3): flips += 1
                if not (1 <= a <= 5): out_of_range += 1
    ok(flips == 0, "grid: binary gate <=3 never flips AQ vs proxy", f"{flips} flips over {n:,} combos")
    ok(out_of_range == 0, "grid: rate_bank_hist always returns 1..5", f"{out_of_range} out of range")
    print(f"  [1] grid {n:,} (ROE,NPL,coverage) combos -> {flips} gate flips, {out_of_range} out-of-range")
    # and the AQ path really does discriminate inside <=3 (otherwise the test above is vacuous)
    H.BANK_AQ = {("ZZZ", "2020Q1"): dict(npl=0.005, cov=2.0)}
    H.BANK_AQ_BY_TK = {"ZZZ": [(H.bank_aq_avail_date("2020Q1"), "2020Q1")]}
    elite = H.rate_bank_hist(row(ROE_Trailing=0.20))
    H.BANK_AQ = {("ZZZ", "2020Q1"): dict(npl=0.050, cov=0.4)}
    dirty = H.rate_bank_hist(row(ROE_Trailing=0.20))
    ok(elite == 1 and dirty == 3, "AQ genuinely differentiates 1 vs 3 inside the <=3 region",
       f"pristine={elite} dirty={dirty} (expect 1 and 3)")
    print(f"  [1] AQ differentiation inside gate: pristine ROE20% -> {elite}, dirty ROE20% -> {dirty}")


# =====================================================================================
# 2. POINT-IN-TIME GATE — publication lag must be exact, and never readable one day early
# =====================================================================================
def test_pit():
    exp = {"2020Q1": "2020-05-15", "2020Q2": "2020-08-14",
           "2020Q3": "2020-11-14", "2020Q4": "2021-03-31"}
    for q, d in exp.items():
        got = H.bank_aq_avail_date(q)
        ok(got == pd.Timestamp(d), f"avail_date({q}) == {d}", f"got {got.date()}")
    print("  [2] avail_date: " + ", ".join(f"{q}->{H.bank_aq_avail_date(q).date()}" for q in exp))

    H.BANK_AQ = {("ZZZ", "2020Q1"): dict(npl=0.005, cov=2.0),
                 ("ZZZ", "2020Q2"): dict(npl=0.050, cov=0.4)}
    H.BANK_AQ_BY_TK = {"ZZZ": sorted((H.bank_aq_avail_date(q), q) for (_t, q) in H.BANK_AQ)}
    ok(H.bank_aq_asof("ZZZ", pd.Timestamp("2020-05-14"))[2] == "",
       "asof: 2020Q1 NOT readable one day before its lag elapses")
    ok(H.bank_aq_asof("ZZZ", pd.Timestamp("2020-05-15"))[2] == "2020Q1",
       "asof: 2020Q1 readable exactly on lag date")
    ok(H.bank_aq_asof("ZZZ", pd.Timestamp("2020-08-13"))[2] == "2020Q1",
       "asof: still 2020Q1 the day before 2020Q2 becomes available (no look-ahead)")
    ok(H.bank_aq_asof("ZZZ", pd.Timestamp("2020-08-14"))[2] == "2020Q2",
       "asof: rolls to 2020Q2 on its lag date")
    ok(H.bank_aq_asof("YYY", pd.Timestamp("2026-01-01"))[2] == "", "asof: unknown ticker -> no AQ")
    ok(H.bank_aq_asof("ZZZ", pd.NaT)[2] == "", "asof: NaT eff_date -> no AQ (never guesses)")
    # the look-ahead a naive implementation would commit: rating at 2020-05-14 must equal the proxy
    r = row(ROE_Trailing=0.20, Release_Date="2020-05-14")
    ok(H.rate_bank_hist(r) == H.rate_bank_proxy(r),
       "no look-ahead: before the lag date the rating is exactly the ROE-only proxy")
    print("  [2] PIT lag honoured on both sides of every boundary date")


# =====================================================================================
# 3. FAIL-SAFE — missing file / missing AQ / nim_only rows must degrade to the proxy, never invent
# =====================================================================================
def test_failsafe():
    H.BANK_AQ, H.BANK_AQ_BY_TK = {}, {}
    diffs = [roe for roe in (0.0, 0.05, 0.079, 0.08, 0.11, 0.12, 0.139, 0.14, 0.179, 0.18, 0.30)
             if H.rate_bank_hist(row(ROE_Trailing=roe)) != H.rate_bank_proxy(row(ROE_Trailing=roe))]
    ok(not diffs, "no AQ loaded -> rate_bank_hist == rate_bank_proxy (pre-wire behaviour)", str(diffs))

    old_csv = H.BANK_AQ_CSV
    try:
        H.BANK_AQ_CSV = "/nonexistent/fiinprox_missing.csv"
        H.load_bank_aq()
        ok(H.BANK_AQ == {}, "missing FiinPro file -> empty AQ (no crash, no invented grade)")
    finally:
        H.BANK_AQ_CSV = old_csv

    # a nim_only row (both NPL and coverage null) must be DROPPED AT LOAD, and even if one reached
    # rate_bank_hist it must degrade to the proxy -- never be read as pristine (a fabricated 1/2).
    _nimonly = pd.DataFrame([dict(ticker="ZZZ", year=2020, quarter=1, npl_ratio_3_5_pct=None,
                                  nim_pct=3.1, casa_ratio_pct=None, llr_coverage_pct=None,
                                  flags="nim_only")])
    _tmpf = os.path.join(tempfile.gettempdir(), "h1_nimonly_probe.csv")
    _nimonly.to_csv(_tmpf, index=False)
    _old_csv = H.BANK_AQ_CSV
    try:
        H.BANK_AQ_CSV = _tmpf; H.load_bank_aq()
        ok(("ZZZ", "2020Q1") not in H.BANK_AQ,
           "load_bank_aq DROPS nim_only rows (npl and coverage both null)", str(list(H.BANK_AQ)))
    finally:
        H.BANK_AQ_CSV = _old_csv
        try: os.unlink(_tmpf)
        except OSError: pass
    H.BANK_AQ = {("ZZZ", "2020Q1"): dict(npl=None, cov=None)}
    H.BANK_AQ_BY_TK = {"ZZZ": [(H.bank_aq_avail_date("2020Q1"), "2020Q1")]}
    _r = row(ROE_Trailing=0.20)
    ok(H.rate_bank_hist(_r) == H.rate_bank_proxy(_r) == 1,
       "npl=cov=None -> falls back to the ROE-only proxy, NOT read as pristine",
       f"hist={H.rate_bank_hist(_r)} proxy={H.rate_bank_proxy(_r)}")
    # coverage present but NPL missing: `pristine`/`strong` must both be False, not None-compares
    H.BANK_AQ = {("ZZZ", "2020Q1"): dict(npl=None, cov=3.0)}
    ok(H.rate_bank_hist(row(ROE_Trailing=0.20)) == 3, "coverage-only AQ -> 3, never 1/2")
    H.BANK_AQ = {("ZZZ", "2020Q1"): dict(npl=0.001, cov=None)}
    ok(H.rate_bank_hist(row(ROE_Trailing=0.20)) == 3, "NPL-only AQ -> 3, never 1/2")
    ok(H.rate_bank_hist(row()) == 3, "no ROE at all -> 3 (same as proxy / rate_bank bank-noROE)")
    print("  [3] fail-safe: 6 degradation paths all land on the proxy / a non-inventing 3")


# =====================================================================================
# 4. FAIL-CLOSED override — a fabricated live grade must never reach the latest history row
# =====================================================================================
def test_override_failclosed(tmp):
    def hist_frame():
        return pd.DataFrame([
            dict(ticker="AAA", eff_date="2026-01-01", q_time="2025-09-30", route="BANK",
                 rating=4, core_score=0, tier="D"),
            dict(ticker="BBB", eff_date="2026-01-01", q_time="2025-09-30", route="BANK",
                 rating=5, core_score=0, tier="E"),
        ])

    def run(live_rows, cols=("ticker", "route", "rating", "note")):
        d = os.path.join(tmp, "data"); os.makedirs(d, exist_ok=True)
        pd.DataFrame(live_rows)[list(cols)].to_csv(os.path.join(d, "rating_8l.csv"), index=False)
        old = H.WORKDIR
        try:
            H.WORKDIR = tmp
            return H.override_current_bank_aq(hist_frame())
        finally:
            H.WORKDIR = old

    out = run([dict(ticker="AAA", route="BANK", rating=3, note="bank-nodata"),
               dict(ticker="BBB", route="BANK", rating=3, note="bank-noROE")])
    ok(list(out["rating"]) == [4, 5],
       "override REJECTS bank-nodata / bank-noROE (fail-closed)", str(list(out["rating"])))
    ok(list(out["tier"]) == ["D", "E"], "override leaves tier alone when it rejects")

    out = run([dict(ticker="AAA", route="BANK", rating=2, note="strong asset-quality"),
               dict(ticker="BBB", route="BANK", rating=1, note="elite asset-quality")])
    ok(list(out["rating"]) == [2, 1], "override still APPLIES a real lens-backed grade",
       str(list(out["rating"])))
    ok(list(out["tier"]) == ["B", "A"], "override updates tier with the rating")

    out = run([dict(ticker="AAA", route="BANK", rating=3, note="bank-nodata"),
               dict(ticker="BBB", route="BANK", rating=1, note="elite asset-quality")])
    ok(list(out["rating"]) == [4, 1], "rejection is per-row, not all-or-nothing", str(list(out["rating"])))

    out = run([dict(ticker="AAA", route="BANK", rating=3), dict(ticker="BBB", route="BANK", rating=1)],
              cols=("ticker", "route", "rating"))
    ok(list(out["rating"]) == [4, 5],
       "no `note` column -> reject EVERY override (never infer from absence, §28)", str(list(out["rating"])))

    # MUTATION KILL: revert the fix (accept every live row) and prove this test catches it
    import types
    saved = H.override_current_bank_aq
    def buggy(out, _saved=saved):
        live = pd.read_csv(os.path.join(H.WORKDIR, "data", "rating_8l.csv"))
        lb = live[live["route"] == "BANK"]
        live_map = {t: int(r) for t, r in zip(lb["ticker"], lb["rating"]) if pd.notna(r)}
        r2t = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
        for tk in out.loc[out["route"] == "BANK", "ticker"].unique():
            if tk not in live_map: continue
            i = out.loc[(out["ticker"] == tk) & (out["route"] == "BANK")].sort_values("eff_date").index[-1]
            out.at[i, "rating"] = live_map[tk]; out.at[i, "tier"] = r2t[live_map[tk]]
        return out
    try:
        H.override_current_bank_aq = buggy
        bad = run([dict(ticker="AAA", route="BANK", rating=3, note="bank-nodata"),
                   dict(ticker="BBB", route="BANK", rating=3, note="bank-noROE")])
        ok(list(bad["rating"]) == [3, 3],
           "MUTATION: pre-fix fail-open code IS caught by this test (4,5 -> 3,3)", str(list(bad["rating"])))
    finally:
        H.override_current_bank_aq = saved
    print("  [4] fail-closed override: 6 assertions + 1 mutation kill")

    # the REAL live file: which banks does the fix now reject, and would the gate have moved?
    live = pd.read_csv(os.path.join(WORKDIR, "data", "rating_8l.csv"))
    lb = live[live["route"] == "BANK"]
    bad = lb[lb["note"].astype(str).str.contains("bank-nodata|bank-noROE", regex=True)]
    print(f"  [4] real data/rating_8l.csv: {len(bad)}/{len(lb)} BANK rows are fabricated "
          f"({', '.join(sorted(bad['ticker']))}) -> now rejected")
    return sorted(bad["ticker"])


# =====================================================================================
# 5. REAL PANEL A/B — the GO invariant on the actual 2014-2026 history
# =====================================================================================
def load_hist():
    cache = os.environ.get("H1_FIN_CACHE")
    if cache and os.path.exists(os.path.join(cache, "hist_fin.csv")):
        df = pd.read_csv(os.path.join(cache, "hist_fin.csv"))
        icb = pd.read_csv(os.path.join(cache, "icb.csv"))
        print(f"  [5] financial history from cache {cache} ({len(df):,} rows)")
    else:
        print("  [5] pulling financial history from BigQuery (no H1_FIN_CACHE) ...")
        df, icb = H.bq(H.HIST_SQL), H.bq(H.ICB_SQL)
    return df.merge(icb, on="ticker", how="left")


def test_real_panel():
    H.BANK_AQ_CSV = os.environ["BANK_AQ_CSV"]
    H.load_bank_aq()
    ok(len(H.BANK_AQ) > 1000, "real FiinPro file loaded", f"{len(H.BANK_AQ)} bank-quarters")
    df = load_hist()
    df["route"] = [H.route_of(t, c) for t, c in zip(df["ticker"], df["ICB_Code"])]
    b = df[df["route"] == "BANK"].copy()
    ok(len(b) > 900, "BANK panel non-trivial", f"{len(b)} rows")

    recs = b.to_dict("records")
    new = np.array([H.rate_bank_hist(r) for r in recs])
    old = np.array([H.rate_bank_proxy(r) for r in recs])
    gate_flips = int(((old <= 3) != (new <= 3)).sum())
    changed = int((old != new).sum())
    have_aq = sum(1 for r in recs if H.bank_aq_asof(r["ticker"], H.bank_eff_date(r))[2] != "")

    ok(gate_flips == 0,
       "REAL PANEL: 0 binary-gate flips over the whole 2014-2026 BANK history",
       f"{gate_flips} flips -- THIS IS THE GO CONDITION, wire must NOT merge")
    ok(changed > 0, "REAL PANEL: the wire does change ratings (test is not vacuous)", f"{changed}")
    print(f"  [5] BANK rows {len(b):,} | AQ readable {have_aq:,} ({100.0*have_aq/len(b):.1f}%) | "
          f"rating changed {changed:,} ({100.0*changed/len(b):.1f}%) | GATE FLIPS {gate_flips}")
    mat = {}
    for o, nw in zip(old, new):
        if o != nw: mat[(int(o), int(nw))] = mat.get((int(o), int(nw)), 0) + 1
    print("  [5] proxy->AQ transitions: " + ", ".join(f"{k[0]}->{k[1]}:{v}" for k, v in sorted(mat.items())))

    # MUTATION KILL: an AQ rule that DOES move the gate must be caught by the assertion above
    def mutant(r):
        roe = r.get("ROE_Trailing", np.nan)
        if pd.isna(roe): roe = r.get("ROE5Y", np.nan)
        if pd.isna(roe): roe = r.get("ROE3Y", np.nan)
        if pd.isna(roe): return 3
        npl, cov, q = H.bank_aq_asof(r.get("ticker"), H.bank_eff_date(r))
        if q and npl is not None and npl > 0.03: return 4      # the classic NPL>3% AVOID cliff
        return H.rate_bank_proxy(r)
    mnew = np.array([mutant(r) for r in recs])
    ok(int(((old <= 3) != (mnew <= 3)).sum()) > 0,
       "MUTATION: an NPL>3%->4 cliff WOULD be caught by the gate-flip assertion",
       "mutant produced 0 flips, so the real-panel test cannot detect a gate change")
    print(f"  [5] mutation (NPL>3% -> 4 cliff): {int(((old<=3)!=(mnew<=3)).sum())} gate flips detected")
    return dict(rows=len(b), changed=changed, gate_flips=gate_flips, have_aq=have_aq)


# =====================================================================================
def main():
    if "--all-tz" in sys.argv:
        env = dict(os.environ); env.pop("TZ", None)
        rcs = []
        for label, tz in (("no TZ", None), ("UTC", "UTC"), ("America/New_York", "America/New_York")):
            e = dict(env)
            if tz: e["TZ"] = tz
            print(f"\n{'='*78}\n== TZ = {label}\n{'='*78}")
            r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=e)
            rcs.append((label, r.returncode))
        print("\n" + "="*78)
        for label, rc in rcs:
            print(f"  TZ {label:<20} -> {'PASS' if rc == 0 else 'FAIL'} (rc={rc})")
        sys.exit(0 if all(rc == 0 for _, rc in rcs) else 1)

    print(f"rating_8l_history bank-AQ selfcheck | TZ={os.environ.get('TZ', '(unset)')} | "
          f"WORKDIR={WORKDIR}")
    test_grid()
    test_pit()
    test_failsafe()
    with tempfile.TemporaryDirectory() as tmp:
        rejected = test_override_failclosed(tmp)
    stats = test_real_panel()

    print(f"\n{'='*78}")
    print(f"assertions PASSED : {N_OK}")
    print(f"assertions FAILED : {len(FAILS)}")
    for f in FAILS:
        print(f"  [FAIL] {f}")
    print(f"BANK panel        : {stats['rows']:,} rows, {stats['changed']:,} ratings changed, "
          f"{stats['gate_flips']} gate flips")
    print(f"override rejected : {len(rejected)} fabricated live bank grade(s): {', '.join(rejected)}")
    print("VERDICT           : " + ("PASS" if not FAILS else "FAIL"))
    sys.exit(0 if not FAILS else 1)


if __name__ == "__main__":
    main()
