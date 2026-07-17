# -*- coding: utf-8 -*-
"""
dcf_earning_power_test.py — Study B (walk-forward MoS IC) + orthogonality-vs-1/PE for the
EXPERIMENTAL DCF variants (dcf_earning_power.py), compared apples-to-apples with the canonical
FCFE model. Job Taylor_20260717_063638.

Isolates two axes independently:
  BASIS      : fcfe (canonical)  vs  earning_power        (Việc 1)
  TERM_MODE  : cpi (canonical)   vs  cpi_gdp_half / cap_rf / cpi_gdp_full   (Việc 3)

Variants computed (6): so each axis moves alone, plus the combined best-guess.
  V0  fcfe          + cpi            == canonical baseline (recomputed here for strict comparability)
  V1  earning_power + cpi            == Việc-1 basis change ALONE
  V2  fcfe          + cpi_gdp_half   == Việc-3 terminal-g change ALONE (faded GDP)
  V3  fcfe          + cap_rf         == Việc-3 alternative (Damodaran risk-free cap)
  V4  fcfe          + cpi_gdp_full   == Việc-3 naive full GDP (fragility demo)
  V5  earning_power + cpi_gdp_half   == combined

Methodology is IDENTICAL to dcf_backtest.py Study B and dcf_orthogonality_test.py (reused verbatim
where possible): FV once per financial release (point-in-time), as-of merged to a monthly price
panel, non-financial rating<=3 universe, 15-month FV freshness, cross-sectional Spearman IC per
month averaged, walk-forward IS(2014-19)/OOS(2020-26), t on the MONTHLY IC series (Spyros).

Two IC reads per variant:
  (a) OWN panel  — every row that variant can value (EP covers MORE names: FCFE-negative build-outs).
  (b) COMMON subset — only rows where ALL 6 variants compute → strict isolation of the ranking change,
      composition held fixed.

Caches to the experiment namespace (coding_guidelines §8) — never the pinned fv_releases.parquet.
Run: DCF_REFRESH=1 $DNA_PYEXE dcf_earning_power_test.py     (build caches, then all tables)
     $DNA_PYEXE dcf_earning_power_test.py                    (reuse caches)
"""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import duckdb
import dcf_valuation as D
import dcf_earning_power as EP

EXPDIR = f"{WORKDIR}/mike/agents/Taylor/dcf_exp"
CACHE = f"{EXPDIR}/fv_releases_epvariants.parquet"
RATINGS = "data/bq_cache/fa_ratings_8l.parquet"
TICKER = "data/bq_cache/ticker/2*.parquet"
TARGETS = ["profit_1M", "profit_2M", "profit_3M"]

# variant key -> (basis, term_mode)
VARIANTS = {
    "V0_fcfe_cpi":        ("fcfe",          "cpi"),
    "V1_ep_cpi":          ("earning_power", "cpi"),
    "V2_fcfe_gdphalf":    ("fcfe",          "cpi_gdp_half"),
    "V3_fcfe_caprf":      ("fcfe",          "cap_rf"),
    "V4_fcfe_gdpfull":    ("fcfe",          "cpi_gdp_full"),
    "V5_ep_gdphalf":      ("earning_power", "cpi_gdp_half"),
}
VKEYS = list(VARIANTS)


def spearman_ic(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    m = (~np.isnan(a)) & (~np.isnan(b))
    if m.sum() < 8:
        return np.nan
    return pd.Series(a[m]).rank().corr(pd.Series(b[m]).rank())


def resid_rank(y, x):
    """rank-space residual of y after neutralizing by x (1D)."""
    y = np.asarray(y, float); x = np.asarray(x, float)
    mask = (~np.isnan(y)) & (~np.isnan(x))
    out = np.full(len(y), np.nan)
    if mask.sum() < 10:
        return out
    yr = pd.Series(y[mask]).rank().values
    xr = pd.Series(x[mask]).rank().values
    X = np.column_stack([np.ones(len(yr)), xr])
    beta, *_ = np.linalg.lstsq(X, yr, rcond=None)
    out[mask] = yr - X @ beta
    return out


# ---------------------------------------------------------------- FV cache (all variants, 1 pass)
# Efficient inline build: the candidate set is already NON-FINANCIAL (route-filtered in SQL), so we
# skip D.is_financial (its full-frame filter was the bottleneck); and the base cash-flow / growth
# assembly is shared across variants — computed ONCE per release, then combined per (basis, mode).
_MODES = ("cpi", "cpi_gdp_half", "cap_rf", "cpi_gdp_full")


def _fv_one_release(rows, t):
    """Return {variant_key: fv_ps or nan} + {variant_key: gordon_bool} for one (ticker, release).
    rows = the ticker's point-in-time frame (time <= t already guaranteed by caller)."""
    out = {k: np.nan for k in VKEYS}
    gc = {k: False for k in VKEYS}
    last = rows.iloc[-1]
    cfoa3 = float(last.CF_OA_3Y) if pd.notna(last.CF_OA_3Y) else np.nan
    if not (cfoa3 > 0):
        return out, gc
    oshares = float(last.OShares) if pd.notna(last.OShares) else 0.0
    if not (oshares > 0):
        return out, gc
    annual_np = D._annual_series(rows, ["NP_P0", "NP_P1", "NP_P2", "NP_P3"])
    # bases
    cfinv3 = float(last.CF_Invest_3Y) if pd.notna(last.CF_Invest_3Y) else 0.0
    base_fcfe = (cfoa3 + cfinv3) / 3.0
    ep_pts = [x for x in annual_np[:3] if x is not None and not (isinstance(x, float) and np.isnan(x))]
    base_ep = float(np.mean(ep_pts)) if ep_pts else np.nan
    bases = {"fcfe": base_fcfe if base_fcfe > 0 else np.nan,
             "earning_power": base_ep if (ep_pts and base_ep > 0) else np.nan}
    # growth (shared)
    g_raw, _ = D.recency_weighted_growth(annual_np)
    r = D.discount_rate(t)
    # terminal g per mode (date-only; EP.terminal_growth_mode memoizes CPI + cheap GDP)
    gT = {md: EP.terminal_growth_mode(t, md) for md in _MODES}
    for k, (basis, mode) in VARIANTS.items():
        base = bases[basis]
        if not (base > 0):
            continue
        g_T = gT[mode]
        g_r = g_T if np.isnan(g_raw) else g_raw
        g_clamp = float(np.clip(g_r, D.G_EXPLICIT_FLOOR, D.G_EXPLICIT_CAP))
        g_exp = g_T + D.GROWTH_SHRINK * (g_clamp - g_T)
        if r <= g_T:
            g_T = r - 0.01
            gc[k] = True
        out[k] = D._fv_per_share(base, g_exp, g_T, r, oshares)
    return out, gc


def build_cache():
    c = duckdb.connect(":memory:")
    cand = c.execute(f"""SELECT DISTINCT ticker FROM read_parquet('{RATINGS}')
        WHERE rating<=3 AND route NOT IN ('BANK','INSURANCE','SECURITIES')""").df().ticker.tolist()
    fin = D._load_financials()
    fin_by_tk = {tk: g for tk, g in fin.groupby("ticker")}
    n_gordon = {k: 0 for k in VKEYS}
    rows = []
    done = 0
    for tk in cand:
        g = fin_by_tk.get(tk)
        if g is None or len(g) < 5:
            continue
        g = g.reset_index(drop=True)
        times = [x for x in g.time.unique() if pd.Timestamp(x) >= pd.Timestamp("2012-06-01")]
        for t in times:
            sub = g[g.time <= t]
            if len(sub) < 4:
                continue
            fvd, gcd = _fv_one_release(sub, pd.Timestamp(t))
            if any(pd.notna(v) for v in fvd.values()):
                rec = {"ticker": tk, "rel_time": pd.Timestamp(t)}
                rec.update(fvd)
                rows.append(rec)
                for k in VKEYS:
                    if gcd[k]:
                        n_gordon[k] += 1
        done += 1
        if done % 300 == 0:
            print(f"  ...{done}/{len(cand)} tickers, {len(rows)} release-points", flush=True)
    fv = pd.DataFrame(rows).sort_values(["ticker", "rel_time"]).reset_index(drop=True)
    os.makedirs(EXPDIR, exist_ok=True)
    fv.to_parquet(CACHE)
    print(f"\nFV cache built: {fv.ticker.nunique()} tickers, {len(fv)} release-points -> {CACHE}")
    print("Gordon-guard clamp count (r <= g_term fired → TV explosive, FRAGILE):")
    for k in VKEYS:
        ok_n = fv[k].notna().sum()
        print(f"  {k:18s} computed={ok_n:6d}  gordon_clamped={n_gordon[k]:5d} "
              f"({100*n_gordon[k]/max(ok_n,1):.1f}%)")
    return fv


def load_cache():
    if os.path.exists(CACHE) and not os.environ.get("DCF_REFRESH"):
        fv = pd.read_parquet(CACHE)
        print(f"FV cache loaded: {fv.ticker.nunique()} tickers, {len(fv)} release-points")
        return fv
    return build_cache()


# ---------------------------------------------------------------- panel assembly
def build_panel(fv):
    c = duckdb.connect(":memory:")
    cand = c.execute(f"""SELECT DISTINCT ticker FROM read_parquet('{RATINGS}')
        WHERE rating<=3 AND route NOT IN ('BANK','INSURANCE','SECURITIES')""").df().ticker.tolist()
    cand_sql = "(" + ",".join(f"'{t}'" for t in cand) + ")"
    px = c.execute(f"""
        SELECT ticker, tdate, Price, profit_1M, profit_2M, profit_3M, PE FROM (
          SELECT ticker, CAST(time AS DATE) AS tdate, Price, profit_1M, profit_2M, profit_3M, PE,
                 row_number() OVER (PARTITION BY ticker, date_trunc('month',CAST(time AS DATE))
                                    ORDER BY CAST(time AS DATE)) rn
          FROM read_parquet('{TICKER}')
          WHERE ticker IN {cand_sql} AND CAST(time AS DATE) >= DATE '2014-01-01'
        ) WHERE rn=1 AND Price IS NOT NULL
    """).df().rename(columns={"tdate": "time"})
    px["time"] = pd.to_datetime(px["time"])
    px = px.sort_values(["ticker", "time"]).reset_index(drop=True)

    merged = []
    for tk, gp in px.groupby("ticker"):
        gf = fv[fv.ticker == tk].drop(columns=["ticker"])
        if len(gf) == 0:
            continue
        merged.append(pd.merge_asof(gp.sort_values("time"), gf.sort_values("rel_time"),
                                    left_on="time", right_on="rel_time", direction="backward"))
    m = pd.concat(merged, ignore_index=True)

    # as-of rating<=3
    rat = c.execute(f"SELECT ticker, time, rating FROM read_parquet('{RATINGS}')").df()
    rat["time"] = pd.to_datetime(rat["time"]); rat = rat.sort_values(["ticker", "time"])
    mm = []
    for tk, gp in m.groupby("ticker"):
        rr = rat[rat.ticker == tk]
        if len(rr) == 0:
            continue
        mm.append(pd.merge_asof(gp.sort_values("time"), rr.sort_values("time"),
                                on="time", by="ticker", direction="backward"))
    m = pd.concat(mm, ignore_index=True)
    m = m[(m.rating <= 3) & (m.rel_time.notna())]
    m = m[(m.time - m.rel_time).dt.days <= 460]          # 15-month freshness (identical to Study B)
    m["inv_pe"] = np.where(m.PE > 0, 1.0 / m.PE, np.nan)
    m["year"] = m.time.dt.year
    for k in VKEYS:
        m[f"mos_{k}"] = np.where(m[k] > 0, (m[k] - m.Price) / m[k], np.nan)
    return m


def windows(m):
    return [("ALL", m), ("IS 14-19", m[m.year <= 2019]), ("OOS 20-26", m[m.year >= 2020])]


def ic_cell(df, moscol, tgt):
    s = df.groupby("time").apply(lambda x: spearman_ic(x[moscol].values, x[tgt].values)).dropna()
    if len(s) == 0:
        return None
    t = s.mean() / (s.std() / np.sqrt(len(s))) if s.std() > 0 else np.nan
    return s.mean(), t, len(s)


def study_b(m, subset_label, restrict_common=False):
    print("\n" + "=" * 92)
    print(f"STUDY B — MoS forward-return IC   [{subset_label}]")
    if restrict_common:
        common = m[[k for k in VKEYS]].notna().all(axis=1) & m[[f"mos_{k}" for k in VKEYS]].notna().all(axis=1)
        m = m[common]
        print(f"   COMMON subset (all 6 variants compute): {len(m)} rows")
    print("=" * 92)
    for k in VKEYS:
        moscol = f"mos_{k}"
        n_ok = m[moscol].notna().sum()
        print(f"\n  {k}  (basis={VARIANTS[k][0]}, term={VARIANTS[k][1]})   rows_valid={n_ok}")
        for wl, w in windows(m):
            parts = []
            for tgt in TARGETS:
                r = ic_cell(w, moscol, tgt)
                parts.append(f"{tgt.split('_')[1]}: n/a" if r is None
                             else f"{tgt.split('_')[1]}={r[0]:+.4f}(t{r[1]:+.1f})")
            print(f"    {wl:9s}  " + "  ".join(parts))


def orthogonality(m, restrict_common=False):
    print("\n" + "=" * 92)
    print("ORTHOGONALITY — does each variant's MoS survive neutralizing 1/PE? (residual IC, 2M/3M)")
    print("   critical for earning_power: is it just 1/PE relabeled? (KNOWLEDGE.md composite trap)")
    if restrict_common:
        common = m[[f"mos_{k}" for k in VKEYS]].notna().all(axis=1) & m.inv_pe.notna()
        m = m[common]
        print(f"   COMMON subset: {len(m)} rows")
    print("=" * 92)
    for k in VKEYS:
        moscol = f"mos_{k}"
        print(f"\n  {k}")
        # rank-corr MoS vs 1/PE (collinearity check)
        cc = m.groupby("time").apply(lambda x: spearman_ic(x[moscol].values, x.inv_pe.values)).dropna()
        print(f"    rank-corr(MoS,1/PE) mean={cc.mean():+.3f}   (high→collinear with 1/PE)")
        for wl, w in windows(m):
            parts = []
            for tgt in ["profit_2M", "profit_3M"]:
                ics = []
                for _, x in w.groupby("time"):
                    r = resid_rank(x[moscol].values, x.inv_pe.values)
                    ics.append(spearman_ic(r, x[tgt].values))
                s = pd.Series(ics).dropna()
                if len(s) == 0:
                    parts.append(f"{tgt.split('_')[1]}: n/a"); continue
                t = s.mean() / (s.std() / np.sqrt(len(s))) if s.std() > 0 else np.nan
                parts.append(f"{tgt.split('_')[1]}⟂PE={s.mean():+.4f}(t{t:+.1f})")
            print(f"    {wl:9s}  " + "  ".join(parts))


def level_impact(m):
    """How much does each variant shift the ABSOLUTE MoS level (the user's 'kém ý nghĩa' complaint)?"""
    print("\n" + "=" * 92)
    print("LEVEL IMPACT — median MoS & %cheap per variant (addresses 'DCF reads everything RICH')")
    print("=" * 92)
    latest = m[m.year >= 2025]
    for k in VKEYS:
        s = m[f"mos_{k}"].dropna()
        sl = latest[f"mos_{k}"].dropna()
        print(f"  {k:18s} ALL: median={s.median():+.2f} %cheap={100*(s>0).mean():4.0f}%  | "
              f"2025+: median={sl.median():+.2f} %cheap={100*(sl>0).mean():4.0f}%  n={len(s)}")


if __name__ == "__main__":
    fv = load_cache()
    m = build_panel(fv)
    print(f"\npanel rows={len(m)}  months={m.time.dt.to_period('M').nunique()}  tickers={m.ticker.nunique()}")
    level_impact(m)
    study_b(m, "OWN panel (each variant's full coverage)")
    study_b(m, "isolate ranking", restrict_common=True)
    orthogonality(m, restrict_common=True)
