#!/usr/bin/env python3
"""cpi_vn_tier15_selfcheck.py — selfcheck for the H2 wire (job Taylor_20260927_022319): Tier 1.5
(FiinPro-X real monthly CPI, 2008-01..2026-08) inserted between Tier 1 (live NSO, absolute priority)
and Tier 2 (linear interpolation, kept as fallback), plus the §14 freshness gate and the rename of
the mislabeled NSO_CPI_YOY_AVG_REAL -> NSO_CPI_CORE_YOY_REAL.

WHAT IS ACTUALLY BEING PROVEN (finding `fiinprox-H2-cpi-swap`):
  1. Tier 1 is untouched: the 13 live-NSO months are byte-identical before and after.
  2. Removing the snapshot reproduces the PRE-WIRE series exactly -- so the fallback is a real
     fallback, not a different code path that happens to look similar.
  3. The consequence is the MEASURED one and nothing more: macro_confidence_regime relabels exactly
     27/185 months on REG_C and 17/185 on REG_B -- the same month lists the finding published, no
     more and no fewer -- and DCF fair value moves 0.0000% on all 7 valuable names.
  4. The §14 gate fires when (and only when) a caller asks for a month no real tier covers.

The A/B is a TRUE before/after: "old" is cpi_vn.py at CPI_OLD_REF (default f4b081b7^, the parent
of the wire commit, read via `git show` -- 2026-10-09; it used to be the canonical checkout's file,
which stopped being "old" the moment the wire merged), "new" is this checkout's. Nothing is re-implemented, so a bug in the wire cannot hide
behind a matching bug in the test.

ENVIRONMENT DEPENDENCIES (verify-before-done): TZ (none by construction -- all months are tz-naive
Timestamps, no now(); broken on purpose by --all-tz); CPI_OLD_ROOT (canonical checkout, needs
mike/data/ and data/macro_features.csv); FIINPRO_CPI_CSV (the snapshot -- absent in a worktree,
which is exactly case 2).

Usage:  python3 cpi_vn_tier15_selfcheck.py [--all-tz]
"""
import importlib.util, os, subprocess, sys

OLD_ROOT = os.environ.get("CPI_OLD_ROOT", "/home/trido/thanhdt/WorkingClaude")
NEW_ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("FIINPRO_CPI_CSV",
                      os.path.join(OLD_ROOT, "mike", "data", "fiinprox_cpi_monthly_20260914.csv"))
FP_CSV = os.environ["FIINPRO_CPI_CSV"]
REF = os.path.join(OLD_ROOT, "mike", "agents", "Taylor", "research",
                   "fiinprox_h3_h1_h2_20260927")

import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd

N_OK, FAILS = 0, []


def ok(cond, label, detail=""):
    global N_OK
    if cond: N_OK += 1
    else: FAILS.append(label + (f" -- {detail}" if detail else ""))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m); return m


# Chân "old" = cpi_vn.py ở CHA của commit wire (f4b081b7), đọc qua `git show` — KHÔNG phải file
# đang nằm trong cây canonical. Bản đầu đọc file canonical: đúng khi chạy từ worktree TRƯỚC merge,
# nhưng sau merge old == new ⇒ test_rename AttributeError mỗi đêm (selfcheck-red 2026-09-27→10-09).
# `__file__` giữ trỏ OLD_ROOT để mọi đường dẫn tương đối của module y như bản canonical.
# Override: CPI_OLD_REF=<ref>.
OLD_REF = os.environ.get("CPI_OLD_REF", "f4b081b7^")


def load_ref(ref, name):
    src = subprocess.run(["git", "show", f"{ref}:./cpi_vn.py"], cwd=OLD_ROOT,
                         capture_output=True, text=True, check=True).stdout
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None))
    m.__file__ = os.path.join(OLD_ROOT, "cpi_vn.py"); sys.modules[name] = m
    exec(compile(src, f"{ref}:cpi_vn.py", "exec"), m.__dict__); return m


OLD = load_ref(OLD_REF, "cpi_old")
NEW = load(os.path.join(NEW_ROOT, "cpi_vn.py"), "cpi_new")
END = "2026-08-01"


# =====================================================================================
def test_rename():
    ok(hasattr(NEW, "NSO_CPI_CORE_YOY_REAL"), "NSO_CPI_CORE_YOY_REAL exists")
    ok(not hasattr(NEW, "NSO_CPI_YOY_AVG_REAL"), "old misleading name NSO_CPI_YOY_AVG_REAL is gone")
    ok(NEW.NSO_CPI_CORE_YOY_REAL == OLD.NSO_CPI_YOY_AVG_REAL,
       "rename is value-preserving (dict unchanged)")
    # the rename is only correct if the values really ARE core inflation, not the YTD average
    f = pd.read_csv(FP_CSV)
    core = dict(zip(f["month"].astype(str) + "-01", f["core_yoy_pct"]))
    head = dict(zip(f["month"].astype(str) + "-01", f["cpi_yoy_pct"]))
    nc = sum(1 for k, v in NEW.NSO_CPI_CORE_YOY_REAL.items()
             if k in core and pd.notna(core[k]) and abs(core[k] - v) < 0.005)
    nh = sum(1 for k, v in NEW.NSO_CPI_CORE_YOY_REAL.items()
             if k in head and pd.notna(head[k]) and abs(head[k] - v) < 0.005)
    n = len(NEW.NSO_CPI_CORE_YOY_REAL)
    ok(nc == n, f"renamed constant matches FiinPro core_yoy_pct {n}/{n}", f"only {nc}/{n}")
    ok(nh == 0, "and matches the HEADLINE series 0/13 (so the old 'bình quân' label was wrong)",
       f"{nh}/{n} matched headline")
    print(f"  [1] rename: core match {nc}/{n}, headline match {nh}/{n}")
    # nobody reads it -- re-grep every .py under both roots rather than trusting the finding
    hits = subprocess.run(["grep", "-rn", "--include=*.py", "NSO_CPI_YOY_AVG_REAL", OLD_ROOT],
                          capture_output=True, text=True).stdout.strip().splitlines()
    hits = [h for h in hits if "/wt-" not in h and "/worktrees/" not in h
            and not h.split(":")[0].endswith(("cpi_vn.py", "cpi_vn_tier15_selfcheck.py"))]
    ok(not hits, "no .py outside cpi_vn.py reads the old name (rename cannot break a caller)",
       "; ".join(hits[:3]))
    print(f"  [1] grep for the old name in .py files: {len(hits)} external reader(s)")


# =====================================================================================
def test_tier1_untouched(a, b):
    real = {pd.to_datetime(k): v for k, v in NEW.NSO_CPI_YOY_REAL.items()}
    A = a.set_index("time")["cpi_yoy"]; B = b.set_index("time")["cpi_yoy"]
    bad_old = [d for d, v in real.items() if d in A.index and A[d] != v]
    bad_new = [d for d, v in real.items() if d in B.index and B[d] != v]
    ok(not bad_old and not bad_new,
       f"Tier 1: all {len(real)} live-NSO months equal the declared print in BOTH legs",
       f"old {bad_old} new {bad_new}")
    moved = [d for d in real if d in A.index and d in B.index and A[d] != B[d]]
    ok(not moved, "Tier 1 months are byte-identical before vs after the wire", str(moved))
    ok(bool(b.loc[b.time.isin(real), "is_real_nso"].all()),
       "is_real_nso flags exactly the Tier-1 months")
    ok(not bool(b.loc[b.time.isin(real), "is_fiinpro"].any()),
       "a Tier-1 month is never also flagged Tier 1.5 (flags are a partition)")
    print(f"  [2] Tier 1: {len(real)}/{len(real)} months identical; flags disjoint")


def test_flags_partition(b):
    n = len(b)
    t1 = b.is_real_nso.astype(int); t15 = b.is_fiinpro.astype(int); t3 = b.is_backfill_2007_2010.astype(int)
    ok(int((t1 + t15 + t3 > 1).sum()) == 0, "no month claims two tiers at once")
    served = int((t1 + t15 + t3).sum())
    print(f"  [2] tier partition: T1={int(t1.sum())} T1.5={int(t15.sum())} T3={int(t3.sum())} "
          f"T2(implicit)={n - served} of {n} months")
    ok(b.cpi_yoy.notna().all(), "every month in the window has a CPI value (no NaN hole)")


# =====================================================================================
def test_fallback_is_prewire():
    """Remove the snapshot: the new module must reproduce the OLD series EXACTLY."""
    saved_env = os.environ.get("FIINPRO_CPI_CSV")
    os.environ["FIINPRO_CPI_CSV"] = "/nonexistent/fiinprox_cpi_missing.csv"
    try:
        M = load(os.path.join(NEW_ROOT, "cpi_vn.py"), "cpi_new_nofile")
        f = M.cpi_monthly_df(end=END); o = OLD.cpi_monthly_df(end=END)
        same = f["cpi_yoy"].equals(o["cpi_yoy"]) and f["time"].equals(o["time"])
        ok(same, "snapshot absent -> series is byte-identical to the pre-wire module",
           f"max|diff|={float((f.cpi_yoy - o.cpi_yoy).abs().max()):.6f}")
        ok(not f["is_fiinpro"].any(), "snapshot absent -> is_fiinpro all False")
        ok(f["is_backfill_2007_2010"].sum() == o["is_backfill_2007_2010"].sum(),
           "snapshot absent -> Tier 3 coverage reverts to its pre-wire extent",
           f"{int(f.is_backfill_2007_2010.sum())} vs {int(o.is_backfill_2007_2010.sum())}")
        print(f"  [3] fallback reproduces pre-wire series exactly "
              f"(T3 months {int(f.is_backfill_2007_2010.sum())}, same as before)")
    finally:
        if saved_env is None: os.environ.pop("FIINPRO_CPI_CSV", None)
        else: os.environ["FIINPRO_CPI_CSV"] = saved_env


def test_freshness_gate():
    """§14: the snapshot is FROZEN, so a caller reaching past every real tier must be told."""
    M = load(os.path.join(NEW_ROOT, "cpi_vn.py"), "cpi_new_fresh")
    real_last, fp_last, gap = M.cpi_coverage(END)
    ok(str(fp_last.date()) == "2026-08-01",
       "coverage reads Tier 1.5's last month FROM THE FILE (not hardcoded)", str(fp_last))
    ok(gap == [], f"end={END} is covered -> no gap reported", str(gap))
    _, _, gap2 = M.cpi_coverage("2026-12-01")
    ok([str(d.date()) for d in gap2] == ["2026-09-01", "2026-10-01", "2026-11-01", "2026-12-01"],
       "end=2026-12-01 -> gap is exactly the 4 uncovered months",
       str([str(d.date()) for d in gap2]))
    ok(any("COVERAGE GAP" in w for w in M._WARNED), "the gap actually printed a warning")
    n_before = len(M._WARNED)
    M.cpi_coverage("2026-12-01")
    ok(len(M._WARNED) == n_before, "the warning is ONE-TIME (dcf_valuation calls this per run)")
    # MUTATION: hardcoding the last month instead of reading the file must be caught
    M2 = load(os.path.join(NEW_ROOT, "cpi_vn.py"), "cpi_new_mut")
    M2.fiinpro_cpi_series = lambda: pd.Series(
        [3.0], index=pd.to_datetime(["2030-01-01"]))         # pretend the snapshot never expires
    _, _, gap3 = M2.cpi_coverage("2026-12-01")
    ok(gap3 == [], "MUTATION: a never-expiring Tier 1.5 silences the gate -> the gate is data-driven")
    print(f"  [4] §14 gate: fp_last={fp_last:%Y-%m} from file; gap(2026-12)={len(gap2)} months; "
          f"warn-once OK")


# =====================================================================================
def test_matches_published_series(b):
    """Cross-check against the finding's own artifact: the wired series must equal the A/B's cpi_new."""
    p = os.path.join(REF, "h2_cpi_series.csv")
    if not os.path.exists(p):
        print(f"  [5] SKIP cross-check (artifact absent: {p})"); return
    ref = pd.read_csv(p, parse_dates=["time"])
    m = b[["time", "cpi_yoy"]].merge(ref[["time", "cpi_new"]], on="time", how="inner")
    d = (m.cpi_yoy - m.cpi_new).abs()
    ok(len(m) > 200 and float(d.max()) < 1e-9,
       "wired series == the finding's published cpi_new, month for month",
       f"n={len(m)} max|diff|={float(d.max()):.9f}")
    print(f"  [5] cross-check vs h2_cpi_series.csv: n={len(m)}, max|diff|={float(d.max()):.2e}")


def regime_labels(cpi_df, dep_mod, mf_raw):
    """REG_B / REG_C monthly labels, recipe copied from macro_confidence_regime.py:
       infl_hot = (cpi_yoy_chg3 > 0) | (cpi_yoy > 4.0);  REG_C = infl_hot | dep_rising;
       REG_B = usd_up126 & REG_C."""
    s = cpi_df.set_index("time")["cpi_yoy"]
    f = pd.DataFrame({"cpi": s, "chg3": s.diff(3)})
    f["infl_hot"] = (f["chg3"] > 0) | (f["cpi"] > 4.0)
    c = f.reset_index()[["time", "infl_hot"]].rename(columns={"time": "ctime"})
    mf = pd.merge_asof(mf_raw.sort_values("time"), c.sort_values("ctime"),
                       left_on="time", right_on="ctime", direction="backward")
    mf["REG_C"] = mf["infl_hot"] | mf["dep_rising"]
    mf["REG_B"] = mf["usd_up126"] & mf["REG_C"]
    mf["ym"] = mf["time"].dt.to_period("M")
    g = mf.groupby("ym").agg(C=("REG_C", "mean"), B=("REG_B", "mean"))
    return (g["C"] >= 0.5), (g["B"] >= 0.5)


def test_regime(a, b):
    sys.path.insert(0, OLD_ROOT)
    from deposit_rate_vn import merge_deposit
    mf = pd.read_csv(os.path.join(OLD_ROOT, "data", "macro_features.csv"),
                     parse_dates=["time"])[["time", "USDVND"]]
    mf = merge_deposit(mf.sort_values("time"))
    mf["usd_up126"] = (mf["USDVND"] / mf["USDVND"].shift(6 * 21) - 1.0) > 0
    mf["dep_rising"] = (mf["deposit_rate"] - mf["deposit_rate"].shift(6 * 21)) > 0
    Co, Bo = regime_labels(a, None, mf)
    Cn, Bn = regime_labels(b, None, mf)
    chC = [str(x) for x in Co.index[Co.values != Cn.values]]
    chB = [str(x) for x in Bo.index[Bo.values != Bn.values]]
    ok(len(Co) == 185, "regime window is the 185 months the finding reported", f"{len(Co)}")
    ok(len(chC) == 27, "REG_C relabels EXACTLY 27/185 months (no more, no fewer)", f"{len(chC)}")
    ok(len(chB) == 17, "REG_B relabels EXACTLY 17/185 months", f"{len(chB)}")
    print(f"  [6] REG_C {len(chC)}/{len(Co)} relabeled, REG_B {len(chB)}/{len(Bo)}")
    p = os.path.join(REF, "h2_regime_flips.csv")
    if os.path.exists(p):
        ref = pd.read_csv(p)
        rC = sorted(ref[ref.regime == "REG_C"].month.astype(str))
        rB = sorted(ref[ref.regime == "REG_B"].month.astype(str))
        ok(sorted(chC) == rC, "the 27 REG_C months are the SAME months the finding listed",
           f"extra={sorted(set(chC)-set(rC))} missing={sorted(set(rC)-set(chC))}")
        ok(sorted(chB) == rB, "the 17 REG_B months are the SAME months the finding listed",
           f"extra={sorted(set(chB)-set(rB))} missing={sorted(set(rB)-set(chB))}")
        print(f"  [6] month lists match the published artifact exactly")
    # the finding's central caveat, asserted rather than trusted: nothing moves in 2011 or 2022-H2
    ep = [m for m in chC if m.startswith("2011") or m in ("2022-05", "2022-06", "2022-07",
                                                          "2022-08", "2022-09", "2022-10",
                                                          "2022-11", "2022-12")]
    ok(not ep, "0 relabels inside the 2011 / 2022-H2 inflation episodes (the finding's caveat)",
       str(ep))
    print(f"  [6] relabels inside the 2011 / 2022-H2 episodes: {len(ep)}")
    return chC, chB


# =====================================================================================
def test_dcf(b):
    """Same DCF code, old CPI vs new CPI. Expected delta: exactly 0.0000% (default DCF_TERMINAL_MODE
    =cap_rf clamps g_term at r_f), on every name that produces a value."""
    cwd = os.getcwd()
    try:
        os.chdir(OLD_ROOT); sys.path.insert(0, OLD_ROOT)
        import dcf_valuation as dv
        TK = ["CSV", "DGC", "DRI", "NCT", "SAB", "TV1", "VNM"]
        ASOF = "2026-09-26"

        def leg(fn):
            dv._CPI_DF = None; dv._TG_CACHE.clear()
            dv._cpi.cpi_monthly_df = fn
            tg = dv.terminal_growth(ASOF); g = dv.terminal_growth_mode(ASOF)
            fv = {}
            for t in TK:
                try:
                    r = dv.fair_value(t, ASOF)
                    fv[t] = float(r["fair_value_ps"]) if isinstance(r, dict) and r.get("fair_value_ps") else None
                except Exception as e:
                    fv[t] = None
            return tg, g, fv

        tg_o, g_o, fv_o = leg(OLD.cpi_monthly_df)
        tg_n, g_n, fv_n = leg(NEW.cpi_monthly_df)
        priced = [t for t in TK if fv_o.get(t) and fv_n.get(t)]
        deltas = {t: 100.0 * (fv_n[t] / fv_o[t] - 1.0) for t in priced}
        ok(len(priced) == 7, "all 7 named tickers price on both legs", f"{len(priced)}: {priced}")
        ok(all(abs(v) < 1e-9 for v in deltas.values()),
           "DCF fair value delta is EXACTLY 0 on all 7 names",
           str({k: round(v, 6) for k, v in deltas.items() if abs(v) >= 1e-9}))
        ok(abs(g_o - g_n) < 1e-12,
           "g_term identical -- the r_f cap is what makes the delta 0 (mechanism, not luck)",
           f"{g_o:.8f} vs {g_n:.8f}")
        ok(abs(tg_o - tg_n) > 1e-9,
           "...and the 5y-avg CPI DID move, so the 0 is not a no-op test",
           f"{tg_o*100:.4f}% vs {tg_n*100:.4f}% -- identical means the new CPI never reached DCF")
        print(f"  [7] DCF: 5y-avg CPI {tg_o*100:.4f}% -> {tg_n*100:.4f}% "
              f"(Δ {100*(tg_n-tg_o):+.4f}pp); g_term {g_o*100:.4f}% -> {g_n*100:.4f}%; "
              f"fair value Δ = {max(abs(v) for v in deltas.values()):.1e}% on {len(priced)} names")
    finally:
        os.chdir(cwd)


# =====================================================================================
def main():
    if "--all-tz" in sys.argv:
        base = dict(os.environ); base.pop("TZ", None)
        rcs = []
        for label, tz in (("no TZ", None), ("UTC", "UTC"), ("Pacific/Auckland", "Pacific/Auckland")):
            e = dict(base)
            if tz: e["TZ"] = tz
            print(f"\n{'='*78}\n== TZ = {label}\n{'='*78}")
            rcs.append((label, subprocess.run([sys.executable, os.path.abspath(__file__)], env=e).returncode))
        print("\n" + "=" * 78)
        for label, rc in rcs:
            print(f"  TZ {label:<20} -> {'PASS' if rc == 0 else 'FAIL'} (rc={rc})")
        sys.exit(0 if all(rc == 0 for _, rc in rcs) else 1)

    print(f"cpi_vn Tier-1.5 selfcheck | TZ={os.environ.get('TZ','(unset)')}")
    print(f"  old = {OLD_REF}:cpi_vn.py (git, cwd {OLD_ROOT})   new = {NEW_ROOT}/cpi_vn.py")
    a = OLD.cpi_monthly_df(end=END); b = NEW.cpi_monthly_df(end=END)
    ok(len(a) == len(b), "same month index before/after", f"{len(a)} vs {len(b)}")
    test_rename()
    test_tier1_untouched(a, b)
    test_flags_partition(b)
    test_fallback_is_prewire()
    test_freshness_gate()
    test_matches_published_series(b)
    chC, chB = test_regime(a, b)
    test_dcf(b)

    print(f"\n{'='*78}")
    print(f"assertions PASSED : {N_OK}")
    print(f"assertions FAILED : {len(FAILS)}")
    for f in FAILS: print(f"  [FAIL] {f}")
    print(f"regime relabels   : REG_C {len(chC)}/185, REG_B {len(chB)}/185")
    print("VERDICT           : " + ("PASS" if not FAILS else "FAIL"))
    sys.exit(0 if not FAILS else 1)


if __name__ == "__main__":
    main()
