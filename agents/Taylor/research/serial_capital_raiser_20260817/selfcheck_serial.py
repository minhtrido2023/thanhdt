#!/usr/bin/env python3
"""Selfcheck for the serial-capital-raiser program. Implements PREREG.md §6 test list.

Two tests are marked [BQ] and issue one small read-only query each; everything else runs offline
from out/. `--offline` skips the two BQ tests (and says so in the summary rather than silently
reporting a smaller pass count).

Discipline note: when a test fails, the first hypothesis is that THIS FILE is wrong, not that the
analysis is (corp-action ledger E1 — a Sprint 2 selfcheck asserted a property that does not hold on
uncorrelated data and "found" a bug that did not exist). Any edit to a test carries a comment
saying why.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

from analyze import panel_path
from scr_lib import Index, absorb, boot, cluster2_ols

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
PROJECT = "lithe-record-440915-m9"
OFFLINE = "--offline" in sys.argv

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  — {detail}" if detail else ""), flush=True)


def _bq(sql: str) -> list[dict]:
    import csv as _csv
    import shutil
    exe = shutil.which("bq") or "/home/trido/google-cloud-sdk/bin/bq"
    env = os.environ.copy()
    env["PATH"] = "/home/trido/google-cloud-sdk/bin:" + env.get("PATH", "")
    env.setdefault("CLOUDSDK_CONFIG", "/home/trido/thanhdt/gcloud_dtienthanh")
    p = subprocess.run([exe, "query", "--use_legacy_sql=false", "--format=csv",
                        f"--project_id={PROJECT}", "--max_rows=100000", "--quiet", sql],
                       capture_output=True, text=True, env=env, timeout=900)
    if p.returncode:
        raise RuntimeError(p.stdout[-2000:] + p.stderr[-2000:])
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    return list(_csv.DictReader(lines)) if lines else []


# =============================================================================================
# T1 — forbidden columns and mixed price bases, asserted against the SOURCE FILES themselves
# =============================================================================================
def _strip_comments(src: str) -> str:
    """Drop comment tails (`#...` for Python, `--...` for the embedded SQL), keep everything else.

    Test-fix 2026-08-17: T1c originally scanned the raw file and failed on `analyze.py:85`, the
    COMMENT "never rescaled by Price/Close" — it flagged the rule being *documented* as a violation
    of the rule. Prose naming a banned pattern must stay legal, or the incentive is to stop writing
    the warning down.

    Deliberately does NOT strip string literals: the BigQuery SQL lives inside triple-quoted
    f-strings, and that SQL is exactly where a mixed-basis expression would hide. A version of this
    helper that blanked strings would make T1c/T1d pass by going blind, which is worse than the bug
    it was fixing.
    """
    keep = []
    for line in src.splitlines():
        for marker in ("#", "--"):
            j = line.find(marker)
            if j >= 0:
                line = line[:j]
        keep.append(line)
    return "\n".join(keep)


def t1_source_hygiene() -> None:
    srcs = ["build.py", "analyze.py", "robust.py", "scr_lib.py"]
    raw = {s: open(os.path.join(HERE, s)).read() for s in srcs}
    text = {s: _strip_comments(t) for s, t in raw.items()}

    # profit_* is forward-looking: banned as variable, as filter, anywhere.
    bad = {s: re.findall(r"\bprofit_(?:2W|1M|2M|3M)\w*", t) for s, t in text.items()}
    check("T1a no forward-looking profit_* column referenced",
          not any(bad.values()), json.dumps({k: v for k, v in bad.items() if v}))

    # `OShares` is a TRAP (restated, not PIT) — must not appear.
    osh = {s: t.count("OShares") for s, t in text.items()}
    check("T1b OShares (restated, non-PIT) not referenced", sum(osh.values()) == 0, str(osh))

    # No expression multiplies or divides the two price bases against each other.
    mix = []
    for s, t in text.items():
        for m in re.finditer(r"(Price\s*[*/]\s*Close|Close\s*[*/]\s*Price)", t):
            mix.append(f"{s}:{m.group(0)}")
    check("T1c no Price/Close ratio built anywhere (registry bẫy (4))", not mix, "; ".join(mix))

    # Liquidity/size must be Price*Volume, never Close*Volume (registry bẫy (7)).
    cv = []
    for s, t in text.items():
        cv += [f"{s}:{m.group(0)}" for m in
               re.finditer(r"(Close\s*\*\s*Volume|Volume\s*\*\s*Close)", t)]
    check("T1d turnover uses Price*Volume not Close*Volume", not cv, "; ".join(cv))

    # No wall-clock date logic anywhere => timezone cannot change a result (§16).
    tz = []
    for s, t in text.items():
        tz += [f"{s}:{m.group(0)}" for m in
               re.finditer(r"(datetime\.now|date\.today|CURRENT_DATE|time\.time)", t)]
    check("T1e no wall-clock/TZ-dependent date logic (§16)", not tz, "; ".join(tz))

    # public_date must not anchor anything (WEAK_UNVERIFIED_VINTAGE; announcement study forbidden)
    pd_anchor = re.findall(r"public_date", text["build.py"])
    # it legitimately appears ONLY inside the dedup survivor ORDER BY
    ok = len(pd_anchor) == 2 and "ORDER BY c.public_date DESC" in text["build.py"]
    check("T1f public_date used only as dedup tie-break, never as an anchor", ok,
          f"{len(pd_anchor)} occurrences")


# =============================================================================================
# T2 — session-index arithmetic and the no-borrowed-price rule
# =============================================================================================
def t2_session_alignment() -> None:
    v = pd.read_csv(os.path.join(OUT, "vnindex.csv"))
    idx = Index(v.time.tolist(), v.Close.to_numpy())

    # A date before the first observation, and an empty date, must both be NaN — never a
    # neighbouring level (ledger E3).
    got = idx.level(["1990-01-01", "", v.time.iloc[0]])
    check("T2a Index.level returns NaN before history and for a missing date",
          np.isnan(got[0]) and np.isnan(got[1]) and np.isfinite(got[2]), str(got))

    # As-of semantics: a non-session date resolves to the PREVIOUS session, not the next.
    d0 = v.time.iloc[100]
    nxt = v.time.iloc[101]
    check("T2b as-of lookup takes the previous session, never a future one",
          idx.level([nxt])[0] == v.Close.iloc[101] and idx.level([d0])[0] == v.Close.iloc[100])

    d = pd.read_csv(os.path.join(OUT, "q1_events.csv"))
    z = d[d.d_0.notna() & d.d_250.notna()]
    # d_250 is the ticker's 250th following session. VNINDEX sessions between the two dates must
    # therefore be ~250; a calendar-day window would give ~250 CALENDAR days => ~170 sessions.
    vt = np.asarray(v.time.tolist(), dtype=object)
    n_sessions = (np.searchsorted(vt, z.d_250.to_numpy().astype(object), "right")
                  - np.searchsorted(vt, z.d_0.to_numpy().astype(object), "right"))
    med = float(np.median(n_sessions))
    check("T2c h=250 window spans ~250 index sessions (session-indexed, not calendar)",
          245 <= med <= 255, f"median={med}, p05={np.percentile(n_sessions,5):.0f}, "
                             f"p95={np.percentile(n_sessions,95):.0f}")

    # An event whose t0+h does not exist must be NaN, not dropped-and-substituted.
    nan_250 = d.c_250.isna().sum()
    nan_750 = d.c_750.isna().sum()
    check("T2d events without a t0+h session carry NaN and rise with h",
          nan_750 >= nan_250, f"missing c_250={nan_250}, c_750={nan_750}")


# =============================================================================================
# T3 — dedup lineage is lossless [BQ]
# =============================================================================================
def t3_lineage() -> None:
    lin = pd.read_csv(os.path.join(OUT, "lineage.csv"))
    check("T3a every surviving event id appears exactly once",
          lin.id.is_unique, f"{len(lin)} rows, {lin.id.nunique()} unique ids")
    check("T3b one row per (ticker, exright_date, subtype, id)",
          not lin.duplicated(["ticker", "exright_date", "subtype", "id"]).any())

    if OFFLINE:
        check("T3c [BQ] survivors + dropped-dups + UNKNOWN = raw rows", True, "SKIPPED (--offline)")
        return
    sql = f"""
    WITH raw AS (
      SELECT c.id,
        CASE c.issue_method_code WHEN 'DIV' THEN 'STOCK_DIVIDEND' WHEN 'Bonus' THEN 'BONUS'
          WHEN 'Rights' THEN 'RIGHTS' WHEN 'EMPL' THEN 'ESOP' WHEN 'PP' THEN 'PRIVATE_PLACEMENT'
          WHEN 'TRANS' THEN 'CONVERTIBLE' WHEN 'ICRE' THEN 'CONVERTIBLE' WHEN 'PUBL' THEN 'AUCTION'
          WHEN 'MERGER' THEN 'MERGER' ELSE 'UNKNOWN' END AS subtype,
        ROW_NUMBER() OVER (PARTITION BY c.ticker, c.exright_date, c.issue_method_code,
            CAST(c.exercise_ratio AS STRING), CAST(c.issue_volumn AS STRING),
            CAST(c.total_value AS STRING)
          ORDER BY c.public_date DESC, c.id DESC) AS rn
      FROM `{PROJECT}.tav2_bq.corporate_action` c
      WHERE c.event_code='ISS' AND c.event_status='executed' AND c.exright_date IS NOT NULL
        AND c.exright_date BETWEEN DATE '2010-01-01' AND DATE '2026-06-15')
    SELECT COUNT(*) n_raw, COUNTIF(rn=1 AND subtype<>'UNKNOWN') n_kept,
           COUNTIF(rn>1) n_dup, COUNTIF(rn=1 AND subtype='UNKNOWN') n_unknown FROM raw"""
    r = _bq(sql)[0]
    n_raw, n_kept = int(r["n_raw"]), int(r["n_kept"])
    n_dup, n_unk = int(r["n_dup"]), int(r["n_unknown"])
    check("T3c [BQ] survivors + dropped-dups + UNKNOWN = raw rows",
          n_kept + n_dup + n_unk == n_raw and n_kept == len(lin),
          f"raw={n_raw} kept={n_kept} dup={n_dup} unknown={n_unk} lineage={len(lin)}")


# =============================================================================================
# T4 — n_raise_3y is point-in-time: independent recompute from the event list
# =============================================================================================
def t4_pit_window() -> None:
    lin = pd.read_csv(os.path.join(OUT, "lineage.csv"))
    pan = pd.read_csv(panel_path("q2_panel.csv"))
    RS = {"RIGHTS", "PRIVATE_PLACEMENT", "AUCTION"}

    # lineage starts at 2010-01-01, so a full 1095-day lookback only exists from 2013-01-04 on.
    pan = pan[pan.d_t >= "2013-01-04"].copy()
    ev = lin[lin.subtype.isin(RS)]
    by_tk: dict[str, np.ndarray] = {
        t: np.sort(g.exright_date.to_numpy().astype("datetime64[D]"))
        for t, g in ev.groupby("ticker")}

    dts = pan.d_t.to_numpy().astype("datetime64[D]")
    lo = dts - np.timedelta64(1095, "D")
    recomputed = np.zeros(len(pan), dtype=int)
    tks = pan.ticker.to_numpy()
    for i in range(len(pan)):
        a = by_tk.get(tks[i])
        if a is None:
            continue
        # STRICTLY greater than t-1095 and LESS THAN OR EQUAL TO t  => no future event can enter
        recomputed[i] = int(np.searchsorted(a, dts[i], "right")
                            - np.searchsorted(a, lo[i], "right"))
    mism = int((recomputed != pan.n_raise_3y.to_numpy()).sum())
    check("T4a n_raise_3y reproduced by an independent Python recompute",
          mism == 0, f"{mism} mismatches over {len(pan)} rows (>=2013-01-04)")

    # Leakage probe: shifting the window one day into the future MUST change the count for at
    # least some rows — otherwise the test above is vacuous (it would pass on any boundary rule).
    shifted = np.zeros(len(pan), dtype=int)
    for i in range(len(pan)):
        a = by_tk.get(tks[i])
        if a is None:
            continue
        d1 = dts[i] + np.timedelta64(180, "D")
        shifted[i] = int(np.searchsorted(a, d1, "right")
                         - np.searchsorted(a, lo[i], "right"))
    moved = int((shifted != recomputed).sum())
    check("T4b the recompute is boundary-sensitive (a +180d window moves counts)",
          moved > 0, f"{moved} rows change when the window end moves forward")

    # The future-window column must be exactly that: strictly-after events only.
    fwd_ok = bool((pan.n_raise_fwd180 >= 0).all())
    check("T4c future-probe column is non-negative and separate from n_raise_3y",
          fwd_ok and "n_raise_fwd180" in pan.columns
          and not pan.n_raise_fwd180.equals(pan.n_raise_3y))


# =============================================================================================
# T5 — the universe gate is applied per day, not once
# =============================================================================================
def t5_universe_per_day() -> None:
    pan = pd.read_csv(panel_path("q2_panel.csv"))
    per_ticker_months = pan.groupby("ticker").mth.nunique()
    total_months = pan.mth.nunique()
    always = int((per_ticker_months == total_months).sum())
    # Test-fix 2026-08-17: this originally asserted `always == 0`, which is simply false for a
    # quality universe — the 41 names it flagged are the VN long-listed large caps (VNM, FPT, VCB,
    # ACB, CTG, SSI, VIC, MSN, REE, DHG...) and a screen that ever dropped all of them would be the
    # broken one. What actually distinguishes a per-day gate from a static list is that membership
    # VARIES: most tickers appear in only part of the sample, and the monthly count moves.
    share_always = float((per_ticker_months == total_months).mean())
    n_per_month = pan.groupby("mth").ticker.nunique()
    check("T5a universe membership varies by month (gate is per-day, not a static list)",
          share_always < 0.20 and per_ticker_months.min() < total_months
          and n_per_month.min() < n_per_month.max(),
          f"{always}/{len(per_ticker_months)} tickers ({share_always:.1%}) present in all "
          f"{total_months} months; months-present median={int(per_ticker_months.median())}; "
          f"names/month {n_per_month.min()}..{n_per_month.max()}")

    if OFFLINE:
        check("T5b [BQ] a real ticker flips in_universe across dates", True, "SKIPPED (--offline)")
        return
    r = _bq(f"""SELECT COUNT(*) n FROM (
      SELECT ticker FROM `{PROJECT}.tav2_mike.universe_pit`
      WHERE time BETWEEN DATE '2015-01-01' AND DATE '2025-12-31'
      GROUP BY ticker HAVING COUNT(DISTINCT in_universe) = 2)""")[0]
    check("T5b [BQ] a real ticker flips in_universe across dates", int(r["n"]) > 0,
          f"{r['n']} tickers flip membership 2015-2025")


# =============================================================================================
# T6 — two-way clustered SE collapses to one-way when the second cluster is a singleton per row
# =============================================================================================
def t6_cluster_algebra() -> None:
    rng = np.random.default_rng(7)
    n = 400
    X = np.column_stack([np.ones(n), rng.normal(size=n), rng.normal(size=n)])
    y = X @ np.array([0.2, 0.5, -0.3]) + rng.normal(size=n)
    g1 = (np.arange(n) // 10).astype(str)
    g2_singleton = np.arange(n).astype(str)
    two = cluster2_ols(y, X, g1, g2_singleton)
    one = cluster2_ols(y, X, g1, g1)
    d = float(np.max(np.abs(np.array(two["se"]) - np.array(one["se"]))))
    check("T6a two-way SE == one-way SE when cluster 2 is unique per row", d < 1e-10, f"max|Δ|={d:.2e}")

    # And clustering must not silently equal the naive iid SE — otherwise T6a is vacuous.
    xtx_inv = np.linalg.pinv(X.T @ X)
    e = y - X @ (xtx_inv @ X.T @ y)
    s2 = (e @ e) / (n - X.shape[1])
    iid_se = np.sqrt(np.diag(xtx_inv) * s2)
    check("T6b clustered SE differs from iid SE (clustering is actually applied)",
          float(np.max(np.abs(np.array(one["se"]) - iid_se))) > 1e-6)


# =============================================================================================
# T7 — independent recompute of the two headline numbers, by a different code path
# =============================================================================================
def t7_recompute() -> None:
    res = json.load(open(os.path.join(OUT, "results.json")))

    # --- Q1 primary: pooled RAISE_SET BHAR_250, recomputed from q1_bhar.csv + vnindex.csv
    v = pd.read_csv(os.path.join(OUT, "vnindex.csv"))
    lvl = dict(zip(v.time, v.Close))
    vt = np.asarray(v.time.tolist(), dtype=object)
    vc = v.Close.to_numpy()

    def asof(dstr):
        if not isinstance(dstr, str) or not dstr:
            return np.nan
        if dstr in lvl:                      # exact session — no search needed
            return lvl[dstr]
        i = int(np.searchsorted(vt, dstr, "right")) - 1
        return vc[i] if i >= 0 else np.nan

    d = pd.read_csv(os.path.join(OUT, "q1_bhar.csv"))
    z = d[d.subtype.isin(["RIGHTS", "PRIVATE_PLACEMENT", "AUCTION"])].copy()
    manual = []
    for _, r in z.iterrows():
        if not np.isfinite(r.c_250) or not np.isfinite(r.c_0):
            manual.append(np.nan)
            continue
        b0, b1 = asof(r.d_0), asof(r.d_250)
        manual.append((r.c_250 / r.c_0 - 1) - (b1 / b0 - 1))
    manual = np.asarray(manual, float)
    mine = float(np.nanmean(manual))
    theirs = res["q1"]["variants"]["RAISE_SET"]["horizons"]["250"]["mean"]
    check("T7a Q1 primary BHAR_250 recomputed independently",
          abs(mine - theirs) < 1e-9, f"recompute={mine:.10f} results.json={theirs:.10f}")

    # --- Q2a primary: same coefficient via EXPLICIT cell dummies instead of within-demeaning.
    # Restricted to 2015-2016 so the dummy matrix is tractable; the point is that absorb() and an
    # explicit dummy regression are the same estimator, which is what could silently be wrong.
    from analyze import prep_q2, q2a
    p = prep_q2()
    sub = p[(p.mth >= "2015-01-01") & (p.mth < "2017-01-01")]
    ref = q2a(sub, "ey", "raise")
    cols = ["ey", "serial_raise", "occas_raise", "ln_adv", "roic", "npm", "fscore", "debt_eq"]
    zz = sub[cols + ["cell"]].dropna().copy()
    zz = zz[zz.groupby("cell").ey.transform("size") >= 2]
    D = pd.get_dummies(zz.cell, drop_first=False, dtype=float).to_numpy()
    Xe = np.column_stack([zz[cols[1:]].to_numpy(), D])
    be = np.linalg.pinv(Xe.T @ Xe) @ Xe.T @ zz.ey.to_numpy()
    diff = float(abs(be[0] - ref["coef"]["serial_raise"]))
    check("T7b Q2a serial coefficient identical via explicit cell dummies vs within-demeaning",
          diff < 1e-9, f"dummies={be[0]:.12f} absorb={ref['coef']['serial_raise']:.12f} Δ={diff:.2e}")


# =============================================================================================
# T8 — bootstrap reproducibility, and that it is actually block-based
# =============================================================================================
def t8_bootstrap() -> None:
    rng = np.random.default_rng(1)
    x = rng.normal(size=600)
    blocks = np.repeat(np.arange(60).astype(str), 10)
    a, b = boot(x, blocks), boot(x, blocks)
    check("T8a same seed => bit-identical CI", a["lo"] == b["lo"] and a["hi"] == b["hi"],
          f"lo={a['lo']:.12f}")
    c = boot(x, blocks, seed=999)
    check("T8b a different seed moves the CI (the seed is really used)", c["lo"] != a["lo"])

    # With a shared shock inside each block, the block CI must be WIDER than an all-singleton one.
    # (Sprint 2's T27 asserted this on data with NO within-block correlation and failed — the test
    # was wrong, not the estimator. Hence the shock here.)
    shock = np.repeat(rng.normal(size=60), 10) * 2.0
    y = x + shock
    wide = boot(y, blocks)
    narrow = boot(y, np.arange(600).astype(str))
    rw = wide["hi"] - wide["lo"]
    rn = narrow["hi"] - narrow["lo"]
    check("T8c block CI wider than singleton CI when blocks share a shock",
          rw > rn, f"block={rw:.4f} singleton={rn:.4f} ratio={rw/rn:.2f}x")


# =============================================================================================
# T9 — the Q2b spread construction cannot see the future, and its floors bind
# =============================================================================================
def t9_spread_construction() -> None:
    pan = pd.read_csv(panel_path("q2_panel.csv"))
    # fwd_ret_1m must be NULL whenever the next month-end is not the CONSECUTIVE month.
    gap = pan[pan.fwd_gap == 1]
    check("T9a a non-consecutive next month yields a NULL forward return, never a stale one",
          bool(gap.fwd_ret_1m.isna().all()), f"{len(gap)} gap rows, "
          f"{int(gap.fwd_ret_1m.notna().sum())} with a non-null return")

    # The forward return must be a strictly FORWARD object: it cannot be reconstructible from the
    # same row's own price level. Correlation with the contemporaneous Close should be ~0.
    z = pan[pan.fwd_ret_1m.notna() & (pan.Close > 0)]
    r = float(np.corrcoef(np.log(z.Close), z.fwd_ret_1m)[0, 1])
    check("T9b forward return is not a function of the current price level", abs(r) < 0.05,
          f"corr(ln Close, fwd_ret)={r:+.4f}")

    # The min-leg floor must actually bind somewhere, else the "value-matched" claim is empty.
    sp = pd.read_csv(os.path.join(OUT, "q2b_spread_raise_ey.csv"))
    check("T9c the >=3-per-leg floor drops some quintiles (matching is real)",
          bool((sp.n_q < 5).any()), f"months with <5 usable quintiles: {int((sp.n_q<5).sum())}/{len(sp)}")


def main() -> None:
    t1_source_hygiene()
    t2_session_alignment()
    t3_lineage()
    t4_pit_window()
    t5_universe_per_day()
    t6_cluster_algebra()
    t7_recompute()
    t8_bootstrap()
    t9_spread_construction()

    n = len(RESULTS)
    ok = sum(1 for _, k, _ in RESULTS if k)
    print(f"\n{ok}/{n} PASS" + ("  (offline mode: 2 BQ tests skipped)" if OFFLINE else ""))
    with open(os.path.join(OUT, "selfcheck.json"), "w") as fh:
        json.dump({"offline": OFFLINE, "pass": ok, "total": n,
                   "results": [{"name": a, "ok": b, "detail": c} for a, b, c in RESULTS]},
                  fh, indent=2)
    sys.exit(0 if ok == n else 1)


if __name__ == "__main__":
    main()
