# -*- coding: utf-8 -*-
"""
rf_slow_measure.py — RESEARCH ONLY (job Taylor_20261013_163831). Does NOT edit dcf_valuation.py.

Question: dcf_valuation's default terminal mode "cap_rf" sets g_T = min(cpi+gdp, rf) with
rf = SPOT deposit rate. The cap binds, so r - g_T = ERP = 6.5% whatever the rate does: a rate hike
moves r and g_T together and the terminal value barely reacts. Variant under test: keep r on the
spot rate, but cap g_T with a SLOW rf.

Variants (pre-registered here, before any number was looked at; N = 4 new + 1 control):
  V0 cap_rf          rf_cap = spot                      (production, CONTROL)
  V1 ma12            rf_cap = trailing 12M mean of the effective deposit step series
  V2 min_spot_ma12   rf_cap = min(spot, ma12)           (slow only on the way UP; keeps g_T <= spot rf)
  V3 ma36            rf_cap = trailing 36M mean
  V4 min_spot_ma36   rf_cap = min(spot, ma36)
  const (2nd control) constant rate for every date (window-mean deposit) -- removes the
        hindsight in the deposit anchors altogether; all variants collapse to one series here.

Parts:  A  today's basket (universe_pit members, latest date with both price and universe)
        B  cross-sectional MoS IC, Study-B mould, IS 2014-19 / OOS 2020+, 2 frames
        B2 hiking episodes (descriptive, N stated)
        C  +1pp / +2pp rate scenarios under both mechanisms
        D  CPI coverage-gap headroom

Run: $DNA_PYEXE rf_slow_measure.py        (threads=1; reads data/bq_cache, writes only next to itself)
"""
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
OUT = os.path.dirname(os.path.abspath(__file__))
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
import duckdb                        # noqa: E402
os.environ.setdefault("DCF_RATE_FRAME", "legacy")  # pin legacy (Taylor_20261030_073001): tái lập số cũ; mặc định prod nay = domestic_v2
import dcf_valuation as D            # noqa: E402  (chdirs to WORKDIR)
import deposit_rate_vn as dep        # noqa: E402
import gdp_growth_vn as gdp_mod      # noqa: E402
import cpi_vn                        # noqa: E402

os.environ.pop("DCF_TERMINAL_MODE", None)
assert D.DEFAULT_TERM_MODE == "cap_rf", D.DEFAULT_TERM_MODE
assert os.path.abspath(D.__file__).startswith(WORKDIR + "/dcf_valuation.py"), D.__file__
ERP = D.ERP
VARIANTS = ["cap_rf", "ma12", "min_spot_ma12", "ma36", "min_spot_ma36"]
R = {"variants": VARIANTS, "erp": ERP}


def con():
    c = duckdb.connect(":memory:")
    c.execute("SET threads=1")
    return c


# ------------------------------------------------------------------ rate series (decimal)
_ev = dep.effective_deposit_events_df()
_days = pd.date_range("2008-01-01", "2028-12-31", freq="D")
_spot = (pd.merge_asof(pd.DataFrame({"time": _days}), _ev, on="time", direction="backward")
         .set_index("time").deposit_rate.bfill() / 100.0)      # pre-2011 = first anchor (same clamp as D.discount_rate)
_ma12 = _spot.rolling(365).mean()
_ma36 = _spot.rolling(1095).mean()


def rf_cap(variant, asof, spot=None, ma12=None, ma36=None):
    a = pd.Timestamp(asof).normalize()
    spot = float(_spot.loc[a]) if spot is None else spot
    ma12 = float(_ma12.loc[a]) if ma12 is None else ma12
    ma36 = float(_ma36.loc[a]) if ma36 is None else ma36
    return {"cap_rf": spot, "ma12": ma12, "min_spot_ma12": min(spot, ma12),
            "ma36": ma36, "min_spot_ma36": min(spot, ma36)}[variant]


def uncapped_g(asof):
    return D.terminal_growth(asof) + gdp_mod.longrun_real_gdp(asof)


def fv_analytic(base_fcfe, g_raw, r, g_T, osh):
    """Same arithmetic, same ORDER as D.fair_value (g_exp from the un-guarded g_T, then the guard)."""
    g_raw_eff = g_T if np.isnan(g_raw) else g_raw
    g_exp = g_T + D.GROWTH_SHRINK * (float(np.clip(g_raw_eff, D.G_EXPLICIT_FLOOR, D.G_EXPLICIT_CAP)) - g_T)
    if r <= g_T:
        g_T = r - 0.01
    return D._fv_per_share(base_fcfe, g_exp, g_T, r, osh)


_ORIG_TGM = D.terminal_growth_mode


def patch(variant):
    """Route D.fair_value / D.dcf_check through a variant WITHOUT touching the file on disk."""
    if variant is None:
        D.terminal_growth_mode = _ORIG_TGM
        return

    def tgm(asof, mode=None, erp=ERP, with_frac=False):
        cpi, frac = D.terminal_growth(asof, with_frac=True)
        g = min(cpi + gdp_mod.longrun_real_gdp(asof), rf_cap(variant, asof))
        return (g, frac) if with_frac else g
    D.terminal_growth_mode = tgm


# ================================================================== base inputs per release
print("=" * 100)
print("rf_slow_measure — interpreter", sys.executable)
c = con()
mx_px = c.execute("SELECT max(CAST(time AS DATE)) FROM read_parquet('data/bq_cache/ticker/2026.parquet')").fetchone()[0]
mx_u = c.execute("SELECT max(time) FROM read_parquet('data/bq_cache/universe_pit/2026.parquet')").fetchone()[0]
mx_fin = c.execute("SELECT max(CAST(time AS DATE)) FROM read_parquet('data/bq_cache/ticker_financial.parquet')").fetchone()[0]
TODAY = min(pd.Timestamp(mx_px), pd.Timestamp(mx_u))
rsv = c.execute("SELECT DISTINCT ruleset_version FROM read_parquet('data/bq_cache/universe_pit/*.parquet')").df().ruleset_version.tolist()
print(f"data vintage: ticker max={mx_px}  universe_pit max={mx_u} (ruleset_version {rsv})  ticker_financial max={mx_fin}")
print(f"TODAY (latest date with BOTH price and universe) = {TODAY.date()}")
R["vintage"] = {"ticker_max": str(mx_px), "universe_pit_max": str(mx_u), "fin_max": str(mx_fin),
                "today": str(TODAY.date()), "ruleset_version": [int(x) for x in rsv]}

sb_cand = set(c.execute("""SELECT DISTINCT ticker FROM read_parquet('data/bq_cache/fa_ratings_8l.parquet')
    WHERE rating<=3 AND route NOT IN ('BANK','INSURANCE','SECURITIES')""").df().ticker)
u_ever = set(c.execute("SELECT DISTINCT ticker FROM read_parquet('data/bq_cache/universe_pit/*.parquet') WHERE in_universe").df().ticker)
ALL_TK = sorted(sb_cand | u_ever)
print(f"tickers: Study-B candidates {len(sb_cand)}, ever in universe_pit {len(u_ever)}, union {len(ALL_TK)}")

base_fp = os.path.join(OUT, "base_inputs_releases.parquet")
if os.path.exists(base_fp) and not os.environ.get("REFRESH"):
    base = pd.read_parquet(base_fp)
    print(f"base inputs loaded: {len(base)} release-points ({base.ticker.nunique()} tickers)")
else:
    fin = D._load_financials(); D._load_routes(); D._load_icb_map()
    by_tk = {tk: g for tk, g in fin.groupby("ticker")}
    rows = []
    for tk in ALL_TK:
        g = by_tk.get(tk)
        if g is None or len(g) < 5:
            continue
        for t in g.time.unique():
            t = pd.Timestamp(t)
            if t < pd.Timestamp("2012-06-01"):
                continue
            res = D.fair_value(tk, t, price=None, fin=g)          # unpatched production call
            if res["ok"]:
                gp = res["growth_points"]
                nanflag = all(pd.isna(x) for x in gp)
                rows.append({"ticker": tk, "rel_time": t, "base_fcfe": res["base_fcfe_vnd"],
                             "g_raw": np.nan if nanflag else res["g_explicit_raw"],
                             "oshares": res["oshares"], "r": res["discount_rate"],
                             "g_T_prod": res["g_terminal"], "fv_prod": res["fair_value_ps"]})
    base = pd.DataFrame(rows).sort_values(["ticker", "rel_time"]).reset_index(drop=True)
    base.to_parquet(base_fp)
    print(f"base inputs computed: {len(base)} release-points ({base.ticker.nunique()} tickers)")

# ---- per-release rate terms
rel = base.rel_time.dt.normalize()
base["spot"] = _spot.reindex(rel).values
base["ma12"] = _ma12.reindex(rel).values
base["ma36"] = _ma36.reindex(rel).values
_ug = {t: uncapped_g(t) for t in base.rel_time.unique()}
base["g_uncap"] = base.rel_time.map(_ug)
chk = float((base.spot - (base.r - ERP / 100.0)).abs().max())
print(f"\nSELF-CHECK 1  spot series == production discount_rate - ERP on every release: max|diff| = {chk:.2e}")
assert chk < 1e-12
bind = (base.g_uncap > base.spot)
print(f"cap binds (cpi+gdp > spot rf) on {100*bind.mean():.1f}% of releases; "
      f"since 2014: {100*bind[base.rel_time >= '2014-01-01'].mean():.1f}%")
R["cap_binding_pct_since_2014"] = float(100 * bind[base.rel_time >= "2014-01-01"].mean())

for v in VARIANTS:
    cap = {"cap_rf": base.spot, "ma12": base.ma12, "min_spot_ma12": np.minimum(base.spot, base.ma12),
           "ma36": base.ma36, "min_spot_ma36": np.minimum(base.spot, base.ma36)}[v]
    gT = np.minimum(base.g_uncap, cap)
    base[f"fv_{v}"] = [fv_analytic(b, g, r, t, o) for b, g, r, t, o in
                       zip(base.base_fcfe, base.g_raw, base.r, gT, base.oshares)]
chk = float((base.fv_cap_rf / base.fv_prod - 1).abs().max())
print(f"SELF-CHECK 2  control leg V0 (analytic) vs production D.fair_value on {len(base)} releases: "
      f"max|rel diff| = {chk:.2e}")
assert chk < 1e-12
R["selfcheck_control_max_rel_diff"] = chk

# constant-rate control: window-mean deposit 2014-01..2026-06 (same window as dcf_rate_robustness)
_idx = pd.date_range("2014-01-01", "2026-06-01", freq="MS")
DEP_CONST = float(_spot.reindex(_idx).mean())
base["fv_const"] = [fv_analytic(b, g, DEP_CONST + ERP / 100.0, min(u, DEP_CONST), o) for b, g, u, o in
                    zip(base.base_fcfe, base.g_raw, base.g_uncap, base.oshares)]
print(f"constant-rate control: deposit {100*DEP_CONST:.2f}% -> r {100*(DEP_CONST)+ERP:.2f}%")
R["const_deposit_pct"] = 100 * DEP_CONST

# ================================================================== A) today's basket
print("\n" + "=" * 100)
print(f"A) TODAY'S BASKET — universe_pit members on {TODAY.date()}, price = Price on that date (BQ cache; research use)")
a_s = str(TODAY.date())
sp, m12, m36 = float(_spot.loc[TODAY]), float(_ma12.loc[TODAY]), float(_ma36.loc[TODAY])
gu = uncapped_g(TODAY)
print(f"  spot rf {100*sp:.2f}%  ma12 {100*m12:.2f}%  ma36 {100*m36:.2f}%  cpi+gdp {100*gu:.2f}%  r {100*sp+ERP:.2f}%")
print("  r - g_T by variant: " + "  ".join(
    f"{v}={100*(sp + ERP/100 - min(gu, rf_cap(v, TODAY))):.2f}pp" for v in VARIANTS))
R["today_rates"] = {"spot": sp, "ma12": m12, "ma36": m36, "g_uncapped": gu,
                    "spread": {v: sp + ERP / 100 - min(gu, rf_cap(v, TODAY)) for v in VARIANTS}}
uni = c.execute(f"SELECT ticker FROM read_parquet('data/bq_cache/universe_pit/2026.parquet') "
                f"WHERE time = DATE '{a_s}' AND in_universe").df().ticker.tolist()
px = c.execute(f"SELECT ticker, Price FROM read_parquet('data/bq_cache/ticker/2026.parquet') "
               f"WHERE CAST(time AS DATE) = DATE '{a_s}' AND Price IS NOT NULL").df().set_index("ticker").Price
rows = []
for tk in uni:
    if tk not in px.index:
        continue
    row = {"ticker": tk, "price": float(px[tk])}
    ok = True
    for v in VARIANTS:
        patch(v)
        d = D.dcf_check(tk, a_s, price=float(px[tk]))
        if d["status"] == "NOT_COMPUTED":
            ok = False
            row["reason"] = d.get("reason")
            break
        res = D.fair_value(tk, a_s, price=float(px[tk]))
        row[f"fv_{v}"], row[f"mos_{v}"] = res["fair_value_ps"], res["margin_of_safety"]
        row[f"st_{v}"], row[f"rb_{v}"] = d["status"], d["robust"]
        if v == "cap_rf":
            row["g_raw"] = res["g_explicit_raw"]
    patch(None)
    row["ok"] = ok
    rows.append(row)
A = pd.DataFrame(rows)
patch(None)
nc = A[~A.ok]
A = A[A.ok].copy()
print(f"  members {len(uni)}, priced {len(rows)}, DCF computed {len(A)}; not computed {len(nc)}: "
      f"{nc.reason.value_counts().to_dict()}")
# control: unpatched production == patched V0
ctl = max(abs(D.fair_value(t, a_s, price=float(px[t]))["fair_value_ps"] / f - 1) for t, f in zip(A.ticker, A.fv_cap_rf))
print(f"  SELF-CHECK 3  patched V0 == unpatched production on today's basket: max|rel diff| = {ctl:.2e}")
assert ctl < 1e-12
A.to_csv(os.path.join(OUT, "today_basket_by_variant.csv"), index=False)
print(f"\n  {'variant':16s} {'%CHEAP':>7s} {'n CHEAP':>8s} {'robust CHEAP':>13s} {'median MoS':>11s} "
      f"{'median dFV vs V0':>17s} {'CHEAP->RICH':>12s} {'RICH->CHEAP':>12s}")
R["today"] = {"n_members": len(uni), "n_dcf": int(len(A))}
for v in VARIANTS:
    dfv = (A[f"fv_{v}"] / A.fv_cap_rf - 1)
    c2r = A[(A.st_cap_rf == "CHEAP") & (A[f"st_{v}"] == "RICH")]
    r2c = A[(A.st_cap_rf == "RICH") & (A[f"st_{v}"] == "CHEAP")]
    cheap = (A[f"st_{v}"] == "CHEAP")
    print(f"  {v:16s} {100*cheap.mean():7.1f} {int(cheap.sum()):8d} {int((cheap & A[f'rb_{v}']).sum()):13d} "
          f"{100*A[f'mos_{v}'].median():+10.1f}% {100*dfv.median():+16.1f}% {len(c2r):12d} {len(r2c):12d}")
    R["today"][v] = {"pct_cheap": float(100 * cheap.mean()), "n_cheap": int(cheap.sum()),
                     "n_robust_cheap": int((cheap & A[f"rb_{v}"]).sum()),
                     "median_mos": float(A[f"mos_{v}"].median()), "median_dfv": float(dfv.median()),
                     "dfv_min": float(dfv.min()), "dfv_max": float(dfv.max()),
                     "cheap_to_rich": sorted(c2r.ticker.tolist()), "rich_to_cheap": sorted(r2c.ticker.tolist())}
for v in ("ma12", "ma36"):
    c2r = A[(A.st_cap_rf == "CHEAP") & (A[f"st_{v}"] == "RICH")].sort_values("mos_cap_rf")
    print(f"\n  CHEAP -> RICH under {v} ({len(c2r)} names; MoS V0 -> MoS {v}):")
    print("   " + "  ".join(f"{t}({100*a:+.0f}->{100*b:+.0f})" for t, a, b in zip(c2r.ticker, c2r.mos_cap_rf, c2r[f"mos_{v}"])))
    lost = A[(A.st_cap_rf == "CHEAP") & A.rb_cap_rf & ~((A[f"st_{v}"] == "CHEAP") & A[f"rb_{v}"])]
    print(f"  robust-CHEAP under V0 that are no longer robust-CHEAP under {v}: {len(lost)}")
    R["today"][v]["robust_cheap_lost"] = sorted(lost.ticker.tolist())

# ================================================================== B) cross-sectional IC
print("\n" + "=" * 100)
print("B) CROSS-SECTIONAL MoS IC (Study-B mould): monthly first trading row, FV as-of latest release <=460d old")
all_sql = "(" + ",".join(f"'{t}'" for t in base.ticker.unique()) + ")"
pxm = c.execute(f"""
    SELECT ticker, tdate AS time, Price, Close, profit_1M, profit_2M, profit_3M FROM (
      SELECT ticker, CAST(time AS DATE) AS tdate, Price, Close, profit_1M, profit_2M, profit_3M,
             row_number() OVER (PARTITION BY ticker, date_trunc('month',CAST(time AS DATE)) ORDER BY CAST(time AS DATE)) rn
      FROM read_parquet('data/bq_cache/ticker/2*.parquet')
      WHERE ticker IN {all_sql} AND CAST(time AS DATE) >= DATE '2014-01-01'
    ) WHERE rn=1 AND Price IS NOT NULL""").df()
pxm["time"] = pd.to_datetime(pxm["time"])
fvc = ["rel_time"] + [f"fv_{v}" for v in VARIANTS] + ["fv_const"]
m = pd.merge_asof(pxm.sort_values("time"), base[["ticker"] + fvc].sort_values("rel_time"),
                  left_on="time", right_on="rel_time", by="ticker", direction="backward")
m = m[m.rel_time.notna() & ((m.time - m.rel_time).dt.days <= 460)]
rat = c.execute("SELECT ticker, time, rating FROM read_parquet('data/bq_cache/fa_ratings_8l.parquet')").df()
rat["time"] = pd.to_datetime(rat["time"])
m = pd.merge_asof(m.sort_values("time"), rat.sort_values("time"), on="time", by="ticker", direction="backward")
up = c.execute("SELECT ticker, time, in_universe FROM read_parquet('data/bq_cache/universe_pit/*.parquet')").df()
up["time"] = pd.to_datetime(up["time"])
m = m.merge(up, on=["ticker", "time"], how="left")
m["in_universe"] = m.in_universe.fillna(False).astype(bool)
m["ym"] = m.time.dt.to_period("M")
m["year"] = m.time.dt.year
for v in VARIANTS + ["const"]:
    m[f"mos_{v}"] = (m[f"fv_{v}"] - m.Price) / m[f"fv_{v}"]
FRAMES = {"StudyB (ever-rated<=3 cand, rating<=3 as-of)": m[m.ticker.isin(sb_cand) & (m.rating <= 3)],
          "universe_pit member as-of AND rating<=3": m[m.in_universe & (m.rating <= 3)]}


def rank_ic(a, b):
    ok = (~pd.isna(a)) & (~pd.isna(b))
    if ok.sum() < 8:
        return np.nan
    return pd.Series(a[ok]).rank().corr(pd.Series(b[ok]).rank())


def nw_t(x, lag):
    """t-stat of the mean with a Newey-West (Bartlett) variance, lag = horizon_months - 1."""
    x = np.asarray(x, float)
    n = len(x)
    if n < 6:
        return np.nan
    e = x - x.mean()
    s = (e @ e) / n
    for k in range(1, lag + 1):
        s += 2 * (1 - k / (lag + 1)) * (e[k:] @ e[:-k]) / n
    return x.mean() / np.sqrt(s / n) if s > 0 else np.nan


R["ic"] = {}
HOR = {"profit_1M": 0, "profit_2M": 1, "profit_3M": 2}
for fname, f in FRAMES.items():
    print(f"\n  FRAME: {fname}   rows={len(f)} months={f.ym.nunique()} tickers={f.ticker.nunique()} "
          f"median names/month={int(f.groupby('ym').ticker.nunique().median())}")
    R["ic"][fname] = {}
    ics = {}
    for v in VARIANTS + ["const"]:
        for tgt in HOR:
            ics[(v, tgt)] = f.groupby("ym").apply(lambda x: rank_ic(x[f"mos_{v}"].values, x[tgt].values)).dropna()
    rk = {v: f.groupby("ym").apply(lambda x: rank_ic(x[f"mos_{v}"].values, x.mos_cap_rf.values)).mean()
          for v in VARIANTS[1:] + ["const"]}
    print("   mean within-month rank corr of MoS vs V0: " + "  ".join(f"{k}={x:.4f}" for k, x in rk.items()))
    R["ic"][fname]["rank_corr_vs_v0"] = {k: float(x) for k, x in rk.items()}
    for wname, sel in (("IS 2014-2019", lambda s: s[s.index.year <= 2019]),
                       ("OOS 2020+", lambda s: s[s.index.year >= 2020]), ("ALL", lambda s: s)):
        print(f"   {wname}:  mean IC (NW t) | paired diff vs V0: mean dIC (NW t)")
        R["ic"][fname][wname] = {}
        for v in VARIANTS + ["const"]:
            cells = []
            R["ic"][fname][wname][v] = {}
            for tgt, lag in HOR.items():
                s = sel(ics[(v, tgt)])
                s0 = sel(ics[("cap_rf", tgt)])
                d = (s - s0).dropna()
                cells.append(f"{tgt[-2:]} {s.mean():+.4f} ({nw_t(s.values, lag):+.1f}) | "
                             f"{d.mean():+.4f} ({nw_t(d.values, lag):+.1f})")
                R["ic"][fname][wname][v][tgt] = {"ic": float(s.mean()), "t_nw": float(nw_t(s.values, lag)),
                                                 "n_months": int(len(s)), "d_ic": float(d.mean()),
                                                 "d_t_nw": float(nw_t(d.values, lag)), "hit": float((s > 0).mean())}
            print(f"     {v:14s} n={len(sel(ics[(v, 'profit_1M')])):3d}  " + "   ".join(cells))

# ================================================================== B2) hiking episodes (descriptive)
print("\n" + "=" * 100)
print("B2) WHERE THE VARIANTS DIFFER IN LEVEL — months with spot - ma12 > 0.5pp (rate rising fast)")
f = FRAMES["universe_pit member as-of AND rating<=3"].copy()
cl = pxm[["ticker", "time", "Close"]].copy()
cl["ym"] = cl.time.dt.to_period("M")
fwd = cl.copy()
fwd["ym"] = fwd.ym - 12
f = f.merge(fwd[["ticker", "ym", "Close"]].rename(columns={"Close": "Close_12m"}), on=["ticker", "ym"], how="left")
f["fwd12"] = f.Close_12m / f.Close - 1
mon = f.groupby("ym").agg(time=("time", "min"), n=("ticker", "nunique"),
                          cheap_v0=("mos_cap_rf", lambda x: 100 * (x > 0).mean()),
                          cheap_ma12=("mos_ma12", lambda x: 100 * (x > 0).mean()),
                          cheap_min12=("mos_min_spot_ma12", lambda x: 100 * (x > 0).mean()),
                          med_fwd3m=("profit_3M", "median"), med_fwd12m=("fwd12", lambda x: 100 * x.median()))
mon["spot"] = [100 * float(_spot.asof(t)) for t in mon.time]
mon["ma12"] = [100 * float(_ma12.asof(t)) for t in mon.time]
mon["gap"] = mon.spot - mon.ma12
mon.to_csv(os.path.join(OUT, "monthly_cheap_share_by_variant.csv"))
hike = mon[mon.gap > 0.5]
ep = (hike.index.to_series().diff().apply(lambda x: getattr(x, "n", 99)) > 1).cumsum()
print(f"  months with gap>0.5pp: {len(hike)} in {ep.nunique()} separate episode(s): "
      + "; ".join(f"{g.index.min()}..{g.index.max()}" for _, g in hike.groupby(ep)))
print(hike[["n", "spot", "ma12", "gap", "cheap_v0", "cheap_ma12", "med_fwd3m", "med_fwd12m"]].round(1).to_string())
ease = mon[mon.gap < -0.5]
print(f"\n  months with gap<-0.5pp (rate FALLING fast; plain ma12 lets g_T exceed spot rf): {len(ease)}; "
      f"%CHEAP V0 {ease.cheap_v0.mean():.1f} vs ma12 {ease.cheap_ma12.mean():.1f} vs min_spot_ma12 {ease.cheap_min12.mean():.1f}")
R["episodes"] = {"n_hike_months": int(len(hike)), "n_hike_episodes": int(ep.nunique()),
                 "episodes": [f"{g.index.min()}..{g.index.max()}" for _, g in hike.groupby(ep)],
                 "n_ease_months": int(len(ease))}

# ================================================================== C) rate scenarios
print("\n" + "=" * 100)
print(f"C) RATE SCENARIOS on today's basket ({len(A)} names): rate steps up tomorrow and stays; fundamentals + price frozen.")
print("   Index 100 = production FV today. Median across names; %CHEAP in brackets.")
tb = base[base.ticker.isin(A.ticker)].sort_values("rel_time").groupby("ticker").tail(1).set_index("ticker")
tb = tb.loc[A.ticker]
pr = A.set_index("ticker").price
R["scenarios"] = {}
for v in VARIANTS:
    R["scenarios"][v] = {}
    line = []
    for shock in (0.0, 0.01, 0.02):
        for hz in (0, 182, 365):
            path = _spot.loc[TODAY - pd.Timedelta(days=1100):TODAY].copy()
            fut = pd.Series(sp + shock, index=pd.date_range(TODAY + pd.Timedelta(days=1), periods=max(hz, 1), freq="D"))
            full = pd.concat([path, fut])
            at = TODAY + pd.Timedelta(days=hz) if hz else TODAY
            s_now = sp + shock
            ma12_s = float(full.loc[:at].iloc[-365:].mean()) if hz else m12
            ma36_s = float(full.loc[:at].iloc[-1095:].mean()) if hz else m36
            gT = min(gu, rf_cap(v, at, spot=s_now, ma12=ma12_s, ma36=ma36_s))
            fv = np.array([fv_analytic(b, g, s_now + ERP / 100, gT, o) for b, g, o in zip(tb.base_fcfe, tb.g_raw, tb.oshares)])
            idx = 100 * np.median(fv / A.fv_cap_rf.values)
            ch = 100 * np.mean((fv - pr.values) / fv > 0)
            R["scenarios"][v][f"+{int(shock*100)}pp@{hz}d"] = {"fv_index": float(idx), "pct_cheap": float(ch),
                                                             "spread_pp": float(100 * (s_now + ERP / 100 - gT))}
            line.append(f"+{int(shock*100)}pp/{hz:3d}d {idx:5.1f} [{ch:4.1f}%]")
    print(f"   {v:14s} " + " | ".join(line))

# ================================================================== D) CPI gap headroom
print("\n" + "=" * 100)
print("D) CPI coverage gap")
cpi = cpi_vn.cpi_monthly_df(end="2026-12-01")
tail = cpi[cpi.time >= "2026-04-01"][["time", "cpi_yoy", "is_real_nso"]]
print(tail.to_string(index=False))
cpi5 = D.terminal_growth(TODAY)
gdp15 = gdp_mod.longrun_real_gdp(TODAY)
print(f"  today: 5y-avg CPI {100*cpi5:.2f}% + 15y real GDP {100*gdp15:.2f}% = {100*gu:.2f}% vs spot rf {100*sp:.2f}% "
      f"(headroom {100*(gu-sp):.2f}pp) / ma12 {100*m12:.2f}% (headroom {100*(gu-m12):.2f}pp)")
w = cpi[(cpi.time <= TODAY) & (cpi.time > TODAY - pd.Timedelta(days=365 * 5))]
n_proxy_recent = int((~w[w.time >= "2026-07-01"].is_real_nso.astype(bool)).sum())
print(f"  5y window: {len(w)} months, of which non-NSO since 2026-07: {n_proxy_recent}. For the cap to stop binding the "
      f"5y average would have to fall by {100*(gu-sp):.2f}pp, i.e. those {n_proxy_recent} months would each have to be "
      f"overstated by {100*(gu-sp)*len(w)/max(n_proxy_recent,1):.0f}pp.")
R["cpi"] = {"cpi5y": cpi5, "gdp15y": gdp15, "headroom_spot_pp": 100 * (gu - sp), "headroom_ma12_pp": 100 * (gu - m12),
            "n_window_months": int(len(w)), "n_non_nso_since_2026_07": n_proxy_recent}

with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(R, fh, indent=1, default=str)
print("\nwrote results.json, today_basket_by_variant.csv, monthly_cheap_share_by_variant.csv")
